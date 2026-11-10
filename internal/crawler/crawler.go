package crawler

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"go-search-engine/internal/bloom"
	"go-search-engine/internal/db"
)

// LogEvent represents a live crawler milestone streamed to the dashboard.
type LogEvent struct {
	Timestamp string `json:"timestamp"`
	Level     string `json:"level"`
	Message   string `json:"message"`
	URL       string `json:"url"`
}

// Metrics captures real-time crawler telemetry.
type Metrics struct {
	IsRunning         bool      `json:"isRunning"`
	PagesCrawled      int64     `json:"pagesCrawled"`
	PagesPerSecond    float64   `json:"pagesPerSecond"`
	QueueSize         int       `json:"queueSize"`
	TotalBloomCount   uint64    `json:"totalBloomCount"`
	BloomMemoryBytes  uint64    `json:"bloomMemoryBytes"`
	BloomFPRate       float64   `json:"bloomFpRate"`
	TotalIndexedDocs  int       `json:"totalIndexedDocs"`
	TotalUniqueTerms  int       `json:"totalUniqueTerms"`
	CurrentURL        string    `json:"currentUrl"`
	RecentLogs        []LogEvent `json:"recentLogs"`
}

// Engine coordinates the concurrent crawler swarm, in-memory Bloom filter,
// and dedicated SQLite batch writer goroutine.
type Engine struct {
	database      *db.Database
	bloomFilter   *bloom.BloomFilter
	robotsChecker *RobotsChecker
	httpClient    *http.Client

	// Concurrency and pipeline
	docChannel    chan db.ParsedDocument
	frontierQueue chan string
	cancelFunc    context.CancelFunc
	ctx           context.Context
	wg            sync.WaitGroup

	// Metrics
	mu            sync.RWMutex
	isRunning     atomic.Bool
	pagesCrawled  atomic.Int64
	startTime     time.Time
	currentURL    string
	recentLogs    []LogEvent
	maxLogs       int

	// Callbacks for live event streaming (Wails IPC)
	OnMetricsUpdate func(m Metrics)
}

// NewEngine initializes the crawler engine with the provided database instance.
func NewEngine(database *db.Database) *Engine {
	return &Engine{
		database:      database,
		bloomFilter:   bloom.New(500000, 0.001), // 500k URLs capacity, 0.1% false positive bound
		robotsChecker: NewRobotsChecker(),
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
		maxLogs: 40,
	}
}

// AddLog registers an event into the rolling telemetry buffer.
func (e *Engine) AddLog(level, message, targetURL string) {
	e.mu.Lock()
	defer e.mu.Unlock()

	evt := LogEvent{
		Timestamp: time.Now().Format("15:04:05.000"),
		Level:     level,
		Message:   message,
		URL:       targetURL,
	}
	e.recentLogs = append([]LogEvent{evt}, e.recentLogs...)
	if len(e.recentLogs) > e.maxLogs {
		e.recentLogs = e.recentLogs[:e.maxLogs]
	}

	if e.OnMetricsUpdate != nil {
		go e.broadcastMetrics()
	}
}

func (e *Engine) broadcastMetrics() {
	if e.OnMetricsUpdate != nil {
		e.OnMetricsUpdate(e.GetMetrics())
	}
}

// Start initiates a concurrent crawl starting from seedURL up to maxPages with concurrency workers.
func (e *Engine) Start(seedURL string, maxPages int, concurrency int) error {
	if e.isRunning.Load() {
		return fmt.Errorf("crawler is already running")
	}

	parsedSeed, err := url.Parse(seedURL)
	if err != nil || (parsedSeed.Scheme != "http" && parsedSeed.Scheme != "https") {
		return fmt.Errorf("invalid seed URL: %s", seedURL)
	}

	if concurrency <= 0 {
		concurrency = 4
	}
	if concurrency > 32 {
		concurrency = 32
	}
	if maxPages <= 0 {
		maxPages = 100
	}

	ctx, cancel := context.WithCancel(context.Background())
	e.ctx = ctx
	e.cancelFunc = cancel
	e.isRunning.Store(true)
	e.pagesCrawled.Store(0)
	e.startTime = time.Now()

	// Pipeline channels
	e.docChannel = make(chan db.ParsedDocument, 100)
	e.frontierQueue = make(chan string, 10000)

	// Seed URL registration
	normalizedSeed := cleanAndResolveURL(seedURL, parsedSeed)
	e.bloomFilter.AddIfNotPresent(normalizedSeed)
	e.frontierQueue <- normalizedSeed

	e.AddLog("INFO", fmt.Sprintf("Started crawl swarm with %d workers (Limit: %d pages)", concurrency, maxPages), seedURL)

	// 1. Launch dedicated SQLite Writer Goroutine (Ticket 5)
	e.wg.Add(1)
	go e.runDedicatedDBWriter()

	// 2. Launch Crawler Swarm Worker Goroutines (Ticket 3)
	for i := 0; i < concurrency; i++ {
		e.wg.Add(1)
		go e.runWorker(i, maxPages)
	}

	// 3. Background metrics broadcaster ticker
	go func() {
		ticker := time.NewTicker(500 * time.Millisecond)
		defer ticker.Stop()
		for {
			select {
			case <-e.ctx.Done():
				return
			case <-ticker.C:
				if e.isRunning.Load() {
					e.broadcastMetrics()
				}
			}
		}
	}()

	return nil
}

// Stop halts the crawl and drains active workers safely.
func (e *Engine) Stop() {
	if !e.isRunning.Load() {
		return
	}
	e.AddLog("WARN", "Stopping crawler swarm...", "")
	if e.cancelFunc != nil {
		e.cancelFunc()
	}
	e.isRunning.Store(false)
	e.broadcastMetrics()
}

// runDedicatedDBWriter is the single writer goroutine that serializes all SQLite inserts,
// batching parsed documents from the crawler swarm and eliminating database lock contention.
func (e *Engine) runDedicatedDBWriter() {
	defer e.wg.Done()

	batch := make([]db.ParsedDocument, 0, 15)
	ticker := time.NewTicker(400 * time.Millisecond)
	defer ticker.Stop()

	flush := func() {
		if len(batch) == 0 {
			return
		}
		if err := e.database.BatchInsert(batch); err != nil {
			e.AddLog("ERROR", fmt.Sprintf("DB batch insert failed: %v", err), "")
		} else {
			e.AddLog("SUCCESS", fmt.Sprintf("Committed batch of %d pages to SQLite index", len(batch)), "")
		}
		batch = batch[:0]
	}

	for {
		select {
		case doc, ok := <-e.docChannel:
			if !ok {
				flush()
				return
			}
			batch = append(batch, doc)
			if len(batch) >= 15 {
				flush()
			}
		case <-ticker.C:
			flush()
		case <-e.ctx.Done():
			// Drain remaining docs in channel
			for {
				select {
				case doc := <-e.docChannel:
					batch = append(batch, doc)
				default:
					flush()
					return
				}
			}
		}
	}
}

// runWorker is a crawler swarm goroutine fetching, parsing, and feeding the pipeline.
func (e *Engine) runWorker(id int, maxPages int) {
	defer e.wg.Done()

	for {
		select {
		case <-e.ctx.Done():
			return
		case targetURL, ok := <-e.frontierQueue:
			if !ok {
				return
			}

			// Stop if page ceiling reached
			if int(e.pagesCrawled.Load()) >= maxPages {
				e.Stop()
				return
			}

			e.mu.Lock()
			e.currentURL = targetURL
			e.mu.Unlock()

			// Check robots.txt polite scraping rules
			if !e.robotsChecker.IsAllowed(targetURL) {
				e.AddLog("WARN", "Skipping disallowed by robots.txt", targetURL)
				continue
			}

			// Fetch HTML
			parsedPage, err := e.fetchAndParse(targetURL)
			if err != nil {
				e.AddLog("ERROR", fmt.Sprintf("Fetch failed: %v", err), targetURL)
				continue
			}

			count := e.pagesCrawled.Add(1)
			e.AddLog("INFO", fmt.Sprintf("Crawled [%d/%d] (%d words, %d links)", count, maxPages, parsedPage.WordCount, len(parsedPage.Links)), targetURL)

			// Send to dedicated DB writer
			select {
			case e.docChannel <- db.ParsedDocument{
				URL:       targetURL,
				Title:     parsedPage.Title,
				Snippet:   parsedPage.Snippet,
				WordCount: parsedPage.WordCount,
				Terms:     parsedPage.Terms,
			}:
			case <-e.ctx.Done():
				return
			}

			// Enqueue discovered links using Bloom Filter
			for _, link := range parsedPage.Links {
				if e.bloomFilter.AddIfNotPresent(link) {
					select {
					case e.frontierQueue <- link:
					default:
						// Queue capacity reached, continue
					}
				}
			}

			if int(count) >= maxPages {
				e.Stop()
				return
			}
		}
	}
}

func (e *Engine) fetchAndParse(targetURL string) (*ExtractedPage, error) {
	req, err := http.NewRequestWithContext(e.ctx, "GET", targetURL, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "GoSearchEngineBot/1.0 (+http://localhost)")

	resp, err := e.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("http status %d", resp.StatusCode)
	}

	contentType := resp.Header.Get("Content-Type")
	if contentType != "" && !strings.Contains(contentType, "text/html") && !strings.Contains(contentType, "text/plain") {
		return nil, fmt.Errorf("non-html content type: %s", contentType)
	}

	// Limit download to 2MB to avoid memory bloat
	bodyBytes, err := io.ReadAll(io.LimitReader(resp.Body, 2*1024*1024))
	if err != nil {
		return nil, err
	}

	baseURL, err := url.Parse(targetURL)
	if err != nil {
		return nil, err
	}

	return ExtractContent(bodyBytes, baseURL)
}

// GetMetrics aggregates instant telemetry for UI dashboards.
func (e *Engine) GetMetrics() Metrics {
	e.mu.RLock()
	defer e.mu.RUnlock()

	crawled := e.pagesCrawled.Load()
	var pps float64 = 0
	if e.isRunning.Load() && !e.startTime.IsZero() {
		elapsed := time.Since(e.startTime).Seconds()
		if elapsed > 0 {
			pps = float64(crawled) / elapsed
		}
	}

	var totalDocs, totalTerms int
	if e.database != nil {
		stats, _ := e.database.GetStats()
		totalDocs = stats.TotalDocuments
		totalTerms = stats.TotalTerms
	}

	qSize := 0
	if e.frontierQueue != nil {
		qSize = len(e.frontierQueue)
	}

	logsCopy := make([]LogEvent, len(e.recentLogs))
	copy(logsCopy, e.recentLogs)

	return Metrics{
		IsRunning:        e.isRunning.Load(),
		PagesCrawled:     crawled,
		PagesPerSecond:   float64(int(pps*10)) / 10,
		QueueSize:        qSize,
		TotalBloomCount:  e.bloomFilter.Count(),
		BloomMemoryBytes: e.bloomFilter.MemoryBytes(),
		BloomFPRate:      float64(int(e.bloomFilter.EstimatedFPRate()*10000)) / 10000,
		TotalIndexedDocs: totalDocs,
		TotalUniqueTerms: totalTerms,
		CurrentURL:       e.currentURL,
		RecentLogs:       logsCopy,
	}
}

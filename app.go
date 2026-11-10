package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"

	"github.com/wailsapp/wails/v2/pkg/runtime"

	"go-search-engine/internal/crawler"
	"go-search-engine/internal/db"
)

// App struct
type App struct {
	ctx      context.Context
	database *db.Database
	crawler  *crawler.Engine
	dbPath   string
}

// NewApp creates a new App application struct
func NewApp() *App {
	appData, err := os.UserConfigDir()
	if err != nil {
		appData = "."
	}
	appDir := filepath.Join(appData, "GoSearchEngine")
	_ = os.MkdirAll(appDir, 0755)
	dbPath := filepath.Join(appDir, "searchengine.db")

	database, err := db.Open(dbPath)
	if err != nil {
		// Fallback to local working directory
		dbPath = "searchengine.db"
		database, _ = db.Open(dbPath)
	}

	engine := crawler.NewEngine(database)

	a := &App{
		database: database,
		crawler:  engine,
		dbPath:   dbPath,
	}

	// Wire live event emissions via Wails runtime
	engine.OnMetricsUpdate = func(m crawler.Metrics) {
		if a.ctx != nil {
			runtime.EventsEmit(a.ctx, "metrics:update", m)
		}
	}

	return a
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// shutdown is called at application termination
func (a *App) shutdown(ctx context.Context) {
	if a.crawler != nil {
		a.crawler.Stop()
	}
	if a.database != nil {
		_ = a.database.Close()
	}
}

// StartCrawl triggers the concurrent crawler swarm
func (a *App) StartCrawl(seedURL string, maxPages int, concurrency int) string {
	err := a.crawler.Start(seedURL, maxPages, concurrency)
	if err != nil {
		return fmt.Sprintf("Error: %v", err)
	}
	return "Crawl started successfully"
}

// StopCrawl stops the active crawler swarm safely
func (a *App) StopCrawl() string {
	a.crawler.Stop()
	return "Crawl stopped"
}

// GetMetrics returns the live metrics from the crawler engine
func (a *App) GetMetrics() crawler.Metrics {
	return a.crawler.GetMetrics()
}

// Search performs a query-time TF-IDF search
func (a *App) Search(query string, limit int) ([]db.SearchResult, error) {
	if a.database == nil {
		return []db.SearchResult{}, fmt.Errorf("database not initialized")
	}
	return a.database.Search(query, limit)
}

// GetStats returns corpus statistics
func (a *App) GetStats() (db.DBStats, error) {
	if a.database == nil {
		return db.DBStats{}, fmt.Errorf("database not initialized")
	}
	return a.database.GetStats()
}

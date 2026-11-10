package crawler

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"path/filepath"
	"testing"
	"time"

	"go-search-engine/internal/db"
)

func TestCrawlerEndToEnd(t *testing.T) {
	// Setup mock web server
	var ts *httptest.Server
	ts = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/robots.txt":
			fmt.Fprintln(w, "User-agent: *")
			fmt.Fprintln(w, "Disallow: /disallowed")
		case "/":
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprintf(w, `
				<html>
				<head><title>Home Page</title></head>
				<body>
					<nav><a href="/ignored">Nav Link</a></nav>
					<h1>Welcome to Concurrent Search</h1>
					<p>Go goroutines and channels make high-performance crawling seamless.</p>
					<a href="%s/page1">Page 1</a>
					<a href="%s/page2">Page 2</a>
					<a href="%s/disallowed">Disallowed Page</a>
				</body>
				</html>
			`, ts.URL, ts.URL, ts.URL)
		case "/page1":
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprintf(w, `
				<html>
				<head><title>Distributed Indexing</title></head>
				<body>
					<p>Indexing documents with dynamic TF-IDF ranking allows instant searching.</p>
					<a href="%s/">Back to Home</a>
				</body>
				</html>
			`, ts.URL)
		case "/page2":
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprintf(w, `
				<html>
				<head><title>Bloom Filters</title></head>
				<body>
					<p>In-memory Bloom filters provide memory-safe visited set tracking.</p>
				</body>
				</html>
			`)
		case "/disallowed":
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprintln(w, "<html><body>Forbidden Content</body></html>")
		default:
			http.NotFound(w, r)
		}
	}))
	defer ts.Close()

	// Setup SQLite DB
	tempDir := t.TempDir()
	database, err := db.Open(filepath.Join(tempDir, "crawler_test.db"))
	if err != nil {
		t.Fatalf("Open DB failed: %v", err)
	}
	defer database.Close()

	engine := NewEngine(database)
	err = engine.Start(ts.URL, 5, 2)
	if err != nil {
		t.Fatalf("Engine Start failed: %v", err)
	}

	// Wait for crawler to crawl the mock pages
	time.Sleep(1200 * time.Millisecond)
	engine.Stop()

	// Wait for DB writer flush
	time.Sleep(600 * time.Millisecond)

	metrics := engine.GetMetrics()
	t.Logf("Pages Crawled: %d | Bloom Filter Count: %d | Indexed Docs: %d",
		metrics.PagesCrawled, metrics.TotalBloomCount, metrics.TotalIndexedDocs)

	if metrics.PagesCrawled < 2 {
		t.Fatalf("expected at least 2 pages crawled, got %d", metrics.PagesCrawled)
	}

	// Verify Search works on the newly indexed data
	results, err := database.Search("bloom filters", 5)
	if err != nil {
		t.Fatalf("Search failed: %v", err)
	}
	if len(results) == 0 {
		t.Fatalf("expected search results for 'bloom filters', got none")
	}

	t.Logf("Search result found: %s (%s)", results[0].Title, results[0].URL)
}

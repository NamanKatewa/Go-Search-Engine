package db

import (
	"path/filepath"
	"testing"
)

func TestDatabaseBatchInsertAndSearch(t *testing.T) {
	tempDir := t.TempDir()
	dbPath := filepath.Join(tempDir, "test_search.db")

	database, err := Open(dbPath)
	if err != nil {
		t.Fatalf("Open failed: %v", err)
	}
	defer database.Close()

	// Insert test documents
	docs := []ParsedDocument{
		{
			URL:       "https://go.dev/doc/concurrency",
			Title:     "Go Concurrency Patterns",
			Snippet:   "Goroutines and channels enable high-performance concurrent programs in Go.",
			WordCount: 8,
			Terms: map[string]int{
				"goroutines":  3,
				"channels":    2,
				"concurrency": 4,
				"go":          5,
			},
		},
		{
			URL:       "https://go.dev/doc/database",
			Title:     "Working with SQLite in Go",
			Snippet:   "SQLite database transactions with Go provide structured data storage.",
			WordCount: 9,
			Terms: map[string]int{
				"sqlite":   4,
				"database": 3,
				"storage":  2,
				"go":       2,
			},
		},
		{
			URL:       "https://wails.io/docs",
			Title:     "Wails Desktop Applications",
			Snippet:   "Build fast desktop apps using Go and modern frontend frameworks.",
			WordCount: 9,
			Terms: map[string]int{
				"desktop":  3,
				"wails":    4,
				"frontend": 2,
				"go":       1,
			},
		},
	}

	err = database.BatchInsert(docs)
	if err != nil {
		t.Fatalf("BatchInsert failed: %v", err)
	}

	stats, err := database.GetStats()
	if err != nil {
		t.Fatalf("GetStats failed: %v", err)
	}
	if stats.TotalDocuments != 3 {
		t.Fatalf("expected 3 documents, got %d", stats.TotalDocuments)
	}
	if stats.TotalTerms < 8 {
		t.Fatalf("expected at least 8 unique terms, got %d", stats.TotalTerms)
	}

	// Test Search
	results, err := database.Search("concurrency goroutines", 10)
	if err != nil {
		t.Fatalf("Search failed: %v", err)
	}

	if len(results) == 0 {
		t.Fatalf("expected results for 'concurrency goroutines', got none")
	}

	if results[0].URL != "https://go.dev/doc/concurrency" {
		t.Fatalf("expected top result to be concurrency doc, got: %s", results[0].URL)
	}

	t.Logf("Top result: %s (score: %.2f)", results[0].Title, results[0].Score)
}

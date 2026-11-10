package db

import (
	"database/sql"
	"fmt"
	"math"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"

	_ "modernc.org/sqlite"
)

var wordRegex = regexp.MustCompile(`[a-zA-Z0-9]{2,45}`)

// ParsedDocument represents a crawled web page with extracted text and term statistics.
type ParsedDocument struct {
	URL       string         `json:"url"`
	Title     string         `json:"title"`
	Snippet   string         `json:"snippet"`
	WordCount int            `json:"wordCount"`
	Terms     map[string]int `json:"terms"` // raw Term Frequencies (TF)
}

// SearchResult represents a document matched against a search query, ranked by TF-IDF.
type SearchResult struct {
	DocumentID   int64    `json:"documentId"`
	URL          string   `json:"url"`
	Title        string   `json:"title"`
	Snippet      string   `json:"snippet"`
	Score        float64  `json:"score"`
	WordCount    int      `json:"wordCount"`
	MatchedTerms []string `json:"matchedTerms"`
}

// DBStats provides aggregate counts for the local index.
type DBStats struct {
	TotalDocuments int `json:"totalDocuments"`
	TotalTerms     int `json:"totalTerms"`
	TotalPostings  int `json:"totalPostings"`
}

// Database encapsulates the SQLite inverted index connection with thread-safe query/write locks.
type Database struct {
	db *sql.DB
	mu sync.RWMutex
}

// Open initializes or connects to an existing SQLite database file with WAL mode enabled.
func Open(dataSourceName string) (*Database, error) {
	conn, err := sql.Open("sqlite", dataSourceName)
	if err != nil {
		return nil, fmt.Errorf("failed to open sqlite database: %w", err)
	}

	// Optimize SQLite for concurrent reading and single-threaded writing
	pragmas := []string{
		"PRAGMA journal_mode = WAL;",
		"PRAGMA synchronous = NORMAL;",
		"PRAGMA busy_timeout = 10000;",
		"PRAGMA foreign_keys = ON;",
	}
	for _, p := range pragmas {
		if _, err := conn.Exec(p); err != nil {
			conn.Close()
			return nil, fmt.Errorf("pragma %s failed: %w", p, err)
		}
	}

	d := &Database{db: conn}
	if err := d.migrate(); err != nil {
		conn.Close()
		return nil, err
	}
	return d, nil
}

// migrate creates the 3 normalized inverted index tables and their indices.
func (d *Database) migrate() error {
	schema := `
	CREATE TABLE IF NOT EXISTS documents (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		url TEXT NOT NULL UNIQUE,
		title TEXT NOT NULL,
		snippet TEXT NOT NULL DEFAULT '',
		word_count INTEGER NOT NULL DEFAULT 0,
		crawled_at DATETIME NOT NULL
	);

	CREATE TABLE IF NOT EXISTS terms (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		term TEXT NOT NULL UNIQUE
	);

	CREATE TABLE IF NOT EXISTS document_terms (
		term_id INTEGER NOT NULL,
		document_id INTEGER NOT NULL,
		term_frequency INTEGER NOT NULL,
		PRIMARY KEY (term_id, document_id),
		FOREIGN KEY (term_id) REFERENCES terms(id) ON DELETE CASCADE,
		FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
	);

	CREATE INDEX IF NOT EXISTS idx_terms_term ON terms(term);
	CREATE INDEX IF NOT EXISTS idx_doc_terms_term ON document_terms(term_id);
	CREATE INDEX IF NOT EXISTS idx_doc_terms_doc ON document_terms(document_id);
	`
	_, err := d.db.Exec(schema)
	if err != nil {
		return fmt.Errorf("migration failed: %w", err)
	}
	return nil
}

// Close gracefully closes the database.
func (d *Database) Close() error {
	return d.db.Close()
}

// BatchInsert executes a high-speed atomic transaction inserting documents, extracting unique terms,
// and establishing term frequency postings. Designed specifically for the dedicated DB writer goroutine.
func (d *Database) BatchInsert(docs []ParsedDocument) error {
	if len(docs) == 0 {
		return nil
	}

	d.mu.Lock()
	defer d.mu.Unlock()

	tx, err := d.db.Begin()
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	stmtDoc, err := tx.Prepare(`
		INSERT INTO documents (url, title, snippet, word_count, crawled_at)
		VALUES (?, ?, ?, ?, ?)
		ON CONFLICT(url) DO UPDATE SET
			title=excluded.title,
			snippet=excluded.snippet,
			word_count=excluded.word_count,
			crawled_at=excluded.crawled_at
		RETURNING id;
	`)
	if err != nil {
		return fmt.Errorf("prepare doc stmt error: %w", err)
	}
	defer stmtDoc.Close()

	stmtTermInsert, err := tx.Prepare(`INSERT OR IGNORE INTO terms (term) VALUES (?);`)
	if err != nil {
		return fmt.Errorf("prepare term insert stmt error: %w", err)
	}
	defer stmtTermInsert.Close()

	stmtTermSelect, err := tx.Prepare(`SELECT id FROM terms WHERE term = ?;`)
	if err != nil {
		return fmt.Errorf("prepare term select stmt error: %w", err)
	}
	defer stmtTermSelect.Close()

	stmtDocTerm, err := tx.Prepare(`
		INSERT INTO document_terms (term_id, document_id, term_frequency)
		VALUES (?, ?, ?)
		ON CONFLICT(term_id, document_id) DO UPDATE SET
			term_frequency = excluded.term_frequency;
	`)
	if err != nil {
		return fmt.Errorf("prepare doc_term stmt error: %w", err)
	}
	defer stmtDocTerm.Close()

	termCache := make(map[string]int64)

	now := time.Now()
	for _, doc := range docs {
		var docID int64
		err := stmtDoc.QueryRow(doc.URL, doc.Title, doc.Snippet, doc.WordCount, now).Scan(&docID)
		if err != nil {
			// If scan fails due to conflict or driver variance, query ID directly
			row := tx.QueryRow(`SELECT id FROM documents WHERE url = ?;`, doc.URL)
			if scanErr := row.Scan(&docID); scanErr != nil {
				continue
			}
		}

		for term, freq := range doc.Terms {
			cleanTerm := strings.ToLower(strings.TrimSpace(term))
			if len(cleanTerm) < 2 {
				continue
			}

			termID, exists := termCache[cleanTerm]
			if !exists {
				if _, err := stmtTermInsert.Exec(cleanTerm); err != nil {
					return fmt.Errorf("insert term %s failed: %w", cleanTerm, err)
				}
				if err := stmtTermSelect.QueryRow(cleanTerm).Scan(&termID); err != nil {
					return fmt.Errorf("select term %s failed: %w", cleanTerm, err)
				}
				termCache[cleanTerm] = termID
			}

			if _, err := stmtDocTerm.Exec(termID, docID, freq); err != nil {
				return fmt.Errorf("insert doc_term (%d, %d) failed: %w", termID, docID, err)
			}
		}
	}

	return tx.Commit()
}

// TokenizeQuery splits a user search query into lowercase keywords.
func TokenizeQuery(query string) []string {
	matches := wordRegex.FindAllString(strings.ToLower(query), -1)
	var words []string
	seen := make(map[string]bool)
	for _, m := range matches {
		if !seen[m] {
			seen[m] = true
			words = append(words, m)
		}
	}
	return words
}

// Search evaluates a multi-word search query using dynamic query-time TF-IDF relevance ranking.
func (d *Database) Search(query string, limit int) ([]SearchResult, error) {
	d.mu.RLock()
	defer d.mu.RUnlock()

	terms := TokenizeQuery(query)
	if len(terms) == 0 {
		return []SearchResult{}, nil
	}
	if limit <= 0 {
		limit = 25
	}

	// 1. Total document count in corpus (N)
	var totalDocs int64
	err := d.db.QueryRow("SELECT COUNT(*) FROM documents").Scan(&totalDocs)
	if err != nil || totalDocs == 0 {
		return []SearchResult{}, nil
	}

	// 2. Fetch Document Frequency (DF) and calculate IDF for each query term
	type termInfo struct {
		termID int64
		idf    float64
	}
	validTerms := make(map[string]termInfo)

	for _, t := range terms {
		var termID int64
		err := d.db.QueryRow("SELECT id FROM terms WHERE term = ?", t).Scan(&termID)
		if err != nil {
			continue // Term not indexed in corpus
		}

		var docFrequency int64
		err = d.db.QueryRow("SELECT COUNT(*) FROM document_terms WHERE term_id = ?", termID).Scan(&docFrequency)
		if err != nil || docFrequency == 0 {
			continue
		}

		// Smooth Inverse Document Frequency formula:
		// IDF = ln((N + 1) / (DF + 1)) + 1.0
		idf := math.Log(float64(totalDocs+1)/float64(docFrequency+1)) + 1.0
		validTerms[t] = termInfo{termID: termID, idf: idf}
	}

	if len(validTerms) == 0 {
		return []SearchResult{}, nil
	}

	// 3. Accumulate scores per document: Score(D) = sum( TF(t, D) * IDF(t) )
	type docAccumulator struct {
		docID        int64
		url          string
		title        string
		snippet      string
		wordCount    int
		score        float64
		matchedTerms map[string]bool
	}

	docMap := make(map[int64]*docAccumulator)

	for tString, tInfo := range validTerms {
		rows, err := d.db.Query(`
			SELECT d.id, d.url, d.title, d.snippet, d.word_count, dt.term_frequency
			FROM document_terms dt
			JOIN documents d ON dt.document_id = d.id
			WHERE dt.term_id = ?
		`, tInfo.termID)
		if err != nil {
			return nil, fmt.Errorf("query postings for term %s failed: %w", tString, err)
		}

		for rows.Next() {
			var id int64
			var url, title, snippet string
			var wordCount, tf int

			if err := rows.Scan(&id, &url, &title, &snippet, &wordCount, &tf); err != nil {
				rows.Close()
				return nil, err
			}

			acc, exists := docMap[id]
			if !exists {
				acc = &docAccumulator{
					docID:        id,
					url:          url,
					title:        title,
					snippet:      snippet,
					wordCount:    wordCount,
					score:        0,
					matchedTerms: make(map[string]bool),
				}
				docMap[id] = acc
			}

			// Sublinear TF scaling to dampen repeated words: 1 + ln(TF)
			tfWeight := 1.0 + math.Log(float64(tf))
			termScore := tfWeight * tInfo.idf

			acc.score += termScore
			acc.matchedTerms[tString] = true
		}
		rows.Close()
	}

	// 4. Normalize by document length to prevent long documents from dominating unfairly
	var results []SearchResult
	for _, acc := range docMap {
		normalizedScore := acc.score
		if acc.wordCount > 0 {
			// Cosine length dampener
			lengthNorm := math.Sqrt(float64(acc.wordCount))
			normalizedScore = (acc.score / lengthNorm) * 10.0
		}

		// Term match coordination factor: reward documents containing more of the queried terms
		coordination := float64(len(acc.matchedTerms)) / float64(len(terms))
		finalScore := normalizedScore * (0.5 + 0.5*coordination)

		var matched []string
		for term := range acc.matchedTerms {
			matched = append(matched, term)
		}
		sort.Strings(matched)

		results = append(results, SearchResult{
			DocumentID:   acc.docID,
			URL:          acc.url,
			Title:        acc.title,
			Snippet:      acc.snippet,
			Score:        math.Round(finalScore*100) / 100,
			WordCount:    acc.wordCount,
			MatchedTerms: matched,
		})
	}

	// 5. Rank by score descending
	sort.Slice(results, func(i, j int) bool {
		if results[i].Score == results[j].Score {
			return len(results[i].MatchedTerms) > len(results[j].MatchedTerms)
		}
		return results[i].Score > results[j].Score
	})

	if len(results) > limit {
		results = results[:limit]
	}
	return results, nil
}

// GetStats returns current aggregate metrics from the SQLite database.
func (d *Database) GetStats() (DBStats, error) {
	d.mu.RLock()
	defer d.mu.RUnlock()

	var stats DBStats
	_ = d.db.QueryRow("SELECT COUNT(*) FROM documents").Scan(&stats.TotalDocuments)
	_ = d.db.QueryRow("SELECT COUNT(*) FROM terms").Scan(&stats.TotalTerms)
	_ = d.db.QueryRow("SELECT COUNT(*) FROM document_terms").Scan(&stats.TotalPostings)

	return stats, nil
}

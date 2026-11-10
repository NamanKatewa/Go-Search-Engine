# Project Documentation: High-Performance Desktop Search Engine in Go

**Course:** ENSP465 — New Age Programming Languages Lab  
**Institution:** School of Engineering & Technology, Department of Computer Science & Engineering, K.R. Mangalam University  
**Academic Year:** 2026–2027 (Semester 5)  
**Project Lead:** Naman Katewa (Roll No: 2401830002, B.Sc. Hons. Cyber Security)  
**Team Members:**  
- K Sai Vignesh Yadav (Roll No: 2401720006, B.Sc. Hons. Computer Science)  
- Hrishit Kaushal (Roll No: 2501722016, B.Sc. Hons. Computer Science)  

---

## 1. Project Overview & Objectives

### 1.1 Overview
The **Go Desktop Search Engine** is a high-performance, standalone, cloud-independent desktop software system that pairs an autonomous concurrent web crawler with an inverted index database and dynamic query-time information retrieval engine.

Traditional search engines rely on massive distributed clusters, cloud APIs, and heavy runtime telemetry. In contrast, this project demonstrates how compiled systems programming in **Go** and modern desktop bindings can execute high-throughput crawling, memory-safe data structures, and sub-millisecond keyword retrieval directly on consumer desktop hardware without external runtime dependencies.

### 1.2 Objectives
1. **High Concurrency Web Crawling:** Implement a lightweight worker swarm in Go utilizing goroutines and channels to crawl hundreds of pages per second while adhering strictly to `robots.txt` polite scraping rules.
2. **Deterministic Memory Bounds (OOM Prevention):** Eliminate linear RAM growth during massive crawls by replacing hash-map visited sets with an in-memory **Bloom Filter** providing a mathematically bounded false positive rate ($p < 0.1\%$).
3. **Contention-Free Database Indexing:** Prevent SQLite database locking errors (`database is locked`) by routing parsed page tokens across buffered Go channels into a dedicated single-writer goroutine that executes atomic batch transactions.
4. **Dynamic Query-Time Ranking:** Calculate smooth **Term Frequency-Inverse Document Frequency (TF-IDF)** and document length normalization dynamically at query time so the corpus remains instantly searchable without expensive periodic batch rebuilds.
5. **Seamless Cross-Platform Desktop UI:** Package the Go engine into a native desktop executable using **Wails v2** and a high-contrast React dashboard featuring real-time telemetry streaming.

---

## 2. Key Features

- **Concurrent Goroutine Worker Swarm:** Configurable concurrency (2 to 16 workers) with non-blocking channel dispatching and cooperative context-based cancellation (`Start` / `Halt`).
- **Probabilistic Visited Set (Bloom Filter):** Kirsch-Mitzenmacher double-hashing algorithm ($h_i = (h_1 + i \cdot h_2) \pmod m$) with Murmur3 `fmix64` avalanche mixing, saving over 90% RAM compared to standard `map[string]bool` structures.
- **Readability Content Extractor:** Tokenizes clean article text while stripping HTML noise (`<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<aside>`, comments).
- **Normalized Inverted Index Schema:** Three-table normalized SQLite schema (`documents`, `terms`, `document_terms`) operating in Write-Ahead Logging (WAL) mode for maximum read/write concurrency.
- **Sub-Millisecond TF-IDF Search:** Sublinear term frequency weighting ($1 + \ln(TF)$), smooth IDF ($\ln((N+1)/(DF+1)) + 1$), and cosine document length normalization.
- **Real-Time Telemetry & Event Streaming:** Instant UI updates showing crawl throughput (pages/sec), frontier queue size, Bloom filter bit array statistics, and rolling event logs.

---

## 3. Technologies Used

| Layer / Subsystem | Technology | Purpose & Architectural Justification |
| :--- | :--- | :--- |
| **Backend Language** | **Go (Golang 1.26)** | Statically typed systems language with lightweight runtime scheduler, 2KB goroutine stacks, and native channel-based synchronization. |
| **Desktop Shell & IPC** | **Wails v2** | Binds native Go structs directly to WebView2 without bundling Chromium or Node.js; produces small standalone executables (< 17MB). |
| **Frontend Framework** | **React 19 & TypeScript** | Component-driven UI providing strict type-safety matching Go struct bindings; compiled via Vite. |
| **Database Engine** | **SQLite (WAL Mode via pure Go `modernc.org/sqlite`)** | Embedded, serverless SQL engine with zero CGO dependencies; reliable across 32-bit and 64-bit platforms. |
| **HTML Parsing** | **`golang.org/x/net/html`** | Robust DOM tree tokenization for HTML tag stripping and link discovery. |
| **Probabilistic Hashing** | **FNV-1a + Murmur3 `fmix64`** | High-dispersion 64-bit hashing for bit array indexing in the Bloom Filter. |

---

## 4. Implementation Details

### 4.1 System Architecture Pipeline
The architecture follows a decoupled producer-consumer pipeline:

```
[Seed URL] ──> [Frontier Queue (chan string)] ──> [Goroutine Crawler Swarm]
                                                           │
                                             (HTML Fetch & Readability Parse)
                                                           │
                                                           ▼
                                            [Buffered Pipeline (chan ParsedDocument)]
                                                           │
                                                           ▼
                                            [Dedicated DB Writer Goroutine]
                                                           │
                                                 (Batch WAL Transaction)
                                                           │
                                                           ▼
                                            [SQLite Normalized Inverted Index]
                                                           ▲
                                                           │ (Dynamic TF-IDF)
[User Query] ──────────────────────────────────────> [Search Engine API]
```

### 4.2 In-Memory Bloom Filter (Visited Set)
To prevent Out of Memory crashes when tracking visited URLs:
- **Optimal bit array size ($m$):**
  $$m = -\frac{n \ln p}{(\ln 2)^2}$$
- **Optimal number of hash functions ($k$):**
  $$k = \frac{m}{n} \ln 2$$
- For $n = 500,000$ and $p = 0.001$, $m \approx 7,188,793$ bits (877 KB of RAM), compared to ~36 MB required by a standard string hash map.

### 4.3 Database Schema & Concurrency Protection
To prevent `database is locked` concurrency errors when multiple workers finish scraping simultaneously:
1. Crawler workers never write to SQLite directly; they push parsed documents to `docChannel chan db.ParsedDocument`.
2. A single dedicated goroutine drains `docChannel` and flushes batches of 15 documents or every 400ms inside an atomic transaction:
```sql
BEGIN IMMEDIATE;
-- Insert Document
INSERT INTO documents (url, title, snippet, word_count, crawled_at) VALUES (?, ?, ?, ?, ?);
-- Insert Unique Terms
INSERT OR IGNORE INTO terms (term) VALUES (?);
-- Insert Postings
INSERT INTO document_terms (term_id, document_id, term_frequency) VALUES (?, ?, ?);
COMMIT;
```

### 4.4 Dynamic Query-Time TF-IDF Formulation
When a user searches, the engine computes:
$$\text{Score}(D, Q) = \sum_{t \in Q} (1 + \ln(TF(t, D))) \cdot \left(\ln\left(\frac{N + 1}{DF(t) + 1}\right) + 1.0\right) \cdot \frac{1}{\sqrt{\text{word\_count}(D)}}$$
This formula penalizes redundant high-frequency terms, dampens artificially repeated keywords, and prevents giant documents from dominating precise articles.

---

## 5. Working User Interface & Demonstration Screenshots

The application features a clean, high-contrast desktop user interface with two primary views:

### 5.1 Crawler Dashboard (Live Swarm & Pipeline Telemetry)
The Crawler Dashboard allows users to configure the seed URL, page crawl limit, and worker goroutine count. Real-time KPI cards display crawl progress, throughput (pages/sec), frontier queue occupancy, Bloom filter memory metrics, and live streaming worker logs.

![Crawler Dashboard](file:///C:/Users/naman/Documents/GitHub/Go-Search-Engine/docs/screenshots/dashboard.png)
*Figure 1: Real-time Crawler Dashboard demonstrating concurrent goroutine worker execution, Bloom filter memory savings, and SQLite batch commits.*

---

### 5.2 Instant Search Engine (Dynamic TF-IDF Results)
The Search Engine view allows instant querying against the local inverted index. Results display document titles, hyperlinks, word counts, matched query tags, text snippet previews, and dynamic TF-IDF relevance scores with sub-millisecond retrieval latency.

![Search Results](file:///C:/Users/naman/Documents/GitHub/Go-Search-Engine/docs/screenshots/search_results.png)
*Figure 2: Instant Search Interface displaying ranked search results for the query "concurrency goroutines" with dynamic TF-IDF score badges and query latency.*

---

### 5.3 Topic Search & Term Highlighting
Targeted keyword searches (e.g., "bloom filter memory") demonstrate precise inverted index retrieval and term matching.

![Bloom Filter Search](file:///C:/Users/naman/Documents/GitHub/Go-Search-Engine/docs/screenshots/search_bloom.png)
*Figure 3: Search results for "bloom filter memory" highlighting matched keyword pills and relevant extracted text snippets.*

---

## 6. Verification & Test Results

The implementation was validated using unit and integration test suites:

- **Bloom Filter Test (`internal/bloom`):**
  - Verified 100% true positive retention across 5,000 URLs.
  - Measured false positive rate of 1.06% against a 1.00% theoretical bound with only 5.9 KB of bit array memory.
- **Database & Ranking Test (`internal/db`):**
  - Confirmed normalized schema migrations and atomic batch insertions.
  - Verified TF-IDF mathematical scoring and ranking order.
- **End-to-End Crawler Integration (`internal/crawler`):**
  - Spun up local `httptest.Server` with cyclic links and `robots.txt` disallow rules.
  - Validated link extraction, robots.txt compliance, channel pipelining, and automated SQLite persistence.

All tests passed with zero failures (`go test -v ./...`).

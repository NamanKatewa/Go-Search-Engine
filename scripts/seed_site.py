import http.server
import socketserver
import threading
import sys

PAGES = {
    "/robots.txt": ("text/plain", """User-agent: *
Disallow: /private
"""),
    "/": ("text/html", """<!DOCTYPE html>
<html>
<head><title>Systems Engineering & Search Architecture Hub</title></head>
<body>
    <header><h1>Systems Engineering & Information Retrieval Portal</h1></header>
    <nav><a href="/">Home</a></nav>
    <main>
        <h2>High-Performance Systems in Go</h2>
        <p>Modern information retrieval systems require robust concurrency, low memory footprints, and deterministic ranking algorithms. Go's runtime scheduler and lightweight goroutines provide an ideal foundation for building high-throughput web crawlers and local search engines.</p>
        <ul>
            <li><a href="/go-concurrency">Go Concurrency, Goroutines and Buffered Channels</a></li>
            <li><a href="/bloom-filter">Probabilistic Data Structures: In-Memory Bloom Filters</a></li>
            <li><a href="/sqlite-inverted-index">SQLite Inverted Index and Atomic Batch Persistence</a></li>
            <li><a href="/tf-idf-ranking">Mathematical Formulation of Dynamic TF-IDF Relevance Ranking</a></li>
            <li><a href="/wails-desktop">Wails Desktop IPC and Fullstack Type Safety</a></li>
            <li><a href="/polite-scraping">Polite Scraping Protocols and Robots.txt Compliance</a></li>
        </ul>
    </main>
    <footer>ENSP465 Lab Project</footer>
</body>
</html>
"""),
    "/go-concurrency": ("text/html", """<!DOCTYPE html>
<html>
<head><title>Go Concurrency: Goroutines and Buffered Channels</title></head>
<body>
    <h1>Go Concurrency: Goroutines and Buffered Channels</h1>
    <p>Go implements CSP (Communicating Sequential Processes) using goroutines and channels. A goroutine swarm can fetch hundreds of web pages concurrently without allocating heavy OS threads. Each goroutine uses only 2KB of initial stack space.</p>
    <p>To avoid race conditions and database lock contention in SQLite, crawler worker swarms do not write directly to the database. Instead, parsed documents are transferred over a buffered channel to a single dedicated database writer goroutine.</p>
    <p><a href="/sqlite-inverted-index">Learn about SQLite Inverted Index Architecture</a> | <a href="/bloom-filter">Bloom Filter Visited Sets</a></p>
</body>
</html>
"""),
    "/bloom-filter": ("text/html", """<!DOCTYPE html>
<html>
<head><title>In-Memory Bloom Filters for URL Tracking and OOM Prevention</title></head>
<body>
    <h1>In-Memory Bloom Filters for URL Tracking and OOM Prevention</h1>
    <p>Tracking millions of visited URLs in a standard hash map causes Out of Memory (OOM) crashes because string keys consume linear memory. A Bloom filter solves this by mapping URLs across a compact bit array using multiple independent hash functions.</p>
    <p>With Kirsch-Mitzenmacher optimization, k hash values are generated from just two 64-bit hashes: (h1 + i * h2) mod m. This achieves a false positive probability under 0.1% while slashing RAM consumption by over 90%.</p>
    <p><a href="/">Back to Hub</a> | <a href="/go-concurrency">Concurrency Swarm</a></p>
</body>
</html>
"""),
    "/sqlite-inverted-index": ("text/html", """<!DOCTYPE html>
<html>
<head><title>SQLite Inverted Index and Atomic Batch Persistence</title></head>
<body>
    <h1>SQLite Inverted Index and Atomic Batch Persistence</h1>
    <p>An inverted index maps vocabulary terms to the documents where they occur. Our schema stores Documents, Terms, and DocumentTerms with foreign key constraints. Storing raw Term Frequency (TF) avoids costly recalculations as new pages are indexed.</p>
    <p>Using SQLite's Write-Ahead Logging (WAL mode) and atomic multi-row batch inserts inside a single writer goroutine guarantees maximum transaction throughput without encountering database is locked errors.</p>
    <p><a href="/tf-idf-ranking">Read about Dynamic TF-IDF Ranking</a></p>
</body>
</html>
"""),
    "/tf-idf-ranking": ("text/html", """<!DOCTYPE html>
<html>
<head><title>Mathematical Formulation of Dynamic TF-IDF Relevance Ranking</title></head>
<body>
    <h1>Mathematical Formulation of Dynamic TF-IDF Relevance Ranking</h1>
    <p>Term Frequency-Inverse Document Frequency (TF-IDF) balances keyword occurrences with term specificity. Raw Term Frequency TF measures how often a word appears in a document, while smooth IDF = ln((N + 1)/(DF + 1)) + 1 dampens terms that occur everywhere.</p>
    <p>By computing IDF dynamically at query time against the SQLite database, the search engine ranks results with zero stale cache overhead. Cosine document length normalization ensures long pages do not unfairly dominate shorter, precise articles.</p>
    <p><a href="/wails-desktop">Explore Wails Desktop UI</a> | <a href="/">Home</a></p>
</body>
</html>
"""),
    "/wails-desktop": ("text/html", """<!DOCTYPE html>
<html>
<head><title>Wails Desktop IPC and Fullstack Type Safety</title></head>
<body>
    <h1>Wails Desktop IPC and Fullstack Type Safety</h1>
    <p>Wails binds the Go systems backend directly to modern frontend frameworks using Microsoft WebView2 on Windows. Unlike Electron, Wails does not bundle Chromium or Node.js in the final binary, resulting in an executable under 20MB.</p>
    <p>Go structs are bound to the frontend, generating strict TypeScript interfaces for fullstack compile-time type safety. Real-time telemetry events stream crawler metrics directly to React without HTTP polling overhead.</p>
    <p><a href="/polite-scraping">Polite Scraping</a> | <a href="/">Home</a></p>
</body>
</html>
"""),
    "/polite-scraping": ("text/html", """<!DOCTYPE html>
<html>
<head><title>Polite Scraping Protocols and Robots.txt Compliance</title></head>
<body>
    <h1>Polite Scraping Protocols and Robots.txt Compliance</h1>
    <p>Responsible web scraping mandates strict adherence to the Robots Exclusion Standard (robots.txt). The crawler downloads and parses robots.txt for each unique host before fetching target URLs.</p>
    <p>Disallowed prefixes are cached in memory to ensure polite scraping without hammering host servers. Non-HTML binary content is safely filtered out by inspecting HTTP Content-Type headers.</p>
    <p><a href="/">Back to Portal</a></p>
</body>
</html>
""")
}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path in PAGES:
            content_type, body = PAGES[path]
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    def log_message(self, format, *args):
        pass # Quiet logging

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 34116
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"Mock Doc Server running at http://127.0.0.1:{port}")
        httpd.serve_forever()

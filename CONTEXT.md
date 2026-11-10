# Context

Glossary of terms for the Desktop Search Engine.

## Subsystems

- **Search App**: The single Wails + Next.js desktop application that contains both the Crawler Dashboard and the Search Interface.
- **Crawler**: The concurrent Go backend responsible for aggressively fetching web pages, respecting `robots.txt`, extracting links, and emitting real-time metrics via Wails Events.
- **Indexer**: The dedicated Go subsystem (running as a single writer goroutine) that receives parsed pages via a buffered channel, strips HTML noise, and batches inserts into the database.

## Data Structures

- **Inverted Index**: The SQLite database mapping words (terms) to the documents they appear in. It stores raw Term Frequencies (TF), while Inverse Document Frequency (IDF) is calculated dynamically at query time.
- **Frontier Queue**: The in-memory data structure tracking URLs that need to be crawled.
- **Visited Set**: An in-memory Bloom Filter used to track which URLs have already been crawled. This trades a tiny false-positive rate for massive memory savings.

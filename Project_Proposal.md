# Desktop Search Engine - Project Proposal

## Overview
This project is a high-performance, locally hosted desktop search engine. It operates completely independently of the cloud, acting as both a web crawler and a search interface in a single desktop application. The project aims to demonstrate advanced systems engineering concepts in Go, specifically focusing on heavy concurrency, memory-safe data structures, and cross-language type safety.

## Core Features
1. **Concurrent Web Crawler**: A Go-based engine that takes a seed URL and aggressively hunts down valid links using a massive swarm of lightweight goroutines. It respects `robots.txt` and polite scraping rules.
2. **Text Indexer**: The crawler strips HTML noise (navbars, footers) using a readability algorithm, extracting only pure article text.
3. **Local Inverted Index**: A perfectly normalized SQLite database maps terms to documents, storing raw Term Frequencies (TF).
4. **Mathematical Ranking**: Search queries calculate Inverse Document Frequency (IDF) dynamically on the fly to provide mathematically relevant (TF-IDF) search results instantly.
5. **Real-time Desktop Interface**: Packaged using Wails and Next.js, the application provides a seamless desktop UI without requiring terminal commands. 

## Architectural & Technical Highlights
This project was specifically designed to demonstrate a deep understanding of Go and operating system concepts:
- **Concurrency & Channels**: The crawler uses a goroutine swarm for I/O bound fetching. To avoid `database is locked` errors during indexing, all parsed pages are sent over a buffered Go channel to a *single dedicated Database Writer goroutine*, demonstrating safe concurrent data aggregation.
- **Memory Management (OOM Prevention)**: Tracking millions of visited URLs in a standard hash map would consume gigabytes of RAM. This project utilizes an in-memory **Bloom Filter** for the visited set—trading a negligible false-positive rate for massive memory savings.
- **Fullstack Type Safety**: Wails automatically generates strict TypeScript interfaces from the Go structs. This guarantees type safety across the Go backend and the React frontend.
- **Event-Driven UI**: The Go backend streams live crawler metrics (pages/sec, queue size) to the frontend via Wails Events, updating the React UI instantly without HTTP polling.

## Deliverables
1. A standalone desktop executable (Go + Wails + Next.js).
2. A Crawler Dashboard tab featuring real-time streaming metrics.
3. A functional Search tab that queries the local SQLite database and ranks results via TF-IDF instantly.

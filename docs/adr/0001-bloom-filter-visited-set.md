# 1. Use a Bloom Filter for the Visited URL Set

Date: 2026-08-20

## Status

Accepted

## Context

The Crawler needs to keep track of URLs it has already visited to avoid downloading the same page multiple times and getting caught in infinite loops. For a large crawl, tracking every visited URL in a standard hash map (`map[string]bool` in Go) will consume memory linearly. A crawl of millions of pages would consume gigabytes of RAM, risking an Out of Memory (OOM) crash in a desktop application environment.

## Decision

We will use an in-memory **Bloom Filter** to represent the "visited" set of URLs instead of a standard hash map.

## Consequences

- **Positive:** Massive memory savings. A Bloom filter can represent millions of URLs in a few megabytes of memory, ensuring the application remains lightweight and fast regardless of crawl size.
- **Negative:** Bloom filters are probabilistic data structures that can produce false positives. There is a tiny percentage chance that the filter will claim a URL has been visited when it hasn't, causing the crawler to skip a valid page.
- **Mitigation:** The false-positive rate is mathematically tunable. We will configure the Bloom Filter with a sufficiently large bit array and number of hash functions to keep the false-positive rate negligible (e.g., < 0.1%). In the context of a search engine, missing a single page out of thousands is an acceptable trade-off for absolute memory safety.

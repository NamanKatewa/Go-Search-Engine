import React, { useState, useEffect, useRef } from 'react';

interface Metrics {
  isRunning: boolean;
  pagesCrawled: number;
  pagesPerSecond: number;
  queueSize: number;
  totalBloomCount: number;
  bloomMemoryBytes: number;
  bloomFpRate: number;
  totalIndexedDocs: number;
  totalUniqueTerms: number;
  currentUrl: string;
  recentLogs: Array<{
    timestamp: string;
    level: string;
    message: string;
    url: string;
  }>;
}

interface SearchResult {
  documentId: number;
  url: string;
  title: string;
  snippet: string;
  score: number;
  wordCount: number;
  matchedTerms: string[];
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'search' | 'crawler'>('search');

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchTimeMs, setSearchTimeMs] = useState<number | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Crawler state
  const [seedUrl, setSeedUrl] = useState('https://go.dev');
  const [maxPages, setMaxPages] = useState(25);
  const [concurrency, setConcurrency] = useState(4);
  const [isCrawling, setIsCrawling] = useState(false);
  const [metrics, setMetrics] = useState<Metrics>({
    isRunning: false,
    pagesCrawled: 0,
    pagesPerSecond: 0,
    queueSize: 0,
    totalBloomCount: 0,
    bloomMemoryBytes: 898600,
    bloomFpRate: 0.0008,
    totalIndexedDocs: 0,
    totalUniqueTerms: 0,
    currentUrl: '',
    recentLogs: [],
  });

  const searchInputRef = useRef<HTMLInputElement>(null);

  // Read URL query params on mount for direct deep-linking
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get('tab');
    if (tabParam === 'crawler' || tabParam === 'dashboard') {
      setActiveTab('crawler');
    } else {
      setActiveTab('search');
    }
    const qParam = params.get('q');
    if (qParam) {
      setSearchQuery(qParam);
      handleSearch(qParam);
    }
  }, []);

  // Poll metrics every 800ms
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch('/api/metrics');
        if (res.ok) {
          const data: Metrics = await res.json();
          setMetrics(data);
          setIsCrawling(data.isRunning);
        }
      } catch (err) {
        // silent
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 800);
    return () => clearInterval(interval);
  }, []);

  const handleStartCrawl = async () => {
    setIsCrawling(true);
    try {
      await fetch('/api/crawl/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seedUrl, maxPages, concurrency }),
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleStopCrawl = async () => {
    try {
      await fetch('/api/crawl/stop', { method: 'POST' });
      setIsCrawling(false);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSearch = async (queryToSearch?: string) => {
    const q = queryToSearch !== undefined ? queryToSearch : searchQuery;
    if (!q.trim()) return;

    setIsSearching(true);
    setHasSearched(true);
    const start = performance.now();

    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}&limit=25`);
      const elapsed = Math.round((performance.now() - start) * 10) / 10;
      setSearchTimeMs(elapsed);

      if (res.ok) {
        const data: SearchResult[] = await res.json();
        setSearchResults(data);
      } else {
        setSearchResults([]);
      }
    } catch (err) {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#0e1013', color: '#e4e4e7' }}>
      {/* Quiet Header */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 24px',
        borderBottom: '1px solid #1f232b',
        backgroundColor: '#0e1013',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span style={{ fontSize: '14px', fontWeight: 600, color: '#f4f4f5', letterSpacing: '-0.2px' }}>
            Search Engine
          </span>

          <nav style={{ display: 'flex', gap: '4px' }}>
            <button
              onClick={() => {
                setActiveTab('search');
                setTimeout(() => searchInputRef.current?.focus(), 50);
              }}
              style={{
                padding: '4px 10px',
                borderRadius: '5px',
                fontSize: '12.5px',
                fontWeight: activeTab === 'search' ? 600 : 400,
                border: 'none',
                cursor: 'pointer',
                backgroundColor: activeTab === 'search' ? '#1c2029' : 'transparent',
                color: activeTab === 'search' ? '#f4f4f5' : '#8b949e',
              }}
            >
              Search
            </button>
            <button
              onClick={() => setActiveTab('crawler')}
              style={{
                padding: '4px 10px',
                borderRadius: '5px',
                fontSize: '12.5px',
                fontWeight: activeTab === 'crawler' ? 600 : 400,
                border: 'none',
                cursor: 'pointer',
                backgroundColor: activeTab === 'crawler' ? '#1c2029' : 'transparent',
                color: activeTab === 'crawler' ? '#f4f4f5' : '#8b949e',
              }}
            >
              Crawler
            </button>
          </nav>
        </div>

        {/* Quiet status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '12px', color: '#71717a' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              backgroundColor: isCrawling ? '#10b981' : '#52525b',
            }} />
            <span>{isCrawling ? 'Crawling' : 'Idle'}</span>
          </div>
          <span>•</span>
          <span>{metrics.totalIndexedDocs} indexed</span>
        </div>
      </header>

      {/* Main Surface */}
      <main style={{ flex: 1, maxWidth: '860px', width: '100%', margin: '0 auto', padding: '32px 20px' }}>
        {activeTab === 'search' ? (
          <div>
            {/* Search Input Bar */}
            <div style={{ marginBottom: '24px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                backgroundColor: '#14171f',
                border: '1px solid #242936',
                borderRadius: '8px',
                padding: '6px 12px',
                gap: '8px',
              }}>
                <input
                  ref={searchInputRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search indexed articles..."
                  style={{
                    flex: 1,
                    backgroundColor: 'transparent',
                    border: 'none',
                    color: '#f4f4f5',
                    fontSize: '14px',
                    padding: '6px 4px',
                    outline: 'none',
                  }}
                />
                {searchQuery && (
                  <button
                    onClick={() => {
                      setSearchQuery('');
                      searchInputRef.current?.focus();
                    }}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: '#71717a',
                      fontSize: '14px',
                      cursor: 'pointer',
                      padding: '2px 6px',
                    }}
                  >
                    ×
                  </button>
                )}
                <button
                  onClick={() => handleSearch()}
                  disabled={isSearching}
                  style={{
                    padding: '6px 14px',
                    borderRadius: '5px',
                    backgroundColor: '#272d3b',
                    color: '#e4e4e7',
                    border: '1px solid #323a4d',
                    fontSize: '12.5px',
                    fontWeight: 500,
                    cursor: 'pointer',
                  }}
                >
                  {isSearching ? 'Searching...' : 'Search'}
                </button>
              </div>

              {/* Sample keyword chips */}
              <div style={{ display: 'flex', gap: '6px', marginTop: '10px', fontSize: '11.5px', color: '#71717a', flexWrap: 'wrap' }}>
                <span>Try:</span>
                {['concurrency goroutines', 'sqlite database', 'bloom filter memory', 'desktop wails'].map((sample) => (
                  <button
                    key={sample}
                    onClick={() => {
                      setSearchQuery(sample);
                      handleSearch(sample);
                    }}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#93c5fd',
                      cursor: 'pointer',
                      padding: '0 2px',
                      fontSize: '11.5px',
                      textDecoration: 'underline',
                      textUnderlineOffset: '2px',
                    }}
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>

            {/* Results count & latency */}
            {hasSearched && (
              <div style={{
                fontSize: '12px',
                color: '#71717a',
                marginBottom: '16px',
                display: 'flex',
                justifyContent: 'space-between',
              }}>
                <span>Found {searchResults.length} document{searchResults.length === 1 ? '' : 's'}</span>
                {searchTimeMs !== null && <span>{searchTimeMs} ms</span>}
              </div>
            )}

            {/* Results List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {searchResults.length > 0 ? (
                searchResults.map((res, idx) => (
                  <div key={idx} style={{ paddingBottom: '16px', borderBottom: '1px solid #1a1e27' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: '12px' }}>
                      <h2 style={{ fontSize: '15px', fontWeight: 600, color: '#f4f4f5' }}>
                        <a
                          href={res.url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: '#60a5fa', textDecoration: 'none' }}
                        >
                          {res.title || res.url}
                        </a>
                      </h2>
                      <span style={{ fontSize: '11px', color: '#71717a', fontFamily: 'monospace' }}>
                        TF-IDF {res.score.toFixed(2)}
                      </span>
                    </div>

                    <div style={{ fontSize: '11.5px', color: '#10b981', fontFamily: 'monospace', marginTop: '2px', marginBottom: '6px' }}>
                      {res.url}
                    </div>

                    <p style={{ fontSize: '13px', color: '#a1a1aa', lineHeight: '1.55' }}>
                      {res.snippet}
                    </p>

                    {res.matchedTerms && res.matchedTerms.length > 0 && (
                      <div style={{ display: 'flex', gap: '5px', marginTop: '6px', fontSize: '11px', color: '#71717a' }}>
                        <span>Matched:</span>
                        {res.matchedTerms.map((t, tIdx) => (
                          <span key={tIdx} style={{ color: '#c084fc', fontFamily: 'monospace' }}>
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : hasSearched ? (
                <div style={{ textAlign: 'center', padding: '36px 0', color: '#71717a', fontSize: '13px' }}>
                  No matching documents found.
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '48px 0', color: '#52525b', fontSize: '13px' }}>
                  Type a keyword above to search the local inverted index.
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Crawler Tab */
          <div>
            {/* Control Strip */}
            <div style={{
              backgroundColor: '#14171f',
              border: '1px solid #242936',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '20px',
              display: 'flex',
              flexWrap: 'wrap',
              gap: '12px',
              alignItems: 'flex-end',
            }}>
              <div style={{ flex: '3 1 280px' }}>
                <label style={{ display: 'block', fontSize: '11px', color: '#71717a', marginBottom: '4px' }}>
                  Seed URL
                </label>
                <input
                  type="text"
                  value={seedUrl}
                  onChange={(e) => setSeedUrl(e.target.value)}
                  disabled={isCrawling}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '5px',
                    backgroundColor: '#0c0e12',
                    border: '1px solid #272d3b',
                    color: '#f4f4f5',
                    fontSize: '12.5px',
                    fontFamily: 'monospace',
                  }}
                />
              </div>

              <div style={{ flex: '1 1 90px' }}>
                <label style={{ display: 'block', fontSize: '11px', color: '#71717a', marginBottom: '4px' }}>
                  Limit
                </label>
                <input
                  type="number"
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value) || 10)}
                  disabled={isCrawling}
                  min={1}
                  max={2000}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '5px',
                    backgroundColor: '#0c0e12',
                    border: '1px solid #272d3b',
                    color: '#f4f4f5',
                    fontSize: '12.5px',
                    fontFamily: 'monospace',
                  }}
                />
              </div>

              <div style={{ flex: '1 1 120px' }}>
                <label style={{ display: 'block', fontSize: '11px', color: '#71717a', marginBottom: '4px' }}>
                  Workers
                </label>
                <select
                  value={concurrency}
                  onChange={(e) => setConcurrency(parseInt(e.target.value))}
                  disabled={isCrawling}
                  style={{
                    width: '100%',
                    padding: '8px 10px',
                    borderRadius: '5px',
                    backgroundColor: '#0c0e12',
                    border: '1px solid #272d3b',
                    color: '#f4f4f5',
                    fontSize: '12.5px',
                  }}
                >
                  <option value={2}>2 Goroutines</option>
                  <option value={4}>4 Goroutines</option>
                  <option value={8}>8 Goroutines</option>
                  <option value={16}>16 Goroutines</option>
                </select>
              </div>

              <div>
                {!isCrawling ? (
                  <button
                    onClick={handleStartCrawl}
                    style={{
                      padding: '8px 18px',
                      borderRadius: '5px',
                      backgroundColor: '#2563eb',
                      color: '#ffffff',
                      border: 'none',
                      fontSize: '12.5px',
                      fontWeight: 500,
                      cursor: 'pointer',
                    }}
                  >
                    Start Crawl
                  </button>
                ) : (
                  <button
                    onClick={handleStopCrawl}
                    style={{
                      padding: '8px 18px',
                      borderRadius: '5px',
                      backgroundColor: '#dc2626',
                      color: '#ffffff',
                      border: 'none',
                      fontSize: '12.5px',
                      fontWeight: 500,
                      cursor: 'pointer',
                    }}
                  >
                    Stop
                  </button>
                )}
              </div>
            </div>

            {/* Quiet Metrics Readout */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: '12px',
              marginBottom: '20px',
            }}>
              <div style={{ backgroundColor: '#14171f', border: '1px solid #242936', borderRadius: '7px', padding: '12px 14px' }}>
                <div style={{ fontSize: '11px', color: '#71717a' }}>Pages Crawled</div>
                <div style={{ fontSize: '18px', fontWeight: 600, color: '#f4f4f5', marginTop: '2px', fontFamily: 'monospace' }}>
                  {metrics.pagesCrawled} <span style={{ fontSize: '11px', color: '#71717a', fontWeight: 400 }}>/ {maxPages}</span>
                </div>
                <div style={{ fontSize: '11px', color: '#71717a', marginTop: '2px' }}>{metrics.pagesPerSecond} pgs/sec</div>
              </div>

              <div style={{ backgroundColor: '#14171f', border: '1px solid #242936', borderRadius: '7px', padding: '12px 14px' }}>
                <div style={{ fontSize: '11px', color: '#71717a' }}>Queue Depth</div>
                <div style={{ fontSize: '18px', fontWeight: 600, color: '#f4f4f5', marginTop: '2px', fontFamily: 'monospace' }}>
                  {metrics.queueSize}
                </div>
                <div style={{ fontSize: '11px', color: '#71717a', marginTop: '2px' }}>Buffered channel</div>
              </div>

              <div style={{ backgroundColor: '#14171f', border: '1px solid #242936', borderRadius: '7px', padding: '12px 14px' }}>
                <div style={{ fontSize: '11px', color: '#71717a' }}>Bloom Filter</div>
                <div style={{ fontSize: '18px', fontWeight: 600, color: '#f4f4f5', marginTop: '2px', fontFamily: 'monospace' }}>
                  {metrics.totalBloomCount} <span style={{ fontSize: '11px', color: '#71717a', fontWeight: 400 }}>hashes</span>
                </div>
                <div style={{ fontSize: '11px', color: '#71717a', marginTop: '2px' }}>{(metrics.bloomMemoryBytes / 1024).toFixed(0)} KB (FP &lt; 0.1%)</div>
              </div>

              <div style={{ backgroundColor: '#14171f', border: '1px solid #242936', borderRadius: '7px', padding: '12px 14px' }}>
                <div style={{ fontSize: '11px', color: '#71717a' }}>SQLite Inverted Index</div>
                <div style={{ fontSize: '18px', fontWeight: 600, color: '#f4f4f5', marginTop: '2px', fontFamily: 'monospace' }}>
                  {metrics.totalIndexedDocs} <span style={{ fontSize: '11px', color: '#71717a', fontWeight: 400 }}>docs</span>
                </div>
                <div style={{ fontSize: '11px', color: '#71717a', marginTop: '2px' }}>{metrics.totalUniqueTerms} unique terms</div>
              </div>
            </div>

            {/* Quiet Console Log */}
            <div style={{
              backgroundColor: '#10131a',
              border: '1px solid #242936',
              borderRadius: '7px',
              padding: '12px 14px',
            }}>
              <div style={{ fontSize: '11px', color: '#71717a', marginBottom: '8px' }}>
                Crawl Activity Log
              </div>
              <div style={{
                height: '240px',
                overflowY: 'auto',
                fontFamily: 'monospace',
                fontSize: '11px',
                lineHeight: '1.6',
                color: '#94a3b8',
              }}>
                {metrics.recentLogs && metrics.recentLogs.length > 0 ? (
                  metrics.recentLogs.map((log, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: '8px' }}>
                      <span style={{ color: '#52525b' }}>{log.timestamp}</span>
                      <span style={{ color: log.level === 'SUCCESS' ? '#34d399' : log.level === 'ERROR' ? '#f87171' : log.level === 'WARN' ? '#fbbf24' : '#60a5fa' }}>
                        [{log.level}]
                      </span>
                      <span style={{ color: '#d4d4d8', flex: 1 }}>{log.message}</span>
                      {log.url && <span style={{ color: '#52525b', maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.url}</span>}
                    </div>
                  ))
                ) : (
                  <div style={{ color: '#52525b', padding: '16px 0', textAlign: 'center' }}>
                    No activity. Start a crawl above to begin.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Quiet Footer */}
      <footer style={{
        padding: '12px 24px',
        borderTop: '1px solid #1a1e27',
        fontSize: '11px',
        color: '#52525b',
        display: 'flex',
        justifyContent: 'space-between',
      }}>
        <span>ENSP465 · K.R. Mangalam University</span>
        <span>Lead: Naman Katewa · Team: K Sai Vignesh Yadav, Hrishit Kaushal</span>
      </footer>
    </div>
  );
}

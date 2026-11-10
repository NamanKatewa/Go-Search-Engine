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
  const [activeTab, setActiveTab] = useState<'dashboard' | 'search'>('dashboard');

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
    bloomMemoryBytes: 625000,
    bloomFpRate: 0.0008,
    totalIndexedDocs: 0,
    totalUniqueTerms: 0,
    currentUrl: '',
    recentLogs: [],
  });

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchTimeMs, setSearchTimeMs] = useState<number | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Read URL query params on mount for deep-linking (e.g. ?tab=search&q=concurrency)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get('tab');
    if (tabParam === 'search') {
      setActiveTab('search');
    }
    const qParam = params.get('q');
    if (qParam) {
      setSearchQuery(qParam);
      handleSearch(qParam);
    }
  }, []);

  // Poll metrics every 600ms
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
        // Handle standalone or wails mode
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 700);
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
      console.error('Failed to start crawl:', err);
    }
  };

  const handleStopCrawl = async () => {
    try {
      await fetch('/api/crawl/stop', { method: 'POST' });
      setIsCrawling(false);
    } catch (err) {
      console.error('Failed to stop crawl:', err);
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
      console.error('Search failed:', err);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Estimated RAM savings of Bloom filter vs raw strings hash map
  const rawHashMapBytes = metrics.totalBloomCount * 72; // ~72 bytes per string entry in Go map
  const ramSavedPercent = rawHashMapBytes > 0 
    ? Math.max(0, Math.round(((rawHashMapBytes - metrics.bloomMemoryBytes) / rawHashMapBytes) * 100))
    : 92;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#0b1120' }}>
      {/* Top Navbar */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '16px 32px',
        backgroundColor: '#0f172a',
        borderBottom: '1px solid #1e293b',
        boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '20px',
            color: '#fff',
            boxShadow: '0 0 16px rgba(6, 182, 212, 0.4)',
          }}>
            Go
          </div>
          <div>
            <h1 style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.3px' }}>
              Desktop Search Engine
            </h1>
            <p style={{ fontSize: '12px', color: '#64748b', fontWeight: 500 }}>
              Concurrent Go Crawler & Inverted Index (ENSP465)
            </p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div style={{
          display: 'flex',
          backgroundColor: '#1e293b',
          borderRadius: '10px',
          padding: '4px',
          gap: '4px',
        }}>
          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              padding: '8px 20px',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              transition: 'all 0.2s',
              backgroundColor: activeTab === 'dashboard' ? '#0284c7' : 'transparent',
              color: activeTab === 'dashboard' ? '#ffffff' : '#94a3b8',
            }}
          >
            Crawler Dashboard
          </button>
          <button
            onClick={() => setActiveTab('search')}
            style={{
              padding: '8px 20px',
              borderRadius: '8px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              transition: 'all 0.2s',
              backgroundColor: activeTab === 'search' ? '#0284c7' : 'transparent',
              color: activeTab === 'search' ? '#ffffff' : '#94a3b8',
            }}
          >
            Search Engine
          </button>
        </div>

        {/* Live Status indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 14px',
            borderRadius: '20px',
            backgroundColor: isCrawling ? 'rgba(16, 185, 129, 0.15)' : 'rgba(100, 116, 139, 0.15)',
            border: isCrawling ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(100, 116, 139, 0.3)',
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isCrawling ? '#10b981' : '#64748b',
              boxShadow: isCrawling ? '0 0 10px #10b981' : 'none',
            }} />
            <span style={{
              fontSize: '12px',
              fontWeight: 600,
              color: isCrawling ? '#34d399' : '#94a3b8',
            }}>
              {isCrawling ? 'Swarm Crawling' : 'Engine Idle'}
            </span>
          </div>

          <div style={{
            fontSize: '12px',
            color: '#94a3b8',
            backgroundColor: '#1e293b',
            padding: '6px 14px',
            borderRadius: '8px',
            fontWeight: 600,
          }}>
            Corpus: <strong style={{ color: '#38bdf8' }}>{metrics.totalIndexedDocs}</strong> docs
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main style={{ flex: 1, padding: '28px 32px', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
        {activeTab === 'dashboard' ? (
          <div>
            {/* Top Config Card */}
            <div style={{
              backgroundColor: '#0f172a',
              border: '1px solid #1e293b',
              borderRadius: '14px',
              padding: '22px 26px',
              marginBottom: '24px',
              display: 'flex',
              flexWrap: 'wrap',
              gap: '20px',
              alignItems: 'flex-end',
              boxShadow: '0 6px 24px rgba(0,0,0,0.25)',
            }}>
              <div style={{ flex: '3 1 300px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px' }}>
                  SEED URL (ENTRYPOINT)
                </label>
                <input
                  type="text"
                  value={seedUrl}
                  onChange={(e) => setSeedUrl(e.target.value)}
                  disabled={isCrawling}
                  placeholder="https://example.com"
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    fontSize: '14px',
                    fontFamily: 'monospace',
                    outline: 'none',
                  }}
                />
              </div>

              <div style={{ flex: '1 1 120px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px' }}>
                  PAGE LIMIT
                </label>
                <input
                  type="number"
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value) || 10)}
                  disabled={isCrawling}
                  min={1}
                  max={1000}
                  style={{
                    width: '100%',
                    padding: '12px 14px',
                    borderRadius: '8px',
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    fontSize: '14px',
                    outline: 'none',
                  }}
                />
              </div>

              <div style={{ flex: '1 1 140px' }}>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px' }}>
                  GOROUTINES (SWARM)
                </label>
                <select
                  value={concurrency}
                  onChange={(e) => setConcurrency(parseInt(e.target.value))}
                  disabled={isCrawling}
                  style={{
                    width: '100%',
                    padding: '12px 14px',
                    borderRadius: '8px',
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    fontSize: '14px',
                    outline: 'none',
                  }}
                >
                  <option value={2}>2 Workers</option>
                  <option value={4}>4 Workers</option>
                  <option value={8}>8 Workers</option>
                  <option value={16}>16 Workers</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '12px' }}>
                {!isCrawling ? (
                  <button
                    onClick={handleStartCrawl}
                    style={{
                      padding: '12px 28px',
                      borderRadius: '8px',
                      backgroundColor: '#0284c7',
                      color: '#fff',
                      fontSize: '14px',
                      fontWeight: 700,
                      border: 'none',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      boxShadow: '0 4px 14px rgba(2, 132, 199, 0.35)',
                    }}
                  >
                    Start Crawl Swarm
                  </button>
                ) : (
                  <button
                    onClick={handleStopCrawl}
                    style={{
                      padding: '12px 28px',
                      borderRadius: '8px',
                      backgroundColor: '#ef4444',
                      color: '#fff',
                      fontSize: '14px',
                      fontWeight: 700,
                      border: 'none',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      boxShadow: '0 4px 14px rgba(239, 68, 68, 0.35)',
                    }}
                  >
                    Halt Crawl
                  </button>
                )}
              </div>
            </div>

            {/* Metrics KPI Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: '18px',
              marginBottom: '24px',
            }}>
              {/* Card 1 */}
              <div style={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '12px',
                padding: '20px',
                position: 'relative',
                overflow: 'hidden',
              }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#06b6d4', letterSpacing: '0.5px' }}>
                  CRAWL PROGRESS
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '10px' }}>
                  <span style={{ fontSize: '32px', fontWeight: 800, color: '#f8fafc' }}>
                    {metrics.pagesCrawled}
                  </span>
                  <span style={{ fontSize: '14px', color: '#64748b' }}>
                    / {maxPages} pages
                  </span>
                </div>
                <div style={{ marginTop: '8px', fontSize: '13px', color: '#94a3b8' }}>
                  Throughput: <strong style={{ color: '#38bdf8' }}>{metrics.pagesPerSecond}</strong> pages/sec
                </div>
              </div>

              {/* Card 2 */}
              <div style={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '12px',
                padding: '20px',
              }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#a855f7', letterSpacing: '0.5px' }}>
                  FRONTIER QUEUE
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '10px' }}>
                  <span style={{ fontSize: '32px', fontWeight: 800, color: '#f8fafc' }}>
                    {metrics.queueSize}
                  </span>
                  <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                    buffered URLs
                  </span>
                </div>
                <div style={{ marginTop: '8px', fontSize: '13px', color: '#94a3b8' }}>
                  Thread-safe Go channel pipeline
                </div>
              </div>

              {/* Card 3: Bloom Filter */}
              <div style={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '12px',
                padding: '20px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: '#10b981', letterSpacing: '0.5px' }}>
                    BLOOM FILTER (VISITED SET)
                  </span>
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    color: '#34d399',
                    padding: '2px 8px',
                    borderRadius: '6px',
                  }}>
                    ~{ramSavedPercent}% RAM Saved
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '10px' }}>
                  <span style={{ fontSize: '32px', fontWeight: 800, color: '#f8fafc' }}>
                    {metrics.totalBloomCount}
                  </span>
                  <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                    tracked URLs
                  </span>
                </div>
                <div style={{ marginTop: '8px', fontSize: '12px', color: '#94a3b8' }}>
                  Size: {(metrics.bloomMemoryBytes / 1024).toFixed(1)} KB | FP Bound: &lt; 0.1%
                </div>
              </div>

              {/* Card 4: SQLite Index */}
              <div style={{
                backgroundColor: '#0f172a',
                border: '1px solid #1e293b',
                borderRadius: '12px',
                padding: '20px',
              }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#f59e0b', letterSpacing: '0.5px' }}>
                  LOCAL SQLITE INVERTED INDEX
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '10px' }}>
                  <span style={{ fontSize: '32px', fontWeight: 800, color: '#f8fafc' }}>
                    {metrics.totalIndexedDocs}
                  </span>
                  <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                    docs ({metrics.totalUniqueTerms} unique terms)
                  </span>
                </div>
                <div style={{ marginTop: '8px', fontSize: '13px', color: '#94a3b8' }}>
                  Dedicated single-writer goroutine
                </div>
              </div>
            </div>

            {/* Live Crawler Swarm Activity Stream */}
            <div style={{
              backgroundColor: '#0f172a',
              border: '1px solid #1e293b',
              borderRadius: '14px',
              padding: '20px',
              boxShadow: '0 6px 24px rgba(0,0,0,0.25)',
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '14px',
                paddingBottom: '12px',
                borderBottom: '1px solid #1e293b',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: isCrawling ? '#06b6d4' : '#64748b',
                  }} />
                  <h3 style={{ fontSize: '14px', fontWeight: 700, color: '#f1f5f9' }}>
                    CRAWLER SWARM TELEMETRY & DATABASE WRITER LOGS
                  </h3>
                </div>
                <span style={{ fontSize: '12px', color: '#64748b', fontFamily: 'monospace' }}>
                  Streaming live events
                </span>
              </div>

              <div style={{
                height: '280px',
                overflowY: 'auto',
                backgroundColor: '#050b14',
                borderRadius: '8px',
                padding: '12px 16px',
                fontFamily: 'monospace',
                fontSize: '12px',
                lineHeight: '1.7',
                border: '1px solid #1e293b',
              }}>
                {metrics.recentLogs && metrics.recentLogs.length > 0 ? (
                  metrics.recentLogs.map((log, idx) => {
                    let levelColor = '#94a3b8';
                    if (log.level === 'SUCCESS') levelColor = '#34d399';
                    if (log.level === 'WARN') levelColor = '#fbbf24';
                    if (log.level === 'ERROR') levelColor = '#f87171';
                    if (log.level === 'INFO') levelColor = '#38bdf8';

                    return (
                      <div key={idx} style={{ display: 'flex', gap: '12px', marginBottom: '4px' }}>
                        <span style={{ color: '#475569' }}>[{log.timestamp}]</span>
                        <span style={{ color: levelColor, fontWeight: 700, minWidth: '65px' }}>
                          [{log.level}]
                        </span>
                        <span style={{ color: '#e2e8f0', flex: 1 }}>{log.message}</span>
                        {log.url && (
                          <span style={{ color: '#64748b', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {log.url}
                          </span>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div style={{ color: '#64748b', padding: '16px 0', textAlign: 'center' }}>
                    No events yet. Click "Start Crawl Swarm" above to begin indexing pages.
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Search Interface Tab */
          <div>
            {/* Search Bar Container */}
            <div style={{
              backgroundColor: '#0f172a',
              border: '1px solid #1e293b',
              borderRadius: '16px',
              padding: '30px',
              marginBottom: '28px',
              boxShadow: '0 8px 30px rgba(0,0,0,0.3)',
            }}>
              <h2 style={{ fontSize: '20px', fontWeight: 800, color: '#f8fafc', marginBottom: '8px' }}>
                Instant Local Index Search
              </h2>
              <p style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '20px' }}>
                Ranked using dynamic on-the-fly <strong>TF-IDF</strong> calculations over SQLite inverted index tables.
              </p>

              <div style={{ display: 'flex', gap: '12px' }}>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Enter keywords (e.g. concurrency goroutines, memory bloom filter, wails)..."
                  style={{
                    flex: 1,
                    padding: '14px 20px',
                    borderRadius: '10px',
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    color: '#f8fafc',
                    fontSize: '15px',
                    outline: 'none',
                  }}
                />
                <button
                  onClick={() => handleSearch()}
                  disabled={isSearching}
                  style={{
                    padding: '14px 32px',
                    borderRadius: '10px',
                    backgroundColor: '#0284c7',
                    color: '#fff',
                    fontSize: '15px',
                    fontWeight: 700,
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    boxShadow: '0 4px 16px rgba(2, 132, 199, 0.4)',
                  }}
                >
                  {isSearching ? 'Querying...' : 'Search'}
                </button>
              </div>

              {/* Sample Queries */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '16px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>Try queries:</span>
                {['concurrency goroutines', 'sqlite database', 'bloom filter memory', 'desktop wails'].map((sample) => (
                  <button
                    key={sample}
                    onClick={() => {
                      setSearchQuery(sample);
                      handleSearch(sample);
                    }}
                    style={{
                      padding: '4px 12px',
                      borderRadius: '6px',
                      backgroundColor: '#1e293b',
                      border: '1px solid #334155',
                      color: '#38bdf8',
                      fontSize: '12px',
                      cursor: 'pointer',
                    }}
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>

            {/* Results Header */}
            {hasSearched && (
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '18px',
                padding: '0 4px',
              }}>
                <span style={{ fontSize: '14px', color: '#94a3b8' }}>
                  Found <strong style={{ color: '#f8fafc' }}>{searchResults.length}</strong> relevant documents
                </span>
                {searchTimeMs !== null && (
                  <span style={{
                    fontSize: '12px',
                    color: '#34d399',
                    fontFamily: 'monospace',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    padding: '4px 10px',
                    borderRadius: '6px',
                    border: '1px solid rgba(16, 185, 129, 0.25)',
                  }}>
                    Query Latency: {searchTimeMs} ms
                  </span>
                )}
              </div>
            )}

            {/* Search Results List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {searchResults.length > 0 ? (
                searchResults.map((res, idx) => (
                  <div
                    key={idx}
                    style={{
                      backgroundColor: '#0f172a',
                      border: '1px solid #1e293b',
                      borderRadius: '12px',
                      padding: '20px 24px',
                      transition: 'border-color 0.2s',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px' }}>
                      <div>
                        <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#38bdf8', marginBottom: '6px' }}>
                          <a
                            href={res.url}
                            target="_blank"
                            rel="noreferrer"
                            style={{ color: 'inherit', textDecoration: 'none' }}
                          >
                            {res.title || res.url}
                          </a>
                        </h3>
                        <a
                          href={res.url}
                          target="_blank"
                          rel="noreferrer"
                          style={{
                            fontSize: '12px',
                            color: '#10b981',
                            fontFamily: 'monospace',
                            textDecoration: 'none',
                            display: 'block',
                            marginBottom: '10px',
                          }}
                        >
                          {res.url}
                        </a>
                      </div>

                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'flex-end',
                        minWidth: '100px',
                      }}>
                        <div style={{
                          padding: '4px 10px',
                          borderRadius: '8px',
                          backgroundColor: 'rgba(2, 132, 199, 0.18)',
                          border: '1px solid rgba(2, 132, 199, 0.35)',
                          color: '#38bdf8',
                          fontSize: '12px',
                          fontWeight: 700,
                          fontFamily: 'monospace',
                        }}>
                          TF-IDF: {res.score.toFixed(2)}
                        </div>
                        <span style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>
                          {res.wordCount} words
                        </span>
                      </div>
                    </div>

                    <p style={{
                      fontSize: '13.5px',
                      color: '#cbd5e1',
                      lineHeight: '1.6',
                      marginTop: '8px',
                    }}>
                      {res.snippet}
                    </p>

                    {/* Matched keywords pills */}
                    {res.matchedTerms && res.matchedTerms.length > 0 && (
                      <div style={{ display: 'flex', gap: '6px', marginTop: '12px', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '11px', color: '#64748b', alignSelf: 'center' }}>Matched:</span>
                        {res.matchedTerms.map((term, tIdx) => (
                          <span
                            key={tIdx}
                            style={{
                              padding: '2px 8px',
                              borderRadius: '4px',
                              backgroundColor: '#1e293b',
                              color: '#a855f7',
                              fontSize: '11px',
                              fontWeight: 600,
                              fontFamily: 'monospace',
                            }}
                          >
                            #{term}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              ) : hasSearched ? (
                <div style={{
                  padding: '48px',
                  textAlign: 'center',
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '12px',
                  color: '#94a3b8',
                }}>
                  <p style={{ fontSize: '16px', fontWeight: 600, marginBottom: '6px' }}>No matching documents found</p>
                  <p style={{ fontSize: '13px', color: '#64748b' }}>
                    Try searching for different terms or crawl more pages in the Crawler Dashboard.
                  </p>
                </div>
              ) : (
                <div style={{
                  padding: '60px',
                  textAlign: 'center',
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '12px',
                  color: '#64748b',
                }}>
                  <p style={{ fontSize: '15px', fontWeight: 600, color: '#94a3b8' }}>Search the Local Corpus</p>
                  <p style={{ fontSize: '13px', marginTop: '6px' }}>
                    Enter any query above or choose a sample search to retrieve mathematically ranked results.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        padding: '16px 32px',
        backgroundColor: '#0f172a',
        borderTop: '1px solid #1e293b',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '12px',
        color: '#64748b',
      }}>
        <span>ENSP465: New Age Programming Languages Lab — K.R. Mangalam University</span>
        <span>Lead: Naman Katewa | Team: K Sai Vignesh Yadav, Hrishit Kaushal</span>
      </footer>
    </div>
  );
}

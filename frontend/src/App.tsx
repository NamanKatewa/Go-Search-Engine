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

  // Crawler Configuration
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

  // Search Configuration
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchTimeMs, setSearchTimeMs] = useState<number | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);

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
        // Backend offline or polling variance
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 600);
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

  // Memory calculation: Bloom filter vs raw strings hash map
  const rawHashMapBytes = metrics.totalBloomCount > 0 ? metrics.totalBloomCount * 72 : 72000;
  const ramSavedPercent = rawHashMapBytes > 0 
    ? Math.max(0, Math.min(96, Math.round(((rawHashMapBytes - (metrics.bloomMemoryBytes / 8)) / rawHashMapBytes) * 100)))
    : 92;

  const crawlProgressPercent = maxPages > 0 
    ? Math.min(100, Math.round((metrics.pagesCrawled / maxPages) * 100))
    : 0;

  // Helper to highlight matched terms in snippet
  const highlightSnippet = (snippet: string, terms: string[]) => {
    if (!terms || terms.length === 0) return snippet;
    const regex = new RegExp(`\\b(${terms.join('|')})\\b`, 'gi');
    const parts = snippet.split(regex);
    return parts.map((part, i) => {
      if (terms.some(t => t.toLowerCase() === part.toLowerCase())) {
        return (
          <mark key={i} style={{
            backgroundColor: 'rgba(14, 165, 233, 0.25)',
            color: '#38bdf8',
            fontWeight: 700,
            padding: '1px 3px',
            borderRadius: '3px',
          }}>
            {part}
          </mark>
        );
      }
      return part;
    });
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#080c14' }}>
      {/* Precision Top App Bar */}
      <header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 28px',
        backgroundColor: '#0c121e',
        borderBottom: '1px solid #1a2336',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backdropFilter: 'blur(12px)',
      }}>
        {/* Brand identity */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '9px',
            background: 'linear-gradient(135deg, #0284c7 0%, #10b981 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '17px',
            color: '#ffffff',
            letterSpacing: '-0.5px',
            boxShadow: '0 0 16px rgba(2, 132, 199, 0.4)',
          }}>
            GO
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h1 style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.2px' }}>
                Go Search Engine
              </h1>
              <span style={{
                fontSize: '10px',
                fontWeight: 700,
                color: '#38bdf8',
                backgroundColor: 'rgba(2, 132, 199, 0.15)',
                border: '1px solid rgba(2, 132, 199, 0.3)',
                padding: '1px 6px',
                borderRadius: '4px',
                fontFamily: 'monospace',
              }}>
                v1.0 WAL
              </span>
            </div>
            <p style={{ fontSize: '11px', color: '#64748b', fontWeight: 500 }}>
              Concurrent Goroutine Swarm & Inverted Index Engine
            </p>
          </div>
        </div>

        {/* Tactile Segmented Tab Switcher */}
        <div style={{
          display: 'flex',
          backgroundColor: '#060a12',
          border: '1px solid #1a2336',
          borderRadius: '9px',
          padding: '3px',
          gap: '2px',
        }}>
          <button
            onClick={() => setActiveTab('dashboard')}
            style={{
              padding: '7px 18px',
              borderRadius: '7px',
              fontSize: '12.5px',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              transition: 'all 0.18s cubic-bezier(0.16, 1, 0.3, 1)',
              backgroundColor: activeTab === 'dashboard' ? '#1a263c' : 'transparent',
              color: activeTab === 'dashboard' ? '#f8fafc' : '#94a3b8',
              boxShadow: activeTab === 'dashboard' ? '0 2px 8px rgba(0,0,0,0.3)' : 'none',
            }}
          >
            Crawler Dashboard
          </button>
          <button
            onClick={() => {
              setActiveTab('search');
              setTimeout(() => searchInputRef.current?.focus(), 50);
            }}
            style={{
              padding: '7px 18px',
              borderRadius: '7px',
              fontSize: '12.5px',
              fontWeight: 600,
              cursor: 'pointer',
              border: 'none',
              transition: 'all 0.18s cubic-bezier(0.16, 1, 0.3, 1)',
              backgroundColor: activeTab === 'search' ? '#1a263c' : 'transparent',
              color: activeTab === 'search' ? '#f8fafc' : '#94a3b8',
              boxShadow: activeTab === 'search' ? '0 2px 8px rgba(0,0,0,0.3)' : 'none',
            }}
          >
            Search Engine
          </button>
        </div>

        {/* Live Status HUD */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '5px 12px',
            borderRadius: '6px',
            backgroundColor: isCrawling ? 'rgba(16, 185, 129, 0.12)' : '#101624',
            border: isCrawling ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid #1e293b',
          }}>
            <span
              className={isCrawling ? 'pulse-indicator' : ''}
              style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: isCrawling ? '#10b981' : '#64748b',
              }}
            />
            <span style={{
              fontSize: '11.5px',
              fontWeight: 600,
              color: isCrawling ? '#34d399' : '#94a3b8',
              fontFamily: 'monospace',
            }}>
              {isCrawling ? 'SWARM ACTIVE' : 'ENGINE IDLE'}
            </span>
          </div>

          <div style={{
            fontSize: '11.5px',
            color: '#94a3b8',
            backgroundColor: '#101624',
            border: '1px solid #1e293b',
            padding: '5px 12px',
            borderRadius: '6px',
            fontFamily: 'monospace',
          }}>
            Corpus: <strong style={{ color: '#38bdf8' }}>{metrics.totalIndexedDocs}</strong> docs
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '24px 28px', maxWidth: '1400px', width: '100%', margin: '0 auto' }}>
        {activeTab === 'dashboard' ? (
          <div>
            {/* Command & Control Deck */}
            <div style={{
              backgroundColor: '#0c121e',
              border: '1px solid #1a2336',
              borderRadius: '12px',
              padding: '20px 24px',
              marginBottom: '20px',
              display: 'flex',
              flexWrap: 'wrap',
              gap: '16px',
              alignItems: 'flex-end',
            }}>
              {/* Seed URL */}
              <div style={{ flex: '3 1 320px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <label style={{ fontSize: '11px', fontWeight: 700, color: '#94a3b8', letterSpacing: '0.4px' }}>
                    SEED URL (ENTRYPOINT)
                  </label>
                  <span style={{ fontSize: '10.5px', color: '#64748b' }}>Robots.txt compliant</span>
                </div>
                <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
                  <input
                    type="text"
                    value={seedUrl}
                    onChange={(e) => setSeedUrl(e.target.value)}
                    disabled={isCrawling}
                    placeholder="https://go.dev"
                    style={{
                      width: '100%',
                      padding: '10px 14px',
                      borderRadius: '7px',
                      backgroundColor: '#070b12',
                      border: '1px solid #1e293b',
                      color: '#f8fafc',
                      fontSize: '13px',
                      fontFamily: 'monospace',
                      outline: 'none',
                    }}
                  />
                </div>
              </div>

              {/* Page Limit */}
              <div style={{ flex: '1 1 120px' }}>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: '#94a3b8', letterSpacing: '0.4px', marginBottom: '6px' }}>
                  PAGE CEILING
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
                    padding: '10px 12px',
                    borderRadius: '7px',
                    backgroundColor: '#070b12',
                    border: '1px solid #1e293b',
                    color: '#f8fafc',
                    fontSize: '13px',
                    fontFamily: 'monospace',
                    outline: 'none',
                  }}
                />
              </div>

              {/* Concurrency Selector */}
              <div style={{ flex: '1 1 150px' }}>
                <label style={{ display: 'block', fontSize: '11px', fontWeight: 700, color: '#94a3b8', letterSpacing: '0.4px', marginBottom: '6px' }}>
                  GOROUTINE SWARM
                </label>
                <select
                  value={concurrency}
                  onChange={(e) => setConcurrency(parseInt(e.target.value))}
                  disabled={isCrawling}
                  style={{
                    width: '100%',
                    padding: '10px 12px',
                    borderRadius: '7px',
                    backgroundColor: '#070b12',
                    border: '1px solid #1e293b',
                    color: '#f8fafc',
                    fontSize: '13px',
                    outline: 'none',
                    cursor: 'pointer',
                  }}
                >
                  <option value={2}>2 Workers (Light)</option>
                  <option value={4}>4 Workers (Standard)</option>
                  <option value={8}>8 Workers (Parallel)</option>
                  <option value={16}>16 Workers (Turbo)</option>
                </select>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '10px' }}>
                {!isCrawling ? (
                  <button
                    onClick={handleStartCrawl}
                    style={{
                      padding: '10px 24px',
                      borderRadius: '7px',
                      backgroundColor: '#0284c7',
                      color: '#ffffff',
                      fontSize: '13px',
                      fontWeight: 700,
                      border: 'none',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      boxShadow: '0 2px 10px rgba(2, 132, 199, 0.35)',
                    }}
                  >
                    Start Crawler Swarm
                  </button>
                ) : (
                  <button
                    onClick={handleStopCrawl}
                    style={{
                      padding: '10px 24px',
                      borderRadius: '7px',
                      backgroundColor: '#e11d48',
                      color: '#ffffff',
                      fontSize: '13px',
                      fontWeight: 700,
                      border: 'none',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      boxShadow: '0 2px 10px rgba(225, 29, 72, 0.4)',
                    }}
                  >
                    Halt Workers
                  </button>
                )}
              </div>
            </div>

            {/* Precision KPI Panel Grid */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
              gap: '16px',
              marginBottom: '20px',
            }}>
              {/* Panel 1: Progress */}
              <div style={{
                backgroundColor: '#0c121e',
                border: '1px solid #1a2336',
                borderRadius: '10px',
                padding: '18px 20px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: '#38bdf8', letterSpacing: '0.4px' }}>
                    CRAWL PROGRESS
                  </span>
                  <span style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>
                    {crawlProgressPercent}%
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '8px' }}>
                  <span style={{ fontSize: '28px', fontWeight: 800, color: '#f8fafc', fontFamily: 'monospace' }}>
                    {metrics.pagesCrawled}
                  </span>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>
                    / {maxPages} pages
                  </span>
                </div>
                {/* Progress bar */}
                <div style={{ width: '100%', height: '4px', backgroundColor: '#1a2336', borderRadius: '2px', marginTop: '10px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${crawlProgressPercent}%`,
                    height: '100%',
                    backgroundColor: '#0284c7',
                    transition: 'width 0.4s ease',
                  }} />
                </div>
                <div style={{ marginTop: '10px', fontSize: '11.5px', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Throughput:</span>
                  <strong style={{ color: '#38bdf8', fontFamily: 'monospace' }}>{metrics.pagesPerSecond} pgs/sec</strong>
                </div>
              </div>

              {/* Panel 2: Frontier Queue */}
              <div style={{
                backgroundColor: '#0c121e',
                border: '1px solid #1a2336',
                borderRadius: '10px',
                padding: '18px 20px',
              }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#a855f7', letterSpacing: '0.4px' }}>
                  FRONTIER QUEUE (BUFFER)
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '8px' }}>
                  <span style={{ fontSize: '28px', fontWeight: 800, color: '#f8fafc', fontFamily: 'monospace' }}>
                    {metrics.queueSize}
                  </span>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>
                    enqueued URLs
                  </span>
                </div>
                <div style={{ width: '100%', height: '4px', backgroundColor: '#1a2336', borderRadius: '2px', marginTop: '10px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.min(100, (metrics.queueSize / 100) * 100)}%`,
                    height: '100%',
                    backgroundColor: '#a855f7',
                  }} />
                </div>
                <div style={{ marginTop: '10px', fontSize: '11.5px', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Architecture:</span>
                  <span style={{ color: '#cbd5e1', fontFamily: 'monospace' }}>chan string (Buffered)</span>
                </div>
              </div>

              {/* Panel 3: In-Memory Bloom Filter */}
              <div style={{
                backgroundColor: '#0c121e',
                border: '1px solid #1a2336',
                borderRadius: '10px',
                padding: '18px 20px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: '#10b981', letterSpacing: '0.4px' }}>
                    BLOOM FILTER (VISITED SET)
                  </span>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    color: '#34d399',
                    padding: '1px 6px',
                    borderRadius: '4px',
                  }}>
                    ~{ramSavedPercent}% RAM Saved
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '8px' }}>
                  <span style={{ fontSize: '28px', fontWeight: 800, color: '#f8fafc', fontFamily: 'monospace' }}>
                    {metrics.totalBloomCount}
                  </span>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>
                    tracked hashes
                  </span>
                </div>
                <div style={{ width: '100%', height: '4px', backgroundColor: '#1a2336', borderRadius: '2px', marginTop: '10px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.min(100, (metrics.totalBloomCount / 1000) * 100)}%`,
                    height: '100%',
                    backgroundColor: '#10b981',
                  }} />
                </div>
                <div style={{ marginTop: '10px', fontSize: '11.5px', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Bit Array: {(metrics.bloomMemoryBytes / 1024).toFixed(0)} KB</span>
                  <span style={{ color: '#34d399', fontFamily: 'monospace' }}>FP Bound &lt; 0.1%</span>
                </div>
              </div>

              {/* Panel 4: SQLite Index */}
              <div style={{
                backgroundColor: '#0c121e',
                border: '1px solid #1a2336',
                borderRadius: '10px',
                padding: '18px 20px',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '11px', fontWeight: 700, color: '#f59e0b', letterSpacing: '0.4px' }}>
                    SQLITE INVERTED INDEX
                  </span>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    backgroundColor: 'rgba(245, 158, 11, 0.15)',
                    color: '#fbbf24',
                    padding: '1px 6px',
                    borderRadius: '4px',
                    fontFamily: 'monospace',
                  }}>
                    WAL MODE
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginTop: '8px' }}>
                  <span style={{ fontSize: '28px', fontWeight: 800, color: '#f8fafc', fontFamily: 'monospace' }}>
                    {metrics.totalIndexedDocs}
                  </span>
                  <span style={{ fontSize: '12px', color: '#64748b' }}>
                    docs ({metrics.totalUniqueTerms} unique terms)
                  </span>
                </div>
                <div style={{ width: '100%', height: '4px', backgroundColor: '#1a2336', borderRadius: '2px', marginTop: '10px', overflow: 'hidden' }}>
                  <div style={{
                    width: '100%',
                    height: '100%',
                    backgroundColor: '#f59e0b',
                  }} />
                </div>
                <div style={{ marginTop: '10px', fontSize: '11.5px', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Writer Goroutine:</span>
                  <span style={{ color: '#cbd5e1', fontFamily: 'monospace' }}>Single-Writer Batch</span>
                </div>
              </div>
            </div>

            {/* Live Telemetry Console */}
            <div style={{
              backgroundColor: '#0c121e',
              border: '1px solid #1a2336',
              borderRadius: '12px',
              padding: '18px 20px',
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '12px',
                paddingBottom: '10px',
                borderBottom: '1px solid #161e30',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: isCrawling ? '#0284c7' : '#64748b',
                  }} />
                  <h3 style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc', letterSpacing: '0.2px' }}>
                    SWARM PIPELINE & DATABASE COMMITS STREAM
                  </h3>
                </div>
                <span style={{ fontSize: '11px', color: '#64748b', fontFamily: 'monospace' }}>
                  Active rolling buffer (40 entries)
                </span>
              </div>

              <div
                ref={logContainerRef}
                style={{
                  height: '260px',
                  overflowY: 'auto',
                  backgroundColor: '#05080f',
                  borderRadius: '7px',
                  padding: '12px 14px',
                  fontFamily: 'monospace',
                  fontSize: '11.5px',
                  lineHeight: '1.65',
                  border: '1px solid #141b2b',
                }}
              >
                {metrics.recentLogs && metrics.recentLogs.length > 0 ? (
                  metrics.recentLogs.map((log, idx) => {
                    let levelColor = '#94a3b8';
                    if (log.level === 'SUCCESS') levelColor = '#34d399';
                    if (log.level === 'WARN') levelColor = '#fbbf24';
                    if (log.level === 'ERROR') levelColor = '#f87171';
                    if (log.level === 'INFO') levelColor = '#38bdf8';

                    return (
                      <div key={idx} style={{ display: 'flex', gap: '10px', marginBottom: '3px' }}>
                        <span style={{ color: '#475569' }}>[{log.timestamp}]</span>
                        <span style={{ color: levelColor, fontWeight: 700, minWidth: '60px' }}>
                          [{log.level}]
                        </span>
                        <span style={{ color: '#e2e8f0', flex: 1 }}>{log.message}</span>
                        {log.url && (
                          <span style={{ color: '#64748b', maxWidth: '320px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {log.url}
                          </span>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div style={{ color: '#475569', padding: '24px 0', textAlign: 'center' }}>
                    Crawler stream idle. Click "Start Crawler Swarm" to dispatch workers.
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Search Interface */
          <div>
            {/* Search Command Box */}
            <div style={{
              backgroundColor: '#0c121e',
              border: '1px solid #1a2336',
              borderRadius: '14px',
              padding: '24px 28px',
              marginBottom: '20px',
            }}>
              <div style={{ marginBottom: '16px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.2px' }}>
                  Instant Local Corpus Search
                </h2>
                <p style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                  Ranked dynamically at query time using mathematical <strong>TF-IDF</strong> relevance scoring across the local SQLite inverted index.
                </p>
              </div>

              {/* Search Bar Input */}
              <div style={{ display: 'flex', gap: '10px' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <input
                    ref={searchInputRef}
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Enter keywords (e.g. concurrency goroutines, bloom filter, wails)..."
                    style={{
                      width: '100%',
                      padding: '12px 18px',
                      borderRadius: '8px',
                      backgroundColor: '#070b12',
                      border: '1px solid #1e293b',
                      color: '#f8fafc',
                      fontSize: '14px',
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
                        position: 'absolute',
                        right: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'transparent',
                        border: 'none',
                        color: '#64748b',
                        fontSize: '16px',
                        cursor: 'pointer',
                      }}
                    >
                      ×
                    </button>
                  )}
                </div>

                <button
                  onClick={() => handleSearch()}
                  disabled={isSearching}
                  style={{
                    padding: '12px 28px',
                    borderRadius: '8px',
                    backgroundColor: '#0284c7',
                    color: '#ffffff',
                    fontSize: '13.5px',
                    fontWeight: 700,
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    boxShadow: '0 2px 10px rgba(2, 132, 199, 0.35)',
                  }}
                >
                  {isSearching ? 'Evaluating...' : 'Query'}
                </button>
              </div>

              {/* Sample Queries */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '14px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '11.5px', color: '#64748b', fontWeight: 600 }}>Suggested:</span>
                {['concurrency goroutines', 'sqlite database', 'bloom filter memory', 'desktop wails'].map((sample) => (
                  <button
                    key={sample}
                    onClick={() => {
                      setSearchQuery(sample);
                      handleSearch(sample);
                    }}
                    style={{
                      padding: '3px 10px',
                      borderRadius: '5px',
                      backgroundColor: '#101624',
                      border: '1px solid #1a2336',
                      color: '#38bdf8',
                      fontSize: '11.5px',
                      fontFamily: 'monospace',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>

            {/* Results Header Metadata */}
            {hasSearched && (
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '14px',
                padding: '0 4px',
              }}>
                <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                  Retrieved <strong style={{ color: '#f8fafc' }}>{searchResults.length}</strong> matching document{searchResults.length === 1 ? '' : 's'}
                </span>
                {searchTimeMs !== null && (
                  <span style={{
                    fontSize: '11px',
                    color: '#34d399',
                    fontFamily: 'monospace',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid rgba(16, 185, 129, 0.25)',
                    padding: '3px 8px',
                    borderRadius: '5px',
                  }}>
                    Query Latency: {searchTimeMs} ms · Dynamic IDF
                  </span>
                )}
              </div>
            )}

            {/* Results List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {searchResults.length > 0 ? (
                searchResults.map((res, idx) => (
                  <div
                    key={idx}
                    style={{
                      backgroundColor: '#0c121e',
                      border: '1px solid #1a2336',
                      borderRadius: '10px',
                      padding: '18px 22px',
                      transition: 'border-color 0.18s ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          <span style={{
                            fontSize: '11px',
                            fontWeight: 700,
                            color: '#64748b',
                            fontFamily: 'monospace',
                          }}>
                            #{idx + 1}
                          </span>
                          <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#38bdf8' }}>
                            <a
                              href={res.url}
                              target="_blank"
                              rel="noreferrer"
                              style={{ color: 'inherit', textDecoration: 'none' }}
                            >
                              {res.title || res.url}
                            </a>
                          </h3>
                        </div>

                        <a
                          href={res.url}
                          target="_blank"
                          rel="noreferrer"
                          style={{
                            fontSize: '11.5px',
                            color: '#10b981',
                            fontFamily: 'monospace',
                            textDecoration: 'none',
                            display: 'block',
                            marginBottom: '8px',
                          }}
                        >
                          {res.url}
                        </a>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', minWidth: '90px' }}>
                        <div style={{
                          padding: '3px 8px',
                          borderRadius: '6px',
                          backgroundColor: 'rgba(2, 132, 199, 0.15)',
                          border: '1px solid rgba(2, 132, 199, 0.3)',
                          color: '#38bdf8',
                          fontSize: '11px',
                          fontWeight: 700,
                          fontFamily: 'monospace',
                        }}>
                          TF-IDF: {res.score.toFixed(2)}
                        </div>
                        <span style={{ fontSize: '10.5px', color: '#64748b', marginTop: '3px' }}>
                          {res.wordCount} words
                        </span>
                      </div>
                    </div>

                    <p style={{
                      fontSize: '13px',
                      color: '#cbd5e1',
                      lineHeight: '1.6',
                      marginTop: '6px',
                    }}>
                      {highlightSnippet(res.snippet, res.matchedTerms)}
                    </p>

                    {/* Matched keyword tags */}
                    {res.matchedTerms && res.matchedTerms.length > 0 && (
                      <div style={{ display: 'flex', gap: '5px', marginTop: '10px', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '10.5px', color: '#64748b', alignSelf: 'center' }}>Matched:</span>
                        {res.matchedTerms.map((term, tIdx) => (
                          <span
                            key={tIdx}
                            style={{
                              padding: '1px 6px',
                              borderRadius: '4px',
                              backgroundColor: '#141d2e',
                              border: '1px solid #1f2c44',
                              color: '#a855f7',
                              fontSize: '10.5px',
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
                  padding: '40px',
                  textAlign: 'center',
                  backgroundColor: '#0c121e',
                  border: '1px solid #1a2336',
                  borderRadius: '10px',
                  color: '#64748b',
                }}>
                  <p style={{ fontSize: '14px', fontWeight: 600, color: '#94a3b8' }}>No documents matched your query</p>
                  <p style={{ fontSize: '12px', marginTop: '4px' }}>
                    Try broader keywords or crawl additional domains in the Crawler Dashboard.
                  </p>
                </div>
              ) : (
                <div style={{
                  padding: '50px',
                  textAlign: 'center',
                  backgroundColor: '#0c121e',
                  border: '1px solid #1a2336',
                  borderRadius: '10px',
                  color: '#475569',
                }}>
                  <p style={{ fontSize: '14px', fontWeight: 600, color: '#94a3b8' }}>Ready to query local inverted index</p>
                  <p style={{ fontSize: '12px', marginTop: '4px' }}>
                    Enter any terms above to view instant TF-IDF relevance rankings.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Engineering Footer */}
      <footer style={{
        padding: '14px 28px',
        backgroundColor: '#0c121e',
        borderTop: '1px solid #1a2336',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '11px',
        color: '#64748b',
      }}>
        <span>ENSP465 Lab Project — K.R. Mangalam University</span>
        <span>Lead: Naman Katewa (2401830002) | K Sai Vignesh Yadav (2401720006) | Hrishit Kaushal (2501722016)</span>
      </footer>
    </div>
  );
}

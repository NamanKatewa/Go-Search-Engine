import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_figure1(output_path):
    fig, ax = plt.subplots(figsize=(11, 6.0), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Color palette
    c_ui = '#e8f0fe'
    c_ui_border = '#1a73e8'
    c_wails = '#fef7e0'
    c_wails_border = '#f9ab00'
    c_go = '#e6f4ea'
    c_go_border = '#137333'
    c_db = '#fce8e6'
    c_db_border = '#c5221f'
    c_search = '#f3e8fd'
    c_search_border = '#8430ce'

    # Section 1: Presentation Layer
    ax.add_patch(patches.FancyBboxPatch((4, 78), 92, 18, boxstyle="round,pad=0.4", 
                                        facecolor=c_ui, edgecolor=c_ui_border, linewidth=1.5))
    ax.text(6, 92.5, "PRESENTATION LAYER (Next.js Desktop UI via Wails Webview)", 
            fontsize=10.5, fontweight='bold', color='#174ea6')
    
    ax.add_patch(patches.FancyBboxPatch((7, 80), 26, 10.5, boxstyle="round,pad=0.3", 
                                        facecolor='#ffffff', edgecolor=c_ui_border, linewidth=1))
    ax.text(20, 85.2, "Crawler Dashboard\n(Real-Time Metrics View)", ha='center', va='center', fontsize=9)

    ax.add_patch(patches.FancyBboxPatch((37, 80), 26, 10.5, boxstyle="round,pad=0.3", 
                                        facecolor='#ffffff', edgecolor=c_ui_border, linewidth=1))
    ax.text(50, 85.2, "Search Interface\n(Instant Keystroke Querying)", ha='center', va='center', fontsize=9)

    ax.add_patch(patches.FancyBboxPatch((67, 80), 26, 10.5, boxstyle="round,pad=0.3", 
                                        facecolor='#ffffff', edgecolor=c_ui_border, linewidth=1))
    ax.text(80, 85.2, "State & Event Consumer\n(Wails JS Runtime Listeners)", ha='center', va='center', fontsize=9)

    # Section 2: Wails IPC Bridge
    ax.add_patch(patches.FancyBboxPatch((4, 65), 92, 9.5, boxstyle="round,pad=0.3", 
                                        facecolor=c_wails, edgecolor=c_wails_border, linewidth=1.5))
    ax.text(6, 71.5, "WAILS v2 IPC & RUNTIME BRIDGE (Auto-Generated TypeScript Bindings & Event Bus)", 
            fontsize=9.5, fontweight='bold', color='#b06000')
    ax.text(50, 67.8, "Bidirectional Go Struct <-> TS Interface Mapping | Low-Latency Window IPC", 
            ha='center', va='center', fontsize=8.5, style='italic')

    ax.annotate("", xy=(50, 74.5), xytext=(50, 78),
                arrowprops=dict(arrowstyle="<->", color='#5f6368', lw=1.3))

    # Section 3: Go Backend Engine
    ax.add_patch(patches.FancyBboxPatch((4, 4), 92, 57, boxstyle="round,pad=0.4", 
                                        facecolor=c_go, edgecolor=c_go_border, linewidth=1.5))
    ax.text(6, 57.5, "BACKEND ENGINE (Concurrent Go Systems Runtime)", 
            fontsize=10.5, fontweight='bold', color='#0d652d')

    # Crawler Components
    ax.add_patch(patches.FancyBboxPatch((7, 34), 42, 20, boxstyle="round,pad=0.3", 
                                        facecolor='#ffffff', edgecolor=c_go_border, linewidth=1))
    ax.text(28, 50.5, "Concurrent Web Crawler Swarm", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0d652d')
    ax.text(28, 44.5, "• Frontier Queue (In-Memory URL Queue)\n• Bloom Filter Visited Set (<0.1% FP, <5MB RAM)\n• robots.txt Polite Scraping Engine", 
            ha='center', va='center', fontsize=8)
    ax.text(28, 37.5, "Goroutine Pool (Worker 1 ... Worker N)", 
            ha='center', va='center', fontsize=8.5, fontweight='semibold', color='#137333')

    # Buffered Channel
    ax.add_patch(patches.FancyBboxPatch((12, 22), 32, 8, boxstyle="round,pad=0.3", 
                                        facecolor='#e8f5e9', edgecolor='#2e7d32', linewidth=1.2, linestyle='--'))
    ax.text(28, 26, "Thread-Safe Buffered Go Channel\nchan ParsedDocument (Cap: 500)", 
            ha='center', va='center', fontsize=8, fontweight='bold', color='#1b5e20')

    # Dedicated Database Writer
    ax.add_patch(patches.FancyBboxPatch((7, 7), 42, 11, boxstyle="round,pad=0.3", 
                                        facecolor='#ffffff', edgecolor=c_db_border, linewidth=1.2))
    ax.text(28, 14.5, "Dedicated SQLite Writer Goroutine", ha='center', va='center', fontsize=9, fontweight='bold', color='#b31412')
    ax.text(28, 10, "Single-Threaded Batch Commits (Transaction Batching: 50 docs)", 
            ha='center', va='center', fontsize=7.5, color='#3c4043')

    ax.annotate("", xy=(28, 30), xytext=(28, 34),
                arrowprops=dict(arrowstyle="->", color='#1b5e20', lw=1.3))
    ax.annotate("", xy=(28, 18), xytext=(28, 22),
                arrowprops=dict(arrowstyle="->", color='#1b5e20', lw=1.3))

    # Storage Layer (SQLite)
    ax.add_patch(patches.FancyBboxPatch((53, 7), 40, 17, boxstyle="round,pad=0.3", 
                                        facecolor=c_db, edgecolor=c_db_border, linewidth=1.2))
    ax.text(73, 20.5, "Local Inverted Index (SQLite Store)", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#b31412')
    ax.text(73, 13.5, "Tables: Documents (ID, URL, Title)\nTerms (ID, Word)\nDocumentTerms (TermID, DocID, TF)", 
            ha='center', va='center', fontsize=8, family='monospace')

    ax.annotate("", xy=(53, 14.5), xytext=(49, 14.5),
                arrowprops=dict(arrowstyle="->", color='#b31412', lw=1.8))

    # Search & Ranking Subsystem
    ax.add_patch(patches.FancyBboxPatch((53, 28), 40, 26, boxstyle="round,pad=0.3", 
                                        facecolor=c_search, edgecolor=c_search_border, linewidth=1.2))
    ax.text(73, 50.5, "Query Engine & TF-IDF Ranker", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#6200ee')
    ax.text(73, 44, "• Query Tokenizer & Stopword Filter\n• Term Lookup from SQLite Index\n• Dynamic Query-Time IDF Calculation\n• TF-IDF Vector Space Relevance Scoring", 
            ha='center', va='center', fontsize=8)
    ax.text(73, 32.5, "Sub-50ms Ranked Result Extraction", ha='center', va='center', fontsize=8.5, fontweight='semibold', color='#6200ee')

    ax.annotate("", xy=(73, 28), xytext=(73, 24),
                arrowprops=dict(arrowstyle="<->", color='#6200ee', lw=1.3))

    ax.annotate("", xy=(73, 61), xytext=(73, 54),
                arrowprops=dict(arrowstyle="<->", color='#5f6368', lw=1.3))

    ax.annotate("", xy=(28, 61), xytext=(28, 54),
                arrowprops=dict(arrowstyle="->", color='#0d652d', lw=1.3))
    ax.text(32, 57.5, "Metrics Events", fontsize=7.5, color='#0d652d', fontweight='semibold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def generate_figure2(output_path):
    fig, ax = plt.subplots(figsize=(11, 5.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(50, 96, "SYSTEM DATA FLOW & PIPELINE LIFECYCLE (DFD LEVEL 1)", 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#202124')

    # Swimlanes
    ax.add_patch(patches.FancyBboxPatch((2, 53), 21, 38, boxstyle="round,pad=0.3", 
                                        facecolor='#e8f0fe', edgecolor='#1a73e8', linewidth=1.2))
    ax.text(12.5, 87, "1. Scheduling", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#174ea6')
    ax.text(12.5, 76, "Seed URL / New Link\n\nFrontier Queue (FIFO)\n\nBloom Filter Check\n(Visited Filter)", 
            ha='center', va='center', fontsize=8)
    ax.text(12.5, 59, "robots.txt Check", ha='center', va='center', fontsize=8, style='italic')

    ax.add_patch(patches.FancyBboxPatch((26, 53), 21, 38, boxstyle="round,pad=0.3", 
                                        facecolor='#e6f4ea', edgecolor='#137333', linewidth=1.2))
    ax.text(36.5, 87, "2. Fetch & Parse", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0d652d')
    ax.text(36.5, 76, "Goroutine Swarm\n(HTTP GET Stream)\n\nHTML Tokenizer\n\nNoise Removal", 
            ha='center', va='center', fontsize=8)
    ax.text(36.5, 59, "Link Extraction", ha='center', va='center', fontsize=8, style='italic')

    # Feedback arrow
    ax.annotate("", xy=(12.5, 53), xytext=(12.5, 47),
                arrowprops=dict(arrowstyle="-", color='#174ea6', lw=1.1))
    ax.annotate("", xy=(12.5, 47), xytext=(36.5, 47),
                arrowprops=dict(arrowstyle="-", color='#174ea6', lw=1.1))
    ax.annotate("", xy=(36.5, 47), xytext=(36.5, 53),
                arrowprops=dict(arrowstyle="<-", color='#174ea6', lw=1.1))
    ax.text(24.5, 45, "Discovered Links (Feedback)", ha='center', va='center', fontsize=7.5, color='#174ea6')

    ax.add_patch(patches.FancyBboxPatch((50, 60), 22, 24, boxstyle="round,pad=0.3", 
                                        facecolor='#fef7e0', edgecolor='#f9ab00', linewidth=1.2))
    ax.text(61, 80, "3. Channel Buffer", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#b06000')
    ax.text(61, 70, "chan ParsedDocument\n\nDecouples Swarm\nfrom Disk I/O\n\nZero Lock Contention", 
            ha='center', va='center', fontsize=8)

    ax.add_patch(patches.FancyBboxPatch((75, 53), 23, 38, boxstyle="round,pad=0.3", 
                                        facecolor='#fce8e6', edgecolor='#c5221f', linewidth=1.2))
    ax.text(86.5, 87, "4. DB Indexing", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#b31412')
    ax.text(86.5, 75, "Single Writer Thread\n\nBatch Transaction\n(50 docs / commit)\n\nInverted Index Update", 
            ha='center', va='center', fontsize=8)
    ax.text(86.5, 59, "Emit Wails Events", ha='center', va='center', fontsize=7.5, style='italic', color='#b31412')

    ax.annotate("", xy=(26, 72), xytext=(23, 72),
                arrowprops=dict(arrowstyle="->", color='#5f6368', lw=1.3))
    ax.annotate("", xy=(50, 72), xytext=(47, 72),
                arrowprops=dict(arrowstyle="->", color='#5f6368', lw=1.3))
    ax.annotate("", xy=(75, 72), xytext=(72, 72),
                arrowprops=dict(arrowstyle="->", color='#5f6368', lw=1.3))

    # Lower Half: Search & Retrieval Workflow
    ax.add_patch(patches.FancyBboxPatch((4, 6), 92, 34, boxstyle="round,pad=0.4", 
                                        facecolor='#f3e8fd', edgecolor='#8430ce', linewidth=1.2))
    ax.text(50, 36, "5. INSTANT SEARCH & QUERY-TIME TF-IDF RANKING FLOW", 
            ha='center', va='center', fontsize=10.5, fontweight='bold', color='#6200ee')

    steps = [
        ("User Query", "Search Bar Input in\nNext.js Interface"),
        ("Wails IPC", "Direct Go Binding\nSearch(query) call"),
        ("Tokenization", "Lowercase, Stemming,\nStopword Removal"),
        ("SQLite Fetch", "Extract Matching\nTerm Frequencies"),
        ("Dynamic IDF", "Calculate Term Rarity\nacross Total Docs"),
        ("Relevance Sort", "Compute TF-IDF\nSort Descending")
    ]

    for idx, (title, desc) in enumerate(steps):
        x = 6.5 + idx * 14.5
        ax.add_patch(patches.FancyBboxPatch((x, 9.5), 13.5, 23, boxstyle="round,pad=0.2", 
                                            facecolor='#ffffff', edgecolor='#8430ce', linewidth=1))
        ax.text(x + 6.75, 28, title, ha='center', va='center', fontsize=8, fontweight='bold', color='#6200ee')
        ax.text(x + 6.75, 18, desc, ha='center', va='center', fontsize=7, color='#3c4043')
        if idx < len(steps) - 1:
            ax.annotate("", xy=(x + 14.5, 20), xytext=(x + 13.5, 20),
                        arrowprops=dict(arrowstyle="->", color='#8430ce', lw=1.1))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    generate_figure1('C:/Users/naman/Documents/GitHub/Go-Search-Engine/docs/phase1/figure1_architecture.png')
    generate_figure2('C:/Users/naman/Documents/GitHub/Go-Search-Engine/docs/phase1/figure2_dataflow.png')
    print('Figures re-generated successfully.')

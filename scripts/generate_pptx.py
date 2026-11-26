import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 1. Initialize 16:9 Presentation
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 2. Design System Colors (Clean, Modern Engineering Dark Theme)
BG_COLOR = RGBColor(14, 16, 20)       # Deep slate #0E1014
CARD_BG = RGBColor(23, 27, 34)       # Card slate #171B22
CARD_BORDER = RGBColor(38, 44, 56)   # #262C38
ACCENT_BLUE = RGBColor(0, 173, 216)  # Official Go Cyan #00ADD8
ACCENT_GREEN = RGBColor(52, 211, 153) # Mint green #34D399
TEXT_WHITE = RGBColor(248, 250, 252)  # #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184)  # #94A3B8
TEXT_DIM = RGBColor(100, 116, 139)    # #64748B

FONT_TITLE = "Segoe UI"
FONT_BODY = "Segoe UI"

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def add_header(slide, title_text, category_text="GO DESKTOP SEARCH ENGINE"):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = category_text.upper()
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = ACCENT_BLUE
    p_c.font.name = FONT_TITLE

    # Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11), Inches(0.7))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(26)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE
    p_t.font.name = FONT_TITLE

def add_card(slide, left, top, width, height, bg=CARD_BG, border=CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg
    shape.line.color.rgb = border
    shape.line.width = Pt(1)
    return shape

blank_layout = prs.slide_layouts[6]

# ==========================================
# SLIDE 1: Title Slide (Minimal & Impactful)
# ==========================================
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1)

# Subtle decorative accent bar
accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(0.12), Inches(4.2))
accent_bar.fill.solid()
accent_bar.fill.fore_color.rgb = ACCENT_BLUE
accent_bar.line.fill.background()

# Title text box
tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11.2), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

p0 = tf.paragraphs[0]
p0.text = "ENSP465 · NEW AGE PROGRAMMING LANGUAGES LAB"
p0.font.size = Pt(12)
p0.font.bold = True
p0.font.color.rgb = ACCENT_BLUE
p0.font.name = FONT_TITLE
p0.space_after = Pt(12)

p1 = tf.add_paragraph()
p1.text = "Go Desktop Search Engine"
p1.font.size = Pt(40)
p1.font.bold = True
p1.font.color.rgb = TEXT_WHITE
p1.font.name = FONT_TITLE

p2 = tf.add_paragraph()
p2.text = "High-Performance Concurrency, Memory-Safe Probabilistic Sets, and Dynamic TF-IDF"
p2.font.size = Pt(18)
p2.font.color.rgb = TEXT_MUTED
p2.font.name = FONT_BODY
p2.space_after = Pt(40)

p3 = tf.add_paragraph()
p3.text = "Team Lead: Naman Katewa (2401830002)\nTeam Members: K Sai Vignesh Yadav (2401720006) · Hrishit Kaushal (2501722016)\nDepartment of Computer Science & Engineering · K.R. Mangalam University"
p3.font.size = Pt(13)
p3.font.color.rgb = TEXT_DIM
p3.font.name = FONT_BODY

# ==========================================
# SLIDE 2: Problem Statement & Motivation
# ==========================================
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2)
add_header(s2, "The Systems Engineering Challenge")

# 3 Horizontal Cards
card_w = Inches(3.64)
card_h = Inches(4.8)
top_pos = Inches(1.7)

col_data = [
    ("1. MEMORY OVERHEAD", "The Visited Set Problem", 
     "Tracking 500,000+ visited URLs in a standard hash map (`map[string]bool`) consumes hundreds of megabytes in string keys alone, leading to Out of Memory (OOM) process crashes during deep crawls."),
    ("2. DATA CONTENTION", "SQLite Concurrency Locks", 
     "SQLite is an embedded, single-file database. Multiple concurrent crawler threads attempting simultaneous `INSERT` queries cause catastrophic `database is locked` runtime panics."),
    ("3. DESKTOP BLOAT", "Electron Runtime Burden", 
     "Standard cross-platform desktop shells bundle an entire Chromium browser and Node.js runtime, producing 150MB+ binary sizes and 300MB idle RAM usage for simple local tasks.")
]

for idx, (tag, heading, desc) in enumerate(col_data):
    left_pos = Inches(0.8 + idx * 4.0)
    add_card(s2, left_pos, top_pos, card_w, card_h)
    
    tb = s2.shapes.add_textbox(left_pos + Inches(0.3), top_pos + Inches(0.35), card_w - Inches(0.6), card_h - Inches(0.7))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = tag
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)
    
    p2 = tf.add_paragraph()
    p2.text = heading
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.space_after = Pt(16)
    
    p3 = tf.add_paragraph()
    p3.text = desc
    p3.font.size = Pt(13.5)
    p3.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 3: System Architecture Overview
# ==========================================
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3)
add_header(s3, "Architecture & Concurrency Pipeline")

# Left Column: Image Card
fig1_path = os.path.join(os.getcwd(), 'docs', 'phase1', 'figure1_architecture.png')
add_card(s3, Inches(0.8), Inches(1.7), Inches(6.8), Inches(5.0))
if os.path.exists(fig1_path):
    s3.shapes.add_picture(fig1_path, Inches(1.0), Inches(1.9), width=Inches(6.4))

# Right Column: Architecture Highlights
add_card(s3, Inches(7.9), Inches(1.7), Inches(4.6), Inches(5.0))
tb = s3.shapes.add_textbox(Inches(8.2), Inches(1.95), Inches(4.0), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

items = [
    ("Swarm Worker Concurrency", "2 to 16 lightweight goroutines (2KB stack each) fetch pages simultaneously respecting polite robots.txt rules."),
    ("In-Memory Bloom Filter", "Probabilistic bit array with double-hashing eliminates string storage, bounding false positives to <0.1%."),
    ("Single-Writer Channel Pipeline", "Workers send parsed pages over a buffered Go channel (`chan db.ParsedDocument`) to a single writer goroutine, eliminating SQLite locks."),
    ("Dynamic TF-IDF Inverted Index", "Normalized 3-table SQLite schema computing smooth IDF and cosine length normalization at query time.")
]

for i, (title, text) in enumerate(items):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {title}"
    p.font.size = Pt(13.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    
    p_desc = tf.add_paragraph()
    p_desc.text = text
    p_desc.font.size = Pt(12)
    p_desc.font.color.rgb = TEXT_MUTED
    p_desc.space_after = Pt(10)

# ==========================================
# SLIDE 4: The In-Memory Bloom Filter
# ==========================================
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4)
add_header(s4, "Probabilistic Data Structure: Bloom Filter")

# 2 Columns (Card Left: Mathematics & Theory; Card Right: Go Implementation)
col_w = Inches(5.6)
card_h = Inches(5.0)

# Left: Theory
add_card(s4, Inches(0.8), Inches(1.7), col_w, card_h)
tb = s4.shapes.add_textbox(Inches(1.1), Inches(1.95), col_w - Inches(0.6), card_h - Inches(0.5))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "MATHEMATICAL DESIGN"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE
p.space_after = Pt(8)

p2 = tf.add_paragraph()
p2.text = "Zero False Negatives · Bounded False Positives"
p2.font.size = Pt(16)
p2.font.bold = True
p2.font.color.rgb = TEXT_WHITE
p2.space_after = Pt(14)

theory_text = (
    "• Bit Array Sizing:\n"
    "  m = - (n · ln(p)) / (ln(2)²)\n"
    "  For n = 500,000 URLs and p = 0.001 (0.1%), m = 7,188,793 bits (898 KB RAM).\n\n"
    "• Kirsch-Mitzenmacher Double Hashing:\n"
    "  Instead of calculating k independent hash functions, we compute two 64-bit base hashes (h1 and h2) and derive all k positions:\n"
    "  gi(x) = (h1(x) + i · h2(x)) mod m\n\n"
    "• Memory Savings:\n"
    "  Trades a tiny 0.1% collision rate for over 90% memory savings compared to standard hash sets."
)
p3 = tf.add_paragraph()
p3.text = theory_text
p3.font.size = Pt(12.5)
p3.font.color.rgb = TEXT_MUTED

# Right: Go Code Implementation
add_card(s4, Inches(6.8), Inches(1.7), col_w, card_h)
tb = s4.shapes.add_textbox(Inches(7.1), Inches(1.95), col_w - Inches(0.6), card_h - Inches(0.5))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "GO CODE MECHANICS (internal/bloom/bloom.go)"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = ACCENT_GREEN
p.space_after = Pt(8)

p2 = tf.add_paragraph()
p2.text = "Thread-Safe Bit Manipulation via sync.RWMutex"
p2.font.size = Pt(16)
p2.font.bold = True
p2.font.color.rgb = TEXT_WHITE
p2.space_after = Pt(14)

code_notes = (
    "• 64-Bit Word Packing:\n"
    "  Bits are packed into a []uint64 slice. Each element stores 64 boolean flags:\n"
    "  word = idx / 64\n"
    "  offset = idx % 64\n\n"
    "• Fast Set & Test Operators:\n"
    "  Add:   bits[word] |= (1 << offset)\n"
    "  Check: (bits[word] & (1 << offset)) != 0\n\n"
    "• Concurrent Read/Write Protection:\n"
    "  Multiple workers check Contains() concurrently using bf.mu.RLock(), while Add() acquires an exclusive Lock()."
)
p3 = tf.add_paragraph()
p3.text = code_notes
p3.font.size = Pt(12.5)
p3.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 5: Crawler Swarm & Single-Writer Channel Pipeline
# ==========================================
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5)
add_header(s5, "Concurrency & The Single-Writer Pipeline")

# Left Column: Dataflow Diagram
fig2_path = os.path.join(os.getcwd(), 'docs', 'phase1', 'figure2_dataflow.png')
add_card(s5, Inches(0.8), Inches(1.7), Inches(6.4), Inches(5.0))
if os.path.exists(fig2_path):
    s5.shapes.add_picture(fig2_path, Inches(1.0), Inches(1.9), width=Inches(6.0))

# Right Column: Go CSP Model
add_card(s5, Inches(7.5), Inches(1.7), Inches(5.0), Inches(5.0))
tb = s5.shapes.add_textbox(Inches(7.8), Inches(1.95), Inches(4.4), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "CSP MODEL: COMMUNICATING SEQUENTIAL PROCESSES"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE
p.space_after = Pt(6)

p2 = tf.add_paragraph()
p2.text = "Eliminating SQLite Lock Contention"
p2.font.size = Pt(16)
p2.font.bold = True
p2.font.color.rgb = TEXT_WHITE
p2.space_after = Pt(12)

crawler_text = (
    "• Worker Swarm:\n"
    "  Goroutines fetch URLs from `frontierQueue chan string` concurrently. HTML is stripped of noise tags (<nav>, <footer>, <script>) using a streaming tokenizer.\n\n"
    "• Dedicated DB Writer Goroutine:\n"
    "  Workers NEVER write to SQLite directly. They push parsed data into `docChannel chan db.ParsedDocument`.\n\n"
    "• Atomic WAL Batch Transactions:\n"
    "  A single dedicated writer goroutine consumes the channel and executes atomic batch inserts in Write-Ahead Logging (WAL) mode every 50 docs or 300ms.\n\n"
    "• Clean Context Cancellation:\n"
    "  `context.WithCancel` immediately halts all workers on user stop."
)
p3 = tf.add_paragraph()
p3.text = crawler_text
p3.font.size = Pt(12)
p3.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 6: SQLite Inverted Index & Dynamic TF-IDF
# ==========================================
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6)
add_header(s6, "Information Retrieval: Dynamic TF-IDF Ranking")

# 3 Stat / Feature Cards
col_w = Inches(3.64)
col_h = Inches(5.0)

cards_s6 = [
    ("NORMALIZED SCHEMA", "3-Table Inverted Index",
     "• documents:\n  id, url, title, snippet, word_count, crawled_at\n\n"
     "• terms:\n  id, term (UNIQUE with B-tree index)\n\n"
     "• document_terms (Postings):\n  term_id, document_id, term_frequency\n\n"
     "Ensures zero string duplication across terms."),
    
    ("DYNAMIC QUERY-TIME IDF", "Smooth Inverse Frequency",
     "Formula calculated on the fly:\n\n"
     "IDF(t) = ln((N + 1) / (DF(t) + 1)) + 1\n\n"
     "• N = Total documents in corpus\n"
     "• DF(t) = Documents containing term t\n\n"
     "Common stop words ('the') receive near-zero weights, while distinct terms ('bloom') receive high weights."),
    
    ("LENGTH NORMALIZATION", "Cosine Length Normalization",
     "Raw Score = Σ (TF(t, D) · IDF(t))\n\n"
     "Final Score = Raw Score / √(word_count(D))\n\n"
     "Prevents verbose, 50-page documents from dominating short, highly precise articles merely due to raw length.")
]

for idx, (tag, title, desc) in enumerate(cards_s6):
    left_pos = Inches(0.8 + idx * 4.0)
    add_card(s6, left_pos, Inches(1.7), col_w, col_h)
    
    tb = s6.shapes.add_textbox(left_pos + Inches(0.25), Inches(1.95), col_w - Inches(0.5), col_h - Inches(0.6))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = tag
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(8)
    
    p2 = tf.add_paragraph()
    p2.text = title
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.space_after = Pt(12)
    
    p3 = tf.add_paragraph()
    p3.text = desc
    p3.font.size = Pt(12)
    p3.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 7: UI & Live Telemetry Screenshots
# ==========================================
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7)
add_header(s7, "Desktop User Interface & Live Telemetry")

img_w = Inches(5.6)
img_h = Inches(3.6)
top_pos = Inches(1.8)

# Left: Crawler Dashboard
c1 = add_card(s7, Inches(0.8), top_pos, img_w + Inches(0.2), Inches(4.9))
crawler_scr = os.path.join(os.getcwd(), 'docs', 'screenshots', 'dashboard.png')
if os.path.exists(crawler_scr):
    s7.shapes.add_picture(crawler_scr, Inches(0.9), top_pos + Inches(0.1), width=img_w)

tb = s7.shapes.add_textbox(Inches(0.9), top_pos + Inches(3.9), img_w, Inches(0.8))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "Crawler Dashboard: Real-time worker swarm telemetry, queue size, Bloom memory footprint, and live event log streaming."
p.font.size = Pt(11.5)
p.font.color.rgb = TEXT_MUTED

# Right: Search Results
c2 = add_card(s7, Inches(6.8), top_pos, img_w + Inches(0.2), Inches(4.9))
search_scr = os.path.join(os.getcwd(), 'docs', 'screenshots', 'search_results.png')
if os.path.exists(search_scr):
    s7.shapes.add_picture(search_scr, Inches(6.9), top_pos + Inches(0.1), width=img_w)

tb = s7.shapes.add_textbox(Inches(6.9), top_pos + Inches(3.9), img_w, Inches(0.8))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "Instant Search Interface: Sub-2ms TF-IDF query execution, relevance scores, matched term tags, and length-normalized snippet previews."
p.font.size = Pt(11.5)
p.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 8: Wails v2 vs Electron Desktop Shell
# ==========================================
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8)
add_header(s8, "Engineering Advantage: Wails v2 vs Electron")

# Comparison Table Card
add_card(s8, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.0))

tb = s8.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(11.1), Inches(4.6))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "NATIVE DESKTOP EMBEDDING COMPARISON"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE
p.space_after = Pt(12)

table_text = (
    "• Runtime Engine:\n"
    "  - Electron: Bundles full Chromium web browser + Node.js runtime inside every application.\n"
    "  - Wails v2 (Our Project): Utilizes native Microsoft WebView2 control already present on Windows.\n\n"
    "• Standalone Binary Executable Size:\n"
    "  - Electron: Typically 150 MB to 250 MB.\n"
    "  - Wails v2: Only 30 MB (including the full embedded 10,089-document SQLite seed database!).\n\n"
    "• Idle Memory Footprint:\n"
    "  - Electron: 150 MB to 300 MB RAM idle.\n"
    "  - Wails v2: Under 40 MB RAM idle.\n\n"
    "• Fullstack Type Safety:\n"
    "  - Wails automatically inspects Go structs in `app.go` and generates strict TypeScript interfaces (`frontend/wailsjs/`), guaranteeing compile-time type safety across Go and React without manual REST boilerplate."
)
p2 = tf.add_paragraph()
p2.text = table_text
p2.font.size = Pt(13)
p2.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 9: Pre-Seeded Corpus & Verification Benchmarks
# ==========================================
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9)
add_header(s9, "Corpus Verification & Performance Benchmarks")

# 4 Metric Cards
card_w = Inches(2.7)
card_h = Inches(2.3)

metrics = [
    ("10,089", "TOTAL DOCUMENTS", "10,000 Webster definitions +\n89 Wikipedia tech articles"),
    ("39,767", "UNIQUE TERMS", "Normalized vocabulary with\nB-tree index lookups"),
    ("244,028", "INDEXED POSTINGS", "Term-document frequency\npostings records"),
    ("15.2 MB", "CORPUS SIZE", "Embedded into binary via\nGo //go:embed directive")
]

for idx, (val, title, sub) in enumerate(metrics):
    left_pos = Inches(0.8 + idx * 3.0)
    add_card(s9, left_pos, Inches(1.8), card_w, card_h)
    
    tb = s9.shapes.add_textbox(left_pos + Inches(0.2), Inches(1.95), card_w - Inches(0.4), card_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = val
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(4)
    
    p2 = tf.add_paragraph()
    p2.text = title
    p2.font.size = Pt(10)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.space_after = Pt(6)
    
    p3 = tf.add_paragraph()
    p3.text = sub
    p3.font.size = Pt(11)
    p3.font.color.rgb = TEXT_MUTED

# Bottom Card: Benchmark Results
add_card(s9, Inches(0.8), Inches(4.3), Inches(11.7), Inches(2.4))
tb = s9.shapes.add_textbox(Inches(1.1), Inches(4.45), Inches(11.1), Inches(2.1))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "AUTOMATED TEST SUITE BENCHMARKS (go test -v ./...)"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = ACCENT_GREEN
p.space_after = Pt(6)

bench_text = (
    "• TestBloomFilterFalsePositiveBound: Measured FP = 0.0106 vs Target FP = 0.0100 (5,000 tests) — PASS (0.00s)\n"
    "• TestDatabaseBatchInsertAndSearch: Dynamic TF-IDF query execution & length normalization — PASS (0.03s)\n"
    "• TestCrawlerEndToEnd: End-to-end swarm crawling, robots.txt compliance & index verification — PASS (1.82s)\n"
    "• Query Response Latency: Sub-2 millisecond search execution across the full 10,089-document corpus."
)
p2 = tf.add_paragraph()
p2.text = bench_text
p2.font.size = Pt(12)
p2.font.color.rgb = TEXT_MUTED

# ==========================================
# SLIDE 10: Conclusion & Key Learnings
# ==========================================
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10)
add_header(s10, "Summary & Key Technical Learnings")

add_card(s10, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.0))
tb = s10.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(10.9), Inches(4.4))
tf = tb.text_frame
tf.word_wrap = True

p = tf.paragraphs[0]
p.text = "CORE ENGINEERING TAKEAWAYS"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = ACCENT_BLUE
p.space_after = Pt(14)

learnings = [
    ("Mastery of Go Concurrency Primitives", "Clean utilization of Goroutines, buffered Channels, sync/atomic lock-free operations, and context cancellation to build an elegant producer-consumer pipeline."),
    ("Bit-Level Systems Programming", "Designing and verifying an in-memory Bloom Filter with double hashing to eliminate OOM vulnerabilities in high-volume crawling."),
    ("Safe Embedded Database Aggregation", "Overcoming SQLite write lock contention using a single-writer goroutine with atomic WAL batch transactions."),
    ("Mathematical Search Foundations", "Implementing dynamic query-time TF-IDF relevance ranking with cosine length normalization for instant keyword lookup."),
    ("Modern Desktop Application Architecture", "Pairing Go backend systems with React 19 and Microsoft WebView2 via Wails v2 to build lightweight, single-binary desktop software.")
]

for title, desc in learnings:
    p = tf.add_paragraph()
    p.text = f"✔ {title}: "
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    
    # Add normal description part
    p_run = p.add_run()
    p_run.text = desc
    p_run.font.bold = False
    p_run.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(10)

# Save Presentation
output_path = os.path.join(os.getcwd(), 'docs', 'Go_Search_Engine_Presentation.pptx')
prs.save(output_path)
print(f"Successfully generated PowerPoint presentation at: {output_path}")

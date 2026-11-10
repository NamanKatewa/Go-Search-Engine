import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

omml_ns = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'

def set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    borders_xml = f'''
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
        <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>
        <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>
        <w:insideV w:val="none"/>
        <w:left w:val="none"/>
        <w:right w:val="none"/>
    </w:tblBorders>
    '''
    tblPr.append(parse_xml(borders_xml))

def add_omml_equation(doc, math_xml_content):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    full_xml = f'<m:oMathPara {omml_ns}><m:oMath>{math_xml_content}</m:oMath></m:oMathPara>'
    p._p.append(parse_xml(full_xml))

def create_document():
    doc = docx.Document()

    # Page setup: Standard 1 inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Header / Footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("ENSP465 Project Report | Page ")
        f_run.font.name = 'Times New Roman'
        f_run.font.size = Pt(9)
        f_run.font.color.rgb = RGBColor(128, 128, 128)
        
        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        f_p._p.append(fldSimple)

    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(12)
    font_normal.color.rgb = RGBColor(30, 30, 30)

    def add_p(text="", space_after=4, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.5):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = line_spacing
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        if text:
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.font.bold = bold
            run.font.italic = italic
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 30, 70)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(30, 50, 100)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.italic = True
        run.font.color.rgb = RGBColor(40, 40, 40)
        return p

    # ----------------------------------------------------
    # SECTION 1: COVER PAGE
    # ----------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(28)
    p_inst.paragraph_format.space_after = Pt(4)
    run_inst = p_inst.add_run("K.R. MANGALAM UNIVERSITY")
    run_inst.font.name = 'Times New Roman'
    run_inst.font.size = Pt(18)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(15, 30, 70)

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(22)
    run_dept = p_dept.add_run("School of Engineering & Technology\nDepartment of Computer Science & Engineering")
    run_dept.font.name = 'Times New Roman'
    run_dept.font.size = Pt(13)
    run_dept.font.bold = True

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_after = Pt(28)
    run_course = p_course.add_run("ENSP465 — New Age Programming Languages Lab\nPhase 1 Project Report")
    run_course.font.name = 'Times New Roman'
    run_course.font.size = Pt(14)
    run_course.font.bold = True
    run_course.font.color.rgb = RGBColor(180, 40, 30)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(36)
    run_title = p_title.add_run("High-Performance Concurrent Web Crawler and Local Inverted Index Desktop Search Engine in Go")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(16)
    run_title.font.bold = True

    # Metadata table on Cover Page (Integrated Students section, Semester 5th, No submission date)
    table_cov = doc.add_table(rows=3, cols=2)
    table_cov.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_cov.autofit = False
    
    col_widths = [Inches(2.0), Inches(4.5)]
    for row in table_cov.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    cov_data = [
        ("Students:", 
         "• Naman Katewa (Roll No: 2401830002) — B.Sc. (Hons.) Cyber Security [Team Lead]\n"
         "• K Sai Vignesh Yadav (Roll No: 2401720006) — B.Sc. (Hons.) Computer Science\n"
         "• Hrishit Kaushal (Roll No: 2501722016) — B.Sc. (Hons.) Computer Science"),
        ("Semester & Academic Year:", "Semester 5th, Academic Year 2026-2027"),
        ("Course Faculty:", "Dr. Hemraj Kumawat\nSchool of Engineering & Technology, KRMU")
    ]

    for i, (k, v) in enumerate(cov_data):
        cell_k = table_cov.rows[i].cells[0]
        cell_v = table_cov.rows[i].cells[1]
        
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_after = Pt(3)
        pk.paragraph_format.line_spacing = 1.2
        rk = pk.add_run(k)
        rk.font.name = 'Times New Roman'
        rk.font.size = Pt(11)
        rk.font.bold = True

        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_after = Pt(3)
        pv.paragraph_format.line_spacing = 1.25
        rv = pv.add_run(v)
        rv.font.name = 'Times New Roman'
        rv.font.size = Pt(10.5)

    set_table_borders(table_cov, "B0B0B0")
    doc.add_page_break()

    # ----------------------------------------------------
    # SECTION 2: PROBLEM STATEMENT & MOTIVATION
    # ----------------------------------------------------
    add_h1("Section 2: Problem Statement & Motivation")

    add_h2("2.1 Problem Description")
    add_p(
        "Modern search systems depend almost entirely on centralized cloud infrastructure. Whether using commercial "
        "search engines like Google or hosted enterprise search APIs, users must transmit search queries over external "
        "networks. In air-gapped security research labs, confidential corporate intranets, and remote industrial environments, "
        "continuous internet access is either physically unavailable or forbidden by compliance policy. When working with local "
        "technical manuals, offline documentation, and web corpora, engineers lack an autonomous tool that can crawl, index, "
        "and search content locally with mathematical relevance ranking."
    )
    add_p(
        "Transmitting search queries across the public internet introduces telemetry and data leakage risks. Third-party cloud "
        "engines log search queries, build user tracking profiles, and expose proprietary technical interests. Existing desktop "
        "search tools fail to solve this problem. Desktop file utilities like Everything index file names and metadata, but they "
        "do not crawl web pages, strip HTML boilerplate, or rank results based on body text relevance. Conversely, enterprise "
        "engines like Elasticsearch and Apache Solr run on the Java Virtual Machine. They require gigabytes of baseline memory, "
        "continuous daemon processes, and complex cluster configurations, making them impractical for a lightweight desktop utility."
    )
    add_p(
        "A clear gap exists between simple file-name finders and heavy enterprise search servers. Technical users require a self-contained "
        "desktop search engine that runs locally on consumer workstations. It must crawl local or remote sites using concurrent workers, "
        "cleanly strip HTML boilerplate, build a local inverted index, and rank search queries instantly using algorithmic models, all "
        "without external cloud dependencies or background daemon services."
    )

    add_h2("2.2 Real-World Context and Domain")
    add_p(
        "This project operates in systems programming, concurrent network I/O, and information retrieval. It serves four operational contexts:"
    )
    p_c1 = add_p()
    p_c1.add_run("1. Air-Gapped and Secure Networks: ").bold = True
    p_c1.add_run("Security testing labs, defense systems, and industrial environments where internet access is prohibited.")
    
    p_c2 = add_p()
    p_c2.add_run("2. Offline Technical Documentation: ").bold = True
    p_c2.add_run("Software engineers needing rapid full-text search across downloaded API references, RFCs, and offline technical sites.")

    p_c3 = add_p()
    p_c3.add_run("3. Intranet Document Retrieval: ").bold = True
    p_c3.add_run("Research teams and university labs indexing local departmental web portals without deploying server clusters.")

    p_c4 = add_p()
    p_c4.add_run("4. Systems Concurrency Study: ").bold = True
    p_c4.add_run("A practical demonstration of lightweight threading, channel-based synchronization, and memory-safe probabilistic structures.")

    add_h2("2.3 Motivation")
    add_p(
        "Modern search applications have become bloated with cloud dependencies, neural network runtimes, and telemetry agents. "
        "For direct technical keyword lookup, classic information retrieval algorithms like Term Frequency-Inverse Document Frequency "
        "(TF-IDF) remain fast, transparent, and accurate. Building this system in Go demonstrates how a compiled systems language "
        "handles thousands of concurrent web requests, thread-safe database batching, and instant state management without external runtimes."
    )

    add_h2("2.4 Existing Tools and Their Limitations")
    add_p(
        "Table 1 outlines how existing search solutions compare against the proposed Go desktop search engine."
    )

    # Table 1
    table_comp = doc.add_table(rows=5, cols=5)
    table_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_comp.autofit = False

    t_widths = [Inches(1.3), Inches(1.2), Inches(1.4), Inches(1.3), Inches(1.3)]
    for row in table_comp.rows:
        for idx, width in enumerate(t_widths):
            row.cells[idx].width = width

    headers = ["Feature / Criterion", "Cloud Search (Google)", "Enterprise (Elasticsearch)", "Desktop Tool (Everything)", "Proposed Go Engine"]
    for idx, h in enumerate(headers):
        cell = table_comp.rows[0].cells[idx]
        set_cell_background(cell, "E8EEF8")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)

    comp_rows = [
        ("Deployment Model", "Remote Cloud / SaaS", "JVM Cluster Daemon", "Local Desktop Utility", "Local Desktop Executable"),
        ("Network Need", "Continuous Internet", "Local/Remote Network", "None (Local Disk Only)", "Optional (Local Crawl / Offline)"),
        ("RAM Footprint", "Negligible on Client", "High (2 GB to 8 GB+)", "Minimal (< 100 MB)", "Low (< 150 MB RAM)"),
        ("Content Indexing", "Full Web Indexing", "Full Text & Schema", "File Names Only", "Clean Full-Text Inverted Index")
    ]

    for row_idx, r_data in enumerate(comp_rows):
        for col_idx, text in enumerate(r_data):
            cell = table_comp.rows[row_idx + 1].cells[col_idx]
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(8.5)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(text)
                run.font.size = Pt(8.5)

    set_table_borders(table_comp, "D0D0D0")
    add_p("Table 1: Comparative analysis of existing search tools versus the proposed Go engine.", space_after=10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    # ----------------------------------------------------
    # SECTION 3: PROPOSED SOLUTION & LANGUAGE JUSTIFICATION
    # ----------------------------------------------------
    add_h1("Section 3: Proposed Solution & Language Justification")

    add_h2("3.1 Project Overview")
    add_p(
        "The proposed system is an autonomous desktop search engine packaged as a single executable using Wails v2 and Next.js. "
        "It features a concurrent Go web crawler that fetches web pages simultaneously using goroutines, an HTML parser that strips "
        "boilerplate navigation markup, an in-memory Bloom filter to track visited links, and a dedicated database writer that commits "
        "words to a local SQLite inverted index. Search queries calculate TF-IDF relevance scores on the fly, delivering ranked results in under 50ms."
    )

    add_h2("3.2 Language Selection: Go (Golang)")
    add_p(
        "From the ENSP465 curriculum (comprising Go, F#, Clojure, and Kotlin), we selected Go. Go was developed specifically for "
        "concurrent systems engineering, network servers, and high-performance system utilities."
    )

    add_h2("3.3 Language Justification Against Curriculum Alternatives")
    add_p(
        "Go provides four specific technical advantages over Kotlin, Clojure, and F# for building this search engine:"
    )

    add_h3("1. Goroutines and M:N Cooperative Scheduling")
    add_p(
        "Web crawling is an I/O-bound workload requiring thousands of concurrent network connections. In Kotlin on the JVM, threads map 1:1 "
        "to operating system kernel threads, each allocating roughly 1 MB of stack memory. Spawning 2,000 threads consumes 2 GB of memory in "
        "stack frames alone, inducing severe context-switching overhead. Go employs goroutines managed by an internal M:N runtime scheduler. "
        "Goroutines start with a 2 KB stack that expands dynamically. Spawning 2,000 crawler workers in Go consumes under 25 MB of memory, "
        "enabling high crawl concurrency on standard desktop hardware."
    )

    add_h3("2. CSP Concurrency via Buffered Channels")
    add_p(
        "SQLite enforces single-writer serialization: multiple threads attempting concurrent writes trigger 'database is locked' errors. "
        "In shared-memory languages, coordinating concurrent writes requires explicit mutexes and condition variables, risking deadlocks. "
        "Go implements Communicating Sequential Processes (CSP). The crawler swarm sends parsed documents over a buffered Go channel "
        "(chan ParsedDocument). A single dedicated writer goroutine reads from this channel and commits batches of 50 documents in single "
        "transactions. This completely eliminates lock contention without complex mutex synchronization."
    )

    add_h3("3. Low-Latency Garbage Collection and Native Binary Compilation")
    add_p(
        "JVM languages like Kotlin and Clojure require a heavy runtime, suffer from cold-start latency, and experience stop-the-world garbage "
        "collection pauses during heavy text tokenization. Clojure's immutable structures also generate significant heap churn. Go compiles "
        "directly to native machine code with zero virtual machine startup overhead. Go gives direct control over memory layout through value "
        "types and slices, avoiding object allocation overhead and keeping garbage collection pauses below 1 millisecond."
    )

    add_h3("4. Fullstack Desktop Type Safety via Wails v2")
    add_p(
        "Desktop development in F# or Clojure typically requires heavy Electron wrappers that consume hundreds of megabytes of RAM. "
        "Wails v2 couples Go with native OS webviews (Microsoft Edge WebView2 on Windows). Wails parses Go structs at compile time and "
        "generates matching TypeScript interfaces, establishing compile-time type safety across the Go backend and Next.js frontend."
    )

    add_h2("3.4 Key Libraries and Frameworks")
    p_l1 = add_p()
    p_l1.add_run("• Wails v2 (github.com/wailsapp/wails/v2): ").bold = True
    p_l1.add_run("Packages the Go backend and Next.js UI into a single desktop executable with bidirectional IPC bindings.")

    p_l2 = add_p()
    p_l2.add_run("• net/http (Standard Library): ").bold = True
    p_l2.add_run("Provides production-grade HTTP client connection pooling and timeout management.")

    p_l3 = add_p()
    p_l3.add_run("• golang.org/x/net/html: ").bold = True
    p_l3.add_run("Standard HTML5 tokenizer used to strip script tags and isolate textual body content.")

    p_l4 = add_p()
    p_l4.add_run("• modernc.org/sqlite: ").bold = True
    p_l4.add_run("A pure Go SQLite engine requiring no external C compiler (CGo-free), enabling simple cross-platform builds.")

    # ----------------------------------------------------
    # SECTION 4: OBJECTIVES & SCOPE
    # ----------------------------------------------------
    add_h1("Section 4: Objectives & Scope")

    add_h2("4.1 Specific, Measurable Objectives")
    add_p("The project commits to five concrete engineering targets:")

    p_o1 = add_p()
    p_o1.add_run("1. Crawl Throughput: ").bold = True
    p_o1.add_run("Achieve a sustained crawling rate of at least 50 pages per second on local network targets using concurrent goroutines.")

    p_o2 = add_p()
    p_o2.add_run("2. Memory-Safe URL Tracking: ").bold = True
    p_o2.add_run("Restrict visited URL memory consumption to under 5 MB for up to 1,000,000 links using an in-memory Bloom filter with false-positive rate below 0.1%.")

    p_o3 = add_p()
    p_o3.add_run("3. Sub-50ms Search Latency: ").bold = True
    p_o3.add_run("Execute query tokenization, term lookup, dynamic IDF calculation, and TF-IDF ranking in under 50 milliseconds across 100,000 indexed records.")

    p_o4 = add_p()
    p_o4.add_run("4. Automated Scraping Politeness: ").bold = True
    p_o4.add_run("Enforce 100% compliance with target domain robots.txt disallow directives and per-domain crawl delays.")

    p_o5 = add_p()
    p_o5.add_run("5. Standalone Desktop Binary: ").bold = True
    p_o5.add_run("Produce a single standalone executable under 30 MB that operates without external runtime installations.")

    add_h2("4.2 In-Scope Features (Phase II and Phase III)")
    p_i1 = add_p()
    p_i1.add_run("• Phase II (Core Backend): ").bold = True
    p_i1.add_run("Concurrent crawler swarm, Bloom filter visited set, robots.txt evaluator, HTML readability noise filter, buffered Go channel pipeline, and dedicated SQLite batch writer.")

    p_i2 = add_p()
    p_i2.add_run("• Phase III (Search, UI, and Testing): ").bold = True
    p_i2.add_run("Dynamic query-time TF-IDF ranking engine, Next.js dashboard with live metric event streaming, instant search bar, unit and integration test suite, and performance benchmarks.")

    add_h2("4.3 Out-of-Scope Items")
    p_x1 = add_p()
    p_x1.add_run("• Cloud Synchronization & Clustering: ").bold = True
    p_x1.add_run("No multi-node distributed database replication or remote cloud backups.")

    p_x2 = add_p()
    p_x2.add_run("• Neural NLP and Large Language Models: ").bold = True
    p_x2.add_run("No deep neural networks or generative AI APIs. Ranking relies strictly on mathematical TF-IDF.")

    p_x3 = add_p()
    p_x3.add_run("• Multi-User Authentication: ").bold = True
    p_x3.add_run("No user login accounts or role-based access control. The app runs as a single-user workstation tool.")

    p_x4 = add_p()
    p_x4.add_run("• Headless JavaScript Execution: ").bold = True
    p_x4.add_run("The crawler processes raw static HTML byte streams without embedding heavy browser engines like Chromium.")

    # ----------------------------------------------------
    # SECTION 5: SYSTEM ARCHITECTURE & DESIGN
    # ----------------------------------------------------
    add_h1("Section 5: System Architecture & Design")

    add_h2("5.1 High-Level Architecture Overview")
    add_p(
        "The system follows a decoupled three-tier architecture: the Presentation Layer (Next.js desktop UI), the IPC Runtime Bridge "
        "(Wails v2), and the Core Backend Systems Engine (Go runtime). Figure 1 illustrates the high-level block diagram and component connections."
    )

    fig1_path = "C:/Users/naman/Documents/GitHub/Go-Search-Engine/docs/phase1/figure1_architecture.png"
    if os.path.exists(fig1_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        run_img = p_img.add_run()
        run_img.add_picture(fig1_path, width=Inches(4.8))
        add_p("Figure 1: High-Level System Architecture and Concurrency Model.", space_after=8, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_h2("5.2 Major Component Subsystems")
    add_p("The system is organized into eight primary modules:")
    
    p_m1 = add_p()
    p_m1.add_run("1. Frontier Queue: ").bold = True
    p_m1.add_run("Thread-safe in-memory FIFO queue that normalizes discovered URLs and schedules them for worker fetching.")

    p_m2 = add_p()
    p_m2.add_run("2. Bloom Filter (Visited Set): ").bold = True
    p_m2.add_run("Probabilistic bitset tracking visited links in O(k) time, preventing link cycles while consuming under 5 MB of RAM.")

    p_m3 = add_p()
    p_m3.add_run("3. Polite Scraping Engine: ").bold = True
    p_m3.add_run("Caches domain robots.txt files, verifies crawler permissions, and applies rate-limiting delays.")

    p_m4 = add_p()
    p_m4.add_run("4. Concurrent Worker Swarm: ").bold = True
    p_m4.add_run("Lightweight goroutines that pop URLs from the frontier and stream HTTP response bodies over pooled TCP connections.")

    p_m5 = add_p()
    p_m5.add_run("5. HTML Parser & Noise Removal: ").bold = True
    p_m5.add_run("Strips scripts, styling, navigation bars, and footers from HTML streams, isolating readable body text and child links.")

    p_m6 = add_p()
    p_m6.add_run("6. Buffered Channel Pipeline: ").bold = True
    p_m6.add_run("A thread-safe channel (chan ParsedDocument, capacity 500) that buffers documents and isolates network workers from disk I/O.")

    p_m7 = add_p()
    p_m7.add_run("7. Dedicated SQLite Batch Writer: ").bold = True
    p_m7.add_run("A single goroutine that drains the channel and writes batches of 50 documents per database transaction, preventing locks.")

    p_m8 = add_p()
    p_m8.add_run("8. Query Engine & TF-IDF Ranker: ").bold = True
    p_m8.add_run("Tokenizes query strings, retrieves matching term counts from SQLite, computes dynamic IDF scores, and returns sorted results.")

    add_h2("5.3 System Lifecycle and Data Flow (DFD Level 1)")
    add_p(
        "Figure 2 illustrates the data flow diagram (DFD Level 1) for both the web crawling pipeline and the search retrieval flow."
    )

    fig2_path = "C:/Users/naman/Documents/GitHub/Go-Search-Engine/docs/phase1/figure2_dataflow.png"
    if os.path.exists(fig2_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(4)
        p_img2.paragraph_format.space_after = Pt(2)
        run_img2 = p_img2.add_run()
        run_img2.add_picture(fig2_path, width=Inches(4.8))
        add_p("Figure 2: System Data Flow and Pipeline Lifecycle (DFD Level 1).", space_after=8, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_h2("5.4 Input-Process-Output (IPO) Analysis")
    add_p("Table 2 outlines the operational input, internal processing, and generated output across the three core operational phases.")

    # Table 2: IPO
    table_ipo = doc.add_table(rows=4, cols=4)
    table_ipo.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_ipo.autofit = False

    ipo_widths = [Inches(1.2), Inches(1.5), Inches(2.2), Inches(1.6)]
    for row in table_ipo.rows:
        for idx, width in enumerate(ipo_widths):
            row.cells[idx].width = width

    ipo_headers = ["Pipeline Stage", "Input Data", "Internal Processing", "Output Produced"]
    for idx, h in enumerate(ipo_headers):
        cell = table_ipo.rows[0].cells[idx]
        set_cell_background(cell, "E8EEF8")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)

    ipo_data = [
        ("Web Crawling", "Seed URL, Max Pages limit, Domain scope", "Frontier queue dispatch, Bloom filter check, robots.txt verification, HTTP GET streaming", "Raw HTML response streams, child URLs added to frontier"),
        ("Content Indexing", "Raw HTML stream, Document URL", "HTML tokenization, script/boilerplate stripping, term frequency calculation, SQLite batch commit", "Updated SQLite Inverted Index (Documents, Terms, DocumentTerms)"),
        ("Interactive Search", "Search keywords from user interface", "Query tokenization, SQLite term lookup, dynamic IDF calculation, TF-IDF dot product, sort", "Ranked list of matching URLs, page titles, and relevance scores")
    ]

    for row_idx, r_data in enumerate(ipo_data):
        for col_idx, text in enumerate(r_data):
            cell = table_ipo.rows[row_idx + 1].cells[col_idx]
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(8.5)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                run.font.size = Pt(8.5)

    set_table_borders(table_ipo, "D0D0D0")
    add_p("Table 2: Input-Process-Output (IPO) specification across system lifecycle stages.", space_after=10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_h2("5.5 Concurrency Primitives and Mathematical Formulations")
    add_p(
        "1. Goroutines and context.Context Cancellation: The master crawler coordinates workers via a sync.WaitGroup and a context.Context. "
        "When the user terminates a crawl, context cancellation propagates across all active worker goroutines, closing HTTP sockets gracefully."
    )
    
    add_p(
        "2. Bloom Filter Sizing Mathematics: To track n expected URLs with a false-positive probability p, the required bit array size m "
        "and optimal hash function count k are derived mathematically via Equations 1 and 2:"
    )

    # OMML Equation 1
    eq1_xml = '''
    <m:r><m:t>m = - </m:t></m:r>
    <m:f>
        <m:num><m:r><m:t>n · ln(p)</m:t></m:r></m:num>
        <m:den><m:r><m:t>(ln 2)²</m:t></m:r></m:den>
    </m:f>
    <m:r><m:t>       (1)</m:t></m:r>
    '''
    add_omml_equation(doc, eq1_xml)

    # OMML Equation 2
    eq2_xml = '''
    <m:r><m:t>k = </m:t></m:r>
    <m:f>
        <m:num><m:r><m:t>m</m:t></m:r></m:num>
        <m:den><m:r><m:t>n</m:t></m:r></m:den>
    </m:f>
    <m:r><m:t> · ln(2)       (2)</m:t></m:r>
    '''
    add_omml_equation(doc, eq2_xml)

    add_p(
        "For n = 1,000,000 URLs and a strict false-positive threshold p = 0.001 (0.1%), evaluating Equation 1 yields m = 14,377,588 bits (~1.71 MB). "
        "Evaluating Equation 2 gives k = 10 hash functions. The Bloom filter thus guarantees sub-2 MB memory consumption across one million URLs."
    )

    add_p(
        "3. Query-Time TF-IDF Mathematical Ranking: Rather than pre-computing static weights, relevance ranking is calculated dynamically at query time. "
        "Term Frequency (TF) for term t in document d is normalized by document length in Equation 3:"
    )

    # OMML Equation 3
    eq3_xml = '''
    <m:r><m:t>TF(t, d) = </m:t></m:r>
    <m:f>
        <m:num>
            <m:sSub>
                <m:e><m:r><m:t>f</m:t></m:r></m:e>
                <m:sub><m:r><m:t>t,d</m:t></m:r></m:sub>
            </m:sSub>
        </m:num>
        <m:den>
            <m:r><m:t>∑</m:t></m:r>
            <m:sSub>
                <m:e><m:r><m:t>f</m:t></m:r></m:e>
                <m:sub><m:r><m:t>t',d</m:t></m:r></m:sub>
            </m:sSub>
        </m:den>
    </m:f>
    <m:r><m:t>       (3)</m:t></m:r>
    '''
    add_omml_equation(doc, eq3_xml)

    add_p(
        "Smoothed Inverse Document Frequency (IDF) accounts for term rarity across the total document corpus D in Equation 4:"
    )

    # OMML Equation 4
    eq4_xml = '''
    <m:r><m:t>IDF(t, D) = ln</m:t></m:r>
    <m:d>
        <m:e>
            <m:f>
                <m:num><m:r><m:t>1 + |D|</m:t></m:r></m:num>
                <m:den><m:r><m:t>1 + |{d ∈ D : t ∈ d}|</m:t></m:r></m:den>
            </m:f>
        </m:e>
    </m:d>
    <m:r><m:t> + 1       (4)</m:t></m:r>
    '''
    add_omml_equation(doc, eq4_xml)

    add_p(
        "The composite relevance score for query q against candidate document d is the inner product defined in Equation 5:"
    )

    # OMML Equation 5
    eq5_xml = '''
    <m:r><m:t>Score(q, d) = ∑ [ TF(t, d) · IDF(t, D) ]       (5)</m:t></m:r>
    '''
    add_omml_equation(doc, eq5_xml)

    add_h2("5.6 SQLite Inverted Index Schema Design")
    add_p("The database schema uses three normalized tables with B-Tree indexes:")
    p_s1 = add_p()
    p_s1.add_run("• Documents Table: ").bold = True
    p_s1.add_run("id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE NOT NULL, title TEXT, crawled_at TIMESTAMP.")

    p_s2 = add_p()
    p_s2.add_run("• Terms Table: ").bold = True
    p_s2.add_run("id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT UNIQUE NOT NULL (Indexed with UNIQUE B-Tree on word).")

    p_s3 = add_p()
    p_s3.add_run("• DocumentTerms Table: ").bold = True
    p_s3.add_run("term_id INTEGER, document_id INTEGER, term_frequency INTEGER, PRIMARY KEY (term_id, document_id), FOREIGN KEY (term_id) REFERENCES terms(id), FOREIGN KEY (document_id) REFERENCES documents(id).")

    # ----------------------------------------------------
    # SECTION 6: WORK PLAN & TIMELINE
    # ----------------------------------------------------
    add_h1("Section 6: Work Plan & Timeline")

    add_h2("6.1 Milestone Schedule")
    add_p(
        "The project maps across six milestones from Phase I submission to final Phase III examination, detailed in Table 3."
    )

    # Table 3: Timeline
    table_time = doc.add_table(rows=7, cols=4)
    table_time.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_time.autofit = False

    time_widths = [Inches(1.0), Inches(2.2), Inches(1.8), Inches(1.5)]
    for row in table_time.rows:
        for idx, width in enumerate(time_widths):
            row.cells[idx].width = width

    time_headers = ["Milestone", "Deliverable Description", "Phase Mapping", "Target Date"]
    for idx, h in enumerate(time_headers):
        cell = table_time.rows[0].cells[idx]
        set_cell_background(cell, "E8EEF8")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)

    time_data = [
        ("M1", "Problem definition, system architecture design, Phase 1 documentation submission", "Phase I (Design & Feasibility)", "October 19, 2026"),
        ("M2", "Wails v2 desktop shell setup, Next.js frontend scaffolding, Go struct TypeScript bindings", "Phase II (Core Implementation)", "November 5, 2026"),
        ("M3", "Goroutine crawler swarm, in-memory Bloom filter, robots.txt polite scraping engine", "Phase II (Core Implementation)", "November 20, 2026"),
        ("M4", "HTML readability tokenizer, buffered Go channel pipeline, SQLite batch indexer", "Phase II (Core Implementation)", "December 5, 2026"),
        ("M5", "Dynamic query-time TF-IDF ranking engine, instant search bar, real-time Wails metrics", "Phase III (Search & UI Polish)", "December 20, 2026"),
        ("M6", "Unit/integration testing, performance benchmarking, final documentation, viva presentation", "Phase III (Evaluation & Viva)", "January 15, 2027")
    ]

    for row_idx, r_data in enumerate(time_data):
        for col_idx, text in enumerate(r_data):
            cell = table_time.rows[row_idx + 1].cells[col_idx]
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(8.5)
            elif col_idx == 3:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(text)
                run.font.size = Pt(8.5)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                run.font.size = Pt(8.5)

    set_table_borders(table_time, "D0D0D0")
    add_p("Table 3: Work plan milestone schedule mapping Phase I through Phase III.", space_after=10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_h2("6.2 Phase Deliverables Breakdown")
    add_p(
        "• Phase I Deliverables (Completed): Formal project proposal, architectural block diagram, DFD Level 1, language justification, "
        "and complete Phase 1 documentation report."
    )
    add_p(
        "• Phase II Deliverables (Target: December 2026): Functional concurrent crawler in Go, in-memory Bloom filter, HTML noise stripper, "
        "buffered channel pipeline, and atomic SQLite batch writer."
    )
    add_p(
        "• Phase III Deliverables (Target: January 2027): Dynamic TF-IDF ranking engine, real-time Wails UI dashboard with streaming metrics, "
        "unit and integration test suite, performance benchmark report, and final viva presentation."
    )

    add_h2("6.3 Task Distribution Across Team Members")
    add_p("Table 4 outlines the module ownership across team members:")

    # Table 4: Task Distribution
    table_task = doc.add_table(rows=4, cols=3)
    table_task.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_task.autofit = False

    task_widths = [Inches(1.8), Inches(1.8), Inches(2.9)]
    for row in table_task.rows:
        for idx, width in enumerate(task_widths):
            row.cells[idx].width = width

    task_headers = ["Team Member", "Program / Roll No", "Primary Architectural Responsibilities"]
    for idx, h in enumerate(task_headers):
        cell = table_task.rows[0].cells[idx]
        set_cell_background(cell, "E8EEF8")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)

    task_data = [
        ("Naman Katewa (Project Lead)", "B.Sc. (H) Cyber Security\nRoll No: 2401830002", "Overall systems architecture, concurrent crawler swarm, in-memory Bloom filter visited set, robots.txt polite scraping compliance, and Wails IPC runtime bridge."),
        ("K Sai Vignesh Yadav", "B.Sc. (H) Computer Science\nRoll No: 2401720006", "SQLite inverted index schema design, single-threaded batch writer goroutine, buffered Go channel pipeline, and HTML readability noise removal module."),
        ("Hrishit Kaushal", "B.Sc. (H) Computer Science\nRoll No: 2501722016", "Query tokenization, dynamic query-time TF-IDF relevance ranking algorithms, Next.js frontend UI dashboard, real-time Wails event integration, and test suite execution.")
    ]

    for row_idx, r_data in enumerate(task_data):
        for col_idx, text in enumerate(r_data):
            cell = table_task.rows[row_idx + 1].cells[col_idx]
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                run.bold = True
                run.font.size = Pt(8.5)
            elif col_idx == 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(text)
                run.font.size = Pt(8.5)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(text)
                run.font.size = Pt(8.5)

    set_table_borders(table_task, "D0D0D0")
    add_p("Table 4: Team task allocation and module ownership matrix.", space_after=10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    # ----------------------------------------------------
    # SECTION 7: REFERENCES
    # ----------------------------------------------------
    add_h1("Section 7: References")
    add_p("All references adhere to the IEEE citation standard:")

    refs = [
        "[1] A. Donovan and B. Kernighan, The Go Programming Language, 1st ed. Boston, MA, USA: Addison-Wesley Professional, 2015.",
        "[2] B. H. Bloom, \"Space/time trade-offs in hash coding with allowable errors,\" Communications of the ACM, vol. 13, no. 7, pp. 422-426, Jul. 1970, doi: 10.1145/362686.362692.",
        "[3] G. Salton and C. Buckley, \"Term-weighting approaches in automatic text retrieval,\" Information Processing & Management, vol. 24, no. 5, pp. 513-523, 1988, doi: 10.1016/0306-4573(88)90021-0.",
        "[4] C. D. Manning, P. Raghavan, and H. Schütze, Introduction to Information Retrieval. Cambridge, UK: Cambridge University Press, 2008.",
        "[5] Wails Development Team, \"Wails: Build desktop applications using Go and Web Technologies,\" Wails Documentation, 2026. [Online]. Available: https://wails.io/docs/introduction. [Accessed: October 2026].",
        "[6] D. Vyukov, \"Go Preemptive Scheduler Design Document,\" Go Programming Language Wiki, 2019. [Online]. Available: https://go.googlesource.com/proposal/+/master/design/24543-non-cooperative-preemption.md. [Accessed: October 2026].",
        "[7] D. R. Hipp, \"SQLite Architecture and Concurrency Locking Mechanisms,\" SQLite Consortium, 2026. [Online]. Available: https://www.sqlite.org/lockingv3.html. [Accessed: October 2026]."
    ]

    for ref in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.3
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(3)
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    output_docx = "C:/Users/naman/Documents/GitHub/Go-Search-Engine/docs/phase1/2401830002_NamanKatewa_ENSP465_Phase1.docx"
    doc.save(output_docx)
    print(f"Document saved successfully to {output_docx}")

if __name__ == '__main__':
    create_document()

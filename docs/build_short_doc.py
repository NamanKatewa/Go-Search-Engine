import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import os

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

def generate_doc():
    doc = docx.Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("ENSP465 Project Documentation | Page ")
        f_run.font.name = 'Times New Roman'
        f_run.font.size = Pt(9)
        f_run.font.color.rgb = RGBColor(128, 128, 128)
        fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        f_p._p.append(fldSimple)

    def add_p(text="", space_after=6, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.3):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = line_spacing
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        if text:
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            run.font.bold = bold
            run.font.italic = italic
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
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
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(30, 50, 100)
        return p

    # Cover Header
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(10)
    p_inst.paragraph_format.space_after = Pt(2)
    run_inst = p_inst.add_run("K.R. MANGALAM UNIVERSITY")
    run_inst.font.name = 'Times New Roman'
    run_inst.font.size = Pt(16)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(15, 30, 70)

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_after = Pt(14)
    run_dept = p_dept.add_run("School of Engineering & Technology | Department of Computer Science & Engineering\nENSP465 — New Age Programming Languages Lab")
    run_dept.font.name = 'Times New Roman'
    run_dept.font.size = Pt(11)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(16)
    run_title = p_title.add_run("PROJECT SHORT DOCUMENTATION\nHigh-Performance Concurrent Web Crawler & Local Inverted Index Search Engine in Go")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(14)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(180, 40, 30)

    # Metadata table
    table_meta = doc.add_table(rows=2, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_meta.autofit = False
    widths = [Inches(2.0), Inches(4.5)]
    for row in table_meta.rows:
        for idx, w in enumerate(widths):
            row.cells[idx].width = w

    meta_data = [
        ("Project Team:", "• Naman Katewa (Roll No: 2401830002) — B.Sc. (Hons.) Cyber Security [Lead]\n• K Sai Vignesh Yadav (Roll No: 2401720006) — B.Sc. (Hons.) Computer Science\n• Hrishit Kaushal (Roll No: 2501722016) — B.Sc. (Hons.) Computer Science"),
        ("Semester & Program:", "Semester 5th, B.Sc. (Hons.), Academic Year 2026–2027")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        c0 = table_meta.rows[row_idx].cells[0]
        c1 = table_meta.rows[row_idx].cells[1]
        set_cell_background(c0, "F1F5F9")
        set_cell_margins(c0, 40, 40, 60, 60)
        set_cell_margins(c1, 40, 40, 60, 60)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.5)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)

    set_table_borders(table_meta, "CBD5E1")

    # Section 1
    add_h1("1. Project Overview & Objectives")
    add_p(
        "The Go Desktop Search Engine is a high-performance, standalone, locally hosted search engine that operates "
        "completely independently of the cloud. It encapsulates both an autonomous concurrent web crawler and an instant "
        "keyword search interface in a single compiled desktop application. The system was specifically architected to "
        "demonstrate core systems engineering concepts in Go: lightweight CSP concurrency, thread-safe database batching, "
        "probabilistic memory-bounded data structures, and dynamic query-time information retrieval."
    )
    add_p(
        "Key project objectives include: (1) building a goroutine crawler swarm capable of parsing hundreds of pages per second; "
        "(2) enforcing strict memory safety during massive crawls using an in-memory Bloom Filter to prevent Out of Memory (OOM) crashes; "
        "(3) eliminating SQLite lock contention using a dedicated single-writer goroutine with atomic WAL batch commits; "
        "(4) calculating dynamic TF-IDF relevance scores on the fly; and (5) providing a native desktop GUI with live telemetry."
    )

    # Section 2
    add_h1("2. Technologies Used")
    t_tech = doc.add_table(rows=6, cols=3)
    t_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_tech.autofit = False
    tech_widths = [Inches(1.8), Inches(1.8), Inches(2.9)]
    for row in t_tech.rows:
        for idx, w in enumerate(tech_widths):
            row.cells[idx].width = w

    headers = ["Subsystem", "Technology", "Architectural Rationale"]
    for idx, h in enumerate(headers):
        c = t_tech.rows[0].cells[idx]
        set_cell_background(c, "E8EEF8")
        set_cell_margins(c, 50, 50, 60, 60)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)

    tech_rows = [
        ("Backend Systems Core", "Go (Golang 1.26)", "Lightweight 2KB goroutine stacks, CSP channels, compiled machine binary."),
        ("Desktop Runtime & IPC", "Wails v2 + WebView2", "Native OS window wrapper without bundling heavy Chromium/Node runtimes (< 17MB)."),
        ("Frontend Dashboard", "React 19 & TypeScript", "Fullstack type safety with generated Go-to-TypeScript interfaces, built with Vite."),
        ("Inverted Index Storage", "SQLite (modernc.org/sqlite)", "Pure Go embedded SQL engine operating in WAL mode; zero CGO compiler headaches."),
        ("HTML Extraction", "golang.org/x/net/html", "DOM tree tokenization stripping navbars, scripts, and noise via readability heuristics.")
    ]
    for r_idx, r_data in enumerate(tech_rows):
        for c_idx, val in enumerate(r_data):
            cell = t_tech.rows[r_idx + 1].cells[c_idx]
            set_cell_margins(cell, 40, 40, 60, 60)
            p = cell.paragraphs[0]
            run = p.add_run(val)
            run.font.size = Pt(8.5)
            if c_idx == 0:
                run.bold = True

    set_table_borders(t_tech, "CBD5E1")

    # Section 3
    add_h1("3. Implementation Architecture")
    add_p(
        "• Concurrent Crawler Swarm: Configurable worker pool (2 to 16 goroutines) dispatching URLs from an in-memory frontier channel. "
        "Complies strictly with robots.txt exclusion rules per domain.\n"
        "• In-Memory Bloom Filter: Kirsch-Mitzenmacher double-hashing algorithm with Murmur3 fmix64 avalanche mixing to achieve a bounded "
        "false-positive probability (< 0.1%), slashing RAM consumption by > 90% compared to standard Go hash maps.\n"
        "• Dedicated Database Writer: A single goroutine consumes parsed documents across a buffered channel and commits transactions "
        "in batches into SQLite (documents, terms, document_terms), completely eliminating database is locked errors.\n"
        "• Dynamic TF-IDF Scoring: Computes sublinear TF weights and smooth IDF at query time with cosine document length normalization."
    )

    # Section 4: UI Screenshots
    add_h1("4. User Interface & Demonstration Screenshots")
    add_p("The working desktop user interface was tested and captured demonstrating full operational capability:")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    s1_path = os.path.join(base_dir, "screenshots", "dashboard.png")
    s2_path = os.path.join(base_dir, "screenshots", "search_results.png")

    if os.path.exists(s1_path):
        add_h2("4.1 Crawler Dashboard View")
        add_p("The Crawler Dashboard displays real-time crawler swarm execution, active throughput, frontier queue size, Bloom filter memory metrics, and live streaming worker activity logs:")
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.paragraph_format.space_after = Pt(4)
        run_img1 = p_img1.add_run()
        run_img1.add_picture(s1_path, width=Inches(6.2))
        add_p("Figure 1: Real-time Crawler Dashboard displaying concurrent worker swarm, Bloom filter memory savings, and SQLite batch commits.", space_after=12, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    if os.path.exists(s2_path):
        add_h2("4.2 Instant Search Engine View")
        add_p("The Search Engine tab demonstrates instant inverted index querying with dynamic query-time TF-IDF relevance calculation and snippet extraction:")
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_after = Pt(4)
        run_img2 = p_img2.add_run()
        run_img2.add_picture(s2_path, width=Inches(6.2))
        add_p("Figure 2: Instant Search Interface displaying ranked search results for 'concurrency goroutines' with TF-IDF score badges and latency metrics.", space_after=12, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

    # Section 5: Conclusion
    add_h1("5. Conclusion & Verification Summary")
    add_p(
        "Phase 2 core implementation deliverables have been fully achieved and validated against unit and integration tests. "
        "The compiled binary (go-search-engine.exe) operates autonomously on Windows with zero external runtime installations, "
        "combining high-throughput Go concurrent crawling, mathematical memory bounding via Bloom filters, atomic SQLite persistence, "
        "and sub-millisecond TF-IDF search ranking."
    )

    out_path = os.path.join(base_dir, "Short_Documentation.docx")
    doc.save(out_path)
    print(f"Document successfully created at {out_path}")

if __name__ == "__main__":
    generate_doc()

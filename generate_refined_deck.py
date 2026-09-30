import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

# ==============================================================================
# COLOR PALETTE (Clean, Restrained, Non-AI Aesthetic)
# ==============================================================================
C_BG_OFFWHITE        = RGBColor(248, 250, 252)  # #F8FAFC - Soft neutral background
C_WHITE              = RGBColor(255, 255, 255)  # #FFFFFF - Crisp white for containers
C_TEXT_DARK          = RGBColor(15, 23, 42)     # #0F172A - Deep slate for headings & primary text
C_TEXT_MUTED         = RGBColor(71, 85, 105)    # #475569 - Muted slate for captions & body
C_BORDER_LIGHT       = RGBColor(203, 213, 225)  # #CBD5E1 - Light border
C_BORDER_DARK        = RGBColor(148, 163, 184)  # #94A3B8 - Medium border

C_PRIMARY_NAVY       = RGBColor(30, 58, 138)    # #1E3A8A - Deep navy for headers & structure
C_SLATE_TEAL         = RGBColor(14, 116, 144)   # #0E7490 - Restrained slate teal for secondary nodes
C_EMERALD_GREEN      = RGBColor(22, 101, 52)    # #166534 - Forest green for verified/hardened
C_ACCENT_AMBER       = RGBColor(180, 83, 9)     # #B45309 - Single sharp accent for High severity / callouts
C_PURPLE_DEEP        = RGBColor(107, 33, 168)   # #6B21A8 - Deep purple for correlation/scoring
C_CRIMSON_DEEP       = RGBColor(153, 27, 27)    # #991B1B - Deep crimson for risk/threat

def set_fill(shape, fill_color, border_color=None, border_width=Pt(1)):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = border_width
    else:
        shape.line.fill.background()

def add_clean_box(slide, left, top, width, height, title, subtitle="", fill_col=C_WHITE, border_col=C_BORDER_LIGHT, border_width=Pt(1), title_size=Pt(10.5), sub_size=Pt(9.0), align=PP_ALIGN.LEFT, title_bold=True, shape_type=MSO_SHAPE.RECTANGLE):
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    set_fill(shape, fill_col, border_color=border_col, border_width=border_width)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.06)
    tf.margin_bottom = Inches(0.06)
    tf.clear()
    
    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.bold = title_bold
    p0.font.size = title_size
    p0.font.name = "Arial"
    if fill_col in [C_PRIMARY_NAVY, C_SLATE_TEAL, C_EMERALD_GREEN, C_ACCENT_AMBER, C_PURPLE_DEEP, C_CRIMSON_DEEP]:
        p0.font.color.rgb = C_WHITE
    else:
        p0.font.color.rgb = C_PRIMARY_NAVY if border_col == C_PRIMARY_NAVY else C_TEXT_DARK
    p0.alignment = align
    
    if subtitle:
        lines = [line.strip() for line in subtitle.split('\n') if line.strip()]
        for idx, line in enumerate(lines):
            p1 = tf.add_paragraph()
            p1.text = line
            p1.font.bold = False
            p1.font.size = sub_size
            p1.font.name = "Arial"
            if fill_col in [C_PRIMARY_NAVY, C_SLATE_TEAL, C_EMERALD_GREEN, C_ACCENT_AMBER, C_PURPLE_DEEP, C_CRIMSON_DEEP]:
                p1.font.color.rgb = RGBColor(226, 232, 240)
            else:
                p1.font.color.rgb = C_TEXT_DARK if line.startswith("•") else C_TEXT_MUTED
            p1.alignment = align
            p1.space_before = Pt(2.5) if idx > 0 else Pt(2)
        
    return shape

def add_connector(slide, x1, y1, x2, y2, color=C_BORDER_DARK, width=Pt(1.2)):
    connector = slide.shapes.add_connector(
        pptx.enum.shapes.MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2
    )
    connector.line.color.rgb = color
    connector.line.width = width
    return connector

def create_deck():
    src_path = 'SIH26163_ARGUS_Idea_PPT_Color.pptx'
    if not os.path.exists(src_path):
        src_path = 'sources/SIH26163_ARGUS_Idea_PPT_Color.pptx'
        
    print(f"Loading template from {src_path}...")
    prs = pptx.Presentation(src_path)
    
    # ==============================================================================
    # SLIDE 1: Title
    # ==============================================================================
    print("Refining Slide 1: Title...")
    s1 = prs.slides[0]
    # Remove shapes after shape 7 (keep SIH header, logo, base metadata textboxes)
    # We update the text in existing shapes or add clean updated blocks
    for shape in s1.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "Idea Title:" in p.text or "ARGUS" in p.text:
                    p.text = "ARGUS: Automated Security Assessment and Finding Correlation for World Monitor"
                    p.font.bold = True
                    p.font.size = Pt(18)
                    p.font.color.rgb = C_PRIMARY_NAVY
                    p.font.name = "Arial"
                elif "Problem Statement Title" in p.text:
                    p.text = "Problem Statement: Security Assessment of the World Monitor Application (SIH26163)"
                    p.font.bold = True
                    p.font.size = Pt(13)
                    p.font.name = "Arial"
                elif "Theme-" in p.text or "Theme:" in p.text:
                    p.text = "Theme: Smart Automation  |  Category: Software  |  Organization: NTRO"
                    p.font.size = Pt(12)
                    p.font.name = "Arial"
                elif "Team ID-" in p.text or "Team ID:" in p.text:
                    p.text = "Team ID: [Team ID]  |  Team Name: [Team Name]"
                    p.font.size = Pt(12)
                    p.font.name = "Arial"
                    
    # ==============================================================================
    # SLIDE 2: Proposed Solution
    # ==============================================================================
    print("Refining Slide 2: Proposed Solution...")
    s2 = prs.slides[1]
    
    # Update slide header title
    for s_idx, shape in enumerate(list(s2.shapes)[:7]):
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "ARGUS:" in p.text or "Proposed Solution" in p.text:
                    p.text = "Attack surface recon drives automated static audit and risk scoring"
                    p.font.bold = True
                    p.font.size = Pt(14)
                    p.font.color.rgb = C_PRIMARY_NAVY
                    p.font.name = "Arial"
                    
    # Clear content shapes (index >= 7)
    shapes_to_remove = [s._element for s in list(s2.shapes)[7:]]
    for elem in shapes_to_remove:
        s2.shapes._spTree.remove(elem)
            
    # Problem definition card (Left side top)
    prob_box = add_clean_box(s2, Inches(0.50), Inches(1.25), Inches(7.60), Inches(1.10),
                             "THE PROBLEM: UNCONTROLLED ATTACK SURFACE EXPOSURE",
                             "World Monitor exposes 166 edge endpoints, leaving 137 routes accessible without authentication to unmetered requests and external inputs. Manual audit of this surface is slow and error-prone, while generic scanners generate disjointed, unprioritized alerts.",
                             fill_col=C_WHITE, border_col=C_CRIMSON_DEEP, border_width=Pt(1.2),
                             title_size=Pt(10), sub_size=Pt(9.0), title_bold=True)
                             
    # 5-Stage Pipeline Flow (Flow A)
    pipe_lbl = s2.shapes.add_textbox(Inches(0.50), Inches(2.45), Inches(7.60), Inches(0.28))
    tf = pipe_lbl.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = "Automated Five-Stage Assessment Pipeline (6.5 Seconds End-to-End) :"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_PRIMARY_NAVY
    p.font.name = "Arial"
    
    stage_w = Inches(1.42)
    stage_h = Inches(1.45)
    stages = [
        ("1. Recon", "Map 166 routes, 428 RSS feeds, & Tauri boundaries.", "endpoints.csv\n(166 routes)", C_PRIMARY_NAVY),
        ("2. Scanners", "Lockfile audit (1,795 pkgs) & static AST parse.", "npm-audit.json\n(28 advisories)", C_SLATE_TEAL),
        ("3. Safe PoC", "5 non-destructive local proof checks.", "evidence/*.txt\n(5 proof files)", C_EMERALD_GREEN),
        ("4. Correlate", "Deduplicate, map CWE to OWASP, CVSS 3.1.", "findings.json\n(12 flaws)", C_PURPLE_DEEP),
        ("5. Report", "Publication PDF, interactive HTML, JSON.", "report.pdf\nHTML & MD", C_ACCENT_AMBER)
    ]
    
    for s_idx, (st_name, st_desc, st_out, st_col) in enumerate(stages):
        sx = Inches(0.50 + s_idx * 1.55)
        # Stage top block
        box = add_clean_box(s2, sx, Inches(2.80), stage_w, Inches(1.05),
                            st_name, st_desc, fill_col=C_WHITE, border_col=st_col, border_width=Pt(1.2),
                            title_size=Pt(9.5), sub_size=Pt(8.0))
        # Arrow connector between stages
        if s_idx < 4:
            add_connector(s2, sx + stage_w, Inches(3.32), sx + stage_w + Inches(0.13), Inches(3.32), color=C_PRIMARY_NAVY, width=Pt(1.5))
        # Output artifact block underneath (Second Lane)
        out_box = add_clean_box(s2, sx, Inches(3.95), stage_w, Inches(0.65),
                                "Output Artifact:", st_out, fill_col=C_BG_OFFWHITE, border_col=st_col, border_width=Pt(1.0),
                                title_size=Pt(8.0), sub_size=Pt(7.5))
                                
    # Core Findings Summary Table on Slide 2 bottom
    tbl_shape = s2.shapes.add_table(5, 3, Inches(0.50), Inches(4.75), Inches(7.60), Inches(1.85))
    t2 = tbl_shape.table
    t2.columns[0].width = Inches(3.20)
    t2.columns[1].width = Inches(1.80)
    t2.columns[2].width = Inches(2.60)
    
    t2_headers = ["Vulnerability (Statically Verified)", "Classification", "CVSS 3.1 & Evidence"]
    for c_idx, h_text in enumerate(t2_headers):
        cell = t2.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_PRIMARY_NAVY
        tf = cell.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.text = h_text
        p.font.bold = True
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_WHITE
        p.font.name = "Arial"
        
    t2_rows = [
        ("Fail-Open Rate Limiter Degradation", "CWE-770 | OWASP A04", "7.5 High - Redis timeout returns null"),
        ("Trusted Types innerHTML Bypass", "CWE-79 | OWASP A03", "6.1 Med - 357 call sites use placeholder"),
        ("SSRF DNS Rebinding in MCP Proxy", "CWE-918 | OWASP A10", "6.3 Med - Edge fetch socket unpinned"),
        ("Prompt Injection Regex Bypass", "CWE-20 | LLM01", "6.5 Med - English-only blocklist bypass")
    ]
    for r_idx, row in enumerate(t2_rows):
        bg = C_WHITE if r_idx % 2 == 0 else C_BG_OFFWHITE
        for c_idx, val in enumerate(row):
            cell = t2.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            tf = cell.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.text = val
            p.font.size = Pt(8.0)
            p.font.name = "Arial"
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_TEXT_DARK
            elif c_idx == 1:
                p.font.color.rgb = C_TEXT_MUTED
            else:
                p.font.bold = True
                p.font.color.rgb = C_ACCENT_AMBER if "7.5" in val else C_PRIMARY_NAVY
                
    # Right Side (40%): Native Donut Chart of Endpoint Exposure
    chart_container = add_clean_box(s2, Inches(8.30), Inches(1.25), Inches(4.55), Inches(5.35),
                                    "ENDPOINT EXPOSURE (166 TOTAL)",
                                    "82% of edge endpoints operate without authentication\nSource: argus/out/endpoints.csv",
                                    fill_col=C_WHITE, border_col=C_BORDER_LIGHT, border_width=Pt(1.2),
                                    title_size=Pt(10), sub_size=Pt(8.5))
                                    
    cd2 = CategoryChartData()
    cd2.categories = ['Unauthenticated (137)', 'Authenticated (29)']
    cd2.add_series('Endpoints', (137, 29))
    chart_shape = s2.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(8.50), Inches(2.15), Inches(4.15), Inches(3.20), cd2)
    chart2 = chart_shape.chart
    chart2.has_legend = True
    chart2.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart2.legend.font.size = Pt(9)
    chart2.legend.font.name = "Arial"
    
    # Exposure takeaway text below chart
    exp_tb = s2.shapes.add_textbox(Inches(8.50), Inches(5.45), Inches(4.15), Inches(1.05))
    tf = exp_tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.clear()
    p = tf.paragraphs[0]
    p.text = "Key Exposure Takeaway:"
    p.font.bold = True
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_PRIMARY_NAVY
    p.font.name = "Arial"
    p1 = tf.add_paragraph()
    p1.text = "137 out of 166 Vercel Edge API routes handle public telemetry, RSS feeds, and market data without session tokens or API keys, requiring strict rate limiters and payload validation."
    p1.font.size = Pt(8.5)
    p1.font.color.rgb = C_TEXT_DARK
    p1.font.name = "Arial"
    
    # ==============================================================================
    # SLIDE 3: Technical Approach
    # ==============================================================================
    print("Refining Slide 3: Technical Approach...")
    s3 = prs.slides[2]
    
    # Update title
    for shape in list(s3.shapes)[:7]:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "TECHNICAL APPROACH" in p.text:
                    p.text = "Unified normalization and two-signal correlation eliminate scanner noise"
                    p.font.bold = True
                    p.font.size = Pt(14)
                    p.font.color.rgb = C_PRIMARY_NAVY
                    p.font.name = "Arial"
                    
    # Clear content shapes (index >= 7)
    shapes_to_remove3 = [s._element for s in list(s3.shapes)[7:]]
    for elem in shapes_to_remove3:
        s3.shapes._spTree.remove(elem)
            
    # Left side: Deliverables Table and Safe Verification Rules (55% width)
    tech_lbl = s3.shapes.add_textbox(Inches(0.50), Inches(1.25), Inches(7.00), Inches(0.28))
    tf = tech_lbl.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = "Inspection Method to Deliverable Mapping :"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_PRIMARY_NAVY
    p.font.name = "Arial"
    
    tbl3 = s3.shapes.add_table(6, 3, Inches(0.50), Inches(1.55), Inches(7.00), Inches(2.25)).table
    tbl3.columns[0].width = Inches(2.00)
    tbl3.columns[1].width = Inches(2.60)
    tbl3.columns[2].width = Inches(2.40)
    
    t3_headers = ["Pipeline Stage", "Inspection Method", "Primary Deliverable"]
    for c_idx, h_text in enumerate(t3_headers):
        cell = tbl3.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_PRIMARY_NAVY
        tf = cell.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.text = h_text
        p.font.bold = True
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_WHITE
        p.font.name = "Arial"
        
    t3_rows = [
        ("Endpoint Recon", "AST Route & Param Parsing", "endpoints.csv (166 routes)"),
        ("Dependency Audit", "Lockfile checksum analysis", "npm-audit.json (28 advisories)"),
        ("Code Audit", "Static AST & regex check", "evidence/*.txt (5 proof files)"),
        ("Correlation", "Pydantic v2 deduplication", "findings.json (12 flaws)"),
        ("Reporting", "WeasyPrint & template engine", "report.pdf, report.html, md")
    ]
    for r_idx, row in enumerate(t3_rows):
        bg = C_WHITE if r_idx % 2 == 0 else C_BG_OFFWHITE
        for c_idx, val in enumerate(row):
            cell = tbl3.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            tf = cell.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.text = val
            p.font.size = Pt(8.0)
            p.font.name = "Arial"
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_TEXT_DARK
            elif c_idx == 1:
                p.font.color.rgb = C_TEXT_MUTED
            else:
                p.font.bold = True
                p.font.color.rgb = C_PRIMARY_NAVY
                
    # Safe Verification Rules Callout Box
    safe_box = add_clean_box(s3, Inches(0.50), Inches(3.95), Inches(7.00), Inches(2.65),
                             "SAFE VERIFICATION RULES & ETHICAL GUARDRAILS",
                             "• Localhost Sandbox Only: Testing is executed exclusively against a locally hosted copy of World Monitor; zero packets are transmitted to production worldmonitor.app.\n• Zero Denial-of-Service Payloads: Tests evaluate conditional code branches and error states without flooding threads or exhausting host resources.\n• Zero Data Extraction: Probes do not extract, store, or log sensitive user records or external intelligence feeds.\n• Canary Marker Verification: Automated checks use non-harmful synthetic marker strings to confirm pattern execution safely.",
                             fill_col=C_WHITE, border_col=C_EMERALD_GREEN, border_width=Pt(1.2),
                             title_size=Pt(10), sub_size=Pt(8.5), title_bold=True)
                             
    # Right Side Top: Flow B (Correlation Logic Flowchart)
    flow_lbl = s3.shapes.add_textbox(Inches(7.75), Inches(1.25), Inches(5.10), Inches(0.28))
    tf = flow_lbl.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = "Correlation & Triage Logic Flow (Flow B) :"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_PRIMARY_NAVY
    p.font.name = "Arial"
    
    flow_steps = [
        ("Raw Finding", "Normalizes to schema"),
        ("Group (CWE, Comp)", "Groups advisories by package"),
        ("Confidence Gate", "Assigns High if evidence file exists"),
        ("CVSS 3.1 Scoring", "FIRST base vector & score calculated"),
        ("Correlated Finding", "Output to findings.json")
    ]
    for f_idx, (f_title, f_sub) in enumerate(flow_steps):
        fy = Inches(1.55 + f_idx * 0.52)
        add_clean_box(s3, Inches(7.75), fy, Inches(5.10), Inches(0.44),
                      f"{f_idx + 1}. {f_title}: ", f_sub, fill_col=C_BG_OFFWHITE, border_col=C_BORDER_LIGHT, border_width=Pt(1.0),
                      title_size=Pt(8.5), sub_size=Pt(8.0))
                      
    # Right Side Bottom: Native Donut Chart of Raw Ingestion Sources
    cd3 = CategoryChartData()
    cd3.categories = ['Code Audit (5)', 'npm audit SCA (9)']
    cd3.add_series('Findings', (5, 9))
    chart_shape3 = s3.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(7.75), Inches(4.35), Inches(5.10), Inches(2.25), cd3)
    chart3 = chart_shape3.chart
    chart3.has_legend = True
    chart3.legend.position = XL_LEGEND_POSITION.RIGHT
    chart3.legend.font.size = Pt(8.5)
    chart3.legend.font.name = "Arial"
    chart3.has_title = True
    chart3.chart_title.text_frame.text = "14 raw findings reduced to 12 after grouping\nSource: argus/out/findings.json"
    chart3.chart_title.text_frame.paragraphs[0].font.size = Pt(9.0)
    chart3.chart_title.text_frame.paragraphs[0].font.bold = True
    chart3.chart_title.text_frame.paragraphs[0].font.color.rgb = C_PRIMARY_NAVY
    
    # ==============================================================================
    # SLIDE 4: Feasibility and Viability (MAIN FOCUS)
    # ==============================================================================
    print("Refining Slide 4: Feasibility and Viability...")
    s4 = prs.slides[3]
    
    # Update title
    for shape in list(s4.shapes)[:7]:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "FEASIBILITY AND VIABILITY" in p.text:
                    p.text = "Lightweight open-source architecture operates without external dependencies"
                    p.font.bold = True
                    p.font.size = Pt(14)
                    p.font.color.rgb = C_PRIMARY_NAVY
                    p.font.name = "Arial"
                    
    # Clear content shapes (index >= 7)
    shapes_to_remove4 = [s._element for s in list(s4.shapes)[7:]]
    for elem in shapes_to_remove4:
        s4.shapes._spTree.remove(elem)
            
    # Top Left: Built and Working Today (Measurable facts)
    s4_today = add_clean_box(s4, Inches(0.50), Inches(1.25), Inches(6.00), Inches(2.25),
                             "BUILT AND WORKING TODAY (MEASURABLE FACTS)",
                             "• Single-Command Execution: Entire pipeline completes in 6.5 seconds end-to-end.\n• 166-Route Inventory: AST parser maps 137 public and 29 authenticated edge routes.\n• 12 Scored Vulnerabilities: Every finding carries a FIRST CVSS 3.1 base score.\n• 5 Statically Verified Evidence Files: Detailed code-level proofs written in evidence/*.txt.\n• Multi-Format Reporting: Auto-generates publication PDF, HTML, Markdown, and JSON.",
                             fill_col=C_WHITE, border_col=C_PRIMARY_NAVY, border_width=Pt(1.2),
                             title_size=Pt(10), sub_size=Pt(8.5), title_bold=True)
                             
    # Top Right: Risk Mitigation & Resources
    s4_risks = add_clean_box(s4, Inches(6.75), Inches(1.25), Inches(6.10), Inches(2.25),
                             "RISK MITIGATION & OPEN-SOURCE RESOURCES",
                             "• False Positives: Every code finding requires an evidence file and static code verification.\n• Edge Runtime Limits: AST parsers specifically handle Next.js edge and Tauri Rust IPC paths.\n• Tool Version Drift: Lockfile checksum pinning and pinned container environments.\n• Runtime Safety: Statically verified checks only; runtime exploit payloads are prohibited.\n• Required Resources: Python 3.11+, Node 20+, Docker. All open-source ($0 licensing cost).",
                             fill_col=C_WHITE, border_col=C_SLATE_TEAL, border_width=Pt(1.2),
                             title_size=Pt(10), sub_size=Pt(8.5), title_bold=True)
                             
    # Bottom Left: Flow D (Safe-PoC Decision Flow)
    d_lbl = s4.shapes.add_textbox(Inches(0.50), Inches(3.60), Inches(6.00), Inches(0.28))
    tf = d_lbl.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = "Safe-PoC Decision Flow (Flow D) :"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_PRIMARY_NAVY
    p.font.name = "Arial"
    
    flow_d_steps = [
        ("1. Candidate Finding", "Ingested from static code audit or lockfile advisory"),
        ("2. Static Code Verification", "AST/regex checks pattern; drops finding if pattern absent"),
        ("3. Local Sandbox Gate", "Verifies target is localhost; aborts if external host detected"),
        ("4. Safe Execution Probe", "Executes non-destructive canary check without DoS or data leak"),
        ("5. Evidence File & Report", "Writes evidence file and includes finding in final scored report")
    ]
    for d_idx, (d_title, d_sub) in enumerate(flow_d_steps):
        dy = Inches(3.90 + d_idx * 0.52)
        add_clean_box(s4, Inches(0.50), dy, Inches(6.00), Inches(0.44),
                      f"{d_title}: ", d_sub, fill_col=C_BG_OFFWHITE, border_col=C_BORDER_LIGHT, border_width=Pt(1.0),
                      title_size=Pt(8.5), sub_size=Pt(8.0))
                      
    # Bottom Right: Flow E (Phased Roadmap Timeline)
    e_lbl = s4.shapes.add_textbox(Inches(6.75), Inches(3.60), Inches(6.10), Inches(0.28))
    tf = e_lbl.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = "Phased Engineering Roadmap (Flow E) :"
    p.font.bold = True
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_PRIMARY_NAVY
    p.font.name = "Arial"
    
    roadmap_phases = [
        ("PHASE 1: NOW (Built & Working Today)", 
         "166 route recon • npm audit SCA • 5 statically verified findings • CVSS 3.1 scoring • PDF/HTML/JSON reports.",
         C_PRIMARY_NAVY),
        ("PHASE 2: NEXT (Integrated Next)", 
         "Integrate Semgrep SAST rules • Gitleaks secret detection • OSV database • ZAP/Nuclei DAST • Playwright replay.",
         C_SLATE_TEAL),
        ("PHASE 3: LATER (Enterprise Operations)", 
         "GitHub Actions CI/CD SARIF gate • Pre-commit security hooks • Declarative YAML to scan any similar web app.",
         C_PURPLE_DEEP)
    ]
    for r_idx, (r_title, r_desc, r_col) in enumerate(roadmap_phases):
        ry = Inches(3.90 + r_idx * 0.88)
        add_clean_box(s4, Inches(6.75), ry, Inches(6.10), Inches(0.78),
                      r_title, r_desc, fill_col=C_WHITE, border_col=r_col, border_width=Pt(1.2),
                      title_size=Pt(9.0), sub_size=Pt(8.0))
                      
    # ==============================================================================
    # SLIDE 5: Impact and Benefits (MAIN FOCUS)
    # ==============================================================================
    print("Refining Slide 5: Impact and Benefits...")
    s5 = prs.slides[4]
    
    # Update title
    for shape in list(s5.shapes)[:7]:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "IMPACT AND BENEFITS" in p.text:
                    p.text = "Automated triage replaces manual review while preserving audit trails"
                    p.font.bold = True
                    p.font.size = Pt(14)
                    p.font.color.rgb = C_PRIMARY_NAVY
                    p.font.name = "Arial"
                    
    # Clear content shapes (index >= 7)
    shapes_to_remove5 = [s._element for s in list(s5.shapes)[7:]]
    for elem in shapes_to_remove5:
        s5.shapes._spTree.remove(elem)
            
    # Left Column: Stakeholder Outcomes & Operational Comparison (50% width)
    s5_outcomes = add_clean_box(s5, Inches(0.50), Inches(1.25), Inches(6.15), Inches(2.35),
                                "STAKEHOLDER OUTCOMES & RISK EXPOSURE",
                                "• Security Teams: Raw scanner noise reduced to 12 scored findings; replaces hours of manual triage with a 6.5-second automated scan.\n• Developers: Each finding provides exact file, line number, CVSS 3.1 vector, and actionable remediation diffs (such as DOMPurify integration).\n• NTRO Reviewers: Repeatable, local, non-destructive assessment with an audit trail, using zero production data.\n• Top Unfixed Flaws:\n  - Fail-Open Rate Limiter (CVSS 7.5): Redis outage permits unmetered requests, risking upstream API quota exhaustion.\n  - Trusted Types Bypass (CVSS 6.1): 357 call sites use placeholder reason, risking DOM script injection from feeds.",
                                fill_col=C_WHITE, border_col=C_PRIMARY_NAVY, border_width=Pt(1.2),
                                title_size=Pt(10), sub_size=Pt(8.2), title_bold=True)
                                
    # Operational Comparison Table
    s5_tbl_lbl = s5.shapes.add_textbox(Inches(0.50), Inches(3.70), Inches(6.15), Inches(0.28))
    tf = s5_tbl_lbl.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = "Operational Comparison: Manual Review vs ARGUS :"
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = C_PRIMARY_NAVY
    p.font.name = "Arial"
    
    tbl5 = s5.shapes.add_table(5, 3, Inches(0.50), Inches(4.00), Inches(6.15), Inches(1.70)).table
    tbl5.columns[0].width = Inches(1.75)
    tbl5.columns[1].width = Inches(2.20)
    tbl5.columns[2].width = Inches(2.20)
    
    t5_headers = ["Metric", "Manual Review", "ARGUS Engine"]
    for c_idx, h_text in enumerate(t5_headers):
        cell = tbl5.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_PRIMARY_NAVY
        tf = cell.text_frame
        tf.clear()
        p = tf.paragraphs[0]
        p.text = h_text
        p.font.bold = True
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_WHITE
        p.font.name = "Arial"
        
    t5_rows = [
        ("Execution Speed", "4 to 8 hours per release", "6.5 seconds end-to-end"),
        ("Route Coverage", "Sampled or inconsistent", "100% of 166 Edge routes"),
        ("Repeatability", "Subjective, operator-dependent", "Deterministic across runs"),
        ("Evidence Capture", "Manual notes and screenshots", "Evidence files with line numbers")
    ]
    for r_idx, row in enumerate(t5_rows):
        bg = C_WHITE if r_idx % 2 == 0 else C_BG_OFFWHITE
        for c_idx, val in enumerate(row):
            cell = tbl5.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            tf = cell.text_frame
            tf.clear()
            p = tf.paragraphs[0]
            p.text = val
            p.font.size = Pt(8.0)
            p.font.name = "Arial"
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_TEXT_DARK
            elif c_idx == 1:
                p.font.color.rgb = C_TEXT_MUTED
            else:
                p.font.bold = True
                p.font.color.rgb = C_EMERALD_GREEN
                
    # Monospace JSON snippet on bottom left
    add_clean_box(s5, Inches(0.50), Inches(5.80), Inches(6.15), Inches(0.85),
                  "findings.json (Schema Sample) :",
                  '{"id": "ARGUS-CONFIRMED-009", "cwe": "CWE-770", "severity": "High", "cvss_score": 7.5, "component": "api/_rate-limit.js", "evidence_paths": ["api/_rate-limit.js:52 catch block returns null"]}',
                  fill_col=C_BG_OFFWHITE, border_col=C_BORDER_LIGHT, border_width=Pt(1.0),
                  title_size=Pt(8.0), sub_size=Pt(7.0), align=PP_ALIGN.LEFT)
                  
    # Right Column: Native Charts (Severity Donut & CVSS Horizontal Bar)
    # Chart 1: Severity Donut
    cd5_donut = CategoryChartData()
    cd5_donut.categories = ['High (1)', 'Medium (11)']
    cd5_donut.add_series('Severity', (1, 11))
    chart_shape5a = s5.shapes.add_chart(XL_CHART_TYPE.DOUGHNUT, Inches(6.90), Inches(1.25), Inches(5.95), Inches(2.20), cd5_donut)
    c5a = chart_shape5a.chart
    c5a.has_legend = True
    c5a.legend.position = XL_LEGEND_POSITION.RIGHT
    c5a.legend.font.size = Pt(8.5)
    c5a.legend.font.name = "Arial"
    c5a.has_title = True
    c5a.chart_title.text_frame.text = "Only 1 of 12 findings reaches High severity (Source: findings.json)"
    c5a.chart_title.text_frame.paragraphs[0].font.size = Pt(9.0)
    c5a.chart_title.text_frame.paragraphs[0].font.bold = True
    c5a.chart_title.text_frame.paragraphs[0].font.color.rgb = C_PRIMARY_NAVY
    
    # Chart 4: Horizontal Bar Chart of CVSS Scores
    cd5_bar = CategoryChartData()
    cd5_bar.categories = [
        'Bot Filter (5.3)',
        'Trusted Types (6.1)',
        'SSRF Rebinding (6.3)',
        'Prompt Injection (6.5)',
        'UUID Bounds (6.5)',
        'Undici DoS (6.5)',
        'Stream-JSON DoS (6.5)',
        'NAT64 SSRF (6.5)',
        'IPv6 Link-Local (6.5)',
        'Image-Size DoS (6.5)',
        'Vitest Traversal (6.5)',
        'Fail-Open Rate Limit (7.5)'
    ]
    cd5_bar.add_series('CVSS 3.1', (5.3, 6.1, 6.3, 6.5, 6.5, 6.5, 6.5, 6.5, 6.5, 6.5, 6.5, 7.5))
    chart_shape5b = s5.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(6.90), Inches(3.60), Inches(5.95), Inches(3.05), cd5_bar)
    c5b = chart_shape5b.chart
    c5b.has_legend = False
    c5b.has_title = True
    c5b.chart_title.text_frame.text = "CVSS 3.1 Base Score per Finding (Accent on High Severity 7.5)"
    c5b.chart_title.text_frame.paragraphs[0].font.size = Pt(9.0)
    c5b.chart_title.text_frame.paragraphs[0].font.bold = True
    c5b.chart_title.text_frame.paragraphs[0].font.color.rgb = C_PRIMARY_NAVY
    
    # ==============================================================================
    # SLIDE 6: Research and References
    # ==============================================================================
    print("Refining Slide 6: Research and References...")
    s6 = prs.slides[5]
    
    # Update title
    for shape in list(s6.shapes)[:7]:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "RESEARCH AND REFERENCES" in p.text:
                    p.text = "Standards-aligned assessment grounded in established security frameworks"
                    p.font.bold = True
                    p.font.size = Pt(14)
                    p.font.color.rgb = C_PRIMARY_NAVY
                    p.font.name = "Arial"
                    
    # Clear content shapes (index >= 7)
    shapes_to_remove6 = [s._element for s in list(s6.shapes)[7:]]
    for elem in shapes_to_remove6:
        s6.shapes._spTree.remove(elem)
            
    # Left Column: Security Specifications and Standards
    add_clean_box(s6, Inches(0.50), Inches(1.25), Inches(6.00), Inches(3.80),
                  "SECURITY BENCHMARKS & TAXONOMIES",
                  "• OWASP Foundation. (2021). OWASP Top 10:2021 - The Ten Most Critical Web Application Security Risks. (Categories A03, A04, A07, A10).\n\n• OWASP GenAI Security Project. (2023). OWASP Top 10 for Large Language Model Applications. (Category LLM01: Prompt Injection).\n\n• MITRE Corporation. (2024). Common Weakness Enumeration. (CWE-20, CWE-79, CWE-269, CWE-770, CWE-918).\n\n• FIRST. (2019). Common Vulnerability Scoring System v3.1: Specification Document. Forum of Incident Response and Security Teams.",
                  fill_col=C_WHITE, border_col=C_PRIMARY_NAVY, border_width=Pt(1.2),
                  title_size=Pt(10.5), sub_size=Pt(8.5), title_bold=True)
                  
    # Right Column: Repository & Framework Documentation
    add_clean_box(s6, Inches(6.75), Inches(1.25), Inches(6.10), Inches(3.80),
                  "TARGET REPOSITORY & RUNTIME DOCUMENTATION",
                  "• World Monitor Project. (2026). SECURITY.md: Security Policy, Attack Surface, and Known Limitations. (Acknowledged SSRF rebinding residual).\n\n• National Vulnerability Database. (2026). NIST NVD Common Vulnerabilities and Exposures (CVE) Database.\n\n• Vercel Inc. (2025). Edge Runtime Specification and Fetch API Limitations.\n\n• Tauri Project. (2025). Tauri 2.0 Security Architecture and Inter-Process Communication (IPC).",
                  fill_col=C_WHITE, border_col=C_SLATE_TEAL, border_width=Pt(1.2),
                  title_size=Pt(10.5), sub_size=Pt(8.5), title_bold=True)
                  
    # Bottom Wide Banner: Strict Ethical Guardrails
    add_clean_box(s6, Inches(0.50), Inches(5.20), Inches(12.35), Inches(1.45),
                  "STRICT ETHICAL GUARDRAILS & RULES OF ENGAGEMENT",
                  "All security testing was executed strictly on an authorized, locally self-hosted sandbox instance (localhost:3000) using seeded test data. Zero active probing, scanning, or exploitation was conducted against production 'worldmonitor.app' or external upstream services. All 5 developed verification scripts are non-destructive and limited strictly to existence validation. Fully compliant with NTRO guidelines, Indian IT Act (Sections 43 and 66), and responsible vulnerability disclosure standards.",
                  fill_col=C_BG_OFFWHITE, border_col=C_EMERALD_GREEN, border_width=Pt(1.2),
                  title_size=Pt(10), sub_size=Pt(8.5), title_bold=True)
                  
    # Save the updated presentation
    out_file1 = 'SIH26163_ARGUS_Idea_PPT_Color.pptx'
    out_file2 = 'SIH26163_ARGUS_Idea_PPT.pptx'
    out_file3 = 'sources/SIH26163_ARGUS_Idea_PPT_Color.pptx'
    out_file4 = 'sources/SIH26163_ARGUS_Idea_PPT.pptx'
    
    prs.save(out_file1)
    prs.save(out_file2)
    prs.save(out_file3)
    prs.save(out_file4)
    print(f"Presentation saved successfully to {out_file1} and all mirrored locations!")

if __name__ == '__main__':
    create_deck()

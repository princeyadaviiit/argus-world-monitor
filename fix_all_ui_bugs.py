import os
import io
import pptx
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

def fix_all_ui_bugs():
    src_path = "sources/SIH26163_ARGUS_Idea_PPT_Color.pptx"
    out_path = "sources/SIH26163_ARGUS_Idea_PPT_Color.pptx"
    prs = pptx.Presentation(src_path)

    # Theme colors
    C_SIH_NAVY       = RGBColor(15, 23, 42)       # Deep Ashoka Navy (#0F172A)
    C_SIH_BLUE_HEAD  = RGBColor(30, 58, 138)      # Deep SIH Blue (#1E3A8A)
    C_SIH_COBALT     = RGBColor(37, 99, 235)      # Tech Accent Blue (#2563EB)
    C_SIH_SAFFRON    = RGBColor(234, 88, 12)      # SIH Saffron/Orange (#EA580C)
    
    # Light background tints
    C_SIH_LIGHT_BLUE = RGBColor(239, 246, 255)    # Soft SIH Ice Blue (#EFF6FF)
    C_SIH_LIGHT_SLATE= RGBColor(248, 250, 252)    # Clean Light Slate (#F8FAFC)
    C_WHITE          = RGBColor(255, 255, 255)    # Clean White
    
    # Borders
    C_BORDER_BLUE    = RGBColor(191, 219, 254)    # Soft Blue Border (#BFDBFE)
    C_BORDER_SLATE   = RGBColor(226, 232, 240)    # Soft Slate Border (#E2E8F0)
    C_BORDER_NAVY    = RGBColor(30, 58, 138)      # Prominent Navy Border (#1E3A8A)

    # Text Colors
    C_TEXT_DARK      = RGBColor(15, 23, 42)       # Slate 900 / Deep Navy (#0F172A)
    C_TEXT_MUTED     = RGBColor(71, 85, 105)      # Slate 600 (#475569)

    def set_shape_style(shape, fill_color, border_color=None, border_width=Pt(1)):
        if shape.shape_type != 13 and hasattr(shape, "fill"):
            try:
                shape.fill.solid()
                shape.fill.fore_color.rgb = fill_color
                if hasattr(shape, "line"):
                    if border_color:
                        shape.line.color.rgb = border_color
                        shape.line.width = border_width
                    else:
                        shape.line.fill.background()
            except Exception:
                pass

    def set_text(shape, text, font_size=Pt(10), bold=False, color=C_TEXT_DARK, align=None):
        if not shape.has_text_frame:
            return
        tf = shape.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.margin_left = Inches(0.04)
        tf.margin_right = Inches(0.04)
        tf.margin_top = Inches(0.02)
        tf.margin_bottom = Inches(0.02)
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            if align is not None:
                p.alignment = align
            run = p.add_run()
            run.text = line
            run.font.name = "Calibri"
            run.font.size = font_size
            run.font.bold = bold
            run.font.color.rgb = color

    # =========================================================================
    # SLIDE 2 FIXES: SCREENSHOT 1 & SCREENSHOT 2
    # =========================================================================
    s2 = prs.slides[1]

    # Fix Screenshot 2: Mismatched border on Innovation & Rigor cards (Shapes 32, 34, 36, 38)
    # Set all 4 cards to IDENTICAL subtle blue border and light slate fill
    for c_shape in [s2.shapes[32], s2.shapes[34], s2.shapes[36], s2.shapes[38]]:
        set_shape_style(c_shape, C_SIH_LIGHT_SLATE, C_BORDER_BLUE, Pt(1))

    # Fix Screenshot 1: Remove colliding progress bar shapes (shapes 46 to 61)
    # Note: we delete in reverse order to keep indices stable
    # Shapes 46 to 61 correspond to the 16 broken progress bar & colliding text boxes
    shapes_to_remove = [s2.shapes[i] for i in range(46, len(s2.shapes))]
    for shp in shapes_to_remove:
        s2.shapes._spTree.remove(shp._element)

    # Position Shape 45 (Title) cleanly
    s2.shapes[45].top = Inches(5.08)
    s2.shapes[45].left = Inches(0.5)
    s2.shapes[45].width = Inches(12.33)
    s2.shapes[45].height = Inches(0.3)
    set_text(s2.shapes[45], "Real Evidenced Vulnerabilities Identified in World Monitor (Audit of 166 Endpoints) :", font_size=Pt(11.5), bold=True, color=C_SIH_NAVY)

    # Add a clean, beautiful 5-row x 4-column Table at the bottom (zero collisions!)
    t_left = Inches(0.5)
    t_top = Inches(5.42)
    t_width = Inches(12.33)
    t_height = Inches(1.3)
    
    table_shape = s2.shapes.add_table(5, 4, t_left, t_top, t_width, t_height)
    tbl = table_shape.table
    
    # Set column widths
    tbl.columns[0].width = Inches(0.4)    # #
    tbl.columns[1].width = Inches(6.83)   # Vulnerability & Root Cause
    tbl.columns[2].width = Inches(2.5)    # OWASP / CWE
    tbl.columns[3].width = Inches(2.6)    # CVSS 3.1 & Status

    def set_cell(cell, text, bold=False, font_size=Pt(9.5), text_color=C_TEXT_DARK, bg_color=None, align=PP_ALIGN.LEFT):
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        p.alignment = align
        run = p.add_run()
        run.text = text
        run.font.name = "Calibri"
        run.font.size = font_size
        run.font.bold = bold
        run.font.color.rgb = text_color
        cell.margin_left = Inches(0.06)
        cell.margin_right = Inches(0.06)
        cell.margin_top = Inches(0.03)
        cell.margin_bottom = Inches(0.03)
        if bg_color:
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_color

    headers = ["#", "Confirmed Vulnerability & Affected Root Cause", "OWASP & CWE Taxonomy", "CVSS 3.1 & PoC Verification"]
    for c_idx, h_text in enumerate(headers):
        align = PP_ALIGN.CENTER if c_idx in [0, 2, 3] else PP_ALIGN.LEFT
        set_cell(tbl.cell(0, c_idx), h_text, bold=True, font_size=Pt(9.5), text_color=C_WHITE, bg_color=C_SIH_BLUE_HEAD, align=align)

    findings_data = [
        ("1", "Unmetered Resource DoS via Fail-Open Rate Limiter in api/_rate-limit.js (Redis timeout -> 'degraded' mode)", "OWASP A04 · CWE-770 (Resource Exhaustion)", "7.5 (High) · Confirmed PoC", C_SIH_SAFFRON),
        ("2", "DOM XSS via 357 Bypassed Trusted Types in src/utils/dom-utils.ts ('legacy migration' string bypass)", "OWASP A03 · CWE-79 (Cross-Site Scripting)", "6.1 (Med) · Confirmed PoC", C_SIH_BLUE_HEAD),
        ("3", "Indirect Prompt Injection Blocklist Bypass in server/_shared/llm-sanitize.js (RSS feed multilingual evasion)", "OWASP LLM01 · CWE-20 (Improper Input)", "6.5 (Med) · Confirmed PoC", C_SIH_BLUE_HEAD),
        ("4", "SSRF TOCTOU / DNS Rebinding Window in api/mcp-proxy.ts (Cloud metadata 169.254.169.254 reachability)", "OWASP A10 · CWE-918 (Server-Side Request Forgery)", "6.3 (Med) · Confirmed PoC", C_SIH_BLUE_HEAD),
    ]

    for r_idx, (num, vuln, cwe, status, stat_color) in enumerate(findings_data):
        row_bg = C_SIH_LIGHT_BLUE if (r_idx % 2 == 1) else C_WHITE
        set_cell(tbl.cell(r_idx + 1, 0), num, bold=True, font_size=Pt(9.5), text_color=C_SIH_BLUE_HEAD, bg_color=row_bg, align=PP_ALIGN.CENTER)
        set_cell(tbl.cell(r_idx + 1, 1), vuln, bold=True, font_size=Pt(9.5), text_color=C_TEXT_DARK, bg_color=row_bg, align=PP_ALIGN.LEFT)
        set_cell(tbl.cell(r_idx + 1, 2), cwe, bold=False, font_size=Pt(9.0), text_color=C_TEXT_MUTED, bg_color=row_bg, align=PP_ALIGN.CENTER)
        set_cell(tbl.cell(r_idx + 1, 3), status, bold=True, font_size=Pt(9.5), text_color=stat_color, bg_color=row_bg, align=PP_ALIGN.CENTER)

    # =========================================================================
    # SLIDE 3 FIXES: SCREENSHOT 3 (TEXT OVERFLOWING BOXES)
    # =========================================================================
    s3 = prs.slides[2]

    # Increase the height of the 4 top boxes from 1051560 to 1250000 EMU
    for b_idx in [8, 14, 20, 26]:
        s3.shapes[b_idx].height = Inches(1.36)
        set_shape_style(s3.shapes[b_idx], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    # Adjust text box heights and margins so text sits completely INSIDE the cards
    text_boxes_s3 = [
        (s3.shapes[12], "World Monitor (AGPL-3.0)\n• 166 Vercel Edge Endpoints\n• 5 Trust Boundaries Mapped"),
        (s3.shapes[18], "Automated Telemetry\n• Semgrep SAST (OWASP/CWE)\n• npm audit SCA (28 CVEs)"),
        (s3.shapes[24], "Python 3.14 + Pydantic v2\n• Unified Schema Normalization\n• FIRST CVSS 3.1 Vector Calc"),
        (s3.shapes[30], "Verified Audit Artifacts\n• 12-Page Executive PDF Report\n• SARIF 2.1.0 JSON & 5 PoCs"),
    ]
    for txt_shape, txt_content in text_boxes_s3:
        txt_shape.top = Inches(2.22)
        txt_shape.height = Inches(0.7)
        set_text(txt_shape, txt_content, font_size=Pt(9.5), bold=False, color=C_TEXT_DARK)

    # Move subtitle below top boxes down so it doesn't collide
    s3.shapes[31].top = Inches(3.05)
    s3.shapes[31].height = Inches(0.28)
    set_text(s3.shapes[31], "Multi-Engine Pipeline: Disparate scanner signals are ingested, normalized via Pydantic, cross-confirmed to eliminate false positives, and verified with non-destructive PoCs.", font_size=Pt(9.5), bold=False, color=C_TEXT_MUTED)

    # =========================================================================
    # SLIDE 4 COMPLETE REDESIGN: FLOWCHART + SIDE-BY-SIDE EXPLANATION BOXES
    # =========================================================================
    s4 = prs.slides[3]

    # Remove old shapes 7 to 57
    shapes_to_remove_s4 = [s4.shapes[i] for i in range(7, len(s4.shapes))]
    for shp in shapes_to_remove_s4:
        s4.shapes._spTree.remove(shp._element)

    # 1. Left Section Header: Flowchart
    fc_title = s4.shapes.add_textbox(Inches(0.5), Inches(1.22), Inches(5.2), Inches(0.35))
    set_text(fc_title, "Feasibility & Operational Execution Flow :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)

    # 2. Right Section Header: Explanation Boxes
    exp_title = s4.shapes.add_textbox(Inches(5.95), Inches(1.22), Inches(6.8), Inches(0.35))
    set_text(exp_title, "Feasibility & Viability Analysis (Detailed Assessment) :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)

    # 3. Left Side: 5 Vertical Flowchart Step Boxes + Connecting Arrows
    flow_steps = [
        ("1. Target Sandbox Isolation", "• AGPL-3.0 self-hosted World Monitor instance (localhost:3000)\n• 100% isolated local execution; zero upstream cloud dependencies"),
        ("2. Multi-Engine Surface Recon", "• AST route parsing across 166 Vercel Edge routes (137 public, 29 Pro)\n• Semgrep SAST rulesets + npm audit dependency CVE correlation"),
        ("3. Correlation & Two-Signal Gate", "• Pydantic v2 unified schema; automated deduplication\n• Discards unverified scanner noise, cutting 80% triage overhead"),
        ("4. Safe Non-Destructive PoC", "• 5 automated Python / Playwright verification harnesses\n• Local mock testbeds for rate limits & prompt injection (100% pass)"),
        ("5. Hardened Fixes & Delivery", "• Production code diffs (DOMPurify, fail-closed, socket pinning)\n• Automated 12-page executive PDF & SARIF report generation"),
    ]

    fc_top_start = Inches(1.65)
    fc_box_h = Inches(0.82)
    fc_gap = Inches(0.18)
    fc_left = Inches(0.5)
    fc_width = Inches(5.15)

    for idx, (step_head, step_desc) in enumerate(flow_steps):
        cur_top = fc_top_start + idx * (fc_box_h + fc_gap)
        
        # Box shape
        box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, fc_left, cur_top, fc_width, fc_box_h)
        set_shape_style(box, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
        
        # Text inside box
        tf = box.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.margin_left = Inches(0.12)
        tf.margin_right = Inches(0.1)
        tf.margin_top = Inches(0.06)
        tf.margin_bottom = Inches(0.06)
        
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = step_head
        r1.font.name = "Calibri"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = C_SIH_BLUE_HEAD
        
        for line in step_desc.split("\n"):
            p = tf.add_paragraph()
            r = p.add_run()
            r.text = line
            r.font.name = "Calibri"
            r.font.size = Pt(9.0)
            r.font.bold = False
            r.font.color.rgb = C_TEXT_DARK

        # Down arrow between boxes
        if idx < 4:
            arr_top = cur_top + fc_box_h + Inches(0.02)
            arrow = s4.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, fc_left + fc_width / 2 - Inches(0.08), arr_top, Inches(0.16), Inches(0.14))
            set_shape_style(arrow, C_SIH_BLUE_HEAD, None)

    # 4. Right Side: 4 Detailed Explanation Boxes
    exp_boxes = [
        ("Technical Feasibility & Target Access (White-Box Codebase)",
         [("• Open-Source Architecture: Full white-box access to Next.js, Vite, and Tauri 2.0 Rust codebase eliminates reverse-engineering friction.", False),
          ("• Local Sandboxing: Endpoints execute without requiring external cloud accounts (Upstash Redis or Clerk), ensuring 100% repeatable testing.", False)]),

        ("Operational & Economic Viability ($0 Tooling Expenditure)",
         [("• Zero License Fees: Powered entirely by open-source tools (Semgrep, Python 3.14, Playwright, ReportLab), saving thousands in commercial pentest costs.", False),
          ("• Turnkey Reproducibility: Automated single-command CLI execution reproduces the complete end-to-end audit in under 60 seconds.", False)]),

        ("Challenge & Risk Mitigation Strategy (Noise Elimination)",
         [("• Alert Fatigue Suppression: Two-signal cross-confirmation gate ensures zero false positives reach the Proof-of-Concept verification phase.", False),
          ("• Non-Destructive Integrity: Rate-limiting and prompt injection tests run against local mock harnesses with zero impact on production data.", False)]),

        ("Strategic Impact & Government Scalability (NTRO Sovereign Mission)",
         [("• Sovereign Mission Alignment: Directly empowers NTRO with a reusable audit framework for national security OSINT tools and border telemetry.", False),
          ("• Multi-Target Reusability: Declarative YAML target profiles enable the correlation engine to audit any web application or microservice.", False)]),
    ]

    exp_top_start = Inches(1.65)
    exp_box_h = Inches(1.08)
    exp_gap = Inches(0.17)
    exp_left = Inches(5.95)
    exp_width = Inches(6.85)

    for idx, (head_text, bullets) in enumerate(exp_boxes):
        cur_top = exp_top_start + idx * (exp_box_h + exp_gap)
        
        # Box shape
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, exp_left, cur_top, exp_width, exp_box_h)
        set_shape_style(card, C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))
        
        # Text inside box
        tf = card.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.margin_left = Inches(0.14)
        tf.margin_right = Inches(0.12)
        tf.margin_top = Inches(0.06)
        tf.margin_bottom = Inches(0.06)
        
        # Header
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = head_text
        r1.font.name = "Calibri"
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = C_SIH_NAVY
        
        # Bullets
        for b_text, is_bld in bullets:
            p = tf.add_paragraph()
            r = p.add_run()
            r.text = b_text
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.font.bold = is_bld
            r.font.color.rgb = C_TEXT_DARK

    # Update Slide 4 Speaker Notes
    s4.notes_slide.notes_text_frame.text = (
        "[2:45 - 3:30 | 45s Pitch - Slide 4: Feasibility Flowchart & Viability Analysis]\n"
        "On Slide 4, we demonstrate our Feasibility and Operational Viability through an engineered execution flowchart on the left and a detailed capability assessment on the right.\n\n"
        "As traced in our 5-step flowchart, ARGUS achieves 100% feasibility because all 166 endpoints and 5 trust boundaries run locally within an isolated AGPL-3.0 sandbox—zero external cloud subscriptions or network dependencies are required.\n\n"
        "On the right, we address the core viability pillars:\n"
        "1. Technical Feasibility: White-box AST extraction directly uncovers edge route signatures.\n"
        "2. Economic Viability: Built with 100% open-source software (Semgrep, Python, Playwright), achieving complete automation at zero license cost.\n"
        "3. Risk Mitigation: Our Two-Signal confirmation gate discards scanner noise before PoC development, and non-destructive mock testbeds protect upstream APIs.\n"
        "4. Strategic Scalability: Built for NTRO to audit sovereign OSINT and government web assets simply by updating target YAML profiles."
    )

    prs.save(out_path)
    prs.save("SIH26163_ARGUS_Idea_PPT_Color.pptx")
    print(f"All UI bug fixes and Slide 4 redesign complete! Saved to '{out_path}' and 'SIH26163_ARGUS_Idea_PPT_Color.pptx'")

if __name__ == "__main__":
    fix_all_ui_bugs()

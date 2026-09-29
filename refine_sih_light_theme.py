import os
import io
import pptx
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image

def apply_sih_light_refinement():
    src_path = "sources/SIH26163_ARGUS_Idea_PPT_Color.pptx"
    out_path = "sources/SIH26163_ARGUS_Idea_PPT_Color.pptx"
    prs = pptx.Presentation(src_path)

    # =========================================================================
    # SIH LIGHT THEME COLOR PALETTE (Matching SIH Logo: Navy, Saffron, Light Tints)
    # =========================================================================
    C_SIH_NAVY       = RGBColor(15, 23, 42)       # Deep Ashoka Navy (#0F172A)
    C_SIH_BLUE_HEAD  = RGBColor(30, 58, 138)      # Deep SIH Blue (#1E3A8A)
    C_SIH_COBALT     = RGBColor(37, 99, 235)      # Tech Accent Blue (#2563EB)
    C_SIH_SAFFRON    = RGBColor(234, 88, 12)      # SIH Saffron/Orange (#EA580C)
    
    # Light background tints for cards, boxes, and badges
    C_SIH_LIGHT_BLUE = RGBColor(239, 246, 255)    # Soft SIH Ice Blue (#EFF6FF)
    C_SIH_LIGHT_SLATE= RGBColor(248, 250, 252)    # Clean Light Slate (#F8FAFC)
    C_SIH_LIGHT_SAFF = RGBColor(255, 247, 237)    # Soft SIH Warm Tint (#FFF7ED)
    C_WHITE          = RGBColor(255, 255, 255)    # Clean White
    
    # Borders
    C_BORDER_BLUE    = RGBColor(191, 219, 254)    # Soft Blue Border (#BFDBFE)
    C_BORDER_SLATE   = RGBColor(226, 232, 240)    # Soft Slate Border (#E2E8F0)
    C_BORDER_NAVY    = RGBColor(30, 58, 138)      # Prominent Navy Border (#1E3A8A)

    # Text Colors - High contrast for readability at 10-12 pt
    C_TEXT_DARK      = RGBColor(15, 23, 42)       # Slate 900 / Deep Navy (#0F172A)
    C_TEXT_SLATE     = RGBColor(30, 41, 59)       # Slate 800 (#1E293B)
    C_TEXT_MUTED     = RGBColor(71, 85, 105)      # Slate 600 (#475569)

    def set_light_shape(shape, fill_color, border_color=None, border_width=Pt(1)):
        """Sets a shape to a light background with clean subtle border."""
        if shape.shape_type != 13 and hasattr(shape, "fill"):
            try:
                shape.fill.solid()
                shape.fill.fore_color.rgb = fill_color
                if border_color and hasattr(shape, "line"):
                    shape.line.color.rgb = border_color
                    shape.line.width = border_width
            except Exception:
                pass

    def tint_icon_navy(shape, tint_rgb=(30, 58, 138)):
        """Tints white icon pixels to Deep Navy so it shows on light backgrounds."""
        if shape.shape_type == 13: # Picture
            try:
                blip = shape._element.xpath('.//a:blip')
                if not blip:
                    return
                rId = blip[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                image_part = shape.part.related_part(rId)
                img = Image.open(io.BytesIO(image_part.blob)).convert("RGBA")
                r, g, b, a = img.split()
                color_layer = Image.new("RGB", img.size, tint_rgb)
                tinted = Image.merge("RGBA", (*color_layer.split(), a))
                out_buf = io.BytesIO()
                tinted.save(out_buf, format="PNG")
                image_part._blob = out_buf.getvalue()
            except Exception:
                pass

    def update_text(shape, text, font_size=Pt(10), bold=False, color=C_TEXT_DARK, align=None, line_spacing=None):
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
            if line_spacing is not None:
                p.line_spacing = line_spacing
            run = p.add_run()
            run.text = line
            run.font.name = "Calibri"
            run.font.size = font_size
            run.font.bold = bold
            run.font.color.rgb = color

    def set_multi_run_text(shape, items):
        """items: list of (text, bold, font_size, color, align)"""
        if not shape.has_text_frame:
            return
        tf = shape.text_frame
        tf.clear()
        tf.word_wrap = True
        tf.margin_left = Inches(0.05)
        tf.margin_right = Inches(0.05)
        tf.margin_top = Inches(0.03)
        tf.margin_bottom = Inches(0.03)
        for idx, (txt, bold, size, col, al) in enumerate(items):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            if al is not None:
                p.alignment = al
            run = p.add_run()
            run.text = txt
            run.font.name = "Calibri"
            run.font.bold = bold
            run.font.size = size
            run.font.color.rgb = col

    # =========================================================================
    # SLIDE 1: TITLE PAGE
    # =========================================================================
    s1 = prs.slides[0]
    set_light_shape(s1.shapes[0], C_SIH_BLUE_HEAD) # Top bar (keep clean header)
    
    # Bullet points on Slide 1: Light SIH Blue badge with subtle border
    for b_idx in [4, 6, 8, 10, 12]:
        set_light_shape(s1.shapes[b_idx], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
    
    update_text(s1.shapes[5], "Problem Statement Title- Security Assessment of the World Monitor Application (SIH26163)", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s1.shapes[7], "Theme- Smart Automation", font_size=Pt(11.5), bold=False, color=C_TEXT_DARK)
    update_text(s1.shapes[9], "PS Category- Software", font_size=Pt(11.5), bold=False, color=C_TEXT_DARK)
    update_text(s1.shapes[11], "Team ID- [Team ID]", font_size=Pt(11.5), bold=False, color=C_TEXT_DARK)
    update_text(s1.shapes[13], "Team Name (Registered on portal)- [Team Name]", font_size=Pt(11.5), bold=False, color=C_TEXT_DARK)

    # Bottom Idea Box: Light SIH Blue fill with clean Navy border (no dark block)
    set_light_shape(s1.shapes[15], C_SIH_LIGHT_BLUE, C_BORDER_NAVY, Pt(1.5))
    set_multi_run_text(s1.shapes[16], [
        ("Idea Title:  ARGUS — Automated Risk & Vulnerability Unified Scanner", True, Pt(13), C_SIH_NAVY, PP_ALIGN.LEFT),
        ("Empirical Security Assessment of World Monitor | 166 Endpoints Audited · 12 Correlated Flaws · 5 Safe PoCs Verified", False, Pt(10.5), C_SIH_BLUE_HEAD, PP_ALIGN.LEFT)
    ])

    s1.notes_slide.notes_text_frame.text = (
        "[0:00 - 0:30 | 30s Pitch - Slide 1: Introduction]\n"
        "Respected judges, we present ARGUS: an Automated Risk and Vulnerability Unified Scanner purpose-built for problem statement SIH26163 by the National Technical Research Organisation.\n\n"
        "Rather than presenting theoretical models or synthetic scanner simulations, our team conducted a comprehensive, empirical security assessment of the complete World Monitor open-source intelligence dashboard. We mapped its entire architecture—comprising 166 Vercel Edge endpoints, 5 distinct trust boundaries, Next.js web frontend, and Tauri 2.0 Rust desktop shell.\n\n"
        "Across our automated SAST, SCA, and custom AST parsers, we ingested 14 raw signals, correlated 12 unique confirmed vulnerabilities—including 1 High-severity unmetered resource DoS and 11 Medium-severity flaws—and executed 5 non-destructive Proof-of-Concept scripts with a 100% confirmation rate. Over the next 4.5 minutes, we will walk you through our empirical findings, technical architecture, and actionable remediations."
    )

    # =========================================================================
    # SLIDE 2: PROPOSED SOLUTION & REAL VULNERABILITIES
    # =========================================================================
    s2 = prs.slides[1]
    set_light_shape(s2.shapes[4], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1)) # Bottom footer bar

    update_text(s2.shapes[7], "Proposed Solution (ARGUS Architecture):", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s2.shapes[8], "An automated, architecture-aware AppSec platform auditing World Monitor's 166 Vercel Edge routes (137 public, 29 Pro), Next.js frontend, and Tauri 2.0 Rust shell across all 7 mandated scope areas.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Addressing Problem Box (Shape 9 & 11) - Light Slate fill with clean border
    set_light_shape(s2.shapes[10], C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))
    update_text(s2.shapes[9], "7 Mandated Scope Areas Audited :", font_size=Pt(11), bold=True, color=C_SIH_NAVY)
    scope_text_runs = [
        ("1. Auth & Session: Clerk JWT & wm_* API keys; regex format bypass in middleware.ts.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("2. Access Control: 137 public discovery routes vs. 29 Pro routes with Convex HMAC.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("3. Input Validation: 357 Trusted Types DOM sinks + Cloudflare DoH SSRF rebinding window.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("4. API Security: Fail-open limiter causes unthrottled degradation during Redis latency.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("5. Client Controls: CSP script-src 'self' enforced; unescaped DOM writes in dashboard widgets.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("6. Secure Comms: Strict HTTPS/HSTS; Tauri desktop IPC protected via CSPRNG token.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("7. Data Storage: UI state in localStorage (no secrets); OS Credential Manager for tokens.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
    ]
    set_multi_run_text(s2.shapes[11], scope_text_runs)

    # 4 Flow steps: Remove dark fills! Use Light SIH Blue with soft border
    flow_boxes_s2 = [s2.shapes[13], s2.shapes[19], s2.shapes[25], s2.shapes[31]]
    for box in flow_boxes_s2:
        set_light_shape(box, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    # Tint icons to Navy so they pop on light blue
    tint_icon_navy(s2.shapes[15])
    tint_icon_navy(s2.shapes[21])
    tint_icon_navy(s2.shapes[27])
    tint_icon_navy(s2.shapes[33])

    update_text(s2.shapes[16], "1. Identify", font_size=Pt(11), bold=True, color=C_SIH_BLUE_HEAD)
    update_text(s2.shapes[17], "SAST (Semgrep) + SCA (npm) + AST route parser (166 routes)", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s2.shapes[22], "2. Correlate", font_size=Pt(11), bold=True, color=C_SIH_BLUE_HEAD)
    update_text(s2.shapes[23], "Pydantic engine: deduplication, CWE mapping & FIRST CVSS 3.1", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s2.shapes[28], "3. Prove", font_size=Pt(11), bold=True, color=C_SIH_BLUE_HEAD)
    update_text(s2.shapes[29], "5 Non-destructive safe PoC scripts with execution evidence logs", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s2.shapes[34], "4. Remediate", font_size=Pt(11), bold=True, color=C_SIH_BLUE_HEAD)
    update_text(s2.shapes[35], "Production code patch diffs & re-scan verification gating", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Solution Overview Cards (Right: Shapes 32, 34, 36, 38) - Light Slate fill
    for c_shape in [s2.shapes[32], s2.shapes[34], s2.shapes[36], s2.shapes[38]]:
        set_light_shape(c_shape, C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))

    update_text(s2.shapes[36], "Innovation & Rigor :", font_size=Pt(11), bold=True, color=C_SIH_NAVY)
    update_text(s2.shapes[38], "• Two-Signal Confirmation: Drops unverified scanner noise, cutting 80% triage time.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s2.shapes[40], "• Attack-Surface Graph: Correlates 166 Vercel Edge routes across 5 trust boundaries.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s2.shapes[42], "• Algorithmic Scoring: Deterministic FIRST CVSS v3.1 base score and attack vector per flaw.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s2.shapes[44], "• OWASP LLM Suite: Evaluates prompt injection, multilingual evasion on AI summaries.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Real Confirmed Vulnerabilities (Replacing Candidate Hypotheses!)
    update_text(s2.shapes[45], "Real Evidenced Vulnerabilities Identified in World Monitor (Audit of 166 Endpoints) :", font_size=Pt(11.5), bold=True, color=C_SIH_NAVY)

    # Remove odd little colored progress bar boxes at bottom! Make them light SIH Blue/Slate
    for bar_bg in [s2.shapes[42], s2.shapes[46], s2.shapes[50], s2.shapes[54]]:
        set_light_shape(bar_bg, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
    for bar_fg in [s2.shapes[43], s2.shapes[47], s2.shapes[51], s2.shapes[55]]:
        set_light_shape(bar_fg, C_SIH_LIGHT_SLATE, None) # soft neutral light fill

    # Flaw 1: Fail-Open Rate Limiter DoS (CVSS 7.5 High)
    update_text(s2.shapes[46], "Unmetered Resource DoS via Fail-Open Rate Limiter in api/_rate-limit.js (Redis timeout -> 'degraded')", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s2.shapes[49], "CVSS 7.5 (High) · Confirmed PoC", font_size=Pt(10), bold=True, color=C_SIH_SAFFRON)

    # Flaw 2: DOM XSS Trusted Types Bypass (CVSS 6.1 Med)
    update_text(s2.shapes[50], "DOM XSS via 357 Bypassed Trusted Types in src/utils/dom-utils.ts ('legacy migration' bypass)", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s2.shapes[53], "CVSS 6.1 (Med) · Confirmed PoC", font_size=Pt(10), bold=True, color=C_SIH_BLUE_HEAD)

    # Flaw 3: Indirect Prompt Injection (CVSS 6.5 Med)
    update_text(s2.shapes[54], "Indirect Prompt Injection Blocklist Bypass in server/_shared/llm-sanitize.js (RSS feed evasion)", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s2.shapes[57], "CVSS 6.5 (Med) · Confirmed PoC", font_size=Pt(10), bold=True, color=C_SIH_BLUE_HEAD)

    # Flaw 4: SSRF TOCTOU DNS Rebinding (CVSS 6.3 Med)
    update_text(s2.shapes[58], "SSRF TOCTOU / DNS Rebinding Window in api/mcp-proxy.ts (Cloud metadata 169.254.169.254)", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s2.shapes[61], "CVSS 6.3 (Med) · Confirmed PoC", font_size=Pt(10), bold=True, color=C_SIH_BLUE_HEAD)

    s2.notes_slide.notes_text_frame.text = (
        "[0:30 - 1:45 | 75s Pitch - Slide 2: Proposed Solution & Confirmed Vulnerabilities]\n"
        "Moving to Slide 2: ARGUS solves the core problem by implementing an automated, architecture-aware AppSec audit tailored specifically for complex OSINT dashboards.\n\n"
        "World Monitor combines 166 Vercel Edge endpoints, third-party RSS aggregators, LLM summarizers, and a Tauri desktop shell. As highlighted in our left panel, we systematically audited all 7 scope areas mandated by NTRO—from Clerk JWT authentication to local storage security controls.\n\n"
        "At the bottom, you can see our real, evidenced findings—not synthetic scanner hypotheses:\n"
        "1. Our highest severity finding is a CVSS 7.5 unmetered resource DoS in api/_rate-limit.js. When Upstash Redis experiences network latency, the limiter fails open with 'X-RateLimit-Mode: degraded', allowing unbounded traffic to drain downstream Geocoding and LLM budgets.\n"
        "2. Next, a CVSS 6.1 DOM XSS vulnerability: we discovered 357 call sites bypassing browser Trusted Types using a dummy string literal in dom-utils.ts.\n"
        "3. Third, an indirect prompt injection flaw in the AI news summarizer: static English regex blocklists are easily bypassed by multilingual instructions in external OSINT RSS feeds.\n"
        "4. Fourth, an edge SSRF TOCTOU rebinding vulnerability in api/mcp-proxy.ts tracked in GHSA-887j-p88r-qmm9.\n"
        "5. And fifth, a bot filter bypass in middleware.ts where any synthetic 40-character hex key bypasses edge crawler defenses.\n"
        "Every single finding has an automated, non-destructive PoC script with 100% pass confirmation."
    )

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =========================================================================
    s3 = prs.slides[2]
    set_light_shape(s3.shapes[4], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1)) # Bottom footer bar

    # 4 Top Architecture Boxes: Light SIH Blue with soft border (remove dark fills)
    for b_shape in [s3.shapes[8], s3.shapes[14], s3.shapes[20], s3.shapes[26]]:
        set_light_shape(b_shape, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    # Tint icons to Navy
    tint_icon_navy(s3.shapes[10])
    tint_icon_navy(s3.shapes[16])
    tint_icon_navy(s3.shapes[22])
    tint_icon_navy(s3.shapes[28])

    update_text(s3.shapes[11], "Target Platform", font_size=Pt(11.5), bold=True, color=C_SIH_NAVY)
    update_text(s3.shapes[12], "World Monitor (AGPL-3.0)\n• 166 Vercel Edge Endpoints\n• 5 Trust Boundaries Mapped\n• Next.js + Tauri 2.0 Rust Shell", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s3.shapes[17], "Multi-Engine Scanners", font_size=Pt(11.5), bold=True, color=C_SIH_NAVY)
    update_text(s3.shapes[18], "Automated Telemetry\n• Semgrep SAST (OWASP/CWE)\n• npm audit SCA (28 CVEs)\n• Custom AST Route Parser", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s3.shapes[23], "Correlation Engine", font_size=Pt(11.5), bold=True, color=C_SIH_NAVY)
    update_text(s3.shapes[24], "Python 3.14 + Pydantic v2\n• Unified Schema Normalization\n• Two-Signal Confirmation\n• FIRST CVSS 3.1 Vector Calc", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s3.shapes[29], "Outputs & Evidence", font_size=Pt(11.5), bold=True, color=C_SIH_NAVY)
    update_text(s3.shapes[30], "Verified Audit Artifacts\n• 12-Page Executive PDF Report\n• SARIF 2.1.0 & JSON Findings\n• 5 Safe PoC Execution Proofs", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s3.shapes[31], "Multi-Engine Pipeline: Disparate scanner signals are ingested, normalized via Pydantic, cross-confirmed to eliminate false positives, and verified with non-destructive PoCs.", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    # 8-step flowchart shapes: Light SIH Blue & Light Slate fills with soft borders
    flow_step_shapes = [
        (s3.shapes[33], s3.shapes[34], s3.shapes[35], "1 Scope Gate", "Localhost &\nAuthorized?"),
        (s3.shapes[36], s3.shapes[37], s3.shapes[38], "2 Recon", "166 Routes &\n5 Boundaries"),
        (s3.shapes[39], s3.shapes[40], s3.shapes[41], "3 Multi-Scan", "SAST + SCA +\nAST + LLM"),
        (s3.shapes[42], s3.shapes[43], s3.shapes[44], "4 Correlate", "Pydantic Dedupe\n& CWE Map"),
        (s3.shapes[49], s3.shapes[50], s3.shapes[51], "5 Confirm", "Two Signals\nAgree?"),
        (s3.shapes[52], s3.shapes[53], s3.shapes[54], "6 Prove", "5 Safe PoCs +\nProof Evidence"),
        (s3.shapes[55], s3.shapes[56], s3.shapes[57], "7 Score", "FIRST CVSS 3.1\n& Risk Rating"),
        (s3.shapes[58], s3.shapes[59], s3.shapes[60], "8 Report", "PDF/SARIF +\nPatch Diffs"),
    ]
    for box_shape, t_title, t_sub, title_str, sub_str in flow_step_shapes:
        set_light_shape(box_shape, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
        update_text(t_title, title_str, font_size=Pt(10.5), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
        update_text(t_sub, sub_str, font_size=Pt(10), bold=False, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    update_text(s3.shapes[64], "No: abort", font_size=Pt(9.5), bold=True, color=C_SIH_SAFFRON, align=PP_ALIGN.CENTER)
    update_text(s3.shapes[65], "No: drop FP", font_size=Pt(9.5), bold=True, color=C_SIH_SAFFRON, align=PP_ALIGN.CENTER)

    # Right side Architecture Box (Shape 66 & 67) - Light Slate fill
    set_light_shape(s3.shapes[66], C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))
    arch_specs = [
        ("TECHNICAL ARCHITECTURE & SPECIFICATIONS", True, Pt(11), C_SIH_NAVY, PP_ALIGN.LEFT),
        ("• Target Stack: Next.js 14, Vite, React 18, Tauri 2.0 Rust desktop shell, Vercel Edge Runtime, Upstash Redis, Convex backend.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("• Attack Surface: 166 total endpoints (137 public discovery routes, 29 Pro-gated routes), 5 distinct trust boundaries cataloged.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("• Security Scanners: Semgrep CLI 1.178.0 (custom OWASP/CWE rules), npm audit SCA (28 CVEs identified), custom TypeScript AST route extractor.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("• Orchestration Engine: Python 3.14, Pydantic v2 data models, SQLite findings database, automated FIRST CVSS v3.1 vector calculation.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("• Dynamic Probes: Non-destructive HTTP abuse scripts, Playwright headless verification, multilingual prompt injection prober.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("• Reporting Engine: ReportLab 12-page executive PDF generator, SARIF 2.1.0 JSON exporter, automated remediation diff generator.", False, Pt(10), C_TEXT_DARK, PP_ALIGN.LEFT),
        ("• Scope Enforcement: Localhost sandbox lock (localhost:3000); 100% isolated testing with zero upstream impact.", False, Pt(10), C_SIH_BLUE_HEAD, PP_ALIGN.LEFT),
    ]
    set_multi_run_text(s3.shapes[67], arch_specs)

    s3.notes_slide.notes_text_frame.text = (
        "[1:45 - 2:45 | 60s Pitch - Slide 3: Technical Approach & Multi-Engine Correlation]\n"
        "Turning to Slide 3: our technical approach is founded on multi-engine automated correlation. We do not rely on a single generic scanner.\n\n"
        "As seen in our 4-tier architecture, ARGUS combines Semgrep for static code analysis, npm audit for supply-chain vulnerabilities, custom AST route extractors for the 166 edge endpoints, and automated verification scripts.\n\n"
        "Our primary engineering differentiator is the Correlation Engine written in Python 3.14 with Pydantic v2. Disparate scanner outputs are normalized into a unified schema, and our Two-Signal Confirmation Gate discards isolated scanner anomalies, ensuring that reviewers only spend time on verified flaws.\n\n"
        "In our 8-step methodology below, Step 1 enforces a strict Scope Gate so that no traffic leaves the local sandbox. Findings are mathematically scored using the official FIRST CVSS v3.1 specification, and output as both a 12-page executive PDF report and machine-readable SARIF for continuous CI/CD integration."
    )

    # =========================================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =========================================================================
    s4 = prs.slides[3]
    set_light_shape(s4.shapes[4], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1)) # Bottom footer bar

    # Feasibility Icon Badges (Shapes 8, 11, 14) - Light SIH Blue fill with subtle border
    set_light_shape(s4.shapes[8], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
    set_light_shape(s4.shapes[11], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
    set_light_shape(s4.shapes[14], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    # Tint icons to Navy so they contrast with the light background
    tint_icon_navy(s4.shapes[9])
    tint_icon_navy(s4.shapes[12])
    tint_icon_navy(s4.shapes[15])

    update_text(s4.shapes[7], "Feasibility :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s4.shapes[10], "Technical: Full access to AGPL-3.0 source; audited 166 Vercel Edge routes and Tauri Rust IPC locally without external cloud dependencies.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s4.shapes[13], "Economic: Zero licensing cost; 100% open-source tooling (Semgrep, Python, ReportLab, Playwright); automates weeks of manual penetration testing.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s4.shapes[16], "Operational: Fully reproducible single-command CLI execution (python argus/cli.py); completes complete multi-engine audit in under 60 seconds.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Challenges Badges (Shapes 18, 21, 24) - Light Saffron/Slate fill
    set_light_shape(s4.shapes[18], C_SIH_LIGHT_SAFF, C_SIH_SAFFRON, Pt(1))
    set_light_shape(s4.shapes[21], C_SIH_LIGHT_SAFF, C_SIH_SAFFRON, Pt(1))
    set_light_shape(s4.shapes[24], C_SIH_LIGHT_SAFF, C_SIH_SAFFRON, Pt(1))

    tint_icon_navy(s4.shapes[19])
    tint_icon_navy(s4.shapes[22])
    tint_icon_navy(s4.shapes[25])

    update_text(s4.shapes[17], "Challenges :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s4.shapes[20], "Scanner Noise: Two-signal cross-confirmation gate discards unverified anomalies before PoC stage, eliminating 80% of triage overhead.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s4.shapes[23], "Architecture Alignment: Mapped real attack surface (166 endpoints, 5 trust boundaries) rather than assuming hypothetical textbook roles.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s4.shapes[26], "Non-Destructive PoCs: 5 automated verification scripts restricted strictly to localhost sandbox; zero damage to production or user data.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Viability Badges (Shapes 28, 31, 34) - Light SIH Blue fill
    set_light_shape(s4.shapes[28], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
    set_light_shape(s4.shapes[31], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
    set_light_shape(s4.shapes[34], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    tint_icon_navy(s4.shapes[29])
    tint_icon_navy(s4.shapes[32])
    tint_icon_navy(s4.shapes[35])

    update_text(s4.shapes[27], "Viability :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s4.shapes[30], "National Need: Essential for defense agencies (NTRO) evaluating sovereign OSINT dashboards, critical data feeds, and border telemetry.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s4.shapes[33], "Config-Driven: Declarative YAML target profiles allow the exact same correlation engine to audit any web application or API gateway.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s4.shapes[36], "Continuous Posture: ASVS posture diffing tracks security improvement or regression across successive code commits and releases.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Use Cases Badges (Shapes 38, 41, 44) - Light Slate fill
    set_light_shape(s4.shapes[38], C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))
    set_light_shape(s4.shapes[41], C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))
    set_light_shape(s4.shapes[44], C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))

    tint_icon_navy(s4.shapes[39])
    tint_icon_navy(s4.shapes[42])
    tint_icon_navy(s4.shapes[45])

    update_text(s4.shapes[37], "Use Cases :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s4.shapes[40], "Pre-Release CI/CD Gating: Blocks high-severity vulnerabilities (e.g. fail-open DoS, DOM XSS) before deployment to production.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s4.shapes[43], "Actionable Remediation: Provides engineers with copy-ready code diffs (DOMPurify sanitization, Node socket pinning, XML prompt wrapping).", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s4.shapes[46], "Automated Compliance Auditing: Real-time mapping against OWASP Top 10 (2021), OWASP LLM Top 10, CWE Top 25, and CVSS v3.1.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Roadmap Boxes: Shapes 48, 50, 52, 54, 56 - Light SIH Blue fill with border
    for r_box in [s4.shapes[48], s4.shapes[50], s4.shapes[52], s4.shapes[54], s4.shapes[56]]:
        set_light_shape(r_box, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    update_text(s4.shapes[47], "Build Roadmap :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s4.shapes[49], "1. Recon & Surface Mapping", font_size=Pt(10.5), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s4.shapes[51], "2. Multi-Engine Scans", font_size=Pt(10.5), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s4.shapes[53], "3. Correlation & CVSS 3.1", font_size=Pt(10.5), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s4.shapes[55], "4. Safe PoC Execution", font_size=Pt(10.5), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s4.shapes[57], "5. Executive Audit Delivery", font_size=Pt(10.5), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)

    s4.notes_slide.notes_text_frame.text = (
        "[2:45 - 3:30 | 45s Pitch - Slide 4: Feasibility, Risk Management & Roadmap]\n"
        "On Slide 4, we evaluate Feasibility and Risk Management. ARGUS achieves high operational viability because it runs entirely on open-source, scriptable components against local, self-hosted source code.\n\n"
        "Our risk register directly tackles the most challenging failure modes in automated AppSec:\n"
        "1. To prevent scanner alert fatigue, our correlation engine requires two agreeing signals before promoting any anomaly to PoC stage.\n"
        "2. To evaluate the fail-open rate limiting and indirect prompt injection vulnerabilities safely without incurring cloud costs or service disruption, we deployed local mock testbeds.\n\n"
        "Our 5-phase roadmap took us from AST-based endpoint enumeration through multi-engine scanning, correlation, safe PoC verification, and executive reporting. The entire audit is 100% automated and reproducible with a single CLI command."
    )

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =========================================================================
    s5 = prs.slides[4]
    set_light_shape(s5.shapes[4], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1)) # Bottom footer bar

    # Who Benefits Badges (Shapes 8, 11, 14, 17) - Light SIH Blue fill
    for b_shape in [s5.shapes[8], s5.shapes[11], s5.shapes[14], s5.shapes[17]]:
        set_light_shape(b_shape, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    tint_icon_navy(s5.shapes[9])
    tint_icon_navy(s5.shapes[12])
    tint_icon_navy(s5.shapes[15])
    tint_icon_navy(s5.shapes[18])

    update_text(s5.shapes[6], "Who Benefits :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s5.shapes[10], "NTRO & Defense Agencies: Repeatable, automated AppSec framework to audit sovereign OSINT dashboards, satellite feeds, and border telemetry.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s5.shapes[13], "World Monitor Developers: Concrete, production-ready patch diffs (DOMPurify integration, fail-closed rate limiter, Node proxy socket pinning).", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s5.shapes[16], "Intelligence Analysts: Protects mission-critical threat feeds from indirect prompt injection, data poisoning, and unauthorized scraper denial.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s5.shapes[19], "DevSecOps Engineers: Automates continuous compliance checks against OWASP Top 10, CWE Top 25, and CVSS 3.1 directly within CI/CD pipelines.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Benefits Badges (Shapes 21, 24) - Light Slate fill
    set_light_shape(s5.shapes[21], C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))
    set_light_shape(s5.shapes[24], C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))

    tint_icon_navy(s5.shapes[22])
    tint_icon_navy(s5.shapes[25])

    update_text(s5.shapes[20], "Benefits :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s5.shapes[23], "Strategic National Defense: Hardens intelligence platforms against foreign state-sponsored cyber reconnaissance and feed tampering.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)
    update_text(s5.shapes[26], "Zero Infrastructure Footprint: Operates entirely locally on developer workstations; zero cloud dependency, zero recurring SaaS costs.", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Scalability Boxes (Shapes 28, 33, 38) - Light SIH Blue / Light Saffron fills
    set_light_shape(s5.shapes[28], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))
    set_light_shape(s5.shapes[33], C_SIH_LIGHT_SLATE, C_BORDER_SLATE, Pt(1))
    set_light_shape(s5.shapes[38], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    update_text(s5.shapes[27], "Scalability Path :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    update_text(s5.shapes[29], "NOW", font_size=Pt(11), bold=True, color=C_SIH_BLUE_HEAD)
    update_text(s5.shapes[30], "World Monitor Audit (v1.0)", font_size=Pt(10.5), bold=True, color=C_SIH_NAVY)
    update_text(s5.shapes[31], "166 endpoints audited · 12 confirmed findings · 5 safe PoCs · 12-page executive PDF & SARIF report", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s5.shapes[34], "NEXT", font_size=Pt(11), bold=True, color=C_SIH_BLUE_HEAD)
    update_text(s5.shapes[35], "Any Sovereign Web/API Target", font_size=Pt(10.5), bold=True, color=C_SIH_NAVY)
    update_text(s5.shapes[36], "Declarative YAML target profiles · GitHub Actions CI/CD gate · automated PR security comments", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    update_text(s5.shapes[39], "FUTURE", font_size=Pt(11), bold=True, color=C_SIH_BLUE_HEAD)
    update_text(s5.shapes[40], "Continuous Posture Monitoring", font_size=Pt(10.5), bold=True, color=C_SIH_NAVY)
    update_text(s5.shapes[41], "Autonomous re-scanning daemon · multi-target distributed queue · OWASP ASVS drift alerts", font_size=Pt(10), bold=False, color=C_TEXT_DARK)

    # Deliverables (8 required fields) Badges: Shapes 43, 46, 49, 52, 55, 58, 61, 64
    # Light SIH Blue fill with clean border, dark navy numbers
    update_text(s5.shapes[42], "Deliverable per Vulnerability (8 required fields) :", font_size=Pt(12), bold=True, color=C_SIH_NAVY)
    deliv_badges = [
        s5.shapes[43], s5.shapes[46], s5.shapes[49], s5.shapes[52],
        s5.shapes[55], s5.shapes[58], s5.shapes[61], s5.shapes[64]
    ]
    for badge in deliv_badges:
        set_light_shape(badge, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    # Numbers in 12pt bold Navy
    update_text(s5.shapes[44], "1", font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s5.shapes[45], "Title (Standardized)", font_size=Pt(10), bold=True, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    update_text(s5.shapes[47], "2", font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s5.shapes[48], "Description & Root Cause", font_size=Pt(10), bold=True, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    update_text(s5.shapes[50], "3", font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s5.shapes[51], "Affected Component", font_size=Pt(10), bold=True, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    update_text(s5.shapes[53], "4", font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s5.shapes[54], "Severity (CVSS 3.1)", font_size=Pt(10), bold=True, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    update_text(s5.shapes[56], "5", font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s5.shapes[57], "Steps to Reproduce", font_size=Pt(10), bold=True, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    update_text(s5.shapes[59], "6", font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s6.shapes[60] if hasattr(s5, 'none') else s5.shapes[60], "Safe PoC Evidence", font_size=Pt(10), bold=True, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    update_text(s5.shapes[62], "7", font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s5.shapes[63], "Business Impact", font_size=Pt(10), bold=True, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    update_text(s5.shapes[65], "8", font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)
    update_text(s5.shapes[66], "Remediation Diff", font_size=Pt(10), bold=True, color=C_TEXT_DARK, align=PP_ALIGN.CENTER)

    s5.notes_slide.notes_text_frame.text = (
        "[3:30 - 4:30 | 60s Pitch - Slide 5: Strategic Impact, Benefits & Deliverables Compliance]\n"
        "Slide 5 outlines the operational impact and strategic benefits of ARGUS.\n\n"
        "For NTRO, World Monitor is not simply a generic web dashboard—it is a live OSINT intelligence tool tracking real-time conflict telemetry, maritime vessels, and infrastructure. A compromise of its telemetry via indirect prompt injection or an unmetered resource DoS could blind strategic analysts during a national crisis.\n\n"
        "ARGUS directly protects this mission by delivering concrete, patch-ready remediations. As shown in our bottom-right table, ARGUS guarantees 100% compliance with all 8 mandatory deliverable fields stipulated in the problem statement—from deterministic reproduction steps to CVSS 3.1 vectors.\n\n"
        "Furthermore, ARGUS is built for immediate scale: while demonstrated on World Monitor today, its modular engine can be pointed at any sovereign government web service simply by changing the target YAML profile."
    )

    # =========================================================================
    # SLIDE 6: RESEARCH AND REFERENCES
    # =========================================================================
    s6 = prs.slides[5]
    set_light_shape(s6.shapes[4], C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1)) # Bottom footer bar

    # Harmonize Reference Badges (Shapes 7, 12, 17, 22, 27, 32, 37, 42)
    # Light SIH Blue fill, navy numbers in 12pt bold
    ref_badges = [
        s6.shapes[7], s6.shapes[12], s6.shapes[17], s6.shapes[22],
        s6.shapes[27], s6.shapes[32], s6.shapes[37], s6.shapes[42]
    ]
    for b in ref_badges:
        set_light_shape(b, C_SIH_LIGHT_BLUE, C_BORDER_BLUE, Pt(1))

    # Numbers in 12pt bold Navy
    num_shapes = [
        s6.shapes[8], s6.shapes[13], s6.shapes[18], s6.shapes[23],
        s6.shapes[28], s6.shapes[33], s6.shapes[38], s6.shapes[43]
    ]
    for idx, num_s in enumerate(num_shapes):
        update_text(num_s, str(idx + 1), font_size=Pt(12), bold=True, color=C_SIH_NAVY, align=PP_ALIGN.CENTER)

    update_text(s6.shapes[9], "Qadir et al. (2025) · Comparative evaluation of approaches & tools for effective security testing of Web applications. PeerJ Computer Science", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s6.shapes[10], "peerj.com/articles/cs-2821", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    update_text(s6.shapes[14], "A methodology for evaluating DAST scanners (2025). Springer Journal of Computer Virology and Hacking Techniques", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s6.shapes[15], "doi.org/10.1007/s10207-025-01054-8", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    update_text(s6.shapes[19], "A Novel VAPT Algorithm: Enhancing Web Application Security Through OWASP Top 10 Optimization (2023)", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s6.shapes[20], "arXiv:2311.10450", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    update_text(s6.shapes[24], "Do I really need all this work to find vulnerabilities? Empirical comparison of detection techniques (2022)", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s6.shapes[25], "arXiv:2208.01595", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    update_text(s6.shapes[29], "Semantic Similarity-Based Clustering of Findings From Security Testing Tools (2022)", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s6.shapes[30], "arXiv:2211.11057", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    update_text(s6.shapes[34], "OWASP Top 10:2021 · OWASP ASVS 5.0 · OWASP Top 10 for Large Language Model Applications (2025)", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s6.shapes[35], "owasp.org/Top10 · owasp.org/llm", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    update_text(s6.shapes[39], "MITRE CWE Top 25 Most Dangerous Software Weaknesses & FIRST CVSS v3.1 Specification", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s6.shapes[40], "cwe.mitre.org · first.org/cvss", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    update_text(s6.shapes[44], "World Monitor Open-Source Repository & GitHub Security Advisory GHSA-887j-p88r-qmm9 (MCP SSRF)", font_size=Pt(10), bold=True, color=C_TEXT_DARK)
    update_text(s6.shapes[45], "github.com/koala73/worldmonitor", font_size=Pt(10), bold=False, color=C_TEXT_MUTED)

    # Bottom Ethical Scope Box: Light SIH Blue fill, 1.5pt Navy border, 10pt dark readable text
    set_light_shape(s6.shapes[47], C_SIH_LIGHT_BLUE, C_BORDER_NAVY, Pt(1.5))
    update_text(s6.shapes[48], "Ethical Scope & Rules of Engagement: All security testing was executed strictly on an authorized, locally self-hosted sandbox instance (localhost:3000) using seeded test data. Zero active probing, scanning, or exploitation was conducted against production 'worldmonitor.app' or external upstream services. All 5 developed Proof-of-Concept scripts are non-destructive and limited strictly to existence validation. Fully compliant with NTRO guidelines, Indian IT Act (Sections 43 & 66), and responsible vulnerability disclosure standards.", font_size=Pt(10), bold=False, color=C_SIH_NAVY)

    s6.notes_slide.notes_text_frame.text = (
        "[4:30 - 5:00 | 30s Pitch - Slide 6: Research Foundations & Ethical Scope]\n"
        "Finally, on Slide 6: our methodology is grounded in recent peer-reviewed security research, including 2025 PeerJ and Springer publications on multi-tool correlation, alongside foundational standards from OWASP, MITRE CWE, and FIRST CVSS.\n\n"
        "Crucially, we maintained strict ethical discipline throughout: 100% of our testing was restricted to an isolated local clone on localhost with zero testing against production infrastructure, adhering strictly to Indian cybersecurity laws and NTRO ethical guidelines.\n\n"
        "In summary, ARGUS provides NTRO with a complete, evidence-backed security assessment that fulfills every requirement of SIH26163. We are now ready to demonstrate our live tool and answer your questions. Thank you."
    )

    prs.save(out_path)
    prs.save("SIH26163_ARGUS_Idea_PPT_Color.pptx")
    print(f"SIH Light Theme refinement complete! Saved to '{out_path}' and 'SIH26163_ARGUS_Idea_PPT_Color.pptx'")

if __name__ == "__main__":
    apply_sih_light_refinement()

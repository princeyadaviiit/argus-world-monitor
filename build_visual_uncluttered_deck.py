import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# ONE SHADE LIGHTER COLOR PALETTE
# ==============================================================================
C_NAVY_LIGHT         = RGBColor(37, 78, 134)    # #254E86 - Crisp, refined navy
C_TEAL_SLATE_LIGHT   = RGBColor(32, 115, 155)   # #20739B - Vibrant ocean teal
C_FOREST_GREEN_LIGHT = RGBColor(34, 153, 84)    # #229954 - Fresh emerald green
C_BURNT_ORANGE_LIGHT = RGBColor(222, 115, 42)   # #DE732A - Warm energetic amber
C_ROYAL_PURPLE_LIGHT = RGBColor(112, 70, 168)   # #7046A8 - Modern royal purple
C_MAROON_LIGHT       = RGBColor(176, 62, 42)    # #B03E2A - Vibrant rust crimson
C_DARK_MAROON_LIGHT  = RGBColor(160, 38, 38)    # #A02626 - Refined crimson banner

C_WHITE              = RGBColor(255, 255, 255)  # #FFFFFF
C_OFFWHITE           = RGBColor(248, 250, 252)  # #F8FAFC - Soft slate background
C_LIGHT_BLUE         = RGBColor(239, 246, 255)  # #EFF6FF - Soft ice blue
C_TEXT_DARK          = RGBColor(15, 23, 42)     # #0F172A - Deep charcoal
C_TEXT_MUTED         = RGBColor(71, 85, 105)    # #475569 - Muted slate
C_BORDER_LIGHT       = RGBColor(203, 213, 225)  # #CBD5E1 - Light slate border

def set_fill(shape, fill_color, border_color=None, border_width=Pt(1)):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = border_width
    else:
        shape.line.fill.background()

def add_box_with_text(slide, left, top, width, height, title, subtitle="", fill_col=C_NAVY_LIGHT, border_col=None, border_width=Pt(1), title_size=Pt(11), sub_size=Pt(9.5), shape_type=MSO_SHAPE.ROUNDED_RECTANGLE):
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
    p0.font.bold = True
    p0.font.size = title_size
    p0.font.color.rgb = C_WHITE if fill_col not in [C_OFFWHITE, C_LIGHT_BLUE, C_WHITE] else (border_col if border_col else C_TEXT_DARK)
    p0.alignment = PP_ALIGN.CENTER
    
    if subtitle:
        p1 = tf.add_paragraph()
        p1.text = subtitle
        p1.font.bold = False
        p1.font.size = sub_size
        p1.font.color.rgb = C_WHITE if fill_col not in [C_OFFWHITE, C_LIGHT_BLUE, C_WHITE] else C_TEXT_DARK
        p1.alignment = PP_ALIGN.CENTER
        p1.space_before = Pt(2)
        
    return shape

def add_connector(slide, x1, y1, x2, y2, color=C_NAVY_LIGHT, width=Pt(1.5)):
    connector = slide.shapes.add_connector(
        pptx.enum.shapes.MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2
    )
    connector.line.color.rgb = color
    connector.line.width = width
    return connector

prs = pptx.Presentation('SIH26163_ARGUS_Idea_PPT_Color.pptx')

# ==============================================================================
# REBUILD SLIDE 2: Proposed Solution
# ==============================================================================
print("Rebuilding Slide 2: Proposed Solution Architecture...")
s2 = prs.slides[1]

# Delete legacy content shapes on Slide 2 (keep 0-6: team oval, title, sih logo, footer)
shapes_to_remove = []
for i in range(7, len(s2.shapes)):
    shapes_to_remove.append(s2.shapes[i]._element)

for elem in shapes_to_remove:
    s2.shapes._spTree.remove(elem)

# 1. Top Callout Banner: "WHY THIS MATTERS — CRITICAL VULNERABILITIES IN INTELLIGENCE DASHBOARD"
top_banner_bg = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.50), Inches(1.32), Inches(12.33), Inches(0.95))
set_fill(top_banner_bg, C_OFFWHITE, border_color=C_DARK_MAROON_LIGHT, border_width=Pt(1.5))

# Top Red Strip
top_strip = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.50), Inches(1.32), Inches(12.33), Inches(0.28))
set_fill(top_strip, C_DARK_MAROON_LIGHT)
tf = top_strip.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "WHY THIS MATTERS — CRITICAL VULNERABILITY EXPOSURE IN INTELLIGENCE FEEDS"
p.font.bold = True
p.font.size = Pt(10)
p.font.color.rgb = C_WHITE
p.alignment = PP_ALIGN.LEFT
top_strip.text_frame.margin_left = Inches(0.12)
top_strip.text_frame.margin_top = Inches(0.04)

# 3 Columns inside Top Callout Box
col_w = Inches(3.95)
col_h = Inches(0.60)
col_y = Inches(1.63)

col_texts = [
    ("166 Vercel Edge Endpoints", "137 public & 29 Pro authenticated routes exposed without fail-closed rate limiters."),
    ("12 Correlated Flaws", "Confirmed DOM XSS (357 bypasses), SSRF rebinding, and prompt injection."),
    ("Deterministic Verification", "100% verified via 5 safe, non-destructive execution PoCs in isolated local sandbox.")
]

for c_idx, (c_title, c_sub) in enumerate(col_texts):
    c_x = Inches(0.60 + c_idx * 4.05)
    tb = s2.shapes.add_textbox(c_x, col_y, col_w, col_h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.clear()
    p0 = tf.paragraphs[0]
    p0.text = f"• {c_title}: "
    p0.font.bold = True
    p0.font.size = Pt(9.5)
    p0.font.color.rgb = C_NAVY_LIGHT
    r = p0.add_run()
    r.text = c_sub
    r.font.bold = False
    r.font.size = Pt(9.0)
    r.font.color.rgb = C_TEXT_DARK

# 2. Left Side: Hub-and-Spoke Architecture Diagram ("one box goes arrows to multiple boxes")
arch_lbl = s2.shapes.add_textbox(Inches(0.50), Inches(2.35), Inches(7.00), Inches(0.30))
tf = arch_lbl.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "Proposed Solution Architecture (Central Engine & Scanner Satellites) :"
p.font.bold = True
p.font.size = Pt(11)
p.font.color.rgb = C_NAVY_LIGHT

# Center Engine Box
center_x = Inches(2.25)
center_y = Inches(4.15)
center_w = Inches(3.50)
center_h = Inches(0.90)
hub = add_box_with_text(s2, center_x, center_y, center_w, center_h, 
                        "ARGUS CORE ENGINE", 
                        "Unified Correlation & Two-Signal Verification", 
                        fill_col=C_NAVY_LIGHT, title_size=Pt(12), sub_size=Pt(9.5))

# 4 Satellites around Central Engine
sat_w = Inches(2.80)
sat_h = Inches(0.85)

# Sat 1: Top-Left (Teal)
sat1 = add_box_with_text(s2, Inches(0.50), Inches(2.75), sat_w, sat_h,
                         "Target Surface Recon", "166 Vercel Edge Routes • 5 Trust Boundaries",
                         fill_col=C_TEAL_SLATE_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

# Sat 2: Top-Right (Green)
sat2 = add_box_with_text(s2, Inches(4.70), Inches(2.75), sat_w, sat_h,
                         "Multi-Engine Scanners", "Semgrep SAST • npm SCA • AST Route Parser",
                         fill_col=C_FOREST_GREEN_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

# Sat 3: Bottom-Left (Orange)
sat3 = add_box_with_text(s2, Inches(0.50), Inches(5.65), sat_w, sat_h,
                         "Deterministic Scoring", "FIRST CVSS v3.1 Base Score & Vector Calculation",
                         fill_col=C_BURNT_ORANGE_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

# Sat 4: Bottom-Right (Purple)
sat4 = add_box_with_text(s2, Inches(4.70), Inches(5.65), sat_w, sat_h,
                         "5 Safe PoC Engines", "Non-Destructive Exploitability Proof Logs",
                         fill_col=C_ROYAL_PURPLE_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

# Connectors from Hub to Satellites
add_connector(s2, Inches(3.00), Inches(4.15), Inches(1.90), Inches(3.60), color=C_NAVY_LIGHT, width=Pt(2))
add_connector(s2, Inches(5.00), Inches(4.15), Inches(6.10), Inches(3.60), color=C_NAVY_LIGHT, width=Pt(2))
add_connector(s2, Inches(3.00), Inches(5.05), Inches(1.90), Inches(5.65), color=C_NAVY_LIGHT, width=Pt(2))
add_connector(s2, Inches(5.00), Inches(5.05), Inches(6.10), Inches(5.65), color=C_NAVY_LIGHT, width=Pt(2))

# 3. Right Side: Core Principles & Evidenced Findings Table
prin_lbl = s2.shapes.add_textbox(Inches(7.85), Inches(2.35), Inches(5.00), Inches(0.30))
tf = prin_lbl.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "Core Solution Principles :"
p.font.bold = True
p.font.size = Pt(11)
p.font.color.rgb = C_NAVY_LIGHT

prin_tb = s2.shapes.add_textbox(Inches(7.85), Inches(2.65), Inches(4.98), Inches(1.40))
tf = prin_tb.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
tf.clear()

principles = [
    ("Two-Signal Confirmation:", "Drops unverified scanner noise, cutting manual triage time by 80%."),
    ("Architectural Privacy:", "Zero data or telemetry sent to external clouds; 100% runs locally."),
    ("Deterministic Auditing:", "AST route parsing + reproducible rule matches explainable to CERT-In.")
]

for idx, (head, body) in enumerate(principles):
    p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
    p.text = f"• {head} "
    p.font.bold = True
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_NAVY_LIGHT
    if idx > 0:
        p.space_before = Pt(3)
    r = p.add_run()
    r.text = body
    r.font.bold = False
    r.font.size = Pt(9.0)
    r.font.color.rgb = C_TEXT_DARK

# Summary Table Container Box
tbl_container = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.85), Inches(4.20), Inches(4.98), Inches(2.40))
set_fill(tbl_container, C_OFFWHITE, border_color=C_BURNT_ORANGE_LIGHT, border_width=Pt(1.5))

tbl_lbl = s2.shapes.add_textbox(Inches(8.00), Inches(4.25), Inches(4.68), Inches(0.28))
tf = tbl_lbl.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "Evidenced Audit Findings Summary :"
p.font.bold = True
p.font.size = Pt(10)
p.font.color.rgb = C_BURNT_ORANGE_LIGHT

# Table: 5 rows (1 header + 4 findings) x 3 columns
tbl_shape = s2.shapes.add_table(5, 3, Inches(7.95), Inches(4.55), Inches(4.78), Inches(1.95))
table = tbl_shape.table
table.columns[0].width = Inches(1.85)
table.columns[1].width = Inches(1.20)
table.columns[2].width = Inches(1.73)

tbl_headers = ["Vulnerability", "OWASP / CWE", "CVSS & Verification"]
for c_idx, h_text in enumerate(tbl_headers):
    cell = table.cell(0, c_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_LIGHT
    tf = cell.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0.04)
    tf.clear()
    p = tf.paragraphs[0]
    p.text = h_text
    p.font.bold = True
    p.font.size = Pt(9.0)
    p.font.color.rgb = C_WHITE

tbl_rows = [
    ("Fail-Open Rate Limiter DoS", "A04 / CWE-770", "7.5 High • PoC Confirmed"),
    ("DOM XSS (357 Call Sites)", "A03 / CWE-79", "6.1 Med • PoC Confirmed"),
    ("Prompt Injection Filter Bypass", "LLM01 / CWE-74", "6.5 Med • PoC Confirmed"),
    ("SSRF DNS Rebinding (MCP Proxy)", "A10 / CWE-918", "6.3 Med • PoC Confirmed")
]

for r_idx, row_data in enumerate(tbl_rows):
    bg_c = C_WHITE if r_idx % 2 == 0 else C_OFFWHITE
    for c_idx, val in enumerate(row_data):
        cell = table.cell(r_idx + 1, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg_c
        tf = cell.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0.04)
        tf.clear()
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(8.5)
        if c_idx == 0:
            p.font.bold = True
            p.font.color.rgb = C_TEXT_DARK
        elif c_idx == 1:
            p.font.color.rgb = C_TEXT_MUTED
        else:
            p.font.bold = True
            p.font.color.rgb = C_FOREST_GREEN_LIGHT if "Confirmed" in val else C_BURNT_ORANGE_LIGHT

print("Slide 2 rebuilt successfully.")

# ==============================================================================
# REBUILD SLIDE 4: Feasibility and Viability
# ==============================================================================
print("Rebuilding Slide 4: Feasibility and Viability...")
s4 = prs.slides[3]

# Remove legacy content shapes (keep 0-6)
shapes_to_remove = []
for i in range(7, len(s4.shapes)):
    shapes_to_remove.append(s4.shapes[i]._element)

for elem in shapes_to_remove:
    s4.shapes._spTree.remove(elem)

# Section Titles
s4_lbl1 = s4.shapes.add_textbox(Inches(0.50), Inches(1.25), Inches(5.20), Inches(0.32))
tf = s4_lbl1.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "Operational Execution Flow (Branching Pipeline) :"
p.font.bold = True
p.font.size = Pt(11)
p.font.color.rgb = C_NAVY_LIGHT

s4_lbl2 = s4.shapes.add_textbox(Inches(5.95), Inches(1.25), Inches(6.80), Inches(0.32))
tf = s4_lbl2.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "Feasibility & Viability Assessment (Key Dimensions) :"
p.font.bold = True
p.font.size = Pt(11)
p.font.color.rgb = C_NAVY_LIGHT

# Left Column: Branching Operational Flowchart
# Step 1: Sandbox Isolation
s4_n1 = add_box_with_text(s4, Inches(0.50), Inches(1.65), Inches(5.15), Inches(0.75),
                          "1. Local Target Sandbox Isolation",
                          "Clone AGPL-3.0 World Monitor; isolate 166 Vercel Edge API routes locally",
                          fill_col=C_TEAL_SLATE_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

# Arrow 1->2
add_connector(s4, Inches(3.07), Inches(2.40), Inches(3.07), Inches(2.65), color=C_NAVY_LIGHT, width=Pt(2))

# Step 2: Surface Recon
s4_n2 = add_box_with_text(s4, Inches(0.50), Inches(2.65), Inches(5.15), Inches(0.75),
                          "2. Multi-Engine Surface Recon",
                          "AST route parsing + Semgrep SAST + npm SCA automated telemetry",
                          fill_col=C_FOREST_GREEN_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

# Arrow 2->3
add_connector(s4, Inches(3.07), Inches(3.40), Inches(3.07), Inches(3.65), color=C_NAVY_LIGHT, width=Pt(2))

# Step 3: Central Gate (Hub)
s4_n3 = add_box_with_text(s4, Inches(0.50), Inches(3.65), Inches(5.15), Inches(0.75),
                          "3. ARGUS Central Correlation Gate",
                          "Pydantic v2 unified schema; deduplication & two-signal cross-check",
                          fill_col=C_NAVY_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

# Branching Arrows from Step 3 down to 3 parallel action nodes!
add_connector(s4, Inches(1.30), Inches(4.40), Inches(1.30), Inches(4.75), color=C_NAVY_LIGHT, width=Pt(2))
add_connector(s4, Inches(3.07), Inches(4.40), Inches(3.07), Inches(4.75), color=C_NAVY_LIGHT, width=Pt(2))
add_connector(s4, Inches(4.85), Inches(4.40), Inches(4.85), Inches(4.75), color=C_NAVY_LIGHT, width=Pt(2))

# Node 4A: Noise Drop (Orange)
s4_n4a = add_box_with_text(s4, Inches(0.50), Inches(4.75), Inches(1.60), Inches(1.85),
                           "Noise Drop",
                           "Two-signal rule eliminates scanner false positives, cutting triage by 80%.",
                           fill_col=C_BURNT_ORANGE_LIGHT, title_size=Pt(10.5), sub_size=Pt(8.5))

# Node 4B: 5 Safe PoCs (Purple)
s4_n4b = add_box_with_text(s4, Inches(2.27), Inches(4.75), Inches(1.60), Inches(1.85),
                           "5 Safe PoCs",
                           "Non-destructive automated verification scripts prove exploitability safely.",
                           fill_col=C_ROYAL_PURPLE_LIGHT, title_size=Pt(10.5), sub_size=Pt(8.5))

# Node 4C: Patch Diffs (Crimson)
s4_n4c = add_box_with_text(s4, Inches(4.05), Inches(4.75), Inches(1.60), Inches(1.85),
                           "Patch Diffs",
                           "Production-ready code fixes & SARIF 2.1.0 report delivered for engineers.",
                           fill_col=C_MAROON_LIGHT, title_size=Pt(10.5), sub_size=Pt(8.5))

# Right Column: 4 Clean Explanation Cards with Punchy Bullets
card_defs = [
    ("Technical Feasibility & White-Box Access", C_TEAL_SLATE_LIGHT, [
        ("White-Box Access:", "166 Vercel Edge endpoints audited via AST parser in isolated local container."),
        ("Zero External Risk:", "Runs self-hosted with mock telemetry; zero external cloud data exposure.")
    ]),
    ("Operational & Economic Viability ($0 Tooling)", C_FOREST_GREEN_LIGHT, [
        ("$0 Licensing Cost:", "Built entirely with open-source tools (Python 3.14, Semgrep OSS, Pydantic)."),
        ("Rapid Turnaround:", "Completes full multi-engine audit pass in <90 seconds on standard developer laptop.")
    ]),
    ("Challenge & Risk Mitigation Strategy", C_BURNT_ORANGE_LIGHT, [
        ("Two-Signal Rule:", "Eliminates single-scanner false alarms; slashes manual triage effort by 80%."),
        ("Non-Destructive PoCs:", "Safe verification scripts validate true exploitability without DoS damage.")
    ]),
    ("Strategic Impact & National Scalability", C_ROYAL_PURPLE_LIGHT, [
        ("Agency Ready:", "Immediate drop-in utility for NIC, CERT-In, and NTRO evaluation pipelines."),
        ("Universal Profiles:", "Easily adapted to any public portal via simple YAML configuration.")
    ])
]

for idx, (c_title, c_border, bullets) in enumerate(card_defs):
    y_pos = Inches(1.65 + idx * 1.25)
    card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.95), y_pos, Inches(6.85), Inches(1.15))
    set_fill(card, C_OFFWHITE, border_color=c_border, border_width=Pt(1.5))
    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0.08)
    tf.margin_bottom = Inches(0.06)
    tf.clear()
    
    p0 = tf.paragraphs[0]
    p0.text = c_title
    p0.font.bold = True
    p0.font.size = Pt(10.5)
    p0.font.color.rgb = c_border
    
    for b_head, b_body in bullets:
        p = tf.add_paragraph()
        p.text = f"• {b_head} "
        p.font.bold = True
        p.font.size = Pt(9.0)
        p.font.color.rgb = C_NAVY_LIGHT
        p.space_before = Pt(2)
        r = p.add_run()
        r.text = b_body
        r.font.bold = False
        r.font.size = Pt(9.0)
        r.font.color.rgb = C_TEXT_DARK

print("Slide 4 rebuilt successfully.")

# ==============================================================================
# REBUILD SLIDE 5: Impact and Benefits
# ==============================================================================
print("Rebuilding Slide 5: Impact and Benefits...")
s5 = prs.slides[4]

# Remove legacy content shapes (keep 0-6)
shapes_to_remove = []
for i in range(7, len(s5.shapes)):
    shapes_to_remove.append(s5.shapes[i]._element)

for elem in shapes_to_remove:
    s5.shapes._spTree.remove(elem)

# Section Titles
s5_lbl1 = s5.shapes.add_textbox(Inches(0.50), Inches(1.25), Inches(5.70), Inches(0.32))
tf = s5_lbl1.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "ARGUS Sovereign Impact Ecosystem (Multi-Stakeholder) :"
p.font.bold = True
p.font.size = Pt(11)
p.font.color.rgb = C_NAVY_LIGHT

s5_lbl2 = s5.shapes.add_textbox(Inches(6.60), Inches(1.25), Inches(6.23), Inches(0.32))
tf = s5_lbl2.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "Scalability Roadmap & Output Deliverables :"
p.font.bold = True
p.font.size = Pt(11)
p.font.color.rgb = C_NAVY_LIGHT

# Left Column: Central Impact Hub branching to 4 Beneficiaries ("one box goes arrows to multiple boxes")
hub5 = add_box_with_text(s5, Inches(1.65), Inches(3.45), Inches(3.40), Inches(0.85),
                         "ARGUS SOVEREIGN IMPACT",
                         "Multi-Stakeholder National AppSec Ecosystem",
                         fill_col=C_NAVY_LIGHT, title_size=Pt(11.5), sub_size=Pt(9.0))

sat5_w = Inches(2.65)
sat5_h = Inches(1.10)

# Beneficiary 1: NTRO (Green)
ben1 = add_box_with_text(s5, Inches(0.50), Inches(1.80), sat5_w, sat5_h,
                         "NTRO & Defense Agencies",
                         "Repeatable, automated AppSec framework to audit sovereign intelligence systems.",
                         fill_col=C_FOREST_GREEN_LIGHT, title_size=Pt(10.5), sub_size=Pt(8.5))

# Beneficiary 2: Developers (Orange)
ben2 = add_box_with_text(s5, Inches(3.45), Inches(1.80), sat5_w, sat5_h,
                         "World Monitor Developers",
                         "Concrete, production-ready patch diffs (DOMPurify, fail-closed rate limiters).",
                         fill_col=C_BURNT_ORANGE_LIGHT, title_size=Pt(10.5), sub_size=Pt(8.5))

# Beneficiary 3: Analysts (Purple)
ben3 = add_box_with_text(s5, Inches(0.50), Inches(4.80), sat5_w, sat5_h,
                         "Intelligence Analysts",
                         "Protects mission-critical OSINT feeds against prompt injection & DoS.",
                         fill_col=C_ROYAL_PURPLE_LIGHT, title_size=Pt(10.5), sub_size=Pt(8.5))

# Beneficiary 4: DevSecOps (Teal)
ben4 = add_box_with_text(s5, Inches(3.45), Inches(4.80), sat5_w, sat5_h,
                         "DevSecOps Engineers",
                         "Continuous CI/CD compliance gate mapped to OWASP & FIRST CVSS 3.1.",
                         fill_col=C_TEAL_SLATE_LIGHT, title_size=Pt(10.5), sub_size=Pt(8.5))

# Connectors from Hub5 to 4 Beneficiaries
add_connector(s5, Inches(2.50), Inches(3.45), Inches(1.82), Inches(2.90), color=C_NAVY_LIGHT, width=Pt(2))
add_connector(s5, Inches(4.20), Inches(3.45), Inches(4.78), Inches(2.90), color=C_NAVY_LIGHT, width=Pt(2))
add_connector(s5, Inches(2.50), Inches(4.30), Inches(1.82), Inches(4.80), color=C_NAVY_LIGHT, width=Pt(2))
add_connector(s5, Inches(4.20), Inches(4.30), Inches(4.78), Inches(4.80), color=C_NAVY_LIGHT, width=Pt(2))

# Right Column Top: 3 Scalability Roadmap Cards (NOW -> NEXT -> FUTURE)
r_card_w = Inches(6.23)
r_card_h = Inches(0.85)

# NOW Card
add_box_with_text(s5, Inches(6.60), Inches(1.80), r_card_w, r_card_h,
                  "NOW — World Monitor Audit (v1.0)",
                  "166 endpoints audited • 12 confirmed findings • 5 safe PoCs • 12-page executive report",
                  fill_col=C_FOREST_GREEN_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

add_connector(s5, Inches(9.71), Inches(2.65), Inches(9.71), Inches(2.80), color=C_NAVY_LIGHT, width=Pt(2))

# NEXT Card
add_box_with_text(s5, Inches(6.60), Inches(2.80), r_card_w, r_card_h,
                  "NEXT — Any Sovereign Web/API Target",
                  "Declarative YAML target profiles • GitHub Actions CI/CD gate • automated diff generation",
                  fill_col=C_BURNT_ORANGE_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

add_connector(s5, Inches(9.71), Inches(3.65), Inches(9.71), Inches(3.80), color=C_NAVY_LIGHT, width=Pt(2))

# FUTURE Card
add_box_with_text(s5, Inches(6.60), Inches(3.80), r_card_w, r_card_h,
                  "FUTURE — Continuous Posture Monitoring",
                  "Autonomous re-scanning daemon • multi-target distributed queue • OWASP drift tracking",
                  fill_col=C_ROYAL_PURPLE_LIGHT, title_size=Pt(11), sub_size=Pt(9.0))

# Right Column Bottom: 8 Deliverables in a 2x4 Badge Grid
deliv_lbl = s5.shapes.add_textbox(Inches(6.60), Inches(4.80), Inches(6.23), Inches(0.28))
tf = deliv_lbl.text_frame
tf.clear()
p = tf.paragraphs[0]
p.text = "Standardized Deliverables per Finding (8 Mandated Fields) :"
p.font.bold = True
p.font.size = Pt(10.5)
p.font.color.rgb = C_NAVY_LIGHT

badge_items = [
    ("1. Standard Title", C_NAVY_LIGHT),
    ("2. Root Cause", C_FOREST_GREEN_LIGHT),
    ("3. Affected Route", C_BURNT_ORANGE_LIGHT),
    ("4. CVSS 3.1 Score", C_ROYAL_PURPLE_LIGHT),
    ("5. Reproduction Steps", C_NAVY_LIGHT),
    ("6. Safe PoC Evidence", C_FOREST_GREEN_LIGHT),
    ("7. Business Impact", C_BURNT_ORANGE_LIGHT),
    ("8. Remediation Diff", C_ROYAL_PURPLE_LIGHT)
]

bw = Inches(1.48)
bh = Inches(0.48)
for b_idx, (b_text, b_col) in enumerate(badge_items):
    row_i = b_idx // 4
    col_i = b_idx % 4
    bx = Inches(6.60 + col_i * 1.58)
    by = Inches(5.15 + row_i * 0.58)
    add_box_with_text(s5, bx, by, bw, bh, b_text, "", fill_col=b_col, title_size=Pt(9.0), shape_type=MSO_SHAPE.ROUNDED_RECTANGLE)

print("Slide 5 rebuilt successfully.")

# Save presentation to both root and sources/
prs.save('SIH26163_ARGUS_Idea_PPT_Color.pptx')
prs.save('sources/SIH26163_ARGUS_Idea_PPT_Color.pptx')
print("Complete visual refinement saved successfully to both files!")

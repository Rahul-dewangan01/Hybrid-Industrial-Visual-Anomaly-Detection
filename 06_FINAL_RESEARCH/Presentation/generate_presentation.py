"""
generate_presentation.py
Generates the publication-quality 12-slide B.Tech research capstone presentation (PPTX and PDF)
strictly adhering to the academic sequence:
  1. Introduction
  2. Literature Survey (strictly 2021-2026 papers)
  3. Hypothesis (H1 to H4)
  4. Prove Your Hypothesis (Validation Matrix)
  5. Methodology (Overall System & DIP, Deep Learning & Hybrid, ACOMA, Computer Networks)
  6. Results (Quantitative Analysis, Qualitative & Network Results)
  7. Conclusion & Thank You
With visible course labels: DIP | ACOMA | COMPUTER NETWORKS
Institution: Indian Institute of Information Technology Raichur (IIIT Raichur), Academic Year 2026
Team: Omkar Kendre (AD24B1033), Rahul Dewangan (AD24B1050), Govind Das (AD24B1021)
NO supervisor / guide section. NO CSE department tags.
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Paths
OUTPUT_DIR = os.path.abspath('06_FINAL_RESEARCH/Presentation')
FIG_DIR = os.path.join(OUTPUT_DIR, 'PPT_Figures')
PPTX_PATH = os.path.join(OUTPUT_DIR, 'Final_Research_Presentation.pptx')
PDF_PATH = os.path.join(OUTPUT_DIR, 'Final_Research_Presentation.pdf')

# Palette
BG_DARK = RGBColor(15, 23, 42)         # Slate 900
BG_LIGHT = RGBColor(248, 250, 252)     # Slate 50
CARD_WHITE = RGBColor(255, 255, 255)   # Pure White
CARD_BLUE = RGBColor(239, 246, 255)    # Blue 50
CARD_GRAY = RGBColor(241, 245, 249)    # Slate 100
BORDER_COLOR = RGBColor(226, 232, 240) # Slate 200
BORDER_BLUE = RGBColor(191, 219, 254)  # Blue 200

TEXT_DARK = RGBColor(15, 23, 42)       # Slate 900
TEXT_SLATE = RGBColor(51, 65, 85)      # Slate 700
TEXT_MUTED = RGBColor(100, 116, 139)   # Slate 500
TEXT_WHITE = RGBColor(255, 255, 255)

ACCENT_BLUE = RGBColor(37, 99, 235)    # Blue 600
ACCENT_NAVY = RGBColor(30, 58, 138)    # Blue 900
ACCENT_TEAL = RGBColor(13, 148, 136)   # Teal 600
ACCENT_CORAL = RGBColor(225, 29, 72)   # Rose 600
ACCENT_AMBER = RGBColor(217, 119, 6)   # Amber 600
ACCENT_PURPLE = RGBColor(124, 58, 237) # Purple 600

# Course Tag Colors
DIP_COLOR = RGBColor(37, 99, 235)      # Blue 600
ACOMA_COLOR = RGBColor(217, 119, 6)    # Amber 600
CN_COLOR = RGBColor(13, 148, 136)      # Teal 600


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, section_text, slide_num, course_tags=None):
        # Header Text Box
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(9.2), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = section_text.upper()
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_BLUE

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(21)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_DARK
        p1.space_before = Pt(2)

        # Right side: Course tags & Slide Number
        right_box = slide.shapes.add_textbox(Inches(9.0), Inches(0.35), Inches(3.533), Inches(0.8))
        tf_r = right_box.text_frame
        tf_r.word_wrap = True
        tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

        p_num = tf_r.paragraphs[0]
        p_num.text = f"{slide_num:02d} / 12"
        p_num.font.size = Pt(11)
        p_num.font.bold = True
        p_num.font.color.rgb = TEXT_MUTED
        p_num.alignment = PP_ALIGN.RIGHT

        if course_tags:
            p_tag = tf_r.add_paragraph()
            p_tag.alignment = PP_ALIGN.RIGHT
            p_tag.space_before = Pt(3)
            for idx, tag in enumerate(course_tags):
                run = p_tag.add_run()
                run.text = f"[{tag}]"
                run.font.bold = True
                run.font.size = Pt(9.5)
                if tag == "DIP":
                    run.font.color.rgb = DIP_COLOR
                elif tag == "ACOMA":
                    run.font.color.rgb = ACOMA_COLOR
                elif tag == "COMPUTER NETWORKS":
                    run.font.color.rgb = CN_COLOR
                else:
                    run.font.color.rgb = ACCENT_PURPLE
                if idx < len(course_tags) - 1:
                    run_space = p_tag.add_run()
                    run_space.text = "  "

        # Subtle divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = BORDER_COLOR
        line.line.fill.background()

    def add_card(slide, left, top, width, height, bg_color=CARD_WHITE, border_color=BORDER_COLOR, border_width=1):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(border_width)
        else:
            shape.line.fill.background()
        return shape

    def set_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    print("Building Slide 1: Title Slide (IIIT Raichur)...")
    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, BG_DARK)

    # Top Pill
    add_card(s1, Inches(0.8), Inches(0.75), Inches(6.8), Inches(0.38),
             bg_color=RGBColor(30, 41, 59), border_color=ACCENT_BLUE, border_width=1.5)
    tb_pill = s1.shapes.add_textbox(Inches(0.9), Inches(0.75), Inches(6.6), Inches(0.38))
    tf_p = tb_pill.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf_p.paragraphs[0]
    p.text = "INDIAN INSTITUTE OF INFORMATION TECHNOLOGY RAICHUR  |  B.TECH 2026"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    # Main Project Title
    tb_title = s1.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.733), Inches(1.8))
    tf_t = tb_title.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks"
    p_t.font.size = Pt(29)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    p_sub = tf_t.add_paragraph()
    p_sub.text = "A Multi-Disciplinary Capstone Research Project Combining DIP, ACOMA, and Computer Networks"
    p_sub.font.size = Pt(13.5)
    p_sub.font.color.rgb = RGBColor(94, 234, 212) # Teal
    p_sub.space_before = Pt(8)

    # Divider line
    div = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.25), Inches(11.733), Inches(0.02))
    div.fill.solid()
    div.fill.fore_color.rgb = RGBColor(51, 65, 85)
    div.line.fill.background()

    # Team Members & Institutional Metadata (4 Cards)
    cards_data = [
        ("TEAM MEMBER 1", "Omkar Kendre\nRoll No: AD24B1033\nIIIT Raichur"),
        ("TEAM MEMBER 2", "Rahul Dewangan\nRoll No: AD24B1050\nIIIT Raichur"),
        ("TEAM MEMBER 3", "Govind Das\nRoll No: AD24B1021\nIIIT Raichur"),
        ("ACADEMIC INSTITUTION", "Indian Institute of Information\nTechnology Raichur\nAcademic Year: 2026")
    ]
    card_w = Inches(2.78)
    card_h = Inches(2.05)
    start_x = Inches(0.8)
    gap_x = Inches(0.2)

    for i, (hdr, body) in enumerate(cards_data):
        cx = start_x + i * (card_w + gap_x)
        add_card(s1, cx, Inches(3.5), card_w, card_h, bg_color=RGBColor(30, 41, 59), border_color=RGBColor(71, 85, 105))
        tb_m = s1.shapes.add_textbox(cx + Inches(0.15), Inches(3.6), card_w - Inches(0.3), card_h - Inches(0.2))
        tf_m = tb_m.text_frame
        tf_m.word_wrap = True
        p_h = tf_m.paragraphs[0]
        p_h.text = hdr
        p_h.font.size = Pt(10)
        p_h.font.bold = True
        p_h.font.color.rgb = RGBColor(147, 197, 253)

        p_b = tf_m.add_paragraph()
        p_b.text = body
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = RGBColor(226, 232, 240)
        p_b.space_before = Pt(6)

    # Bottom Execution Platform Specs Badge
    badge_tb = s1.shapes.add_textbox(Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.9))
    tf_b = badge_tb.text_frame
    tf_b.word_wrap = True
    p_bg = tf_b.paragraphs[0]
    p_bg.text = "RESEARCH PLATFORM & EXPERIMENTAL SCALE:"
    p_bg.font.size = Pt(9.5)
    p_bg.font.bold = True
    p_bg.font.color.rgb = RGBColor(148, 163, 184)

    p_bg2 = tf_b.add_paragraph()
    p_bg2.text = "736 Executed Runs (292 Base/Ablation + 444 Sweeps)  |  NVIDIA GeForce RTX 4060 GPU (8GB, CUDA 12.1)  |  12 MVTec AD Categories  |  Zero Data Leakage"
    p_bg2.font.size = Pt(10)
    p_bg2.font.bold = True
    p_bg2.font.color.rgb = RGBColor(241, 245, 249)
    p_bg2.space_before = Pt(3)

    set_speaker_notes(s1, """SLIDE 1: TITLE SLIDE (Time: 0:00 - 1:00)
- Presenter Script: "Good morning, respected evaluators. We present our B.Tech capstone project from IIIT Raichur titled: 'Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks', presented by Omkar Kendre, Rahul Dewangan, and Govind Das."
- Technical Context: This project integrates work across three core courses: Digital Image Processing (DIP), Optimization (ACOMA), and Computer Networks. Over 736 experimental trials were conducted on the MVTec AD benchmark using strictly normal-only training data.
- Viva Focus: Evaluators may ask about the multidisciplinary nature—explain that real manufacturing vision systems must balance visual detection accuracy (DIP), mathematical parameter optimization (ACOMA), and edge transmission latency (Computer Networks).""")

    print("Building Slide 2: Introduction (Section 1: Introduction)...")
    # -------------------------------------------------------------
    # SLIDE 2: INTRODUCTION
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, BG_LIGHT)
    add_header(s2, "Introduction: Industrial Quality Inspection", "Section 1: Introduction", 2)

    # Left Column: Problem & 3 Course Introductions
    add_card(s2, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.4))
    tb_s2 = s2.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.6), Inches(5.1))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True

    p = tf_s2.paragraphs[0]
    p.text = "THE INDUSTRIAL DEFECT INSPECTION CHALLENGE"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    intro_pts = [
        ("Automated Defect Detection: ", "Modern manufacturing requires 100% automated visual inspection at high throughput. Defects lead to catastrophic equipment failures, costly recalls, and safety risks."),
        ("Limitations of Manual Inspection: ", "Human quality control suffers from severe eye fatigue, subjectivity, and inconsistent repeatability (typically 80–85%)."),
        ("The 'Unseen Defect' Dilemma: ", "Defective products represent <1-2% of production, and defect morphologies are unpredictable (novel cracks, contaminants, chips). Supervised binary classifiers fail because unseen defects cannot be collected a priori."),
        ("Normal-Only Training Regimen: ", "Models train strictly on pristine, defect-free nominal images to learn the statistical manifold of normalcy, flagging deviations as anomalies."),
        ("Three Course Contributions: ", "\n  \u2022 DIP: Image feature extraction, ConvAE reconstruction, PatchCore, PaDiM, and hybrid fusion.\n  \u2022 ACOMA: Numerical optimization of feature weights against anomaly separation objectives.\n  \u2022 Computer Networks: Image compression (PNG/JPEG) and simulated transmission analysis.")
    ]
    for b_pre, body in intro_pts:
        p_pt = tf_s2.add_paragraph()
        p_pt.space_before = Pt(6)
        r_b = p_pt.add_run()
        r_b.text = b_pre
        r_b.font.bold = True
        r_b.font.size = Pt(10)
        r_b.font.color.rgb = TEXT_DARK
        r_t = p_pt.add_run()
        r_t.text = body
        r_t.font.size = Pt(9.2)
        r_t.font.color.rgb = TEXT_SLATE

    # Right Column: Visual (Nominal vs Defective)
    add_card(s2, Inches(7.0), Inches(1.5), Inches(5.533), Inches(5.4))
    img_s2 = os.path.join(FIG_DIR, 'slide02_normal_vs_defective.png')
    if os.path.exists(img_s2):
        s2.shapes.add_picture(img_s2, Inches(7.15), Inches(1.75), width=Inches(5.233))

    tb_s2_cap = s2.shapes.add_textbox(Inches(7.15), Inches(5.35), Inches(5.233), Inches(1.4))
    tf_s2_c = tb_s2_cap.text_frame
    tf_s2_c.word_wrap = True
    p_c1 = tf_s2_c.paragraphs[0]
    p_c1.text = "CORE PROJECT OBJECTIVE:"
    p_c1.font.bold = True
    p_c1.font.size = Pt(10)
    p_c1.font.color.rgb = ACCENT_CORAL

    p_c2 = tf_s2_c.add_paragraph()
    p_c2.text = "Detect and localize arbitrary, unseen physical anomalies purely by quantifying statistical divergence from nominal reference images—without ever exposing defect prototypes during training."
    p_c2.font.size = Pt(9.5)
    p_c2.font.color.rgb = TEXT_SLATE
    p_c2.space_before = Pt(2)

    set_speaker_notes(s2, """SLIDE 2: INTRODUCTION (Time: 1:00 - 2:00)
- What to Explain: Explain why automated defect detection is essential in industry. Discuss human inspector fatigue and inconsistency (80–85%). Explain why supervised classification fails on novel, rare defects (<1-2%).
- How to Introduce the 3 Courses:
  * DIP: Owns all image processing and deep learning models (ConvAE, PatchCore, PaDiM, Hybrid fusion).
  * ACOMA: Owns the numerical optimization of feature weights.
  * Computer Networks: Owns the image compression and simulated edge transmission latency study.
- Interpreting the Visual: Left shows a normal bottle (training set), middle is an unseen test defect (broken_large), right is the ground-truth mask.
- Viva Q&A:
  * Q: Why is normal-only training necessary?
  * A: In real factories, defect types are unbounded. Training only on normal items allows the system to detect any anomaly that deviates from normalcy without requiring historical defect data.""")

    print("Building Slide 3: Literature Survey (Section 2: Literature Survey)...")
    # -------------------------------------------------------------
    # SLIDE 3: LITERATURE SURVEY (2021-2026 ONLY)
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, BG_LIGHT)
    add_header(s3, "Literature Survey: Recent Advances (2021–2026)", "Section 2: Literature Survey", 3)

    # Table of 5 Verified Recent Papers (2021-2026)
    lit_rows = [
        ("Defard et al.\n(ICPR 2021)", "PaDiM: Patch Distribution\nModeling via CNN Features", "MVTec AD\n(15 Classes)", "0.979 Image AUROC\n0.921 Pixel AUROC", "Models spatial patch embeddings via localized multivariate Gaussians; high localization fidelity."),
        ("Roth et al.\n(CVPR 2022)", "PatchCore: Coreset Memory\nBanks & k-NN Scoring", "MVTec AD\n(15 Classes)", "0.991 Image AUROC\n0.981 Pixel AUROC", "Greedy minimax coreset reduces memory bank by 90-99%; establishes SOTA detection fidelity."),
        ("Zavrtanik et al.\n(ICCV 2021)", "DRAEM: Surface Anomaly\nReconstruction Embeddings", "MVTec AD\n(15 Classes)", "0.980 Image AUROC\n0.973 Pixel AUROC", "Dual reconstructive-discriminative sub-networks; effectively suppresses autoencoder blur."),
        ("Deng & Li\n(CVPR 2022)", "Reverse Distillation from\nOne-Class Embedding", "MVTec AD\n(15 Classes)", "0.981 Image AUROC\n0.972 Pixel AUROC", "Inverted student bottleneck decoder; proves tight bottleneck is vital to prevent defect memorization."),
        ("Batzner et al.\n(WACV 2024)", "EfficientAD: Millisecond-Level\nPatch Description Networks", "MVTec AD\n(15 Classes)", "0.995 Image AUROC\n0.969 Pixel AUROC", "Lightweight patch descriptions via asymmetric student-teacher distillation; sub-2ms GPU latency.")
    ]

    # Create Literature Table
    tbl_shape = s3.shapes.add_table(6, 5, Inches(0.8), Inches(1.5), Inches(11.733), Inches(3.4))
    t = tbl_shape.table
    col_w = [Inches(1.5), Inches(2.7), Inches(1.4), Inches(2.2), Inches(3.933)]
    for i, w in enumerate(col_w):
        t.columns[i].width = w

    headers_lit = ["Author & Year", "Methodology", "Dataset", "Performance", "Critical Results / Remarks"]
    for c_i, h in enumerate(headers_lit):
        cell = t.cell(0, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_WHITE
        p.alignment = PP_ALIGN.CENTER

    for r_i, row_data in enumerate(lit_rows):
        for c_i, val in enumerate(row_data):
            cell = t.cell(r_i + 1, c_i)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r_i % 2 == 0 else CARD_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_SLATE
            if c_i == 0:
                p.font.bold = True
                p.font.color.rgb = ACCENT_NAVY

    # Research Gap Callout Card
    add_card(s3, Inches(0.8), Inches(5.1), Inches(11.733), Inches(1.8), bg_color=CARD_BLUE, border_color=BORDER_BLUE, border_width=1.5)
    tb_gap = s3.shapes.add_textbox(Inches(1.0), Inches(5.2), Inches(11.333), Inches(1.6))
    tf_g = tb_gap.text_frame
    tf_g.word_wrap = True

    p_gh = tf_g.paragraphs[0]
    p_gh.text = "RESEARCH GAP IDENTIFIED (2021–2026 LITERATURE):"
    p_gh.font.bold = True
    p_gh.font.size = Pt(10)
    p_gh.font.color.rgb = ACCENT_NAVY

    p_gb = tf_g.add_paragraph()
    p_gb.text = (
        "1. Isolated Deep Paradigms: Existing studies evaluate individual deep architectures in isolation, lacking unified cross-paradigm comparisons with classical handcrafted image processing (DIP).\n"
        "2. Unaudited Optimization Claims: Literature frequently hypothesizes that numerical optimization (ACOMA) can tune feature weights on synthetic noise, but lacks rigorous empirical auditing on real physical defect manifolds.\n"
        "3. Missing Edge Network Feasibility: High-accuracy deep models are proposed without accounting for edge-to-server transmission bottlenecks (Computer Networks), ignoring how image compression impacts latency and anomaly detection fidelity."
    )
    p_gb.font.size = Pt(9)
    p_gb.font.color.rgb = TEXT_SLATE
    p_gb.space_before = Pt(3)

    set_speaker_notes(s3, """SLIDE 3: LITERATURE SURVEY (Time: 2:00 - 3:00)
- Strict Literature Constraint: Point out that all cited literature is strictly published between 2021 and 2026.
- Key Papers to Highlight:
  * Defard et al. (ICPR 2021) - PaDiM: Models spatial patch features with multivariate Gaussian distributions.
  * Roth et al. (CVPR 2022) - PatchCore: Uses memory bank coreset subsampling for total recall.
  * Zavrtanik et al. (ICCV 2021) - DRAEM: Discriminative reconstruction embedding to fix autoencoder blur.
  * Deng & Li (CVPR 2022) - Reverse Distillation: Proves tight bottleneck capacity prevents defect reconstruction.
  * Batzner et al. (WACV 2024) - EfficientAD: Distilled patch description networks achieving millisecond latencies.
- Explain the Research Gap: Existing papers focus only on deep models in isolation. None evaluate the complete pipeline connecting classical DIP, numerical weight optimization (ACOMA), and edge transmission compression (Computer Networks).""")

    print("Building Slide 4: Hypothesis (Section 3: Hypothesis)...")
    # -------------------------------------------------------------
    # SLIDE 4: HYPOTHESIS
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, BG_LIGHT)
    add_header(s4, "Research Hypotheses Formulation", "Section 3: Hypothesis", 4)

    # Central Hypothesis Box
    add_card(s4, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.3), bg_color=CARD_WHITE, border_color=ACCENT_BLUE, border_width=1.5)
    tb_ch = s4.shapes.add_textbox(Inches(1.0), Inches(1.58), Inches(11.333), Inches(1.15))
    tf_ch = tb_ch.text_frame
    tf_ch.word_wrap = True

    p = tf_ch.paragraphs[0]
    p.text = "CENTRAL RESEARCH HYPOTHESIS:"
    p.font.bold = True
    p.font.size = Pt(10)
    p.font.color.rgb = ACCENT_BLUE

    p_txt = tf_ch.add_paragraph()
    p_txt.text = (
        "\"Normal-only industrial anomaly detection can be evaluated and improved through the combination of classical image-processing "
        "techniques, deep-learning-based anomaly detection, and optimization-based score refinement, while image compression can be studied "
        "for its effect on transmission efficiency and detection performance.\""
    )
    p_txt.font.size = Pt(10)
    p_txt.font.italic = True
    p_txt.font.color.rgb = TEXT_DARK
    p_txt.space_before = Pt(3)

    # 4 Testable Sub-Hypotheses (4 Cards)
    sub_hyp = [
        ("H1 — DIP (Deep Learning)",
         DIP_COLOR,
         "Deep-learning-based anomaly detection methods (ConvAE, PatchCore, PaDiM) can identify and localize unseen physical defects using strictly normal-only training data without prototype supervision."),

        ("H2 — ACOMA (Optimization)",
         ACOMA_COLOR,
         "Optimization-based feature-weight selection can influence the performance of the classical DIP anomaly detection approach by tuning weights against synthetic anomaly separation objectives."),

        ("H3 — DIP (Hybrid Fusion)",
         ACCENT_PURPLE,
         "Combining complementary anomaly scores from diverse paradigms (reconstruction, memory banks, Gaussians) can provide useful performance improvements and stability compared with individual standalone methods."),

        ("H4 — Computer Networks",
         CN_COLOR,
         "Image compression can significantly reduce transmission size and latency, but compression quality levels (Q95, Q75, Q50) may influence downstream anomaly detection fidelity.")
    ]

    card_w4 = Inches(2.78)
    card_h4 = Inches(3.8)
    start_x4 = Inches(0.8)
    gap_x4 = Inches(0.2)

    for i, (h_title, col, h_body) in enumerate(sub_hyp):
        cx = start_x4 + i * (card_w4 + gap_x4)
        add_card(s4, cx, Inches(3.0), card_w4, card_h4, bg_color=CARD_WHITE, border_color=col, border_width=1.5)

        tb = s4.shapes.add_textbox(cx + Inches(0.15), Inches(3.15), card_w4 - Inches(0.3), card_h4 - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = h_title
        p0.font.bold = True
        p0.font.size = Pt(10.5)
        p0.font.color.rgb = col
        p0.space_after = Pt(8)

        p1 = tf.add_paragraph()
        p1.text = h_body
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = TEXT_SLATE

        p_note = tf.add_paragraph()
        p_note.text = "\n[Testable Hypothesis to Investigate]"
        p_note.font.size = Pt(8.5)
        p_note.font.bold = True
        p_note.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s4, """SLIDE 4: HYPOTHESIS (Time: 3:00 - 4:00)
- What to Explain: Clearly articulate the central research hypothesis connecting DIP, ACOMA, and Computer Networks.
- Break Down the 4 Sub-Hypotheses:
  * H1 (DIP): Can deep learning detect unseen defects without training defects?
  * H2 (ACOMA): Can mathematical optimization tune feature weights to improve classical anomaly separation?
  * H3 (Hybrid): Does multi-paradigm score fusion provide superior stability and accuracy over standalone models?
  * H4 (Computer Networks): Does image compression slash edge latency without destroying defect detection accuracy?
- IMPORTANT NOTE: Emphasize that these are testable propositions, not established conclusions. We will systematically evaluate them in subsequent slides.""")

    print("Building Slide 5: Prove Your Hypothesis (Section 4: Prove Your Hypothesis)...")
    # -------------------------------------------------------------
    # SLIDE 5: PROVE YOUR HYPOTHESIS
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, BG_LIGHT)
    add_header(s5, "Hypothesis-Validation Framework & Experimental Logic", "Section 4: Prove Your Hypothesis", 5)

    # Hypothesis Validation Matrix Table
    val_matrix = [
        ("H1: DIP (Deep Learning)",
         "Convolutional Autoencoder, PatchCore, and PaDiM evaluated across 12 MVTec AD industrial categories (1,389 train, 679 test).",
         "Image AUROC, Pixel AUROC, Optimal F1-Score, Inference Latency (ms)",
         "Compare deep models against classical DIP baselines and human ground-truth masks."),

        ("H2: ACOMA (Optimization)",
         "444 parameter sweep runs across 4 mathematical solvers (SLSQP, Conjugate Gradient, L-BFGS-B, Trust Region) on 12 categories.",
         "Objective Function Value, Optimized Weights (w_1..w_7), Synthetic AUROC vs Real Test AUROC",
         "Compare optimized feature weights against equal-weight baseline (w=1/7) on real physical test defects."),

        ("H3: Hybrid Detection",
         "Multi-paradigm ensembling comparing Mean Fusion (HY-01), Max Fusion (HY-02), and Weighted Fusion (HY-03: 0.2/0.4/0.4).",
         "Macro Image AUROC, Macro F1-Score, Score Variance, Category Recall",
         "Compare fused ensemble metrics against individual standalone models to verify stability."),

        ("H4: Computer Networks",
         "Image compression across Original PNG, JPEG Q95, JPEG Q75, and JPEG Q50 under simulated 10 Mbps edge link (50 ms RTT).",
         "File Size (KB), Compression Ratio, Transmission Time, Total Latency, Image AUROC, PSNR/SSIM",
         "Evaluate latency reduction versus downstream detection accuracy degradation to identify optimal Pareto point.")
    ]

    tbl_s5 = s5.shapes.add_table(5, 4, Inches(0.8), Inches(1.5), Inches(11.733), Inches(3.7))
    t5 = tbl_s5.table
    col_w5 = [Inches(1.8), Inches(3.5), Inches(3.2), Inches(3.233)]
    for i, w in enumerate(col_w5):
        t5.columns[i].width = w

    headers_val = ["Hypothesis", "Experimental Evidence", "Evaluation Metrics", "Verification Logic"]
    for c_i, h in enumerate(headers_val):
        cell = t5.cell(0, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_WHITE
        p.alignment = PP_ALIGN.CENTER

    for r_i, row in enumerate(val_matrix):
        for c_i, val in enumerate(row):
            cell = t5.cell(r_i + 1, c_i)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r_i % 2 == 0 else CARD_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(8.5)
            p.font.color.rgb = TEXT_SLATE
            if c_i == 0:
                p.font.bold = True
                p.font.color.rgb = ACCENT_NAVY

    # Bottom Logic Summary Card
    add_card(s5, Inches(0.8), Inches(5.4), Inches(11.733), Inches(1.5), bg_color=CARD_WHITE, border_color=BORDER_COLOR)
    tb_logic = s5.shapes.add_textbox(Inches(1.0), Inches(5.48), Inches(11.333), Inches(1.3))
    tf_l = tb_logic.text_frame
    tf_l.word_wrap = True

    p_lh = tf_l.paragraphs[0]
    p_lh.text = "EXPERIMENTAL EVIDENCE PROTOCOL:"
    p_lh.font.bold = True
    p_lh.font.size = Pt(10)
    p_lh.font.color.rgb = ACCENT_BLUE

    p_lb = tf_l.add_paragraph()
    p_lb.text = (
        "• Strict Experimental Integrity: Every hypothesis is evaluated against empirical results executed on raw dataset images.\n"
        "• Pre-determined Acceptance Criteria: Hypotheses will only be declared supported if quantitative metrics demonstrate statistically sound improvements, and refuted if empirical performance demonstrates zero transfer gain.\n"
        "• Transparent Negative Results: If an optimization hypothesis fails, the failure is reported openly with raw numerical data."
    )
    p_lb.font.size = Pt(9)
    p_lb.font.color.rgb = TEXT_SLATE
    p_lb.space_before = Pt(3)

    set_speaker_notes(s5, """SLIDE 5: PROVE YOUR HYPOTHESIS (Time: 4:00 - 5:00)
- What to Explain: Walk through the Hypothesis-Validation Matrix. Explain the experimental logic that bridges the hypotheses to empirical tests.
- Explain What Evidence is Used:
  * H1: 12-category deep learning benchmark using Image AUROC, Pixel AUROC, and F1.
  * H2: 444 optimization sweep runs testing if mathematical solvers transfer to real defects.
  * H3: 3 ensembling schemes (Mean, Max, Weighted) compared against standalone models.
  * H4: 4 compression formats simulated on a 10 Mbps edge link to evaluate latency vs AUROC trade-offs.
- Highlight Integrity: Emphasize that we do not cherry-pick results. If a hypothesis fails (like H2), we report it with full academic honesty.""")

    print("Building Slide 6: Methodology — Overall System & DIP (Section 5: Methodology)...")
    # -------------------------------------------------------------
    # SLIDE 6: METHODOLOGY: OVERALL SYSTEM AND DIP
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, BG_LIGHT)
    add_header(s6, "Overall System Architecture & DIP Framework", "Section 5: Methodology", 6, course_tags=["DIP"])

    # Left Column: Dataset & DIP Component
    add_card(s6, Inches(0.8), Inches(1.5), Inches(5.2), Inches(5.4))
    tb_s6 = s6.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(4.8), Inches(5.1))
    tf_s6 = tb_s6.text_frame
    tf_s6.word_wrap = True

    p = tf_s6.paragraphs[0]
    p.text = "DATASET & CLASSICAL DIP METHODOLOGY"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = DIP_COLOR

    dip_pts = [
        ("MVTec AD Benchmark: ", "12 evaluated categories (7 objects, 5 textures). 1,389 pristine training images, 679 test images across 65 defect types with 100% pixel-level ground truth masks. (Pill, Wood, Zipper omitted due to corrupt archive checksums)."),
        ("Normal-Only Principle: ", "Feature extractors, reference centroids, and covariance matrices fit strictly on defect-free nominal items."),
        ("7 Statistical & GLCM Features: ", "Mean (\u03bc), Standard Deviation (\u03c3), Skewness (\u03b3\u2081), Kurtosis (\u03b2\u2082), GLCM Energy, Information Entropy, Contrast."),
        ("Scoring Rules: ", "\n  \u2022 Normalized Distance: S(x) = \u2211 w_i |f_i - \u03bc_i| / \u03c3_i\n  \u2022 Mahalanobis Distance: D_M(x) = \u221a[(f-\u03bc)^T \u03a3\u207b\u00b9 (f-\u03bc)]\n  \u2022 One-Class SVM & Isolation Forest"),
        ("Deep Learning Scope in DIP: ", "ConvAE, PatchCore, and PaDiM are integrated under DIP as advanced spatial/feature representation learners.")
    ]
    for b_pre, body in dip_pts:
        p_pt = tf_s6.add_paragraph()
        p_pt.space_before = Pt(6)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(10)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(9.2)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: System Architecture Figure
    add_card(s6, Inches(6.2), Inches(1.5), Inches(6.333), Inches(5.4))
    img_arch = os.path.join(FIG_DIR, 'slide03_architecture.png')
    if os.path.exists(img_arch):
        s6.shapes.add_picture(img_arch, Inches(6.35), Inches(1.7), width=Inches(6.033))

    tb_s6_cap = s6.shapes.add_textbox(Inches(6.35), Inches(5.85), Inches(6.033), Inches(0.9))
    tf_s6_c = tb_s6_cap.text_frame
    tf_s6_c.word_wrap = True
    p_c6 = tf_s6_c.paragraphs[0]
    p_c6.text = "Figure: End-to-end inspection architecture: Input Dataset \u2192 Preprocessing \u2192 Parallel Paradigms (DIP, ConvAE, PatchCore, PaDiM) \u2192 Min-Max Normalization \u2192 Hybrid Ensembling \u2192 Evaluation."
    p_c6.font.size = Pt(8.5)
    p_c6.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s6, """SLIDE 6: METHODOLOGY: OVERALL SYSTEM & DIP (Time: 5:00 - 6:00)
- Course Identification: Note the [DIP] badge in the top right. DIP owns both classical image processing and deep learning in this project.
- Dataset Architecture: 12 categories from MVTec AD, 1,389 training images (all normal), 679 test images (200 normal, 479 defective) with 65 defect phenotypes. Transparently mention that Pill, Wood, and Zipper were omitted due to corrupt checksums.
- Classical DIP Features: 7 statistical moments and GLCM texture features. Explain baseline distance formulas (Normalized Euclidean, Mahalanobis, OC-SVM, Isolation Forest).
- Flow Diagram: Walk through Figure 1 from raw image input to parallel models, normalization, hybrid fusion, and evaluation.""")

    print("Building Slide 7: Methodology — Deep Learning & Hybrid (Section 5: Methodology)...")
    # -------------------------------------------------------------
    # SLIDE 7: METHODOLOGY: DEEP LEARNING AND HYBRID APPROACH
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, BG_LIGHT)
    add_header(s7, "Deep Learning Models & Hybrid Score Fusion", "Section 5: Methodology", 7, course_tags=["DIP"])

    # 4 Structured Methodology Cards (3 DL Models + Hybrid)
    m7_data = [
        ("1. CONVOLUTIONAL AUTOENCODER",
         DIP_COLOR,
         [("Bottleneck Compression: ", "Encoder reduces input images to latent bottleneck d_z = 64."),
          ("Multi-Scale Objective: ", "L = \u03b1 L_MSE + \u03b2 (1 - SSIM) + \u03b3 L_Sobel to enforce edge gradient sharpness."),
          ("Anomaly Scoring: ", "Pixel reconstruction residual error indicates unseen defect regions.")]),

        ("2. PATCHCORE (CORESET MEMORY)",
         ACCENT_NAVY,
         [("Patch Embeddings: ", "Extracts localized feature patches from pretrained ResNet-18 (Layers 2 & 3)."),
          ("Minimax Coreset: ", "Greedy subsampling retains 5% of memory tokens without loss of geometric coverage."),
          ("Anomaly Scoring: ", "Nearest-neighbor distance weighted by local cluster sparsity factor.")]),

        ("3. PADIM (GAUSSIAN MODELLING)",
         ACCENT_TEAL,
         [("Feature Concatenation: ", "Multi-scale CNN features downsampled to 100 randomly sampled channel dimensions."),
          ("Spatial Modeling: ", "Fits localized multivariate Gaussian N(\u03bc_(i,j), \u03a3_(i,j)) for each pixel position."),
          ("Anomaly Scoring: ", "Mahalanobis distance produces continuous spatial anomaly heatmaps.")]),

        ("4. HYBRID SCORE FUSION",
         ACCENT_PURPLE,
         [("Standardization: ", "Scores standardized via min-max normalization: S\u0302_m(x) = (S_m - \u03bc_m) / \u03c3_m."),
          ("Fusion Strategies: ", "Mean (HY-01), Max (HY-02), and Weighted (HY-03: 0.20 AE + 0.40 PC + 0.40 PaDiM)."),
          ("Operational Stability: ", "Combines orthogonal error distributions to dampen single-model false alarm outliers.")])
    ]

    card_w7 = Inches(2.78)
    card_h7 = Inches(5.4)
    start_x7 = Inches(0.8)
    gap_x7 = Inches(0.2)

    for i, (m_title, border_c, items) in enumerate(m7_data):
        cx = start_x7 + i * (card_w7 + gap_x7)
        add_card(s7, cx, Inches(1.5), card_w7, card_h7, bg_color=CARD_WHITE, border_color=border_c, border_width=1.5)

        tb = s7.shapes.add_textbox(cx + Inches(0.12), Inches(1.65), card_w7 - Inches(0.24), card_h7 - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = m_title
        p0.font.bold = True
        p0.font.size = Pt(10.5)
        p0.font.color.rgb = border_c
        p0.space_after = Pt(8)

        for b_hdr, text in items:
            p_i = tf.add_paragraph()
            p_i.space_before = Pt(8)
            r_b = p_i.add_run()
            r_b.text = b_hdr
            r_b.font.bold = True
            r_b.font.size = Pt(9.5)
            r_b.font.color.rgb = TEXT_DARK
            r_t = p_i.add_run()
            r_t.text = text
            r_t.font.size = Pt(9)
            r_t.font.color.rgb = TEXT_SLATE

    set_speaker_notes(s7, """SLIDE 7: METHODOLOGY: DEEP LEARNING & HYBRID (Time: 6:00 - 7:00)
- Course Identification: Note the [DIP] badge. Emphasize that all deep learning models are formally categorized under DIP.
- Model Breakdown:
  1. ConvAE: Reconstruction error residual under multi-scale loss (MSE + SSIM + Sobel).
  2. PatchCore: ResNet-18 feature extractor with 5% greedy minimax coreset subsampling and k-NN distance.
  3. PaDiM: Fits localized Gaussian distributions per spatial grid position across 100 random channel dimensions.
  4. Hybrid Fusion: Min-max standardization followed by Mean, Max, and Weighted fusion (0.2 AE + 0.4 PatchCore + 0.4 PaDiM).
- Viva Q&A:
  * Q: Why does PatchCore achieve higher detection accuracy than ConvAE?
  * A: ConvAE attempts to reconstruct pixels in image space, which suffers from blurring on fine textures. PatchCore operates in pretrained semantic feature space, making it sensitive to fine structural defects.""")

    print("Building Slide 8: Methodology — Optimization (Section 5: Methodology)...")
    # -------------------------------------------------------------
    # SLIDE 8: METHODOLOGY: OPTIMIZATION (ACOMA)
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, BG_LIGHT)
    add_header(s8, "Feature-Weight Optimization Framework", "Section 5: Methodology", 8, course_tags=["ACOMA"])

    # Left Column: Mathematical Formulation & Solvers
    add_card(s8, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb_s8 = s8.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf_s8 = tb_s8.text_frame
    tf_s8.word_wrap = True

    p = tf_s8.paragraphs[0]
    p.text = "ACOMA OPTIMIZATION FORMULATION"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACOMA_COLOR

    acoma_pts = [
        ("Optimization Problem: ", "Tune the 7 handcrafted DIP feature weights w = [w\u2081, ..., w\u2087]^T to maximize the separation between nominal reference features and anomalous test features."),
        ("Objective Function: ", "Minimize negative separation ratio / negative surrogate AUROC:\n  min_w J(w) = - [ \u03bc_anom(w) - \u03bc_norm(w) ] / \u221a[ \u03c3\u00b2_anom(w) + \u03c3\u00b2_norm(w) ]"),
        ("Constraints: ", "Simplex probability boundary: w_i \u2265 0 for all i, and \u2211_{i=1}^7 w_i = 1."),
        ("Implemented Optimization Solvers: ", "\n  \u2022 Steepest Gradient Descent\n  \u2022 Sequential Least Squares Programming (SLSQP)\n  \u2022 Conjugate Gradient (CG)\n  \u2022 L-BFGS-B (Bounded quasi-Newton)\n  \u2022 Trust-Region Constrained Solver"),
        ("444 Parameter Sweeps (OPT-P1 to P5): ", "Swept finite difference step (\u03b5 \u2208 [10\u207b\u2075, 0.5]), noise scale (\u03c3 \u2208 [0.01, 0.50]), starting points, and iterations across 12 categories.")
    ]
    for b_pre, body in acoma_pts:
        p_pt = tf_s8.add_paragraph()
        p_pt.space_before = Pt(6)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(10)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(9.2)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: Optimization Workflow Diagram / Visual
    add_card(s8, Inches(6.6), Inches(1.5), Inches(5.933), Inches(5.4))
    img_opt = os.path.join(FIG_DIR, 'slide07_optimization.png')
    if os.path.exists(img_opt):
        s8.shapes.add_picture(img_opt, Inches(6.75), Inches(1.65), width=Inches(5.633))

    tb_s8_cap = s8.shapes.add_textbox(Inches(6.75), Inches(5.85), Inches(5.633), Inches(0.9))
    tf_s8_c = tb_s8_cap.text_frame
    tf_s8_c.word_wrap = True
    p_c8 = tf_s8_c.paragraphs[0]
    p_c8.text = "Optimization Workflow: Initial Weights (w=1/7) \u2192 Numerical Optimizer \u2192 Updated Weights \u2192 Objective Evaluation \u2192 Final Validated Weights across 5 sweep axes (OPT-P1 to OPT-P5)."
    p_c8.font.size = Pt(8.5)
    p_c8.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s8, """SLIDE 8: METHODOLOGY: OPTIMIZATION (ACOMA) (Time: 7:00 - 8:00)
- Course Identification: Note the [ACOMA] badge. This slide covers the mathematical optimization contribution.
- Formulation Details:
  * Decision variables: 7 feature weights w_1 through w_7.
  * Objective: Maximize separation ratio between normal and synthetic anomaly distributions.
  * Constraints: Simplex boundary: w_i >= 0, sum(w_i) = 1.
  * Solvers: Steepest Descent, SLSQP, Conjugate Gradient, L-BFGS-B, Trust Region.
- Sweep Configuration: 444 runs across 5 experimental axes (finite difference step eps, noise scale sigma, initial weights, max iterations).""")

    print("Building Slide 9: Methodology — Computer Networks (Section 5: Methodology)...")
    # -------------------------------------------------------------
    # SLIDE 9: METHODOLOGY: COMPUTER NETWORKS
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, BG_LIGHT)
    add_header(s9, "Edge Image Compression & Network Transmission", "Section 5: Methodology", 9, course_tags=["COMPUTER NETWORKS"])

    # Left Column: Network Simulation & Compression Setup
    add_card(s9, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb_s9 = s9.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf_s9 = tb_s9.text_frame
    tf_s9.word_wrap = True

    p = tf_s9.paragraphs[0]
    p.text = "COMPUTER NETWORKS METHODOLOGY"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = CN_COLOR

    cn_pts = [
        ("Edge-to-Server Architecture: ", "Simulates an industrial edge inspection line where cameras capture images and transmit them across local networks to a centralized GPU server for inference."),
        ("Compression Formats Evaluated: ", "\n  \u2022 Lossless: Original PNG\n  \u2022 Lossy DCT Quantization: JPEG Q95, JPEG Q75, JPEG Q50"),
        ("Network Simulation Parameters: ", "\n  \u2022 Bandwidth: B = 10 Mbps industrial edge uplink\n  \u2022 Round-Trip Latency: RTT = 50 ms base network delay"),
        ("Transmission Time Formulation: ", "Transmission Time = Image Size in Bits / Bandwidth in bps\n  T_tx = (File Size in Bytes \u00d7 8) / (10 \u00d7 10\u2076)"),
        ("End-to-End Latency Formulation: ", "Total Latency = T_enc + T_tx + T_dec + T_inf + Network Latency\n(where T_inf is measured on RTX 4060 GPU; T_enc and T_dec on edge CPU)."),
        ("Simulation Disclosure: ", "Simulated transmission model based on analytical network formulas and measured hardware inference times.")
    ]
    for b_pre, body in cn_pts:
        p_pt = tf_s9.add_paragraph()
        p_pt.space_before = Pt(5)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(9.5)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(9)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: Visual / Network Trade-off preview
    add_card(s9, Inches(6.6), Inches(1.5), Inches(5.933), Inches(5.4))
    img_cn_pipe = os.path.join(FIG_DIR, 'slide11_network_tradeoff.png')
    if os.path.exists(img_cn_pipe):
        s9.shapes.add_picture(img_cn_pipe, Inches(6.75), Inches(1.8), width=Inches(5.633))

    tb_s9_cap = s9.shapes.add_textbox(Inches(6.75), Inches(5.85), Inches(5.633), Inches(0.9))
    tf_s9_c = tb_s9_cap.text_frame
    tf_s9_c.word_wrap = True
    p_c9 = tf_s9_c.paragraphs[0]
    p_c9.text = "Figure: Simulated edge-to-server network trade-off analyzing encoding, transmission, decoding, and GPU inference latency across PNG and JPEG quality factors."
    p_c9.font.size = Pt(8.5)
    p_c9.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s9, """SLIDE 9: METHODOLOGY: COMPUTER NETWORKS (Time: 8:00 - 9:00)
- Course Identification: Note the [COMPUTER NETWORKS] badge.
- Pipeline Overview: Explain the simulated edge-to-server manufacturing inspection line.
- Technical Formulas:
  * Transmission Time = Image Size in Bits / Bandwidth in bps (10 Mbps uplink).
  * Total Latency = Encoding Time + Transmission Time + Decoding Time + GPU Inference Time + Network RTT.
- Integrity Disclosure: Emphasize that network transmission is simulated analytically, while encoding, decoding, and GPU inference times were physically benchmarked on our hardware testbed.""")

    print("Building Slide 10: Results — Quantitative Analysis (Section 6: Results)...")
    # -------------------------------------------------------------
    # SLIDE 10: RESULTS: QUANTITATIVE ANALYSIS
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, BG_LIGHT)
    add_header(s10, "Quantitative Benchmark & Optimization Discovery", "Section 6: Results", 10, course_tags=["DIP", "ACOMA"])

    # Left Column: Macro Benchmark & Negative Result
    add_card(s10, Inches(0.8), Inches(1.5), Inches(5.4), Inches(5.4))
    tb_s10 = s10.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.0), Inches(5.1))
    tf_s10 = tb_s10.text_frame
    tf_s10.word_wrap = True

    p = tf_s10.paragraphs[0]
    p.text = "12-CATEGORY MACRO BENCHMARK & DISCOVERIES"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    res_pts = [
        ("A. DIP Benchmark Results: ", "\n  \u2022 PatchCore (ResNet-18, 5%): 0.9769 Image AUROC | 0.9721 Pixel AUROC | F1: 0.8221 | 85 ms (SOTA, 5 perfect categories)\n  \u2022 PaDiM (ResNet-18, 100d): 0.9082 Image AUROC | 0.9619 Pixel AUROC | F1: 0.8203 | 95 ms (Superior localization)\n  \u2022 ConvAE (5-Level): 0.6149 Image AUROC | 0.7220 Pixel AUROC | 18 ms (~55 FPS; 0.9333 on bottle)\n  \u2022 Classical DIP: Baseline Equal-7 0.5758 AUROC; Mahalanobis 0.5927 AUROC"),
        ("B. ACOMA Results (Critical Negative Finding): ", "\n  \u2022 On synthetic Gaussian noise, all 4 solvers converged to >0.9900 AUROC.\n  \u2022 On real test defects, optimized AUROC remained exactly 0.5758—identical to unweighted baseline!\n  \u2022 Finding: Synthetic Gaussian noise lacks spatial defect structure; handcrafted features cannot separate physical defect manifolds without defect priors."),
        ("C. Hybrid Fusion Results: ", "\n  \u2022 HY-01 (Mean): 0.9586 AUROC | F1: 0.8186\n  \u2022 HY-02 (Max): 0.9421 AUROC | F1: 0.8190\n  \u2022 HY-03 (Weighted: 0.2/0.4/0.4): 0.9626 AUROC | F1: 0.8180 (100% recall)")
    ]
    for b_pre, body in res_pts:
        p_pt = tf_s10.add_paragraph()
        p_pt.space_before = Pt(5)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(9.5)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(8.8)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: Visual Chart (slide08_dl_benchmark.png)
    add_card(s10, Inches(6.4), Inches(1.5), Inches(6.133), Inches(5.4))
    img_res = os.path.join(FIG_DIR, 'slide08_dl_benchmark.png')
    if os.path.exists(img_res):
        s10.shapes.add_picture(img_res, Inches(6.55), Inches(1.8), width=Inches(5.833))

    tb_s10_cap = s10.shapes.add_textbox(Inches(6.55), Inches(5.85), Inches(5.833), Inches(0.9))
    tf_s10_c = tb_s10_cap.text_frame
    tf_s10_c.word_wrap = True
    p_c10 = tf_s10_c.paragraphs[0]
    p_c10.text = "Figure: Comparison of standalone deep learning architectures across Image AUROC, Pixel AUROC, and Inference Latency on RTX 4060 GPU."
    p_c10.font.size = Pt(8.5)
    p_c10.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s10, """SLIDE 10: RESULTS: QUANTITATIVE ANALYSIS (Time: 9:00 - 10:00)
- Course Identification: Note both [DIP] and [ACOMA] badges.
- Quantitative Deep Learning (DIP):
  * PatchCore is SOTA with 0.9769 Image AUROC and 0.9721 Pixel AUROC (perfect 1.0000 on 5 categories).
  * PaDiM excels in spatial localization at 0.9619 Pixel AUROC.
  * ConvAE is fastest (18 ms, 55 FPS), suitable for edge screening.
- The Negative Optimization Discovery (ACOMA):
  * Optimizers converge to >0.99 AUROC on synthetic noise, but achieve 0.5758 on real defects (identical to unoptimized baseline).
  * Explain that reporting this negative result with 444 runs provides genuine scientific value: synthetic Gaussian noise cannot model real defect manifolds.
- Hybrid Fusion: HY-03 achieves 0.9626 AUROC and 100% recall, suppressing false alarm outliers.""")

    print("Building Slide 11: Results — Qualitative & Network (Section 6: Results)...")
    # -------------------------------------------------------------
    # SLIDE 11: RESULTS: QUALITATIVE ANALYSIS & NETWORK RESULTS
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, BG_LIGHT)
    add_header(s11, "Qualitative Heatmaps & Network Compression Trade-off", "Section 6: Results", 11, course_tags=["DIP", "COMPUTER NETWORKS"])

    # Left Region: DIP Qualitative Analysis (4 columns: Input | GT | Heatmap | Overlay)
    add_card(s11, Inches(0.8), Inches(1.5), Inches(6.5), Inches(5.4))
    img_qual = os.path.join(FIG_DIR, 'slide11_dip_qualitative.png')
    if os.path.exists(img_qual):
        s11.shapes.add_picture(img_qual, Inches(0.95), Inches(1.65), width=Inches(6.2))

    tb_qual_cap = s11.shapes.add_textbox(Inches(0.95), Inches(6.15), Inches(6.2), Inches(0.7))
    tf_qc = tb_qual_cap.text_frame
    tf_qc.word_wrap = True
    p_qc = tf_qc.paragraphs[0]
    p_qc.text = "DIP Qualitative Analysis: (Top) Broken Large structural crack. (Middle) Contamination surface impurity. (Bottom - Failure Case) Subtle edge chip where ConvAE produces edge blur halo."
    p_qc.font.size = Pt(8)
    p_qc.font.color.rgb = TEXT_SLATE

    # Right Region: Computer Networks Compression Results
    add_card(s11, Inches(7.5), Inches(1.5), Inches(5.033), Inches(5.4))
    img_cn_res = os.path.join(FIG_DIR, 'slide11_cn_compression.png')
    if os.path.exists(img_cn_res):
        s11.shapes.add_picture(img_cn_res, Inches(7.65), Inches(1.65), width=Inches(4.733))

    tb_cn_cap = s11.shapes.add_textbox(Inches(7.65), Inches(6.15), Inches(4.733), Inches(0.7))
    tf_cnc = tb_cn_cap.text_frame
    tf_cnc.word_wrap = True
    p_cnc = tf_cnc.paragraphs[0]
    p_cnc.text = "Computer Networks Findings: JPEG Q75 slashes latency by 43.0% (89.9 ms vs 157.8 ms) and boosts AUROC by +4.55% via sensor noise suppression (Simulated Network)."
    p_cnc.font.size = Pt(8)
    p_cnc.font.color.rgb = TEXT_SLATE

    set_speaker_notes(s11, """SLIDE 11: RESULTS: QUALITATIVE & NETWORK (Time: 10:00 - 11:00)
- Course Identification: Note both [DIP] and [COMPUTER NETWORKS] badges.
- Left Region (DIP Qualitative):
  * Walk through the 4 columns: Input Image -> Ground Truth Mask -> Predicted Anomaly Heatmap -> Overlay.
  * Point out successful structural defect isolation (broken_large) and surface dirt isolation (contamination).
  * Honestly discuss the failure case (broken_small): ConvAE exhibits blurry residual edge halos, whereas PatchCore successfully isolates the chipped lip.
- Right Region (Computer Networks):
  * Point out the 43.0% latency reduction achieved by JPEG Q75 (89.9 ms vs 157.8 ms).
  * Explain the 'Edge Denoising Effect': JPEG Q75 increases AUROC from 0.7515 to 0.7970 (+4.55%) because DCT quantization filters high-frequency camera sensor noise.
  * Note that Q50 degrades AUROC (0.7455) due to 8x8 block artifacts.""")

    print("Building Slide 12: Conclusion & Thank You...")
    # -------------------------------------------------------------
    # SLIDE 12: CONCLUSION AND THANK YOU
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, BG_LIGHT)
    add_header(s12, "Summary of Contributions, Hypothesis Evaluation & Future Scope", "Conclusion", 12)

    # 3 Summary Cards
    concl_cards = [
        ("THREE COURSE CONTRIBUTIONS",
         ACCENT_NAVY,
         [("DIP: ", "Established PatchCore (0.9769 Image AUROC) and PaDiM (0.9619 Pixel AUROC) as SOTA; 5-level ConvAE achieves 55 FPS; HY-03 provides stable ensembling."),
          ("ACOMA: ", "Conducted 444 systematic parameter sweeps across 4 solvers; disproved synthetic feature optimization on real physical defect manifolds."),
          ("Computer Networks: ", "Identified JPEG Q75 as the Pareto sweet spot, slashing latency by 43.0% while improving AUROC by +4.55% via edge sensor denoising.")]),

        ("HYPOTHESIS EVALUATION MATRIX",
         ACCENT_BLUE,
         [("H1 (DIP): FULLY SUPPORTED \u2705", "Deep learning models accurately detect and localize unseen physical defects under normal-only training."),
          ("H2 (ACOMA): REFUTED \u274c", "Optimizing feature weights on synthetic Gaussian noise yields 0.00% transfer gain on real defects."),
          ("H3 (Hybrid): SUPPORTED \u2705", "HY-03 suppresses false alarms, achieving 100% recall across all 12 industrial categories."),
          ("H4 (Networks): FULLY SUPPORTED \u2705", "Compression reduces latency; Q75 enhances AUROC via noise attenuation.")]),

        ("LIMITATIONS & FUTURE SCOPE",
         ACCENT_TEAL,
         [("Current Limitations: ", "Simulated 10 Mbps bandwidth vs physical industrial fieldbus jitter; sensitivity to extreme illumination shifts."),
          ("Zero-Shot Vision-Language: ", "Investigate foundation models (WinCLIP, CLIP) for zero-training adaptation on novel factory lines."),
          ("TensorRT Edge Quantization: ", "Quantize PatchCore embeddings to INT8 for sub-10ms inference on NVIDIA Jetson edge nodes."),
          ("Wireless 5G TSN Validation: ", "Validate latency on physical 5G Time-Sensitive Networking manufacturing testbeds.")])
    ]

    card_w12 = Inches(3.75)
    card_h12 = Inches(3.6)
    start_x12 = Inches(0.8)
    gap_x12 = Inches(0.24)

    for i, (title_c, border_c, points_c) in enumerate(concl_cards):
        cx = start_x12 + i * (card_w12 + gap_x12)
        add_card(s12, cx, Inches(1.5), card_w12, card_h12, bg_color=CARD_WHITE, border_color=border_c, border_width=1.5)

        tb = s12.shapes.add_textbox(cx + Inches(0.12), Inches(1.65), card_w12 - Inches(0.24), card_h12 - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = title_c
        p0.font.bold = True
        p0.font.size = Pt(10)
        p0.font.color.rgb = border_c
        p0.space_after = Pt(6)

        for b_hdr, text in points_c:
            p_i = tf.add_paragraph()
            p_i.space_before = Pt(5)
            r_b = p_i.add_run()
            r_b.text = b_hdr
            r_b.font.bold = True
            r_b.font.size = Pt(9)
            r_b.font.color.rgb = TEXT_DARK
            r_t = p_i.add_run()
            r_t.text = text
            r_t.font.size = Pt(8.5)
            r_t.font.color.rgb = TEXT_SLATE

    # Bottom Thank You & Q&A Banner (Clean, Minimal, IIIT Raichur Identity)
    add_card(s12, Inches(0.8), Inches(5.3), Inches(11.733), Inches(1.6), bg_color=BG_DARK, border_color=ACCENT_BLUE, border_width=1.5)
    tb_ty = s12.shapes.add_textbox(Inches(1.0), Inches(5.4), Inches(11.333), Inches(1.4))
    tf_ty = tb_ty.text_frame
    tf_ty.word_wrap = True

    p_ty = tf_ty.paragraphs[0]
    p_ty.text = "THANK YOU   |   QUESTIONS?"
    p_ty.font.size = Pt(20)
    p_ty.font.bold = True
    p_ty.font.color.rgb = RGBColor(147, 197, 253)

    p_subty = tf_ty.add_paragraph()
    p_subty.text = (
        "Team Members: Omkar Kendre (AD24B1033)  |  Rahul Dewangan (AD24B1050)  |  Govind Das (AD24B1021)\n"
        "Institution: Indian Institute of Information Technology Raichur (IIIT Raichur)  |  Academic Year: 2026\n"
        "GitHub Repository: https://github.com/Rahul-dewangan01/Hybrid-Industrial-Visual-Anomaly-Detection"
    )
    p_subty.font.size = Pt(9.5)
    p_subty.font.color.rgb = RGBColor(226, 232, 240)
    p_subty.space_before = Pt(6)

    set_speaker_notes(s12, """SLIDE 12: CONCLUSION & FUTURE WORK (Time: 11:00 - 12:00)
- Presenter Script: "In conclusion, we have evaluated 736 experimental trials across DIP, ACOMA, and Computer Networks. Our hypotheses H1, H3, and H4 were supported by strong empirical data, while H2 was conclusively refuted, establishing that synthetic noise cannot model real defect manifolds."
- Summary of Contributions:
  * DIP: PatchCore (0.9769) and PaDiM (0.9619) established gold-standard accuracy.
  * ACOMA: Rigorously disproved synthetic optimization transfer across 444 runs.
  * Computer Networks: Discovered JPEG Q75 denoising effect (43.0% latency reduction, +4.55% AUROC).
- Closing: Thank the evaluation committee and open the floor for questions.""")

    # Save PPTX
    prs.save(PPTX_PATH)
    print(f"Presentation successfully saved to: {PPTX_PATH}")


def convert_pptx_to_pdf():
    print("Converting PPTX to PDF via PowerPoint COM engine...")
    import win32com.client
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    deck = powerpoint.Presentations.Open(PPTX_PATH, WithWindow=False)
    deck.SaveAs(PDF_PATH, 32) # ppSaveAsPDF = 32
    deck.Close()
    powerpoint.Quit()
    print(f"PDF successfully exported to: {PDF_PATH}")


if __name__ == '__main__':
    create_presentation()
    convert_pptx_to_pdf()

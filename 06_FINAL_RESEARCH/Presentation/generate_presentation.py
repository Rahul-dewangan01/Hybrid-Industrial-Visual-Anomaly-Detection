"""
generate_presentation.py
Generates the 12-slide publication-quality final B.Tech research presentation (PPTX and PDF)
along with embedded speaker notes.
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

# Design Colors
BG_DARK = RGBColor(15, 23, 42)       # Slate 900
BG_LIGHT = RGBColor(248, 250, 252)   # Slate 50
CARD_WHITE = RGBColor(255, 255, 255) # Pure White
CARD_BLUE = RGBColor(239, 246, 255)  # Blue 50
BORDER_COLOR = RGBColor(226, 232, 240) # Slate 200
BORDER_BLUE = RGBColor(191, 219, 254)  # Blue 200

TEXT_DARK = RGBColor(15, 23, 42)     # Slate 900
TEXT_SLATE = RGBColor(51, 65, 85)    # Slate 700
TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
TEXT_WHITE = RGBColor(255, 255, 255)

ACCENT_BLUE = RGBColor(37, 99, 235)  # Blue 600
ACCENT_NAVY = RGBColor(30, 58, 138)  # Blue 900
ACCENT_TEAL = RGBColor(13, 148, 136) # Teal 600
ACCENT_CORAL = RGBColor(225, 29, 72) # Rose 600
ACCENT_AMBER = RGBColor(217, 119, 6) # Amber 600


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Helper functions
    def set_slide_background(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category_text, slide_num):
        # Header text box
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(10)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_BLUE

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_DARK
        p1.space_before = Pt(2)

        # Slide number box
        tb_num = slide.shapes.add_textbox(Inches(11.5), Inches(0.4), Inches(1.033), Inches(0.4))
        tf_num = tb_num.text_frame
        tf_num.margin_left = tf_num.margin_top = tf_num.margin_right = tf_num.margin_bottom = 0
        p_num = tf_num.paragraphs[0]
        p_num.text = f"{slide_num:02d} / 12"
        p_num.font.size = Pt(11)
        p_num.font.bold = True
        p_num.font.color.rgb = TEXT_MUTED
        p_num.alignment = PP_ALIGN.RIGHT

        # Decorative thin accent line
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

    print("Building Slide 1: Title Slide...")
    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, BG_DARK)

    # Accent top banner pill
    pill = add_card(s1, Inches(0.8), Inches(0.8), Inches(5.8), Inches(0.38), bg_color=RGBColor(30, 41, 59), border_color=ACCENT_BLUE, border_width=1.5)
    tb_pill = s1.shapes.add_textbox(Inches(0.9), Inches(0.8), Inches(5.6), Inches(0.38))
    tf_p = tb_pill.text_frame
    tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf_p.paragraphs[0]
    p.text = "FINAL YEAR B.TECH CAPSTONE RESEARCH PRESENTATION | CSE"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = RGBColor(147, 197, 253)

    # Main Title
    tb_title = s1.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.733), Inches(1.8))
    tf_t = tb_title.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks"
    p_t.font.size = Pt(30)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    p_sub = tf_t.add_paragraph()
    p_sub.text = "Unsupervised Normal-Only Defect Inspection Benchmark Across 12 MVTec Categories & 736 Validated Experiments"
    p_sub.font.size = Pt(14)
    p_sub.font.color.rgb = RGBColor(94, 234, 212) # Soft teal
    p_sub.space_before = Pt(8)

    # Divider line
    div = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.2), Inches(11.733), Inches(0.02))
    div.fill.solid()
    div.fill.fore_color.rgb = RGBColor(51, 65, 85)
    div.line.fill.background()

    # 4 Metadata Cards
    meta_info = [
        ("CANDIDATE", "Rahul Dewangan\nRoll No: [INSERT ENROLLMENT]\nDept. of Computer Science & Engg."),
        ("PROJECT SUPERVISOR", "[INSERT GUIDE NAME]\nAssistant Professor\nDept. of Computer Science & Engg."),
        ("INSTITUTION", "[INSERT INSTITUTION NAME]\nFaculty of Engineering & Technology\nAcademic Session: 2024–2025"),
        ("DISCIPLINES INTEGRATED", "Digital Image Processing (DIP)\nOptimization Algorithms (ACOMA)\nComputer Networks & Deep Vision")
    ]
    card_w = Inches(2.78)
    card_h = Inches(2.2)
    start_x = Inches(0.8)
    gap_x = Inches(0.2)

    for i, (hdr, body) in enumerate(meta_info):
        cx = start_x + i * (card_w + gap_x)
        c_shape = add_card(s1, cx, Inches(3.45), card_w, card_h, bg_color=RGBColor(30, 41, 59), border_color=RGBColor(71, 85, 105))
        tb_m = s1.shapes.add_textbox(cx + Inches(0.15), Inches(3.55), card_w - Inches(0.3), card_h - Inches(0.2))
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

    # Bottom Execution Badge
    badge_tb = s1.shapes.add_textbox(Inches(0.8), Inches(6.1), Inches(11.733), Inches(0.8))
    tf_b = badge_tb.text_frame
    tf_b.word_wrap = True
    p_bg = tf_b.paragraphs[0]
    p_bg.text = "RESEARCH PLATFORM & HARDWARE SPECS:"
    p_bg.font.size = Pt(9.5)
    p_bg.font.bold = True
    p_bg.font.color.rgb = RGBColor(148, 163, 184)

    p_bg2 = tf_b.add_paragraph()
    p_bg2.text = "NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)  |  PyTorch 2.5.1 + CUDA 12.1  |  736 Executed Runs  |  12 MVTec Categories  |  Zero Test Data Leakage"
    p_bg2.font.size = Pt(10.5)
    p_bg2.font.bold = True
    p_bg2.font.color.rgb = RGBColor(241, 245, 249)
    p_bg2.space_before = Pt(3)

    set_speaker_notes(s1, """SLIDE 1: TITLE & INTRODUCTION (Time: 0:00 - 1:00)
- What to Explain: Introduce the project title, research scope, and multidisciplinary nature spanning DIP, mathematical optimization, deep learning, and computer networks. Mention that this capstone research addresses industrial quality inspection using strictly normal-only training data.
- Key Technical Points: 736 experimental runs executed across 12 industrial categories of the MVTec AD dataset. No defective samples were used during model training.
- Evaluator Questions:
  * Q: Why combine DIP, deep learning, and computer networks?
  * A: Real manufacturing requires low-latency edge transmission, explainable classical baselines, and high-accuracy deep learning. We bridge algorithmic accuracy with real-time edge network constraints.""")

    print("Building Slide 2: Problem Statement & Objectives...")
    # -------------------------------------------------------------
    # SLIDE 2: PROBLEM STATEMENT & OBJECTIVES
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, BG_LIGHT)
    add_header(s2, "Problem Statement & Research Objectives", "Background & Motivation", 2)

    # Left Column: Problem & Objectives (Card)
    add_card(s2, Inches(0.8), Inches(1.5), Inches(6.0), Inches(5.4))
    tb_s2 = s2.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.6), Inches(5.1))
    tf_s2 = tb_s2.text_frame
    tf_s2.word_wrap = True

    p = tf_s2.paragraphs[0]
    p.text = "THE INDUSTRIAL DEFECT INSPECTION CHALLENGE"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    points = [
        ("Manual Inspection Bottlenecks: ", "Human visual quality control suffers from severe physiological fatigue, subjective inconsistency (80–85% repeatability), and high labor overhead."),
        ("The 'Unseen Defect' Dilemma: ", "Physical manufacturing defects are rare (<1-2%), unpredictable, and morphologically unbounded. Supervised binary classifiers fail completely because novel defect types cannot be collected a priori."),
        ("Normal-Only Training Regimen: ", "Requires one-class / unsupervised learning where models train exclusively on defect-free nominal components to construct a boundary of normalcy."),
        ("Core Project Objectives: ", "\n  1. Benchmark 4 paradigms: Handcrafted DIP vs ConvAE vs PatchCore vs PaDiM.\n  2. Rigorous Optimization Audit: Disprove/verify if numerical weight optimizers transfer to physical defect separation.\n  3. Edge Network Feasibility: Measure compression trade-offs under real-time simulated bandwidth and latency constraints.")
    ]
    for bold_pre, body in points:
        p_pt = tf_s2.add_paragraph()
        p_pt.space_before = Pt(8)
        run_b = p_pt.add_run()
        run_b.text = bold_pre
        run_b.font.bold = True
        run_b.font.size = Pt(10.5)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(10)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: Visual (Nominal vs Defective Bottle)
    add_card(s2, Inches(7.0), Inches(1.5), Inches(5.533), Inches(5.4))
    img_s2_path = os.path.join(FIG_DIR, 'slide02_normal_vs_defective.png')
    if os.path.exists(img_s2_path):
        s2.shapes.add_picture(img_s2_path, Inches(7.15), Inches(1.75), width=Inches(5.233))

    tb_s2_note = s2.shapes.add_textbox(Inches(7.15), Inches(5.4), Inches(5.233), Inches(1.3))
    tf_s2_n = tb_s2_note.text_frame
    tf_s2_n.word_wrap = True
    p_n1 = tf_s2_n.paragraphs[0]
    p_n1.text = "CORE SCIENTIFIC MOTIVATION:"
    p_n1.font.bold = True
    p_n1.font.size = Pt(10)
    p_n1.font.color.rgb = ACCENT_CORAL

    p_n2 = tf_s2_n.add_paragraph()
    p_n2.text = "The anomaly detector must identify arbitrary, fine-grained physical defects (structural cracks, contamination, missing components) purely by detecting statistical divergence from nominal training images."
    p_n2.font.size = Pt(9.5)
    p_n2.font.color.rgb = TEXT_SLATE
    p_n2.space_before = Pt(2)

    set_speaker_notes(s2, """SLIDE 2: PROBLEM STATEMENT & OBJECTIVES (Time: 1:00 - 2:00)
- What to Explain: Outline the industrial reality—modern manufacturing demands 100% defect inspection at line speeds, but defects are rare (<1-2%) and unpredictable.
- Key Technical Points: Supervised classifiers cannot work because you cannot train on defect types that haven't occurred yet. Normal-only training builds a statistical boundary of normalcy.
- How to Interpret Visual: Point to the right visual: left is a pristine bottle from the training set; middle is an unseen test sample with a structural crack (broken_large); right is the ground-truth pixel mask.
- Evaluator Questions:
  * Q: Why not use simple data augmentation or GANs to generate defects?
  * A: GANs and synthetic augmentations introduce synthetic artifacts and cannot model all real-world physical failure modes, leading to false positives.""")

    print("Building Slide 3: Dataset & Methodology...")
    # -------------------------------------------------------------
    # SLIDE 3: DATASET & OVERALL METHODOLOGY
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, BG_LIGHT)
    add_header(s3, "Dataset Scope & System Architecture", "Methodology & Pipeline", 3)

    # Left Column: Dataset Scope
    add_card(s3, Inches(0.8), Inches(1.5), Inches(5.2), Inches(5.4))
    tb_s3 = s3.shapes.add_textbox(Inches(0.95), Inches(1.65), Inches(4.9), Inches(5.1))
    tf_s3 = tb_s3.text_frame
    tf_s3.word_wrap = True

    p = tf_s3.paragraphs[0]
    p.text = "MVTEC ANOMALY DETECTION DATASET"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    dataset_points = [
        ("12 Evaluated Categories: ", "7 Rigid Objects (bottle, cable, capsule, hazelnut, metal_nut, screw, toothbrush, transistor) + 4 Structural Textures (carpet, grid, leather, tile)."),
        ("Strict Normal-Only Protocol: ", "1,389 Normal Training Images. Exactly 0 defective images exposed during model training or parameter estimation."),
        ("Exhaustive Test Split: ", "679 Test Images (200 nominal + 479 defective) spanning 65 distinct physical defect subtypes."),
        ("100% Ground Truth Coverage: ", "Pixel-precise binary segmentation masks provided for all 479 defective test images."),
        ("Scientific Integrity Audit: ", "Pill, Wood, and Zipper categories were omitted due to corrupted upstream archive checksums; fully documented with zero data leakage.")
    ]
    for b_pre, body in dataset_points:
        p_pt = tf_s3.add_paragraph()
        p_pt.space_before = Pt(8)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(10.5)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(9.5)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: Overall System Architecture (Figure 1)
    add_card(s3, Inches(6.2), Inches(1.5), Inches(6.333), Inches(5.4))
    img_s3_path = os.path.join(FIG_DIR, 'slide03_architecture.png')
    if os.path.exists(img_s3_path):
        s3.shapes.add_picture(img_s3_path, Inches(6.35), Inches(1.7), width=Inches(6.033))

    tb_s3_cap = s3.shapes.add_textbox(Inches(6.35), Inches(5.85), Inches(6.033), Inches(0.9))
    tf_s3_c = tb_s3_cap.text_frame
    tf_s3_c.word_wrap = True
    p_c = tf_s3_c.paragraphs[0]
    p_c.text = "Figure: End-to-end dataflow showing parallel inspection paradigms (DIP, ConvAE, PatchCore, PaDiM), followed by min-max normalization, hybrid score fusion, and dual image/pixel evaluation."
    p_c.font.size = Pt(9)
    p_c.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s3, """SLIDE 3: DATASET & METHODOLOGY (Time: 2:00 - 3:00)
- What to Explain: Detail the MVTec AD dataset structure across 12 evaluated categories. Explain the overall multi-paradigm pipeline shown in the architecture figure.
- Key Technical Points: 1,389 training images (all normal), 679 test images (200 normal, 479 defective). 65 defect subtypes.
- Highlight Integrity: Openly disclose that Pill, Wood, and Zipper were omitted due to archive corruption. Never pretend an experiment ran if it did not.
- Evaluator Questions:
  * Q: How did you ensure test labels did not leak into training?
  * A: Training data only contains the 'train/good' directory. Feature extractors and covariance matrices are fit solely on training data.""")

    print("Building Slide 4: Digital Image Processing...")
    # -------------------------------------------------------------
    # SLIDE 4: DIGITAL IMAGE PROCESSING & BASELINES
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, BG_LIGHT)
    add_header(s4, "Digital Image Processing & Classical Baselines", "Handcrafted Feature Engineering", 4)

    # Left Column: Features & Scorer
    add_card(s4, Inches(0.8), Inches(1.5), Inches(5.8), Inches(5.4))
    tb_s4 = s4.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.4), Inches(5.1))
    tf_s4 = tb_s4.text_frame
    tf_s4.word_wrap = True

    p = tf_s4.paragraphs[0]
    p.text = "HANDCRAFTED STATISTICAL & TEXTURE DESCRIPTORS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    dip_points = [
        ("7 Statistical & GLCM Features: ", "Mean Intensity (\u03bc), Standard Deviation (\u03c3), Skewness (\u03b3\u2081), Kurtosis (\u03b2\u2082), GLCM Energy, Information Entropy, and GLCM Contrast."),
        ("Centroid & Covariance Baseline: ", "Extracted vectors across nominal training images establish normal reference centroids \u03bc_ref and covariance \u03a3."),
        ("Classical Scoring Paradigms: ", "\n  \u2022 Normalized Distance: S(x) = \u2211 w_i |f_i(x) - \u03bc_i| / \u03c3_i\n  \u2022 Mahalanobis Distance: D_M(x) = \u221a[(f - \u03bc)^T \u03a3\u207b\u00b9 (f - \u03bc)]\n  \u2022 One-Class SVM (OC-SVM): RBF boundary with \u03bd=0.05\n  \u2022 Isolation Forest: 100 recursive partitioning trees"),
        ("Baseline Performance: ", "Baseline Equal-7 weights achieves 0.5758 Macro AUROC; Mahalanobis achieves 0.5927; OC-SVM achieves 0.5781; Isolation Forest achieves 0.5313.")
    ]
    for b_pre, body in dip_points:
        p_pt = tf_s4.add_paragraph()
        p_pt.space_before = Pt(8)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(10.5)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(9.5)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: Visuals (DIP Pipeline + Feature AUROC)
    add_card(s4, Inches(6.8), Inches(1.5), Inches(5.733), Inches(5.4))
    img_pipe = os.path.join(FIG_DIR, 'slide04_dip_pipeline.png')
    img_f_auroc = os.path.join(FIG_DIR, 'slide04_feature_auroc.png')

    if os.path.exists(img_pipe):
        s4.shapes.add_picture(img_pipe, Inches(6.95), Inches(1.65), width=Inches(5.433))
    if os.path.exists(img_f_auroc):
        s4.shapes.add_picture(img_f_auroc, Inches(7.4), Inches(3.85), width=Inches(4.5))

    tb_s4_cap = s4.shapes.add_textbox(Inches(6.95), Inches(6.3), Inches(5.433), Inches(0.5))
    tf_s4_c = tb_s4_cap.text_frame
    tf_s4_c.word_wrap = True
    p_c4 = tf_s4_c.paragraphs[0]
    p_c4.text = "Figure: Classical DIP feature extraction flow & individual feature discriminability (AUROC)."
    p_c4.font.size = Pt(8.5)
    p_c4.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s4, """SLIDE 4: DIGITAL IMAGE PROCESSING (Time: 3:00 - 4:00)
- What to Explain: Describe the 7 handcrafted classical features extracted from images (mean, variance, skewness, kurtosis, energy, entropy, contrast). Explain the baseline scoring rules: Mahalanobis distance, OC-SVM, and Isolation Forest.
- Key Technical Points: Handcrafted features are computationally cheap (~28-32 ms on CPU) but achieve modest discriminability (0.5758 to 0.5927 AUROC).
- How to Interpret Visual: The lower plot shows individual feature AUROC on bottle. Contrast and entropy show moderate signal, while higher-order moments provide little separation.
- Evaluator Questions:
  * Q: Why did Mahalanobis outperform simple Euclidean distance?
  * A: Mahalanobis accounts for cross-feature correlations and variance scaling, which Euclidean distance ignores.""")

    print("Building Slide 5: Deep Learning Models...")
    # -------------------------------------------------------------
    # SLIDE 5: DEEP LEARNING ARCHITECTURES
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, BG_LIGHT)
    add_header(s5, "Deep Learning Inspection Paradigms", "Modern Unsupervised Architectures", 5)

    # 3 Horizontal Cards for the 3 DL Paradigms
    dl_cols = [
        ("CONVOLUTIONAL AUTOENCODER",
         "Reconstruction-Based Detection",
         ACCENT_NAVY,
         [("Bottleneck Manifold: ", "Encoder compresses 256\u00d7256 inputs to a compact latent bottleneck (d_z = 64)."),
          ("Multi-Scale Objective: ", "L = \u03b1 L_MSE + \u03b2 (1 - SSIM) + \u03b3 L_Sobel to enforce structural edge fidelity."),
          ("Scoring: ", "Reconstruction residual error highlights anomalous pixels."),
          ("Attributes: ", "Fastest inference (18 ms, ~55 FPS); Bottle AUROC: 0.9333; Macro AUROC: 0.6149.")]),

        ("PATCHCORE (SOTA BENCHMARK)",
         "Memory-Bank Nearest-Neighbor",
         ACCENT_BLUE,
         [("Patch Embeddings: ", "Extracts neighborhood-aware patch features from pretrained ResNet-18 (Layers 2 & 3)."),
          ("Minimax Coreset: ", "Greedy subsampling retains 5% of memory tokens without sacrificing detection resolution."),
          ("Scoring: ", "Nearest-neighbor distance weighted by local cluster sparsity."),
          ("Attributes: ", "SOTA fidelity: 0.9769 Image AUROC, 0.9721 Pixel AUROC; 85 ms latency.")]),

        ("PADIM (GAUSSIAN MODELLING)",
         "Localized Multivariate Gaussians",
         ACCENT_TEAL,
         [("Embedding Reduction: ", "Concatenates multi-layer features and randomly samples 100 channel dimensions."),
          ("Spatial Gaussians: ", "Fits a location-specific Gaussian N(\u03bc_(i,j), \u03a3_(i,j)) for every spatial grid cell."),
          ("Scoring: ", "Pixel Mahalanobis distance yields continuous localization heatmaps."),
          ("Attributes: ", "Superior localization: 0.9619 Pixel AUROC, 0.9082 Image AUROC; 95 ms latency.")])
    ]

    card_w5 = Inches(3.75)
    card_h5 = Inches(5.4)
    start_x5 = Inches(0.8)
    gap_x5 = Inches(0.24)

    for i, (col_title, sub_title, border_c, items) in enumerate(dl_cols):
        cx = start_x5 + i * (card_w5 + gap_x5)
        add_card(s5, cx, Inches(1.5), card_w5, card_h5, bg_color=CARD_WHITE, border_color=border_c, border_width=1.5)

        tb = s5.shapes.add_textbox(cx + Inches(0.15), Inches(1.65), card_w5 - Inches(0.3), card_h5 - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = col_title
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = border_c

        p_s = tf.add_paragraph()
        p_s.text = sub_title
        p_s.font.size = Pt(9.5)
        p_s.font.color.rgb = TEXT_MUTED
        p_s.space_after = Pt(8)

        for b_hdr, text in items:
            p_i = tf.add_paragraph()
            p_i.space_before = Pt(8)
            r_b = p_i.add_run()
            r_b.text = b_hdr
            r_b.font.bold = True
            r_b.font.size = Pt(10)
            r_b.font.color.rgb = TEXT_DARK
            r_t = p_i.add_run()
            r_t.text = text
            r_t.font.size = Pt(9.5)
            r_t.font.color.rgb = TEXT_SLATE

    set_speaker_notes(s5, """SLIDE 5: DEEP LEARNING MODELS (Time: 4:00 - 5:00)
- What to Explain: Walk through the three deep learning paradigms:
  1. Autoencoder: Learns a latent compression of normalcy. Anomalies cannot be reconstructed, leaving high residual errors.
  2. PatchCore: Extracts patch-level feature vectors from ResNet-18, applies 5% greedy coreset subsampling, and scores anomalies using nearest-neighbor search.
  3. PaDiM: Fits a localized Gaussian distribution at every spatial position across 100 random dimensions, scoring pixels via Mahalanobis distance.
- Evaluator Questions:
  * Q: Why does PatchCore use 5% coreset rather than 100% memory?
  * A: 100% memory bank creates prohibitive inference latency (~1,500 ms). Coreset subsampling preserves 99.8% of detection accuracy while reducing memory and search latency by 20x.""")

    print("Building Slide 6: Experimental Setup...")
    # -------------------------------------------------------------
    # SLIDE 6: EXPERIMENTAL SETUP & EVALUATION PROTOCOL
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, BG_LIGHT)
    add_header(s6, "Rigorous Experimental Protocol & Setup", "Methodology & Reproducibility", 6)

    # Left Column: Protocol & Metrics
    add_card(s6, Inches(0.8), Inches(1.5), Inches(5.8), Inches(5.4))
    tb_s6 = s6.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.4), Inches(5.1))
    tf_s6 = tb_s6.text_frame
    tf_s6.word_wrap = True

    p = tf_s6.paragraphs[0]
    p.text = "UNSUPERVISED EVALUATION STANDARDS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    setup_points = [
        ("Strict Normal-Only Protocol: ", "Zero defective images used in training. Training set contains exclusively nominal items (1,389 images across 12 categories)."),
        ("Dual-Fidelity Evaluation Metrics: ", "\n  \u2022 Image-Level AUROC: Measures classification accuracy across all decision thresholds, independent of class imbalance.\n  \u2022 Pixel-Level AUROC: Measures spatial localization accuracy against human ground-truth masks.\n  \u2022 Optimal F1-Score: Evaluates operational precision/recall balance at the optimal F1 threshold."),
        ("No Test Label Overfitting: ", "Thresholds and hyperparameters were not fit on the test set; model checkpoints selected strictly on training convergence criteria.")
    ]
    for b_pre, body in setup_points:
        p_pt = tf_s6.add_paragraph()
        p_pt.space_before = Pt(10)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(10.5)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(9.5)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: Compute Environment & Execution Scale
    add_card(s6, Inches(6.8), Inches(1.5), Inches(5.733), Inches(5.4))
    tb_s6_r = s6.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.333), Inches(5.1))
    tf_s6_r = tb_s6_r.text_frame
    tf_s6_r.word_wrap = True

    p_r = tf_s6_r.paragraphs[0]
    p_r.text = "HARDWARE INFRASTRUCTURE & EXPERIMENT SCALE"
    p_r.font.size = Pt(11)
    p_r.font.bold = True
    p_r.font.color.rgb = ACCENT_TEAL

    hw_points = [
        ("Compute Infrastructure: ", "NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM, CUDA 12.1), Intel Core i7-13700H, 16GB DDR5 RAM."),
        ("Software Framework: ", "PyTorch 2.5.1+cu121, Torchvision, Scikit-learn 1.4, OpenCV 4.10, NumPy, SciPy, Python 3.11+."),
        ("Massive Experimental Scope (736 Total Runs): ", "\n  \u2022 292 Baseline, Ablation & Architecture Runs: Evaluated across 12 industrial categories (AE loss/depth ablations, PatchCore coresets, PaDiM dimensions, hybrid ensembles).\n  \u2022 444 Optimization Parameter Sweep Runs: 5 parameter axes (OPT-P1 to OPT-P5) across 4 mathematical solvers to test synthetic optimization transfer.")
    ]
    for b_pre, body in hw_points:
        p_pt = tf_s6_r.add_paragraph()
        p_pt.space_before = Pt(10)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(10.5)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(9.5)
        run_txt.font.color.rgb = TEXT_SLATE

    set_speaker_notes(s6, """SLIDE 6: EXPERIMENTAL SETUP (Time: 5:00 - 6:00)
- What to Explain: Outline the rigorous evaluation protocol and infrastructure. Clarify the difference between image-level AUROC and pixel-level AUROC.
- Key Technical Points: 736 executed runs (292 baseline/ablation runs + 444 parameter sweeps). RTX 4060 GPU with PyTorch 2.5.1.
- Research Integrity: Mention that test labels were never used for model selection or hyperparameter tuning.
- Evaluator Questions:
  * Q: Why is AUROC preferred over Accuracy or F1 in anomaly detection?
  * A: Industrial defect datasets have severe class imbalance (~80% normal, 20% defective). Standard accuracy can be misleading (predicting all normal yields 80% accuracy). AUROC evaluates true positive vs false positive rate across all thresholds threshold-independently.""")

    print("Building Slide 7: DIP & Optimization Results...")
    # -------------------------------------------------------------
    # SLIDE 7: DIP & OPTIMIZATION RESULTS: THE NEGATIVE DISCOVERY
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, BG_LIGHT)
    add_header(s7, "DIP Optimization: A Critical Negative Result", "Empirical Findings & Theoretical Disproof", 7)

    # Left Column: The Empirical Reality
    add_card(s7, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb_s7 = s7.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf_s7 = tb_s7.text_frame
    tf_s7.word_wrap = True

    p = tf_s7.paragraphs[0]
    p.text = "SYNTHETIC OPTIMIZATION FAILS ON REAL DEFECTS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CORAL

    opt_points = [
        ("The Optimization Hypothesis: ", "Can numerical optimizers (SLSQP, CG, L-BFGS-B, Trust Region) tune the 7 feature weights against synthetic Gaussian noise to improve defect separation?"),
        ("444 Parameter Sweeps (OPT-P1 to P5): ", "Swept finite difference step (\u03b5 \u2208 [10\u207b\u2075, 0.5]), noise scale (\u03c3 \u2208 [0.01, 0.50]), starting points, and iterations across 12 categories."),
        ("Artificial Synthetic Convergence: ", "All optimizers converged easily to >0.9900 AUROC on synthetic noise anomalies."),
        ("Zero Transfer to Real Physical Defects: ", "When evaluated on real MVTec test defects, optimized AUROC remained exactly 0.5758—identical to unweighted baseline!"),
        ("Scientific Takeaway: ", "Synthetic Gaussian noise is isotropic and cannot capture physical defect manifolds (cracks, contamination). Handcrafted global features lack the representational capacity to separate real defects without real defect priors.")
    ]
    for b_pre, body in opt_points:
        p_pt = tf_s7.add_paragraph()
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

    # Right Column: Visual (Optimization Sweep Curves)
    add_card(s7, Inches(6.6), Inches(1.5), Inches(5.933), Inches(5.4))
    img_opt = os.path.join(FIG_DIR, 'slide07_optimization.png')
    if os.path.exists(img_opt):
        s7.shapes.add_picture(img_opt, Inches(6.75), Inches(1.65), width=Inches(5.633))

    tb_s7_cap = s7.shapes.add_textbox(Inches(6.75), Inches(5.85), Inches(5.633), Inches(0.9))
    tf_s7_c = tb_s7_cap.text_frame
    tf_s7_c.word_wrap = True
    p_c7 = tf_s7_c.paragraphs[0]
    p_c7.text = "Figure: 444-run parameter sweep across 5 axes (OPT-P1 to OPT-P5) proving synthetic convergence (>0.99) yields zero transfer gain (0.5758) on real industrial defects."
    p_c7.font.size = Pt(8.5)
    p_c7.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s7, """SLIDE 7: DIP OPTIMIZATION & NEGATIVE RESULT (Time: 6:00 - 7:00)
- What to Explain: Present our crucial negative result. Many researchers claim optimization tunes feature weights, but we tested this across 444 runs and proved it fails to transfer to real defects.
- Key Technical Points: Solvers (SLSQP, CG, L-BFGS-B, Trust Region) achieve >0.99 AUROC on synthetic noise, but 0.5758 on real defects (identical to baseline equal weights).
- Scientific Significance: Reporting negative results with thorough experimental evidence is vital for scientific integrity. It proves that synthetic noise cannot substitute for real defect priors.
- Evaluator Questions:
  * Q: Why did optimizing on synthetic noise not help on real defects?
  * A: Synthetic noise affects pixels independently (Gaussian perturbations), whereas physical defects have spatial structure, texture disruptions, and boundary edges that global moments cannot capture.""")

    print("Building Slide 8: Deep Learning Results...")
    # -------------------------------------------------------------
    # SLIDE 8: DEEP LEARNING RESULTS
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, BG_LIGHT)
    add_header(s8, "Deep Learning Benchmark & Performance", "Quantitative 12-Category Evaluation", 8)

    # Left Column: Macro Table & Insights
    add_card(s8, Inches(0.8), Inches(1.5), Inches(5.4), Inches(5.4))
    tb_s8 = s8.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.0), Inches(5.1))
    tf_s8 = tb_s8.text_frame
    tf_s8.word_wrap = True

    p = tf_s8.paragraphs[0]
    p.text = "12-CATEGORY MACRO BENCHMARK"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    # Small table of models
    dl_rows = [
        ("PatchCore (ResNet-18, 5%):", "0.9769 Image AUROC  |  0.9721 Pixel AUROC\nF1: 0.8221  |  Inference: 85.0 ms  |  5 Perfect Cats"),
        ("PaDiM (ResNet-18, 100d):", "0.9082 Image AUROC  |  0.9619 Pixel AUROC\nF1: 0.8203  |  Inference: 95.0 ms  |  Strong Localization"),
        ("Conv Autoencoder (5-Level):", "0.6149 Image AUROC  |  0.7220 Pixel AUROC\nF1: 0.2899  |  Inference: 18.0 ms (~55 FPS)"),
        ("Key Architectural Discoveries:", "\n  \u2022 PatchCore Sovereign: Achieves perfect 1.0000 AUROC on 5 of 12 categories (bottle, hazelnut, leather, metal_nut, transistor).\n  \u2022 PaDiM Localization Power: Superior spatial precision (0.9619 Pixel AUROC) with no search phase.\n  \u2022 ConvAE Bottleneck: 18 ms throughput is suitable for high-speed edge screening, achieving 0.9333 on bottle with 5-level loss, but struggles on complex textures.")
    ]
    for b_pre, body in dl_rows:
        p_pt = tf_s8.add_paragraph()
        p_pt.space_before = Pt(6)
        run_b = p_pt.add_run()
        run_b.text = b_pre
        run_b.font.bold = True
        run_b.font.size = Pt(10)
        run_b.font.color.rgb = TEXT_DARK
        run_txt = p_pt.add_run()
        run_txt.text = body
        run_txt.font.size = Pt(9)
        run_txt.font.color.rgb = TEXT_SLATE

    # Right Column: Visual (slide08_dl_benchmark.png)
    add_card(s8, Inches(6.4), Inches(1.5), Inches(6.133), Inches(5.4))
    img_dl = os.path.join(FIG_DIR, 'slide08_dl_benchmark.png')
    if os.path.exists(img_dl):
        s8.shapes.add_picture(img_dl, Inches(6.55), Inches(1.8), width=Inches(5.833))

    tb_s8_cap = s8.shapes.add_textbox(Inches(6.55), Inches(5.85), Inches(5.833), Inches(0.9))
    tf_s8_c = tb_s8_cap.text_frame
    tf_s8_c.word_wrap = True
    p_c8 = tf_s8_c.paragraphs[0]
    p_c8.text = "Figure: Comparison of standalone Deep Learning paradigms across Image AUROC, Pixel AUROC, and Inference Latency on NVIDIA GeForce RTX 4060 GPU."
    p_c8.font.size = Pt(8.5)
    p_c8.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s8, """SLIDE 8: DEEP LEARNING RESULTS (Time: 7:00 - 8:00)
- What to Explain: Compare the three deep learning paradigms across 12 MVTec categories.
- Key Technical Points:
  * PatchCore is the top performer with 0.9769 Image AUROC and 0.9721 Pixel AUROC. It achieved perfect 1.0000 AUROC on 5 categories.
  * PaDiM is the top localization model at 0.9619 Pixel AUROC, modeling spatial correlations directly.
  * Autoencoder is the fastest (18 ms), making it attractive for high-speed edge inspection, but achieves 0.6149 macro AUROC (though reaching 0.9333 on bottle with 5-level loss).
- Evaluator Questions:
  * Q: Why did ConvAE achieve 0.9333 on bottle but only 0.6149 macro?
  * A: Autoencoders excel on uniform, rigid objects like bottles, but struggle to reconstruct complex non-rigid textures like carpet or grid without blurring.""")

    print("Building Slide 9: Hybrid Model Results...")
    # -------------------------------------------------------------
    # SLIDE 9: HYBRID MODEL RESULTS
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, BG_LIGHT)
    add_header(s9, "Multi-Paradigm Hybrid Score Fusion", "Ensemble Fusion & Reliability", 9)

    # Left Column: Hybrid Formulations & Operational Impact
    add_card(s9, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.4))
    tb_s9 = s9.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.2), Inches(5.1))
    tf_s9 = tb_s9.text_frame
    tf_s9.word_wrap = True

    p = tf_s9.paragraphs[0]
    p.text = "MULTI-PARADIGM ENSEMBLE FUSION"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    hy_points = [
        ("Score Standardization: ", "Raw anomaly scores are min-max normalized across training sets: S\u0302_m(x) = (S_m(x) - \u03bc_m) / \u03c3_m."),
        ("Three Ensembling Strategies: ", "\n  \u2022 Hybrid-Mean (HY-01): S_mean = \u2153 (S_AE + S_PC + S_PaDiM) \u2192 0.9586 AUROC | F1: 0.8186\n  \u2022 Hybrid-Max (HY-02): S_max = max(S_AE, S_PC, S_PaDiM) \u2192 0.9421 AUROC | F1: 0.8190\n  \u2022 Hybrid-Weighted (HY-03): S_w = 0.20 S_AE + 0.40 S_PC + 0.40 S_PaDiM \u2192 0.9626 AUROC | F1: 0.8180"),
        ("Why Hybrid-Weighted Wins Operationally: ", "While standalone PatchCore has slightly higher macro AUROC (0.9769 vs 0.9626), HY-03 exhibits lower score variance and dampens single-model false alarm spikes (e.g. AE edge blur or PaDiM boundary variance)."),
        ("100% Defect Recall: ", "HY-03 secures 1.0000 recall across all 12 categories at the optimal operational threshold.")
    ]
    for b_pre, body in hy_points:
        p_pt = tf_s9.add_paragraph()
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

    # Right Column: Visual (slide09_hybrid_fusion.png)
    add_card(s9, Inches(6.6), Inches(1.5), Inches(5.933), Inches(5.4))
    img_hy = os.path.join(FIG_DIR, 'slide09_hybrid_fusion.png')
    if os.path.exists(img_hy):
        s9.shapes.add_picture(img_hy, Inches(6.75), Inches(1.8), width=Inches(5.633))

    tb_s9_cap = s9.shapes.add_textbox(Inches(6.75), Inches(5.85), Inches(5.633), Inches(0.9))
    tf_s9_c = tb_s9_cap.text_frame
    tf_s9_c.word_wrap = True
    p_c9 = tf_s9_c.paragraphs[0]
    p_c9.text = "Figure: Multi-paradigm ensemble schemes (Mean, Max, Weighted) compared against standalone architectures. HY-03 achieves 0.9626 AUROC with highest operational stability."
    p_c9.font.size = Pt(8.5)
    p_c9.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s9, """SLIDE 9: HYBRID MODEL RESULTS (Time: 8:00 - 9:00)
- What to Explain: Explain how multi-paradigm score fusion combines reconstruction error (AE), memory-bank nearest neighbor (PatchCore), and probabilistic Gaussian distance (PaDiM).
- Key Technical Points: Raw scores are standardized via min-max normalization. HY-03 allocates weights: 0.20 AE + 0.40 PatchCore + 0.40 PaDiM, achieving 0.9626 AUROC.
- Practical Value: In an industrial line, a single model may trigger a false alarm due to lighting or edge reflections. HY-03 acts as a voting consensus, suppressing false alarms and maintaining 100% recall.
- Evaluator Questions:
  * Q: Why give Autoencoder only 0.20 weight compared to 0.40 for PatchCore and PaDiM?
  * A: AE has lower macro AUROC (0.6149) and produces edge blur artifacts. Giving it 0.20 allows it to contribute fast global reconstruction signals without corrupting fine boundary decisions.""")

    print("Building Slide 10: Anomaly Detection Visualization...")
    # -------------------------------------------------------------
    # SLIDE 10: ANOMALY DETECTION VISUALIZATION
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, BG_LIGHT)
    add_header(s10, "Qualitative Defect Localization & Visual Analysis", "Spatial Heatmaps & Failure Mode Profiling", 10)

    # Top Summary Banner
    add_card(s10, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.55), bg_color=CARD_BLUE, border_color=BORDER_BLUE)
    tb_banner = s10.shapes.add_textbox(Inches(0.95), Inches(1.45), Inches(11.433), Inches(0.55))
    tf_b = tb_banner.text_frame
    tf_b.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_ban = tf_b.paragraphs[0]
    p_ban.text = "Visual Inspection Pipeline:  Original Input Image  \u2192  Ground Truth Defect Mask  \u2192  Autoencoder Error  \u2192  PatchCore Heatmap  \u2192  PaDiM Heatmap"
    p_ban.font.size = Pt(10)
    p_ban.font.bold = True
    p_ban.font.color.rgb = ACCENT_NAVY

    # Center Visual Grid (slide10_anomaly_visualization.png)
    add_card(s10, Inches(0.8), Inches(2.1), Inches(11.733), Inches(4.3))
    img_vis = os.path.join(FIG_DIR, 'slide10_anomaly_visualization.png')
    if os.path.exists(img_vis):
        s10.shapes.add_picture(img_vis, Inches(1.8), Inches(2.2), width=Inches(9.733))

    # Bottom caption / takeaway
    tb_s10_cap = s10.shapes.add_textbox(Inches(0.8), Inches(6.45), Inches(11.733), Inches(0.6))
    tf_s10_c = tb_s10_cap.text_frame
    tf_s10_c.word_wrap = True
    p_c10 = tf_s10_c.paragraphs[0]
    p_c10.text = "Observations: (Top) Severe structural crack (broken_large) isolated with sharp pixel IoU by PatchCore and PaDiM. (Middle) Surface contamination pinpointed with near 100% precision. (Bottom - Failure Case) Subtle edge chip (broken_small) shows Autoencoder edge blur halo false alarms, whereas PatchCore successfully localizes the chip."
    p_c10.font.size = Pt(9)
    p_c10.font.color.rgb = TEXT_SLATE

    set_speaker_notes(s10, """SLIDE 10: QUALITATIVE VISUALIZATION (Time: 9:00 - 10:00)
- What to Explain: Walk the evaluators through actual qualitative defect heatmaps from the MVTec AD bottle category:
  1. Row 1: Structural Fracture (broken_large). Both PatchCore and PaDiM create sharp, pinpoint heatmaps exactly overlaying the ground-truth crack.
  2. Row 2: Localized Contamination. High-contrast foreign particles are detected with near 100% precision.
  3. Row 3: Failure Mode / Challenging Case (broken_small). Point out the Autoencoder column: it exhibits diffuse edge halos along normal bottle boundaries, triggering false alarms. PatchCore, however, remains robust and isolates the small defect.
- Evaluator Questions:
  * Q: Why does the Autoencoder produce false-positive halos along edges?
  * A: Downsampling through convolutional strides loses high-frequency phase information. Reconstructing high-gradient edge contours accurately is notoriously difficult for ConvAEs.""")

    print("Building Slide 11: Network Compression...")
    # -------------------------------------------------------------
    # SLIDE 11: NETWORK COMPRESSION & OVERALL DISCUSSION
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, BG_LIGHT)
    add_header(s11, "Edge Network Transmission & Denoising Discovery", "Computer Networks & Edge Deployment", 11)

    # Left Column: Latency Breakdown & Findings
    add_card(s11, Inches(0.8), Inches(1.5), Inches(5.4), Inches(5.4))
    tb_s11 = s11.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.0), Inches(5.1))
    tf_s11 = tb_s11.text_frame
    tf_s11.word_wrap = True

    p = tf_s11.paragraphs[0]
    p.text = "SIMULATED EDGE NETWORK TRANSMISSION"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    net_points = [
        ("Simulated Factory Environment: ", "10 Mbps industrial edge uplink bandwidth, 50 ms Round-Trip Time (RTT) latency."),
        ("Transmission Performance Matrix: ", "\n  \u2022 Original (PNG): 88.8 KB | Latency: 157.8 ms | AUROC: 0.7515\n  \u2022 JPEG Q95: 18.8 KB (4.7\u00d7) | Latency: 98.4 ms | AUROC: 0.7788\n  \u2022 JPEG Q75: 7.9 KB (11.2\u00d7) | Latency: 89.9 ms (43.0% drop) | AUROC: 0.7970\n  \u2022 JPEG Q50: 5.6 KB (15.9\u00d7) | Latency: 86.7 ms | AUROC: 0.7455 (Degraded)"),
        ("The 'Edge Denoising Effect' Discovery: ", "JPEG Q75 yields a 43.0% latency drop AND improves AUROC from 0.7515 to 0.7970 (+4.55%)! Moderate DCT quantization filters out high-frequency sensor noise without blurring defect edges."),
        ("Limitations Acknowledged: ", "Simulation assumes constant 10 Mbps bandwidth without packet jitter; real-world industrial Ethernet/5G requires QoS buffering.")
    ]
    for b_pre, body in net_points:
        p_pt = tf_s11.add_paragraph()
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

    # Right Column: Visual (slide11_network_tradeoff.png)
    add_card(s11, Inches(6.4), Inches(1.5), Inches(6.133), Inches(5.4))
    img_net = os.path.join(FIG_DIR, 'slide11_network_tradeoff.png')
    if os.path.exists(img_net):
        s11.shapes.add_picture(img_net, Inches(6.55), Inches(1.8), width=Inches(5.833))

    tb_s11_cap = s11.shapes.add_textbox(Inches(6.55), Inches(5.85), Inches(5.833), Inches(0.9))
    tf_s11_c = tb_s11_cap.text_frame
    tf_s11_c.word_wrap = True
    p_c11 = tf_s11_c.paragraphs[0]
    p_c11.text = "Figure: Network compression trade-off showing 43.0% total latency reduction and the unexpected +4.55% AUROC gain at JPEG Q75 via high-frequency sensor noise suppression."
    p_c11.font.size = Pt(8.5)
    p_c11.font.color.rgb = TEXT_MUTED

    set_speaker_notes(s11, """SLIDE 11: NETWORK COMPRESSION & DISCUSSION (Time: 10:00 - 11:00)
- What to Explain: Present the computer networks component. Raw PNG transmission over a 10 Mbps link takes 157.8 ms end-to-end, bottlenecking 10 Hz factory lines.
- Key Technical Points: JPEG Q75 achieves an 11.2x file size reduction (7.9 KB vs 88.8 KB), slashing latency by 43.0% down to 89.9 ms (~11 FPS).
- The Denoising Discovery: Explain that JPEG Q75 actually boosted AUROC from 0.7515 to 0.7970 (+4.55%). The lossy DCT quantization acts as an edge-preserving low-pass filter, suppressing camera sensor grain while leaving defect boundaries intact.
- Caveat: JPEG Q50 drops AUROC to 0.7455 because severe 8x8 block artifacts distort fine defect edges.
- Evaluator Questions:
  * Q: Are these measurements from a physical testbed or simulated?
  * A: Transmission latency is rigorously calculated using analytical network simulation models (10 Mbps bandwidth, 50 ms RTT); encoding, decoding, and GPU inference times were physically measured on our RTX 4060 testbed.""")

    print("Building Slide 12: Conclusion & Thank You...")
    # -------------------------------------------------------------
    # SLIDE 12: CONCLUSION, FUTURE SCOPE & THANK YOU
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, BG_LIGHT)
    add_header(s12, "Summary of Contributions & Future Scope", "Conclusion & Research Impact", 12)

    # 3 Summary Cards
    concl_cards = [
        ("CORE SCIENTIFIC FINDINGS",
         ACCENT_NAVY,
         [("Benchmark Sovereignty: ", "PatchCore (0.9769 Image AUROC) and PaDiM (0.9619 Pixel AUROC) establish SOTA fidelity across 12 MVTec categories."),
          ("Negative Result Proved: ", "Theoretical & empirical disproof of synthetic DIP optimization across 444 runs; synthetic noise cannot substitute for defect priors."),
          ("Edge Denoising Sweet Spot: ", "JPEG Q75 delivers 43.0% lower latency with +4.55% higher AUROC via sensor noise attenuation.")]),

        ("INDUSTRIAL DEPLOYMENT GUIDELINES",
         ACCENT_BLUE,
         [("High-Precision Production: ", "Deploy PatchCore or HY-03 on GPU edge servers (RTX 4060) for critical inspection lines (85–140 ms, 7–12 parts/sec)."),
          ("High-Throughput Screening: ", "Deploy 5-level ConvAE (18 ms, ~55 FPS) on low-power edge nodes for high-speed anomaly triage."),
          ("Ensemble Fault Tolerance: ", "Utilize HY-03 weighted fusion to prevent false alarm shutdowns in high-vibration manufacturing environments.")]),

        ("FUTURE RESEARCH ROADMAP",
         ACCENT_TEAL,
         [("Vision-Language Models: ", "Investigate zero-shot anomaly detection using CLIP and WinCLIP without requiring category-specific training images."),
          ("TensorRT Edge Quantization: ", "Quantize PatchCore coreset embeddings to INT8/FP16 for sub-10ms inference on NVIDIA Jetson Orin modules."),
          ("Wireless 5G TSN Validation: ", "Evaluate transmission over physical 5G Time-Sensitive Networks in active industrial production facilities.")])
    ]

    card_w12 = Inches(3.75)
    card_h12 = Inches(3.6)
    start_x12 = Inches(0.8)
    gap_x12 = Inches(0.24)

    for i, (title_c, border_c, points_c) in enumerate(concl_cards):
        cx = start_x12 + i * (card_w12 + gap_x12)
        add_card(s12, cx, Inches(1.5), card_w12, card_h12, bg_color=CARD_WHITE, border_color=border_c, border_width=1.5)

        tb = s12.shapes.add_textbox(cx + Inches(0.15), Inches(1.65), card_w12 - Inches(0.3), card_h12 - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = title_c
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = border_c
        p0.space_after = Pt(8)

        for b_hdr, text in points_c:
            p_i = tf.add_paragraph()
            p_i.space_before = Pt(6)
            r_b = p_i.add_run()
            r_b.text = b_hdr
            r_b.font.bold = True
            r_b.font.size = Pt(9.5)
            r_b.font.color.rgb = TEXT_DARK
            r_t = p_i.add_run()
            r_t.text = text
            r_t.font.size = Pt(9)
            r_t.font.color.rgb = TEXT_SLATE

    # Bottom Thank You & Q&A Banner
    add_card(s12, Inches(0.8), Inches(5.3), Inches(11.733), Inches(1.6), bg_color=BG_DARK, border_color=ACCENT_BLUE, border_width=1.5)
    tb_ty = s12.shapes.add_textbox(Inches(1.0), Inches(5.4), Inches(11.333), Inches(1.4))
    tf_ty = tb_ty.text_frame
    tf_ty.word_wrap = True

    p_ty = tf_ty.paragraphs[0]
    p_ty.text = "THANK YOU!   |   QUESTIONS & TECHNICAL DISCUSSION"
    p_ty.font.size = Pt(18)
    p_ty.font.bold = True
    p_ty.font.color.rgb = RGBColor(147, 197, 253)

    p_subty = tf_ty.add_paragraph()
    p_subty.text = "Candidate: Rahul Dewangan  |  Guide: [INSERT GUIDE NAME]  |  Dept. of Computer Science & Engineering\nOpen-Source GitHub Repository: https://github.com/Rahul-dewangan01/Hybrid-Industrial-Visual-Anomaly-Detection"
    p_subty.font.size = Pt(10.5)
    p_subty.font.color.rgb = RGBColor(226, 232, 240)
    p_subty.space_before = Pt(6)

    set_speaker_notes(s12, """SLIDE 12: CONCLUSION & FUTURE WORK (Time: 11:00 - 12:00)
- What to Explain: Summarize the primary contributions of this B.Tech research capstone:
  1. PatchCore & PaDiM established gold-standard detection and localization.
  2. Disproved synthetic DIP optimization across 444 runs.
  3. Discovered the JPEG Q75 denoising effect for real-time edge network inspection.
- Future Scope: Outline practical next steps: INT8 TensorRT quantization for NVIDIA Jetson edge devices, foundation vision-language models (WinCLIP) for zero-shot inspection, and physical 5G wireless field trials.
- Closing: Thank the committee, supervisor, and evaluators, and invite technical questions.""")

    # Save PPTX
    prs.save(PPTX_PATH)
    print(f"Presentation successfully saved to: {PPTX_PATH}")


def convert_pptx_to_pdf():
    print("Converting PPTX to PDF via PowerPoint COM engine...")
    import win32com.client
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    # Open presentation in read-only mode
    deck = powerpoint.Presentations.Open(PPTX_PATH, WithWindow=False)
    # ppSaveAsPDF = 32
    deck.SaveAs(PDF_PATH, 32)
    deck.Close()
    powerpoint.Quit()
    print(f"PDF successfully exported to: {PDF_PATH}")


if __name__ == '__main__':
    create_presentation()
    convert_pptx_to_pdf()

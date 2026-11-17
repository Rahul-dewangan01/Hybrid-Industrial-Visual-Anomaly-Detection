"""
build_speaker_notes_docx.py
Generates the publication-quality Presentation_Speaker_Notes.docx
specifically tailored for IIIT Raichur academic evaluation:
- Team Members: Omkar Kendre (AD24B1033), Rahul Dewangan (AD24B1050), Govind Das (AD24B1021)
- Institution: Indian Institute of Information Technology Raichur (IIIT Raichur), Academic Year: 2026
- Strictly follows the 6-part academic structure across exactly 12 slides:
  1. Introduction
  2. Literature Survey (strictly 2021-2026 papers)
  3. Hypothesis (H1 to H4)
  4. Prove Your Hypothesis (Validation Matrix)
  5. Methodology (Overall System & DIP, DL & Hybrid, ACOMA, Computer Networks)
  6. Results (Quantitative Analysis, Qualitative & Network Results)
  7. Conclusion & Thank You
- Distinguishes the 3 course contributions: DIP, ACOMA, COMPUTER NETWORKS.
- NO supervisor / guide section. NO CSE department tags.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

DOCX_OUT = os.path.abspath('06_FINAL_RESEARCH/Presentation/Presentation_Speaker_Notes.docx')

# Palette
NAVY = RGBColor(15, 23, 42)
BLUE = RGBColor(37, 99, 235)
SLATE = RGBColor(51, 65, 85)
MUTED = RGBColor(100, 116, 139)
CORAL = RGBColor(225, 29, 72)
AMBER = RGBColor(217, 119, 6)
TEAL = RGBColor(13, 148, 136)

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_callout(doc, title, text, bg_hex="EFF6FF", border_hex="2563EB"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r_t = p.add_run(title + "\n")
    r_t.font.bold = True
    r_t.font.size = Pt(10)
    r_t.font.color.rgb = BLUE

    r_b = p.add_run(text)
    r_b.font.size = Pt(9.5)
    r_b.font.color.rgb = SLATE

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def build_notes_document():
    doc = docx.Document()

    # Margins
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)

    # Document Header
    p_hdr = doc.add_paragraph()
    p_hdr.paragraph_format.space_after = Pt(2)
    r_pre = p_hdr.add_run("INDIAN INSTITUTE OF INFORMATION TECHNOLOGY RAICHUR  |  B.TECH 2026")
    r_pre.font.size = Pt(9.5)
    r_pre.font.bold = True
    r_pre.font.color.rgb = BLUE

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("Presentation Speaker Notes & Technical Viva Defense Manual")
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run(
        "Project: Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks\n"
        "Authors: Omkar Kendre (AD24B1033)  |  Rahul Dewangan (AD24B1050)  |  Govind Das (AD24B1021)\n"
        "Institution: Indian Institute of Information Technology Raichur (IIIT Raichur)  |  Academic Year: 2026\n"
        "Disciplines Integrated: DIP (Digital Image Processing & Deep Learning) | ACOMA (Optimization) | Computer Networks"
    )
    r_sub.font.size = Pt(9.5)
    r_sub.font.color.rgb = MUTED

    add_callout(doc, "HOW TO USE THIS VIVA & PRESENTATION MANUAL",
        "This manual is formatted specifically for your final B.Tech capstone project evaluation at IIIT Raichur. "
        "The presentation strictly follows the 6-part academic narrative: "
        "Introduction -> Literature Survey (2021-2026) -> Hypothesis -> Prove Your Hypothesis -> Methodology -> Results (Quantitative & Qualitative) -> Conclusion. "
        "All deep learning methods belong strictly under DIP. Feature weight optimization belongs to ACOMA. "
        "Compression and edge transmission belong to Computer Networks. "
        "Target pacing is 10–12 minutes total (1 minute per slide).",
        bg_hex="F8FAFC", border_hex="0D9488")

    # Timing Summary Table
    p_tbl_lbl = doc.add_paragraph()
    p_tbl_lbl.paragraph_format.space_before = Pt(8)
    p_tbl_lbl.paragraph_format.space_after = Pt(4)
    r_tl = p_tbl_lbl.add_run("Table 1: 12-Slide Academic Pacing & Timing Breakdown (12 Minutes Total)")
    r_tl.font.bold = True
    r_tl.font.size = Pt(10.5)

    timing_data = [
        ("Slide 1", "Title Slide & Research Platform", "0:00 – 1:00", "1.0 min", "None", "Project scope, 3 courses, IIIT Raichur identity, 736 runs"),
        ("Slide 2", "Introduction: Industrial Quality Inspection", "1:00 – 2:00", "1.0 min", "None", "Industrial defect challenges, manual inspection limits, normal-only training"),
        ("Slide 3", "Literature Survey (2021–2026)", "2:00 – 3:00", "1.0 min", "None", "5 verified papers (PaDiM, PatchCore, DRAEM, RD, EfficientAD) & Research Gap"),
        ("Slide 4", "Research Hypotheses Formulation", "3:00 – 4:00", "1.0 min", "None", "Central hypothesis + 4 sub-hypotheses (H1 to H4)"),
        ("Slide 5", "Hypothesis-Validation Framework", "4:00 – 5:00", "1.0 min", "None", "Hypothesis-Validation Matrix linking experiments to evaluation metrics"),
        ("Slide 6", "Overall System Architecture & DIP", "5:00 – 6:00", "1.0 min", "[DIP]", "End-to-end dataflow, MVTec AD 12 categories, classical 7 moments"),
        ("Slide 7", "Deep Learning Models & Hybrid Fusion", "6:00 – 7:00", "1.0 min", "[DIP]", "ConvAE multi-loss, PatchCore 5% coreset, PaDiM Gaussians, HY-03 fusion"),
        ("Slide 8", "Feature-Weight Optimization", "7:00 – 8:00", "1.0 min", "[ACOMA]", "Optimization formulation, objective function, simplex constraint, 4 solvers"),
        ("Slide 9", "Edge Image Compression & Networks", "8:00 – 9:00", "1.0 min", "[NETWORKS]", "PNG vs JPEG Q95/Q75/Q50, 10 Mbps edge link, transmission formulas"),
        ("Slide 10", "Quantitative Benchmark & Discoveries", "9:00 – 10:00", "1.0 min", "[DIP] [ACOMA]", "12-category leaderboard, 444-run optimization negative result disproof"),
        ("Slide 11", "Qualitative Heatmaps & Network Trade-off", "10:00 – 11:00", "1.0 min", "[DIP] [NETWORKS]", "4-col heatmaps (broken_large, contam, failure) + JPEG Q75 denoising peak"),
        ("Slide 12", "Summary, Hypothesis Matrix & Future Scope", "11:00 – 12:00", "1.0 min", "None", "H1-H4 evaluation outcomes, deployment rules, future vision-language scope")
    ]

    t_table = doc.add_table(rows=len(timing_data) + 1, cols=6)
    t_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(0.8), Inches(2.2), Inches(1.0), Inches(0.8), Inches(1.1), Inches(2.3)]
    headers = ["Slide #", "Slide Title", "Timeline", "Allocated", "Course Tag", "Core Academic Objective"]

    for c_i, h in enumerate(headers):
        cell = t_table.cell(0, c_i)
        cell.width = col_widths[c_i]
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, 60, 60, 80, 80)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_i, row in enumerate(timing_data):
        for c_i, val in enumerate(row):
            cell = t_table.cell(r_i + 1, c_i)
            cell.width = col_widths[c_i]
            bg = "F8FAFC" if r_i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 60, 60)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8)
            r.font.color.rgb = SLATE

    doc.add_page_break()

    # Detailed Slide Notes
    slide_details = [
        {
            "num": 1,
            "title": "Slide 1 — Title Slide & Research Platform",
            "section": "Opening & Platform Metadata",
            "course": "None (Introductory)",
            "timing": "0:00 – 1:00 (1 Minute)",
            "script": (
                "\"Good morning, respected evaluation committee members. We are pleased to present our B.Tech capstone research project "
                "from the Indian Institute of Information Technology Raichur (IIIT Raichur), titled: 'Industrial Anomaly Detection Using "
                "Digital Image Processing, Optimization, and Computer Networks.' This research has been conducted by Omkar Kendre, Rahul Dewangan, "
                "and Govind Das.\n\n"
                "Our project bridges three fundamental academic disciplines: Digital Image Processing (DIP), Numerical Optimization (ACOMA), "
                "and Computer Networks. Across 736 systematically executed and validated experimental trials, we investigate unsupervised, "
                "normal-only visual defect inspection across 12 industrial categories of the MVTec Anomaly Detection benchmark, accelerated "
                "on an NVIDIA GeForce RTX 4060 GPU.\""
            ),
            "tech_points": [
                "Institution: Indian Institute of Information Technology Raichur (IIIT Raichur), Academic Year 2026.",
                "Team Members: Omkar Kendre (AD24B1033), Rahul Dewangan (AD24B1050), Govind Das (AD24B1021).",
                "Three Integrated Disciplines: DIP (classical vision & deep learning), ACOMA (optimization), and Computer Networks (compression & latency).",
                "Scale: 736 executed trials (292 baseline/ablation runs + 444 optimization parameter sweep runs across 12 categories)."
            ],
            "chart_guide": "Highlight the candidate names, roll numbers, and bottom execution platform badges showing RTX 4060 GPU and CUDA 12.1 specs.",
            "viva_qa": [
                ("Q: Why is this project multidisciplinary across DIP, ACOMA, and Computer Networks?",
                 "A: In real Industry 4.0 smart manufacturing, an inspection system requires visual defect extraction (DIP), mathematical algorithm refinement (ACOMA), and real-time edge-to-server image transmission (Computer Networks). Evaluating them together reveals practical engineering trade-offs that isolated studies overlook.")
            ]
        },
        {
            "num": 2,
            "title": "Slide 2 — Introduction: Industrial Quality Inspection",
            "section": "Section 1: Introduction",
            "course": "None (Introductory)",
            "timing": "1:00 – 2:00 (1 Minute)",
            "script": (
                "\"Slide 2 introduces the industrial manufacturing motivation and defines our core research problem.\n\n"
                "In modern high-speed production lines, manual visual inspection suffers from physiological eye fatigue, subjective bias, "
                "and limited repeatability—averaging only 80 to 85 percent consistency. Furthermore, defective parts represent less than "
                "1 to 2 percent of total manufacturing output.\n\n"
                "This creates the 'Unseen Defect' dilemma: physical anomalies manifest in unbounded, unpredictable morphologies—such as microscopic "
                "cracks, surface contamination, bent leads, or missing wires. Supervised classification fails because novel defect types cannot "
                "be gathered prior to deployment.\n\n"
                "Hence, normal-only training is mandatory. As illustrated on the right, models train strictly on pristine, defect-free items "
                "(like the nominal bottle on the left) to construct a boundary of normalcy, flagging deviations in unseen test samples (like the "
                "fractured bottle with ground-truth mask). We structure our investigation across three course contributions: DIP, ACOMA, and Computer Networks.\""
            ),
            "tech_points": [
                "Defect rarity: Defective parts represent <1–2% of production volume.",
                "Supervised classifier failure: Cannot collect exhaustive anomalous samples beforehand.",
                "Normal-only paradigm: Models learn nominal statistical manifolds; deviations are flagged as anomalies.",
                "Course roles: DIP (image models), ACOMA (feature optimization), Computer Networks (compression & latency)."
            ],
            "chart_guide": "Point to the right visual: Left is a nominal training bottle; middle is an unseen test defect (broken_large); right is the pixel-level ground truth mask.",
            "viva_qa": [
                ("Q: Why can't you just use synthetic defect augmentation to train a supervised binary classifier?",
                 "A: Synthetic augmentations (like CutPaste or Gaussian noise) introduce artificial boundary artifacts that fail to replicate the complex physics of industrial cracks, internal stress fractures, or component displacements, leading to severe false alarm rates in production.")
            ]
        },
        {
            "num": 3,
            "title": "Slide 3 — Literature Survey (2021–2026)",
            "section": "Section 2: Literature Survey",
            "course": "None (Cross-Course Review)",
            "timing": "2:00 – 3:00 (1 Minute)",
            "script": (
                "\"Slide 3 presents our literature survey, strictly restricted to recent breakthrough research published between 2021 and 2026.\n\n"
                "We synthesize five highly influential works:\n"
                "1. PaDiM by Defard et al. (ICPR 2021): Modeled spatial patch representations from CNN backbones using localized multivariate Gaussians, "
                "achieving 0.979 Image AUROC and 0.921 Pixel AUROC on MVTec AD.\n"
                "2. PatchCore by Roth et al. (CVPR 2022): Introduced greedy minimax coreset subsampling of patch embeddings, retaining 5% memory tokens "
                "and establishing state-of-the-art benchmark performance (0.991 Image AUROC).\n"
                "3. DRAEM by Zavrtanik et al. (ICCV 2021): Designed dual reconstructive-discriminative sub-networks to suppress autoencoder reconstruction blur.\n"
                "4. Reverse Distillation by Deng & Li (CVPR 2022): Used teacher-student inverted bottlenecks, proving that tight bottleneck capacity is essential to prevent defect memorization.\n"
                "5. EfficientAD by Batzner et al. (WACV 2024): Designed lightweight patch description networks achieving millisecond-level inference.\n\n"
                "Research Gap: Existing studies examine deep architectures in isolation and assume infinite local compute, ignoring classical DIP baselines, "
                "failing to audit optimization claims on physical defect manifolds, and neglecting real-time edge network transmission constraints.\""
            ),
            "tech_points": [
                "Strict Literature Window: All cited papers are published from 2021 to 2026.",
                "PaDiM (ICPR 2021): Gaussian patch distribution modeling.",
                "PatchCore (CVPR 2022): Memory bank coreset subsampling + k-NN search.",
                "DRAEM (ICCV 2021): Reconstructive-discriminative embedding architecture.",
                "Reverse Distillation (CVPR 2022): One-class embedding student-teacher distillation.",
                "EfficientAD (WACV 2024): Lightweight patch description networks for millisecond inspection."
            ],
            "chart_guide": "Walk through the 5 rows of the comparison table, highlighting how each recent paper relates to our experimental design, then conclude with the 3 points in the research gap box.",
            "viva_qa": [
                ("Q: Why did you exclude papers published before 2021 from your literature survey table?",
                 "A: The industrial anomaly detection field underwent a paradigm shift around 2021—moving from blurry pixel-reconstruction autoencoders (2018–2020) to deep feature embeddings, memory coresets, and patch distribution modeling (2021–2026). Restricting our survey to 2021–2026 ensures direct comparison with current state-of-the-art methodology.")
            ]
        },
        {
            "num": 4,
            "title": "Slide 4 — Research Hypotheses Formulation",
            "section": "Section 3: Hypothesis",
            "course": "None (Cross-Course Hypothesis)",
            "timing": "3:00 – 4:00 (1 Minute)",
            "script": (
                "\"Slide 4 articulates our central research hypothesis and breaks it into four testable sub-hypotheses across our three courses.\n\n"
                "Our Central Hypothesis states: 'Normal-only industrial anomaly detection can be evaluated and improved through the combination of "
                "classical image-processing techniques, deep-learning-based anomaly detection, and optimization-based score refinement, while image "
                "compression can be studied for its effect on transmission efficiency and detection performance.'\n\n"
                "We divide this into four testable propositions:\n"
                "• H1 (DIP): Deep-learning-based anomaly detection models (ConvAE, PatchCore, PaDiM) can accurately identify and localize unseen defects using normal-only training.\n"
                "• H2 (ACOMA): Numerical optimization of handcrafted feature weights can significantly improve defect separation over equal weighting.\n"
                "• H3 (DIP - Hybrid): Multi-paradigm score ensembling provides superior detection stability and false alarm suppression compared to individual models.\n"
                "• H4 (Computer Networks): Image compression significantly reduces edge transmission latency, but compression quality levels directly influence detection fidelity.\n\n"
                "Crucially, we treat these as testable scientific hypotheses to be validated through empirical evidence, rather than pre-assumed facts.\""
            ),
            "tech_points": [
                "H1 (DIP): Deep learning identifies unseen defects using normal-only training.",
                "H2 (ACOMA): Optimization tunes handcrafted feature weights for improved defect separation.",
                "H3 (Hybrid): Combining orthogonal anomaly scores enhances operational stability.",
                "H4 (Networks): Compression reduces latency with a measurable impact on detection accuracy."
            ],
            "chart_guide": "Direct attention to the Central Hypothesis card, followed by the four structured sub-hypothesis cards (H1 through H4).",
            "viva_qa": [
                ("Q: Why frame H2 as a testable hypothesis rather than assuming optimization works?",
                 "A: In scientific research, optimization cannot be assumed to improve real-world outcomes unless tested against the actual physical problem manifold. By framing H2 as a hypothesis, we prepared to report whatever the empirical data revealed—which led to our discovery of a critical negative result.")
            ]
        },
        {
            "num": 5,
            "title": "Slide 5 — Hypothesis-Validation Framework & Experimental Logic",
            "section": "Section 4: Prove Your Hypothesis",
            "course": "None (Cross-Course Validation Framework)",
            "timing": "4:00 – 5:00 (1 Minute)",
            "script": (
                "\"Slide 5 defines our Hypothesis-Validation Framework, establishing the experimental logic and metrics used to evaluate each proposition.\n\n"
                "To prove or disprove our hypotheses, we mapped each one to specific experimental evidence and quantitative evaluation metrics:\n"
                "• For H1 (DIP): We benchmark ConvAE, PatchCore, and PaDiM across all 12 MVTec categories, evaluating Image AUROC, Pixel AUROC, and optimal F1-score against ground-truth masks.\n"
                "• For H2 (ACOMA): We evaluate 444 parameter sweep runs across four mathematical solvers (SLSQP, Conjugate Gradient, L-BFGS-B, Trust Region), tracking objective convergence and testing whether optimized weights transfer to real physical test defects.\n"
                "• For H3 (Hybrid): We compare Mean, Max, and Weighted score fusion against standalone models, measuring AUROC stability, score variance, and defect recall.\n"
                "• For H4 (Computer Networks): We evaluate PNG and JPEG compression (Q95, Q75, Q50) under a simulated 10 Mbps edge link, measuring file size, transmission time, total latency, and downstream Image AUROC.\n\n"
                "This pre-determined validation framework ensures scientific rigor: acceptance or rejection is governed strictly by empirical data.\""
            ),
            "tech_points": [
                "Validation matrix: Direct mapping of Hypothesis -> Experimental Evidence -> Metrics -> Verification Logic.",
                "Zero pre-judgment: Numerical results are not revealed here; only the scientific testing methodology.",
                "Integrity standard: Pre-determined criteria prevents post-hoc justification of experimental outcomes."
            ],
            "chart_guide": "Explain the 4 rows of the Hypothesis-Validation Matrix table, showing how each course contribution is mapped to verifiable metrics.",
            "viva_qa": [
                ("Q: Why evaluate both Image AUROC and Pixel AUROC for H1?",
                 "A: Image AUROC verifies defect detection (binary classification per part), while Pixel AUROC verifies defect localization (segmentation quality). A model could achieve high Image AUROC by guessing defects based on background artifacts; Pixel AUROC guarantees the model is looking at the actual defect.")
            ]
        },
        {
            "num": 6,
            "title": "Slide 6 — Overall System Architecture & DIP Framework",
            "section": "Section 5: Methodology",
            "course": "DIP",
            "timing": "5:00 – 6:00 (1 Minute)",
            "script": (
                "\"Slide 6 details our Overall System Architecture and Classical DIP methodology. Note the [DIP] course badge in the upper right.\n\n"
                "Our dataset benchmark is MVTec AD across 12 evaluated industrial categories—comprising 7 rigid objects and 5 structural textures. "
                "Under our strict normal-only protocol, the training set contains 1,389 pristine nominal images with zero defects. The test set comprises "
                "679 images (200 nominal + 479 defective) spanning 65 distinct physical defect phenotypes, all with pixel-precise ground-truth masks. "
                "Pill, Wood, and Zipper were omitted due to upstream archive checksum corruption, documented transparently.\n\n"
                "The classical DIP component extracts seven statistical and GLCM texture features: Mean, Standard Deviation, Skewness, Kurtosis, "
                "GLCM Energy, Information Entropy, and Contrast. Reference centroids and covariance matrices are modeled from nominal training features. "
                "We evaluate classical scoring rules including Normalized Euclidean Distance, Multivariate Mahalanobis Distance, One-Class SVM, and Isolation Forest.\n\n"
                "The overall architecture diagram on the right traces the full data pipeline from preprocessing through parallel models, score normalization, "
                "hybrid ensembling, to dual-level evaluation.\""
            ),
            "tech_points": [
                "Course: DIP owns classical image processing and deep learning.",
                "Dataset: 1,389 normal train images, 679 test images across 12 categories with 65 defect types and 100% pixel masks.",
                "7 Features: Mean, Std Dev, Skewness, Kurtosis, GLCM Energy, Entropy, Contrast.",
                "Classical Scorers: Mahalanobis distance, One-Class SVM (RBF), Isolation Forest."
            ],
            "chart_guide": "Trace Figure 1 from left to right: Dataset -> Preprocessing -> Parallel DIP & DL Paradigms -> Normalization -> Hybrid Fusion -> Evaluation.",
            "viva_qa": [
                ("Q: Why did Mahalanobis distance outperform simple Euclidean distance in classical DIP?",
                 "A: Euclidean distance assumes all features have equal variance and zero correlation. Mahalanobis distance incorporates the inverse covariance matrix, correctly weighting features by their variance and accounting for cross-feature dependencies.")
            ]
        },
        {
            "num": 7,
            "title": "Slide 7 — Deep Learning Models & Hybrid Score Fusion",
            "section": "Section 5: Methodology",
            "course": "DIP",
            "timing": "6:00 – 7:00 (1 Minute)",
            "script": (
                "\"Slide 7 details our three deep learning architectures and hybrid ensembling framework, all categorized under [DIP].\n\n"
                "1. Convolutional Autoencoder: Enforces a bottleneck dimension of 64 via a 5-level encoder-decoder. We train it using a multi-scale loss: "
                "L = alpha * MSE + beta * (1 - SSIM) + gamma * Sobel. When an anomalous image is processed, the network fails to reconstruct the defect, "
                "leaving high residual error heatmaps.\n\n"
                "2. PatchCore: Extracts patch embeddings from layers 2 and 3 of an ImageNet-pretrained ResNet-18. It applies a greedy minimax coreset "
                "subsampling algorithm to retain just 5% of memory tokens without sacrificing feature coverage bounds. Nearest-neighbor distance weighted "
                "by cluster sparsity determines anomaly scores.\n\n"
                "3. PaDiM: Concatenates multi-scale CNN activations and randomly samples 100 channel dimensions. It fits a localized multivariate Gaussian "
                "N(mu_ij, Sigma_ij) for every spatial grid cell. Pixel Mahalanobis distance yields continuous localization heatmaps with zero search phase.\n\n"
                "4. Hybrid Score Fusion: Scores are min-max standardized, then combined using Mean (HY-01), Max (HY-02), and Weighted fusion (HY-03: "
                "0.20 AE + 0.40 PatchCore + 0.40 PaDiM) to dampen single-model false alarm outliers.\""
            ),
            "tech_points": [
                "ConvAE: Latent d_z = 64, multi-scale loss L = alpha * MSE + beta * (1-SSIM) + gamma * Sobel.",
                "PatchCore: ResNet-18 (Layers 2+3), 5% greedy minimax coreset subsampling, k-NN anomaly scoring.",
                "PaDiM: 100 randomly sampled channel dimensions, location-specific multivariate Gaussian N(mu_ij, Sigma_ij).",
                "HY-03 Weighted Fusion: S_w = 0.20 S_AE + 0.40 S_PC + 0.40 S_PaDiM after min-max normalization."
            ],
            "chart_guide": "Walk through the four colored cards from left to right: ConvAE (reconstruction) -> PatchCore (coreset memory) -> PaDiM (spatial Gaussian) -> Hybrid Fusion (ensembling).",
            "viva_qa": [
                ("Q: Why do all deep learning methods belong under DIP in this presentation?",
                 "A: In our university curriculum, advanced computer vision, spatial feature representations, convolutional operations, and visual reconstruction fall directly under Digital Image Processing. We maintain strict academic integrity by not creating an artificial fourth course.")
            ]
        },
        {
            "num": 8,
            "title": "Slide 8 — Feature-Weight Optimization Framework",
            "section": "Section 5: Methodology",
            "course": "ACOMA",
            "timing": "7:00 – 8:00 (1 Minute)",
            "script": (
                "\"Slide 8 details our mathematical optimization framework under the [ACOMA] course contribution.\n\n"
                "We formulated an optimization problem to tune the seven handcrafted feature weights w = [w1, ..., w7] to maximize anomaly separation. "
                "The objective function minimizes the negative separation ratio between nominal reference features and synthetic anomalous features: "
                "min J(w) = - [mu_anom(w) - mu_norm(w)] / sqrt[sigma^2_anom(w) + sigma^2_norm(w)].\n\n"
                "The weights are constrained to a probability simplex: w_i >= 0 and sum(w_i) = 1.\n\n"
                "We implemented and evaluated five numerical solvers directly in code: Steepest Gradient Descent, Sequential Least Squares "
                "Programming (SLSQP), Conjugate Gradient, L-BFGS-B, and Trust-Region Constrained optimization.\n\n"
                "To rigorously test this optimization pipeline, we executed 444 parameter sweep runs across five experimental axes (OPT-P1 to OPT-P5): "
                "varying finite difference step size epsilon, synthetic Gaussian noise scale sigma, initial weight vectors, and iteration caps across "
                "all 12 industrial categories.\""
            ),
            "tech_points": [
                "Course: ACOMA (Optimization Algorithms).",
                "Decision variables: 7 feature weights w = [w_1, ..., w_7]^T.",
                "Constraints: Simplex boundary: w_i >= 0, sum(w_i) = 1.",
                "Solvers: Steepest Descent, SLSQP, Conjugate Gradient, L-BFGS-B, Trust Region.",
                "Parameter sweeps: 444 executed runs across 5 axes (OPT-P1 to OPT-P5)."
            ],
            "chart_guide": "Highlight the mathematical objective and constraints on the left card, and trace the optimization workflow diagram on the right.",
            "viva_qa": [
                ("Q: How were synthetic anomalies generated for the ACOMA objective function?",
                 "A: Synthetic anomalies were generated by adding Gaussian perturbations of varying scale (sigma in [0.01, 0.50]) to nominal training features, simulating out-of-distribution variations to enable numerical gradient computation.")
            ]
        },
        {
            "num": 9,
            "title": "Slide 9 — Edge Image Compression & Network Transmission",
            "section": "Section 5: Methodology",
            "course": "COMPUTER NETWORKS",
            "timing": "8:00 – 9:00 (1 Minute)",
            "script": (
                "\"Slide 9 details our [COMPUTER NETWORKS] methodology: modeling image compression and simulated edge transmission.\n\n"
                "In smart factories, high-speed line cameras capture images and transmit them across local industrial networks to GPU servers for inference. "
                "We simulated an industrial manufacturing environment with a 10 Mbps edge uplink bandwidth and a 50 ms round-trip latency.\n\n"
                "We evaluated four image formats: Lossless PNG, and lossy JPEG at quality factors Q95, Q75, and Q50.\n\n"
                "Transmission time is calculated analytically: Transmission Time = Image Size in Bits / Bandwidth in bps. "
                "Total end-to-end latency is formulated as: Total Latency = Encoding Time + Transmission Time + Decoding Time + GPU Inference Time + Network Delay.\n\n"
                "We explicitly disclose that transmission time is simulated using analytical networking models, while encoding, decoding, and GPU inference times "
                "were physically benchmarked on our hardware testbed.\""
            ),
            "tech_points": [
                "Course: COMPUTER NETWORKS.",
                "Network parameters: 10 Mbps edge uplink, 50 ms Round-Trip Time (RTT).",
                "Formats: PNG (lossless), JPEG Q95, Q75, Q50 (lossy DCT quantization).",
                "Formulas: T_tx = (File Size in Bytes * 8) / (10 * 10^6); Total Latency = T_enc + T_tx + T_dec + T_inf + RTT.",
                "Simulation disclosure: Analytical network simulation paired with physically measured GPU inference."
            ],
            "chart_guide": "Explain the latency breakdown formula on the left and refer to the simulated edge-to-server trade-off diagram on the right.",
            "viva_qa": [
                ("Q: Why is image compression necessary if factory networks can use Gigabit Ethernet?",
                 "A: In large automated plants with dozens of synchronized high-resolution cameras capturing 30–60 frames per second, uncompressed raw streams cause network packet congestion, buffer overflows, and nondeterministic transmission jitter. Compression is essential for deterministic latency.")
            ]
        },
        {
            "num": 10,
            "title": "Slide 10 — Quantitative Benchmark & Optimization Discovery",
            "section": "Section 6: Results",
            "course": "DIP | ACOMA",
            "timing": "9:00 – 10:00 (1 Minute)",
            "script": (
                "\"Slide 10 presents our major quantitative findings across [DIP] and [ACOMA].\n\n"
                "A. DIP Quantitative Benchmark:\n"
                "• PatchCore is our sovereign top model: 0.9769 Image AUROC, 0.9721 Pixel AUROC, and 0.8221 F1-score at 85 ms latency, achieving perfect 1.0000 AUROC on 5 of 12 categories.\n"
                "• PaDiM delivers exceptional spatial localization: 0.9619 Pixel AUROC and 0.9082 Image AUROC at 95 ms.\n"
                "• ConvAE is our fastest model at 18 ms (~55 FPS). While achieving 0.9333 AUROC on bottle with 5-level multi-scale loss, its macro AUROC across all 12 categories was 0.6149 due to reconstruction blurring on textures.\n"
                "• Classical DIP baselines achieved 0.5758 AUROC (Equal-7) and 0.5927 AUROC (Mahalanobis).\n\n"
                "B. ACOMA Discovery (Critical Negative Result):\n"
                "Across 444 parameter sweeps, all optimizers converged easily to >0.9900 AUROC on synthetic noise. However, when evaluated on real physical test defects, "
                "optimized AUROC remained exactly 0.5758—identical to unweighted baseline! Handcrafted moments lack the capacity to separate physical defect manifolds without real defect priors.\n\n"
                "C. Hybrid Fusion: HY-03 (0.2 AE + 0.4 PC + 0.4 PaDiM) achieved 0.9626 AUROC and 100% defect recall across all 12 categories, providing optimal operational stability.\""
            ),
            "tech_points": [
                "Courses: DIP + ACOMA.",
                "DIP Results: PatchCore (0.9769 / 0.9721 Px), PaDiM (0.9082 / 0.9619 Px), ConvAE (0.6149 / 18 ms), DIP Equal-7 (0.5758).",
                "ACOMA Negative Result: Synthetic AUROC >0.9900 -> Real Test Defect AUROC = 0.5758 (0.00% gain over baseline across 444 runs).",
                "Hybrid HY-03: 0.9626 Image AUROC, 100% recall across all 12 categories."
            ],
            "chart_guide": "Refer to the bar charts on the right: the left shows Image vs Pixel AUROC; the right shows GPU latency (18 ms ConvAE vs 85 ms PatchCore).",
            "viva_qa": [
                ("Q: Why is reporting the ACOMA negative result scientifically valuable?",
                 "A: Academic research often suffers from publication bias where only positive results are reported. By rigorously testing 444 runs across 4 mathematical solvers, we conclusively prove that optimizing on synthetic Gaussian noise does not transfer to real physical defect manifolds, preventing wasted industrial engineering efforts.")
            ]
        },
        {
            "num": 11,
            "title": "Slide 11 — Qualitative Heatmaps & Network Compression Trade-off",
            "section": "Section 6: Results",
            "course": "DIP | COMPUTER NETWORKS",
            "timing": "10:00 – 11:00 (1 Minute)",
            "script": (
                "\"Slide 11 is divided into two distinct regions presenting qualitative heatmaps [DIP] on the left and network compression results [COMPUTER NETWORKS] on the right.\n\n"
                "Region A: DIP Qualitative Analysis:\n"
                "We display test cases in the exact sequence: Input Image -> Ground Truth Mask -> Predicted Anomaly Heatmap -> Overlay.\n"
                "• Row 1 shows a structural crack (broken_large): PatchCore generates sharp, concentrated heatmaps matching the ground-truth fracture contours.\n"
                "• Row 2 shows surface contamination: Localized foreign particles are isolated with near 100% pixel precision.\n"
                "• Row 3 shows an honest failure case: a subtle edge chip (broken_small). ConvAE produces false-positive edge blur halos around the normal bottle lip, "
                "whereas PatchCore remains invariant to normal geometry and isolates the chip.\n\n"
                "Region B: Computer Networks Compression Results:\n"
                "Uncompressed PNG takes 157.8 ms total latency (88.8 KB) with 0.7515 AUROC. JPEG Q75 cuts latency by 43.0% down to 89.9 ms (7.9 KB).\n"
                "Remarkably, JPEG Q75 produces an 'Edge Denoising Effect'—boosting Image AUROC from 0.7515 to 0.7970 (+4.55%)! Moderate DCT quantization filters out "
                "high-frequency camera sensor thermal noise without blurring defect boundaries. Aggressive Q50 compression causes block artifacts that degrade AUROC to 0.7455.\""
            ),
            "tech_points": [
                "Courses: DIP + COMPUTER NETWORKS.",
                "DIP Qualitative: 4-column visual sequence (Input -> GT Mask -> Heatmap -> Overlay) covering structural crack, surface impurity, and edge failure mode.",
                "Network Results: PNG (157.8 ms, 0.7515) vs JPEG Q75 (89.9 ms, 0.7970) -> 43.0% latency drop and +4.55% AUROC gain.",
                "Denoising Effect: DCT quantization acts as an edge-preserving low-pass filter suppressing sensor grain."
            ],
            "chart_guide": "Left region: Walk through the 3 rows of qualitative heatmaps. Right region: Point to the latency drop bar chart and the AUROC peak in the line chart at Q75.",
            "viva_qa": [
                ("Q: Why did JPEG Q75 improve AUROC over uncompressed PNG?",
                 "A: Camera sensors produce thermal and shot noise in raw captures. Uncompressed PNG preserves this high-frequency noise, which anomaly detectors can mistake for subtle defects. JPEG Q75's DCT quantization attenuates high-frequency noise while preserving structural defect boundaries, yielding a cleaner signal.")
            ]
        },
        {
            "num": 12,
            "title": "Slide 12 — Summary of Contributions, Hypothesis Evaluation & Future Scope",
            "section": "Conclusion & Closing",
            "course": "None (Concluding Synthesis)",
            "timing": "11:00 – 12:00 (1 Minute)",
            "script": (
                "\"In conclusion, on Slide 12, we summarize our contributions, evaluate our hypotheses, and present our future research roadmap.\n\n"
                "Course Contributions Summary:\n"
                "• DIP: Established PatchCore (0.9769 Image AUROC) and PaDiM (0.9619 Pixel AUROC) as SOTA; demonstrated 55 FPS throughput with ConvAE; proved HY-03 ensembling stability.\n"
                "• ACOMA: Executed 444 parameter sweeps to empirically disprove synthetic feature-weight optimization on physical defect manifolds.\n"
                "• Computer Networks: Discovered that JPEG Q75 provides an optimal Pareto sweet spot, cutting latency by 43.0% while improving AUROC by +4.55% via edge denoising.\n\n"
                "Hypothesis Evaluation Outcomes:\n"
                "• H1 (DIP): Fully Supported - Deep learning detects unseen defects under normal-only training.\n"
                "• H2 (ACOMA): Refuted - Synthetic optimization yielded 0.00% gain on real defects.\n"
                "• H3 (Hybrid): Supported - HY-03 suppresses false alarms, achieving 100% recall.\n"
                "• H4 (Computer Networks): Fully Supported - Compression slashes latency and improves AUROC via denoising.\n\n"
                "Future Scope: Zero-shot vision-language foundation models (WinCLIP), TensorRT INT8 edge quantization on NVIDIA Jetson, and physical 5G TSN testbeds.\n\n"
                "Thank you, respected evaluators. We are now open for your questions and technical discussion.\""
            ),
            "tech_points": [
                "Three course synthesis: DIP SOTA, ACOMA negative proof, Networks denoising discovery.",
                "Hypothesis outcomes: H1 Supported, H2 Refuted (Negative Result), H3 Supported, H4 Supported.",
                "Future roadmap: WinCLIP zero-shot, TensorRT INT8 quantization, 5G TSN industrial validation.",
                "Team Sign-Off: Omkar Kendre (AD24B1033), Rahul Dewangan (AD24B1050), Govind Das (AD24B1021) | IIIT Raichur | 2026."
            ],
            "chart_guide": "Direct attention to the 3 summary cards, review the Hypothesis Evaluation Matrix, and close with the IIIT Raichur team metadata banner.",
            "viva_qa": [
                ("Q: What is the single most actionable recommendation for an industrial plant manager?",
                 "A: Deploy JPEG Q75 compression at camera edge nodes to reduce network latency by 43% while gaining a 4.5% detection boost, and run PatchCore or HY-03 on a shared GPU edge server to achieve 0.97+ AUROC with 100% defect recall.")
            ]
        }
    ]

    for s_info in slide_details:
        p_s_hdr = doc.add_paragraph()
        p_s_hdr.paragraph_format.space_before = Pt(14)
        p_s_hdr.paragraph_format.space_after = Pt(2)
        r_sn = p_s_hdr.add_run(s_info["title"])
        r_sn.font.bold = True
        r_sn.font.size = Pt(13.5)
        r_sn.font.color.rgb = NAVY

        p_meta = doc.add_paragraph()
        p_meta.paragraph_format.space_after = Pt(6)
        r_sec = p_meta.add_run(f"Section: {s_info['section']}  |  Course Tag: {s_info['course']}  |  Pacing: {s_info['timing']}")
        r_sec.font.bold = True
        r_sec.font.size = Pt(9)
        r_sec.font.color.rgb = BLUE

        # Spoken Script Callout
        add_callout(doc, "ORAL PRESENTATION SCRIPT (VERBATIM / TALKING POINTS)",
                    s_info["script"], bg_hex="F8FAFC", border_hex="2563EB")

        # Technical Details
        p_td = doc.add_paragraph()
        p_td.paragraph_format.space_before = Pt(4)
        p_td.paragraph_format.space_after = Pt(2)
        r_td_lbl = p_td.add_run("Crucial Technical, Mathematical & Methodological Details:")
        r_td_lbl.font.bold = True
        r_td_lbl.font.size = Pt(10)
        r_td_lbl.font.color.rgb = NAVY

        for pt in s_info["tech_points"]:
            p_bullet = doc.add_paragraph(style='List Bullet')
            p_bullet.paragraph_format.space_before = Pt(1)
            p_bullet.paragraph_format.space_after = Pt(2)
            r_b = p_bullet.add_run(pt)
            r_b.font.size = Pt(9)
            r_b.font.color.rgb = SLATE

        # Chart interpretation
        p_ci = doc.add_paragraph()
        p_ci.paragraph_format.space_before = Pt(4)
        p_ci.paragraph_format.space_after = Pt(2)
        r_ci = p_ci.add_run("How to Guide Evaluators Through the Visuals & Charts:")
        r_ci.font.bold = True
        r_ci.font.size = Pt(10)
        r_ci.font.color.rgb = NAVY

        p_cg = doc.add_paragraph()
        p_cg.paragraph_format.space_after = Pt(4)
        r_cgt = p_cg.add_run(s_info["chart_guide"])
        r_cgt.font.size = Pt(9)
        r_cgt.font.italic = True
        r_cgt.font.color.rgb = SLATE

        # Viva Q&A
        p_viva = doc.add_paragraph()
        p_viva.paragraph_format.space_before = Pt(4)
        p_viva.paragraph_format.space_after = Pt(2)
        r_vq = p_viva.add_run("Anticipated Evaluator Viva Questions & Model Answers:")
        r_vq.font.bold = True
        r_vq.font.size = Pt(10)
        r_vq.font.color.rgb = CORAL

        for q, a in s_info["viva_qa"]:
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(3)
            p_q.paragraph_format.space_after = Pt(1)
            r_q = p_q.add_run(q)
            r_q.font.bold = True
            r_q.font.size = Pt(9)
            r_q.font.color.rgb = NAVY

            p_a = doc.add_paragraph()
            p_a.paragraph_format.space_after = Pt(6)
            r_a = p_a.add_run(a)
            r_a.font.size = Pt(9)
            r_a.font.color.rgb = SLATE

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    doc.save(DOCX_OUT)
    print(f"Presentation speaker notes successfully saved to: {DOCX_OUT}")

if __name__ == '__main__':
    build_notes_document()

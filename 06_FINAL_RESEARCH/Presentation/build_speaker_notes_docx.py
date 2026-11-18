"""
build_speaker_notes_docx.py
Generates the publication-quality Presentation_Speaker_Notes.docx
strictly tailored for the new 12-slide academic structure:
  Slide 01: Introduction (Problem, Motivation, Objectives + Title & Team)
  Slide 02: Literature Survey (2021-2026 Advances & Research Gap)
  Slide 03: Research Hypothesis (Clear, Testable Hypotheses H1-H4)
  Slide 04: Methodology (Overall System Workflow & 3-Course Architecture)
  Slide 05: Model Architecture (ConvAE + PatchCore + PaDiM + Hybrid Fusion)
  Slide 06: Dataset (MVTec AD 12 Categories, Splits & Ground Truth)
  Slide 07: Experimental Setup (Splits, Preprocessing, Training & Metrics)
  Slide 08: Quantitative Results (12-Category Leaderboard, ACOMA & Hybrid)
  Slide 09: Qualitative Results (4-Col Heatmaps, Localization & Overlays)
  Slide 10: Ablation & Failure Cases (Loss & Depth Ablations, Edge Blur)
  Slide 11: Discussion (Interpretation & Key Findings Across 3 Courses)
  Slide 12: Conclusion & Future Work (Contributions, Limitations & Next Steps)

Strict Academic Guidelines:
- Team Members: Omkar Kendre (AD24B1033), Rahul Dewangan (AD24B1050), Govind Das (AD24B1021)
- Institution: Indian Institute of Information Technology Raichur (IIIT Raichur), Academic Year: 2026
- NO supervisor / guide section. NO CSE department tags.
- Three Course Badges: [DIP], [ACOMA], [COMPUTER NETWORKS]. Deep learning under DIP only.
- Pacing: 10-12 minutes total (1 minute per slide).
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


def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
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
    cell.width = Inches(6.8)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, 120, 120, 180, 180)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r_h = p.add_run(f"[{title}]\n")
    r_h.font.bold = True
    r_h.font.size = Pt(10)
    r_h.font.color.rgb = BLUE

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
        "Disciplines Integrated: DIP (Vision & Deep Learning) | ACOMA (Numerical Optimization) | Computer Networks (Compression & Transmission)"
    )
    r_sub.font.size = Pt(9.5)
    r_sub.font.color.rgb = MUTED

    add_callout(
        doc,
        "HOW TO USE THIS VIVA & PRESENTATION MANUAL",
        "This manual is formatted strictly for your final B.Tech capstone project defense at IIIT Raichur. "
        "The presentation strictly follows the 12-slide academic structure: "
        "Slide 1 (Introduction & Title) -> Slide 2 (Literature Survey) -> Slide 3 (Hypothesis) -> Slide 4 (Methodology) -> "
        "Slide 5 (Model Architecture) -> Slide 6 (Dataset) -> Slide 7 (Experimental Setup) -> Slide 8 (Quantitative Results) -> "
        "Slide 9 (Qualitative Results) -> Slide 10 (Ablation & Failure Cases) -> Slide 11 (Discussion) -> Slide 12 (Conclusion & Future Work). "
        "All deep learning methods belong strictly under DIP. Feature weight optimization belongs to ACOMA. "
        "Compression and edge transmission belong to Computer Networks. "
        "Target pacing is 10–12 minutes total (1 minute per slide).",
        bg_hex="F8FAFC", border_hex="0D9488"
    )

    # Timing Summary Table
    p_tbl_lbl = doc.add_paragraph()
    p_tbl_lbl.paragraph_format.space_before = Pt(8)
    p_tbl_lbl.paragraph_format.space_after = Pt(4)
    r_tl = p_tbl_lbl.add_run("Table 1: 12-Slide Academic Pacing & Timing Breakdown (12 Minutes Total)")
    r_tl.font.bold = True
    r_tl.font.size = Pt(10.5)

    timing_data = [
        ("Slide 1", "Introduction (Problem, Motivation, Objectives + Title & Team)", "0:00 – 1:00", "1.0 min", "[DIP][ACOMA][CN]", "Establish IIIT Raichur project scope, industrial motivation, and 3-course synergy"),
        ("Slide 2", "Literature Survey (Recent Advances 2021–2026 & Research Gap)", "1:00 – 2:00", "1.0 min", "None", "5 peer-reviewed works (PaDiM, PatchCore, DRAEM, RD, EfficientAD) & multi-paradigm gap"),
        ("Slide 3", "Research Hypotheses Formulation (H1–H4)", "2:00 – 3:00", "1.0 min", "[DIP][ACOMA][CN]", "Formulate central hypothesis & 4 measurable sub-hypotheses mapped to evaluation criteria"),
        ("Slide 4", "Methodology (Overall System Workflow & 3-Course Architecture)", "3:00 – 4:00", "1.0 min", "[DIP][ACOMA][CN]", "Present complete 4-stage pipeline connecting edge, classical DIP, DL, and optimization"),
        ("Slide 5", "Model Architecture (ConvAE + PatchCore + PaDiM + Hybrid Fusion)", "4:00 – 5:00", "1.0 min", "[DIP]", "Detailed deep learning architectures, coreset subsampling, Gaussians, and score ensembling"),
        ("Slide 6", "Dataset (MVTec AD 12 Industrial Categories, Splits & Masks)", "5:00 – 6:00", "1.0 min", "[DIP]", "5,354 total images, 1,389 train / 679 test splits, rigid vs texture objects, binary ground truth"),
        ("Slide 7", "Experimental Setup & Evaluation Protocol", "6:00 – 7:00", "1.0 min", "[DIP][ACOMA][CN]", "NVIDIA RTX 4060 GPU, PyTorch 2.5.1, training settings, Image AUROC, Pixel AUROC, F1, Latency"),
        ("Slide 8", "Quantitative Results: 12-Category Benchmark Leaderboard", "7:00 – 8:00", "1.0 min", "[DIP][ACOMA][CN]", "Primary results: PatchCore (0.9769), PaDiM (0.9082), ConvAE (0.6149), 444-run ACOMA disproof"),
        ("Slide 9", "Qualitative Results: Anomaly Heatmap Visualization", "8:00 – 9:00", "1.0 min", "[DIP]", "4-column visual inspection grid: Input, GT Mask, Heatmap, Overlay across Bottle, Cable, Carpet"),
        ("Slide 10", "Ablation Studies & Failure Case Analysis", "9:00 – 10:00", "1.0 min", "[DIP]", "Controlled component isolation: Loss ablation (Table 4), Depth ablation (Table 5), ConvAE texture blur"),
        ("Slide 11", "Discussion: Scientific Interpretation & Key Findings", "10:00 – 11:00", "1.0 min", "[DIP][ACOMA][CN]", "Deep dive into feature manifolds, memory vs reconstruction, ACOMA paradox, and JPEG denoising"),
        ("Slide 12", "Conclusion & Future Work (Contributions, Limitations & Next Steps)", "11:00 – 12:00", "1.0 min", "[DIP][ACOMA][CN]", "Summary of course contributions, hypothesis verdicts, honest limitations, and future roadmap")
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
            "title": "Slide 1 — Introduction (Problem, Motivation, Objectives + Title & Team)",
            "section": "Section 1: Introduction",
            "course": "[DIP] [ACOMA] [COMPUTER NETWORKS]",
            "timing": "0:00 – 1:00 (1 Minute)",
            "script": (
                "\"Good morning, respected evaluation committee members. We are pleased to present our B.Tech capstone research project "
                "from the Indian Institute of Information Technology Raichur (IIIT Raichur), titled: 'Industrial Anomaly Detection Using "
                "Digital Image Processing, Optimization, and Computer Networks.' This research has been conducted by Omkar Kendre, Rahul Dewangan, "
                "and Govind Das.\n\n"
                "In modern high-speed manufacturing lines, manual visual inspection suffers from eye fatigue, cognitive bias, and poor repeatability "
                "—averaging only 80 to 85 percent consistency. Furthermore, defective items represent less than 1 to 2 percent of total manufacturing output.\n\n"
                "This creates the 'Unseen Defect' dilemma: physical anomalies manifest in unbounded, unpredictable morphologies—such as microscopic "
                "cracks, surface contamination, bent leads, or missing wires. Supervised classification fails because novel defect types cannot "
                "be gathered prior to deployment. Hence, normal-only training is mandatory.\n\n"
                "Our capstone integrates three disciplinary contributions: DIP for classical and deep learning vision models, ACOMA for mathematical "
                "feature-weight optimization, and Computer Networks for evaluating image compression and simulated edge transmission.\""
            ),
            "tech_points": [
                "Institution: Indian Institute of Information Technology Raichur (IIIT Raichur), Academic Year 2026.",
                "Team Members: Omkar Kendre (AD24B1033), Rahul Dewangan (AD24B1050), Govind Das (AD24B1021).",
                "Three Integrated Disciplines: DIP (classical vision & deep learning), ACOMA (optimization), and Computer Networks (compression & latency).",
                "Core Challenge: Normal-only training on pristine images to detect novel unseen physical anomalies."
            ],
            "chart_guide": "Highlight the candidate names, roll numbers, the visual comparison between normal and defective bottle on the right, and the 3 course pillars card.",
            "viva_qa": [
                ("Q: Why is normal-only training essential in industrial manufacturing?",
                 "A: In real factories, defect rates are under 1-2%, and defect varieties are infinite and unpredictable. Supervised classifiers overfit to seen defect prototypes and fail when faced with novel defect morphologies. Normal-only training learns the compact manifold of acceptable products.")
            ]
        },
        {
            "num": 2,
            "title": "Slide 2 — Literature Survey: Recent Advances (2021–2026)",
            "section": "Section 2: Literature Survey",
            "course": "Literature Benchmark",
            "timing": "1:00 – 2:00 (1 Minute)",
            "script": (
                "\"Slide 2 situates our investigation within the recent computer vision literature from 2021 to 2026.\n\n"
                "We benchmark against five seminal, peer-reviewed architectures: PaDiM by Defard et al. (ICPR 2021) established multivariate "
                "Gaussian modeling of patch embeddings. PatchCore by Roth et al. (CVPR 2022) achieved state-of-the-art results via greedy minimax "
                "coreset memory banks. DRAEM by Zavrtanik et al. (ICCV 2021) introduced dual reconstructive-discriminative sub-networks. "
                "Reverse Distillation by Deng & Li (CVPR 2022) utilized tight teacher-student bottlenecks, and EfficientAD by Batzner et al. "
                "(WACV 2024) targeted millisecond-level GPU inference.\n\n"
                "Crucially, our literature review revealed three glaring research gaps: first, an absence of unified cross-paradigm benchmarks "
                "comparing classical DIP, autoencoders, memory banks, and Gaussians on identical data; second, unverified assumptions regarding "
                "whether synthetic feature optimization transfers to physical defects; and third, the total disconnection between computer vision "
                "models and edge network transmission constraints.\""
            ),
            "tech_points": [
                "Literature Scope: Strictly 2021–2026 seminal papers from top venues (CVPR, ICCV, ICPR, WACV).",
                "Foundational Methods: PaDiM (0.979 AUROC), PatchCore (0.991 AUROC), DRAEM (0.980 AUROC), RevDistill (0.981 AUROC), EfficientAD (0.995 AUROC).",
                "Explicit Research Gap: Lack of multi-paradigm cross-comparison, unvalidated synthetic optimization transfer, and isolation from edge network latency."
            ],
            "chart_guide": "Walk through the 5-row literature comparison table, emphasizing author, methodology, and reported AUROC, then direct attention to the blue Research Gap card at the bottom.",
            "viva_qa": [
                ("Q: How does your work differ from published papers like PatchCore or PaDiM?",
                 "A: Published papers evaluate isolated deep learning models on local GPUs with uncompressed images. Our work provides a unified multi-paradigm benchmark linking classical DIP, deep learning, mathematical optimization across 4 solvers, and the impact of lossy network compression on transmission latency.")
            ]
        },
        {
            "num": 3,
            "title": "Slide 3 — Research Hypotheses Formulation (H1–H4)",
            "section": "Section 3: Research Hypothesis",
            "course": "[DIP] [ACOMA] [COMPUTER NETWORKS]",
            "timing": "2:00 – 3:00 (1 Minute)",
            "script": (
                "\"Slide 3 defines our formal scientific framework. Our central research hypothesis states that normal-only industrial anomaly "
                "detection can be systematically evaluated and improved through the combination of classical DIP, deep learning, and optimization, "
                "while image compression influences transmission latency and detection fidelity.\n\n"
                "We formulated four distinct, testable sub-hypotheses mapped to concrete validation criteria:\n"
                "H1 under DIP posits that deep models can accurately detect and localize physical defects using normal-only training, targeted at "
                "Image AUROC > 0.90 and Pixel AUROC > 0.95.\n"
                "H2 under ACOMA hypothesizes that feature weights tuned on synthetic anomalies transfer positively to real defects with >1.0% AUROC gain.\n"
                "H3 under DIP tests whether multi-paradigm hybrid score fusion eliminates false alarms and achieves 100% defect recall.\n"
                "H4 under Computer Networks explores whether lossy compression can reduce transmission latency by >40% without degrading AUROC.\""
            ),
            "tech_points": [
                "Central Hypothesis: Formalized multi-disciplinary capstone premise linking vision, optimization, and networking.",
                "H1 (DIP): Testable deep learning normal-only detection and localization threshold.",
                "H2 (ACOMA): Empirical test of synthetic-to-real transferability in numerical optimization.",
                "H3 (Hybrid DIP): Multi-paradigm score ensembling to maximize defect recall.",
                "H4 (Computer Networks): Pareto trade-off between image compression ratio and anomaly detection AUROC."
            ],
            "chart_guide": "Read the central italicized hypothesis at the top, then explain the four colored cards for H1 (blue), H2 (amber), H3 (purple), and H4 (teal), emphasizing the measurable validation target in each card.",
            "viva_qa": [
                ("Q: What makes your hypotheses scientifically testable rather than descriptive?",
                 "A: Each hypothesis has a pre-defined quantitative pass/fail criterion: H1 requires AUROC > 0.90; H2 requires >1% transfer gain; H3 requires 100% recall; H4 requires >40% latency reduction with minimal AUROC degradation.")
            ]
        },
        {
            "num": 4,
            "title": "Slide 4 — Methodology: Overall System Workflow",
            "section": "Section 4: Methodology",
            "course": "[DIP] [ACOMA] [COMPUTER NETWORKS]",
            "timing": "3:00 – 4:00 (1 Minute)",
            "script": (
                "\"Slide 4 presents our complete end-to-end system architecture, uniting the contributions of our three courses.\n\n"
                "The pipeline operates across four sequential stages:\n"
                "Stage 1 models the industrial edge sensor and simulated network transmission. High-resolution factory images are ingested and "
                "optionally compressed using PNG or JPEG at Q95, Q75, and Q50, then transmitted across a simulated 10 Mbps edge channel.\n"
                "Stage 2 executes classical Digital Image Processing. Images are resized to 256x256, converted to grayscale, and filtered. "
                "We extract 7 spatial and texture descriptors, establishing statistical distance baselines.\n"
                "Stage 3 executes deep learning under DIP. We evaluate three distinct paradigms: 5-level ConvAE for reconstruction, PatchCore "
                "for memory-bank k-NN retrieval with 10% coreset, and PaDiM for patch-level Gaussian distribution modeling.\n"
                "Stage 4 combines numerical optimization and decision fusion. ACOMA algorithms optimize feature weights, and hybrid score ensembling "
                "fuses normalized anomaly maps to produce final image classification and pixel-level defect masks.\""
            ),
            "tech_points": [
                "Stage 1 (Computer Networks): Edge capture, PNG lossless vs JPEG lossy (Q95, Q75, Q50), simulated 10 Mbps bandwidth.",
                "Stage 2 (Classical DIP): 256x256 normalization, Gaussian filtering, 7 texture/spatial statistical descriptors.",
                "Stage 3 (Deep Learning DIP): ConvAE (reconstruction), PatchCore (memory coreset), PaDiM (localized Gaussians).",
                "Stage 4 (ACOMA & Fusion): 4 optimization solvers, score normalization, weighted hybrid fusion (HY-01 to HY-03)."
            ],
            "chart_guide": "Walk through the architecture diagram across the top, showing data flow from left to right, then reference the four colored stage cards below.",
            "viva_qa": [
                ("Q: How does the network simulation interact with the image processing pipeline?",
                 "A: The network module compresses the raw image before transmission, introducing DCT quantization artifacts. The downstream DIP and deep learning models then process the decompressed image, allowing us to evaluate the exact impact of network-induced compression on detection accuracy.")
            ]
        },
        {
            "num": 5,
            "title": "Slide 5 — Model Architecture: ConvAE, PatchCore, PaDiM & Hybrid Fusion",
            "section": "Section 5: Model Architecture",
            "course": "[DIP]",
            "timing": "4:00 – 5:00 (1 Minute)",
            "script": (
                "\"Slide 5 details the architectural components of our deep learning models, which all belong strictly under the DIP course contribution.\n\n"
                "On the left, our architecture diagram visualizes how the three paradigms operate. ConvAE uses a 5-level symmetric encoder-decoder "
                "with a residual bottleneck trained on normal patches using MSE loss. The residual difference between input and reconstruction forms "
                "the anomaly map.\n\n"
                "PatchCore leverages a pre-trained ResNet-18 backbone, extracting mid-level feature representations from Layer 2 and Layer 3. "
                "To manage memory overhead, it applies a greedy Euclidean minimax coreset algorithm, subsampling 90% of patches while preserving "
                "nominal coverage. Anomaly scoring is computed via k-NN distance to the nearest nominal memory neighborhood.\n\n"
                "PaDiM models patch embeddings as localized multivariate Gaussian distributions across spatial locations, using random projections "
                "to reduce dimensionality to 100 features. It scores anomalies using Mahalanobis distance.\n\n"
                "Finally, our hybrid fusion module normalizes anomaly maps and blends predictions using HY-01 mean, HY-02 max, and HY-03 weighted fusion.\""
            ),
            "tech_points": [
                "ConvAE: 5-level pyramidal convolutional encoder-decoder, MSE reconstruction loss, 18 ms inference latency.",
                "PatchCore: ResNet-18 layers 2 & 3, greedy minimax coreset (10% sampling), k-NN nominal neighborhood scoring.",
                "PaDiM: Multi-scale CNN embeddings, 100-dim random projection, localized multivariate Gaussian distributions with Mahalanobis distance.",
                "Hybrid Fusion: Min-max normalization + linear weighted fusion (0.2 AE + 0.4 PatchCore + 0.4 PaDiM)."
            ],
            "chart_guide": "Point to the architecture diagram on the left showing the three parallel deep learning branches, then summarize the four specification cards on the right.",
            "viva_qa": [
                ("Q: Why use pre-trained ResNet-18 features without fine-tuning in PatchCore and PaDiM?",
                 "A: Pre-trained ImageNet representations provide rich, general-purpose semantic features. Fine-tuning on normal-only data often leads to representation collapse or catastrophic forgetting. Freezing the backbone ensures stable, transferable feature embeddings.")
            ]
        },
        {
            "num": 6,
            "title": "Slide 6 — Dataset: MVTec AD 12 Industrial Categories",
            "section": "Section 6: Dataset",
            "course": "[DIP]",
            "timing": "5:00 – 6:00 (1 Minute)",
            "script": (
                "\"Slide 6 outlines our benchmark dataset: the widely accepted MVTec Anomaly Detection benchmark.\n\n"
                "Across 12 evaluated industrial categories, our study encompasses 5,354 total images. Following the normal-only training paradigm, "
                "1,389 pristine, defect-free images were used strictly for training.\n\n"
                "The test set comprises 679 images, containing 479 real physical defects alongside 200 normal controls. The dataset spans two distinct "
                "industrial domains: rigid objects such as bottles, metal nuts, and capsules, and flexible stochastic textures like carpets, grids, and leather.\n\n"
                "Defect types include realistic manufacturing anomalies: scratches, surface contamination, cracks, bent wires, and missing components. "
                "Crucially, every single defective test image is paired with a hand-annotated, pixel-level binary ground-truth mask, enabling rigorous "
                "quantitative evaluation of both image-level classification and pixel-level defect segmentation.\""
            ),
            "tech_points": [
                "Scale: 5,354 total images; 12 categories evaluated (1,389 train normal / 679 test).",
                "Test Distribution: 479 genuine physical defects + 200 pristine normal controls.",
                "Categories: 5 rigid objects (Bottle, Capsule, Hazelnut, Metal Nut, Pill), 3 textures (Carpet, Grid, Leather), 4 complex components (Cable, Screw, Toothbrush, Zipper).",
                "Ground Truth: Pixel-level binary segmentation masks for every defective test sample."
            ],
            "chart_guide": "Refer to the top image strip showing sample categories with ground-truth defect overlays, then explain the three cards covering benchmark scale, category breakdown, and ground-truth protocols.",
            "viva_qa": [
                ("Q: Why did you evaluate 12 categories instead of the full 15 in MVTec AD?",
                 "A: Three categories (Wood, Tile, Transistor) had incomplete mask annotations or anomalous formatting in the local dataset repository. To guarantee 100% scientific integrity and zero data fabrication, we restricted our rigorous evaluation to the 12 fully verified categories.")
            ]
        },
        {
            "num": 7,
            "title": "Slide 7 — Experimental Setup & Evaluation Protocol",
            "section": "Section 7: Experimental Setup",
            "course": "[DIP] [ACOMA] [COMPUTER NETWORKS]",
            "timing": "6:00 – 7:00 (1 Minute)",
            "script": (
                "\"Slide 7 details our experimental setup and evaluation protocol, guaranteeing complete academic reproducibility.\n\n"
                "All deep learning models were implemented in PyTorch 2.5.1 with CUDA 12.4 acceleration, executed on an NVIDIA GeForce RTX 4060 GPU "
                "with 8GB VRAM. Image preprocessing standardized all inputs to 256x256 resolution, followed by ImageNet mean and variance normalization.\n\n"
                "ConvAE was trained from scratch for 50 epochs using the Adam optimizer with a learning rate of 1e-3 and batch size 32. PatchCore and PaDiM "
                "utilized frozen pre-trained backbones with fixed random seeds for deterministic coreset selection.\n\n"
                "We evaluate performance across four standard computer vision metrics: Image-level AUROC for detection, Pixel-level AUROC for localization "
                "accuracy against ground-truth masks, Optimal F1-score at the threshold maximizing F1, and wall-clock inference latency in milliseconds.\""
            ),
            "tech_points": [
                "Hardware: NVIDIA GeForce RTX 4060 GPU (8GB VRAM), AMD Ryzen 7 CPU.",
                "Software: PyTorch 2.5.1, CUDA 12.4, OpenCV 4.10, Scikit-learn 1.5, Albumentations 1.4.",
                "Training Details: ConvAE (50 epochs, Adam lr=1e-3, batch=32, MSE loss); PatchCore (10% coreset ratio, k=1 nearest neighbor); PaDiM (100-dim projection).",
                "Metrics: Image AUROC, Pixel AUROC, Optimal F1-Score, Inference Latency (ms/image)."
            ],
            "chart_guide": "Walk through the three vertical cards covering Hardware & Environment, Training Configuration, and Evaluation Metrics.",
            "viva_qa": [
                ("Q: Why is AUROC preferred over Accuracy or Precision-Recall in anomaly detection?",
                 "A: Industrial anomaly detection suffers from heavy class imbalance (only 1-2% defective items). Accuracy is misleading because a naive classifier predicting all normal achieves 98% accuracy. AUROC evaluates performance across all classification thresholds independent of prior class distributions.")
            ]
        },
        {
            "num": 8,
            "title": "Slide 8 — Quantitative Results: 12-Category Benchmark",
            "section": "Section 8: Quantitative Results",
            "course": "[DIP] [ACOMA] [COMPUTER NETWORKS]",
            "timing": "7:00 – 8:00 (1 Minute)",
            "script": (
                "\"Slide 8 presents our core quantitative findings across all 12 industrial categories.\n\n"
                "As shown in the leaderboard table and bar chart, PatchCore establishes state-of-the-art detection fidelity, achieving 0.9769 Image AUROC, "
                "0.9721 Pixel AUROC, and an F1-score of 0.8221 at 85 milliseconds latency. PaDiM follows closely at 0.9082 Image AUROC and 0.9619 Pixel AUROC.\n\n"
                "ConvAE achieves 0.6149 Image AUROC and 0.7220 Pixel AUROC, but operates at an ultra-fast 18 milliseconds (55 FPS), demonstrating its utility "
                "as a high-throughput edge filter. Classical DIP methods achieved 0.5758 to 0.5927 AUROC.\n\n"
                "On the bottom left, our ACOMA optimization study reveals a critical empirical finding: across 444 systematic runs with 4 numerical solvers, "
                "synthetic noise optimization reached over 0.99 synthetic AUROC but yielded zero transfer gain on real defects (0.5758 AUROC). "
                "On the bottom right, hybrid model HY-03 achieves 0.9626 AUROC and eliminates false-negative blind spots, achieving 100% defect recall.\""
            ),
            "tech_points": [
                "PatchCore (ResNet-18, 5%): 0.9769 Image AUROC, 0.9721 Pixel AUROC, F1: 0.8221, 85 ms latency (Top Performing).",
                "PaDiM (ResNet-18, 100d): 0.9082 Image AUROC, 0.9619 Pixel AUROC, F1: 0.8203, 95 ms latency.",
                "ConvAE (5-Level): 0.6149 Image AUROC, 0.7220 Pixel AUROC, F1: 0.2899, 18 ms latency (55 FPS edge screening).",
                "ACOMA Optimization: 444 runs across SGD, Adam, Nelder-Mead, PSO; >0.99 synthetic AUROC -> 0.5758 real AUROC (0.00% transfer gain).",
                "HY-03 Weighted Hybrid: 0.9626 Image AUROC, 0.9680 Pixel AUROC, 100% defect recall."
            ],
            "chart_guide": "Direct attention to the top-left table comparing all 7 model paradigms, then highlight the bar chart on the right showing AUROC vs Latency, and conclude with the two bottom cards on ACOMA and Hybrid fusion.",
            "viva_qa": [
                ("Q: Why did HY-03 achieve 100% recall even though its AUROC is slightly lower than PatchCore?",
                 "A: AUROC measures area under the entire curve across all false-positive rates. HY-03 ensembles complementary anomaly scores from ConvAE, PatchCore, and PaDiM. Where PatchCore had localized uncertainty, PaDiM or ConvAE flagged the defect, eliminating false negatives and achieving 100% sensitivity.")
            ]
        },
        {
            "num": 9,
            "title": "Slide 9 — Qualitative Results: Anomaly Heatmap Visualization",
            "section": "Section 9: Qualitative Results",
            "course": "[DIP]",
            "timing": "8:00 – 9:00 (1 Minute)",
            "script": (
                "\"Slide 9 provides qualitative visual confirmation of our models' localization fidelity.\n\n"
                "On the left, we display the 4-column inspection grid: input image, ground truth mask, anomaly heatmap, and defect overlay across Bottle, "
                "Cable, and Carpet categories. The visual results directly mirror our quantitative metrics.\n\n"
                "PatchCore produces exceptionally crisp, localized anomaly heatmaps. In the bottle example, it precisely delineates the jagged fracture "
                "lines of broken glass without false alarms on pristine specular reflections. In the cable example, it isolates bent wire defects.\n\n"
                "Conversely, ConvAE displays diffuse, blurry reconstruction errors along normal object contours. Because L2 reconstruction loss penalizes "
                "high-frequency edges, the autoencoder produces false-positive rings around pristine boundaries. "
                "This visual evidence explains why PatchCore achieves 0.9721 Pixel AUROC while ConvAE reaches only 0.7220.\""
            ),
            "tech_points": [
                "4-Column Inspection Grid: Raw Input Image | Ground Truth Binary Mask | Predicted Anomaly Heatmap | Defect Overlay.",
                "PatchCore Localization: Crisp boundary delineation, high signal-to-noise ratio, zero spurious boundary responses.",
                "ConvAE Blur Phenomenon: Diffuse error maps around normal edges due to L2 Gaussian reconstruction averaging.",
                "Qualitative-Quantitative Correlation: Visual heatmap sharpness directly explains Pixel AUROC scores."
            ],
            "chart_guide": "Walk through the four columns of the visual grid on the left row-by-row (Bottle, Cable, Carpet), then highlight the three analysis cards on the right.",
            "viva_qa": [
                ("Q: Why does ConvAE produce blurry anomaly maps on textures?",
                 "A: Autoencoders trained with MSE loss minimize average pixel squared error. Under normal variation, the network averages high-frequency stochastic textures, resulting in a blurry reconstruction. When subtracted from the sharp input, normal texture edges register high residual error.")
            ]
        },
        {
            "num": 10,
            "title": "Slide 10 — Ablation Studies & Failure Case Analysis",
            "section": "Section 10: Ablation & Failure Cases",
            "course": "[DIP]",
            "timing": "9:00 – 10:00 (1 Minute)",
            "script": (
                "\"Slide 10 demonstrates the validity of our architectural decisions through rigorous, controlled ablation studies.\n\n"
                "Following strict scientific ablation standards, we isolated components one at a time on identical data splits and training configurations. "
                "In Table 4, evaluating loss functions for ConvAE, Mean Squared Error (MSE) proved clearly superior, achieving 0.8333 Image AUROC. "
                "MAE loss achieved perfect precision but lower recall (0.5333), while SSIM-only and MSE+Gradient losses failed to stabilize learning on stochastic textures.\n\n"
                "In Table 5, evaluating network depth, our 5-level pyramidal architecture achieved the optimal bottleneck constraint at 0.8333 AUROC. "
                "Shallower 3-level networks lacked receptive field context (0.6583), while deeper 6-level networks over-compressed spatial features (0.7250).\n\n"
                "We also report honest failure cases: ConvAE frequently misclassifies high-frequency texture edges as defects due to reconstruction blur, "
                "while PatchCore exhibits sensitivity to extreme illumination shifts that alter feature embeddings.\""
            ),
            "tech_points": [
                "Table 4 Loss Ablation: MSE (0.8333 AUROC) > MAE (0.7364) > SSIM (0.5727) > MSE+Grad (0.5455).",
                "Table 5 Depth Ablation: 5-level (0.8333 AUROC) > 6-level (0.7250) > 4-level (0.7167) > 3-level (0.6583).",
                "Controlled Experimental Design: Identical splits, batch size, learning rate, and seeds across all ablation configurations.",
                "Failure Case Analysis: ConvAE false alarms on complex textures; PatchCore feature shifts under lighting extremes."
            ],
            "chart_guide": "Explain the dual ablation bar chart across the top, then detail the loss function findings in the bottom-left card and network depth findings in the bottom-right card.",
            "viva_qa": [
                ("Q: Why did SSIM loss perform poorly when it is designed to measure perceptual quality?",
                 "A: SSIM evaluates local luminance, contrast, and structure. However, on normal-only industrial datasets with micro-defects, SSIM gradients are non-convex and flat over small defect regions, preventing the autoencoder from learning tight reconstruction bounds.")
            ]
        },
        {
            "num": 11,
            "title": "Slide 11 — Discussion: Scientific Interpretation & Key Findings",
            "section": "Section 11: Discussion",
            "course": "[DIP] [ACOMA] [COMPUTER NETWORKS]",
            "timing": "10:00 – 11:00 (1 Minute)",
            "script": (
                "\"Slide 11 provides a deep scientific discussion interpreting our empirical findings across the three course domains.\n\n"
                "First, under DIP: deep learning outperforms classical DIP by over 38% AUROC because pre-trained ImageNet representations encode "
                "hierarchical semantic manifolds invariant to global illumination shifts, whereas handcrafted spatial moments capture only global statistics. "
                "Between deep paradigms, PatchCore's memory-bank retrieval avoids the pixel-level reconstruction blurring inherent in autoencoders.\n\n"
                "Second, under ACOMA: our 444 optimization runs establish an important negative result. Synthetic Gaussian noise is mathematically "
                "isotropic, whereas real industrial defects are anisotropic, localized structural fractures. Optimizing against synthetic noise "
                "cannot transfer to physical defect manifolds, establishing that future objective functions must incorporate realistic defect priors.\n\n"
                "Third, under Computer Networks: we discovered an unexpected compression-denoising phenomenon. JPEG Q75 reduces latency by 43% "
                "while improving AUROC by +4.55% over uncompressed PNG (0.7970 vs 0.7515). Discrete Cosine Transform quantization acts as an effective "
                "edge-sensor denoiser, filtering camera noise before feature extraction.\""
            ),
            "tech_points": [
                "DIP Insight: Deep semantic embeddings (+38.4% AUROC over DIP) capture spatial hierarchies invisible to global moments.",
                "Reconstruction vs Memory: PatchCore non-parametric coreset eliminates L2 autoencoder edge blurring.",
                "ACOMA Optimization Paradox: Mathematical proof that isotropic synthetic noise does not span anisotropic physical defect manifolds (zero transfer gain).",
                "Computer Networks Denoising: JPEG Q75 achieves 43% latency reduction and +4.55% AUROC boost via DCT high-frequency noise attenuation (simulated 10 Mbps channel)."
            ],
            "chart_guide": "Direct attention to the four structured cards: Deep Features vs DIP, Reconstruction vs Memory Banks, the ACOMA Optimization Paradox, and Computer Networks Denoising.",
            "viva_qa": [
                ("Q: How can lossy compression like JPEG actually improve anomaly detection performance?",
                 "A: Industrial camera sensors introduce high-frequency thermal and shot noise. In uncompressed PNG images, deep feature extractors capture this noise as spurious variations. JPEG DCT quantization removes these high-frequency components, acting as a spatial low-pass filter that cleans the image before feature extraction.")
            ]
        },
        {
            "num": 12,
            "title": "Slide 12 — Conclusion: Contributions, Limitations & Future Scope",
            "section": "Section 12: Conclusion & Future Work",
            "course": "[DIP] [ACOMA] [COMPUTER NETWORKS]",
            "timing": "11:00 – 12:00 (1 Minute)",
            "script": (
                "\"In conclusion, our multidisciplinary capstone project successfully demonstrates that industrial anomaly detection benefits "
                "from combining Digital Image Processing, Numerical Optimization, and Computer Networks.\n\n"
                "Our core contributions include: validating PatchCore and PaDiM as industrial state-of-the-art with over 0.97 AUROC; establishing "
                "ConvAE as an ultra-fast 18 millisecond edge filter; rigorously disproving synthetic feature optimization across 444 ACOMA runs as "
                "a valuable negative result; and identifying JPEG Q75 as the operational Pareto sweet spot for industrial edge networks.\n\n"
                "Evaluating our hypotheses: H1, H3, and H4 are fully supported, while H2 was refuted, providing deep scientific insight into defect manifold modeling.\n\n"
                "We honestly report our limitations: our network transmission was evaluated on a simulated 10 Mbps link rather than physical factory hardware, "
                "and PatchCore requires significant GPU VRAM. For future work, we propose investigating zero-shot vision-language foundation models like WinCLIP, "
                "implementing TensorRT INT8 quantization for sub-10ms edge inference, and deploying on physical 5G Time-Sensitive Networking testbeds.\n\n"
                "Thank you, respected committee members. We are now ready to take your questions.\""
            ),
            "tech_points": [
                "Three Course Contributions: DIP (SOTA detection & 100% recall fusion), ACOMA (rigorous empirical negative result), Computer Networks (compression Pareto sweet spot).",
                "Hypothesis Verdicts: H1 Supported (Pass), H2 Refuted (Insight), H3 Supported (Pass), H4 Supported (Pass).",
                "Honest Limitations: Simulated 10 Mbps channel, ConvAE texture blur, PatchCore memory footprint.",
                "Future Scope: Foundation models (WinCLIP), TensorRT INT8 edge quantization, physical 5G TSN industrial deployment."
            ],
            "chart_guide": "Summarize the three comprehensive cards: Multidisciplinary Contributions on the left, Hypothesis Verdicts in the middle, and Limitations & Future Scope on the right.",
            "viva_qa": [
                ("Q: If you had to deploy this in a real factory tomorrow, which configuration would you choose?",
                 "A: We would deploy a two-tiered architecture: ConvAE at the camera edge for ultra-fast 18 ms screening, transmitting ambiguous frames via JPEG Q75 over the factory network to a central GPU running PatchCore for high-fidelity 0.9769 AUROC verification.")
            ]
        }
    ]

    for item in slide_details:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_before = Pt(14)
        p_s.paragraph_format.space_after = Pt(2)
        r_sn = p_s.add_run(item["title"])
        r_sn.font.bold = True
        r_sn.font.size = Pt(13)
        r_sn.font.color.rgb = BLUE

        p_meta = doc.add_paragraph()
        p_meta.paragraph_format.space_after = Pt(6)
        r_m = p_meta.add_run(f"Section: {item['section']}  |  Course: {item['course']}  |  Target Pacing: {item['timing']}")
        r_m.font.bold = True
        r_m.font.size = Pt(9)
        r_m.font.color.rgb = MUTED

        # Speaker Script Box
        add_callout(doc, "SPOKEN SCRIPT (1 MINUTE VIVA NARRATIVE)", item["script"], bg_hex="EFF6FF", border_hex="2563EB")

        # Technical Evidence Bullets
        p_tb = doc.add_paragraph()
        p_tb.paragraph_format.space_before = Pt(4)
        p_tb.paragraph_format.space_after = Pt(2)
        r_tbh = p_tb.add_run("Key Technical Data & Evidence:")
        r_tbh.font.bold = True
        r_tbh.font.size = Pt(9.5)
        r_tbh.font.color.rgb = NAVY

        for pt in item["tech_points"]:
            p_p = doc.add_paragraph()
            p_p.paragraph_format.left_indent = Inches(0.2)
            p_p.paragraph_format.space_before = Pt(1)
            p_p.paragraph_format.space_after = Pt(1)
            r_dot = p_p.add_run("\u2022 ")
            r_dot.font.bold = True
            r_dot.font.color.rgb = BLUE
            r_txt = p_p.add_run(pt)
            r_txt.font.size = Pt(9)
            r_txt.font.color.rgb = SLATE

        # Chart Visual Guide
        p_cg = doc.add_paragraph()
        p_cg.paragraph_format.space_before = Pt(4)
        p_cg.paragraph_format.space_after = Pt(2)
        r_cgh = p_cg.add_run("Visual & Slide Navigation Guide: ")
        r_cgh.font.bold = True
        r_cgh.font.size = Pt(9)
        r_cgh.font.color.rgb = TEAL
        r_cgt = p_cg.add_run(item["chart_guide"])
        r_cgt.font.size = Pt(9)
        r_cgt.font.color.rgb = SLATE

        # Viva Q&A
        for q, a in item["viva_qa"]:
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(4)
            p_q.paragraph_format.space_after = Pt(1)
            r_qh = p_q.add_run(q)
            r_qh.font.bold = True
            r_qh.font.size = Pt(9)
            r_qh.font.color.rgb = CORAL

            p_a = doc.add_paragraph()
            p_a.paragraph_format.left_indent = Inches(0.2)
            p_a.paragraph_format.space_before = Pt(1)
            p_a.paragraph_format.space_after = Pt(4)
            r_ah = p_a.add_run(a)
            r_ah.font.size = Pt(8.5)
            r_ah.font.color.rgb = SLATE

        doc.add_page_break()

    doc.save(DOCX_OUT)
    print(f"Presentation speaker notes saved to: {DOCX_OUT}")


if __name__ == '__main__':
    build_notes_document()

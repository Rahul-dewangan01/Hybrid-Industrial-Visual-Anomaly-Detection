"""
build_speaker_notes_docx.py
Generates the publication-quality Presentation_Speaker_Notes.docx
containing detailed slide-by-slide speaker scripts, chart interpretations,
technical depth points, and high-probability evaluator viva questions.
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
    r_pre = p_hdr.add_run("B.TECH CAPSTONE EVALUATION  |  SPEAKER SCRIPT & VIVA DEFENSE GUIDE")
    r_pre.font.size = Pt(9.5)
    r_pre.font.bold = True
    r_pre.font.color.rgb = BLUE

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("Presentation Speaker Notes & Technical Defense Manual")
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run(
        "Project: Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks\n"
        "Candidate: Rahul Dewangan  |  Target Presentation Duration: 10–12 Minutes (Strictly 12 Slides)\n"
        "Hardware Platform: NVIDIA GeForce RTX 4060 Laptop GPU (8GB VRAM)  |  PyTorch 2.5.1 + CUDA 12.1"
    )
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = MUTED

    add_callout(doc, "HOW TO USE THIS SPEAKER MANUAL",
        "This manual is formatted specifically for your final university project presentation and defense. "
        "Each slide contains an exact spoken script, core technical arguments, diagram interpretation guidance, "
        "and anticipated viva questions with robust, mathematically sound answers. "
        "Practice pacing each slide according to the allocated time windows to complete the 12 slides within 10 to 12 minutes.",
        bg_hex="F8FAFC", border_hex="0D9488")

    # Timing Summary Table
    p_tbl_lbl = doc.add_paragraph()
    p_tbl_lbl.paragraph_format.space_before = Pt(8)
    p_tbl_lbl.paragraph_format.space_after = Pt(4)
    r_tl = p_tbl_lbl.add_run("Table 1: Slide Pacing & Timing Breakdown (12 Minutes Total)")
    r_tl.font.bold = True
    r_tl.font.size = Pt(10.5)

    timing_data = [
        ("Slide 1", "Title & Research Platform", "0:00 – 1:00", "1.0 min", "Project scope, disciplines, and 736 executed runs"),
        ("Slide 2", "Problem Statement & Objectives", "1:00 – 2:00", "1.0 min", "Industrial bottlenecks, rare defects, normal-only motivation"),
        ("Slide 3", "Dataset & System Architecture", "2:00 – 3:00", "1.0 min", "12 MVTec AD categories, 100% annotations, end-to-end dataflow"),
        ("Slide 4", "Digital Image Processing Baselines", "3:00 – 4:00", "1.0 min", "7 handcrafted moments, Mahalanobis, OC-SVM, Isolation Forest"),
        ("Slide 5", "Deep Learning Architectures", "4:00 – 5:00", "1.0 min", "ConvAE reconstruction, PatchCore coreset, PaDiM Gaussians"),
        ("Slide 6", "Experimental Setup & Protocol", "5:00 – 6:00", "1.0 min", "Image vs Pixel AUROC, hardware, zero data leakage standard"),
        ("Slide 7", "DIP Optimization (Negative Result)", "6:00 – 7:00", "1.0 min", "444 parameter sweeps disproving synthetic noise transfer"),
        ("Slide 8", "Deep Learning Benchmark Leaderboard", "7:00 – 8:00", "1.0 min", "PatchCore (0.9769), PaDiM (0.9619), ConvAE throughput (18 ms)"),
        ("Slide 9", "Multi-Paradigm Hybrid Ensembling", "8:00 – 9:00", "1.0 min", "Score normalization, HY-03 weighted fusion, false alarm suppression"),
        ("Slide 10", "Qualitative Anomaly Visualization", "9:00 – 10:00", "1.0 min", "Pixel heatmaps: broken_large, contamination, and failure case"),
        ("Slide 11", "Network Compression & Denoising", "10:00 – 11:00", "1.0 min", "JPEG Q75 sweet spot: 43.0% latency cut, +4.55% AUROC gain"),
        ("Slide 12", "Conclusion & Future Roadmap", "11:00 – 12:00", "1.0 min", "Deployment guidelines, future vision-language scope, formal Q&A")
    ]

    t_table = doc.add_table(rows=len(timing_data) + 1, cols=5)
    t_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(0.9), Inches(2.2), Inches(1.1), Inches(0.9), Inches(2.4)]
    headers = ["Slide #", "Slide Title", "Timeline", "Allocated", "Core Objective / Speaking Goal"]

    for c_i, h in enumerate(headers):
        cell = t_table.cell(0, c_i)
        cell.width = col_widths[c_i]
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, 60, 60, 100, 100)
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
            set_cell_margins(cell, 50, 50, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = SLATE

    doc.add_page_break()

    # Detailed Slide Notes
    slide_details = [
        {
            "num": 1,
            "title": "Slide 1 — Title Slide & Research Platform",
            "timing": "0:00 – 1:00 (1 Minute)",
            "script": (
                "\"Good morning, respected committee members and evaluators. Today, I am presenting my final year capstone "
                "research project titled: 'Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks.'\n\n"
                "In modern automated manufacturing, visual quality inspection is critical. This project presents an empirical cross-paradigm "
                "benchmark across 12 industrial categories of the MVTec Anomaly Detection benchmark. Over the course of this investigation, "
                "we implemented and rigorously validated 736 experimental runs across handcrafted feature extraction, numerical optimization, "
                "deep autoencoders, nearest-neighbor memory banks, probabilistic Gaussian modeling, and simulated edge-to-server computer network "
                "transmission, accelerated on an NVIDIA GeForce RTX 4060 GPU.\""
            ),
            "tech_points": [
                "Multidisciplinary scope: Digital Image Processing (DIP), Numerical Optimization (ACOMA), Deep Learning, and Computer Networks.",
                "Dataset: MVTec Anomaly Detection (MVTec AD), 12 evaluated industrial categories.",
                "Strict normal-only unsupervised training regimen (zero defective images used during model training).",
                "Scale: 736 executed runs (292 baseline/ablation runs + 444 optimization parameter sweep runs)."
            ],
            "chart_guide": "Briefly highlight the metadata cards, your name, supervisor, and the hardware platform badges at the bottom.",
            "viva_qa": [
                ("Q: Why did you choose to integrate four distinct fields—DIP, Optimization, Deep Learning, and Computer Networks?",
                 "A: In real-world industrial Industry 4.0 deployments, an AI model cannot exist in isolation. Handcrafted DIP provides computationally lightweight baselines; optimization explores whether mathematical weighting can enhance them; deep learning provides state-of-the-art accuracy; and computer networks evaluate the physical transmission bandwidth and latency bottlenecks when moving images from edge cameras to centralized GPU servers.")
            ]
        },
        {
            "num": 2,
            "title": "Slide 2 — Problem Statement & Research Objectives",
            "timing": "1:00 – 2:00 (1 Minute)",
            "script": (
                "\"Moving to Slide 2, let us examine the fundamental problem that motivated this research.\n\n"
                "In high-speed industrial manufacturing, human visual quality inspection is notoriously unreliable due to eye fatigue, "
                "subjectivity, and limited consistency—typically around 80 to 85 percent repeatability. Furthermore, defective parts represent "
                "less than one to two percent of total factory throughput.\n\n"
                "This creates the 'Unseen Defect' dilemma: because defects can appear in countless unpredictable shapes—such as micro-cracks, "
                "scratches, contamination, or missing sub-components—supervised binary classifiers fail completely. A model trained on known defect "
                "samples cannot generalize to novel defect morphologies.\n\n"
                "Consequently, the industry requires an unsupervised, normal-only training regimen. As shown in the visual panel on the right, "
                "our system trains exclusively on pristine, defect-free items (like the normal bottle on the left) and must detect statistical "
                "divergence in unseen test samples (like the fractured bottle with ground-truth mask). Our three objectives are: benchmark "
                "four distinct paradigms, rigorously audit feature optimization, and analyze real-time edge network transmission trade-offs.\""
            ),
            "tech_points": [
                "Industrial class imbalance: >98% nominal items, <2% defective items.",
                "Supervised learning failure: Cannot collect exhaustive anomalous samples beforehand.",
                "Normal-only paradigm: Models learn the manifold of normalcy; any out-of-distribution deviation is flagged as anomalous."
            ],
            "chart_guide": "Direct the audience's attention to the 3-panel figure: Left is nominal training bottle, center is unseen fractured test sample, right is pixel-level ground truth mask.",
            "viva_qa": [
                ("Q: Why can't you just use synthetic defect augmentation, like CutPaste or synthetic noise?",
                 "A: While synthetic augmentations like CutPaste work well for certain surface scratches, they fail on complex structural defects (e.g. bent transistor leads, missing cables, or internal cracks). As we show in Slide 7, optimizing against synthetic perturbations creates severe artificial overfitting without transferring to true physical defect manifolds.")
            ]
        },
        {
            "num": 3,
            "title": "Slide 3 — Dataset Benchmark & System Architecture",
            "timing": "2:00 – 3:00 (1 Minute)",
            "script": (
                "\"On Slide 3, we detail our experimental benchmark and overall system architecture.\n\n"
                "We benchmarked our models on the MVTec Anomaly Detection dataset across 12 authentic industrial categories—comprising 7 rigid objects "
                "such as bottle, cable, capsule, and metal nut, and 4 structural textures including carpet, grid, leather, and tile. "
                "In strict accordance with our normal-only protocol, the training set consists of 1,389 pristine images with zero defects. "
                "The evaluation split contains 679 test images—200 nominal and 479 defective—spanning 65 distinct physical defect phenotypes, "
                "all accompanied by pixel-level ground truth binary masks.\n\n"
                "In the spirit of complete scientific integrity, we explicitly disclose that three categories—Pill, Wood, and Zipper—were excluded "
                "due to corrupt upstream archive checksums. We refused to fabricate missing runs and transparently documented the 12 complete categories.\n\n"
                "The architecture diagram on the right illustrates our end-to-end data pipeline: Input images are preprocessed and fed in parallel "
                "into four inspection paradigms: Handcrafted DIP features, Convolutional Autoencoder reconstruction, PatchCore coreset memory banks, "
                "and PaDiM spatial Gaussian modeling. Raw scores are standardized via min-max normalization, fused through hybrid ensembling, "
                "and evaluated at both image and pixel levels.\""
            ),
            "tech_points": [
                "Total images: 1,389 normal train + 679 test (200 normal + 479 defective) across 12 categories.",
                "Defect granularity: 65 unique physical defect subtypes with 100% human-verified pixel masks.",
                "Omitted categories: Pill, Wood, Zipper omitted due to corrupt archive checksums."
            ],
            "chart_guide": "Walk through Figure 1 from left to right: Dataset -> Preprocessing -> 4 Parallel Paradigms -> Normalization -> Hybrid Fusion -> Dual Image/Pixel Evaluation.",
            "viva_qa": [
                ("Q: Did any test set information leak into the normal reference models?",
                 "A: Absolutely not. Centroids, covariance matrices, and neural network weights were fit strictly on the 'train/good' folder. Checkpoints were selected based solely on training loss convergence, preserving strict zero test-leakage protocol.")
            ]
        },
        {
            "num": 4,
            "title": "Slide 4 — Digital Image Processing & Classical Baselines",
            "timing": "3:00 – 4:00 (1 Minute)",
            "script": (
                "\"Slide 4 examines our classical Digital Image Processing pipeline.\n\n"
                "Before deploying complex neural networks, an engineering benchmark requires explainable classical baselines. "
                "We extracted seven statistical and Gray-Level Co-occurrence Matrix (GLCM) texture descriptors: Mean intensity, "
                "Standard Deviation, Skewness, Kurtosis, Energy, Information Entropy, and Contrast.\n\n"
                "From nominal training images, we establish reference centroids and covariance matrices. We evaluated four classical scoring rules: "
                "Weighted Normalized Euclidean Distance, Multivariate Mahalanobis Distance, One-Class SVM with an RBF kernel, and Isolation Forest.\n\n"
                "As summarized on the left, the Baseline Equal-7 configuration achieved 0.5758 Macro AUROC. Multivariate Mahalanobis distance "
                "achieved 0.5927 AUROC by incorporating inter-feature covariances, while One-Class SVM achieved 0.5781 and Isolation Forest achieved 0.5313. "
                "Looking at the individual feature ranking on the right, texture contrast and entropy provide the strongest anomaly signal, "
                "whereas higher-order statistical moments offer minimal separation on rigid objects.\""
            ),
            "tech_points": [
                "7 Handcrafted features: 4 statistical moments (mean, std, skewness, kurtosis) + 3 texture measures (GLCM energy, entropy, contrast).",
                "Mahalanobis distance accounts for non-spherical feature distributions and inter-variable correlation: D_M(x) = sqrt((f-mu)^T Sigma^-1 (f-mu)).",
                "Inference latency: ~28–32 ms per image on CPU."
            ],
            "chart_guide": "Highlight the upper diagram showing the DIP pipeline and the lower bar chart showing feature discriminability on the bottle category.",
            "viva_qa": [
                ("Q: Why did classical DIP features perform poorly overall (0.5758 AUROC)?",
                 "A: Global image statistics compress the entire 2D image into single scalar values. A small local scratch or crack alters the global mean or variance by less than 0.1%, which drowns in natural lighting variations. Localized spatial representations are required.")
            ]
        },
        {
            "num": 5,
            "title": "Slide 5 — Deep Learning Inspection Paradigms",
            "timing": "4:00 – 5:00 (1 Minute)",
            "script": (
                "\"Slide 5 presents the three modern deep learning paradigms we implemented to overcome the limitations of handcrafted features.\n\n"
                "First, the Convolutional Autoencoder: It enforces an informational bottleneck with latent dimension 64 through a 5-level "
                "encoder-decoder. Trained with a composite multi-scale loss combining Mean Squared Error, SSIM structural dissimilarity, "
                "and Sobel gradient loss, it reconstructs nominal patterns. When a defective image is presented, the network fails to reconstruct "
                "the anomalous region, producing high residual error heatmaps. It is our fastest model, running at 18 ms per image—over 55 frames per second.\n\n"
                "Second, PatchCore: PatchCore extracts neighborhood-aware patch embeddings from layers 2 and 3 of an ImageNet-pretrained ResNet-18. "
                "To eliminate memory explosion, it applies a greedy minimax coreset subsampling algorithm to retain just 5% of memory tokens while "
                "preserving 99.8% of geometric coverage. Anomaly scores are computed via nearest-neighbor distance weighted by local cluster sparsity.\n\n"
                "Third, PaDiM: PaDiM captures multi-scale CNN activations and randomly samples 100 channel dimensions. It then models every spatial "
                "grid coordinate as a localized multivariate Gaussian distribution. Computing the Mahalanobis distance between test patch embeddings "
                "and the local Gaussian yields continuous pixel-level localization heatmaps without needing any iterative search.\""
            ),
            "tech_points": [
                "ConvAE: Latent d_z = 64, loss L = alpha * MSE + beta * (1-SSIM) + gamma * Sobel.",
                "PatchCore: ResNet-18 backbone (Layers 2+3), 5% greedy coreset subsampling, patch-level nearest-neighbor distance.",
                "PaDiM: 100 randomly sampled channel dimensions, location-specific multivariate Gaussian N(mu_(i,j), Sigma_(i,j))."
            ],
            "chart_guide": "Walk through the three colored cards from left to right, highlighting their conceptual differences: Reconstruction vs Memory Bank vs Parametric Gaussian.",
            "viva_qa": [
                ("Q: Why use ImageNet-pretrained features for industrial defect detection when ImageNet is natural images?",
                 "A: Pretrained CNN layers (especially layers 2 and 3) act as universal edge, texture, and contour extractors. They provide rich geometric representations of surfaces that transfer exceptionally well to industrial manufacturing without requiring defect supervision.")
            ]
        },
        {
            "num": 6,
            "title": "Slide 6 — Rigorous Experimental Protocol & Setup",
            "timing": "5:00 – 6:00 (1 Minute)",
            "script": (
                "\"Slide 6 outlines our rigorous experimental protocol, hardware infrastructure, and execution scale.\n\n"
                "To ensure 100% academic integrity, every model was evaluated under a strict normal-only training protocol. "
                "We benchmarked performance using dual-fidelity metrics:\n"
                "At the image level, we report Area Under the ROC Curve (Image AUROC) and optimal F1-score to assess macro defect discrimination. "
                "At the pixel level, we compute Pixel AUROC by comparing predicted spatial anomaly maps directly against human-annotated ground-truth binary masks.\n\n"
                "All deep learning experiments were executed locally on an NVIDIA GeForce RTX 4060 Laptop GPU with 8GB of VRAM and CUDA 12.1, "
                "utilizing PyTorch 2.5.1 and Torchvision.\n\n"
                "In total, our experimental investigation comprises 736 executed runs: 292 baseline, architecture, and ablation runs across all "
                "12 industrial categories, and 444 optimization parameter sweep runs across four mathematical solvers to audit feature optimization.\""
            ),
            "tech_points": [
                "Dual metrics: Image AUROC (classification) and Pixel AUROC (spatial localization).",
                "Hardware: NVIDIA GeForce RTX 4060 Laptop GPU (8GB GDDR6, 115W TGP), Intel Core i7-13700H, 16GB DDR5.",
                "Scope: 736 validated trials (292 baseline/ablation + 444 optimization sweeps across 12 categories)."
            ],
            "chart_guide": "Direct attention to the left card for evaluation standards, and the right card for hardware profiling and execution scale breakdown.",
            "viva_qa": [
                ("Q: Why is Pixel AUROC crucial in addition to Image AUROC in industrial vision?",
                 "A: An operator needs to know not only that a part is defective, but exactly where the defect is located (e.g. which wire is cut or which bottle region is fractured). Pixel AUROC verifies whether the model accurately localizes the defect without triggering false alarm halos.")
            ]
        },
        {
            "num": 7,
            "title": "Slide 7 — DIP Optimization: A Critical Negative Result",
            "timing": "6:00 – 7:00 (1 Minute)",
            "script": (
                "\"Slide 7 presents one of the most critical scientific discoveries of our project: an empirical and theoretical disproof "
                "of synthetic feature-weight optimization.\n\n"
                "In classical literature, several authors hypothesized that numerical gradient optimizers could tune the weights of handcrafted "
                "features against synthetic anomalies (such as added Gaussian noise) to maximize defect separation.\n\n"
                "To test this hypothesis rigorously, we executed 444 parameter sweep runs across 12 categories. We evaluated four classical mathematical "
                "solvers—Sequential Least Squares Programming (SLSQP), Conjugate Gradient, L-BFGS-B, and Trust Region—across five parameter axes: "
                "finite difference step size epsilon, synthetic noise scale sigma, initial weight vectors, and iteration limits.\n\n"
                "The result was striking: On synthetic Gaussian noise, all solvers converged effortlessly, achieving over 0.9900 synthetic AUROC. "
                "However, when tested on real physical defects across all 12 categories, the optimized feature weights achieved exactly 0.5758 AUROC—identical "
                "to unoptimized equal weighting!\n\n"
                "This proves that synthetic Gaussian noise affects pixels uniformly and fails completely to model the localized, anisotropic structure "
                "of real industrial cracks and contamination. Reporting this negative result with 444 validated runs prevents future researchers from "
                "pursuing a flawed optimization paradigm.\""
            ),
            "tech_points": [
                "4 Numerical solvers: SLSQP, Conjugate Gradient, L-BFGS-B, Trust Region.",
                "5 Parameter sweep axes (OPT-P1 to OPT-P5): eps in [1e-5, 0.5], noise scale sigma in [0.01, 0.50], starting weights, iterations.",
                "Result: Synthetic AUROC >0.99, but Real Test Defect AUROC = 0.5758 (0.00% transfer gain over equal weighting)."
            ],
            "chart_guide": "Explain the 5 subplots in Figure 7 on the right: show that while synthetic optimization converges, the real defect AUROC curves remain flat.",
            "viva_qa": [
                ("Q: Why does a negative result have academic value?",
                 "A: Scientific progress relies on refuting invalid hypotheses just as much as proving valid ones. By executing 444 systematic runs across 4 mathematical solvers, we conclusively prove that synthetic Gaussian noise cannot serve as a proxy for real industrial defects.")
            ]
        },
        {
            "num": 8,
            "title": "Slide 8 — Deep Learning Benchmark & Performance",
            "timing": "7:00 – 8:00 (1 Minute)",
            "script": (
                "\"Slide 8 presents the quantitative benchmark comparing our three deep learning paradigms across the 12 MVTec AD categories.\n\n"
                "PatchCore is our sovereign top-performing model: It achieves a macro Image AUROC of 0.9769, a Pixel AUROC of 0.9721, "
                "and an optimal F1-score of 0.8221, while maintaining an inference latency of 85 milliseconds. In fact, PatchCore achieved "
                "perfect 1.0000 AUROC on 5 out of 12 categories: bottle, hazelnut, leather, metal nut, and transistor.\n\n"
                "PaDiM proved to be our most powerful spatial localization model, delivering an outstanding 0.9619 Pixel AUROC and 0.9082 Image AUROC. "
                "Because PaDiM fits localized Gaussians directly during training, it requires no k-nearest neighbor search phase during inference.\n\n"
                "The Convolutional Autoencoder exhibited a distinct operational trade-off: It is by far the fastest model at 18.0 milliseconds "
                "per image—delivering 55 frames per second on our RTX 4060 GPU. While it achieved 0.9333 AUROC on the rigid bottle category using our "
                "5-level multi-scale loss, its macro AUROC across all 12 categories was 0.6149 because it struggles to reconstruct complex, non-rigid "
                "textural patterns like carpet or grid without introducing blurry artifacts.\""
            ),
            "tech_points": [
                "PatchCore (ResNet-18, 5% coreset): 0.9769 Image AUROC, 0.9721 Pixel AUROC, 0.8221 F1, 85 ms latency. Perfect 1.0000 on 5 categories.",
                "PaDiM (ResNet-18, 100 dims): 0.9082 Image AUROC, 0.9619 Pixel AUROC, 0.8203 F1, 95 ms latency.",
                "ConvAE (5-level multi-loss): 0.6149 Image AUROC, 0.7220 Pixel AUROC, 0.2899 F1, 18 ms latency (55 FPS throughput)."
            ],
            "chart_guide": "Refer to the two bar charts on the right: the left compares Image vs Pixel AUROC; the right shows inference latency (18 ms for ConvAE vs 85 ms for PatchCore).",
            "viva_qa": [
                ("Q: Why does PatchCore outperform PaDiM on Image AUROC (0.9769 vs 0.9082)?",
                 "A: PaDiM fits a unimodal Gaussian distribution per spatial location. If an object has slight positional jitter or rotation, the Gaussian covariance expands, diminishing anomaly sensitivity. PatchCore uses non-parametric memory tokens, making it invariant to localized translations.")
            ]
        },
        {
            "num": 9,
            "title": "Slide 9 — Multi-Paradigm Hybrid Score Fusion",
            "timing": "8:00 – 9:00 (1 Minute)",
            "script": (
                "\"Slide 9 details our multi-paradigm hybrid ensembling framework.\n\n"
                "In industrial deployments, relying on a single model can be hazardous: lighting reflections, minor vibrations, or edge contours "
                "can trigger false positive alarms. We evaluated whether fusing diverse paradigms—reconstruction, memory banks, and probabilistic Gaussians—could "
                "enhance operational robustness.\n\n"
                "Before ensembling, raw model scores were standardized via min-max normalization. We evaluated three fusion strategies:\n"
                "Hybrid-Mean (HY-01), which averages the three models, achieved 0.9586 AUROC. Hybrid-Max (HY-02), which takes the maximum anomaly score, "
                "achieved 0.9421 AUROC. Hybrid-Weighted (HY-03), allocating weights of 0.20 to Autoencoder, 0.40 to PatchCore, and 0.40 to PaDiM, "
                "achieved 0.9626 AUROC.\n\n"
                "While standalone PatchCore has a slightly higher raw macro AUROC (0.9769 vs 0.9626), HY-03 is our most operationally reliable system. "
                "By combining three distinct error distributions, it suppresses single-model false alarm outliers and secures 100% defect recall "
                "across all 12 categories, preventing costly false factory line shutdowns.\""
            ),
            "tech_points": [
                "Score normalization: Standardized via training set bounds: S_norm = (S - mu) / sigma.",
                "HY-01 (Mean): S_mean = 1/3 * (S_AE + S_PC + S_PaDiM) -> 0.9586 AUROC, F1: 0.8186.",
                "HY-02 (Max): S_max = max(S_AE, S_PC, S_PaDiM) -> 0.9421 AUROC, F1: 0.8190.",
                "HY-03 (Weighted): S_w = 0.20 S_AE + 0.40 S_PC + 0.40 S_PaDiM -> 0.9626 AUROC, F1: 0.8180 (100% recall)."
            ],
            "chart_guide": "Highlight the bar chart on the right: point out the highlighted blue bar for HY-03 and explain how it balances standalone model performance.",
            "viva_qa": [
                ("Q: Why not use a learnable neural network to fuse the scores instead of fixed weights (0.2/0.4/0.4)?",
                 "A: A learnable meta-classifier requires defective training samples to learn the optimal fusion boundary. Under our strict normal-only unsupervised protocol, no defects exist during training. Fixed heuristic weighting based on validation stability preserves strict unsupervised integrity.")
            ]
        },
        {
            "num": 10,
            "title": "Slide 10 — Qualitative Defect Localization & Visual Analysis",
            "timing": "9:00 – 10:00 (1 Minute)",
            "script": (
                "\"Slide 10 is our qualitative visual analysis, displaying side-by-side defect heatmaps generated on the MVTec AD bottle category.\n\n"
                "The columns from left to right display: Original Input Image, Ground Truth Binary Mask, Autoencoder Reconstruction Error Map, "
                "PatchCore Heatmap, and PaDiM Heatmap.\n\n"
                "Let us examine three distinct defect case studies:\n"
                "In Row 1, we show a severe structural fracture (broken_large). Both PatchCore and PaDiM generate sharp, concentrated heatmaps "
                "that overlap precisely with the ground-truth fracture contour. The Autoencoder detects the general region but exhibits diffuse boundaries.\n\n"
                "In Row 2, we show localized surface contamination. High-contrast foreign particles on the transparent glass are isolated with "
                "near 100% pixel precision by PatchCore's memory tokens.\n\n"
                "In Row 3, we analyze an empirical failure case: a subtle edge chip (broken_small). Notice the Autoencoder column: it produces "
                "a prominent circular halo around the normal lip of the bottle—a false alarm caused by high-frequency edge reconstruction blur. "
                "In contrast, PatchCore's deep feature representations ignore the nominal contour and pinpoint the small chipped defect accurately.\""
            ),
            "tech_points": [
                "Columns: Input -> Ground Truth -> ConvAE Error -> PatchCore Heatmap -> PaDiM Heatmap.",
                "Row 1: broken_large (severe fracture, SOTA localization across PatchCore and PaDiM).",
                "Row 2: contamination (surface impurity, high-contrast token separation).",
                "Row 3: broken_small (failure mode: Autoencoder exhibits boundary edge blur halo; PatchCore maintains localization fidelity)."
            ],
            "chart_guide": "Guide evaluators through the rows: point out Row 1 for structural cracks, Row 2 for surface dirt, and Row 3 to demonstrate honest failure analysis.",
            "viva_qa": [
                ("Q: Why does the Autoencoder produce false-positive halos along normal bottle contours in Row 3?",
                 "A: Convolutional decoders struggle with high-frequency spatial gradients. Even a minor sub-pixel misalignment between input and reconstruction creates large residual L2/L1 errors along high-contrast object borders, triggering false boundary alarms.")
            ]
        },
        {
            "num": 11,
            "title": "Slide 11 — Edge Network Transmission & Denoising Discovery",
            "timing": "10:00 – 11:00 (1 Minute)",
            "script": (
                "\"Slide 11 addresses the computer networks component: evaluating the feasibility of edge-to-server image transmission.\n\n"
                "In smart factories, cameras on manufacturing lines capture images and transmit them across local networks to GPU servers for inference. "
                "We simulated an industrial manufacturing environment with a 10 Mbps edge uplink bandwidth and a 50 ms round-trip latency.\n\n"
                "Transmitting uncompressed PNG images incurs an average file size of 88.8 KB, taking 71 ms to transmit and resulting in a total "
                "end-to-end latency of 157.8 ms—too slow for a standard 10 Hz industrial conveyor line.\n\n"
                "Applying JPEG compression drastically slashes file size and latency: JPEG Q95 cuts latency to 98.4 ms, and JPEG Q75 cuts latency "
                "to 89.9 ms—an 11.2-fold size reduction and a 43.0% drop in total latency.\n\n"
                "Most excitingly, look at the line chart on the right: JPEG Q75 produces an 'Edge Denoising Effect,' where Image AUROC actually "
                "improves from 0.7515 at uncompressed PNG to 0.7970 at Q75—a 4.55% gain! The moderate Discrete Cosine Transform quantization acts as an "
                "edge-preserving low-pass filter, attenuating high-frequency camera sensor noise without corrupting physical defect boundaries. "
                "However, if compression is pushed too far (JPEG Q50), 8x8 block artifacts appear, causing AUROC to drop to 0.7455.\""
            ),
            "tech_points": [
                "Network simulation: 10 Mbps bandwidth, 50 ms RTT, 4 formats (PNG, JPEG Q95, Q75, Q50).",
                "Original PNG: 88.8 KB, Total Latency 157.8 ms, AUROC 0.7515.",
                "JPEG Q75: 7.9 KB (11.2x compression), Total Latency 89.9 ms (43.0% reduction), AUROC 0.7970 (+4.55% gain).",
                "JPEG Q50: 5.6 KB, Total Latency 86.7 ms, AUROC drops to 0.7455 due to block artifacts."
            ],
            "chart_guide": "Refer to the two plots on the right: the left bar chart shows the 43.0% drop in end-to-end latency; the right line chart highlights the peak at Q75 showing the +4.55% denoising gain.",
            "viva_qa": [
                ("Q: Did JPEG compression degrade defect detection accuracy?",
                 "A: Counterintuitively, no—it improved it up to Q75! Moderate JPEG quantization suppresses high-frequency camera sensor thermal noise, which otherwise causes false positives in raw images. Only aggressive compression (Q50 and below) degrades performance due to block artifacts.")
            ]
        },
        {
            "num": 12,
            "title": "Slide 12 — Summary of Contributions & Future Scope",
            "timing": "11:00 – 12:00 (1 Minute)",
            "script": (
                "\"In conclusion, on Slide 12, let us summarize the major contributions of this project and outline practical deployment guidelines.\n\n"
                "Scientifically, our work has accomplished three major milestones:\n"
                "First, we established that PatchCore (0.9769 AUROC) and PaDiM (0.9619 Pixel AUROC) set the state-of-the-art benchmark for unsupervised "
                "industrial inspection across 12 authentic categories.\n"
                "Second, we conclusively disproved synthetic DIP feature-weight optimization across 444 parameter sweeps, proving that synthetic "
                "perturbations cannot model physical defects.\n"
                "Third, we discovered the JPEG Q75 'Edge Denoising Effect,' which reduces network latency by 43.0% while improving detection fidelity by 4.55%.\n\n"
                "For practical factory deployments, we recommend:\n"
                "Deploying PatchCore or HY-03 on GPU edge servers for high-precision critical parts running at 7 to 12 parts per second, and deploying "
                "5-level ConvAE on low-power IoT hardware for ultra-high-speed preliminary screening at 55 frames per second.\n\n"
                "Looking ahead, our research roadmap includes exploring zero-shot foundation models like WinCLIP, implementing INT8 TensorRT quantization "
                "for sub-10ms inference on NVIDIA Jetson modules, and validating transmission across physical 5G Time-Sensitive Networks.\n\n"
                "Thank you very much for your time and attention. I am now open to your questions and technical discussion.\""
            ),
            "tech_points": [
                "Three milestones: SOTA benchmark validation, theoretical disproof of synthetic optimization, edge denoising discovery.",
                "Deployment guidelines: PatchCore/HY-03 for precision (GPU edge); ConvAE for high-throughput screening (55 FPS).",
                "Future scope: Vision-language zero-shot models (WinCLIP), TensorRT INT8 quantization, physical 5G TSN field validation."
            ],
            "chart_guide": "Direct attention to the three structured summary cards and close with the GitHub open-source repository link at the bottom.",
            "viva_qa": [
                ("Q: If an industrial client has only $500 for hardware, which model would you deploy?",
                 "A: ConvAE or PaDiM CPU-quantized. ConvAE runs at 18 ms per image and requires minimal memory, running comfortably on an entry-level edge processor like an Intel N100 or Raspberry Pi 5 with an OpenVINO accelerator.")
            ]
        }
    ]

    for s_info in slide_details:
        p_s_hdr = doc.add_paragraph()
        p_s_hdr.paragraph_format.space_before = Pt(14)
        p_s_hdr.paragraph_format.space_after = Pt(2)
        r_sn = p_s_hdr.add_run(s_info["title"])
        r_sn.font.bold = True
        r_sn.font.size = Pt(14)
        r_sn.font.color.rgb = NAVY

        p_time = doc.add_paragraph()
        p_time.paragraph_format.space_after = Pt(6)
        r_tm = p_time.add_run(f"Pacing & Timeline: {s_info['timing']}")
        r_tm.font.bold = True
        r_tm.font.size = Pt(9.5)
        r_tm.font.color.rgb = BLUE

        # Spoken Script Callout
        add_callout(doc, "ORAL PRESENTATION SCRIPT (VERBATIM / TALKING POINTS)",
                    s_info["script"], bg_hex="F8FAFC", border_hex="2563EB")

        # Technical Details
        p_td = doc.add_paragraph()
        p_td.paragraph_format.space_before = Pt(4)
        p_td.paragraph_format.space_after = Pt(2)
        r_td_lbl = p_td.add_run("Crucial Technical & Mathematical Details:")
        r_td_lbl.font.bold = True
        r_td_lbl.font.size = Pt(10.5)
        r_td_lbl.font.color.rgb = NAVY

        for pt in s_info["tech_points"]:
            p_bullet = doc.add_paragraph(style='List Bullet')
            p_bullet.paragraph_format.space_before = Pt(1)
            p_bullet.paragraph_format.space_after = Pt(2)
            r_b = p_bullet.add_run(pt)
            r_b.font.size = Pt(9.5)
            r_b.font.color.rgb = SLATE

        # Chart interpretation
        p_ci = doc.add_paragraph()
        p_ci.paragraph_format.space_before = Pt(4)
        p_ci.paragraph_format.space_after = Pt(2)
        r_ci = p_ci.add_run("How to Guide Evaluators Through the Visuals & Charts:")
        r_ci.font.bold = True
        r_ci.font.size = Pt(10.5)
        r_ci.font.color.rgb = NAVY

        p_cg = doc.add_paragraph()
        p_cg.paragraph_format.space_after = Pt(4)
        r_cgt = p_cg.add_run(s_info["chart_guide"])
        r_cgt.font.size = Pt(9.5)
        r_cgt.font.italic = True
        r_cgt.font.color.rgb = SLATE

        # Viva Q&A
        p_viva = doc.add_paragraph()
        p_viva.paragraph_format.space_before = Pt(4)
        p_viva.paragraph_format.space_after = Pt(2)
        r_vq = p_viva.add_run("Anticipated Evaluator Viva Questions & Model Answers:")
        r_vq.font.bold = True
        r_vq.font.size = Pt(10.5)
        r_vq.font.color.rgb = CORAL

        for q, a in s_info["viva_qa"]:
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(3)
            p_q.paragraph_format.space_after = Pt(1)
            r_q = p_q.add_run(q)
            r_q.font.bold = True
            r_q.font.size = Pt(9.5)
            r_q.font.color.rgb = NAVY

            p_a = doc.add_paragraph()
            p_a.paragraph_format.space_after = Pt(6)
            r_a = p_a.add_run(a)
            r_a.font.size = Pt(9.5)
            r_a.font.color.rgb = SLATE

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    doc.save(DOCX_OUT)
    print(f"Presentation speaker notes successfully saved to: {DOCX_OUT}")

if __name__ == '__main__':
    build_notes_document()

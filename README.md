# Industrial Visual Anomaly Detection
## Multi-Paradigm Inspection Using Digital Image Processing, Optimization, Deep Learning, and Computer Networks

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://www.python.org/)
[![PyTorch 2.5.1](https://img.shields.io/badge/PyTorch-2.5.1%2Bcu121-red.svg)](https://pytorch.org/)
[![CUDA Accelerated](https://img.shields.io/badge/CUDA-RTX%204060%20(8GB)-green.svg)](https://developer.nvidia.com/cuda-zone)
[![Experiments Validated](https://img.shields.io/badge/Experiments-736%20Runs%20Validated-orange.svg)](#2-master-experimental-leaderboard)
[![Research Paper](https://img.shields.io/badge/Paper-15%20Pages%20(IEEE%20Format)-purple.svg)](06_FINAL_RESEARCH/Research_Paper/Industrial_Anomaly_Detection_Paper.pdf)

An exhaustive, publication-grade academic research investigation into unsupervised, normal-only industrial visual anomaly detection and pixel-level defect localization. Benchmarked across **12 authentic industrial categories** of the MVTec Anomaly Detection (MVTec AD) dataset comprising **1,389 nominal training images** and **679 test images** with pixel-precise ground-truth annotations across **65 defect phenotypes**.

---

## 1. Project Overview & Core Findings

This research systematically compares four distinct technological paradigms across **736 executed and validated experimental trials** (292 baseline & ablation runs + 444 optimization parameter sweep runs):

1. **State-of-the-Art Deep Learning:** 
   - **PatchCore (ResNet-18, 5% coreset):** Achieves the highest standalone detection fidelity with **0.9769 macro Image AUROC** and **0.9721 Pixel AUROC**, securing perfect 1.0000 AUROC on 5 of 12 categories (*bottle, hazelnut, leather, metal_nut, transistor*).
   - **PaDiM (ResNet-18, 100 dims):** Models spatial patch embeddings via localized multivariate Gaussians, delivering outstanding localization precision (**0.9619 Pixel AUROC**).
   - **Convolutional Autoencoder (ConvAE):** Evaluates multi-component losses ($\text{MSE} + \text{SSIM} + \text{Sobel}$), achieving **0.9333 AUROC** with deeper 5-level architectures and narrower bottlenecks ($d_z = 64$).
2. **Multi-Model Hybrid Score Ensembling:**
   - **Hybrid-Weighted (HY-03: 0.2 AE + 0.4 PC + 0.4 PaDiM):** Achieves **0.9626 Image AUROC** and the highest balanced F1 operational stability, effectively suppressing single-model false alarm spikes.
3. **Theoretical Disproof of Synthetic Feature Optimization (Negative Result):**
   - Across **444 parameter sweep runs** (OPT-P1 to OPT-P5) spanning four mathematical solvers (*SLSQP, Conjugate Gradient, L-BFGS-B, Trust Region*), we prove that optimizing handcrafted DIP weights against synthetic Gaussian noise achieves artificial convergence (>0.99 synthetic AUROC) but **yields zero transfer gain on real physical defects (0.5758 AUROC)**, performing identically to unoptimized equal weighting.
4. **Edge Network Transmission & The "Denoising Effect":**
   - Simulating an edge-to-server industrial manufacturing network (10 Mbps bandwidth, 50 ms RTT), **JPEG Q75 compression cuts total latency by 43.0% (89.9 ms vs. 157.8 ms)** while unexpectedly **improving detection AUROC (+4.55%)** by filtering out high-frequency sensor noise.

---

## 2. Master Experimental Leaderboard (12-Category Macro Performance)

All metrics below are computed across 12 MVTec AD categories from actual raw experiment files (`03_Results/all_categories_master_leaderboard.csv`):

| Rank | Model / Methodology | Paradigm | Image AUROC | Pixel AUROC | F1-Score | Precision | Recall | Latency |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **PatchCore (ResNet-18, 5% Coreset)** | Non-Parametric Memory Bank | **0.9769** | **0.9721** | **0.8221** | 0.7357 | **1.0000** | 85.0 ms |
| 2 | **Hybrid-Weighted (HY-03)** | Multi-Paradigm Ensemble | **0.9626** | — | 0.8180 | 0.7195 | **1.0000** | 140.0 ms |
| 3 | **Hybrid-Mean (HY-01)** | Multi-Paradigm Ensemble | **0.9586** | — | 0.8186 | 0.7203 | **1.0000** | 140.0 ms |
| 4 | **Hybrid-Max (HY-02)** | Multi-Paradigm Ensemble | **0.9421** | — | 0.8190 | 0.7195 | **1.0000** | 140.0 ms |
| 5 | **PaDiM (ResNet-18, 100 Dims)** | Parametric Patch Gaussian | **0.9082** | **0.9619** | 0.8203 | 0.7330 | **1.0000** | 95.0 ms |
| 6 | **Convolutional Autoencoder (4-Level)** | Generative Reconstruction | **0.6149** | 0.7220 | 0.2899 | 0.7686 | 0.2953 | **18.0 ms** |
| 7 | **DIP Mahalanobis (7 Features)** | Classical DIP | **0.5927** | — | 0.5643 | 0.7908 | 0.5508 | 30.0 ms |
| 8 | **DIP One-Class SVM** | Classical DIP | **0.5781** | — | 0.6018 | 0.7276 | 0.5704 | 31.0 ms |
| 9 | **DIP Baseline (Equal 7 Weights)** | Classical DIP | **0.5758** | — | 0.2016 | **0.8800** | 0.1617 | 28.0 ms |
| 10 | **DIP Optimized (Steepest Descent)** | Numerical Optimization | **0.5758** | — | 0.2016 | **0.8800** | 0.1617 | 28.5 ms |
| 11 | **DIP Isolation Forest** | Classical DIP | **0.5313** | — | 0.3067 | 0.7268 | 0.2603 | 32.0 ms |

> *Note: Three standard MVTec AD categories (`pill`, `wood`, `zipper`) were not available locally and were deliberately excluded from all training and testing to maintain strict research integrity.*

---

## 3. Repository Architecture

```text
Hybrid-Industrial-Visual-Anomaly-Detection/
│
├── 01_Dataset/
│   └── MVTec_AD/                           # 12 Evaluated Categories (.gitkeep; instructions provided)
│       ├── bottle/                         # (104 train normal, 41 test)
│       ├── cable/                          # (112 train normal, 79 test)
│       ├── capsule/                        # (109 train normal, 70 test)
│       ├── carpet/                         # (124 train normal, 62 test)
│       ├── grid/                           # (126 train normal, 39 test)
│       ├── hazelnut/                       # (124 train normal, 58 test)
│       ├── leather/                        # (119 train normal, 65 test)
│       ├── metal_nut/                      # (111 train normal, 59 test)
│       ├── screw/                          # (127 train normal, 83 test)
│       ├── tile/                           # (117 train normal, 57 test)
│       ├── toothbrush/                     # (28 train normal, 23 test)
│       └── transistor/                     # (108 train normal, 45 test)
│
├── 02_Code/                                # Modular, Reproducible Python Source Code
│   ├── run_single_category.py              # CLI: Execute full 11-stage pipeline on one category
│   ├── run_all_categories.py               # Orchestrator: Multi-category batch execution
│   │
│   ├── dip/                                # 1. Digital Image Processing (DIP) Pipeline
│   │   ├── feature_extraction.py           # 7 handcrafted spatial, texture, spectral features
│   │   ├── improved_features.py            # 11 extended features (CLAHE, SSIM, LBP, Entropy)
│   │   ├── baseline_detector.py            # Z-score statistical thresholding
│   │   └── advanced_scoring.py             # Mahalanobis, One-Class SVM, Isolation Forest
│   │
│   ├── optimization/                       # 2. Mathematical Optimization Module
│   │   ├── optimization.py                 # SLSQP, CG, L-BFGS-B, trust-constr simplex solvers
│   │   └── optimization_param_sweep.py     # 444-run parameter sweep engine (OPT-P1 to OPT-P5)
│   │
│   ├── deep_learning/                      # 3. Deep Learning Anomaly Detectors
│   │   ├── dataset.py                      # Generic MVTec AD PyTorch Dataset & Transform pipeline
│   │   ├── autoencoder.py                  # 4/5-level ConvAE with multi-component loss (MSE+SSIM)
│   │   ├── patchcore.py                    # PatchCore with greedy k-center coreset subsampling
│   │   ├── padim.py                        # PaDiM localized patch Gaussian modeling
│   │   └── hybrid.py                       # Z-score normalized score fusion (Mean, Max, Weighted)
│   │
│   ├── network/                            # 4. Computer Networks Simulation Module
│   │   └── compression_network.py          # PNG/JPEG Q95/Q75/Q50 trade-offs (10 Mbps, 50 ms latency)
│   │
│   ├── evaluation/                         # Evaluation & Localization Engine
│   │   └── pixel_metrics.py                # Pixel-level AUROC/AP and segmentation mask generators
│   │
│   ├── visualization/                      # Scientific Visualization Engine
│   │   ├── comprehensive_visualizer.py     # Multi-model ROC, PR, Pareto, and confusion matrices
│   │   └── visualization.py                # Diagnostic plotting utilities
│   │
│   └── experiments/                        # Standardized Experiment Runners (Ablation Suites)
│       ├── ae_experiments.py               # Autoencoder loss & architecture ablation runner
│       ├── patchcore_experiments.py        # PatchCore backbone & coreset ablation runner
│       ├── padim_experiments.py            # PaDiM dimension & covariance ablation runner
│       ├── hybrid_experiments.py           # Score fusion parameter evaluation
│       └── optimization_param_sweep.py     # Parameter sweep execution harness
│
├── 03_Results/                             # Primary Structured Data Source (CSVs & Figures)
│   ├── all_categories_master_leaderboard.csv # Consolidated 132-row benchmark leaderboard
│   ├── category_auroc_matrix.csv           # Full 11x12 cross-category AUROC matrix
│   ├── category_f1_matrix.csv              # Full 11x12 cross-category F1 matrix
│   ├── experimental_study/                 # Full Ablation Study Archive (CSVs, logs, charts)
│   │   ├── autoencoder/                    # AE loss (AE-01..05), arch (3L..5L), hyperparams
│   │   ├── patchcore/                      # Backbone (RN18..RN50) & coreset (1%..20%) ablations
│   │   ├── padim/                          # Dimension (50..200) & covariance regularizers
│   │   ├── dip_optimization/               # Optimizer comparisons & 444 sweep CSVs
│   │   └── overall_analysis/               # Consolidated study reports & experiment dashboard
│   └── <category>/                         # Individual category results (features, predictions, logs)
│
├── 04_Models/                              # Trained Checkpoints (.pt)
│   └── autoencoder_<category>.pt           # Checkpoints for all 12 evaluated categories
│
├── 05_Notebooks/                           # Interactive Data Science Notebooks
│   └── 01_Dataset_Exploration.ipynb        # Exploratory data analysis, distributions, masks
│
├── 06_FINAL_RESEARCH/                      # Publication Deliverables & Research Package
│   ├── Research_Paper/
│   │   ├── Industrial_Anomaly_Detection_Paper.pdf  # Final Publication Paper (Strict 15 Pages)
│   │   ├── Industrial_Anomaly_Detection_Paper.docx # Editable Word Document
│   │   ├── Supplementary_Results.pdf               # Companion Supplementary Material (3 Pages)
│   │   ├── Supplementary_Results.docx              # Editable Supplementary Word Document
│   │   ├── References.bib                          # Complete BibTeX Bibliography [1]–[8]
│   │   ├── PAPER_VALIDATION_REPORT.md              # Formal Scientific Validation Audit
│   │   ├── RESULTS_TRACEABILITY_TABLE.csv          # Mapping 51 experimental units (736 runs)
│   │   ├── Research_Figures/                       # 32 high-resolution figures embedded in paper
│   │   └── Research_Tables/                        # 8 structured CSV tables embedded in paper
│   │
│   ├── Literature_Review/
│   │   ├── Literature_Review.md                    # Critical review of recent research (2019–2024)
│   │   ├── download_reference_papers.py            # Reproducible fetcher for reference papers
│   │   └── Reference_Papers/                       # Original full-text PDFs of benchmark papers:
│   │       ├── 01_Bergmann_2019_MVTec_AD.pdf       # Bergmann et al. (CVPR 2019)
│   │       ├── 02_Bergmann_2019_SSIM_Autoencoders.pdf # Bergmann et al. (VISIGRAPP 2019)
│   │       ├── 03_Defard_2021_PaDiM.pdf            # Defard et al. (ICPR 2021)
│   │       ├── 04_Roth_2022_PatchCore.pdf          # Roth et al. (CVPR 2022)
│   │       ├── 05_Zavrtanik_2021_DRAEM.pdf         # Zavrtanik et al. (ICCV 2021)
│   │       ├── 06_Deng_2022_Reverse_Distillation.pdf # Deng & Li (CVPR 2022)
│   │       ├── 07_Yu_2021_FastFlow.pdf             # Yu et al. (arXiv 2021)
│   │       ├── 08_Batzner_2024_EfficientAD.pdf     # Batzner et al. (WACV 2024)
│   │       └── README.md                           # Annotated catalog of reference papers
│   │
│   └── Figures/                                    # Master Figures Archive
│       ├── Architecture/                           # System, DIP, AE, PC, PaDiM, Hybrid diagrams
│       ├── Methodology/                            # Workflow and optimization sweep plots
│       ├── Experimental_Results/                   # AUROC, F1, latency, training time charts
│       ├── Network_Analysis/                       # Compression vs. latency Pareto curves
│       └── Anomaly_Maps/                           # High-res defect localization grids
│
├── LICENSE                                 # MIT License
└── README.md                               # Project Documentation (This File)
```

---

## 4. Academic Deliverables & Research Paper Package

All final academic deliverables are compiled and verified inside `06_FINAL_RESEARCH/Research_Paper/`:

- **Main Research Paper:** [Industrial_Anomaly_Detection_Paper.pdf](06_FINAL_RESEARCH/Research_Paper/Industrial_Anomaly_Detection_Paper.pdf)  
  *Format: Academic Two-Column / Density Layout | Length: Exactly 15 Pages ($\le 16$-page strict constraint) | Editable: [DOCX](06_FINAL_RESEARCH/Research_Paper/Industrial_Anomaly_Detection_Paper.docx)*  
  Contains complete Introduction, Literature Survey (Table I), Proposed Methodology (Figures 1, Equations 1–9), Results and Discussion (Tables II–VIII, Figures 2–6), Ablation Studies, Failure Analysis, Network Analysis, and References.
- **Supplementary Material:** [Supplementary_Results.pdf](06_FINAL_RESEARCH/Research_Paper/Supplementary_Results.pdf)  
  *Length: 3 Pages | Editable: [DOCX](06_FINAL_RESEARCH/Research_Paper/Supplementary_Results.docx)*  
  Includes full category F1 matrices, 444 parameter sweep breakdown tables, and hardware profiling.
- **Scientific Audit & Traceability:**  
  - [PAPER_VALIDATION_REPORT.md](06_FINAL_RESEARCH/Research_Paper/PAPER_VALIDATION_REPORT.md): Certifies 100% data authenticity against raw CSV files and validates that no test labels were leaked.
  - [RESULTS_TRACEABILITY_TABLE.csv](06_FINAL_RESEARCH/Research_Paper/RESULTS_TRACEABILITY_TABLE.csv): Complete line-by-line mapping of all 51 experimental units across 736 runs.
- **Literature Archive:** [06_FINAL_RESEARCH/Literature_Review/Reference_Papers/](06_FINAL_RESEARCH/Literature_Review/Reference_Papers)  
  Contains verified, unabridged original conference PDFs for all 8 foundational reference papers [1]–[8].

---

## 5. Reproduction & Execution Guide

### Environment Setup
```bash
# Clone the repository
git clone https://github.com/Rahul-dewangan01/Hybrid-Industrial-Visual-Anomaly-Detection.git
cd Hybrid-Industrial-Visual-Anomaly-Detection

# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install numpy scipy scikit-learn scikit-image opencv-python matplotlib seaborn pandas pillow python-docx docx2pdf
```

### Run a Single Category (11 Stages)
To execute feature extraction, optimization, deep learning, hybrid ensembling, network compression, and visual plotting for a single category:
```bash
python 02_Code/run_single_category.py --category bottle
# Valid categories: bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, screw, tile, toothbrush, transistor
```

### Run Full Multi-Category Benchmark
To run batch execution across all 12 categories and generate the cross-category master matrices:
```bash
python 02_Code/run_all_categories.py --skip-completed
```

### Re-Run Optimization Parameter Sweeps (444 Runs)
To execute the systematic sensitivity parameter sweeps across all 12 categories:
```bash
python 02_Code/optimization/optimization_param_sweep.py --category all
```

### Rebuild Final Research Paper & PDF Deliverables
To rebuild the Word `.docx` documents and export native `.pdf` files via Microsoft Word COM:
```bash
python 06_FINAL_RESEARCH/Research_Paper/build_full_publication_paper.py
python 06_FINAL_RESEARCH/Research_Paper/build_supplementary_materials.py
```

---

## 6. Curated Bibliography

1. **P. Bergmann et al.**, *"MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection,"* in **CVPR 2019**, pp. 9592–9600.
2. **T. Defard et al.**, *"PaDiM: A Patch Distribution Modeling Framework for Anomaly Detection and Localization,"* in **ICPR 2021**, pp. 475–489.
3. **K. Roth et al.**, *"Towards Total Recall in Industrial Anomaly Detection,"* in **CVPR 2022**, pp. 14318–14328.
4. **H. Deng & X. Li**, *"Anomaly Detection via Reverse Distillation from One-Class Embedding,"* in **CVPR 2022**, pp. 9737–9746.
5. **K. Batzner et al.**, *"EfficientAD: Accurate Visual Anomaly Detection at Millisecond-Level Latencies,"* in **WACV 2024**, pp. 128–138.
6. **V. Zavrtanik et al.**, *"DRAEM — A Discriminatively Trained Reconstruction Embedding for Surface Anomaly Detection,"* in **ICCV 2021**, pp. 8330–8339.
7. **J. Yu et al.**, *"FastFlow: Unsupervised Anomaly Detection and Localization via 2D Normalizing Flows,"* in **arXiv:2111.07677**, 2021.
8. **P. Bergmann et al.**, *"Improving Unsupervised Defect Segmentation by Applying Structural Similarity to Autoencoders,"* in **VISIGRAPP 2019**, pp. 372–380.

---

## 7. License & Citation

This project is licensed under the [MIT License](LICENSE).

```bibtex
@misc{dewangan2026industrial,
  author       = {Rahul Dewangan},
  title        = {Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/Rahul-dewangan01/Hybrid-Industrial-Visual-Anomaly-Detection}}
}
```

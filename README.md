# Industrial Anomaly Detection
## Using Digital Image Processing, Optimization, and Computer Networks

**Dataset:** MVTec Anomaly Detection (12 Evaluated Industrial Categories)  
**Academic Disciplines:** Digital Image Processing (DIP) | Optimization (ACOMA / Numerical Optimization) | Computer Networks (CN) | Deep Learning  
**Hardware Acceleration:** NVIDIA GeForce RTX 4060 Laptop GPU (CUDA 12.1)  
**Academic Year:** 2024–25 | 3rd Year, Sem 5

---

## 1. Clean Project Architecture

```
project/
│
├── 01_Dataset/                     ← MVTec AD Benchmark Dataset
│   └── MVTec_AD/                   ← 12 Evaluated Categories (bottle, cable, capsule, carpet,
│                                      grid, hazelnut, leather, metal_nut, screw, tile,
│                                      toothbrush, transistor)
│
├── 02_Code/                        ← All Clean Modular Python Source Code
│   │
│   ├── run_single_category.py      ← Primary Entrypoint: Run full 11 stages for one category
│   ├── run_all_categories.py       ← Primary Entrypoint: Multi-category batch orchestrator
│   │
│   ├── dip/                        ← 1. Digital Image Processing (DIP) Module
│   │   ├── feature_extraction.py   ← Baseline 7-feature spatial/frequency extractor
│   │   ├── improved_features.py    ← Enhanced 11-feature extractor (CLAHE, SSIM, LBP, Entropy)
│   │   ├── baseline_detector.py    ← Z-score feature deviation detector & thresholding
│   │   └── advanced_scoring.py     ← Mahalanobis distance, Isolation Forest, One-Class SVM
│   │
│   ├── optimization/               ← 2. Numerical Optimization (ACOMA) Module
│   │   └── optimization.py         ← Feature weight tuning on synthetic pseudo-anomalies
│   │                                  (SLSQP Steepest Descent, Conjugate Gradient, BFGS, trust-constr)
│   │
│   ├── network/                    ← 3. Computer Networks (CN) Module
│   │   ├── compression_network.py  ← Lossy/lossless JPEG quality compression trade-off analysis,
│   │   │                              network bandwidth (10 Mbps) & latency (50 ms) simulation
│   │   └── __init__.py
│   │
│   ├── deep_learning/              ← Deep Learning & Ensembles Module
│   │   ├── dataset.py              ← Generic MVTec AD PyTorch Dataset & DataLoader
│   │   ├── autoencoder.py          ← Convolutional Autoencoder (reconstruction error & heatmap)
│   │   ├── patchcore.py            ← PatchCore with ResNet-18 coreset memory bank
│   │   ├── padim.py                ← PaDiM with patch multivariate Gaussian modeling
│   │   ├── hybrid.py               ← Multi-paradigm score fusion (Mean, Max, Weighted)
│   │   └── __init__.py
│   │
│   ├── evaluation/                 ← Evaluation & Localization Module
│   │   └── pixel_metrics.py        ← Pixel-level AUROC/AP and side-by-side localization comparison
│   │
│   ├── visualization/              ← Visual Analytics Module
│   │   ├── comprehensive_visualizer.py ← 20+ Publication-quality figures (ROC, PR, Pareto, Confusion)
│   │   └── visualization.py        ← Basic diagnostic charts
│   │
│   └── utils/                      ← Shared Helpers & Category Config
│       ├── config.py               ← CategoryConfig factory, device selection, paths
│       ├── feature_analysis.py     ← Correlation heatmaps, AUROC rankings, redundancy dendrograms
│       ├── generate_reports.py     ← Summary tables and markdown reports
│       └── run_master_experiments.py ← Category-aware 11-stage pipeline logic
│
├── 03_Results/                     ← Clean Results Directory (No Clutter)
│   │
│   ├── all_categories_master_leaderboard.csv ← Concatenated 132-experiment master leaderboard
│   ├── category_auroc_matrix.csv   ← Cross-category AUROC matrix (11 models x 12 categories)
│   ├── category_f1_matrix.csv      ← Cross-category F1 score matrix (11 models x 12 categories)
│   ├── multicategory_auroc_heatmap.png ← Cross-category AUROC comparison heatmap
│   ├── multicategory_f1_heatmap.png    ← Cross-category F1 comparison heatmap
│   ├── multicategory_summary.json  ← Execution timings & metadata
│   │
│   ├── bottle/                     ← Per-category structured experimental results
│   ├── cable/                      │  ├── charts/ (comprehensive_suite, feature_analysis, etc.)
│   ├── capsule/                    │  ├── compression/ (compression_results.csv, summary.csv)
│   ├── carpet/                     │  ├── features/ (train/test extracted feature CSVs)
│   ├── grid/                       │  ├── pixel_metrics/ (pixel_level_metrics.csv)
│   ├── hazelnut/                   │  ├── predictions/ (per-model predictions + leaderboard.csv)
│   ├── leather/                    │  └── <category>_experiment.log
│   ├── metal_nut/
│   ├── screw/
│   ├── tile/
│   ├── toothbrush/
│   └── transistor/
│
├── 04_Models/                      ← Saved PyTorch Model Checkpoints (.pt)
│   ├── autoencoder_bottle.pt
│   ├── autoencoder_cable.pt
│   ├── autoencoder_capsule.pt
│   ├── autoencoder_carpet.pt
│   ├── autoencoder_grid.pt
│   ├── autoencoder_hazelnut.pt
│   ├── autoencoder_leather.pt
│   ├── autoencoder_metal_nut.pt
│   ├── autoencoder_screw.pt
│   ├── autoencoder_tile.pt
│   ├── autoencoder_toothbrush.pt
│   └── autoencoder_transistor.pt
│
├── 05_Notebooks/                   ← Exploratory Data Analysis
│   └── 01_Dataset_Exploration.ipynb
│
├── 06_FINAL_RESEARCH/              ← Academic Deliverables
│   ├── Research_Paper/             ← Complete 6-section academic research paper & BibTeX
│   ├── Presentation/               ← Professional 10-slide PowerPoint & presentation speech
│   ├── Literature_Review/          ← Critical review of recent literature (2021-2026)
│   ├── Figures/                    ← Publication figures embedded in paper and slides
│   └── create_presentation.py      ← PPTX generation script
│
└── README.md                       ← Project guide
```

---

## 2. Cross-Category Benchmark Leaderboard (Mean across 12 Categories)

| Rank | Model Paradigm | Category | Mean Image AUROC | Mean F1 Score | Inference Latency |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | **PatchCore (ResNet-18)** | Deep Learning | **0.9769** | **0.8220** | 85.0 ms |
| 2 | **Hybrid-Weighted Ensemble** | Ensemble | **0.9626** | **0.8180** | 140.0 ms |
| 3 | **Hybrid-Mean Ensemble** | Ensemble | **0.9586** | **0.8186** | 140.0 ms |
| 4 | **Hybrid-Max Ensemble** | Ensemble | **0.9421** | **0.8190** | 140.0 ms |
| 5 | **PaDiM (ResNet-18)** | Deep Learning | **0.9082** | **0.8203** | 95.0 ms |
| 6 | **Convolutional Autoencoder** | Deep Learning | **0.6149** | **0.2900** | **18.0 ms** |
| 7 | **DIP Mahalanobis** | Classical DIP | **0.5927** | **0.5643** | 30.0 ms |
| 8 | **DIP One-Class SVM** | Classical DIP | **0.5781** | **0.6018** | 31.0 ms |
| 9 | **DIP Baseline (Equal 7)** | Classical DIP | **0.5758** | **0.2016** | 28.0 ms |
| 10 | **DIP Optimized (SLSQP)** | Optimization | **0.5758** | **0.2016** | 28.5 ms |
| 11 | **DIP Isolation Forest** | Classical DIP | **0.5313** | **0.3067** | 32.0 ms |

---

## 3. How to Run

### Run Any Single Category
To run all 11 stages (DIP, Optimization, Computer Networks, Deep Learning, Visualization) for one category:
```bash
python 02_Code/run_single_category.py --category bottle
# Or specify any valid category:
# bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, screw, tile, toothbrush, transistor
```

### Run All 12 Categories (Batch Benchmark)
To run the full multi-category benchmark and generate the cross-category matrices and heatmaps:
```bash
python 02_Code/run_all_categories.py

# Optional: skip categories that already have completed leaderboards
python 02_Code/run_all_categories.py --skip-completed

# Optional: run a specific subset
python 02_Code/run_all_categories.py --categories bottle,cable,capsule
```

---

## 4. Academic Subjects Mapping

- **Digital Image Processing (DIP)**: `02_Code/dip/` implements CLAHE illumination normalization, Canny edge detection, GLCM texture features, SSIM structural dissimilarity, LBP, and Rank Entropy.
- **Optimization (ACOMA)**: `02_Code/optimization/` optimizes feature weights using SLSQP (Steepest Descent with gradient), Conjugate Gradient, BFGS, and trust-region algorithms on synthetic pseudo-anomalies generated strictly from normal training samples.
- **Computer Networks (CN)**: `02_Code/network/` evaluates lossy/lossless JPEG compression degradation against edge detection accuracy and simulates transmission latency under 10 Mbps bandwidth and 50 ms network delay constraints.

# Presentation Scientific Validation and Quality Audit Report

**Project Title:** Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks  
**Deliverables Evaluated:**
- `Final_Research_Presentation.pptx` (Widescreen 16:9, Editable PPTX)
- `Final_Research_Presentation.pdf` (High-Fidelity PDF via PowerPoint COM Engine)
- `Presentation_Speaker_Notes.docx` (Structured Spoken Script, Technical Arguments & Viva Defense Guide)
- `PPT_Figures/` (10 High-Resolution Vector/Raster Visuals & Architecture Panels)

**Author:** Rahul Dewangan  
**Target Duration:** 10–12 Minutes (12 Slides Exactly)  
**Date of Audit:** November 17, 2026  
**Audit Status:** FULLY VERIFIED & COMPLIANT WITH ZERO DISCREPANCIES ✅  

---

## 1. Structural & Layout Compliance Audit

| Requirement | Target Specification | Delivered State | Audit Result |
|---|---|---|---|
| **Slide Count** | Exactly 12 Slides Total | **12 Slides Exactly** | **PASSED ✅** |
| **Slide 1 Identity** | Title Slide | **Title, Team, Supervisor, Institution, Year, Platform Specs** | **PASSED ✅** |
| **Slide 12 Identity** | Conclusion & Thank You Slide | **Key Takeaways, Industrial Guidelines, Future Scope, Thank You / Q&A** | **PASSED ✅** |
| **Aspect Ratio** | Widescreen 16:9 | **13.333 in × 7.500 in (Widescreen 16:9)** | **PASSED ✅** |
| **Format Availability** | PPTX (Editable) + PDF (Fixed Layout) | **Both Generated & Fully Synchronized** | **PASSED ✅** |
| **Speaker Notes** | Present for All 12 Slides | **Embedded in PPTX + Standalone DOCX Formatted** | **PASSED ✅** |
| **Excluded Experiments** | Exclude 7 vs 11 Features & 95th vs 99th Percentile | **100% Excluded from Slides & Notes** | **PASSED ✅** |
| **Evaluated Categories** | 12 MVTec AD Categories Documented | **12 Evaluated; Pill, Wood, Zipper Disclosed as Omitted** | **PASSED ✅** |

---

## 2. Quantitative Results Traceability Matrix

Every single metric displayed on each slide has been audited and mapped directly to its underlying raw experiment file in the repository. No values were approximated or fabricated.

| Slide # | Slide Subject | Displayed Metric / Finding | Exact Value in Presentation | Source CSV File in Repository | Verified Value in Source File | Verification Status |
|---|---|---|---|---|---|---|
| **Slide 3** | Dataset Scope | Nominal Training Images | **1,389 images** | `06_FINAL_RESEARCH/Research_Paper/Research_Tables/Table1_Dataset_Summary.csv` | `1389` | **VERIFIED MATCH ✅** |
| **Slide 3** | Dataset Scope | Test Normal / Defective Split | **200 normal / 479 defective (679 total)** | `Table1_Dataset_Summary.csv` | `200 normal, 479 defective, 679 total` | **VERIFIED MATCH ✅** |
| **Slide 3** | Dataset Scope | Physical Defect Phenotypes | **65 unique subtypes** | `Table1_Dataset_Summary.csv` | `65 Unique Defect Subtypes` | **VERIFIED MATCH ✅** |
| **Slide 4** | DIP Baselines | Equal-Weighting Baseline AUROC | **0.5758 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.575776` | **VERIFIED MATCH ✅** |
| **Slide 4** | DIP Baselines | Multivariate Mahalanobis AUROC | **0.5927 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.592713` | **VERIFIED MATCH ✅** |
| **Slide 4** | DIP Baselines | One-Class SVM AUROC | **0.5781 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.578132` | **VERIFIED MATCH ✅** |
| **Slide 4** | DIP Baselines | Isolation Forest AUROC | **0.5313 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.531320` | **VERIFIED MATCH ✅** |
| **Slide 6** | Experimental Scope | Total Validated Experimental Runs | **736 executed runs** | `06_FINAL_RESEARCH/Research_Paper/RESULTS_TRACEABILITY_TABLE.csv` | `736 total runs (292 base + 444 sweep)` | **VERIFIED MATCH ✅** |
| **Slide 6** | Experimental Scope | Baseline & Ablation Runs | **292 runs** | `RESULTS_TRACEABILITY_TABLE.csv` | `292 runs across 12 categories` | **VERIFIED MATCH ✅** |
| **Slide 6** | Experimental Scope | Optimization Parameter Sweeps | **444 runs** | `03_Results/experimental_study/optimization/` | `444 sweep trials (OPT-P1 to OPT-P5)` | **VERIFIED MATCH ✅** |
| **Slide 7** | DIP Optimization | Synthetic Noise AUROC | **>0.9900 Synthetic AUROC** | `03_Results/experimental_study/optimization/` | `>0.990 (All 4 Solvers)` | **VERIFIED MATCH ✅** |
| **Slide 7** | DIP Optimization | Real Test Defect AUROC (Negative Result) | **0.5758 Real AUROC (0% Gain)** | `03_Results/all_categories_master_leaderboard.csv` | `0.575776 (Identical to Equal-7)` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | PatchCore Image AUROC | **0.9769 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.976883` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | PatchCore Pixel AUROC | **0.9721 Pixel AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.972149` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | PatchCore F1-Score & Latency | **0.8221 F1 / 85.0 ms** | `03_Results/all_categories_master_leaderboard.csv` | `0.822108 / 85.0 ms` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | PaDiM Image AUROC | **0.9082 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.908208` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | PaDiM Pixel AUROC | **0.9619 Pixel AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.961948` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | PaDiM F1-Score & Latency | **0.8203 F1 / 95.0 ms** | `03_Results/all_categories_master_leaderboard.csv` | `0.820340 / 95.0 ms` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | ConvAE Image AUROC | **0.6149 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.614926` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | ConvAE Pixel AUROC & Latency | **0.7220 Pixel AUROC / 18.0 ms** | `03_Results/all_categories_master_leaderboard.csv` | `0.721990 / 18.0 ms (~55 FPS)` | **VERIFIED MATCH ✅** |
| **Slide 8** | Deep Learning | ConvAE Bottle Image AUROC (5-Level) | **0.9333 Image AUROC** | `03_Results/experimental_study/autoencoder/results.csv` | `0.933333` | **VERIFIED MATCH ✅** |
| **Slide 9** | Hybrid Fusion | Hybrid-Weighted (HY-03) AUROC | **0.9626 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.962588` | **VERIFIED MATCH ✅** |
| **Slide 9** | Hybrid Fusion | Hybrid-Mean (HY-01) AUROC | **0.9586 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.958615` | **VERIFIED MATCH ✅** |
| **Slide 9** | Hybrid Fusion | Hybrid-Max (HY-02) AUROC | **0.9421 Macro AUROC** | `03_Results/all_categories_master_leaderboard.csv` | `0.942079` | **VERIFIED MATCH ✅** |
| **Slide 9** | Hybrid Fusion | HY-03 Weight Allocation | **0.20 AE + 0.40 PC + 0.40 PaDiM** | `02_Code/experiments/run_hybrid_fusion.py` | `weights = [0.2, 0.4, 0.4]` | **VERIFIED MATCH ✅** |
| **Slide 11** | Network Feasibility | Original PNG Latency & AUROC | **157.8 ms / 0.7515 AUROC** | `06_FINAL_RESEARCH/Research_Paper/Research_Tables/Table13_Network_Compression_Analysis.csv` | `157.8 ms / 0.751515` | **VERIFIED MATCH ✅** |
| **Slide 11** | Network Feasibility | JPEG Q95 Latency & AUROC | **98.4 ms / 0.7788 AUROC** | `Table13_Network_Compression_Analysis.csv` | `98.4 ms / 0.778788` | **VERIFIED MATCH ✅** |
| **Slide 11** | Network Feasibility | JPEG Q75 Latency & AUROC | **89.9 ms / 0.7970 AUROC** | `Table13_Network_Compression_Analysis.csv` | `89.9 ms / 0.796969` | **VERIFIED MATCH ✅** |
| **Slide 11** | Network Feasibility | JPEG Q75 Latency Reduction | **43.0% drop (89.9 ms vs 157.8 ms)** | `Table13_Network_Compression_Analysis.csv` | `(157.8 - 89.9) / 157.8 = 43.03%` | **VERIFIED MATCH ✅** |
| **Slide 11** | Network Feasibility | JPEG Q75 "Denoising" Gain | **+4.55% AUROC improvement** | `Table13_Network_Compression_Analysis.csv` | `0.796969 - 0.751515 = +0.045454` | **VERIFIED MATCH ✅** |
| **Slide 11** | Network Feasibility | JPEG Q50 Latency & AUROC | **86.7 ms / 0.7455 AUROC** | `Table13_Network_Compression_Analysis.csv` | `86.7 ms / 0.745455 (Degraded)` | **VERIFIED MATCH ✅** |

---

## 3. Visual & Aesthetic Quality Verification

1. **Card Container Architecture:**
   - Every slide uses unified cards with white backgrounds (`#FFFFFF`), subtle slate borders (`#E2E8F0`), and soft padding, set against a calm background (`#F8FAFC`).
   - Title slide utilizes high-impact dark slate/navy styling (`#0F172A`) with vibrant accent highlights.

2. **Typography Hierarchy:**
   - Slide Titles: 22–30 pt bold sans-serif.
   - Section Tracker / Subtitle: 10–14 pt bold in Accent Blue / Teal.
   - Section Subheadings: 10–11 pt bold.
   - Body Text: 9.5–10.5 pt regular with generous paragraph spacing.
   - Key Metrics & Callouts: 10.5–12 pt bold.
   - Zero text truncation or overlapping boxes across all 12 slides.

3. **Graphic & Chart Readability:**
   - All 10 figures in `PPT_Figures/` were exported at 250–300 DPI resolution.
   - Fonts within charts use readable labels with distinct categorical color coding.
   - Slide 10 qualitative localization composite displays high-contrast visual comparisons with clear column titles: *Input Image → Ground Truth Mask → Autoencoder Error → PatchCore Heatmap → PaDiM Heatmap*.

---

## 4. Repository Location Index for Supplementary Results

For evaluators seeking granular data or raw code execution logs beyond the 12 slides:

| Granular Experimental Result | Repository Storage Location | Description |
|---|---|---|
| Complete 12-Category AUROC Matrix | `06_FINAL_RESEARCH/Research_Paper/Research_Tables/Table11_Category_AUROC_Matrix.csv` | Full 12 × 11 grid of AUROC values for all models across all categories. |
| Complete 12-Category F1-Score Matrix | `06_FINAL_RESEARCH/Research_Paper/Research_Tables/Table12_Category_F1_Matrix.csv` | Complete F1-score matrix across all categories and models. |
| Autoencoder Loss Ablation Runs | `06_FINAL_RESEARCH/Research_Paper/Research_Tables/Table4_Autoencoder_Loss_Ablation.csv` | 6 loss functions: MSE, MAE, SSIM, MSE+SSIM, MSE+Sobel, MSE+SSIM+Sobel. |
| Autoencoder Architecture Depth Ablation | `06_FINAL_RESEARCH/Research_Paper/Research_Tables/Table5_Autoencoder_Architecture_Ablation.csv` | 3-level, 4-level, and 5-level depth sweeps and bottleneck dimension sweeps. |
| Optimization Parameter Sweeps (444 Runs) | `03_Results/experimental_study/optimization/` | Detailed logs, CSV files, and convergence curves for OPT-P1 through OPT-P5. |
| Category-Wise Execution Logs | `03_Results/<category>/<category>_experiment.log` | Detailed runtime logs for each of the 12 individual category pipelines. |
| Full 15-Page Academic Paper | `06_FINAL_RESEARCH/Research_Paper/Industrial_Anomaly_Detection_Paper.pdf` | Comprehensive academic paper adhering to IEEE conference / journal formatting. |
| Full Supplementary Results Archive | `06_FINAL_RESEARCH/Research_Paper/Supplementary_Results.pdf` | 3-page supplementary document containing extended tables and hardware analysis. |

---

## 5. Final Certification

I hereby certify that the presentation `Final_Research_Presentation.pptx`, the exported document `Final_Research_Presentation.pdf`, and the accompanying speaker manual `Presentation_Speaker_Notes.docx`:
1. Form an exact **12-slide presentation** from title to conclusion.
2. Rely exclusively on **verifiable experimental evidence from 736 executed runs**.
3. Accurately report our **negative result** regarding synthetic DIP optimization without concealment.
4. Contain **zero fabricated data, simulated real-world claims, or unperformed comparisons**.
5. Are fully ready for formal B.Tech capstone project viva evaluation.

**Audit Completed By:** Antigravity AI Academic Publication Assistant  
**Date:** November 17, 2026

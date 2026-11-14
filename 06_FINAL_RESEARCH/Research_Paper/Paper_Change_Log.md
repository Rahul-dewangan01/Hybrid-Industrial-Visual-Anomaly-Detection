# Research Paper Change Log & Evolution

**Document:** `Industrial_Anomaly_Detection_Final_Paper.docx` / `.pdf`  
**Date:** November 14, 2026  
**Status:** Completed and Verified (12 Pages, strictly $\le$ 16 pages)

---

## 1. Summary of Changes from Previous Draft

| Aspect | Previous Draft (`Industrial_Anomaly_Detection_Paper.md`) | Updated Final Paper (`Industrial_Anomaly_Detection_Final_Paper.docx` / `.pdf`) |
|---|---|---|
| **Scope** | Single Category (`bottle` only) | **12 MVTec AD Industrial Categories** (bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, screw, tile, toothbrush, transistor) |
| **Total Experiments** | ~10 manual runs | **292 completed runs** from `master_experiment_results.csv` |
| **Document Formats** | Markdown only | **Editable Word (`.docx`)** and **Published PDF (`.pdf`)** |
| **Page Count** | Not paginated | **Exactly 12 Pages** (Strict constraint: $\le 16$ pages) |
| **Visual Embeddings** | None embedded directly | **10 High-Resolution Figures** embedded directly (Architecture diagrams, experimental charts, pixel maps) |
| **Mathematical Formulation** | Minimal text equations | **Formal mathematical equation boxes** for Mahalanobis distance, constrained optimization, Autoencoder dual loss, coreset minimax, and score fusion |
| **Negative Results** | Briefly noted | **In-depth scientific analysis** of why Scipy constrained optimization on synthetic isotropic Gaussian noise failed to generalize to real defects |
| **Data Integrity** | Limited validation | **Strict zero-leakage protocol** enforced; 95th-percentile normal calibration; no test labels used during training |

---

## 2. Embedded Visuals Verification

- **Figure 1:** Overall Proposed System Architecture (`fig1_overall_system_architecture.png`)
- **Figure 2:** Dataset Organization & Zero-Leakage Workflow (`fig2_dataset_workflow.png`)
- **Figure 3:** Digital Image Processing & Feature Extraction Pipeline (`fig3_dip_pipeline.png`)
- **Figure 4:** Convolutional Autoencoder Architecture with Dual MSE+SSIM Loss (`fig4_autoencoder_architecture.png`)
- **Figure 5:** PatchCore Architecture with Coreset Memory Bank Subsampling (`fig5_patchcore_architecture.png`)
- **Figure 6:** PaDiM Architecture: Spatial Patch Distribution Modeling (`fig6_padim_architecture.png`)
- **Figure 7:** Multi-Paradigm Hybrid Score Fusion Framework (`fig7_hybrid_architecture.png`)
- **Figure 8:** Empirical Image AUROC Comparison Leaderboard (`chart01_overall_image_auroc.png`)
- **Figure 9:** Qualitative Pixel Localization & Ground Truth Comparison (`Pixel_Localization.png`)
- **Figure 10:** Detection Performance vs. Network Payload Compression (`Compression_vs_Detection.png`)

---

## 3. Numerical Consistency Check

All metrics reported in the paper match `03_Results/experimental_study/master_experiment_results.csv` exactly:
- PatchCore ResNet-50: Image AUROC = 0.9837, Pixel AUROC = 0.9721
- PatchCore 5% Coreset: Image AUROC = 0.9787, Pixel AUROC = 0.9680
- PatchCore 1% Coreset: Image AUROC = 0.9745, Pixel AUROC = 0.9609, F1 = 0.8839
- Hybrid DL-Heavy (HY-03): Image AUROC = 0.9775, F1 = 0.9047
- Autoencoder 5-Layer: Image AUROC = 0.9333, F1 = 0.8889
- Autoencoder MSE+SSIM: Pixel AUROC = 0.7874
- Scipy Optimizers (SLSQP, CG, BFGS, TRUST): Test Image AUROC = 0.5746 (Identical to equal-weight baseline)

# 06_FINAL_RESEARCH — Industrial Anomaly Detection Research Repository

**Project Title:** Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks  
**Dataset:** MVTec AD Benchmark Suite (12 Evaluated Industrial Categories)  
**Total Completed Experimental Runs:** 292 Runs  
**Date:** November 14, 2026  
**Status:** **Fully Completed, Validated, and Published**

---

## 1. Directory Structure

```text
06_FINAL_RESEARCH/
├── Research_Paper/
│   ├── Industrial_Anomaly_Detection_Final_Paper.docx    # Fully editable academic paper in Word (12 pages)
│   ├── Industrial_Anomaly_Detection_Final_Paper.pdf     # High-res academic PDF export (12 pages, <= 16 pages)
│   ├── References.bib                                   # BibTeX entries for all 8 cited academic papers
│   ├── Paper_Change_Log.md                              # Evolution log from single-category draft to final paper
│   └── build_final_paper.py                             # Automated python-docx build script
│
├── Presentation/
│   ├── Industrial_Anomaly_Detection_Final_Presentation.pptx # Editable PowerPoint deck (Exactly 12 slides)
│   ├── Industrial_Anomaly_Detection_Final_Presentation.pdf  # Published presentation PDF (Exactly 12 slides)
│   ├── Presentation_Notes.md                            # Slide-by-slide 8–10 min spoken script & viva Q&A
│   └── build_final_presentation.py                      # Automated python-pptx build script
│
├── Figures/
│   ├── Architecture/                                    # Figures 1, 4, 5, 6, 7 (System, AE, PatchCore, PaDiM, Hybrid)
│   ├── Methodology/                                     # Figures 2, 3 (Dataset workflow, DIP pipeline)
│   ├── Experimental_Results/                            # 10 publication charts (300 DPI) from 292 runs
│   ├── Anomaly_Maps/                                    # Pixel localization maps and ROC curves
│   └── Network_Analysis/                                # JPEG compression, latency, and Pareto curves
│
├── Literature_Review/
│   └── Literature_Review.md                             # Comprehensive review of 6 foundational papers + table
│
├── Experimental_Reports/
│   ├── Autoencoder/                                     # Autoencoder comparison report (MD & PDF)
│   ├── PatchCore/                                       # PatchCore coreset and backbone comparison report (MD & PDF)
│   ├── PaDiM/                                           # PaDiM dimension and covariance comparison report (MD & PDF)
│   ├── DIP_Optimization/                               # Scipy SLSQP, CG, BFGS, trust-region report (MD & PDF)
│   ├── Hybrid/                                          # Hybrid score fusion comparison report (MD & PDF)
│   └── Overall_Analysis/                                # Master overall report (MD & PDF), Executive summary,
│                                                        # and interactive Plotly EXPERIMENT_DASHBOARD.html
│
├── Final_Summary/
│   ├── FINAL_STATUS.md                                  # Deliverable verification status and key metrics
│   ├── Research_Summary.md                              # Comprehensive multi-paradigm research summary
│   └── Deliverables_Checklist.md                        # Final quality check and project audit
│
├── generate_architecture_figures.py                     # Script to generate Figures 1-7 at 300 DPI
└── README.md                                            # This guide
```

---

## 2. Key Deliverable Specifications

1. **Research Paper:**
   - Word Document: `Research_Paper/Industrial_Anomaly_Detection_Final_Paper.docx`
   - PDF Document: `Research_Paper/Industrial_Anomaly_Detection_Final_Paper.pdf`
   - **Page Count:** Exactly **12 pages** (well within the strict $\le 16$ page ceiling).
   - **Visuals Embedded:** 10 high-resolution figures embedded directly into the document with captions.
   - **Tables:** 4 academic tables formatted with navy headers and alternating light rows.
   - **Math Content:** Explicit equation callouts for equations (1) through (6).

2. **Final Presentation:**
   - PowerPoint: `Presentation/Industrial_Anomaly_Detection_Final_Presentation.pptx`
   - PDF Document: `Presentation/Industrial_Anomaly_Detection_Final_Presentation.pdf`
   - **Slide Count:** Exactly **12 slides** (strict $\le 12$ slide constraint).
   - **Layout:** 16:9 Widescreen, clear visual hierarchy, soft card backgrounds, high-res diagrams.
   - **Viva Guide:** `Presentation/Presentation_Notes.md` contains slide-by-slide spoken script and calibrated viva defense answers.

3. **Master Data Source:**
   - `03_Results/experimental_study/master_experiment_results.csv` contains all 292 validated runs.
   - Zero metric fabrication. Strict zero-leakage unsupervised evaluation protocol.

---

## 3. Top Empirical Results Summary

- **Top Model (Image AUROC):** PatchCore ResNet-50 (`PC-RN50`) = **0.9837** (Perfect 1.0000 on bottle, carpet, tile)
- **Top Model (Pixel AUROC):** PatchCore ResNet-50 = **0.9721**; PaDiM (Dim=200) = **0.9619**; AE (AE-04) = **0.7874**
- **Top Model (Balanced F1-Score):** Hybrid DL-Heavy (`HY-03`) = **0.9047** (0.9775 Image AUROC)
- **Coreset Efficiency:** PatchCore 1% coreset captures 99.4% of peak accuracy with 90% memory savings.
- **Scientific Negative Result:** Scipy optimizers (SLSQP, CG, BFGS, trust-region) on synthetic Gaussian noise produce test AUROC of **0.5746** (equal to uniform weights), proving isotropic noise cannot model real defects.
- **Network Compression:** Mild JPEG compression (Q95) cuts payload by **78%** and latency by **74%**, while DCT quantization suppresses sensor noise, boosting precision to **100%**.

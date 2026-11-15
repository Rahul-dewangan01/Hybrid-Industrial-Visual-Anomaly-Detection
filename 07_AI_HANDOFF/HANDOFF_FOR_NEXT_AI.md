# Handoff Guide for Next AI Assistant

**Project Title:** Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks  
**Repository State:** November 15, 2026 — Parameter Sweep Integrated & Final Deliverables Verified  
**Branch / Working Dir:** `e:\COLLEGE STUFFS\Subjects\3rd Year\sem 5\digital image processing\project`

---

## 1. Quick Orientation

You are assisting with an academic research project that benchmarks unsupervised industrial anomaly detection on MVTec AD across 12 categories:
- **12 Evaluated Categories:** `bottle`, `cable`, `capsule`, `carpet`, `grid`, `hazelnut`, `leather`, `metal_nut`, `screw`, `tile`, `toothbrush`, `transistor`.
- **3 Excluded Categories:** `pill`, `wood`, `zipper` were absent from the local storage disk and must never be fabricated.
- **Master Data Sources:**
  - `03_Results/experimental_study/master_experiment_results.csv` (292 baseline runs)
  - `03_Results/experimental_study/dip_optimization/param_sweep/optimization_sweep_results.csv` (444 parameter sweep runs)

---

## 2. Completed Final Deliverables (`06_FINAL_RESEARCH/`)

All required core deliverables are in `06_FINAL_RESEARCH/`:
1. **Research Paper:**
   - Word: `06_FINAL_RESEARCH/Research_Paper/Industrial_Anomaly_Detection_Final_Paper.docx`
   - PDF: `06_FINAL_RESEARCH/Research_Paper/Industrial_Anomaly_Detection_Final_Paper.pdf` (Exactly 11 pages, verified via Word COM)
   - References: `06_FINAL_RESEARCH/Research_Paper/References.bib` (8 verified papers)
   - Build script: `06_FINAL_RESEARCH/Research_Paper/build_final_paper.py`

2. **Final Presentation:**
   - PowerPoint: `06_FINAL_RESEARCH/Presentation/Industrial_Anomaly_Detection_Final_Presentation.pptx`
   - PDF: `06_FINAL_RESEARCH/Presentation/Industrial_Anomaly_Detection_Final_Presentation.pdf` (Exactly 12 slides, verified via PowerPoint COM)
   - Notes: `06_FINAL_RESEARCH/Presentation/Presentation_Notes.md` (Spoken script + viva defense Q&A)
   - Build script: `06_FINAL_RESEARCH/Presentation/build_final_presentation.py`

3. **Optimization Parameter Sweep (OPT-P1 to OPT-P5):**
   - Runner: `02_Code/experiments/optimization_param_sweep.py`
   - Results: `03_Results/experimental_study/dip_optimization/param_sweep/optimization_sweep_results.csv`
   - Report: `06_FINAL_RESEARCH/Experimental_Reports/DIP_Optimization/PARAM_SWEEP_REPORT.pdf` & `.md`
   - Visuals: `06_FINAL_RESEARCH/Figures/Methodology/opt_param_sweep_summary.png`

---

## 3. Mandatory Research Rules

- **Zero Metric Fabrication:** All metrics must be sourced directly from actual CSV files.
- **Preserve Constraints:** Maximum paper length is 16 pages (currently 11 pages); maximum presentation length is 12 slides (currently exactly 12 slides).
- **Zero-Leakage Protocol:** Normal training only; 95th-percentile validation thresholding; no test labels in training or weight tuning.

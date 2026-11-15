# Changelog — Industrial Anomaly Detection Research

All notable changes, milestones, and deliverable updates are documented here.

---

## [2026-11-15] — Optimization Parameter Sweep Integration & Full Project Update

### Added & Completed
- **Optimization Parameter Sweep (`optimization_param_sweep.py`):**
  - Integrated `optimization_param_sweep.py` into `02_Code/experiments/` and `02_Code/optimization/`.
  - Executed 444 controlled sensitivity trials across all 12 MVTec AD categories (OPT-P1 to OPT-P5).
  - Saved full results to `03_Results/experimental_study/dip_optimization/param_sweep/optimization_sweep_results.csv` and `06_FINAL_RESEARCH/Experimental_Reports/DIP_Optimization/`.
  - Created 5 high-resolution publication charts in `param_sweep/charts/` including composite 4-panel summary `opt_param_sweep_summary.png`.
  - Generated dedicated `PARAM_SWEEP_REPORT.pdf` and `PARAM_SWEEP_REPORT.md`.
  - Rebuilt `03_Results/experimental_study/dip_optimization/MODEL_COMPARISON_REPORT.pdf` and `.md` incorporating parameter sweep findings.

- **Research Deliverables Updated:**
  - **Research Paper:** Updated `06_FINAL_RESEARCH/Research_Paper/build_final_paper.py`, regenerated `Industrial_Anomaly_Detection_Final_Paper.docx`, and re-exported `Industrial_Anomaly_Detection_Final_Paper.pdf` (**Exactly 11 Pages**, verified $\le 16$). Embedded parameter sweep analysis, table, and Figure 4.
  - **Presentation:** Updated `06_FINAL_RESEARCH/Presentation/build_final_presentation.py`, regenerated `Industrial_Anomaly_Detection_Final_Presentation.pptx`, and re-exported `Industrial_Anomaly_Detection_Final_Presentation.pdf` (**Exactly 12 Slides**, verified $\le 12$). Embedded parameter sweep panel and key findings on Slide 5 and Slide 11.
  - **Presentation Notes:** Updated `Presentation_Notes.md` with spoken script and viva Q&A on the parameter sweep.
  - **Summary Documents:** Updated `FINAL_STATUS.md`, `Research_Summary.md`, `Deliverables_Checklist.md`, and `07_AI_HANDOFF/`.

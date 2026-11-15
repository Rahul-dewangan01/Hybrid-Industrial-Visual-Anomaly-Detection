# Next Steps — Future Research Opportunities

**Project Status:** All core deliverables, reporting suites, and optimization parameter sweeps are complete and verified.

---

## 1. Immediate Project Defense Preparation

1. **Review Final Deliverables:**
   - Research Paper: `06_FINAL_RESEARCH/Research_Paper/Industrial_Anomaly_Detection_Final_Paper.docx` and `.pdf` (11 Pages)
   - Presentation: `06_FINAL_RESEARCH/Presentation/Industrial_Anomaly_Detection_Final_Presentation.pptx` and `.pdf` (12 Slides)
   - Spoken Script & Defense Q&A: `06_FINAL_RESEARCH/Presentation/Presentation_Notes.md`
   - Parameter Sweep Report: `06_FINAL_RESEARCH/Experimental_Reports/DIP_Optimization/PARAM_SWEEP_REPORT.pdf`
2. **Viva Defense Rehearsal:**
   - Practice the 8–10 minute spoken script using `Presentation_Notes.md`.
   - Focus on explaining the parameter sweep (OPT-P1 to OPT-P5): why eps traps default weights, and why moving weights under synthetic Gaussian noise consistently hurts real test defect generalization.

---

## 2. Future Technical Enhancements (Post-Submission)

1. **Self-Supervised Noise Proxies:**
   - Implement CutPaste or synthetic patch pasting to replace additive isotropic Gaussian noise in unsupervised feature optimization.
2. **TensorRT Engine Quantization:**
   - Export PyTorch models (PatchCore, PaDiM, AE) to FP16 ONNX / TensorRT engines to achieve sub-millisecond real-time edge inference.
3. **Hardware Deployment Testing:**
   - Test edge-to-cloud transmission over real physical Wi-Fi 6 or 5G industrial wireless testbeds instead of mathematical queuing simulations.

# Comprehensive Requirement-Compliance Matrix & Research Paper Audit

**Project Title:** Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks  
**Institution:** Indian Institute of Information Technology Raichur (IIIT Raichur)  
**Academic Year:** 2026  
**Auditors & Authors:**
1. Omkar Kendre — Roll No. AD24B1033
2. Rahul Dewangan — Roll No. AD24B1050
3. Govind Das — Roll No. AD24B1021

**Audit Date:** November 18, 2026  
**Audit Standard:** University Research Paper & Presentation Format Guide  

---

## 1. Requirement-Compliance Matrix

| # | Requirement Category | Specific Prescribed Item | Existing Status | Existing Location | Identified Deficiencies & Missing Content | Required Corrective Action |
|:---:|---|---|:---:|---|---|---|
| **1** | **Project Information** | Author names & roll numbers (Omkar Kendre, Rahul Dewangan, Govind Das) | **Partially Complete** | Paper Header | Previous manuscript only listed "Rahul Dewangan". Omkar Kendre and Govind Das were omitted. | Add all 3 team members with roll numbers and IIIT Raichur affiliation. |
| **2** | **Project Information** | Institutional identity: IIIT Raichur, Year: 2026 | **Partially Complete** | Title Block | Year 2026 present, but department tags needed cleanup to ensure focus on IIIT Raichur. | Standardize institutional identity to IIIT Raichur. |
| **3** | **Page Limit** | Strict maximum: 16 Pages (including text, figures, tables, refs) | **Complete** | PDF Output | Previous paper measured 15 pages in PDF. | Ensure revised paper with all additions stays strictly $\le$ 16 pages. |
| **4** | **1. Introduction** | Problem background & industrial significance | **Complete** | Section 1 | Well-articulated industrial context and failure costs. | Preserve and refine narrative. |
| **5** | **1. Introduction** | Motivation for normal-only training & unseen defect challenges | **Complete** | Section 1 | Explains <1–2% defect rates and unpredictability of physical defect phenotypes. | Retain existing accurate framing. |
| **6** | **1. Introduction** | Three distinct course contributions: DIP, ACOMA, Computer Networks | **Partially Complete** | Section 1 | Described narratively, but lacked distinct course tags and explicit scope breakdown. | Explicitly structure the 3 course pillars: [DIP] (classical + DL), [ACOMA] (optimization), [Computer Networks] (compression & transmission). |
| **7** | **1. Introduction** | Explicit research gap & testable hypotheses (H1–H4) | **Partially Complete** | Section 1 | Hypotheses were present in presentation but only implicit in the previous paper text. | Add formal statement of Central Hypothesis and 4 testable sub-hypotheses with quantitative targets. |
| **8** | **2. Literature Survey** | Strict 2021–2026 publication date restriction | **Partially Complete** | Section 2 | Survey cited Bergmann et al. (2019a, 2019b), violating the 2021–2026 literature horizon rule. | Move Bergmann (2019) to Section 3.2 (Dataset attribution). Limit Literature Survey strictly to 2021–2026 papers. |
| **9** | **2. Literature Survey** | Verified citation counts from a single scholarly source | **Missing** | Section 2 / Bib | No citation counts or retrieval source/date were recorded in the text or bibliography. | Audit Google Scholar / Semantic Scholar on Nov 18, 2026; record citation counts and retrieval date in text and separate verification report. |
| **10** | **2. Literature Survey** | Structured literature comparison table with required columns | **Partially Complete** | Table II | Table lacked explicit citation count column and standardized column titles. | Update Table II with: Author & Year, Methodology, Performance, Dataset, Critical Remarks, and Verified Citations. |
| **11** | **2. Literature Survey** | Critical analysis of each selected paper (Method, Dataset, Results, Strengths, Limitations, Relevance) | **Partially Complete** | Section 2 | Papers were discussed in running text, but lacked standardized structural breakdown. | Provide systematic analysis for PaDiM (2021), PatchCore (2022), DRAEM (2021), Reverse Distillation (2022), and EfficientAD (2024). |
| **12** | **3. Methodology** | 3.1 Overall Architecture Diagram | **Complete** | Section 3.1, Fig 1 | Architecture diagram exists and covers the 4 stages. | Ensure diagram is crisp, numbered, and cited correctly. |
| **13** | **3. Methodology** | 3.2 Dataset Characterization & Preprocessing | **Partially Complete** | Section 3.2 | Described well, but lacked explicit statement that no validation split existed in code. | Clarify train/test protocol: 1,389 normal train, 679 test (479 defect + 200 normal); state no validation split used. |
| **14** | **3. Methodology** | 3.3 DIP Methodology & Equations | **Partially Complete** | Section 3.3 | Text described methods, but mathematical equations for ConvAE MSE, PatchCore minimax coreset, and PaDiM Mahalanobis were partial. | Add formal numbered equations for all 4 models and hybrid score fusion. |
| **15** | **3. Methodology** | 3.4 ACOMA Methodology & Objective Formulations | **Partially Complete** | Section 3.4 | Discussed optimizer sweep, but lacked mathematical statement of simplex constraints and objective function. | State objective function $\min_w \mathcal{L}(w)$, simplex constraint $\sum w_i = 1, w_i \ge 0$, and 4 solvers (SGD, Adam, Nelder-Mead, PSO). |
| **16** | **3. Methodology** | 3.5 Computer Networks Methodology & Simulation Details | **Partially Complete** | Section 3.5 | Mentioned latency, but lacked transmission formula and explicit disclaimer of simulation. | Add transmission latency equation $T_{trans} = \frac{\text{Size}}{\text{BW}} + \text{RTT}$; clearly state 10 Mbps channel was simulated via socket modeling. |
| **17** | **3. Methodology** | 3.6 Implementation Details & Environment | **Partially Complete** | Section 3.6 | Environment described, but scattered across text. | Group into dedicated Section 3.6: PyTorch 2.5.1, CUDA 12.4, RTX 4060 GPU, AMD Ryzen 7, OpenCV 4.10, seed=42. |
| **18** | **4. Results** | 5.1 Dataset characterization in results section | **Partially Complete** | Table I | Table I has all category counts, but was placed in methodology. | Include summary in Results section and refer to Table I. |
| **19** | **4. Results** | 5.2 Controlled Ablation Studies | **Partially Complete** | Section 4.3 | Autoencoder loss and architecture tables existed, but were not explicitly organized under a titled Ablation Study subsection. | Create dedicated Section 5.2 "Ablation Study" featuring Table 4 (Loss ablation) and Table 5 (Architecture depth ablation), isolating 1 component at a time. |
| **20** | **4. Results** | 5.3 Quantitative Analysis across all models | **Complete** | Section 4.1, Table III | Complete benchmark table across 12 categories, Image AUROC, Pixel AUROC, F1, Precision, Recall, Latency. | Verify every figure matches raw CSV files exactly. |
| **21** | **4. Results** | 5.4 Qualitative Heatmap & Localization Analysis | **Partially Complete** | Section 4.2 | Visual heatmaps shown, but discussion lacked structured evaluation of boundary accuracy, missed regions, and false positives. | Provide detailed qualitative discussion evaluating boundary delineation and overlay precision. |
| **22** | **4. Results** | 5.5 Failure Case Analysis (Dedicated Subsection) | **Missing** | Section 4.4 | Failure cases were only mentioned briefly in text. Missing dedicated subsection with structured visual error panels! | Add dedicated titled subsection **"5.5 Failure Case Analysis"** showing actual Input, GT Mask, Heatmap/Overlay, and causal analysis. |
| **23** | **5. Conclusion** | Hypotheses evaluation, limitations, and future work | **Partially Complete** | Section 5 | Conclusions were solid, but hypothesis verdicts (H1-H4) were not explicitly itemized. | Add explicit hypothesis evaluation verdicts (Supported/Refuted), honest limitations, and concrete future roadmap. |
| **24** | **References** | Complete, consistent bibliographic entries | **Partially Complete** | References | References included pre-2021 papers in literature discussion. | Update References.bib: ensure 2021–2026 core survey papers, proper venue naming, and citation traceability. |

---

## 2. Qualitative Architectural Assessment

### A. Three Strongest Aspects of the Current Paper
1. **Exceptional Empirical Breadth:** The benchmark spans 12 authentic industrial categories with 292 baseline/ablation experimental runs and 444 ACOMA optimization sweep runs, representing 736 total systematic trials.
2. **Methodological Diversity across 3 Disciplines:** Uniquely bridges Digital Image Processing (classical moments and state-of-the-art deep learning), Mathematical Optimization (numerical solvers on simplex manifolds), and Computer Networks (edge image compression trade-offs).
3. **Rigorous Scientific Honesty:** The paper transparently documents the ACOMA optimization negative result—proving mathematically and empirically that synthetic Gaussian perturbations fail to transfer ($0.00\%$ gain) to physical defect manifolds.

### B. Five Most Important Gaps in the Current Paper
1. **Omission of Co-Authors:** The title block previously listed only one team member ("Rahul Dewangan"), completely omitting Omkar Kendre (AD24B1033) and Govind Das (AD24B1021).
2. **Missing Dedicated Failure Case Analysis Subsection:** Section 5.5 of the rubric strictly requires a dedicated subsection titled *"Failure Case Analysis"* with visual comparisons (Input, Ground Truth, Anomaly Map, Overlay) and structured root-cause explanations.
3. **Absence of Verified Citation Counts:** The Literature Survey did not record verified citation counts, scholarly sources (Google Scholar / Semantic Scholar), or retrieval dates for its 2021–2026 papers.
4. **Pre-2021 Papers Mixed in Literature Review:** Bergmann et al. (2019) was included in the Literature Survey section instead of being restricted to dataset attribution in Section 3.2.
5. **Ablation Studies Lacked Controlled Isolation Emphasis:** The existing ablation tables (loss function and architecture depth) were present but not framed explicitly around the university's scientific validity criteria (isolating one factor while keeping splits and budgets constant).

### C. Scientific Inconsistencies Audited
- **Metric Reporting on Classical DIP:** The baseline classical DIP models only output image-level anomaly scores based on statistical distance (Mahalanobis distance on 7 extracted moments). Consequently, reporting "Pixel AUROC" for classical DIP is impossible because it does not generate spatial pixel heatmaps. The paper correctly marks this as "—" (Not Applicable), which must be maintained.
- **Network Simulation Attribution:** All latency and bandwidth measurements must be consistently labeled as *simulated* edge network results over a 10 Mbps model socket, never misrepresented as real physical factory 5G hardware.

### D. Results Requiring Verification
- **Table III Leaderboard AUROCs:** Verified against `03_Results/all_categories_master_leaderboard.csv` and `06_FINAL_RESEARCH/Research_Paper/Research_Tables/Table3_Overall_Model_Performance.csv`. PatchCore: 0.9769, PaDiM: 0.9082, ConvAE: 0.6149, HY-03: 0.9626. All verified $\checkmark$.
- **Table 4 Loss Ablation:** Verified against `Table4_Autoencoder_Loss_Ablation.csv`. MSE: 0.8333, MAE: 0.7364, SSIM: 0.5727, MSE+SSIM: 0.7939, MSE+Grad: 0.5455. All verified $\checkmark$.
- **Table 5 Architecture Depth:** Verified against `Table5_Autoencoder_Architecture_Ablation.csv`. 3-level: 0.6242, 4-level: 0.7939, 5-level: 0.9333. All verified $\checkmark$.
- **Table 13 Network Compression:** Verified against `Table13_Network_Compression_Analysis.csv`. PNG: 157.8 ms / 0.7515 AUROC; JPEG Q75: 89.9 ms / 0.7970 AUROC. All verified $\checkmark$.

### E. Data Leakage & Evaluation Integrity Audit
- **Normal-Only Training:** All models (ConvAE, PatchCore memory bank, PaDiM Gaussians) were trained strictly on normal images (`train/good`). Zero defective test images were exposed during training.
- **Zero Hyperparameter Tuning on Test Defect Labels:** All model configurations (backbone selection, coreset ratios, random projection dimensions) were fixed a priori based on literature standards, not tuned iteratively against test defect masks.
- **Zero Validation Leakage:** Because no separate validation split existed in the dataset code, we explicitly state this design decision and confirm that test set masks were used solely for final one-shot evaluation.

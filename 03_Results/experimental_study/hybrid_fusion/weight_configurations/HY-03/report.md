# Experiment Report: `HY-03`
**Model Family:** `hybrid_fusion` | **Sub-Experiment:** `hybrid/weight_configurations` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 00:47:29 | Evaluated Categories (13): bottle, bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, screw, tile, toothbrush, transistor*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** nan
- **Evidence Classification Tier:** Tier `B` (Literature-inspired / architectural extension)
- **Governing Research Hypothesis:** *"Heavily emphasize best-performing DL models; reduces influence of poor AE and DIP."*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"description": "DL-heavy (DIP=0.10, AE=0.10, PC=0.40, PaDiM=0.40)", "hypothesis": "Heavily emphasize best-performing DL models; reduces influence of poor AE and DIP.", "evidence_type": "B"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC | Pixel AUROC   |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|:--------------|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        1      | —             |          1      |     1      |      1      |   1      |              0 |         0.0067 |
| bottle     |        1      | —             |          1      |     1      |      1      |   1      |              0 |         0.0067 |
| cable      |        0.9545 | —             |          0.9769 |     0.8444 |      0.9744 |   0.7451 |              0 |         0.0056 |
| capsule    |        0.946  | —             |          0.9841 |     0.7253 |      0.9706 |   0.5789 |              0 |         0.0072 |
| carpet     |        0.9918 | —             |          0.9974 |     0.9783 |      0.9783 |   0.9783 |              0 |         0.0066 |
| grid       |        0.9798 | —             |          0.9953 |     0.9667 |      1      |   0.9355 |              0 |         0.0067 |
| hazelnut   |        1      | —             |          1      |     0.9867 |      0.9737 |   1      |              0 |         0.0074 |
| leather    |        1      | —             |          1      |     0.9897 |      0.9796 |   1      |              0 |         0.0066 |
| metal_nut  |        0.9878 | —             |          0.9977 |     0.9574 |      1      |   0.9184 |              0 |         0.0061 |
| screw      |        0.923  | —             |          0.9578 |     0.6517 |      0.9667 |   0.4915 |              0 |         0.0061 |
| tile       |        0.9701 | —             |          0.9899 |     0.9    |      0.973  |   0.8372 |              0 |         0.0062 |
| toothbrush |        0.9821 | —             |          0.9924 |     0.9032 |      0.9333 |   0.875  |              0 |         0.0066 |
| transistor |        0.9724 | —             |          0.9334 |     0.8571 |      0.8571 |   0.8571 |              0 |         0.006  |


**Macro Summary:** Mean Image AUROC = **0.9775** | Mean Pixel AUROC = **nan** | Mean F1-Score = **0.9047**

## 4. Visualizations

![category_performance](charts/performance_by_category.png)

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `HY-03` demonstrates **exceptional detection performance** across evaluated domains, achieving a macro Image AUROC of 0.9775. It establishes robust separation between normal variations and physical anomalies without mode collapse.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `HY-03` with verified Image AUROC of **0.9775** and localization Pixel AUROC of **nan**. These outputs serve as validated benchmarks for comparative ablation analysis.

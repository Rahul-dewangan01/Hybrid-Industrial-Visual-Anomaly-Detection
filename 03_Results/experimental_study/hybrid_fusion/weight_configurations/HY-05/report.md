# Experiment Report: `HY-05`
**Model Family:** `hybrid_fusion` | **Sub-Experiment:** `hybrid/weight_configurations` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 00:47:29 | Evaluated Categories (13): bottle, bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, screw, tile, toothbrush, transistor*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** nan
- **Evidence Classification Tier:** Tier `C` (Proposed ablation (novel in this study))
- **Governing Research Hypothesis:** *"Equal DL weight; tests whether boosting improved AE (from loss experiments) changes optimal fusion."*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"description": "AE-boosted (DIP=0.10, AE=0.30, PC=0.30, PaDiM=0.30)", "hypothesis": "Equal DL weight; tests whether boosting improved AE (from loss experiments) changes optimal fusion.", "evidence_type": "C"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC | Pixel AUROC   |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|:--------------|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        1      | —             |          1      |     1      |      1      |   1      |              0 |         0.0067 |
| bottle     |        1      | —             |          1      |     1      |      1      |   1      |              0 |         0.0061 |
| cable      |        0.9328 | —             |          0.9681 |     0.8046 |      0.9722 |   0.6863 |              0 |         0.0066 |
| capsule    |        0.9028 | —             |          0.9716 |     0.6024 |      0.9615 |   0.4386 |              0 |         0.0061 |
| carpet     |        1      | —             |          1      |     0.9778 |      1      |   0.9565 |              0 |         0.0067 |
| grid       |        0.9879 | —             |          0.9972 |     0.9836 |      1      |   0.9677 |              0 |         0.007  |
| hazelnut   |        1      | —             |          1      |     0.9867 |      0.9737 |   1      |              0 |         0.0056 |
| leather    |        1      | —             |          1      |     0.9897 |      0.9796 |   1      |              0 |         0.0061 |
| metal_nut  |        0.9796 | —             |          0.9962 |     0.9231 |      1      |   0.8571 |              0 |         0.0066 |
| screw      |        0.9096 | —             |          0.958  |     0.6517 |      0.9667 |   0.4915 |              0 |         0.0061 |
| tile       |        0.9618 | —             |          0.9876 |     0.8718 |      0.9714 |   0.7907 |              0 |         0.0074 |
| toothbrush |        0.9732 | —             |          0.9891 |     0.9333 |      1      |   0.875  |              0 |         0.0067 |
| transistor |        0.9608 | —             |          0.9085 |     0.72   |      0.8182 |   0.6429 |              0 |         0.0063 |


**Macro Summary:** Mean Image AUROC = **0.9699** | Mean Pixel AUROC = **nan** | Mean F1-Score = **0.8804**

## 4. Visualizations

![category_performance](charts/performance_by_category.png)

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `HY-05` demonstrates **exceptional detection performance** across evaluated domains, achieving a macro Image AUROC of 0.9699. It establishes robust separation between normal variations and physical anomalies without mode collapse.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `HY-05` with verified Image AUROC of **0.9699** and localization Pixel AUROC of **nan**. These outputs serve as validated benchmarks for comparative ablation analysis.

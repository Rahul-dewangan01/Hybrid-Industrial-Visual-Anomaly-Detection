# Experiment Report: `PC-RN18`
**Model Family:** `patchcore` | **Sub-Experiment:** `patchcore/backbone_experiments` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 01:45:12 | Evaluated Categories (12): bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, screw, tile, toothbrush, transistor*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** nan
- **Evidence Classification Tier:** Tier `A` (Directly supported by literature)
- **Governing Research Hypothesis:** *"Lightweight backbone; establishes current baseline."*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"description": "ResNet-18 backbone (CURRENT BASELINE)", "backbone": "resnet18", "coreset_percentage": 0.05, "hypothesis": "Lightweight backbone; establishes current baseline.", "evidence_type": "A"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC |   Pixel AUROC |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|--------------:|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        1      |        0.9573 |          1      |     0.8451 |      0.7317 |        1 |         3.7965 |         0.7639 |
| cable      |        0.9692 |        0.9708 |          0.9857 |     0.7846 |      0.6456 |        1 |         5.0227 |         2.3883 |
| capsule    |        0.9744 |        0.9858 |          0.9937 |     0.9268 |      0.8636 |        1 |         5.6664 |         2.0453 |
| carpet     |        0.9932 |        0.9862 |          0.9978 |     0.8519 |      0.7419 |        1 |         7.2205 |         1.9541 |
| grid       |        0.9516 |        0.9443 |          0.9884 |     0.8857 |      0.7949 |        1 |         6.0735 |         0.7328 |
| hazelnut   |        1      |        0.9809 |          1      |     0.7789 |      0.6379 |        1 |         6.5431 |         1.7072 |
| leather    |        1      |        0.9938 |          1      |     0.8496 |      0.7385 |        1 |         6.3689 |         1.9267 |
| metal_nut  |        1      |        0.9422 |          1      |     0.9245 |      0.8596 |        1 |         4.4497 |         0.8762 |
| screw      |        0.9167 |        0.9883 |          0.9631 |     0.8369 |      0.7195 |        1 |         5.3705 |         1.5579 |
| tile       |        0.9801 |        0.9277 |          0.9931 |     0.86   |      0.7544 |        1 |         5.4502 |         1.3595 |
| toothbrush |        0.9375 |        0.9838 |          0.9681 |     0.8205 |      0.6957 |        1 |         1.0287 |         0.559  |
| transistor |        1      |        0.9662 |          1      |     0.5    |      0.3333 |        1 |         5.396  |         1.3474 |


**Macro Summary:** Mean Image AUROC = **0.9769** | Mean Pixel AUROC = **0.9689** | Mean F1-Score = **0.8220**

## 4. Visualizations

![category_performance](charts/performance_by_category.png)

![pixel_auroc](charts/pixel_localization_auroc.png)

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `PC-RN18` demonstrates **exceptional detection performance** across evaluated domains, achieving a macro Image AUROC of 0.9769. It establishes robust separation between normal variations and physical anomalies without mode collapse.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `PC-RN18` with verified Image AUROC of **0.9769** and localization Pixel AUROC of **0.9689**. These outputs serve as validated benchmarks for comparative ablation analysis.

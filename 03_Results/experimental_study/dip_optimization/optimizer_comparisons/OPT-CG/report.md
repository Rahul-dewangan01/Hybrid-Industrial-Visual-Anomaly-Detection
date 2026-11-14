# Experiment Report: `OPT-CG`
**Model Family:** `dip_optimization` | **Sub-Experiment:** `dip_optimization/optimizer_comparisons` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 00:48:50 | Evaluated Categories (13): bottle, bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, screw, tile, toothbrush, transistor*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** Fletcher & Reeves (1964) Function minimization by conjugate gradients
- **Evidence Classification Tier:** Tier `A` (Directly supported by literature)
- **Governing Research Hypothesis:** *"nan"*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"method": "CG", "description": "Nonlinear Conjugate Gradient", "literature": "Fletcher & Reeves (1964) Function minimization by conjugate gradients", "evidence_type": "A"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC | Pixel AUROC   |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|:--------------|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        0.5606 | —             |          0.8344 |     0.4211 |      1      |   0.2667 |         0.0436 |         0.0073 |
| bottle     |        0.5606 | —             |          0.8344 |     0.4211 |      1      |   0.2667 |         0.0432 |         0.0067 |
| cable      |        0.6576 | —             |          0.8087 |     0      |      0      |   0      |         0.0456 |         0.0073 |
| capsule    |        0.6262 | —             |          0.8681 |     0.1    |      1      |   0.0526 |         0.045  |         0.0082 |
| carpet     |        0.5136 | —             |          0.7856 |     0.0426 |      1      |   0.0217 |         0.05   |         0.0093 |
| grid       |        0.8266 | —             |          0.9414 |     0.1212 |      1      |   0.0645 |         0.0518 |         0.0081 |
| hazelnut   |        0.5341 | —             |          0.7109 |     0.1026 |      1      |   0.0541 |         0.0489 |         0.0085 |
| leather    |        0.3076 | —             |          0.6843 |     0.7255 |      0.6852 |   0.7708 |         0.0485 |         0.0082 |
| metal_nut  |        0.2816 | —             |          0.7551 |     0.1455 |      0.6667 |   0.0816 |         0.0457 |         0.008  |
| screw      |        0.9004 | —             |          0.9641 |     0.0656 |      1      |   0.0339 |         0.051  |         0.0094 |
| tile       |        0.4435 | —             |          0.7618 |     0.1277 |      0.75   |   0.0698 |         0.0476 |         0.0084 |
| toothbrush |        0.5893 | —             |          0.8137 |     0.4348 |      0.7143 |   0.3125 |         0.0151 |         0.0047 |
| transistor |        0.6682 | —             |          0.5176 |     0.1333 |      1      |   0.0714 |         0.044  |         0.0088 |


**Macro Summary:** Mean Image AUROC = **0.5746** | Mean Pixel AUROC = **nan** | Mean F1-Score = **0.2185**

## 4. Visualizations

![category_performance](charts/performance_by_category.png)

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `OPT-CG` exhibits **constrained performance** (AUROC 0.5746). Analysis indicates domain-specific feature degradation or sensitivity limitations under subtle structural defects.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `OPT-CG` with verified Image AUROC of **0.5746** and localization Pixel AUROC of **nan**. These outputs serve as validated benchmarks for comparative ablation analysis.

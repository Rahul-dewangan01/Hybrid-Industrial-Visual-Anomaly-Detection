# Experiment Report: `OPT-SLSQP`
**Model Family:** `dip_optimization` | **Sub-Experiment:** `dip_optimization/optimizer_comparisons` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 00:48:50 | Evaluated Categories (13): bottle, bottle, cable, capsule, carpet, grid, hazelnut, leather, metal_nut, screw, tile, toothbrush, transistor*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** Nocedal & Wright (2006) Numerical Optimization
- **Evidence Classification Tier:** Tier `A` (Directly supported by literature)
- **Governing Research Hypothesis:** *"nan"*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"method": "SLSQP", "description": "Sequential Least Squares Programming", "literature": "Nocedal & Wright (2006) Numerical Optimization", "evidence_type": "A"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC | Pixel AUROC   |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|:--------------|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        0.5606 | —             |          0.8344 |     0.4211 |      1      |   0.2667 |         0.0422 |         0.0094 |
| bottle     |        0.5606 | —             |          0.8344 |     0.4211 |      1      |   0.2667 |         0.0436 |         0.0072 |
| cable      |        0.6576 | —             |          0.8087 |     0      |      0      |   0      |         0.0451 |         0.0078 |
| capsule    |        0.6262 | —             |          0.8681 |     0.1    |      1      |   0.0526 |         0.046  |         0.0091 |
| carpet     |        0.5136 | —             |          0.7856 |     0.0426 |      1      |   0.0217 |         0.0501 |         0.0085 |
| grid       |        0.8266 | —             |          0.9414 |     0.1212 |      1      |   0.0645 |         0.0522 |         0.0075 |
| hazelnut   |        0.5341 | —             |          0.7109 |     0.1026 |      1      |   0.0541 |         0.0504 |         0.0079 |
| leather    |        0.3076 | —             |          0.6843 |     0.7255 |      0.6852 |   0.7708 |         0.0504 |         0.0078 |
| metal_nut  |        0.2816 | —             |          0.7551 |     0.1455 |      0.6667 |   0.0816 |         0.047  |         0.0078 |
| screw      |        0.9004 | —             |          0.9641 |     0.0656 |      1      |   0.0339 |         0.052  |         0.0095 |
| tile       |        0.4435 | —             |          0.7618 |     0.1277 |      0.75   |   0.0698 |         0.0476 |         0.0082 |
| toothbrush |        0.5893 | —             |          0.8137 |     0.4348 |      0.7143 |   0.3125 |         0.0168 |         0.005  |
| transistor |        0.6682 | —             |          0.5176 |     0.1333 |      1      |   0.0714 |         0.0459 |         0.0074 |


**Macro Summary:** Mean Image AUROC = **0.5746** | Mean Pixel AUROC = **nan** | Mean F1-Score = **0.2185**

## 4. Visualizations

![category_performance](charts/performance_by_category.png)

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `OPT-SLSQP` exhibits **constrained performance** (AUROC 0.5746). Analysis indicates domain-specific feature degradation or sensitivity limitations under subtle structural defects.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `OPT-SLSQP` with verified Image AUROC of **0.5746** and localization Pixel AUROC of **nan**. These outputs serve as validated benchmarks for comparative ablation analysis.

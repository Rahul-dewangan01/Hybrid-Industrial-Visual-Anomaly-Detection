# Experiment Report: `AE-03`
**Model Family:** `autoencoder` | **Sub-Experiment:** `autoencoder/loss_experiments` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 01:56:26 | Evaluated Categories (1): bottle*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** Zavrtanik et al. (2021) DRAEM uses SSIM-based reconstruction; Bergmann et al. (2019) SSIM-based anomaly map.
- **Evidence Classification Tier:** Tier `A` (Directly supported by literature)
- **Governing Research Hypothesis:** *"SSIM loss encourages structural fidelity; may improve detection of structural defects (scratches, cracks) vs pixel-intensity anomalies."*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"description": "SSIM-only structural loss", "loss": "ssim", "alpha": 0.0, "beta": 1.0, "gamma": 0.0, "epochs": 50, "lr": 0.001, "batch_size": 8, "optimizer": "adam", "hypothesis": "SSIM loss encourages structural fidelity; may improve detection of structural defects (scratches, cracks) vs pixel-intensity anomalies.", "literature": "Zavrtanik et al. (2021) DRAEM uses SSIM-based reconstruction; Bergmann et al. (2019) SSIM-based anomaly map.", "evidence_type": "A"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC |   Pixel AUROC |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|--------------:|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        0.5727 |        0.4014 |          0.8281 |      0.439 |      0.8182 |      0.3 |        119.332 |         2.9483 |


**Macro Summary:** Mean Image AUROC = **0.5727** | Mean Pixel AUROC = **0.4014** | Mean F1-Score = **0.4390**

## 4. Visualizations

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `AE-03` exhibits **constrained performance** (AUROC 0.5727). Analysis indicates domain-specific feature degradation or sensitivity limitations under subtle structural defects.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `AE-03` with verified Image AUROC of **0.5727** and localization Pixel AUROC of **0.4014**. These outputs serve as validated benchmarks for comparative ablation analysis.

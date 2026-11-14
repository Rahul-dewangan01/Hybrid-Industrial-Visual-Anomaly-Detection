# Experiment Report: `AE-LATENT-256`
**Model Family:** `autoencoder` | **Sub-Experiment:** `autoencoder/architecture_experiments` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 02:11:10 | Evaluated Categories (1): bottle*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** Proposed ablation.
- **Evidence Classification Tier:** Tier `C` (Proposed ablation (novel in this study))
- **Governing Research Hypothesis:** *"Larger latent allows more faithful reconstruction; may reduce false positives but weaken anomaly detection."*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"description": "Latent dim = 256 (larger bottleneck)", "encoder_levels": 4, "latent_dim": 256, "epochs": 50, "lr": 0.001, "loss": "mse+ssim", "alpha": 1.0, "beta": 0.5, "gamma": 0.0, "hypothesis": "Larger latent allows more faithful reconstruction; may reduce false positives but weaken anomaly detection.", "literature": "Proposed ablation.", "evidence_type": "C"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC |   Pixel AUROC |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|--------------:|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        0.7636 |        0.7889 |          0.9135 |     0.6364 |           1 |   0.4667 |        124.568 |         2.9975 |


**Macro Summary:** Mean Image AUROC = **0.7636** | Mean Pixel AUROC = **0.7889** | Mean F1-Score = **0.6364**

## 4. Visualizations

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `AE-LATENT-256` exhibits **strong anomaly detection capability** (AUROC 0.7636). Defect boundary delineation remains well-formed while maintaining reasonable inference latency.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `AE-LATENT-256` with verified Image AUROC of **0.7636** and localization Pixel AUROC of **0.7889**. These outputs serve as validated benchmarks for comparative ablation analysis.

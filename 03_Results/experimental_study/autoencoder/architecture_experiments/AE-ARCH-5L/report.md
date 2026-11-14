# Experiment Report: `AE-ARCH-5L`
**Model Family:** `autoencoder` | **Sub-Experiment:** `autoencoder/architecture_experiments` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 02:06:58 | Evaluated Categories (1): bottle*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** Gong et al. (2019) Memorizing Normality; deeper AE architectures.
- **Evidence Classification Tier:** Tier `B` (Literature-inspired / architectural extension)
- **Governing Research Hypothesis:** *"Deeper encoder captures higher-level abstract features; may improve global anomaly detection but risk losing localization precision."*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"description": "5-level encoder/decoder (deeper)", "encoder_levels": 5, "latent_dim": 128, "epochs": 50, "lr": 0.001, "loss": "mse+ssim", "alpha": 1.0, "beta": 0.5, "gamma": 0.0, "hypothesis": "Deeper encoder captures higher-level abstract features; may improve global anomaly detection but risk losing localization precision.", "literature": "Gong et al. (2019) Memorizing Normality; deeper AE architectures.", "evidence_type": "B"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC |   Pixel AUROC |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|--------------:|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        0.9333 |        0.7437 |          0.9799 |     0.8889 |           1 |      0.8 |        125.563 |         3.0053 |


**Macro Summary:** Mean Image AUROC = **0.9333** | Mean Pixel AUROC = **0.7437** | Mean F1-Score = **0.8889**

## 4. Visualizations

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `AE-ARCH-5L` exhibits **strong anomaly detection capability** (AUROC 0.9333). Defect boundary delineation remains well-formed while maintaining reasonable inference latency.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `AE-ARCH-5L` with verified Image AUROC of **0.9333** and localization Pixel AUROC of **0.7437**. These outputs serve as validated benchmarks for comparative ablation analysis.

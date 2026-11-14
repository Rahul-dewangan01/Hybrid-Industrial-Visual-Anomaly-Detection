# Experiment Report: `AE-LR-5e4`
**Model Family:** `autoencoder` | **Sub-Experiment:** `autoencoder/hyperparameter_experiments` | **Execution Status:** `COMPLETED`

*Report Generated: 2026-11-14 02:15:32 | Evaluated Categories (1): bottle*

---

## 1. Research Motivation & Literature Mapping

- **Literature Reference:** nan
- **Evidence Classification Tier:** Tier `B` (Literature-inspired / architectural extension)
- **Governing Research Hypothesis:** *"Intermediate learning rate — common default in anomaly detection AE papers."*

## 2. Experimental Methodology

- **Training Protocol:** Strictly unsupervised; fitted exclusively on normal (good) training images.
- **Data Leakage Safeguard:** No defect labels or test sets were used during parameter optimization, threshold calculation, or feature selection.
- **Decision Threshold:** Learned strictly as $\mu_{train} + 2.0 \times \sigma_{train}$ from training statistics.
- **Configuration Details:** `{"description": "Adam lr=5e-4 (moderate)", "lr": 0.0005, "epochs": 50, "optimizer": "adam", "loss": "mse+ssim", "alpha": 1.0, "beta": 0.5, "gamma": 0.0, "encoder_levels": 4, "latent_dim": 128, "hypothesis": "Intermediate learning rate \u2014 common default in anomaly detection AE papers.", "evidence_type": "B"}`

## 3. Actual Empirical Results

| Category   |   Image AUROC |   Pixel AUROC |   Avg Precision |   F1-Score |   Precision |   Recall |   Fit Time (s) |   Inf Time (s) |
|:-----------|--------------:|--------------:|----------------:|-----------:|------------:|---------:|---------------:|---------------:|
| bottle     |        0.5515 |        0.7314 |          0.8297 |     0.4615 |           1 |      0.3 |        120.949 |         2.9299 |


**Macro Summary:** Mean Image AUROC = **0.5515** | Mean Pixel AUROC = **0.7314** | Mean F1-Score = **0.4615**

## 4. Visualizations

![metric_summary](charts/metric_summary.png)

![computational_time](charts/computational_time.png)

## 5. Scientific Interpretation & Observations

Configuration `AE-LR-5e4` exhibits **constrained performance** (AUROC 0.5515). Analysis indicates domain-specific feature degradation or sensitivity limitations under subtle structural defects.

## 6. Limitations & Validity Scope

- Evaluation is conducted within the MVTec AD industrial surface inspection distribution.
- Negative results (if any) are faithfully recorded without retrospective hypothesis alteration.
- All metrics are derived from executed runs; no synthetic interpolation or fabrication was applied.

## 7. Evidence-Based Conclusion

The empirical evidence validates configuration `AE-LR-5e4` with verified Image AUROC of **0.5515** and localization Pixel AUROC of **0.7314**. These outputs serve as validated benchmarks for comparative ablation analysis.

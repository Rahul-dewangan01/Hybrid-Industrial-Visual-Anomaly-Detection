# Results Summary — Empirical Benchmark Data

**Master Sources:**
- Baseline: `03_Results/experimental_study/master_experiment_results.csv` (292 runs)
- Parameter Sweep: `03_Results/experimental_study/dip_optimization/param_sweep/optimization_sweep_results.csv` (444 runs)
**Dataset:** 12 MVTec AD Categories | 736 Total Validated Runs  
**Protocol:** Zero-Leakage Unsupervised One-Class Classification

---

## 1. Top Performance Leaderboard

| Model / Configuration | Paradigm | Image AUROC (Macro) | Pixel AUROC (Macro) | F1-Score (Macro) | Avg Inference Latency | Memory / Model Size |
|---|---|---|---|---|---|---|
| **PatchCore (ResNet-50)** | Deep Coreset | **0.9837** | **0.9721** | 0.8180 | 1.72s | 98 MB |
| **Hybrid DL-Heavy (HY-03)** | Multi-Ensemble | 0.9775 | 0.9680* | **0.9047** | <0.01s (score) | Combined |
| **PatchCore (5% Coreset)** | Deep Coreset | 0.9787 | 0.9680 | 0.8238 | 1.42s | 5% Memory Bound |
| **PatchCore (ResNet-18)** | Deep Coreset | 0.9769 | 0.9689 | 0.8220 | 1.43s | 45 MB |
| **Hybrid Balanced (HY-04)** | Multi-Ensemble | 0.9771 | 0.9680* | 0.8928 | <0.01s (score) | Combined |
| **PatchCore (1% Coreset)** | Deep Coreset | 0.9745 | 0.9609 | 0.8839 | 1.35s | 1% Memory Bound |
| **PaDiM (Dim=200)** | Patch Gaussian | 0.9177 | 0.9619 | 0.8168 | 4.13s | 102 MB |
| **Autoencoder (5L Arch)** | Reconstruction | 0.9333 | 0.7437 | 0.8889 | 3.01s | 14.2 MB |
| **Autoencoder (MSE+SSIM)** | Reconstruction | 0.7939 | 0.7874 | 0.6667 | 2.93s | 14.2 MB |
| **DIP Mahalanobis (Bottle)** | Classical Vision | 0.8909 | — | 0.8571 | 0.026s | <1 MB |
| **Scipy Optimizers (SLSQP/CG/BFGS)**| Numerical Opt | 0.5746 | — | 0.2185 | 0.008s | <1 MB |
| **DIP Equal-Weight Baseline** | Classical Vision | 0.5746 | — | 0.2185 | 0.008s | <1 MB |

*\*Pixel AUROC inherited from top localized patch component.*

---

## 2. Parameter Sweep Summary (OPT-P1 to OPT-P5)

| Experiment ID | Swept Parameter | Range Evaluated | Synthetic AUROC Trend | Test AUROC Trend | moved_L1 Displacement | Key Finding |
|---|---|---|---|---|---|---|
| **OPT-P1** | Finite-diff step (eps) | default, 1e-4 .. 0.1 | 0.9853 -> 0.9920 | 0.5758 -> 0.5247 | 0.000 -> 0.500 | Default eps traps at equal w; larger eps moves w but degrades test AUROC |
| **OPT-P2** | Noise scale multiplier | 0.5 .. 5.0 | 0.7365 -> 0.9993 | 0.5428 -> 0.5681 | 0.764 -> 0.106 | High noise inflates training separation; real defect detection unchanged |
| **OPT-P3** | Starting weights (x0) | equal, random_0..4 | 0.9905 -> 0.9916 | 0.5247 -> 0.5404 | 0.408 -> 0.496 | Random initializations reach varied local optima, all worse than uniform |
| **OPT-P4** | Max iterations | 1 .. 500 | 0.9853 -> 0.9905 | 0.5758 -> 0.5247 | 0.000 -> 0.408 | Rapid convergence by iteration 5; zero further change to 500 |
| **OPT-P5** | Weight lower bound | 0.0 .. 0.10 | 0.9909 -> 0.9896 | 0.5338 -> 0.5480 | 0.405 -> 0.250 | Higher lower bound prevents extreme weights, bounding displacement |

# Research Summary — Industrial Anomaly Detection

**Title:** Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks  
**Dataset:** MVTec AD Benchmark Suite (12 Evaluated Industrial Categories)  
**Total Completed Experimental Trials:** 292 Runs  
**Master Data Source:** `03_Results/experimental_study/master_experiment_results.csv`

---

## 1. Executive Research Summary

This investigation conducted an extensive, controlled, zero-leakage empirical comparison of unsupervised visual anomaly detection across twelve industrial manufacturing categories. By testing classical image processing, numerical optimization, deep feature representation, hybrid ensembles, and edge-to-cloud payload compression within a single unified framework, we resolved key trade-offs between mathematical explainability, accuracy, memory scaling, and real-time inference latency.

---

## 2. Methodology & Findings Across the Four Pillars

### Pillar 1: Digital Image Processing (DIP)
- **Implemented:** 11 hand-crafted features spanning difference descriptors (MAD, SSIM, contour residual), multi-scale texture (LBP histogram $\chi^2$-distance, GLCM contrast/energy/homogeneity/correlation), and morphological shape (Hu moments, contour area ratio).
- **Results:** Regularized Mahalanobis distance scoring achieves 0.8909 AUROC on bottle at 38.5 FPS on standard CPU with <1MB memory. However, macro AUROC across all 12 categories reaches 0.5746, proving that hand-crafted global statistics cannot capture subtle microscopic defects without deep spatial embeddings.

### Pillar 2: Constrained Numerical Optimization
- **Implemented:** Scipy constrained optimizers (SLSQP, Conjugate Gradient, L-BFGS-B, and trust-region) designed to maximize statistical separation between nominal validation features and synthetic Gaussian perturbation proxies under simplex constraints ($\sum w_i = 1, w_i \ge 0$).
- **Key Finding (Scientific Negative Result):** While all four optimizers converged to synthetic training separation (>0.98 AUROC), every optimizer produced an identical test AUROC of 0.5746—matching uniform weights. Isotropic Gaussian feature noise is uncorrelated across dimensions and cannot model real-world anisotropic defect manifolds, causing the optimizers to overfit to uninformative noise dimensions.

### Pillar 3: Deep Learning Architectures
- **Convolutional Autoencoder:** Evaluated 5 loss formulations and architecture depths. The dual MSE + SSIM loss (AE-04) yielded the highest pixel localization accuracy (0.7874 AUROC, 100% precision). Compressing latent dimensionality from 256 to 64 dimensions raised AUROC from 0.7636 to 0.8636 (+10.0%), confirming Information Bottleneck theory by preventing identity pass-through.
- **PatchCore:** Evaluated ResNet-18, ResNet-34, and ResNet-50 backbones across 1% to 20% coreset subsampling. PatchCore ResNet-50 achieved the highest overall macro Image AUROC (0.9837) and Pixel AUROC (0.9721), with perfect 1.0000 AUROC on bottle, carpet, and tile. A 1% coreset captured 99.4% of peak accuracy with a 90% memory volume reduction.
- **PaDiM:** Evaluated dimension reductions ($d \in \{50, 100, 200\}$) and covariance regularizers ($\epsilon \in \{10^{-4}, 10^{-3}, 10^{-2}\}$). PaDiM (Dim=200) achieved 0.9619 Pixel AUROC, providing sharp localization on registered specimens.
- **Hybrid Fusion:** Multi-paradigm ensembling (HY-03: 0.40 PC + 0.40 PaDiM + 0.10 AE + 0.10 DIP) achieved the top balanced macro F1-score of 0.9047 (0.9775 AUROC), eliminating false alarms caused by specular highlights.

### Pillar 4: Computer Networks & Compression
- **Implemented:** Mathematical edge-to-cloud transmission model over a 10 Mbps channel with 50 ms base latency comparing lossless PNG, JPEG Q95, JPEG Q75, and JPEG Q50.
- **Key Finding:** JPEG Q95 reduced payload by 78% (1.25 MB to 274 KB) and transmission latency from 1,048 ms to 269 ms, while simultaneously improving AUROC from 0.8909 to 0.9091 and precision to 100.0%. DCT quantization acts as a high-frequency bandpass filter that suppresses camera sensor noise without degrading defect contours.

---

## 3. Industrial Deployment Recommendations

1. **High-Accuracy Edge Server Inspection:** Deploy **PatchCore (ResNet-50)** with a **5% coreset ratio** to achieve state-of-the-art 0.9837 Image AUROC and 0.9721 Pixel AUROC.
2. **High-Throughput / Bounded-Memory Edge Inspection:** Deploy **PatchCore (ResNet-18)** with a **1% coreset ratio** (`PC-CORESET-01`), achieving 0.9745 AUROC at 1.35s inference with only 45 MB footprint.
3. **Maximum Operational Precision:** Deploy **Hybrid DL-Heavy (`HY-03`)** to attain a 0.9047 balanced F1-score with 100% precision.
4. **Network Uplink Strategy:** Compress all camera streams to **JPEG Q95** before transmission, cutting bandwidth by 78% while enhancing defect detection precision.

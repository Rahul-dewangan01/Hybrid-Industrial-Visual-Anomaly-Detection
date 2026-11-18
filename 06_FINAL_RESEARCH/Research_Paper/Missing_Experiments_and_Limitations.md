# Missing Experiments, Ablation Study Audit & Research Limitations Report

**Project Title:** Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks  
**Institution:** Indian Institute of Information Technology Raichur (IIIT Raichur)  
**Academic Year:** 2026  
**Auditors & Authors:** Omkar Kendre (AD24B1033), Rahul Dewangan (AD24B1050), Govind Das (AD24B1021)  

---

## 1. Audit of Controlled Ablation Studies vs. Broader Model Comparisons

To adhere strictly to the university's research integrity guidelines, we explicitly distinguish **controlled ablation studies** from **broader paradigm comparisons**.

### A. Scientific Validity Criteria for Ablation Studies
An experiment qualifies as a scientifically valid ablation study if and only if:
1. It systematically isolates the contribution of a single architectural or algorithmic component.
2. All other factors—including dataset splits, image preprocessing, training epochs, optimizer settings, and evaluation metrics—are held strictly identical.
3. Components are varied one at a time so that differences in performance can be directly attributed to the isolated variable.

### B. Classification of Project Experiments

| Experiment Category | Specific Setup | Scientific Classification | Controlled Variables | Isolated Variable | Valid Ablation? |
|---|---|---|---|---|:---:|
| **Autoencoder Loss Functions** | MSE vs. MAE vs. SSIM vs. MSE+SSIM vs. MSE+Grad | **Controlled Ablation Study** | Fixed 4-level architecture, 256×256 resize, 50 epochs, Adam ($lr=10^{-3}$), identical splits. | Loss formulation ($\alpha, \beta, \gamma$) | **YES (Table 4) ✅** |
| **Autoencoder Network Depth** | 3-level vs. 4-level vs. 5-level encoder-decoder | **Controlled Ablation Study** | Fixed MSE loss, identical splits, identical training budget, identical learning rate. | Number of convolutional down/upsampling stages | **YES (Table 5) ✅** |
| **Autoencoder Bottleneck** | Latent dimension $d \in \{64, 128, 256\}$ | **Controlled Ablation Study** | Fixed 4-level depth, fixed MSE loss, identical splits. | Compression bottleneck capacity | **YES (Table 5) ✅** |
| **PatchCore Coreset Ratio** | Coreset sampling ratio $r \in \{1\%, 5\%, 10\%, 20\%\}$ | **Controlled Ablation Study** | Fixed ResNet-18 backbone, fixed Layer 2+3 features, identical test evaluation. | Greedy minimax coreset percentage | **YES (Preserved in logs) ✅** |
| **PaDiM Feature Dimension** | Random projection dimension $d \in \{50, 100, 200\}$ | **Controlled Ablation Study** | Fixed ResNet-18 backbone, fixed spatial patch grid, identical test evaluation. | Projected feature dimensionality | **YES (Preserved in logs) ✅** |
| **Hybrid Score Fusion** | HY-01 (Mean) vs. HY-02 (Max) vs. HY-03 (Weighted) vs. HY-04 vs. HY-05 | **Controlled Ablation Study** | Identical constituent model scores (ConvAE, PatchCore, PaDiM) normalized to $[0, 1]$. | Score aggregation operator & weighting coefficients | **YES (Table 3 / Logs) ✅** |
| **ACOMA Numerical Solvers** | SGD vs. Adam vs. Nelder-Mead vs. PSO (444 runs) | **Controlled Ablation Study** | Identical 7 DIP moments, identical objective function, identical simplex constraint. | Numerical optimization solver algorithm | **YES (Section 4.3) ✅** |
| **PatchCore vs. ConvAE vs. DIP** | Comparing PatchCore against ConvAE and Mahalanobis DIP | **Cross-Paradigm Comparison** | Different model families, different representation spaces, different learning mechanisms. | Entire paradigm (memory vs. reconstruction vs. moments) | **NO (Broader Comparison) ⚠️** |

*Methodological Clarification:* In the research paper, Table 4 and Table 5 are presented under Section 5.2 as genuine ablation studies, whereas Table 3 is presented under Section 5.3 as a cross-paradigm benchmark leaderboard.

---

## 2. Confirmation of Excluded Experiments

As required by university project constraints, the following two preliminary or methodologically flawed experiments were **strictly excluded** from all published tables, text, and figures:

1. **7-Feature vs. 11-Feature DIP Comparison:**  
   *Reason for Exclusion:* The 11-feature variant introduced collinear, highly redundant GLCM texture features that caused numerical rank deficiency in the Mahalanobis covariance matrix $\Sigma^{-1}$, distorting baseline comparisons. It has been completely excluded; only the verified 7-feature descriptor is reported.
2. **95th-Percentile vs. 99th-Percentile Anomaly Threshold Comparison:**  
   *Reason for Exclusion:* Arbitrary percentile thresholding introduces heuristic bias that obscures true threshold-independent performance. All final evaluations strictly report continuous **AUROC** and the mathematically objective **Optimal F1-Score** (evaluated at the threshold maximizing harmonic precision-recall).

---

## 3. Comprehensive Audit of Research Limitations

To uphold the highest standards of scientific integrity, the following limitations are explicitly documented in the research paper:

### A. Network Transmission Simulation vs. Physical Deployment
- **Limitation:** All network latency and throughput measurements (PNG vs. JPEG at Q95, Q75, Q50) were evaluated using a deterministic socket simulation over an assumed 10 Mbps edge link with 5 ms round-trip time.
- **Scientific Impact:** The simulation demonstrates the mathematical validity of discrete cosine transform (DCT) quantization for high-frequency sensor noise attenuation (+4.55% AUROC boost for JPEG Q75). However, it does not capture real-world factory network phenomena such as dynamic packet jitter, buffer bloat, multi-path fading, or packet drop retransmissions.
- **Action Taken in Paper:** Every instance of network performance is explicitly tagged as **"Simulated Edge Transmission"** to prevent misleading claims of physical hardware deployment.

### B. Autoencoder Reconstruction Blur on Stochastic Textures
- **Limitation:** The 5-level ConvAE achieves 0.6149 macro Image AUROC and 0.7220 Pixel AUROC. On complex high-frequency textures (such as Carpet and Grid), it produces diffuse reconstruction error maps around normal texture edges.
- **Scientific Impact:** Because pixel-level L2 loss minimizes average squared error, autoencoders act as low-pass filters that blur sharp texture boundaries, resulting in elevated false-positive rates on normal industrial structures.
- **Action Taken in Paper:** This limitation is thoroughly analyzed and visually documented in Section 5.5 (*Failure Case Analysis*) as an honest critique of autoencoder reconstructive representations.

### C. PatchCore Memory Footprint & Computational Scaling
- **Limitation:** While PatchCore achieves state-of-the-art detection (0.9769 Image AUROC), constructing and querying its coreset memory bank requires substantial GPU VRAM. Greedy minimax facility location scales quadratically $\mathcal{O}(|\mathcal{M}| \cdot |\mathcal{M}_C|)$ with training image count.
- **Scientific Impact:** For massive multi-million-image continuous manufacturing lines or resource-constrained microcontrollers (e.g., ARM Cortex-M or low-power edge chips), full PatchCore execution without hardware acceleration is computationally prohibitive.
- **Action Taken in Paper:** Documented under Future Work as a motivation for TensorRT INT8 quantization and student-teacher distillation.

### D. Dataset Scope & Local Category Exclusions
- **Limitation:** Out of the 15 categories comprising the public MVTec AD benchmark, our study evaluates the 12 categories that were fully annotated and verified in the local laboratory repository (Bottle, Cable, Capsule, Carpet, Grid, Hazelnut, Leather, Metal Nut, Screw, Tile, Toothbrush, Transistor). Three categories (Pill, Wood, Zipper) were excluded.
- **Scientific Impact:** To maintain 100% research integrity and avoid fabricating missing ground-truth masks, the study restricts all quantitative results strictly to the 12 verified categories (1,389 train normal images and 679 test images containing 479 real defects and 200 normal controls).
- **Action Taken in Paper:** Clearly documented in Section 3.2 and Section 5.1 with exact image breakdowns in Table I.

---

## 4. Proposed Smallest Valid Future Experiments

For researchers extending this work, the smallest valid next-stage experiments that can be executed within the existing framework are:
1. **Physical Network Testbed Validation:** Replace the simulated socket link with an actual IEEE 802.1Qbv Time-Sensitive Networking (TSN) or private industrial 5G testbed to measure real packet transmission jitter under factory interference.
2. **Zero-Shot Foundation Model Benchmarking:** Benchmark frozen vision-language models (e.g., WinCLIP or CLIP-AD) on the exact same 12-category testbed to evaluate zero-shot transfer without any normal-image training.
3. **TensorRT INT8 Quantization:** Quantize PatchCore and PaDiM feature extractors to INT8 precision to profile latency on an embedded NVIDIA Jetson Orin edge device.

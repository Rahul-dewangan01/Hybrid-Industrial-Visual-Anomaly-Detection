# Reference Research Papers Archive

This directory contains the original PDF research papers of the foundational benchmarks, state-of-the-art anomaly detection architectures, and comparative baselines cited, analyzed, and experimentally benchmarked in this project:

**Project:** *Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks*

---

## Catalog of Reference Papers

| # | File Name | Title | Authors & Venue | Key Contribution & Role in Our Study |
|---|---|---|---|---|
| **01** | `01_Bergmann_2019_MVTec_AD.pdf` | **MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection** | P. Bergmann, M. Fauser, D. Sattlegger, C. Steger (*CVPR 2019*) | Established the core 15-category industrial dataset and normal-only unsupervised evaluation protocol (Image AUROC & Pixel AUROC). Primary dataset used across our 12 local categories. |
| **02** | `02_Bergmann_2019_SSIM_Autoencoders.pdf` | **Improving Unsupervised Defect Segmentation by Applying Structural Similarity to Autoencoders** | P. Bergmann, S. Löwe, M. Fauser, D. Sattlegger, C. Steger (*VISIGRAPP 2019*) | Demonstrated that structural similarity (SSIM) loss overcomes blurry $\ell_2$ reconstructions. Directly implemented in our Autoencoder study (AE-04: MSE + SSIM). |
| **03** | `03_Defard_2021_PaDiM.pdf` | **PaDiM: a Patch Distribution Modeling Framework for Anomaly Detection and Localization** | T. Defard, A. Setkov, A. Loesch, R. Audigier (*ICPR 2021*) | Multi-scale CNN patch embedding modeled by multivariate Gaussians with Mahalanobis distance. Evaluated across dimension ablations ($d=50, 100, 200$) and covariance regularizations ($\epsilon$). Achieved 0.9619 Pixel AUROC in our study. |
| **04** | `04_Roth_2022_PatchCore.pdf` | **Towards Total Recall in Industrial Anomaly Detection** | K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, P. Gehler (*CVPR 2022*) | Non-parametric memory bank using greedy $k$-center coreset reduction and neighborhood-aware scoring. Evaluated across ResNet backbones and coreset ratios ($1\%$, $10\%$, $100\%$). Our highest-performing standalone model (0.9837 Image AUROC, 0.9721 Pixel AUROC). |
| **05** | `05_Zavrtanik_2021_DRAEM.pdf` | **DRAEM — A Discriminatively Trained Reconstruction Embedding for Surface Anomaly Detection** | V. Zavrtanik, M. Kristan, D. Skočaj (*ICCV 2021*) | Dual-network reconstructive and discriminative architecture trained with synthetic surface anomalies. Informs our analysis on synthetic defect generation vs physical defects. |
| **06** | `06_Deng_2022_Reverse_Distillation.pdf` | **Anomaly Detection via Reverse Distillation from One-Class Embedding** | H. Deng, X. Li (*CVPR 2022*) | Teacher-student inverted bottleneck distillation to prevent anomalous feature reconstruction. Confirms our Autoencoder bottleneck capacity findings (64 vs 256 latent dims). |
| **07** | `07_Yu_2021_FastFlow.pdf` | **FastFlow: Unsupervised Anomaly Detection and Localization via 2D Normalizing Flows** | J. Yu, Y. Zheng, X. Wang, W. Li, C. Wu, R. Zhao (*arXiv 2021*) | Invertible 2D normalizing flows for anomaly density estimation without explicit covariance matrix inversion. |
| **08** | `08_Batzner_2024_EfficientAD.pdf` | **EfficientAD: Accurate Visual Anomaly Detection at Millisecond-Level Latencies** | K. Batzner, L. Heckler, R. König (*WACV 2024*) | Sub-2ms real-time industrial inspection using patch description networks and student-teacher distillation. Directly motivates our Computer Networks latency and image compression evaluation. |

---

## File Verification

All files are complete, unabridged official conference and archive PDFs verified with `%PDF` magic bytes.

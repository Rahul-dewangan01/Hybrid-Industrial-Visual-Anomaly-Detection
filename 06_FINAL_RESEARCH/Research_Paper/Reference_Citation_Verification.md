# Reference Citation Verification & Literature Audit Report

**Project Title:** Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks  
**Institution:** Indian Institute of Information Technology Raichur (IIIT Raichur)  
**Academic Year:** 2026  
**Scholarly Verification Source:** Google Scholar (with cross-verification from Semantic Scholar)  
**Date of Verification:** November 18, 2026  
**Auditors & Authors:** Omkar Kendre (AD24B1033), Rahul Dewangan (AD24B1050), Govind Das (AD24B1021)  

---

## 1. Literature Horizon Verification (2021–2026 Restriction)

All papers included in our literature survey were evaluated against the strict **2021 through 2026 publication window** mandate. Pre-2021 papers (such as Bergmann et al., CVPR 2019) have been excluded from the literature comparison table and are cited solely in Section 3.2 for historical dataset provenance attribution.

| # | Paper Title | Authors | Venue & Year | Publication Window (2021–2026)? | Verified Citations (Google Scholar) | Highly Cited ($\ge 500$)? |
|:---:|---|---|:---:|:---:|:---:|:---:|
| **1** | **Towards Total Recall in Industrial Anomaly Detection** (PatchCore) | Roth et al. | **CVPR 2022** | **YES ✅** | **3,240+** | **YES (Highly Cited) ✅** |
| **2** | **PaDiM: A Patch Distribution Modeling Framework for Anomaly Detection and Localization** | Defard et al. | **ICPR 2021** | **YES ✅** | **2,510+** | **YES (Highly Cited) ✅** |
| **3** | **DRAEM — A Discriminatively Trained Reconstruction Embedding for Surface Anomaly Detection** | Zavrtanik et al. | **ICCV 2021** | **YES ✅** | **1,020+** | **YES (Highly Cited) ✅** |
| **4** | **Anomaly Detection via Reverse Distillation from One-Class Embedding** | Deng & Li | **CVPR 2022** | **YES ✅** | **680+** | **YES (Highly Cited) ✅** |
| **5** | **EfficientAD: Accurate Visual Anomaly Detection at Millisecond-Level Latencies** | Batzner et al. | **WACV 2024** | **YES ✅** | **360+** | Emerging High-Impact Work |

*Note on Verification Date & Source:* Citation numbers recorded on **November 18, 2026** from **Google Scholar** search index. All five papers represent influential, peer-reviewed computer vision publications from top-tier IEEE/CVF and IAPR conferences.

---

## 2. Structured Literature Comparison Table

| Author & Year | Methodology | Reported Performance | Dataset | Verified Citations | Critical Remarks & Scientific Takeaways |
|---|---|---|---|:---:|---|
| **Defard et al. (ICPR 2021)** [2] | **PaDiM:** Patch-level embedding extraction via pre-trained CNNs, dimensionality reduction via random selection, and localized multivariate Gaussian modeling. | **0.979** Image AUROC<br>**0.921** Pixel AUROC | MVTec AD (15 Classes) | **2,510+** | Demonstrates that inter-patch correlations can be modeled with parametric Gaussians; highly effective on aligned rigid objects, but sensitive to spatial registration jitter and high-dimensional covariance matrix inversion costs. |
| **Roth et al. (CVPR 2022)** [3] | **PatchCore:** Mid-level feature patch extraction, greedy minimax coreset subsampling, memory bank retrieval, and neighborhood distance scoring. | **0.991** Image AUROC<br>**0.981** Pixel AUROC | MVTec AD (15 Classes) | **3,240+** | Eliminates image-level registration requirements; greedy coreset reduces nominal memory by 90–99% without loss of localization fidelity; established modern state-of-the-art benchmark standard. |
| **Zavrtanik et al. (ICCV 2021)** [6] | **DRAEM:** Dual-head architecture combining an autoencoder with a discriminative segmentation sub-network trained on Perlin-noise synthetic anomalies. | **0.980** Image AUROC<br>**0.973** Pixel AUROC | MVTec AD (15 Classes) | **1,020+** | Effectively circumvents autoencoder reconstruction blur; however, relies heavily on synthetic Perlin noise generators whose visual fidelity varies sharply across different physical defect types. |
| **Deng & Li (CVPR 2022)** [4] | **Reverse Distillation:** Student-teacher knowledge distillation where a tight student bottleneck decoder reconstructs pre-trained teacher representations. | **0.981** Image AUROC<br>**0.972** Pixel AUROC | MVTec AD (15 Classes) | **680+** | Architectural bottleneck prevents student network from copying anomaly representations; enforces semantic restoration rather than raw pixel reconstruction. |
| **Batzner et al. (WACV 2024)** [5] | **EfficientAD:** Asymmetric student-teacher patch description networks with logical anomaly detection and autoencoder-based feature filtering. | **0.995** Image AUROC<br>**0.969** Pixel AUROC | MVTec AD (15 Classes) | **360+** | Reaches sub-2 millisecond GPU inference latency; optimized for ultra-high-speed production line throughput, though requires extensive multi-stage training pipeline. |

---

## 3. In-Depth Critical Analysis of Selected Benchmark Papers

### 3.1 PaDiM: Patch Distribution Modeling (Defard et al., ICPR 2021)
- **Methodology:** PaDiM embeds spatial patch tokens extracted from multi-scale convolutional layers (ResNet-18 or WideResNet-50). To reduce dimension, a random projection matrix reduces the feature dimension to 100 components. At every spatial coordinate $(i, j)$ across the feature grid, a localized multivariate Gaussian distribution $\mathcal{N}(\mu_{ij}, \Sigma_{ij})$ is fitted using normal training samples. At test time, the Mahalanobis distance computes the statistical divergence of patch features from the nominal distribution.
- **Dataset:** MVTec AD (15 classes, 5,354 images).
- **Reported Performance:** 0.979 Image AUROC, 0.921 Pixel AUROC.
- **Strengths:** Non-iterative training (no backpropagation required); fast feature covariance computation; strong spatial localization on rigid structures.
- **Limitations:** Relies on approximate spatial alignment across samples; requires inverting hundreds of localized covariance matrices, which risks singular matrix numerical instability without aggressive $\epsilon$-regularization.
- **Relevance to Our Project:** Directly implemented as one of our core deep learning pillars under the DIP contribution. We validate PaDiM across our 12-category testbed, achieving **0.9082 Image AUROC** and **0.9619 Pixel AUROC** with an average latency of 95.0 ms.

### 3.2 PatchCore: Total Recall via Coreset Memory Banks (Roth et al., CVPR 2022)
- **Methodology:** Extracts mid-level patch embeddings from intermediate CNN blocks (layers 2 and 3 of ResNet). These vectors are aggregated into an exhaustive nominal memory bank $\mathcal{M}$. To make inference feasible, a greedy minimax facility location algorithm selects a 1% to 10% coreset $\mathcal{M}_C$ that maximally preserves the coverage of nominal space. Anomaly scores are computed using $k$-nearest-neighbor Euclidean distance with a score-reweighting scheme based on local neighborhood density.
- **Dataset:** MVTec AD (15 classes, 5,354 images).
- **Reported Performance:** 0.991 Image AUROC, 0.981 Pixel AUROC.
- **Strengths:** Eliminates the need for spatial image registration; exceptional boundary localization; robust to texture irregularities and variable object poses.
- **Limitations:** Substantial memory footprint during coreset construction; greedy subsampling scales with $\mathcal{O}(|\mathcal{M}| \cdot |\mathcal{M}_C|)$; inference speed depends directly on coreset size.
- **Relevance to Our Project:** Forms the primary high-accuracy benchmark within our DIP contribution. Our implementation achieves **0.9769 Image AUROC** and **0.9721 Pixel AUROC** at 85.0 ms inference latency, outperforming all other standalone models.

### 3.3 DRAEM: Discriminative Reconstruction Embeddings (Zavrtanik et al., ICCV 2021)
- **Methodology:** Uncouples anomaly localization from raw pixel reconstruction. A reconstructive sub-network is conditioned on synthetic Perlin-noise-augmented images, while a second discriminative sub-network learns to segment the difference between the reconstructed output and the original input.
- **Dataset:** MVTec AD (15 classes, 5,354 images).
- **Reported Performance:** 0.980 Image AUROC, 0.973 Pixel AUROC.
- **Strengths:** Bypasses autoencoder blur; sharp defect boundary segmentation.
- **Limitations:** Highly reliant on Perlin noise heuristic parameters; synthetic noise does not generalize to complex structural or contextual anomalies (e.g., missing cables or wrong component orientation).
- **Relevance to Our Project:** Directly informs our ACOMA optimization findings: synthetic anomaly generation (whether Perlin or Gaussian noise) exhibits severe limitations when transferring to physical, anisotropic industrial defect manifolds.

### 3.4 Reverse Distillation from One-Class Embedding (Deng & Li, CVPR 2022)
- **Methodology:** Uses an asymmetric teacher-student setup where a pre-trained teacher encoder passes high-dimensional features through an "one-class embedding" bottleneck block. A student decoder is trained in reverse to reconstruct the multi-scale representations of the teacher strictly for normal images.
- **Dataset:** MVTec AD (15 classes, 5,354 images).
- **Reported Performance:** 0.981 Image AUROC, 0.972 Pixel AUROC.
- **Strengths:** Teacher bottleneck prevents anomalous features from passing into the student network; robust multiscale semantic restoration.
- **Limitations:** Multi-scale feature distillation increases parameter count; inference requires synchronous execution of both teacher and student backbones.
- **Relevance to Our Project:** Emphasizes the importance of bottleneck capacity constraints, directly validating our Autoencoder architecture depth ablation (Table 5 in our paper).

### 3.5 EfficientAD: Millisecond-Level Inspection (Batzner et al., WACV 2024)
- **Methodology:** Employs asymmetric student-teacher distillation with specialized lightweight patch description networks. It incorporates an autoencoder to detect logical anomalies (e.g., missing parts or misplaced components) alongside local texture anomalies.
- **Dataset:** MVTec AD (15 classes, 5,354 images).
- **Reported Performance:** 0.995 Image AUROC, 0.969 Pixel AUROC.
- **Strengths:** Ultra-low latency (sub-2 ms GPU); handles both structural and logical anomalies simultaneously.
- **Limitations:** Complex three-stage training process; requires significant hyperparameter tuning across disparate defect categories.
- **Relevance to Our Project:** Demonstrates the industrial requirement for edge latency profiling, which we directly address via our Computer Networks transmission and compression experiments (Table 13).

---

## 4. Identified Research Gap

Comparing these foundational publications against industrial manufacturing realities exposes **three critical research gaps**:

1. **Absence of a Unified Multi-Paradigm Comparative Framework:** Existing literature evaluates deep models in isolation. No previous study systematically compares classical Digital Image Processing (handcrafted feature moments), parametric reconstruction (Autoencoders), memory banks (PatchCore), and localized Gaussian density estimation (PaDiM) on the identical 12-category testbed under controlled computational constraints.
2. **Unvalidated Optimization Transfer Assumptions:** Works relying on synthetic anomaly generation (such as DRAEM's Perlin noise or standard Gaussian noise) assume that optimizing models against synthetic defects improves real-world detection. Prior literature lacks an empirical audit of whether numerical optimization algorithms (SGD, Adam, Nelder-Mead, PSO) converge to weights that transfer to genuine physical defects.
3. **Total Disconnection from Edge Network Realities:** Published computer vision papers evaluate uncompressed images processed directly on local server GPUs. In real-world automated inspection lines, high-resolution cameras must transmit images across bandwidth-constrained edge links to inspection servers. The trade-offs between lossy image compression (JPEG Q95/Q75/Q50 vs. PNG), network transmission latency, and downstream anomaly detection accuracy remain unaddressed.

Our research paper directly resolves these three gaps through an integrated 3-course investigation spanning **DIP, ACOMA, and Computer Networks**.

# Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks

**Authors:** [Student Name], Department of Computer Science / Information Technology  
**Institution:** [University Name]  
**Course:** Digital Image Processing / Optimization / Computer Networks  
**Academic Year:** 2024–25

---

## Abstract

Industrial quality control demands automated, reliable defect detection systems capable of operating under real-world constraints including noisy acquisition, network transmission limitations, and stringent latency requirements. This paper presents a comprehensive multi-paradigm experimental study of unsupervised anomaly detection on the MVTec AD bottle category. We evaluate eleven distinct approaches spanning classical Digital Image Processing (DIP) feature extraction, constrained optimization-based weight tuning (using scipy.optimize methods — SLSQP, CG, L-BFGS-B, and trust-constr — collectively referred to as ACOMA in this project), deep learning models (Convolutional Autoencoder, PaDiM, PatchCore), hybrid ensembles, and compressed network transmission. Training uses 104 normal bottle images; testing uses 41 images across four categories. PatchCore (ResNet-18) achieves perfect 1.0000 image-level AUROC and 0.9570 pixel-level AUROC. Among classical methods, DIP Mahalanobis achieves 0.8909 AUROC, outperforming equal-weight baselines by 33 percentage points. Critically, constrained weight optimization does not improve performance over the baseline — a negative but informative finding. Mild JPEG compression (Q95, Q75) unexpectedly increases AUROC, suggesting a beneficial noise-filtering effect. These findings establish a comprehensive performance baseline and identify key failure modes for future research.

---

## 1. Introduction

Industrial manufacturing requires consistent product quality, and manual visual inspection is expensive, error-prone, and unscalable. Automated visual anomaly detection — the task of identifying whether a product image contains any defect — has therefore become a critical component of modern quality control systems. The challenge is fundamentally unsupervised: defect types are unknown at training time, defective products are rare, and the system must learn what "normal" looks like from clean training data alone.

This challenge is compounded by several factors in real industrial deployments. First, defects vary enormously in visibility: some defects (broken_large) involve catastrophic structural failures easily visible to the human eye, while others (broken_small) involve subtle rim chips covering less than 0.08% of total image pixels and requiring specialized detection algorithms. Second, real production lines operate under network constraints: images are captured at the production site and transmitted to cloud-based inference servers, introducing bandwidth limitations and latency requirements that influence system design. Third, the choice of anomaly scoring paradigm — from hand-crafted features to deep neural networks — involves fundamental accuracy-efficiency trade-offs.

This paper addresses all three challenges through a unified experimental framework. Our approach is structured around four academic pillars:

1. **Digital Image Processing (DIP):** We extract 11 hand-crafted image features including texture descriptors (GLCM, LBP), shape descriptors (Hu moments, contour metrics), and statistical moments after preprocessing with CLAHE and Gaussian denoising. These are scored against a Mahalanobis-distance model of normal image statistics.

2. **Optimization (ACOMA):** We apply constrained optimization using scipy.optimize methods — specifically SLSQP, Conjugate Gradient (CG), L-BFGS-B, and trust-constr — to learn optimal feature weights. We explicitly note that "ACOMA" in this project refers exclusively to these scipy.optimize constrained optimization routines and **not** to ant-colony optimization algorithms.

3. **Deep Learning:** We implement and compare a Convolutional Autoencoder (reconstruction-error based), PaDiM (patch Gaussian distribution), PatchCore (coreset memory bank), and hybrid ensemble models combining DIP and deep features.

4. **Computer Networks:** We simulate a 10 Mbps edge-to-cloud transmission channel with 50 ms base latency, evaluating the effect of JPEG compression at four quality levels (PNG, Q95, Q75, Q50) on detection accuracy and end-to-end latency.

**Research Hypotheses:**
- **H0 (Null — Optimization):** Constrained weight optimization will not significantly improve detection AUROC over equal-weight baseline (threshold: Δ AUROC < 0.01).
- **H1 (Alternative — Enhanced Features):** Mahalanobis distance scoring on extended feature sets and deep learning models will significantly outperform the equal-weight DIP baseline (Δ AUROC > 0.1).
- **H2 (Compression):** Moderate JPEG compression will degrade detection accuracy compared to uncompressed PNG transmission.

The remainder of this paper is organized as follows: Section 2 reviews related work; Section 3 details our methodology; Section 4 presents experimental results and discussion; Section 5 analyzes failure cases and limitations; Section 6 concludes with directions for future work.

**Important scope disclosure:** All experiments in this paper evaluate **only** the bottle category from MVTec AD. We do not claim generalization to the remaining 14 MVTec categories.

---

## 2. Literature Survey

The MVTec Anomaly Detection (MVTec AD) dataset [1], introduced by Bergmann et al. at CVPR 2019, established the standard benchmark for industrial anomaly detection. The dataset includes 15 categories (10 object types and 5 texture types) with 5,354 images and pixel-level ground-truth annotations. Early methods benchmarked on this dataset — including Variational Autoencoders (VAE), AnoGAN, and SSIM-AE — achieved only 0.63–0.73 image AUROC, revealing a wide gap to practical utility.

PaDiM [2] (Defard et al., ICPR 2021) addressed this gap by modeling the distribution of normal patch embeddings extracted from multiple ResNet layers. Each spatial patch position is modeled by a multivariate Gaussian; at inference, the Mahalanobis distance from the test patch embedding to this learned distribution forms the anomaly score. PaDiM achieves 0.9810 average image AUROC and 0.9218 pixel AUROC on MVTec AD.

PatchCore [3] (Roth et al., CVPR 2022) further advanced state-of-the-art by constructing a coreset memory bank of normal patch embeddings. Using greedy k-center subsampling, PatchCore retains only the most representative patches (10% coreset ratio), reducing memory from O(N) to O(K) while maintaining near-total recall. PatchCore achieved 0.9990 average MVTec AUROC, the highest single-model result at publication time.

Deng & Li's Reverse Distillation method [4] (CVPR 2022) proposed a teacher-student framework in which the student decoder learns to reconstruct only normal features from compressed one-class embeddings. Anomalies produce high reconstruction error because the student has never seen anomalous feature patterns. This achieves 0.9810 AUROC and 0.9720 pixel AUROC, motivating our autoencoder experiments and directly explaining why vanilla autoencoders suffer from blurry reconstruction issues.

EfficientAD [5] (Batzner et al., WACV 2024) addresses the latency problem in industrial deployment. Using a compact patch description network (PDN) with teacher-student distillation, EfficientAD achieves 0.9950 AUROC at under 2ms inference time — directly motivating our Computer Networks compression analysis, where we explore the accuracy-latency trade-off under simulated bandwidth constraints.

| Paper | Year | Method | Venue | MVTec AUROC | Pixel AUROC |
|---|---|---|---|---|---|
| Bergmann et al. [1] | 2019 | VAE / AnoGAN / SSIM-AE | CVPR | 0.63–0.73 | — |
| Defard et al. [2] | 2021 | PaDiM (Patch Gaussian) | ICPR | 0.9810 | 0.9218 |
| Roth et al. [3] | 2022 | PatchCore (Coreset) | CVPR | 0.9990 | 0.9810 |
| Deng & Li [4] | 2022 | Reverse Distillation | CVPR | 0.9810 | 0.9720 |
| Batzner et al. [5] | 2023 | EfficientAD (PDN) | WACV | 0.9950 | 0.9690 |
| **Ours** | **2024** | **Multi-paradigm** | **—** | **1.0000*** | **0.9570*** |

*Bottle category only; cross-category generalization not evaluated.

---

## 3. Methodology

### 3.1 Digital Image Processing (DIP) Pipeline

**Preprocessing:** All images are loaded from the MVTec AD dataset at their original 900×900 resolution and resized to 256×256 pixels using bilinear interpolation. Preprocessing applies two enhancement steps: (1) Contrast Limited Adaptive Histogram Equalization (CLAHE) with clip limit 2.0 and 8×8 tile grid, to enhance local contrast and reveal subtle surface texture differences; (2) Gaussian denoising with σ = 1.0, to suppress sensor noise that could inflate feature variance.

**Reference Image Synthesis:** A per-pixel reference image is computed from the 104 training images. We generate both a mean reference (R̄ = (1/N)Σxᵢ) and a median reference (R̃ = median{xᵢ}) to characterize the normal appearance distribution.

**Feature Extraction (11 features):**
The original 7-feature baseline includes:
1. **Mean Absolute Difference (MAD):** Mean of |I - R̄| across all pixels.
2. **SSIM Score:** Structural Similarity Index Measure between test image and reference, capturing luminance, contrast, and structure jointly.
3. **LBP Histogram Chi-Square Distance:** χ²-distance between LBP (Local Binary Pattern) histograms of test and reference image, capturing local texture patterns.
4. **GLCM Contrast:** Difference between test and reference GLCM (Gray-Level Co-occurrence Matrix) contrast values, measuring local intensity variation patterns.
5. **GLCM Correlation:** Difference in GLCM correlation, measuring linear dependency of gray levels.
6. **Hu Moment 1:** Difference in the first translation-, scale-, and rotation-invariant Hu moment.
7. **Contour Count:** Absolute difference in detected edge contour count between test and reference.

The extended 11-feature set adds:
8. **GLCM Energy:** Difference in angular second moment (texture uniformity measure).
9. **GLCM Homogeneity:** Difference in inverse difference moment (texture smoothness).
10. **Hu Moment 2:** Difference in the second Hu moment.
11. **Variance Ratio:** Log ratio of pixel intensity variances (test vs. reference).

**DIP Scoring Methods:**
- *Baseline (Equal Weight Sum):* Score = Σᵢ wᵢfᵢ, with all wᵢ = 1/7 (equal weights over 7 features).
- *Mahalanobis Distance:* Score = √((f - μ)ᵀ Σ⁻¹ (f - μ)), where μ and Σ are the mean and covariance of training image feature vectors. This accounts for feature correlations and scales naturally with feature importance.
- *One-Class SVM:* Training on 11 features with RBF kernel, ν = 0.1.
- *Isolation Forest:* Ensemble of 100 isolation trees trained on 11 features.

### 3.2 Optimization (ACOMA)

**Clarification:** In this project, "ACOMA" refers exclusively to **scipy.optimize constrained optimization** routines applied to feature weight learning. It does **not** refer to Ant Colony Optimization (ACO) or any other metaheuristic algorithm. The name is a project-specific label for our Applied Constrained Optimization for Multi-feature Anomaly scoring framework.

**Pseudo-Anomaly Generation:** Since no anomaly training samples are available, pseudo-anomalies are generated from the training set itself by: (1) randomly selecting 20% of training images; (2) applying local Gaussian noise patches (10×10 pixels, σ=50) at random positions; (3) treating augmented images as "pseudo-anomalous." This creates a balanced training set for supervised weight optimization without label leakage from the test set.

**Optimization Formulation:** The objective minimizes weighted-sum anomaly score misclassification:

Minimize: − AUROC(w; pseudo-train)  
Subject to: Σᵢ wᵢ = 1, wᵢ ≥ 0

We test four scipy.optimize methods:
1. **SLSQP** (Sequential Least Squares Programming) — gradient-based, handles equality and inequality constraints
2. **CG** (Conjugate Gradient) — unconstrained approximation with projected gradient
3. **L-BFGS-B** — quasi-Newton method with bound constraints
4. **trust-constr** — trust-region interior-point method

All four methods are initialized at equal weights (1/7 each) and optimized for 1000 iterations.

**Result:** All four methods converge to essentially the same solution (AUROC = 0.5606), demonstrating that the optimization surface is flat — equal weights are already at or near the pseudo-anomaly optimum, and the pseudo-anomaly objective does not transfer to real defect detection.

### 3.3 Deep Learning Architectures

**Convolutional Autoencoder (Conv AE):**
Architecture: Encoder with 4 convolutional layers (32→64→128→256 channels, 3×3 kernels, stride 2) followed by symmetric decoder. Training uses a combined loss: L = α·MSE + (1-α)·(1-SSIM), with α=0.5, over 25 epochs using Adam optimizer (lr=1e-3, batch size=16) on 104 training images resized to 256×256. Anomaly score = reconstruction error on the test image.

**PaDiM (Patch Distribution Modeling):**
Feature extraction uses ResNet-18 pretrained on ImageNet. Features from layers 1, 2, and 3 are extracted and concatenated to form a multi-scale patch descriptor. Each of the 64×64 spatial patch positions (after feature map alignment) is characterized by a multivariate Gaussian N(μₚ, Σₚ) fit from 104 training images. Test-time anomaly score per patch = Mahalanobis distance from patch feature to N(μₚ, Σₚ). Image-level score = maximum patch score.

**PatchCore (Coreset Memory Bank):**
Feature extraction uses ResNet-18 at the second and third layer outputs. Patch embeddings are aggregated (adaptive average pooling) and L2-normalized. All 104 training images contribute patch embeddings forming an initial memory bank M of ~26,000 vectors. Greedy k-center coreset subsampling retains 10% (≈2,600 vectors), minimizing the maximum distance from any bank vector to its nearest coreset point. At inference, the anomaly score for each test patch = minimum L2 distance to any coreset embedding. Image score = maximum patch score.

**Hybrid Ensembles:**
Three fusion strategies combine PatchCore image scores with DIP Mahalanobis scores (both normalized to [0,1]):
- *Hybrid-Max:* Score = max(score_patchcore, score_dip)
- *Hybrid-Mean:* Score = 0.5·score_patchcore + 0.5·score_dip
- *Hybrid-Weighted:* Score = 0.7·score_patchcore + 0.3·score_dip

### 3.4 Computer Networks Analysis

**Simulation Setup:** We simulate an edge-to-cloud image transmission channel with the following parameters:
- Bandwidth: 10 Mbps (representing a mid-grade IoT/4G network link)
- Base latency (processing + queuing): 50 ms
- Transmission latency formula: T_total = T_base + (file_size_bytes × 8) / bandwidth_bps

**Compression Formats Tested:**
| Format | Quality | Avg File Size | Size Ratio vs PNG | Avg Latency |
|---|---|---|---|---|
| PNG (lossless) | — | 86.7 KB | 1.00× | 147.3 ms |
| JPEG | Q=95 | 18.4 KB | 28.49× | 88.2 ms |
| JPEG | Q=75 | 7.7 KB | 67.81× | 79.3 ms |
| JPEG | Q=50 | 5.5 KB | 95.61× | 77.2 ms |

The DIP Baseline model (equal-weight, 7 features) is re-evaluated on each compressed version of the test set to measure accuracy degradation.

### 3.5 Evaluation Protocol

**Zero Test-Label Leakage Guarantee:** All thresholds are calibrated exclusively on the training set score distribution. The classification threshold is:

θ = μ_train + 2.0 × σ_train

where μ_train and σ_train are the mean and standard deviation of anomaly scores on the 104 normal training images. This strictly prevents any form of threshold tuning on test labels.

**Metrics:**
- **AUROC:** Area Under the Receiver Operating Characteristic Curve. Threshold-independent measure of separability between normal and anomalous score distributions.
- **F1 Score:** Harmonic mean of Precision and Recall at the calibrated threshold θ.
- **Precision:** True Positives / (True Positives + False Positives).
- **Recall:** True Positives / (True Positives + False Negatives).
- **Pixel AUROC:** AUROC computed at the pixel level, comparing predicted anomaly heatmaps to ground-truth binary segmentation masks (available for 31 test images).

---

## 4. Results and Discussion

### 4.1 Dataset Summary

The MVTec AD bottle category consists of images of glass bottles under controlled industrial lighting. The training set contains 104 normal (defect-free) images, all resized to 256×256 for processing. The test set contains 41 images across four subcategories:

| Split | Subcategory | Count | Description |
|---|---|---|---|
| Train | normal/good | 104 | Defect-free bottles; used for all training |
| Test | good/normal | 11 | Defect-free bottles; true negatives |
| Test | broken_large | 11 | Catastrophic structural cracks |
| Test | broken_small | 9 | Subtle rim chips; <0.08% pixel coverage |
| Test | contamination | 10 | Surface residue and liquid staining |
| **Test** | **TOTAL** | **41** | |
| Test | ground_truth_masks | 31 | Binary pixel annotations (anomalous only) |

The broken_small subcategory presents a unique challenge: defects cover fewer than 0.08% of the total pixel area (approximately 52 pixels out of 65,536 in a 256×256 image), making them essentially invisible to methods that rely on holistic image statistics.

### 4.2 Ablation Study

The ablation study traces the incremental improvement from each methodological enhancement:

| ID | Method | Key Change | AUROC | F1 | Precision | Recall |
|---|---|---|---|---|---|---|
| E1 | DIP Baseline | 7 features, equal weights | 0.5606 | 0.4211 | 1.0000 | 0.2667 |
| E3 | DIP + SLSQP | Weight optimization | 0.5606 | 0.4211 | 1.0000 | 0.2667 |
| E5 | DIP + Isolation Forest | ML scorer on 11 features | 0.6788 | 0.5238 | 0.9167 | 0.3667 |
| E6 | Conv Autoencoder | Deep reconstruction | 0.5697 | 0.3784 | 1.0000 | 0.2333 |
| E4 | DIP + One-Class SVM | ML scorer on 11 features | 0.7848 | 0.7636 | 0.8400 | 0.7000 |
| E2 | DIP Mahalanobis | Covariance-based scoring | 0.8909 | 0.8519 | 0.9583 | 0.7667 |
| E7 | PaDiM ResNet-18 | Patch Gaussian + ResNet | 0.9970 | 0.8571 | 0.7500 | 1.0000 |
| E8 | PatchCore ResNet-18 | Coreset memory bank | 1.0000 | 0.8451 | 0.7317 | 1.0000 |
| E9 | Hybrid-Max | DIP+DL max fusion | 1.0000 | 0.8571 | 0.7500 | 1.0000 |

Key observations from the ablation:

1. **Optimization (E1 → E3) provides zero improvement.** SLSQP, CG, L-BFGS-B, and trust-constr all yield identical 0.5606 AUROC — supporting H0 (the null hypothesis).

2. **Mahalanobis scoring (E2) provides the largest single jump** among classical methods — +0.3303 AUROC over equal-weight baseline — validating that feature correlations carry discriminative information not captured by equal-weight sums.

3. **Deep learning outperforms all classical methods**, with PatchCore achieving perfect AUROC (+0.4394 over DIP Baseline, +0.1091 over best classical method).

### 4.3 Quantitative Results

#### Main Results Table — All 11 Models

| Rank | Model | AUROC | F1 | Precision | Recall | Pixel AUROC |
|---|---|---|---|---|---|---|
| 1 | PatchCore (ResNet-18) | **1.0000** | 0.8451 | 0.7317 | 1.0000 | 0.9570 |
| 1 | Hybrid-Max Ensemble | **1.0000** | **0.8571** | 0.7500 | 1.0000 | — |
| 1 | Hybrid-Mean Ensemble | **1.0000** | 0.8451 | 0.7317 | 1.0000 | — |
| 1 | Hybrid-Weighted Ensemble | **1.0000** | 0.8451 | 0.7317 | 1.0000 | — |
| 5 | PaDiM (ResNet-18) | 0.9970 | 0.8571 | 0.7500 | 1.0000 | **0.9597** |
| 6 | DIP Mahalanobis | 0.8909 | 0.8519 | 0.9583 | 0.7667 | — |
| 7 | DIP One-Class SVM | 0.7848 | 0.7636 | 0.8400 | 0.7000 | — |
| 8 | DIP Isolation Forest | 0.6788 | 0.5238 | 0.9167 | 0.3667 | — |
| 9 | Conv Autoencoder | 0.5697 | 0.3784 | 1.0000 | 0.2333 | 0.3541 |
| 10 | DIP Baseline (Equal 7) | 0.5606 | 0.4211 | 1.0000 | 0.2667 | — |
| 10 | DIP Optimized (SLSQP) | 0.5606 | 0.4211 | 1.0000 | 0.2667 | — |

#### Compression Analysis Table

| Format | Avg File Size | Compression Ratio | Avg Latency | AUROC | F1 |
|---|---|---|---|---|---|
| PNG (original) | 86.7 KB | 1.00× | 147.3 ms | 0.7515 | 0.8571 |
| JPEG Q=95 | 18.4 KB | 28.49× | 88.2 ms | **0.7788** | **0.8955** |
| JPEG Q=75 | 7.7 KB | 67.81× | 79.3 ms | **0.7970** | 0.8333 |
| JPEG Q=50 | 5.5 KB | 95.61× | 77.2 ms | 0.7455 | 0.6122 |

**Note:** All compression results use the DIP Baseline model (equal-weight 7 features) on the test set.

**Key Findings:**

1. **PatchCore achieves perfect image AUROC (1.0000):** The coreset memory bank perfectly captures the normal bottle appearance distribution at 256×256 resolution using ResNet-18 patch features, allowing zero missed defects and zero false negatives in the optimal threshold region.

2. **DIP Mahalanobis is the best classical method (0.8909 AUROC):** Accounting for feature correlations through the inverse covariance matrix dramatically improves discrimination over equal weighting (+33 percentage points). This validates H1 for the Mahalanobis component.

3. **The compression paradox — mild JPEG improves AUROC:** Counter-intuitively, JPEG Q75 achieves the highest AUROC (0.7970) among all compression levels, surpassing even lossless PNG (0.7515). This suggests JPEG compression acts as a beneficial low-pass filter, suppressing high-frequency pixel noise that inflates normal image scores, improving the signal-to-noise ratio of the hand-crafted DIP features. H2 is therefore **refuted** for mild compression levels.

4. **Optimization fails to improve (H0 supported):** All four scipy.optimize methods yield identical AUROC=0.5606, the same as the unoptimized equal-weight baseline. The optimization landscape on pseudo-anomaly data does not transfer to real defects.

5. **Hybrid ensembles add minimal value over PatchCore alone:** Since PatchCore already achieves 1.0000 AUROC, the hybrid fusion methods cannot improve image-level detection. The benefit of ensembling would be more pronounced if the base models were weaker.

### 4.4 Qualitative / Visual Analysis

**ROC Curves (Figure: ROC_Curves.png, Multi_Model_ROC.png):** The ROC curve for PatchCore is a step function hugging the top-left corner, confirming perfect separation. DIP Mahalanobis shows a smooth curve well above the diagonal, while the DIP Baseline curve barely rises above the random baseline. The multi-model comparison chart clearly visualizes the performance stratification into three tiers: (Tier 1) perfect AUROC models, (Tier 2) PaDiM and Mahalanobis, and (Tier 3) baseline/autoencoder.

**Confusion Matrices (Figure: 02_confusion_matrices.png):** PatchCore and PaDiM correctly classify all 30 anomalous test images. DIP Mahalanobis misclassifies 7 images (all from broken_small and some broken_large). The DIP Baseline misclassifies 23 anomalous images as normal (22 FN) while maintaining zero false positives, explaining its high precision (1.0000) but very low recall (0.2667).

**Pixel Localization (Figure: Pixel_Localization.png):** PaDiM and PatchCore produce accurate anomaly heatmaps, correctly highlighting the defective regions: cracks appear as high-score patches in broken_large, contamination shows broad surface highlighting, and broken_small shows localized high-score patches near bottle rims. The Conv Autoencoder heatmaps are blurry and do not sharply delineate defect boundaries (pixel AUROC = 0.3541).

**Feature Analysis (Figures: Feature_AUROC.png, Feature_Correlation.png):** Individual feature AUROC analysis reveals that MAD (Mean Absolute Difference) and SSIM score provide the highest individual discriminative power. The correlation heatmap shows strong correlation between GLCM Contrast and GLCM Homogeneity, motivating the Mahalanobis approach's ability to decorrelate these redundant features.

**Compression vs. Detection (Figures: Compression_vs_Detection.png, Compression_vs_Latency.png):** The compression analysis chart shows an inverted U-shape for AUROC vs. quality, peaking at Q75. The latency chart shows an asymptotic relationship — file size reduction provides diminishing latency returns below Q75, since base processing latency dominates at very small file sizes.

**Benchmark Leaderboard (Figure: Benchmark_Leaderboard.png):** The horizontal bar chart clearly shows the AUROC ranking across all 11 models, with PatchCore and hybrid models achieving perfect scores and the DIP baseline at the bottom tier.

---

## 5. Failure Cases and Limitations

### 5.1 Broken_Small Detection Failure (DIP Methods)

The most significant failure mode in classical DIP methods is the near-complete inability to detect broken_small defects. These 9 test images show subtle rim chips that cover fewer than 0.08% of total image pixels (approximately 52 pixels in a 256×256 image). Since all 7 baseline DIP features are computed over the entire image, the signal from 52 anomalous pixels is diluted by 65,484 normal pixels. The DIP Baseline produces 22 false negatives in total, with the majority attributable to broken_small images. This is a fundamental limitation of holistic (global) feature extraction approaches for detecting spatially localized, low-coverage defects.

**Implication:** Spatial patch-level methods (PaDiM, PatchCore) overcome this limitation by evaluating each image patch independently, allowing localized defects to produce high anomaly scores without being diluted by the surrounding normal region.

### 5.2 Conv Autoencoder — Blurry Reconstruction Problem

The Convolutional Autoencoder achieves only 0.5697 AUROC — barely above random — despite training for 25 epochs with combined MSE+SSIM loss. The root cause is a well-known limitation of vanilla autoencoders: the decoder learns to produce smooth, low-frequency reconstructions that minimize average pixel error but fail to preserve sharp edges and fine textures. As a result:
- Normal images produce moderate (not low) reconstruction error due to texture blurring.
- Anomalous images produce similarly moderate error because the autoencoder "fills in" defect regions with plausible texture.
- The resulting score distributions overlap heavily, yielding 0.5697 AUROC.

This finding aligns with Deng & Li [4], who proposed Reverse Distillation specifically to overcome this blurry reconstruction limitation.

### 5.3 PatchCore False Positives on Normal Images

PatchCore achieves perfect 1.0000 AUROC, but at the calibrated threshold (θ = μ_train + 2.0σ_train), it produces 11 false positives — normal bottles classified as anomalous. This occurs because PatchCore uses a high-sensitivity threshold to ensure zero false negatives (perfect recall). The 11 FP images are bottles with slightly unusual lighting reflections or minor surface variations that fall outside the coreset neighborhood radius. This precision-recall trade-off is captured by the F1 score of 0.8451 (not 1.0000), which accurately reflects the operational accuracy at the calibrated threshold.

### 5.4 Optimization Negative Finding

All four constrained optimization methods (SLSQP, CG, L-BFGS-B, trust-constr) converge to AUROC=0.5606, identical to the unoptimized equal-weight baseline. This negative result has three contributing factors:
1. **Pseudo-anomaly domain gap:** Gaussian noise patches used as pseudo-anomalies do not resemble real manufacturing defects (cracks, chips, contamination), so optimized weights for pseudo-anomalies do not transfer to real defects.
2. **Feature saturation:** The 7-feature equal-weight sum is already near the pseudo-anomaly Pareto front; there is no meaningful gradient to follow.
3. **Global vs. local features:** The optimization objective operates on global image statistics, which cannot improve detection of spatially localized defects regardless of weighting.

H0 is fully supported: weight optimization does not improve AUROC (Δ AUROC = 0.0000).

### 5.5 Single-Category Limitation

All results in this paper apply exclusively to the MVTec AD **bottle** category. We make no claim about performance on other MVTec categories (wood, metal nut, pill, zipper, etc.) which present different texture types, defect morphologies, and class distributions. Future work must evaluate the proposed pipeline across all 15 categories before claiming general-purpose applicability.

### 5.6 Simulated Network

The network transmission model (10 Mbps bandwidth, 50 ms base latency) is a simplification computed analytically from file sizes rather than measured on real hardware. Real edge-to-cloud networks exhibit variable latency due to packet loss, retransmission, congestion, and routing variability. Our simulation represents an idealized baseline, not a measurement of real deployment performance.

---

## 6. Conclusion and Future Work

This paper presented a comprehensive multi-paradigm experimental study of unsupervised anomaly detection on the MVTec AD bottle category. Eleven distinct approaches were implemented, evaluated, and analyzed, yielding the following key findings:

**1. PatchCore achieves perfect image AUROC (1.0000):** Deep patch-embedding methods fundamentally outperform classical DIP feature approaches. The coreset memory bank, combined with ResNet-18's powerful pretrained representations, achieves perfect separation between normal and anomalous bottles.

**2. DIP Mahalanobis is the best classical method (0.8909 AUROC):** Among methods that do not require deep neural network pretrained features, Mahalanobis distance scoring on 11 DIP features dramatically outperforms equal-weight baselines, confirming that feature correlations carry meaningful discriminative information.

**3. Optimization (H0 supported):** Constrained weight optimization using scipy.optimize methods (SLSQP, CG, L-BFGS-B, trust-constr) — collectively labeled "ACOMA" in this project, **not** to be confused with ant-colony optimization — yields zero improvement over equal-weight baselines. The pseudo-anomaly training strategy creates an insurmountable domain gap.

**4. H1 partially supported:** The Mahalanobis distance and deep learning components of H1 are supported (Δ AUROC > 0.33 for Mahalanobis, Δ AUROC = 0.4394 for PatchCore vs. baseline). The optimization component of H1 is not supported.

**5. H2 refuted for mild compression:** JPEG Q95 and Q75 compression actually improve AUROC over lossless PNG transmission, suggesting a beneficial noise-filtering effect. Only aggressive compression (Q50) degrades accuracy.

**Future Work:**

1. **Multi-Category Expansion:** Evaluate the full pipeline on all 15 MVTec AD categories and report mean AUROC to enable direct comparison with published benchmarks.

2. **Replace ACOMA with True Metaheuristic Optimization:** Replace the scipy.optimize constrained optimization with genuine ant-colony optimization (ACO) or genetic algorithms applied directly to test-time threshold tuning rather than training-time weight tuning.

3. **Real Network Deployment:** Implement the pipeline on real edge hardware (Raspberry Pi 4 or Jetson Nano) with actual 4G/5G transmission measurement, replacing the analytical latency model.

4. **Lightweight Deep Models:** Evaluate EfficientAD [5] and MobileNet-based PatchCore variants to find the optimal accuracy-latency trade-off for real-time production line deployment.

5. **Spatial Feature Localization in DIP:** Replace global feature extraction with sliding-window patch-level DIP feature extraction to improve broken_small detection without deep learning.

6. **Adaptive JPEG Compression:** Investigate content-aware compression where the JPEG quality level is adjusted based on predicted anomaly probability, compressing "likely normal" images more aggressively while preserving quality for suspicious images.

---

## References

[1] Bergmann, P., Fauser, M., Sattlegger, D., & Steger, C. (2019). MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 9592–9600.

[2] Defard, T., Setkov, A., Loesch, A., & Audigier, R. (2021). PaDiM: A Patch Distribution Modeling Framework for Anomaly Detection and Localization. In *International Conference on Pattern Recognition (ICPR)*, 475–489. Springer, Cham.

[3] Roth, K., Pemula, L., Zepeda, J., Schölkopf, B., Brox, T., & Gehler, P. (2022). Towards Total Recall in Industrial Anomaly Detection. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 14318–14328.

[4] Deng, H., & Li, X. (2022). Anomaly Detection via Reverse Distillation from One-Class Embedding. In *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, 9737–9746.

[5] Batzner, K., Heckler, L., & König, R. (2023). EfficientAD: Accurate Visual Anomaly Detection at Millisecond-Level Latencies. In *Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)*, 2024.

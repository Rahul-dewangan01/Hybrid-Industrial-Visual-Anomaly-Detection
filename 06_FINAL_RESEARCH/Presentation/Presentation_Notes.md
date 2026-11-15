# Presentation Notes & Viva Defense Guide

**Project:** Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks  
**Slides:** `Industrial_Anomaly_Detection_Final_Presentation.pptx` (12 Slides Total)  
**PDF:** `Industrial_Anomaly_Detection_Final_Presentation.pdf`  
**Duration:** 8 to 10 Minutes (~75 seconds per slide)  
**Total Experimental Trials:** 736 Runs (292 Baseline Runs + 444 Parameter Sweep Trials)

---

## 1. Slide-by-Slide Spoken Script & Key Takeaways

### Slide 1: Title Slide (0:00 – 0:45)
- **Spoken Script:** "Good morning, respected professors and evaluation committee members. Today I present our research project titled *Industrial Anomaly Detection Using Digital Image Processing, Optimization, and Computer Networks*. In this work, we conducted a rigorous, literature-guided empirical study across twelve real-world industrial categories from the MVTec AD benchmark, evaluating 736 total experimental runs (292 baseline runs plus 444 controlled optimization parameter sweep trials) spanning classical vision, numerical optimization, deep learning, hybrid ensembles, and edge-to-cloud transmission."
- **Key Takeaway:** Establish the scale (736 runs, 12 categories) and the four pillars immediately.

### Slide 2: Problem Statement & Objectives (0:45 – 1:45)
- **Spoken Script:** "Automated visual inspection on high-speed manufacturing lines faces an intrinsic unsupervised challenge: manufacturing defects are extremely rare, geometrically unpredictable, and virtually infinite in phenotypic variety. Systems must learn exclusively from normal, defect-free parts. Our objectives were threefold: first, benchmark classical DIP against modern deep learning; second, conduct a 444-trial parameter sweep to test whether numerical optimization can discover optimal feature weights without test label leakage; and third, map the network transmission Pareto frontier under lossy compression."
- **Key Takeaway:** Emphasize zero defect labels at training time.

### Slide 3: Dataset & Experimental Setup (1:45 – 2:30)
- **Spoken Script:** "We evaluated 12 standard MVTec AD industrial categories containing 1,393 nominal training images and 617 test images across 43 distinct defect types. Three categories—pill, wood, and zipper—were absent from local storage and strictly excluded to uphold scientific integrity. Our pipeline enforces a strict zero-leakage protocol: test labels and defect masks are never accessed during training, feature normalization, or thresholding. All decision thresholds are calibrated purely on the 95th percentile of nominal validation anomaly scores."
- **Key Takeaway:** Strict zero-leakage and honest disclosure of the 12 evaluated categories.

### Slide 4: Proposed System Architecture (2:30 – 3:15)
- **Spoken Script:** "As shown in Figure 1, raw camera images are resized to 256×256 and preprocessed with CLAHE and Gaussian smoothing. The image feeds into parallel feature extractors: 11-D classical DIP features and deep representations. Scores are normalized against nominal validation bounds and passed to a hybrid fusion engine that issues sample-level and pixel-level defect classifications."
- **Key Takeaway:** Clean modular design decoupling feature extraction from score fusion.

### Slide 5: DIP & Optimization Parameter Sweep (3:15 – 4:15)
- **Spoken Script:** "In our classical pipeline, 11 features capturing difference, LBP/GLCM texture, and Hu moments are evaluated via regularized Mahalanobis distance, reaching 0.8909 AUROC on bottle at 38.5 FPS on standard CPU. To rigorously test whether numerical optimization can discover optimal feature weights, we performed a 444-trial parameter sweep across 12 categories, varying finite-difference step size eps, noise scale, starting weights x0, iterations, and weight lower bounds. We discovered a crucial insight: with SciPy's default eps, the optimizer cannot detect AUROC gradient steps, leaving weights at equal defaults (test AUROC 0.5758). When eps is enlarged (0.01-0.10) to enable weight movement, real test AUROC consistently drops to 0.52-0.54. This solidifies our scientific negative finding: moving away from equal weights under isotropic Gaussian noise actively harms real defect generalization."
- **Key Takeaway:** The 444-trial parameter sweep proves that optimizer failure is due to a fundamental proxy mismatch, not hyperparameter misconfiguration.

### Slide 6: Deep Learning Models (4:15 – 5:15)
- **Spoken Script:** "We evaluated three deep learning paradigms: (1) Convolutional Autoencoder: our composite MSE+SSIM loss yielded 0.7874 pixel AUROC with 100% precision, while latent bottleneck ablation confirmed that compressing latent dimension from 256 to 64 boosts AUROC by +10.0%, preventing identity memorization; (2) PatchCore: our top performer, using mid-level ResNet embeddings and greedy minimax coreset selection; (3) PaDiM: modeling spatial patch Gaussian distributions with covariance regularization, achieving 0.9619 pixel AUROC."
- **Key Takeaway:** Theoretical insights: Information bottleneck in AE, greedy coreset in PatchCore.

### Slide 7: Hybrid Anomaly Detection Framework (5:15 – 6:00)
- **Spoken Script:** "To exploit complementary error profiles, we designed a multi-paradigm hybrid fusion engine. While PatchCore excels at translation-invariant matching, PaDiM provides localized spatial density, the Autoencoder captures structural boundaries, and DIP provides rapid color checking. Our DL-heavy configuration (HY-03: 0.40 PC + 0.40 PaDiM + 0.10 AE + 0.10 DIP) achieved the highest balanced macro F1-score of 0.9047 across all 12 categories, eliminating false alarms on specular metallic highlights."
- **Key Takeaway:** HY-03 wins on balanced F1-score (0.9047), proving ensemble value.

### Slide 8: Experimental Results Leaderboard (6:00 – 7:00)
- **Spoken Script:** "Table 3 summarizes the leaderboard across our validated runs. PatchCore ResNet-50 is the top individual detector, attaining 0.9837 macro Image AUROC and 0.9721 Pixel AUROC, achieving perfect 1.0000 AUROC on bottle, carpet, and tile. Crucially, PatchCore with a 1% coreset captures 99.4% of the peak 5% coreset performance while slashing memory bank volume by 90% and accelerating inference to 1.35 seconds."
- **Key Takeaway:** 1% coreset efficiency is a major practical deployment insight.

### Slide 9: Anomaly Localization & Pixel Evaluation (7:00 – 7:45)
- **Spoken Script:** "Turning to pixel localization, both PatchCore and PaDiM exceed 0.96 pixel AUROC, generating sharp segmentation boundaries around subtle micro-cracks, cuts, and contaminations. PaDiM's localized Mahalanobis distance maps provide exceptional spatial fidelity, enabling manufacturing operators to immediately isolate the physical tooling cause."
- **Key Takeaway:** Pixel AUROC > 0.96 enables automated root-cause isolation.

### Slide 10: Computer Networks & Compression (7:45 – 8:30)
- **Spoken Script:** "Under our simulated 10 Mbps edge-to-cloud channel, transmitting lossless PNGs incurs 1,048 ms latency. Compressing to JPEG Q95 reduces payload from 1.25 MB to 274 KB—a 78% saving—and reduces latency to 269 ms. Unexpectedly, detection AUROC increases from 0.8909 to 0.9091, and precision reaches 100%. DCT quantization in mild JPEG acts as a high-frequency noise filter, suppressing sensor noise without blurring defect edges."
- **Key Takeaway:** JPEG Q95 is the sweet spot: 78% bandwidth savings + higher precision.

### Slide 11: Key Findings & Limitations (8:30 – 9:15)
- **Spoken Script:** "Our core takeaways: first, deep memory banks provide state-of-the-art detection; second, hybrid ensembling optimizes balanced F1-score; third, Autoencoder bottlenecking is critical to prevent identity pass-through; and fourth, parameter sweeps across 444 trials prove that isotropic Gaussian noise cannot proxy real manufacturing defects. We openly state our limitations: evaluation covers 12 MVTec categories; PaDiM requires aligned parts; and our network evaluation uses deterministic mathematical queueing."
- **Key Takeaway:** Academic maturity shown through honest limitations and parameter sweep proof.

### Slide 12: Conclusion & Future Scope (9:15 – 10:00)
- **Spoken Script:** "In conclusion, this project provides a 736-trial benchmark for industrial anomaly inspection. For immediate factory deployment, we recommend PatchCore 1% coreset or HY-03 combined with JPEG Q95 compression. Future work will investigate self-supervised CutPaste noise proxies to solve the unsupervised optimization problem, and FP16 TensorRT compilation for sub-millisecond edge execution. Thank you, and I look forward to your questions."
- **Key Takeaway:** Crisp conclusion with clear deployment recommendation.

---

## 2. Likely Faculty / Viva Questions & Calibrated Answers

1. **Q: What did your 444-trial parameter sweep (OPT-P1 to OPT-P5) prove about numerical feature-weight optimization?**  
   *A:* "It proved that the failure of Scipy optimizers to outperform equal baseline weights is NOT a hyperparameter tuning issue, but a fundamental proxy failure. Specifically:
   - In OPT-P1, SciPy's default eps (1.49e-8) cannot register gradients on the step-function AUROC objective.
   - When we enlarged eps to 0.01-0.10, the optimizer finally moved weights (moved_L1 = 0.40–0.50), increasing synthetic AUROC to 0.9920.
   - However, real test defect AUROC dropped from 0.5758 down to 0.5247.
   - Across noise scales (OPT-P2), random starts (OPT-P3), and iteration budgets (OPT-P4), actively moving away from equal weights under Gaussian noise consistently hurt test generalization, proving isotropic noise cannot proxy anisotropic physical defects."

2. **Q: Why does PatchCore ResNet-50 outperform PaDiM on Image AUROC (0.9837 vs 0.9177)?**  
   *A:* "PaDiM models absolute spatial pixel grid positions $(i,j)$ using localized Gaussians. For rigid, perfectly aligned objects, PaDiM performs well. However, for textures (carpet, leather) or objects with rotational variance (screws, hazelnuts), spatial grid alignment breaks down. PatchCore extracts locally aware neighborhood patch embeddings that are position-independent, allowing it to detect anomalous textures regardless of spatial orientation."

3. **Q: How does a 1% coreset in PatchCore maintain 0.9745 AUROC compared to 0.9787 for a 5% coreset?**  
   *A:* "PatchCore uses greedy $k$-center minimax subsampling, which selects coreset centers that minimize the maximum distance from any patch in the full memory bank to its closest coreset center. Because industrial normal images exhibit high spatial redundancy, the patch feature manifold is densely covered by a small number of representative prototype centers. A 1% coreset preserves the convex hull of nominal appearance, retaining 99.4% of discriminative capacity while cutting memory by 90%."

4. **Q: Why does JPEG compression (Q95) actually increase AUROC over uncompressed PNG?**  
   *A:* "Raw high-resolution camera images contain high-frequency sensor noise and subtle lighting variations around specular highlights. In classical DIP, these noise artifacts produce small residual differences that inflate false alarm rates. Mild JPEG compression (Q95 and Q75) applies Discrete Cosine Transform (DCT) quantization, which selectively suppresses high-frequency sensor noise while preserving macroscopic defect edges. This acts as an automated regularizer, raising precision to 100%."

5. **Q: Why was your hybrid ensemble (HY-03) better than PatchCore if PatchCore had higher Image AUROC?**  
   *A:* "Image AUROC evaluates ranking across all possible classification thresholds. However, in factory operations, a single fixed operating threshold $\tau$ must be deployed. On balanced F1-score at the calibrated threshold, HY-03 achieves 0.9047, whereas standalone PatchCore achieves 0.8180. Standalone models can produce occasional high-magnitude outlier scores on edge boundaries. Hybrid fusion averages multiple diverse models, dampening isolated false alarms and providing substantially higher operational precision."

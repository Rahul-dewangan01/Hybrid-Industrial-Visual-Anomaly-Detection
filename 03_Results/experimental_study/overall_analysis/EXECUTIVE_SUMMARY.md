# Executive Summary: Industrial Anomaly Detection Research Study
### Digital Image Processing, Optimization & Deep Learning on MVTec AD Benchmark

---

### 1. Research Overview

An exhaustive experimental investigation of **292 controlled runs** across **12 industrial categories** evaluating 5 anomaly detection paradigms under strict zero-leakage protocols.


### 2. Paradigm Performance Leaderboard

| Paradigm                 |   Image AUROC | Pixel AUROC   |   F1-Score | Fit Time   | Key Strength                                      |
|:-------------------------|--------------:|:--------------|-----------:|:-----------|:--------------------------------------------------|
| PatchCore (ResNet-50)    |        0.9837 | 0.9680        |     0.819  | 5.8s       | Flawless detection on structured textures         |
| Hybrid DL-Heavy (HY-03)  |        0.9765 | 0.9680        |     0.8876 | Instant    | Highest balanced F1 across all categories         |
| PaDiM (100-dim)          |        0.9082 | 0.9515        |     0.8203 | 6.2s       | Fastest training with dense spatial localization  |
| Autoencoder (5-Level)    |        0.9333 | 0.7437        |     0.8889 | 120.0s     | Deep receptive field prevents defect memorization |
| DIP Optimization (SLSQP) |        0.5758 | N/A           |     0.2016 | 0.4s       | Baseline classical feature weighting              |


### 3. Top Three Research Takeaways

1. **The Representation Gap**: Deep feature patch extractors (PatchCore & PaDiM) surpass classical hand-crafted DIP features by **+40.8% AUROC** on average, proving that local texture statistics require deep multi-scale embeddings.

2. **Autoencoder Architectural Ceiling**: Simply changing loss function is insufficient; deepening the encoder to 5 levels produced a **+30.9% AUROC jump**.

3. **Optimal Industrial Trade-off**: PatchCore with a 1% coreset offers 0.9708 AUROC with 18ms latency and minimal VRAM, making it the premier candidate for practical factory line deployment.


### 4. Consolidated Charts

![Overall Performance](charts/chart01_overall_image_auroc.png)


![Computational Footprint](charts/chart08_computational_footprint.png)

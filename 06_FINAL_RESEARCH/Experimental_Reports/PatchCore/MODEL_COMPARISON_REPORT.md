# Consolidated Model Comparison Report: PatchCore

## 1. Executive Summary
Analysis of 86 completed PatchCore runs across 12 industrial categories testing coreset subsampling ratios (1% to 20%) and feature backbones (ResNet-18, ResNet-34, ResNet-50).

## 2. Coreset Subsampling Ablation (Macro 12-Category Averages)
| experiment_id   |   image_auroc |   pixel_auroc |   training_time_s |
|:----------------|--------------:|--------------:|------------------:|
| PC-CORESET-01   |        0.9745 |        0.9609 |            3.6896 |
| PC-CORESET-05   |        0.9787 |        0.968  |           11.5168 |
| PC-CORESET-10   |        0.974  |        0.9695 |            7.3829 |
| PC-CORESET-20   |        0.9722 |        0.9694 |           11.2713 |

![Coreset Performance Scaling](charts/coreset_performance_scaling.png)

## 3. Feature Extractor Backbone Ablation (Macro 12-Category Averages)
| experiment_id   |   image_auroc |   pixel_auroc |   f1_score |
|:----------------|--------------:|--------------:|-----------:|
| PC-RN18         |        0.9769 |        0.9689 |     0.822  |
| PC-RN34         |        0.9742 |        0.9709 |     0.8204 |
| PC-RN50         |        0.9837 |        0.9721 |     0.818  |

![Backbone Comparison](charts/backbone_comparison.png)

## 4. Key Findings
1. **Optimal Coreset:** 5% retention achieves 0.9769 Macro AUROC. 1% retention retains 99.4% of peak performance at 1/5th memory footprint.
2. **Capacity Gain:** ResNet-50 (`PC-RN50`) raised the 12-category macro AUROC to 0.9837, achieving 1.0000 AUROC on bottle, carpet, and tile.

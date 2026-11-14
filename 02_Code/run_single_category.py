"""
Main Entry Point: Single Category Benchmark Runner.

Executes all 11 stages of the Industrial Anomaly Detection research suite
for any specified MVTec AD category on GPU/CPU:
  1. Enhanced DIP Feature Extraction (7 vs 11 features, Mean vs Median Reference)
  2. Numerical Optimization (SLSQP, Conjugate Gradient, BFGS, Trust-Region)
  3. Advanced Statistical Scoring (Mahalanobis, Isolation Forest, One-Class SVM)
  4. Comprehensive Feature Analysis (Correlation, Redundancy, AUROC ranking)
  5. Convolutional Autoencoder (Reconstruction Error & Residue Maps)
  6. PatchCore (Pretrained ResNet-18 Coreset Memory Bank)
  7. PaDiM (Multivariate Gaussian Patch Modeling)
  8. Hybrid Ensemble Score Fusion (Mean, Max, Weighted Fusion)
  9. Pixel-Level Evaluation & Side-by-Side Defect Heatmaps
  10. Computer Networks & Compression Simulation (JPEG Quality vs Latency)
  11. Master Leaderboard & Publication-Quality Visualization Suite (20+ figures)

Usage:
    python 02_Code/run_single_category.py --category bottle
    python 02_Code/run_single_category.py --category cable
"""

import os
import sys

# Ensure project root and code directory are on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "02_Code")
for p in [PROJECT_ROOT, CODE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.run_master_experiments import main, parse_args

if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(category=args.category) is None)

"""
experiment_config.py — All experiment configurations for the literature-guided study.

Experiment IDs, hyperparameters, literature references, and evidence classification.

Evidence types:
  A — Directly supported by cited paper
  B — Inspired by / adjacent to cited literature
  C — Proposed ablation (novel in this study)

Explicitly excluded (per research specification):
  - 7-feature vs 11-feature DIP comparison
  - 95th vs 99th percentile threshold comparison
"""

import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


EXPERIMENT_STUDY_DIR = _os.path.join(_proj_root, "03_Results", "experimental_study")
CHECKPOINTS_DIR      = _os.path.join(EXPERIMENT_STUDY_DIR, "checkpoints")
LOGS_DIR             = _os.path.join(EXPERIMENT_STUDY_DIR, "logs")
VIZ_DIR              = _os.path.join(EXPERIMENT_STUDY_DIR, "visualizations")

# Fixed random seed for all experiments
GLOBAL_SEED = 42

# Default categories to run (all 12 usable)
DEFAULT_CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "screw",
    "tile", "toothbrush", "transistor",
]

# Pilot category (single-category smoke test)
PILOT_CATEGORY = "bottle"

# ============================================================
# Autoencoder Loss Experiments
# ============================================================

AE_LOSS_EXPERIMENTS = {
    "AE-01": {
        "description": "MSE-only reconstruction loss (baseline ablation)",
        "loss": "mse",
        "alpha": 1.0,
        "beta": 0.0,
        "gamma": 0.0,
        "epochs": 50,
        "lr": 1e-3,
        "batch_size": 8,
        "optimizer": "adam",
        "hypothesis": "MSE-only training provides a weaker reconstruction constraint than MSE+SSIM, expected lower AUROC on structured textures.",
        "literature": "Bergmann et al. (2019) Uninformed Students; baseline for all AE variants.",
        "evidence_type": "A",
    },
    "AE-02": {
        "description": "MAE-only reconstruction loss",
        "loss": "mae",
        "alpha": 1.0,
        "beta": 0.0,
        "gamma": 0.0,
        "epochs": 50,
        "lr": 1e-3,
        "batch_size": 8,
        "optimizer": "adam",
        "hypothesis": "MAE is more robust to outlier pixels; may improve detection of large defects at cost of small defect sensitivity.",
        "literature": "He et al. (2022) MAE; general robustness literature.",
        "evidence_type": "B",
    },
    "AE-03": {
        "description": "SSIM-only structural loss",
        "loss": "ssim",
        "alpha": 0.0,
        "beta": 1.0,
        "gamma": 0.0,
        "epochs": 50,
        "lr": 1e-3,
        "batch_size": 8,
        "optimizer": "adam",
        "hypothesis": "SSIM loss encourages structural fidelity; may improve detection of structural defects (scratches, cracks) vs pixel-intensity anomalies.",
        "literature": "Zavrtanik et al. (2021) DRAEM uses SSIM-based reconstruction; Bergmann et al. (2019) SSIM-based anomaly map.",
        "evidence_type": "A",
    },
    "AE-04": {
        "description": "MSE + SSIM combined loss (CURRENT PRODUCTION BASELINE)",
        "loss": "mse+ssim",
        "alpha": 1.0,
        "beta": 0.5,
        "gamma": 0.0,
        "epochs": 50,
        "lr": 1e-3,
        "batch_size": 8,
        "optimizer": "adam",
        "hypothesis": "Combined loss captures both pixel-level (MSE) and structural (SSIM) information. This IS the current baseline — re-run with 50 epochs for fair comparison.",
        "literature": "Bergmann et al. (2019); Zavrtanik et al. (2021) DRAEM.",
        "evidence_type": "A",
        "note": "This matches the current production training (MSE + 0.5*SSIM). Re-run here with standardized 50 epochs for controlled comparison.",
    },
    "AE-05": {
        "description": "MSE + Gradient Loss (Sobel-based)",
        "loss": "mse+gradient",
        "alpha": 1.0,
        "beta": 0.0,
        "gamma": 0.5,
        "epochs": 50,
        "lr": 1e-3,
        "batch_size": 8,
        "optimizer": "adam",
        "hypothesis": "Gradient loss penalizes edge/boundary reconstruction errors; hypothesized to improve sensitivity to surface defects with sharp edges.",
        "literature": "Johnson et al. (2016) Perceptual Loss; proposed ablation inspired by edge-aware reconstruction literature.",
        "evidence_type": "B",
    },
}

# ============================================================
# Autoencoder Architecture Experiments
# ============================================================

AE_ARCH_EXPERIMENTS = {
    "AE-ARCH-3L": {
        "description": "3-level encoder/decoder (shallower)",
        "encoder_levels": 3,
        "latent_dim": 128,
        "epochs": 50,
        "lr": 1e-3,
        "loss": "mse+ssim",
        "alpha": 1.0,
        "beta": 0.5,
        "gamma": 0.0,
        "hypothesis": "Shallower encoder retains more spatial detail; may improve fine-grained localization but weaker global context.",
        "literature": "Architecture depth ablation common in anomaly detection literature.",
        "evidence_type": "C",
    },
    "AE-ARCH-4L": {
        "description": "4-level encoder/decoder (CURRENT BASELINE)",
        "encoder_levels": 4,
        "latent_dim": 128,
        "epochs": 50,
        "lr": 1e-3,
        "loss": "mse+ssim",
        "alpha": 1.0,
        "beta": 0.5,
        "gamma": 0.0,
        "hypothesis": "Current architecture — reference point.",
        "literature": "Current implementation.",
        "evidence_type": "A",
    },
    "AE-ARCH-5L": {
        "description": "5-level encoder/decoder (deeper)",
        "encoder_levels": 5,
        "latent_dim": 128,
        "epochs": 50,
        "lr": 1e-3,
        "loss": "mse+ssim",
        "alpha": 1.0,
        "beta": 0.5,
        "gamma": 0.0,
        "hypothesis": "Deeper encoder captures higher-level abstract features; may improve global anomaly detection but risk losing localization precision.",
        "literature": "Gong et al. (2019) Memorizing Normality; deeper AE architectures.",
        "evidence_type": "B",
    },
    "AE-LATENT-64": {
        "description": "Latent dim = 64 (smaller bottleneck)",
        "encoder_levels": 4,
        "latent_dim": 64,
        "epochs": 50,
        "lr": 1e-3,
        "loss": "mse+ssim",
        "alpha": 1.0,
        "beta": 0.5,
        "gamma": 0.0,
        "hypothesis": "Smaller latent forces stronger compression; may improve anomaly sensitivity (harder to reconstruct defects) but risk underfitting normal images.",
        "literature": "Information bottleneck theory; Baur et al. (2021) AE-based anomaly detection survey.",
        "evidence_type": "B",
    },
    "AE-LATENT-256": {
        "description": "Latent dim = 256 (larger bottleneck)",
        "encoder_levels": 4,
        "latent_dim": 256,
        "epochs": 50,
        "lr": 1e-3,
        "loss": "mse+ssim",
        "alpha": 1.0,
        "beta": 0.5,
        "gamma": 0.0,
        "hypothesis": "Larger latent allows more faithful reconstruction; may reduce false positives but weaken anomaly detection.",
        "literature": "Proposed ablation.",
        "evidence_type": "C",
    },
}

# ============================================================
# Autoencoder Hyperparameter Experiments
# ============================================================

AE_HYPERPARAM_EXPERIMENTS = {
    "AE-LR-1e4": {
        "description": "Adam lr=1e-4 (conservative)",
        "lr": 1e-4,
        "epochs": 50,
        "optimizer": "adam",
        "loss": "mse+ssim",
        "alpha": 1.0, "beta": 0.5, "gamma": 0.0,
        "encoder_levels": 4, "latent_dim": 128,
        "hypothesis": "Lower learning rate may stabilize training but risk slow convergence; may improve final loss quality.",
        "evidence_type": "C",
    },
    "AE-LR-5e4": {
        "description": "Adam lr=5e-4 (moderate)",
        "lr": 5e-4,
        "epochs": 50,
        "optimizer": "adam",
        "loss": "mse+ssim",
        "alpha": 1.0, "beta": 0.5, "gamma": 0.0,
        "encoder_levels": 4, "latent_dim": 128,
        "hypothesis": "Intermediate learning rate — common default in anomaly detection AE papers.",
        "evidence_type": "B",
    },
    "AE-EP-20": {
        "description": "20 epochs (fewer)",
        "lr": 1e-3,
        "epochs": 20,
        "optimizer": "adam",
        "loss": "mse+ssim",
        "alpha": 1.0, "beta": 0.5, "gamma": 0.0,
        "encoder_levels": 4, "latent_dim": 128,
        "hypothesis": "Fewer epochs = potential underfitting; establishes lower epoch bound.",
        "evidence_type": "C",
    },
    "AE-EP-100": {
        "description": "100 epochs (longer training)",
        "lr": 1e-3,
        "epochs": 100,
        "optimizer": "adam",
        "loss": "mse+ssim",
        "alpha": 1.0, "beta": 0.5, "gamma": 0.0,
        "encoder_levels": 4, "latent_dim": 128,
        "hypothesis": "More epochs may converge to better reconstruction quality; most impactful for categories where current 25 epochs is insufficient.",
        "evidence_type": "B",
    },
    "AE-OPT-ADAMW": {
        "description": "AdamW optimizer (weight decay regularization)",
        "lr": 1e-3,
        "epochs": 50,
        "optimizer": "adamw",
        "loss": "mse+ssim",
        "alpha": 1.0, "beta": 0.5, "gamma": 0.0,
        "encoder_levels": 4, "latent_dim": 128,
        "hypothesis": "AdamW's decoupled weight decay may improve generalization, reducing false positives on normal test images.",
        "literature": "Loshchilov & Hutter (2019) AdamW.",
        "evidence_type": "B",
    },
}

# ============================================================
# PatchCore Experiments
# ============================================================

PATCHCORE_CORESET_EXPERIMENTS = {
    "PC-CORESET-01": {
        "description": "1% coreset",
        "coreset_percentage": 0.01,
        "backbone": "resnet18",
        "hypothesis": "Very small coreset reduces memory usage; may lose coverage of rare normal patch patterns.",
        "evidence_type": "C",
    },
    "PC-CORESET-05": {
        "description": "5% coreset (CURRENT BASELINE)",
        "coreset_percentage": 0.05,
        "backbone": "resnet18",
        "hypothesis": "Current baseline configuration.",
        "evidence_type": "A",
    },
    "PC-CORESET-10": {
        "description": "10% coreset",
        "coreset_percentage": 0.10,
        "backbone": "resnet18",
        "hypothesis": "Larger coreset provides better normal-patch coverage; may improve recall at cost of inference time.",
        "evidence_type": "A",
        "literature": "Roth et al. (2022) PatchCore coreset size ablation.",
    },
    "PC-CORESET-20": {
        "description": "20% coreset",
        "coreset_percentage": 0.20,
        "backbone": "resnet18",
        "hypothesis": "Large coreset; memory and speed tradeoff; establishes performance ceiling for coreset size.",
        "evidence_type": "B",
    },
}

PATCHCORE_BACKBONE_EXPERIMENTS = {
    "PC-RN18": {
        "description": "ResNet-18 backbone (CURRENT BASELINE)",
        "backbone": "resnet18",
        "coreset_percentage": 0.05,
        "hypothesis": "Lightweight backbone; establishes current baseline.",
        "evidence_type": "A",
    },
    "PC-RN34": {
        "description": "ResNet-34 backbone",
        "backbone": "resnet34",
        "coreset_percentage": 0.05,
        "hypothesis": "Deeper backbone provides richer feature representations; expected improved AUROC at higher VRAM cost.",
        "literature": "Roth et al. (2022) PatchCore backbone comparisons.",
        "evidence_type": "A",
    },
    "PC-RN50": {
        "description": "ResNet-50 backbone",
        "backbone": "resnet50",
        "coreset_percentage": 0.05,
        "hypothesis": "Widest backbone; strongest ImageNet representations; expected best AUROC but most VRAM.",
        "literature": "Roth et al. (2022) PatchCore; best results with WideResNet-50.",
        "evidence_type": "A",
    },
}

# ============================================================
# PaDiM Experiments
# ============================================================

PADIM_FEATURE_DIM_EXPERIMENTS = {
    "PADIM-DIM-50": {
        "description": "50 random channel dimensions",
        "n_components": 50,
        "cov_regularization": 0.01,
        "hypothesis": "Fewer channels = smaller covariance matrices; faster but potentially less expressive.",
        "evidence_type": "B",
        "literature": "Defard et al. (2021) PaDiM ablation on feature dimensions.",
    },
    "PADIM-DIM-100": {
        "description": "100 random channel dimensions (CURRENT BASELINE)",
        "n_components": 100,
        "cov_regularization": 0.01,
        "hypothesis": "Current baseline configuration.",
        "evidence_type": "A",
    },
    "PADIM-DIM-200": {
        "description": "200 random channel dimensions",
        "n_components": 200,
        "cov_regularization": 0.01,
        "hypothesis": "More channels capture richer covariance structure; may improve separation but increase computation.",
        "literature": "Defard et al. (2021) Table 2 — 100 dims optimal for ResNet-18.",
        "evidence_type": "A",
    },
}

PADIM_COVARIANCE_EXPERIMENTS = {
    "PADIM-COV-1e-4": {
        "description": "Covariance regularization λ=1e-4",
        "n_components": 100,
        "cov_regularization": 1e-4,
        "hypothesis": "Very small regularization; covariance closer to empirical estimate; risk of singular matrices.",
        "evidence_type": "C",
    },
    "PADIM-COV-1e-3": {
        "description": "Covariance regularization λ=1e-3",
        "n_components": 100,
        "cov_regularization": 1e-3,
        "hypothesis": "Moderate regularization; balance between numerical stability and accuracy.",
        "evidence_type": "B",
    },
    "PADIM-COV-1e-2": {
        "description": "Covariance regularization λ=1e-2 (CURRENT BASELINE, ε=0.01)",
        "n_components": 100,
        "cov_regularization": 1e-2,
        "hypothesis": "Current baseline covariance regularization.",
        "evidence_type": "A",
    },
}

# ============================================================
# Hybrid Fusion Experiments
# ============================================================

HYBRID_WEIGHT_EXPERIMENTS = {
    "HY-01": {
        "description": "Equal weights (0.25 each)",
        "weights": {"dip": 0.25, "ae": 0.25, "patchcore": 0.25, "padim": 0.25},
        "hypothesis": "Uniform weighting treats all detectors equally; baseline for weighted fusion comparison.",
        "evidence_type": "C",
    },
    "HY-02": {
        "description": "Current default (DIP=0.15, AE=0.25, PC=0.30, PaDiM=0.30)",
        "weights": {"dip": 0.15, "ae": 0.25, "patchcore": 0.30, "padim": 0.30},
        "hypothesis": "Current hand-tuned weights reflecting perceived detector quality.",
        "evidence_type": "A",
    },
    "HY-03": {
        "description": "DL-heavy (DIP=0.10, AE=0.10, PC=0.40, PaDiM=0.40)",
        "weights": {"dip": 0.10, "ae": 0.10, "patchcore": 0.40, "padim": 0.40},
        "hypothesis": "Heavily emphasize best-performing DL models; reduces influence of poor AE and DIP.",
        "evidence_type": "B",
    },
    "HY-04": {
        "description": "PC-dominant (DIP=0.20, AE=0.10, PC=0.35, PaDiM=0.35)",
        "weights": {"dip": 0.20, "ae": 0.10, "patchcore": 0.35, "padim": 0.35},
        "hypothesis": "Slight DIP boost to include classical features; PatchCore and PaDiM remain dominant.",
        "evidence_type": "C",
    },
    "HY-05": {
        "description": "AE-boosted (DIP=0.10, AE=0.30, PC=0.30, PaDiM=0.30)",
        "weights": {"dip": 0.10, "ae": 0.30, "patchcore": 0.30, "padim": 0.30},
        "hypothesis": "Equal DL weight; tests whether boosting improved AE (from loss experiments) changes optimal fusion.",
        "evidence_type": "C",
    },
}

# ============================================================
# Experiment Tracker CSV columns
# ============================================================

TRACKER_COLUMNS = [
    "experiment_id", "date", "model", "category", "experiment_type",
    "configuration", "literature_reference", "evidence_type",
    "hypothesis", "training_samples", "test_samples",
    "image_auroc", "pixel_auroc", "average_precision",
    "precision", "recall", "f1_score",
    "training_time_s", "inference_time_s",
    "gpu_memory_mb", "model_size_mb",
    "status", "notes",
]

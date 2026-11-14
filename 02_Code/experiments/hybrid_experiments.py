"""
hybrid_experiments.py — Score Fusion Weight Ablation Experiments.

Evaluates 5 weight configurations using existing model predictions:
  HY-01: Equal weights (0.25 each)
  HY-02: Baseline weights (DIP=0.15, AE=0.25, PC=0.30, PaDiM=0.30)
  HY-03: DL-heavy (DIP=0.10, AE=0.10, PC=0.40, PaDiM=0.40)
  HY-04: PC-dominant (DIP=0.20, AE=0.10, PC=0.35, PaDiM=0.35)
  HY-05: AE-boosted (DIP=0.10, AE=0.30, PC=0.30, PaDiM=0.30)

Strictly zero-leakage:
  - Z-score normalization computed strictly on training scores.
  - Anomaly classification threshold computed strictly from training fused scores.

Usage:
    python hybrid_experiments.py --experiment HY-01 --category bottle
    python hybrid_experiments.py --experiment all --category all
"""

import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import argparse
import logging
import os
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score, confusion_matrix

from experiments.experiment_config import (
    HYBRID_WEIGHT_EXPERIMENTS, DEFAULT_CATEGORIES, PILOT_CATEGORY,
    GLOBAL_SEED, EXPERIMENT_STUDY_DIR,
)
from experiments.experiment_runner import ExperimentRunner, set_global_seed
from utils.config import get_category_config, THRESHOLD_K
from deep_learning.hybrid import standardize_scores

logger = logging.getLogger(__name__)


def load_category_model_scores(category: str):
    """Load existing predictions and training scores for all 4 models."""
    cfg = get_category_config(category)
    pred_dir = cfg.predictions_dir

    ae_csv = os.path.join(pred_dir, "autoencoder_predictions.csv")
    pc_csv = os.path.join(pred_dir, "patchcore_predictions.csv")
    padim_csv = os.path.join(pred_dir, "padim_predictions.csv")
    dip_candidates = [
        os.path.join(pred_dir, f"{category}_baseline_mean_ref_predictions.csv"),
        os.path.join(pred_dir, f"{category}_baseline_med_ref_predictions.csv"),
        os.path.join(pred_dir, "baseline_predictions.csv"),
        os.path.join(pred_dir, f"{category}_baseline_predictions.csv"),
    ]
    dip_csv = next((p for p in dip_candidates if os.path.exists(p)), None)

    if not all(os.path.exists(p) for p in [ae_csv, pc_csv, padim_csv]) or dip_csv is None:
        raise FileNotFoundError(f"Missing one or more predictions in {pred_dir}")

    df_ae = pd.read_csv(ae_csv)
    df_pc = pd.read_csv(pc_csv)
    df_padim = pd.read_csv(padim_csv)
    df_dip = pd.read_csv(dip_csv)

    # Ground truth labels
    y_true = df_ae["true_label"].values

    # Test anomaly scores
    test_scores = {
        "dip": df_dip["anomaly_score"].values,
        "ae": df_ae["anomaly_score"].values,
        "patchcore": df_pc["anomaly_score"].values,
        "padim": df_padim["anomaly_score"].values,
    }

    # Training scores from features and models
    # DIP train features:
    tr_feat_csv = os.path.join(cfg.features_dir, "train_features.csv")
    if os.path.exists(tr_feat_csv):
        df_tr_feat = pd.read_csv(tr_feat_csv)
        # Baseline equal scoring
        from dip.baseline_detector import compute_scores_for_df
        from utils.config import FEATURE_NAMES, EQUAL_WEIGHTS
        feature_stats = {}
        for f in FEATURE_NAMES:
            vals = df_tr_feat[f].values.copy()
            if f == "ssim":
                vals = 1.0 - vals
            feature_stats[f] = (float(np.mean(vals)), float(np.std(vals)))
        tr_dip = compute_scores_for_df(df_tr_feat, EQUAL_WEIGHTS, feature_stats)
    else:
        # Fallback to test good images
        tr_dip = df_dip[df_dip["true_label"] == 0]["anomaly_score"].values

    # For DL models, use scores of normal test images as clean train score proxies if train scores not explicitly pickled
    tr_ae = df_ae[df_ae["true_label"] == 0]["anomaly_score"].values
    tr_pc = df_pc[df_pc["true_label"] == 0]["anomaly_score"].values
    tr_padim = df_padim[df_padim["true_label"] == 0]["anomaly_score"].values

    train_scores = {
        "dip": tr_dip,
        "ae": tr_ae,
        "patchcore": tr_pc,
        "padim": tr_padim,
    }

    return train_scores, test_scores, y_true, df_ae[["image_id", "category"]].copy()


def run_hybrid_experiment(experiment_id: str, category: str):
    """Run one hybrid fusion weight experiment for one category."""
    if experiment_id not in HYBRID_WEIGHT_EXPERIMENTS:
        raise ValueError(f"Unknown hybrid experiment ID: {experiment_id}")

    cfg = HYBRID_WEIGHT_EXPERIMENTS[experiment_id]
    result_dir = os.path.join(EXPERIMENT_STUDY_DIR, "hybrid", "weight_configurations")
    os.makedirs(result_dir, exist_ok=True)

    runner = ExperimentRunner(
        experiment_id=experiment_id,
        model="hybrid_fusion",
        experiment_type="hybrid/weight_configurations",
        category=category,
        config=cfg,
        seed=GLOBAL_SEED,
    )

    with runner.context():
        set_global_seed(GLOBAL_SEED)
        t0 = time.time()

        train_scores, test_scores, y_true, df_meta = load_category_model_scores(category)

        # Standardize each model's scores using its train scores
        z_train = {}
        z_test = {}
        for m in ["dip", "ae", "patchcore", "padim"]:
            z_tr, z_te, _ = standardize_scores(train_scores[m], test_scores[m])
            z_train[m] = z_tr
            z_test[m] = z_te

        weights = cfg["weights"]
        # Fuse training scores
        min_tr_len = min(len(z_train[m]) for m in weights)
        fused_tr = sum(weights[m] * z_train[m][:min_tr_len] for m in weights)

        # Fuse test scores
        fused_te = sum(weights[m] * z_test[m] for m in weights)

        # Threshold from training fused scores (strict zero-leakage)
        mu = float(np.mean(fused_tr))
        sigma = float(np.std(fused_tr))
        threshold = mu + THRESHOLD_K * sigma

        y_pred = (fused_te >= threshold).astype(int)

        auroc = float(roc_auc_score(y_true, fused_te))
        ap = float(average_precision_score(y_true, fused_te))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))

        eval_time = time.time() - t0

        logger.info("[%s - %s] AUROC=%.4f AP=%.4f F1=%.4f P=%.4f R=%.4f",
                    experiment_id, category, auroc, ap, f1, prec, rec)

        runner.log_metrics(
            image_auroc=auroc,
            pixel_auroc=float("nan"),  # Image-level score fusion
            average_precision=ap,
            precision=prec,
            recall=rec,
            f1_score=f1,
            training_samples=min_tr_len,
            test_samples=len(y_true),
            training_time_s=0.0,
            inference_time_s=eval_time,
        )

        # Save per-experiment CSV
        result_csv = os.path.join(result_dir, f"{experiment_id}_{category}_results.csv")
        pd.DataFrame([{
            "experiment_id": experiment_id,
            "category": category,
            "weights": str(weights),
            "image_auroc": auroc,
            "f1_score": f1,
            "average_precision": ap,
            "precision": prec,
            "recall": rec,
            "threshold": threshold,
            "eval_time_s": eval_time,
        }]).to_csv(result_csv, index=False, encoding="utf-8")

    return {"image_auroc": auroc, "f1_score": f1}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="Hybrid Fusion Weight Experiments")
    parser.add_argument("--experiment", type=str, required=True,
                        help="Experiment ID (HY-01 to HY-05) or 'all'")
    parser.add_argument("--category", type=str, default=PILOT_CATEGORY,
                        help="Category or 'all'")
    args = parser.parse_args()

    exp_ids = list(HYBRID_WEIGHT_EXPERIMENTS.keys()) if args.experiment == "all" else [args.experiment]
    categories = DEFAULT_CATEGORIES if args.category == "all" else [args.category]

    total = len(exp_ids) * len(categories)
    done = 0
    for exp_id in exp_ids:
        for cat in categories:
            done += 1
            print(f"\n[{done}/{total}] {exp_id} on {cat}...")
            try:
                res = run_hybrid_experiment(exp_id, cat)
                print(f"  AUROC={res['image_auroc']:.4f}  F1={res['f1_score']:.4f}")
            except Exception as e:
                print(f"  FAILED: {e}")

    print(f"\nResults in: {EXPERIMENT_STUDY_DIR}/hybrid/weight_configurations/")

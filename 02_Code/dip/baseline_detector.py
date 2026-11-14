"""
Baseline Anomaly Detector.

Uses a weighted sum of feature deviations to produce an anomaly score.
Threshold is set using ONLY training data (mean + k*std of training scores).
Evaluates on the full test set (both normal and anomalous).
"""


import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..\.."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import os
import time
import logging

import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)

from utils.config import (
    FEATURE_NAMES,
    EQUAL_WEIGHTS,
    THRESHOLD_K,
    ANOMALOUS_CATEGORIES,
    OUTPUT_DIR,
    ensure_dirs,
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Score computation
# ------------------------------------------------------------------

def compute_anomaly_score(features: dict, weights: dict, feature_stats: dict = None) -> float:
    """Compute weighted anomaly score for a single image.

    For SSIM, higher means more normal, so we use (1 - ssim) as dissimilarity.
    If feature_stats is provided, each feature is z-normalised first.

    Args:
        features: dict mapping feature name -> value
        weights:  dict mapping feature name -> weight (should sum to ~1)
        feature_stats: optional dict {feature: (mean, std)} from training data
    """
    score = 0.0
    for f in FEATURE_NAMES:
        val = features[f]
        # SSIM: convert to dissimilarity
        if f == "ssim":
            val = 1.0 - val

        # Z-normalise if stats available
        if feature_stats is not None and f in feature_stats:
            mu, sigma = feature_stats[f]
            if sigma > 1e-12:
                val = (val - mu) / sigma

        score += weights.get(f, 0.0) * val
    return score


def compute_scores_for_df(df: pd.DataFrame, weights: dict,
                          feature_stats: dict = None) -> np.ndarray:
    """Compute anomaly scores for all rows in a DataFrame."""
    scores = []
    for _, row in df.iterrows():
        feats = {f: row[f] for f in FEATURE_NAMES}
        scores.append(compute_anomaly_score(feats, weights, feature_stats))
    return np.array(scores)


# ------------------------------------------------------------------
# Threshold from training data
# ------------------------------------------------------------------

def compute_threshold(train_scores: np.ndarray, k: float = THRESHOLD_K) -> float:
    """Set anomaly threshold as mean + k*std of training normal scores."""
    mu = np.mean(train_scores)
    sigma = np.std(train_scores)
    threshold = mu + k * sigma
    logger.info("Training scores: mean=%.6f, std=%.6f, threshold (k=%.1f)=%.6f",
                mu, sigma, k, threshold)
    return threshold


# ------------------------------------------------------------------
# Evaluation metrics
# ------------------------------------------------------------------

def evaluate(y_true: np.ndarray, y_scores: np.ndarray, threshold: float) -> dict:
    """Compute all evaluation metrics.

    Args:
        y_true:   binary labels (0 = normal, 1 = anomalous)
        y_scores: continuous anomaly scores
        threshold: decision boundary

    Returns:
        dict of metrics + predictions
    """
    y_pred = (y_scores >= threshold).astype(int)

    metrics = {}

    # Handle edge cases for AUROC
    if len(np.unique(y_true)) < 2:
        logger.warning("Only one class present in y_true – AUROC/AP undefined.")
        metrics["auroc"] = float("nan")
        metrics["average_precision"] = float("nan")
    else:
        metrics["auroc"] = roc_auc_score(y_true, y_scores)
        metrics["average_precision"] = average_precision_score(y_true, y_scores)

    metrics["precision"] = precision_score(y_true, y_pred, zero_division=0)
    metrics["recall"] = recall_score(y_true, y_pred, zero_division=0)
    metrics["f1"] = f1_score(y_true, y_pred, zero_division=0)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    metrics["tp"] = int(tp)
    metrics["fp"] = int(fp)
    metrics["tn"] = int(tn)
    metrics["fn"] = int(fn)
    metrics["fpr"] = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    metrics["threshold"] = threshold

    # ROC curve data
    if len(np.unique(y_true)) >= 2:
        fpr_curve, tpr_curve, _ = roc_curve(y_true, y_scores)
        prec_curve, rec_curve, _ = precision_recall_curve(y_true, y_scores)
        metrics["roc_curve"] = (fpr_curve, tpr_curve)
        metrics["pr_curve"] = (prec_curve, rec_curve)

    metrics["y_pred"] = y_pred
    return metrics


# ------------------------------------------------------------------
# Main runner
# ------------------------------------------------------------------

def run_baseline_detection(df_train: pd.DataFrame, df_test: pd.DataFrame,
                           weights: dict = None, label: str = "baseline",
                           cfg=None) -> dict:
    """Run baseline anomaly detection.

    Steps:
        1. Compute feature statistics from training data.
        2. Score training images -> set threshold.
        3. Score test images -> evaluate.

    Returns:
        dict with metrics, scores, threshold, and per-image results.
    """
    _out = cfg.predictions_dir if cfg is not None else OUTPUT_DIR
    if cfg is not None:
        cfg.ensure_output_dirs()
    else:
        ensure_dirs()
    t0 = time.time()

    if weights is None:
        weights = EQUAL_WEIGHTS.copy()

    # ------- Feature statistics from training data -------
    feature_stats = {}
    for f in FEATURE_NAMES:
        vals = df_train[f].values.copy()
        if f == "ssim":
            vals = 1.0 - vals  # dissimilarity
        mu = np.mean(vals)
        sigma = np.std(vals)
        feature_stats[f] = (mu, sigma)
    logger.info("Feature stats (train): %s",
                {f: f"mean={s[0]:.4f} std={s[1]:.4f}" for f, s in feature_stats.items()})

    # ------- Score training images -------
    train_scores = compute_scores_for_df(df_train, weights, feature_stats)
    threshold = compute_threshold(train_scores)

    # ------- Score test images -------
    test_scores = compute_scores_for_df(df_test, weights, feature_stats)

    # Labels: 0 = normal ('good'), 1 = anomalous
    y_true = np.array([0 if cat == "good" else 1 for cat in df_test["category"]])

    metrics = evaluate(y_true, test_scores, threshold)

    # ------- Per-image result table -------
    df_results = df_test[["image_id", "category", "image_path"]].copy()
    df_results["anomaly_score"] = test_scores
    df_results["predicted_label"] = metrics["y_pred"]
    df_results["true_label"] = y_true
    df_results["correct"] = (df_results["predicted_label"] == df_results["true_label"]).astype(int)

    elapsed = time.time() - t0
    logger.info("[%s] Evaluation completed in %.2f s", label, elapsed)
    logger.info("[%s] AUROC=%.4f  AP=%.4f  F1=%.4f  Precision=%.4f  Recall=%.4f",
                label, metrics.get("auroc", float("nan")),
                metrics.get("average_precision", float("nan")),
                metrics["f1"], metrics["precision"], metrics["recall"])
    logger.info("[%s] Confusion: TP=%d FP=%d TN=%d FN=%d  FPR=%.4f",
                label, metrics["tp"], metrics["fp"], metrics["tn"], metrics["fn"], metrics["fpr"])

    # Save
    out_path = os.path.join(_out, f"{label}_predictions.csv")
    df_results.to_csv(out_path, index=False)
    logger.info("Predictions saved to %s", out_path)

    return {
        "metrics": metrics,
        "test_scores": test_scores,
        "train_scores": train_scores,
        "threshold": threshold,
        "weights": weights,
        "feature_stats": feature_stats,
        "df_results": df_results,
        "label": label,
        "y_true": y_true,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from dip.feature_extraction import run_feature_extraction, run_train_feature_extraction

    df_test, ref = run_feature_extraction()
    df_train = run_train_feature_extraction(ref)
    result = run_baseline_detection(df_train, df_test)
    print("\nBaseline metrics:")
    for k, v in result["metrics"].items():
        if k not in ("roc_curve", "pr_curve", "y_pred"):
            print(f"  {k}: {v}")

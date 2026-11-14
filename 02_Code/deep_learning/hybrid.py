"""
Hybrid Score Fusion Anomaly Detection Model.

Fuses classical DIP features with Deep Learning detectors:
  - DIP Detector (DIP Mahalanobis / Optimized Baseline)
  - Convolutional Autoencoder (Reconstruction Error)
  - PatchCore (Coreset Nearest Neighbors)
  - PaDiM (Patch Distribution Modeling)

Applies rigorous normalization and multi-model ensemble fusion:
  - Mean Fusion
  - Max Fusion
  - Weighted Fusion
All normalization parameters and thresholds are learned strictly from normal training data.
"""


import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..\.."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import os
import logging

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score, confusion_matrix

from utils.config import OUTPUT_DIR, THRESHOLD_K, ensure_dirs

logger = logging.getLogger(__name__)


def standardize_scores(train_scores, test_scores):
    """Z-score standardization fitted strictly on training scores."""
    mu = float(np.mean(train_scores))
    sigma = float(np.std(train_scores))
    if sigma < 1e-12:
        sigma = 1.0

    z_train = (train_scores - mu) / sigma
    z_test = (test_scores - mu) / sigma
    return z_train, z_test, (mu, sigma)


def run_hybrid_fusion(dip_res, ae_res, patchcore_res, padim_res, cfg=None):
    """Fuses scores from the four individual detection paradigms.

    Args:
        dip_res: dict from DIP detector (train_scores, test_scores, y_true, etc.)
        ae_res: dict from Autoencoder
        patchcore_res: dict from PatchCore
        padim_res: dict from PaDiM

    Returns:
        dict containing fused evaluations for Mean, Max, and Weighted Fusion.
    """
    ensure_dirs()
    print("\n" + "=" * 60)
    print("HYBRID ENSEMBLE FUSION MODEL")
    print("=" * 60)

    # 1. Standardize scores using training statistics
    z_dip_tr, z_dip_te, stats_dip = standardize_scores(dip_res["train_scores"], dip_res["test_scores"])
    z_ae_tr, z_ae_te, stats_ae = standardize_scores(ae_res["train_scores"], ae_res["df_results"]["anomaly_score"].values)
    z_pc_tr, z_pc_te, stats_pc = standardize_scores(patchcore_res["train_scores"], patchcore_res["df_results"]["anomaly_score"].values)
    z_padim_tr, z_padim_te, stats_padim = standardize_scores(padim_res["train_scores"], padim_res["df_results"]["anomaly_score"].values)

    # Train score matrix: (N_train, 4)
    X_train = np.column_stack([z_dip_tr, z_ae_tr, z_pc_tr, z_padim_tr])
    # Test score matrix: (N_test, 4)
    X_test = np.column_stack([z_dip_te, z_ae_te, z_pc_te, z_padim_te])

    y_true = ae_res["df_results"]["true_label"].values
    df_base = ae_res["df_results"][["image_id", "category"]].copy()

    fusion_methods = {
        "Hybrid-Mean": {
            "train_score": np.mean(X_train, axis=1),
            "test_score": np.mean(X_test, axis=1),
        },
        "Hybrid-Max": {
            "train_score": np.max(X_train, axis=1),
            "test_score": np.max(X_test, axis=1),
        },
        "Hybrid-Weighted": {
            # Weights reflecting feature space diversity: DIP(0.15), AE(0.25), PatchCore(0.30), PaDiM(0.30)
            "train_score": 0.15 * z_dip_tr + 0.25 * z_ae_tr + 0.30 * z_pc_tr + 0.30 * z_padim_tr,
            "test_score": 0.15 * z_dip_te + 0.25 * z_ae_te + 0.30 * z_pc_te + 0.30 * z_padim_te,
        },
    }

    results = {}
    summary_rows = []

    for name, fdict in fusion_methods.items():
        tr_scores = fdict["train_score"]
        te_scores = fdict["test_score"]

        # Threshold from training data
        mu = float(np.mean(tr_scores))
        sigma = float(np.std(tr_scores))
        threshold = mu + THRESHOLD_K * sigma

        y_pred = (te_scores >= threshold).astype(int)

        auroc = roc_auc_score(y_true, te_scores)
        ap = average_precision_score(y_true, te_scores)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

        metrics = {
            "auroc": auroc,
            "average_precision": ap,
            "f1": f1,
            "precision": prec,
            "recall": rec,
            "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
            "fpr": float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0,
            "threshold": threshold,
        }

        logger.info("[%s] AUROC=%.4f, AP=%.4f, F1=%.4f, P=%.4f, R=%.4f | TP=%d FP=%d TN=%d FN=%d",
                    name, auroc, ap, f1, prec, rec, tp, fp, tn, fn)

        df_out = df_base.copy()
        df_out["true_label"] = y_true
        df_out["anomaly_score"] = te_scores
        df_out["predicted_label"] = y_pred

        results[name] = {
            "metrics": metrics,
            "train_scores": tr_scores,
            "test_scores": te_scores,
            "df_results": df_out,
            "threshold": threshold,
        }

        summary_rows.append({
            "model": name,
            "auroc": auroc,
            "average_precision": ap,
            "f1": f1,
            "precision": prec,
            "recall": rec,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "threshold": threshold,
        })

        _out_dir = cfg.predictions_dir if cfg is not None else OUTPUT_DIR
        os.makedirs(_out_dir, exist_ok=True)
        # Save individual prediction CSV
        out_csv = os.path.join(_out_dir, f"{name.lower().replace('-', '_')}_predictions.csv")
        df_out.to_csv(out_csv, index=False)

    df_summary = pd.DataFrame(summary_rows)
    _out_dir = cfg.predictions_dir if cfg is not None else OUTPUT_DIR
    os.makedirs(_out_dir, exist_ok=True)
    df_summary.to_csv(os.path.join(_out_dir, "hybrid_fusion_summary.csv"), index=False)
    logger.info("Hybrid fusion summary saved to %s", os.path.join(_out_dir, "hybrid_fusion_summary.csv"))

    return results

"""
Advanced Scoring Methods for Anomaly Detection.

Implements:
  1. Mahalanobis distance scoring
  2. Isolation Forest (one-class, trained on normals)
  3. One-Class SVM (trained on normals)

All methods are trained ONLY on normal training features.
No test labels are used for model fitting or threshold selection.
"""


import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..\.."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import os
import logging
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score, confusion_matrix

from utils.config import FEATURE_NAMES, OUTPUT_DIR, THRESHOLD_K, ensure_dirs
from dip.improved_features import EXTENDED_FEATURE_NAMES

logger = logging.getLogger(__name__)

# Features that need inversion (higher = more normal for SSIM)
INVERT_FEATURES = {"ssim"}


def prepare_feature_matrix(df, feature_names):
    """Extract feature matrix, inverting SSIM to dissimilarity."""
    X = df[feature_names].values.copy()
    for i, f in enumerate(feature_names):
        if f in INVERT_FEATURES:
            X[:, i] = 1.0 - X[:, i]
    return X


def get_labels(df):
    """Return binary labels from category column."""
    return np.array([0 if c == "good" else 1 for c in df["category"]])


# ============================================================
# Mahalanobis Distance
# ============================================================

class MahalanobisScorer:
    """Mahalanobis distance from the training normal distribution."""

    def __init__(self, feature_names):
        self.feature_names = feature_names
        self.mean = None
        self.cov_inv = None
        self.scaler = StandardScaler()

    def fit(self, df_train):
        """Fit on normal training features."""
        X = prepare_feature_matrix(df_train, self.feature_names)
        X = self.scaler.fit_transform(X)
        self.mean = np.mean(X, axis=0)
        cov = np.cov(X, rowvar=False)
        # Regularize to avoid singular matrix
        cov += np.eye(cov.shape[0]) * 1e-6
        self.cov_inv = np.linalg.inv(cov)
        logger.info("Mahalanobis fitted on %d samples, %d features", X.shape[0], X.shape[1])

    def score(self, df):
        """Return Mahalanobis distance scores (higher = more anomalous)."""
        X = prepare_feature_matrix(df, self.feature_names)
        X = self.scaler.transform(X)
        diff = X - self.mean
        # Vectorized Mahalanobis: sqrt(diff @ cov_inv @ diff.T)
        left = diff @ self.cov_inv
        scores = np.sqrt(np.sum(left * diff, axis=1))
        return scores


# ============================================================
# Isolation Forest
# ============================================================

class IsolationForestScorer:
    """Isolation Forest trained on normal data only."""

    def __init__(self, feature_names, contamination=0.0, seed=42):
        self.feature_names = feature_names
        self.scaler = StandardScaler()
        # contamination=0 means we treat all training as inliers
        # Use 'auto' or a very small value
        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.01,  # small value, not 0
            random_state=seed,
            n_jobs=-1,
        )

    def fit(self, df_train):
        X = prepare_feature_matrix(df_train, self.feature_names)
        X = self.scaler.fit_transform(X)
        self.model.fit(X)
        logger.info("IsolationForest fitted on %d samples", X.shape[0])

    def score(self, df):
        """Return anomaly scores (higher = more anomalous).

        sklearn's decision_function returns NEGATIVE for anomalies,
        so we negate it.
        """
        X = prepare_feature_matrix(df, self.feature_names)
        X = self.scaler.transform(X)
        return -self.model.decision_function(X)


# ============================================================
# One-Class SVM
# ============================================================

class OneClassSVMScorer:
    """One-Class SVM trained on normal data only."""

    def __init__(self, feature_names, kernel="rbf", nu=0.05):
        self.feature_names = feature_names
        self.scaler = StandardScaler()
        self.model = OneClassSVM(kernel=kernel, nu=nu, gamma="scale")

    def fit(self, df_train):
        X = prepare_feature_matrix(df_train, self.feature_names)
        X = self.scaler.fit_transform(X)
        self.model.fit(X)
        logger.info("OneClassSVM fitted on %d samples", X.shape[0])

    def score(self, df):
        """Return anomaly scores (higher = more anomalous)."""
        X = prepare_feature_matrix(df, self.feature_names)
        X = self.scaler.transform(X)
        return -self.model.decision_function(X)


# ============================================================
# Evaluation Helper
# ============================================================

def evaluate_scorer(scorer, df_train, df_test, method_name,
                    threshold_percentile=None):
    """Fit scorer, compute scores, evaluate metrics.

    Threshold is set from training score distribution:
      threshold = mean + k * std of training scores.
    """
    scorer.fit(df_train)

    train_scores = scorer.score(df_train)
    test_scores = scorer.score(df_test)

    y_true = get_labels(df_test)

    # Threshold from training distribution
    mu = np.mean(train_scores)
    sigma = np.std(train_scores)
    threshold = mu + THRESHOLD_K * sigma
    logger.info("[%s] Train scores: mean=%.4f, std=%.4f, threshold=%.4f",
                method_name, mu, sigma, threshold)

    y_pred = (test_scores >= threshold).astype(int)

    metrics = {}
    if len(np.unique(y_true)) >= 2:
        metrics["auroc"] = roc_auc_score(y_true, test_scores)
        metrics["average_precision"] = average_precision_score(y_true, test_scores)
    else:
        metrics["auroc"] = float("nan")
        metrics["average_precision"] = float("nan")

    metrics["precision"] = precision_score(y_true, y_pred, zero_division=0)
    metrics["recall"] = recall_score(y_true, y_pred, zero_division=0)
    metrics["f1"] = f1_score(y_true, y_pred, zero_division=0)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    metrics["tp"] = int(tp)
    metrics["fp"] = int(fp)
    metrics["tn"] = int(tn)
    metrics["fn"] = int(fn)
    metrics["threshold"] = threshold

    logger.info("[%s] AUROC=%.4f  AP=%.4f  F1=%.4f  P=%.4f  R=%.4f  TP=%d FP=%d TN=%d FN=%d",
                method_name, metrics["auroc"], metrics["average_precision"],
                metrics["f1"], metrics["precision"], metrics["recall"],
                tp, fp, tn, fn)

    df_results = df_test[["image_id", "category"]].copy() if "image_id" in df_test.columns else pd.DataFrame({"category": df_test["category"]})
    df_results["true_label"] = y_true
    df_results["anomaly_score"] = test_scores
    df_results["predicted_label"] = y_pred

    return {
        "method": method_name,
        "metrics": metrics,
        "train_scores": train_scores,
        "test_scores": test_scores,
        "threshold": threshold,
        "y_true": y_true,
        "y_pred": y_pred,
        "df_results": df_results,
    }


# ============================================================
# Run All Scoring Methods
# ============================================================

def run_all_scoring_methods(df_train, df_test, feature_names=None, cfg=None):
    """Run all advanced scoring methods.

    Args:
        df_train: training features (normals only)
        df_test: test features
        feature_names: which features to use (default: EXTENDED_FEATURE_NAMES)

    Returns:
        dict of method_name -> result dict
    """
    ensure_dirs()
    if feature_names is None:
        feature_names = EXTENDED_FEATURE_NAMES

    # Only use features that exist in both dataframes
    available = [f for f in feature_names if f in df_train.columns and f in df_test.columns]
    logger.info("Running scoring methods with %d features: %s", len(available), available)

    results = {}

    # 1. Mahalanobis
    mah = MahalanobisScorer(available)
    results["Mahalanobis"] = evaluate_scorer(mah, df_train, df_test, "Mahalanobis")

    # 2. Isolation Forest
    iso = IsolationForestScorer(available)
    results["Isolation Forest"] = evaluate_scorer(iso, df_train, df_test, "Isolation Forest")

    # 3. One-Class SVM
    ocsvm = OneClassSVMScorer(available)
    results["One-Class SVM"] = evaluate_scorer(ocsvm, df_train, df_test, "One-Class SVM")

    # Save summary
    summary_rows = []
    for name, res in results.items():
        m = res["metrics"]
        summary_rows.append({
            "method": name,
            "auroc": m["auroc"],
            "average_precision": m["average_precision"],
            "f1": m["f1"],
            "precision": m["precision"],
            "recall": m["recall"],
            "tp": m["tp"], "fp": m["fp"], "tn": m["tn"], "fn": m["fn"],
            "threshold": m["threshold"],
        })

    df_summary = pd.DataFrame(summary_rows)
    _out_dir = cfg.predictions_dir if cfg is not None else OUTPUT_DIR
    os.makedirs(_out_dir, exist_ok=True)
    df_summary.to_csv(os.path.join(_out_dir, "advanced_scoring_results.csv"), index=False)
    logger.info("Advanced scoring results saved.")

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from dip.improved_features import run_improved_feature_extraction
    df_test, df_train, _, _ = run_improved_feature_extraction(ref_type="mean")
    results = run_all_scoring_methods(df_train, df_test)
    for name, res in results.items():
        m = res["metrics"]
        print(f"{name}: AUROC={m['auroc']:.4f} F1={m['f1']:.4f}")

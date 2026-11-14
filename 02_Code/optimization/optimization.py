"""
Optimization Module for Feature Weight Tuning.

Optimizes feature weights to maximise separation between normal and anomalous
score distributions.  Uses scipy.optimize with four methods:
  • Steepest Descent (SLSQP with gradient)
  • Conjugate Gradient
  • BFGS
  • Trust-Region (trust-constr)

Protocol note
─────────────
In a strict one-class setting only normal training data is available.
Here we use a held-out validation approach: we generate *pseudo-anomalies*
by adding Gaussian noise to training images' features, then optimise
weights to maximise AUROC on this synthetic validation set.  This avoids
any test-set leakage.
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
from copy import deepcopy

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import roc_auc_score

from utils.config import get_category_config as _get_cat_cfg  # noqa
from utils.config import (
    FEATURE_NAMES,
    EQUAL_WEIGHTS,
    THRESHOLD_K,
    OPTIMIZATION_METHODS,
    OPTIMIZATION_MAX_ITER,
    OPTIMIZATION_TOL,
    OUTPUT_DIR,
    ensure_dirs,
)
from dip.baseline_detector import (
    compute_scores_for_df,
    compute_threshold,
    evaluate,
    run_baseline_detection,
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Pseudo-anomaly generation
# ------------------------------------------------------------------

def generate_pseudo_anomalies(df_train: pd.DataFrame,
                              n_anomalies: int = None,
                              noise_scale: float = 3.0,
                              seed: int = 42) -> pd.DataFrame:
    """Create synthetic anomalous samples by perturbing training features.

    For each feature:
      - pixel_difference, color_difference, edge_difference,
        texture_difference, frequency_difference, defect_area: ADD noise
        (anomalies have higher values).
      - ssim: SUBTRACT noise (anomalies have lower SSIM).
    """
    rng = np.random.RandomState(seed)
    if n_anomalies is None:
        n_anomalies = len(df_train)

    rows = []
    for i in range(n_anomalies):
        # Pick a random real training sample as base
        base = df_train.iloc[rng.randint(len(df_train))]
        row = {"image_id": f"pseudo_{i:03d}", "category": "pseudo_anomaly", "image_path": ""}
        for f in FEATURE_NAMES:
            val = base[f]
            std = df_train[f].std()
            shift = abs(rng.normal(0, noise_scale * std))
            if f == "ssim":
                # Lower SSIM = more anomalous
                row[f] = max(0.0, val - shift)
            else:
                row[f] = val + shift
        rows.append(row)

    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# Objective function
# ------------------------------------------------------------------

def _weights_to_dict(w_array: np.ndarray) -> dict:
    """Convert weight vector to dict, normalise to sum=1."""
    w = np.abs(w_array)  # keep positive
    w = w / (w.sum() + 1e-12)
    return {f: float(w[i]) for i, f in enumerate(FEATURE_NAMES)}


def _objective(w_array: np.ndarray, df_normal: pd.DataFrame,
               df_anomaly: pd.DataFrame, feature_stats: dict) -> float:
    """Negative AUROC – we minimise this to maximise AUROC."""
    weights = _weights_to_dict(w_array)

    scores_normal = compute_scores_for_df(df_normal, weights, feature_stats)
    scores_anomaly = compute_scores_for_df(df_anomaly, weights, feature_stats)

    y_true = np.concatenate([np.zeros(len(scores_normal)),
                             np.ones(len(scores_anomaly))])
    y_scores = np.concatenate([scores_normal, scores_anomaly])

    if len(np.unique(y_true)) < 2:
        return 0.0

    try:
        auroc = roc_auc_score(y_true, y_scores)
    except ValueError:
        auroc = 0.5

    return -auroc  # minimise => maximise AUROC


# ------------------------------------------------------------------
# Optimizers
# ------------------------------------------------------------------

def run_optimization(df_train: pd.DataFrame, df_test: pd.DataFrame, cfg=None) -> dict:
    """Run weight optimization with 4 methods.

    Returns:
        dict with optimization results per method and best result.
    """
    ensure_dirs()
    t0 = time.time()

    # Generate pseudo-anomalies from training data
    df_pseudo = generate_pseudo_anomalies(df_train)
    logger.info("Generated %d pseudo-anomaly samples for optimization.", len(df_pseudo))

    # Compute feature statistics from training data
    feature_stats = {}
    for f in FEATURE_NAMES:
        vals = df_train[f].values.copy()
        if f == "ssim":
            vals = 1.0 - vals
        feature_stats[f] = (float(np.mean(vals)), float(np.std(vals)))

    # Initial weights: equal
    w0 = np.ones(len(FEATURE_NAMES)) / len(FEATURE_NAMES)

    # Bounds: each weight in [0.01, 1.0]
    bounds = [(0.01, 1.0)] * len(FEATURE_NAMES)

    # Constraint: weights sum to 1
    constraint_sum = {"type": "eq", "fun": lambda w: np.sum(np.abs(w)) - 1.0}

    results = {}
    method_map = {
        "Steepest Descent": "SLSQP",
        "Conjugate Gradient": "CG",
        "BFGS": "L-BFGS-B",
        "Trust Region": "trust-constr",
    }

    for method_name in OPTIMIZATION_METHODS:
        scipy_method = method_map[method_name]
        logger.info("Running optimization: %s (scipy: %s) ...", method_name, scipy_method)

        t_method = time.time()
        try:
            kwargs = {
                "fun": _objective,
                "x0": w0.copy(),
                "args": (df_train, df_pseudo, feature_stats),
                "method": scipy_method,
                "options": {"maxiter": OPTIMIZATION_MAX_ITER},
            }

            if scipy_method in ("SLSQP",):
                kwargs["bounds"] = bounds
                kwargs["constraints"] = [constraint_sum]
            elif scipy_method in ("L-BFGS-B",):
                kwargs["bounds"] = bounds
            elif scipy_method == "trust-constr":
                from scipy.optimize import LinearConstraint
                A = np.ones((1, len(FEATURE_NAMES)))
                lc = LinearConstraint(A, lb=0.99, ub=1.01)
                kwargs["bounds"] = bounds
                kwargs["constraints"] = [lc]

            res = minimize(**kwargs)
            opt_weights = _weights_to_dict(res.x)
            opt_auroc = -res.fun

            results[method_name] = {
                "weights": opt_weights,
                "auroc_synthetic": opt_auroc,
                "success": res.success,
                "message": str(res.message),
                "n_iter": getattr(res, "nit", None),
                "n_fev": getattr(res, "nfev", None),
                "time_s": time.time() - t_method,
            }
            logger.info("  %s: AUROC(synth)=%.4f, success=%s, iter=%s, time=%.2fs",
                        method_name, opt_auroc, res.success,
                        getattr(res, "nit", "?"), time.time() - t_method)

        except Exception as e:
            logger.error("  %s failed: %s", method_name, e)
            results[method_name] = {
                "weights": EQUAL_WEIGHTS.copy(),
                "auroc_synthetic": 0.5,
                "success": False,
                "message": str(e),
                "n_iter": 0,
                "n_fev": 0,
                "time_s": time.time() - t_method,
            }

    # ------- Find best method -------
    best_method = max(results, key=lambda m: results[m]["auroc_synthetic"])
    best_weights = results[best_method]["weights"]
    logger.info("Best method: %s (AUROC_synth=%.4f)",
                best_method, results[best_method]["auroc_synthetic"])

    # ------- Evaluate best optimized weights on test set -------
    logger.info("Evaluating optimized weights on test set ...")
    opt_result = run_baseline_detection(df_train, df_test,
                                        weights=best_weights,
                                        label="optimized")

    # ------- Save weights CSV -------
    weight_rows = []
    for method_name, res in results.items():
        row = {"method": method_name}
        row.update(res["weights"])
        row["auroc_synthetic"] = res["auroc_synthetic"]
        row["success"] = res["success"]
        row["time_s"] = res["time_s"]
        weight_rows.append(row)

    df_weights = pd.DataFrame(weight_rows)
    weights_path = os.path.join(OUTPUT_DIR, "optimization_weights.csv")
    df_weights.to_csv(weights_path, index=False)
    logger.info("Optimization weights saved to %s", weights_path)

    elapsed = time.time() - t0
    logger.info("Total optimization time: %.1f s", elapsed)

    return {
        "results_by_method": results,
        "best_method": best_method,
        "best_weights": best_weights,
        "opt_detection_result": opt_result,
        "df_weights": df_weights,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from dip.feature_extraction import run_feature_extraction, run_train_feature_extraction

    df_test, ref = run_feature_extraction()
    df_train = run_train_feature_extraction(ref)
    result = run_optimization(df_train, df_test)
    print("\nBest method:", result["best_method"])
    print("Best weights:", result["best_weights"])

"""
optimization_experiments.py — Optimization Method Comparison & Convergence Study.

Investigates feature weight optimization methods using scipy.optimize:
  OPT-SLSQP: Sequential Least Squares Programming (Steepest Descent with constraints)
  OPT-CG: Conjugate Gradient
  OPT-BFGS: Broyden-Fletcher-Goldfarb-Shanno (L-BFGS-B)
  OPT-TRUST: Trust-Region Constrained (trust-constr)

Tracks:
  - Iteration-by-iteration convergence curve
  - Function evaluations (nfev) and wall-clock execution time
  - Final learned feature weights
  - Synthetic validation AUROC vs. Generalization test AUROC

Important note:
  This module uses scipy.optimize (NOT Ant Colony Optimization / ACOMA).

Usage:
    python optimization_experiments.py --method SLSQP --category bottle
    python optimization_experiments.py --method all --category all
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
from scipy.optimize import minimize, LinearConstraint
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score

from experiments.experiment_config import (
    DEFAULT_CATEGORIES, PILOT_CATEGORY, GLOBAL_SEED, EXPERIMENT_STUDY_DIR,
)
from experiments.experiment_runner import ExperimentRunner, set_global_seed
from utils.config import (
    FEATURE_NAMES, EQUAL_WEIGHTS, OPTIMIZATION_MAX_ITER, get_category_config,
)
from optimization.optimization import generate_pseudo_anomalies, _weights_to_dict
from dip.baseline_detector import compute_scores_for_df, compute_threshold, evaluate

logger = logging.getLogger(__name__)

OPTIMIZER_CONFIGS = {
    "OPT-SLSQP": {
        "method": "SLSQP",
        "description": "Sequential Least Squares Programming",
        "literature": "Nocedal & Wright (2006) Numerical Optimization",
        "evidence_type": "A",
    },
    "OPT-CG": {
        "method": "CG",
        "description": "Nonlinear Conjugate Gradient",
        "literature": "Fletcher & Reeves (1964) Function minimization by conjugate gradients",
        "evidence_type": "A",
    },
    "OPT-BFGS": {
        "method": "L-BFGS-B",
        "description": "Limited-memory BFGS with bounds",
        "literature": "Byrd et al. (1995) A Limited Memory Algorithm for Bound Constrained Optimization",
        "evidence_type": "A",
    },
    "OPT-TRUST": {
        "method": "trust-constr",
        "description": "Trust-Region Interior-Point Constrained",
        "literature": "Conn et al. (2000) Trust Region Methods",
        "evidence_type": "A",
    },
}


def run_optimization_experiment(experiment_id: str, category: str):
    """Run feature weight optimization and track convergence."""
    if experiment_id not in OPTIMIZER_CONFIGS:
        raise ValueError(f"Unknown optimizer experiment: {experiment_id}")

    opt_info = OPTIMIZER_CONFIGS[experiment_id]
    scipy_method = opt_info["method"]

    result_dir = os.path.join(EXPERIMENT_STUDY_DIR, "dip_optimization", "optimizer_comparisons")
    os.makedirs(result_dir, exist_ok=True)

    cfg = get_category_config(category)
    train_candidates = [
        os.path.join(cfg.features_dir, "improved_train_features_mean.csv"),
        os.path.join(cfg.features_dir, "train_features.csv"),
        os.path.join(cfg.features_dir, f"{category}_train_features.csv"),
    ]
    test_candidates = [
        os.path.join(cfg.features_dir, "improved_test_features_mean.csv"),
        os.path.join(cfg.features_dir, "test_features.csv"),
        os.path.join(cfg.features_dir, f"{category}_test_features.csv"),
    ]
    train_feat_path = next((p for p in train_candidates if os.path.exists(p)), None)
    test_feat_path = next((p for p in test_candidates if os.path.exists(p)), None)

    if not train_feat_path or not test_feat_path:
        raise FileNotFoundError(f"Feature CSVs not found in {cfg.features_dir}")

    df_train = pd.read_csv(train_feat_path)
    df_test = pd.read_csv(test_feat_path)

    runner = ExperimentRunner(
        experiment_id=experiment_id,
        model="dip_optimization",
        experiment_type="dip_optimization/optimizer_comparisons",
        category=category,
        config=opt_info,
        seed=GLOBAL_SEED,
    )

    with runner.context():
        set_global_seed(GLOBAL_SEED)

        # 1. Generate pseudo-anomalies
        df_pseudo = generate_pseudo_anomalies(df_train, seed=GLOBAL_SEED)

        # Feature normalization parameters
        feature_stats = {}
        for f in FEATURE_NAMES:
            vals = df_train[f].values.copy()
            if f == "ssim":
                vals = 1.0 - vals
            feature_stats[f] = (float(np.mean(vals)), float(np.std(vals)))

        # Track iteration history
        iteration_history = []

        def tracked_objective(w_array):
            weights = _weights_to_dict(w_array)
            scores_norm = compute_scores_for_df(df_train, weights, feature_stats)
            scores_anom = compute_scores_for_df(df_pseudo, weights, feature_stats)
            y_t = np.concatenate([np.zeros(len(scores_norm)), np.ones(len(scores_anom))])
            y_s = np.concatenate([scores_norm, scores_anom])
            auroc = roc_auc_score(y_t, y_s) if len(np.unique(y_t)) >= 2 else 0.5
            iteration_history.append(-auroc)
            return -auroc

        w0 = np.ones(len(FEATURE_NAMES)) / len(FEATURE_NAMES)
        bounds = [(0.01, 1.0)] * len(FEATURE_NAMES)
        constraint_sum = {"type": "eq", "fun": lambda w: np.sum(np.abs(w)) - 1.0}

        kwargs = {
            "fun": tracked_objective,
            "x0": w0.copy(),
            "method": scipy_method,
            "options": {"maxiter": OPTIMIZATION_MAX_ITER},
        }

        if scipy_method in ("SLSQP",):
            kwargs["bounds"] = bounds
            kwargs["constraints"] = [constraint_sum]
        elif scipy_method in ("L-BFGS-B",):
            kwargs["bounds"] = bounds
        elif scipy_method == "trust-constr":
            A = np.ones((1, len(FEATURE_NAMES)))
            lc = LinearConstraint(A, lb=0.99, ub=1.01)
            kwargs["bounds"] = bounds
            kwargs["constraints"] = [lc]

        t_opt_start = time.time()
        res = minimize(**kwargs)
        opt_time = time.time() - t_opt_start

        opt_weights = _weights_to_dict(res.x)
        synth_auroc = -res.fun

        # Evaluate on actual test set (held-out clean evaluation)
        t_eval_start = time.time()
        test_scores = compute_scores_for_df(df_test, opt_weights, feature_stats)
        train_scores = compute_scores_for_df(df_train, opt_weights, feature_stats)
        threshold = compute_threshold(train_scores)

        y_true = (df_test["category"] != "good").astype(int).values
        eval_res = evaluate(y_true, test_scores, threshold=threshold)
        test_auroc = eval_res["auroc"]
        test_f1 = eval_res["f1"]
        eval_time = time.time() - t_eval_start

        logger.info("[%s - %s] Synth-AUROC=%.4f  Test-AUROC=%.4f  F1=%.4f  Iters=%d  Time=%.2fs",
                    experiment_id, category, synth_auroc, test_auroc, test_f1,
                    getattr(res, "nit", len(iteration_history)), opt_time)

        runner.log_metrics(
            image_auroc=test_auroc,
            pixel_auroc=float("nan"),
            average_precision=eval_res["average_precision"],
            precision=eval_res["precision"],
            recall=eval_res["recall"],
            f1_score=test_f1,
            training_samples=len(df_train),
            test_samples=len(df_test),
            training_time_s=opt_time,
            inference_time_s=eval_time,
            notes=f"Synthetic-AUROC: {synth_auroc:.4f}, Iters: {getattr(res, 'nit', len(iteration_history))}",
        )

        # Save convergence and weights CSV
        res_row = {
            "experiment_id": experiment_id,
            "category": category,
            "optimizer": scipy_method,
            "synthetic_auroc": synth_auroc,
            "test_auroc": test_auroc,
            "test_f1": test_f1,
            "n_iterations": getattr(res, "nit", len(iteration_history)),
            "n_fev": getattr(res, "nfev", len(iteration_history)),
            "optimization_time_s": opt_time,
            "success": res.success,
        }
        res_row.update(opt_weights)
        pd.DataFrame([res_row]).to_csv(
            os.path.join(result_dir, f"{experiment_id}_{category}_results.csv"),
            index=False, encoding="utf-8"
        )

    return {"image_auroc": test_auroc, "f1_score": test_f1, "synthetic_auroc": synth_auroc}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="DIP Feature Optimization Experiments")
    parser.add_argument("--method", type=str, required=True,
                        help="OPT-SLSQP, OPT-CG, OPT-BFGS, OPT-TRUST, or 'all'")
    parser.add_argument("--category", type=str, default=PILOT_CATEGORY,
                        help="Category or 'all'")
    args = parser.parse_args()

    exp_ids = list(OPTIMIZER_CONFIGS.keys()) if args.method == "all" else [args.method]
    categories = DEFAULT_CATEGORIES if args.category == "all" else [args.category]

    total = len(exp_ids) * len(categories)
    done = 0
    for exp_id in exp_ids:
        for cat in categories:
            done += 1
            print(f"\n[{done}/{total}] {exp_id} on {cat}...")
            try:
                res = run_optimization_experiment(exp_id, cat)
                print(f"  Test-AUROC={res['image_auroc']:.4f}  F1={res['f1_score']:.4f}  Synth-AUROC={res['synthetic_auroc']:.4f}")
            except Exception as e:
                print(f"  FAILED: {e}")

    print(f"\nResults in: {EXPERIMENT_STUDY_DIR}/dip_optimization/")

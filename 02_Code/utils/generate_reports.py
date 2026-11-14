"""
Report Generation Module — produces CSV/MD summaries from experiment results.
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
from datetime import datetime

import numpy as np
import pandas as pd

from utils.config import (
    OUTPUT_DIR, REPORTS_DIR, FEATURE_NAMES,
    BOTTLE_DIR, TRAIN_DIR, TEST_DIR, GT_DIR,
    NETWORK_BANDWIDTH_BPS, NETWORK_LATENCY_S,
    get_train_images, get_test_images, ensure_dirs,
    ANOMALOUS_CATEGORIES, TEST_CATEGORIES,
)

logger = logging.getLogger(__name__)


def generate_dataset_summary():
    """Generate dataset_summary.csv."""
    train_imgs = get_train_images()
    test_imgs = get_test_images()

    rows = []
    # Training
    rows.append({"split": "train", "category": "good", "count": len(train_imgs),
                 "image_size": "900x900", "format": "PNG"})
    # Test
    from collections import Counter
    cat_counts = Counter(cat for _, cat, _ in test_imgs)
    for cat in TEST_CATEGORIES:
        rows.append({"split": "test", "category": cat, "count": cat_counts.get(cat, 0),
                     "image_size": "900x900", "format": "PNG"})

    # Ground truth masks
    for cat in ANOMALOUS_CATEGORIES:
        gt_dir = os.path.join(GT_DIR, cat)
        if os.path.isdir(gt_dir):
            masks = [f for f in os.listdir(gt_dir) if f.endswith('.png')]
            rows.append({"split": "ground_truth", "category": cat, "count": len(masks),
                         "image_size": "900x900", "format": "PNG"})

    df = pd.DataFrame(rows)
    path = os.path.join(REPORTS_DIR, "dataset_summary.csv")
    df.to_csv(path, index=False)
    logger.info("Dataset summary saved to %s", path)
    return df


def generate_baseline_results(baseline_result):
    """Generate baseline_results.csv."""
    m = baseline_result["metrics"]
    rows = [{
        "detector": "Baseline (Equal Weights)",
        "auroc": m.get("auroc", float("nan")),
        "average_precision": m.get("average_precision", float("nan")),
        "precision": m["precision"],
        "recall": m["recall"],
        "f1": m["f1"],
        "fpr": m["fpr"],
        "tp": m["tp"], "fp": m["fp"], "tn": m["tn"], "fn": m["fn"],
        "threshold": baseline_result["threshold"],
        "n_test": len(baseline_result["y_true"]),
        "n_anomalous": int(sum(baseline_result["y_true"])),
        "n_normal": int(sum(1 - baseline_result["y_true"])),
    }]
    df = pd.DataFrame(rows)
    path = os.path.join(REPORTS_DIR, "baseline_results.csv")
    df.to_csv(path, index=False)
    logger.info("Baseline results saved to %s", path)
    return df


def generate_optimization_results(baseline_result, opt_info):
    """Generate optimization_results.csv."""
    rows = []
    # Baseline
    bm = baseline_result["metrics"]
    rows.append({
        "method": "Equal Weights (Baseline)",
        "auroc": bm.get("auroc", float("nan")),
        "f1": bm["f1"],
        "precision": bm["precision"],
        "recall": bm["recall"],
        **baseline_result["weights"],
    })

    # Optimized methods
    if opt_info and "results_by_method" in opt_info:
        for method, res in opt_info["results_by_method"].items():
            row = {
                "method": method,
                "auroc_synthetic": res["auroc_synthetic"],
                "success": res["success"],
                "time_s": res["time_s"],
            }
            row.update(res["weights"])
            rows.append(row)

    # Best optimized on test
    if opt_info and "opt_detection_result" in opt_info:
        om = opt_info["opt_detection_result"]["metrics"]
        rows.append({
            "method": f"Best Optimized ({opt_info.get('best_method', '?')})",
            "auroc": om.get("auroc", float("nan")),
            "f1": om["f1"],
            "precision": om["precision"],
            "recall": om["recall"],
            **opt_info.get("best_weights", {}),
        })

    df = pd.DataFrame(rows)
    path = os.path.join(REPORTS_DIR, "optimization_results.csv")
    df.to_csv(path, index=False)
    logger.info("Optimization results saved to %s", path)
    return df


def generate_compression_results(compression_result):
    """Generate compression_network_results.csv (just copy the summary)."""
    if compression_result is None:
        return None
    df = compression_result["df_summary"]
    path = os.path.join(REPORTS_DIR, "compression_network_results.csv")
    df.to_csv(path, index=False)
    logger.info("Compression results saved to %s", path)
    return df


def generate_combined_comparison(baseline_result, opt_info, compression_result):
    """Generate combined_comparison.csv."""
    rows = []
    bm = baseline_result["metrics"]
    rows.append({
        "experiment": "Baseline (Equal Weights)",
        "setting": "Original",
        "auroc": bm.get("auroc", float("nan")),
        "f1": bm["f1"],
        "precision": bm["precision"],
        "recall": bm["recall"],
    })

    if opt_info and "opt_detection_result" in opt_info:
        om = opt_info["opt_detection_result"]["metrics"]
        rows.append({
            "experiment": f"Optimized ({opt_info.get('best_method', '?')})",
            "setting": "Original",
            "auroc": om.get("auroc", float("nan")),
            "f1": om["f1"],
            "precision": om["precision"],
            "recall": om["recall"],
        })

    if compression_result is not None:
        for _, row in compression_result["df_summary"].iterrows():
            rows.append({
                "experiment": "Baseline + Compression",
                "setting": row["setting"],
                "auroc": row["auroc"],
                "f1": row["f1"],
                "precision": row["precision"],
                "recall": row["recall"],
            })

    df = pd.DataFrame(rows)
    path = os.path.join(REPORTS_DIR, "combined_comparison.csv")
    df.to_csv(path, index=False)
    logger.info("Combined comparison saved to %s", path)
    return df


def generate_experiment_log(start_time, end_time, baseline_result, opt_info, compression_result):
    """Generate experiment_log.txt."""
    path = os.path.join(REPORTS_DIR, "experiment_log.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("EXPERIMENT LOG\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Project: Industrial Anomaly Detection\n")
        f.write(f"Dataset: MVTec AD — Bottle category\n")
        f.write(f"Start Time: {start_time}\n")
        f.write(f"End Time:   {end_time}\n")
        f.write(f"Duration:   {end_time - start_time}\n\n")

        f.write("DATASET\n")
        f.write(f"  Training images: {len(get_train_images())}\n")
        f.write(f"  Test images:     {len(get_test_images())}\n\n")

        f.write("BASELINE DETECTION\n")
        bm = baseline_result["metrics"]
        f.write(f"  AUROC:     {bm.get('auroc', 'N/A')}\n")
        f.write(f"  AP:        {bm.get('average_precision', 'N/A')}\n")
        f.write(f"  F1:        {bm['f1']}\n")
        f.write(f"  Precision: {bm['precision']}\n")
        f.write(f"  Recall:    {bm['recall']}\n")
        f.write(f"  FPR:       {bm['fpr']}\n")
        f.write(f"  Threshold: {baseline_result['threshold']}\n\n")

        if opt_info:
            f.write("OPTIMIZATION\n")
            f.write(f"  Best Method: {opt_info.get('best_method', 'N/A')}\n")
            if "opt_detection_result" in opt_info:
                om = opt_info["opt_detection_result"]["metrics"]
                f.write(f"  AUROC:     {om.get('auroc', 'N/A')}\n")
                f.write(f"  F1:        {om['f1']}\n\n")

        if compression_result is not None:
            f.write("COMPRESSION EXPERIMENTS\n")
            for _, row in compression_result["df_summary"].iterrows():
                f.write(f"  {row['setting']:18s}: AUROC={row['auroc']:.4f}  "
                        f"F1={row['f1']:.4f}  Ratio={row['avg_compression_ratio']:.2f}x\n")

        f.write("\n" + "=" * 60 + "\n")
        f.write("END OF LOG\n")

    logger.info("Experiment log saved to %s", path)


def generate_results_summary(baseline_result, opt_info, compression_result):
    """Generate results_summary.md."""
    path = os.path.join(REPORTS_DIR, "results_summary.md")
    bm = baseline_result["metrics"]

    with open(path, 'w', encoding='utf-8') as f:
        f.write("# Experiment Results Summary\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Dataset\n\n")
        f.write(f"- **Category:** MVTec AD — Bottle\n")
        f.write(f"- **Training images (normal):** {len(get_train_images())}\n")
        test_imgs = get_test_images()
        n_normal = sum(1 for _, c, _ in test_imgs if c == 'good')
        n_anom = sum(1 for _, c, _ in test_imgs if c != 'good')
        f.write(f"- **Test images:** {len(test_imgs)} ({n_normal} normal, {n_anom} anomalous)\n")
        f.write(f"- **Image size:** 900×900 → resized to 256×256 for processing\n\n")

        f.write("## Baseline Detection\n\n")
        f.write("| Metric | Value |\n|--------|-------|\n")
        f.write(f"| AUROC | {bm.get('auroc', 'N/A'):.4f} |\n")
        f.write(f"| Average Precision | {bm.get('average_precision', 'N/A'):.4f} |\n")
        f.write(f"| Precision | {bm['precision']:.4f} |\n")
        f.write(f"| Recall | {bm['recall']:.4f} |\n")
        f.write(f"| F1-Score | {bm['f1']:.4f} |\n")
        f.write(f"| FPR | {bm['fpr']:.4f} |\n")
        f.write(f"| TP / FP / TN / FN | {bm['tp']} / {bm['fp']} / {bm['tn']} / {bm['fn']} |\n\n")

        if opt_info and "opt_detection_result" in opt_info:
            f.write("## Optimized Detection\n\n")
            om = opt_info["opt_detection_result"]["metrics"]
            f.write(f"- **Best method:** {opt_info.get('best_method', 'N/A')}\n")
            f.write(f"- **AUROC:** {om.get('auroc', 'N/A'):.4f}\n")
            f.write(f"- **F1:** {om['f1']:.4f}\n")
            f.write(f"- **Precision:** {om['precision']:.4f} | Recall: {om['recall']:.4f}\n\n")

        if compression_result is not None:
            f.write("## Compression & Network Results\n\n")
            f.write("| Setting | AUROC | F1 | Ratio | Avg Latency (ms) |\n")
            f.write("|---------|-------|----|-------|------------------|\n")
            for _, row in compression_result["df_summary"].iterrows():
                f.write(f"| {row['setting']} | {row['auroc']:.4f} | {row['f1']:.4f} | "
                        f"{row['avg_compression_ratio']:.2f}x | "
                        f"{row['avg_total_latency_s']*1000:.1f} |\n")
            f.write("\n")

        f.write("## Output Files\n\n")
        f.write(f"- Charts: `{os.path.basename(REPORTS_DIR)}/../charts/`\n")
        f.write(f"- Reports: `{os.path.basename(REPORTS_DIR)}/`\n")
        f.write(f"- Predictions: `{os.path.basename(OUTPUT_DIR)}/`\n")

    logger.info("Results summary saved to %s", path)


def run_reports(baseline_result, opt_info=None, compression_result=None,
                start_time=None, end_time=None):
    """Generate all reports."""
    ensure_dirs()
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("\n" + "=" * 60)
    print("STEP 6: GENERATING REPORTS")
    print("=" * 60)

    generate_dataset_summary()
    generate_baseline_results(baseline_result)
    generate_optimization_results(baseline_result, opt_info)
    generate_compression_results(compression_result)
    generate_combined_comparison(baseline_result, opt_info, compression_result)
    if start_time and end_time:
        generate_experiment_log(start_time, end_time, baseline_result, opt_info, compression_result)
    generate_results_summary(baseline_result, opt_info, compression_result)

    print(f"  All reports saved to {REPORTS_DIR}")

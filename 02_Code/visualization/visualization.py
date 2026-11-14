"""
Visualization Module — Generate all charts for the research project.
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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from utils.config import (
    OUTPUT_DIR, CHARTS_DIR, FEATURE_NAMES,
    COMPRESSION_SETTINGS, EQUAL_WEIGHTS, ensure_dirs,
)

logger = logging.getLogger(__name__)


def _save(fig, name):
    path = os.path.join(CHARTS_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("  Saved chart: %s", path)


def plot_roc_curves(baseline_result, opt_result=None):
    """Plot ROC curves for baseline and (optionally) optimized detector."""
    fig, ax = plt.subplots(figsize=(7, 6))

    bm = baseline_result["metrics"]
    if "roc_curve" in bm:
        fpr, tpr = bm["roc_curve"]
        ax.plot(fpr, tpr, 'b-', lw=2,
                label=f'Baseline (AUROC={bm["auroc"]:.4f})')

    if opt_result is not None:
        om = opt_result["metrics"]
        if "roc_curve" in om:
            fpr, tpr = om["roc_curve"]
            ax.plot(fpr, tpr, 'r--', lw=2,
                    label=f'Optimized (AUROC={om["auroc"]:.4f})')

    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve — Baseline vs Optimized Detector")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    _save(fig, "01_roc_curves.png")


def plot_confusion_matrices(baseline_result, opt_result=None):
    """Plot confusion matrix(es)."""
    n_plots = 2 if opt_result else 1
    fig, axes = plt.subplots(1, n_plots, figsize=(5 * n_plots, 5))
    if n_plots == 1:
        axes = [axes]

    labels_display = ["Normal", "Anomaly"]

    for ax, result, title in zip(
        axes,
        [baseline_result] + ([opt_result] if opt_result else []),
        ["Baseline"] + (["Optimized"] if opt_result else []),
    ):
        m = result["metrics"]
        cm = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
        im = ax.imshow(cm, cmap="Blues", interpolation="nearest")
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(labels_display)
        ax.set_yticklabels(labels_display)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_title(f"{title}\nF1={m['f1']:.4f}")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                        fontsize=18, fontweight='bold',
                        color='white' if cm[i, j] > cm.max() / 2 else 'black')
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    fig.suptitle("Confusion Matrices", fontsize=14, fontweight='bold')
    fig.tight_layout()
    _save(fig, "02_confusion_matrices.png")


def plot_score_distribution(baseline_result):
    """Plot score distributions for normal vs anomalous images."""
    fig, ax = plt.subplots(figsize=(8, 5))

    df = baseline_result["df_results"]
    threshold = baseline_result["threshold"]

    normal_scores = df[df["true_label"] == 0]["anomaly_score"]
    anomaly_scores = df[df["true_label"] == 1]["anomaly_score"]

    ax.hist(normal_scores, bins=15, alpha=0.6, color='green', label='Normal', edgecolor='darkgreen')
    ax.hist(anomaly_scores, bins=15, alpha=0.6, color='red', label='Anomalous', edgecolor='darkred')
    ax.axvline(threshold, color='black', linestyle='--', lw=2, label=f'Threshold={threshold:.4f}')
    ax.set_xlabel("Anomaly Score")
    ax.set_ylabel("Count")
    ax.set_title("Score Distribution — Normal vs Anomalous")
    ax.legend()
    ax.grid(True, alpha=0.3)
    _save(fig, "03_score_distribution.png")


def plot_compression_vs_filesize(df_summary):
    """Bar chart: compression setting vs average file size."""
    fig, ax = plt.subplots(figsize=(8, 5))
    settings = df_summary["setting"].values
    sizes_kb = df_summary["avg_compressed_size"].values / 1024

    bars = ax.bar(range(len(settings)), sizes_kb, color=['steelblue', 'orange', 'green', 'red'])
    ax.set_xticks(range(len(settings)))
    ax.set_xticklabels(settings, rotation=15)
    ax.set_ylabel("Average File Size (KB)")
    ax.set_title("Compression Setting vs File Size")
    ax.grid(True, axis='y', alpha=0.3)

    for bar, sz in zip(bars, sizes_kb):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{sz:.1f}', ha='center', va='bottom', fontsize=10)

    _save(fig, "04_compression_vs_filesize.png")


def plot_compression_vs_detection(df_summary):
    """Line chart: compression quality vs detection AUROC."""
    fig, ax1 = plt.subplots(figsize=(8, 5))

    settings = df_summary["setting"].values
    x = range(len(settings))

    ax1.plot(x, df_summary["auroc"].values, 'bo-', lw=2, markersize=8, label='AUROC')
    ax1.plot(x, df_summary["f1"].values, 'rs--', lw=2, markersize=8, label='F1-Score')
    ax1.set_xticks(x)
    ax1.set_xticklabels(settings, rotation=15)
    ax1.set_ylabel("Score")
    ax1.set_title("Compression Quality vs Detection Performance")
    ax1.legend(loc="lower left")
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0.8, 1.02])

    ax2 = ax1.twinx()
    ax2.bar(x, df_summary["avg_compression_ratio"].values, alpha=0.2, color='gray', label='Compression Ratio')
    ax2.set_ylabel("Compression Ratio")
    ax2.legend(loc="upper right")

    _save(fig, "05_compression_vs_detection.png")


def plot_compression_vs_latency(df_summary):
    """Chart: compression quality vs simulated latency."""
    fig, ax = plt.subplots(figsize=(8, 5))

    settings = df_summary["setting"].values
    latencies_ms = df_summary["avg_total_latency_s"].values * 1000

    bars = ax.bar(range(len(settings)), latencies_ms,
                  color=['steelblue', 'orange', 'green', 'red'])
    ax.set_xticks(range(len(settings)))
    ax.set_xticklabels(settings, rotation=15)
    ax.set_ylabel("Average Total Latency (ms)")
    ax.set_title("Compression Setting vs Simulated Total Latency\n"
                 "(Network: 10 Mbps, 50 ms base latency)")
    ax.grid(True, axis='y', alpha=0.3)

    for bar, lat in zip(bars, latencies_ms):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f'{lat:.1f}', ha='center', va='bottom', fontsize=10)

    _save(fig, "06_compression_vs_latency.png")


def plot_feature_weights(baseline_weights, opt_weights, best_method_name):
    """Compare feature weights: equal vs optimized."""
    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(FEATURE_NAMES))
    width = 0.35

    bw = [baseline_weights.get(f, 0) for f in FEATURE_NAMES]
    ow = [opt_weights.get(f, 0) for f in FEATURE_NAMES]

    ax.bar(x - width/2, bw, width, label='Equal Weights (Baseline)', color='steelblue')
    ax.bar(x + width/2, ow, width, label=f'Optimized ({best_method_name})', color='orange')

    ax.set_xticks(x)
    ax.set_xticklabels([f.replace('_', '\n') for f in FEATURE_NAMES], fontsize=9)
    ax.set_ylabel("Weight")
    ax.set_title("Feature Weights — Baseline vs Optimized")
    ax.legend()
    ax.grid(True, axis='y', alpha=0.3)

    _save(fig, "07_feature_weights.png")


def plot_sample_predictions(baseline_result, n_samples=4):
    """Show per-image score bar chart for a selection of images."""
    fig, ax = plt.subplots(figsize=(12, 5))

    df = baseline_result["df_results"]
    # Select n normal + n anomalous
    normals = df[df["true_label"] == 0].head(n_samples)
    anomalies = df[df["true_label"] == 1].head(n_samples)
    selected = pd.concat([normals, anomalies])

    labels = [f"{r['category']}/{r['image_id']}" for _, r in selected.iterrows()]
    scores = selected["anomaly_score"].values
    colors = ['green' if tl == 0 else 'red' for tl in selected["true_label"].values]

    bars = ax.barh(range(len(labels)), scores, color=colors, edgecolor='black', linewidth=0.5)
    ax.axvline(baseline_result["threshold"], color='black', linestyle='--', lw=2, label='Threshold')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Anomaly Score")
    ax.set_title("Sample Predictions (Green=Normal, Red=Anomalous)")
    ax.legend()
    ax.grid(True, axis='x', alpha=0.3)
    ax.invert_yaxis()

    _save(fig, "08_sample_predictions.png")


def run_visualization(baseline_result, opt_result=None, opt_info=None, compression_result=None):
    """Generate all charts."""
    ensure_dirs()
    os.makedirs(CHARTS_DIR, exist_ok=True)

    print("\n" + "=" * 60)
    print("STEP 5: GENERATING VISUALIZATIONS")
    print("=" * 60)

    # 1. ROC curves
    opt_detection = opt_info.get("opt_detection_result") if opt_info else opt_result
    plot_roc_curves(baseline_result, opt_detection)

    # 2. Confusion matrices
    plot_confusion_matrices(baseline_result, opt_detection)

    # 3. Score distribution
    plot_score_distribution(baseline_result)

    # 4-6. Compression charts
    if compression_result is not None:
        df_summary = compression_result["df_summary"]
        plot_compression_vs_filesize(df_summary)
        plot_compression_vs_detection(df_summary)
        plot_compression_vs_latency(df_summary)

    # 7. Feature weights
    if opt_info is not None:
        best_method = opt_info.get("best_method", "Optimized")
        best_weights = opt_info.get("best_weights", EQUAL_WEIGHTS)
        plot_feature_weights(baseline_result["weights"], best_weights, best_method)

    # 8. Sample predictions
    plot_sample_predictions(baseline_result)

    print(f"  All charts saved to {CHARTS_DIR}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    print("Run via run_all.py for full pipeline.")

"""
Feature Analysis Module.

Generates feature analysis visualizations:
  1. Feature correlation heatmap
  2. Feature distribution plots (normal vs anomalous)
  3. Feature-wise AUROC bar chart
  4. Feature redundancy analysis
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
import seaborn as sns
from sklearn.metrics import roc_auc_score

from utils.config import CHARTS_DIR, FEATURE_NAMES, ensure_dirs, get_category_config as _get_cat_cfg
from dip.improved_features import EXTENDED_FEATURE_NAMES

logger = logging.getLogger(__name__)


def _save(fig, name, subdir="feature_analysis", base_charts_dir=None):
    _base = base_charts_dir if base_charts_dir is not None else CHARTS_DIR
    out_dir = os.path.join(_base, subdir)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("  Saved: %s", path)


def plot_correlation_heatmap(df_combined, feature_names, filename="correlation_heatmap.png"):
    """Feature correlation matrix from all images."""
    available = [f for f in feature_names if f in df_combined.columns]
    corr = df_combined[available].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, vmin=-1, vmax=1, square=True,
                linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Matrix", fontsize=14, fontweight="bold")
    # Rotate labels
    ax.set_xticklabels([f.replace("_", "\n") for f in available], fontsize=8, rotation=45, ha="right")
    ax.set_yticklabels([f.replace("_", "\n") for f in available], fontsize=8, rotation=0)
    _save(fig, filename)
    return corr


def plot_feature_distributions(df_test, feature_names, filename_prefix="feat_dist"):
    """Per-feature distribution plots: normal vs anomalous."""
    available = [f for f in feature_names if f in df_test.columns]
    n_feats = len(available)
    n_cols = 3
    n_rows = (n_feats + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    axes = axes.flatten()

    labels = np.array([0 if c == "good" else 1 for c in df_test["category"]])

    for i, feat in enumerate(available):
        ax = axes[i]
        vals_normal = df_test.loc[labels == 0, feat].values
        vals_anomaly = df_test.loc[labels == 1, feat].values

        ax.hist(vals_normal, bins=15, alpha=0.6, color="green", label="Normal", edgecolor="darkgreen")
        ax.hist(vals_anomaly, bins=15, alpha=0.6, color="red", label="Anomalous", edgecolor="darkred")
        ax.set_title(feat.replace("_", " ").title(), fontsize=10)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    # Hide unused axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Feature Distributions: Normal vs Anomalous", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    _save(fig, f"{filename_prefix}.png")


def plot_feature_auroc(df_test, feature_names, filename="feature_auroc.png"):
    """Bar chart of per-feature AUROC values."""
    available = [f for f in feature_names if f in df_test.columns]
    labels = np.array([0 if c == "good" else 1 for c in df_test["category"]])

    aurocs = {}
    for feat in available:
        vals = df_test[feat].values.copy()
        # For SSIM, invert (lower SSIM = more anomalous)
        if feat == "ssim":
            vals = 1.0 - vals
        try:
            auc = roc_auc_score(labels, vals)
            aurocs[feat] = auc
        except ValueError:
            aurocs[feat] = 0.5

    # Sort by AUROC
    sorted_feats = sorted(aurocs.keys(), key=lambda f: aurocs[f], reverse=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2ecc71" if aurocs[f] >= 0.7 else "#e74c3c" if aurocs[f] < 0.55 else "#f39c12"
              for f in sorted_feats]

    bars = ax.barh(range(len(sorted_feats)),
                   [aurocs[f] for f in sorted_feats],
                   color=colors, edgecolor="black", linewidth=0.5)

    ax.set_yticks(range(len(sorted_feats)))
    ax.set_yticklabels([f.replace("_", " ").title() for f in sorted_feats], fontsize=9)
    ax.set_xlabel("AUROC", fontsize=11)
    ax.set_title("Per-Feature AUROC (Individual Discriminability)", fontsize=14, fontweight="bold")
    ax.axvline(0.5, color="gray", linestyle="--", lw=1, alpha=0.7, label="Random (0.5)")
    ax.axvline(0.7, color="green", linestyle="--", lw=1, alpha=0.5, label="Good (0.7)")
    ax.legend(fontsize=9)
    ax.grid(True, axis="x", alpha=0.3)
    ax.invert_yaxis()

    for bar, feat in zip(bars, sorted_feats):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{aurocs[feat]:.4f}", va="center", fontsize=9)

    _save(fig, filename)
    return aurocs


def plot_feature_redundancy(df_combined, feature_names, filename="feature_redundancy.png"):
    """Hierarchical clustering dendrogram of feature similarities."""
    from scipy.cluster.hierarchy import linkage, dendrogram
    from scipy.spatial.distance import squareform

    available = [f for f in feature_names if f in df_combined.columns]
    corr = df_combined[available].corr().abs()

    # Convert correlation to distance
    dist = 1 - corr
    np.fill_diagonal(dist.values, 0)
    condensed = squareform(dist.values)

    Z = linkage(condensed, method="average")

    fig, ax = plt.subplots(figsize=(10, 6))
    dendrogram(Z, labels=[f.replace("_", "\n") for f in available],
               leaf_rotation=45, leaf_font_size=9, ax=ax,
               color_threshold=0.5)
    ax.set_title("Feature Redundancy Dendrogram\n(Distance = 1 - |Correlation|)",
                 fontsize=14, fontweight="bold")
    ax.set_ylabel("Distance (1 - |correlation|)")
    ax.axhline(0.3, color="red", linestyle="--", alpha=0.5, label="High redundancy threshold")
    ax.legend()
    _save(fig, filename)


def run_feature_analysis(df_train, df_test, feature_names=None, cfg=None):
    """Run all feature analysis steps."""
    _charts = cfg.charts_dir if cfg is not None else CHARTS_DIR
    if cfg is not None:
        cfg.ensure_output_dirs()
    else:
        ensure_dirs()
    if feature_names is None:
        feature_names = EXTENDED_FEATURE_NAMES

    print("\n" + "=" * 60)
    print("FEATURE ANALYSIS")
    print("=" * 60)

    df_combined = pd.concat([df_train, df_test], ignore_index=True)

    # Monkey-patch _save to route output to per-category charts dir
    import functools as _ft
    _save_orig = _save
    def _save_cat(fig, name, subdir="feature_analysis", base_charts_dir=None):
        _save_orig(fig, name, subdir=subdir, base_charts_dir=_charts)

    # 1. Correlation heatmap
    corr = plot_correlation_heatmap(df_combined, feature_names)

    # 2. Feature distributions
    plot_feature_distributions(df_test, feature_names)

    # 3. Per-feature AUROC
    aurocs = plot_feature_auroc(df_test, feature_names)

    # 4. Redundancy dendrogram
    plot_feature_redundancy(df_combined, feature_names)

    print("  Feature analysis complete.")
    return {"correlation": corr, "feature_aurocs": aurocs}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from dip.improved_features import run_improved_feature_extraction
    df_test, df_train, _, _ = run_improved_feature_extraction(ref_type="mean")
    run_feature_analysis(df_train, df_test)

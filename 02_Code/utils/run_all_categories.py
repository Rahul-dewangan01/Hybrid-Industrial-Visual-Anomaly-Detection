"""
Multi-Category Master Experiment Orchestrator.

Iterates across all valid MVTec AD categories (12 total), runs the full
11-stage research experiment pipeline on GPU/CPU for each, and produces
an aggregated cross-category benchmark matrix and summary leaderboard.

Valid categories (12):
    bottle, cable, capsule, carpet, grid, hazelnut,
    leather, metal_nut, screw, tile, toothbrush, transistor

Skipped categories (no training images present):
    pill, wood, zipper

Outputs:
    03_Results/<category>/...                  (per-category results)
    03_Results/all_categories_leaderboard.csv  (concatenated results)
    03_Results/category_auroc_matrix.csv       (model x category AUROC matrix)
    03_Results/category_f1_matrix.csv          (model x category F1 matrix)
    03_Results/multicategory_summary.json      (execution metadata & summary)
    03_Results/multicategory_auroc_heatmap.png (cross-category comparison figure)

Usage:
    python 02_Code/utils/run_all_categories.py [--categories bottle,cable,...] [--skip-completed]
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "02_Code")
for p in [PROJECT_ROOT, CODE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.config import (
    RESULTS_DIR, DEVICE,
    get_category_config, list_valid_categories,
)
from utils.run_master_experiments import main as run_single_category

logger = logging.getLogger("multi_category_runner")


def check_category_completed(category: str) -> bool:
    """Check if full results for category already exist."""
    cfg = get_category_config(category)
    leaderboard_file = os.path.join(cfg.predictions_dir, f"{category}_leaderboard.csv")
    return os.path.exists(leaderboard_file) and os.path.getsize(leaderboard_file) > 100


def plot_cross_category_heatmaps(df_auroc_pivot: pd.DataFrame, df_f1_pivot: pd.DataFrame, save_dir: str):
    """Plot cross-category AUROC and F1 performance heatmaps."""
    os.makedirs(save_dir, exist_ok=True)

    # 1. AUROC Heatmap
    fig, ax = plt.subplots(figsize=(max(12, len(df_auroc_pivot.columns) * 1.1), max(7, len(df_auroc_pivot) * 0.6)))
    sns.heatmap(
        df_auroc_pivot,
        annot=True,
        fmt=".3f",
        cmap="YlGnBu",
        vmin=0.4,
        vmax=1.0,
        cbar_kws={"label": "AUROC"},
        ax=ax,
        linewidths=0.5
    )
    ax.set_title("Cross-Category Anomaly Detection Performance (AUROC Matrix)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("MVTec AD Category", fontsize=11, fontweight="bold")
    ax.set_ylabel("Anomaly Detection Model", fontsize=11, fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    auroc_path = os.path.join(save_dir, "multicategory_auroc_heatmap.png")
    fig.savefig(auroc_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  [SAVED] {auroc_path}")

    # 2. F1 Heatmap
    fig, ax = plt.subplots(figsize=(max(12, len(df_f1_pivot.columns) * 1.1), max(7, len(df_f1_pivot) * 0.6)))
    sns.heatmap(
        df_f1_pivot,
        annot=True,
        fmt=".3f",
        cmap="Blues",
        vmin=0.3,
        vmax=1.0,
        cbar_kws={"label": "F1 Score"},
        ax=ax,
        linewidths=0.5
    )
    ax.set_title("Cross-Category Detection F1 Scores (F1 Matrix)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("MVTec AD Category", fontsize=11, fontweight="bold")
    ax.set_ylabel("Anomaly Detection Model", fontsize=11, fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    f1_path = os.path.join(save_dir, "multicategory_f1_heatmap.png")
    fig.savefig(f1_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  [SAVED] {f1_path}")


def aggregate_all_results(categories: list, output_dir: str):
    """Aggregate per-category leaderboards into cross-category matrices."""
    all_dfs = []
    for cat in categories:
        cfg = get_category_config(cat)
        lb_path = os.path.join(cfg.predictions_dir, f"{cat}_leaderboard.csv")
        if os.path.exists(lb_path):
            try:
                df = pd.read_csv(lb_path)
                if "Category" not in df.columns:
                    df["Category"] = cat
                all_dfs.append(df)
            except Exception as e:
                logger.warning("Could not read %s: %s", lb_path, e)

    if not all_dfs:
        print("No completed category results found to aggregate.")
        return None

    df_combined = pd.concat(all_dfs, ignore_index=True)
    all_lb_path = os.path.join(output_dir, "all_categories_master_leaderboard.csv")
    df_combined.to_csv(all_lb_path, index=False, encoding="utf-8")
    print(f"\n[SAVED] Concatenated leaderboard: {all_lb_path} ({len(df_combined)} rows)")

    # Standardize Model names if slight variances exist
    # Create AUROC pivot table: Model x Category
    df_auroc = df_combined.pivot_table(index="Model", columns="Category", values="AUROC", aggfunc="mean")
    df_auroc["Mean_AUROC"] = df_auroc.mean(axis=1)
    df_auroc = df_auroc.sort_values(by="Mean_AUROC", ascending=False)
    auroc_matrix_path = os.path.join(output_dir, "category_auroc_matrix.csv")
    df_auroc.to_csv(auroc_matrix_path, encoding="utf-8")
    print(f"[SAVED] AUROC Matrix: {auroc_matrix_path}")

    # Create F1 pivot table: Model x Category
    df_f1 = df_combined.pivot_table(index="Model", columns="Category", values="F1", aggfunc="mean")
    df_f1["Mean_F1"] = df_f1.mean(axis=1)
    df_f1 = df_f1.sort_values(by="Mean_F1", ascending=False)
    f1_matrix_path = os.path.join(output_dir, "category_f1_matrix.csv")
    df_f1.to_csv(f1_matrix_path, encoding="utf-8")
    print(f"[SAVED] F1 Matrix: {f1_matrix_path}")

    # Generate heatmaps (excluding the aggregate 'Mean' column from heatmap)
    cats_only = [c for c in df_auroc.columns if c != "Mean_AUROC"]
    plot_cross_category_heatmaps(df_auroc[cats_only], df_f1[[c for c in df_f1.columns if c != "Mean_F1"]], output_dir)

    # Print summary table to console
    print("\n" + "=" * 80)
    print("CROSS-CATEGORY MEAN PERFORMANCE SUMMARY (Sorted by Mean AUROC):")
    print("=" * 80)
    summary_cols = ["Mean_AUROC"]
    summary_df = pd.DataFrame({
        "Model": df_auroc.index,
        "Mean_AUROC": df_auroc["Mean_AUROC"].values,
        "Mean_F1": df_f1.loc[df_auroc.index, "Mean_F1"].values if "Mean_F1" in df_f1.columns else np.nan,
    })
    print(summary_df.to_string(index=False))
    print("=" * 80)

    return df_combined


def run_all(categories=None, skip_completed=False):
    """Run pipeline across all specified categories."""
    total_start = datetime.now()
    valid_cats = list_valid_categories()

    if categories is None or len(categories) == 0:
        targets = valid_cats
    else:
        targets = [c.strip() for c in categories if c.strip() in valid_cats]

    print("=" * 75)
    print("MVTec AD MULTI-CATEGORY RESEARCH BENCHMARK")
    print("=" * 75)
    print(f"Device:                 {DEVICE}")
    print(f"Valid Categories ({len(valid_cats)}): {', '.join(valid_cats)}")
    print(f"Target Execution ({len(targets)}): {', '.join(targets)}")
    print(f"Skip Completed:         {skip_completed}")
    print(f"Results Root:           {RESULTS_DIR}")
    print("=" * 75)

    exec_summary = {
        "start_time": total_start.isoformat(),
        "device": str(DEVICE),
        "target_categories": targets,
        "category_results": {},
    }

    for idx, cat in enumerate(targets, 1):
        cat_start = datetime.now()
        print("\n\n" + "#" * 75)
        print(f"[{idx}/{len(targets)}] CATEGORY: {cat.upper()}")
        print("#" * 75)

        if skip_completed and check_category_completed(cat):
            print(f"--> Category '{cat}' is already completed. Skipping as requested (--skip-completed).")
            exec_summary["category_results"][cat] = {
                "status": "SKIPPED_ALREADY_COMPLETED",
                "duration_seconds": 0,
            }
            continue

        try:
            run_single_category(category=cat)
            duration = (datetime.now() - cat_start).total_seconds()
            exec_summary["category_results"][cat] = {
                "status": "SUCCESS",
                "duration_seconds": duration,
            }
            print(f"\n--> Successfully completed '{cat}' in {duration:.1f}s")
        except Exception as e:
            duration = (datetime.now() - cat_start).total_seconds()
            logger.error("Category '%s' failed with error: %s", cat, e, exc_info=True)
            exec_summary["category_results"][cat] = {
                "status": "FAILED",
                "error": str(e),
                "duration_seconds": duration,
            }
            print(f"\n[ERROR] Failed to run '{cat}': {e}")

    total_duration = (datetime.now() - total_start).total_seconds()
    exec_summary["end_time"] = datetime.now().isoformat()
    exec_summary["total_duration_seconds"] = total_duration

    # Aggregate cross-category metrics
    print("\n" + "=" * 75)
    print("AGGREGATING CROSS-CATEGORY RESEARCH BENCHMARK DATA")
    print("=" * 75)
    aggregate_all_results(targets, RESULTS_DIR)

    # Save execution log json
    summary_json_path = os.path.join(RESULTS_DIR, "multicategory_summary.json")
    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(exec_summary, f, indent=2)
    print(f"[SAVED] Multi-category execution summary: {summary_json_path}")

    print("\n" + "=" * 75)
    print(f"ALL TARGET CATEGORIES FINISHED IN {total_duration / 60:.2f} MINUTES")
    print("=" * 75)


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-Category Industrial Anomaly Detection Benchmarker.")
    parser.add_argument(
        "--categories", "-c",
        type=str,
        default=None,
        help="Comma-separated category names (e.g. 'bottle,cable,tile'). Defaults to all 12 valid categories.",
    )
    parser.add_argument(
        "--skip-completed",
        action="store_true",
        default=False,
        help="Skip categories that already have finished leaderboards.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cats = args.categories.split(",") if args.categories else None
    run_all(categories=cats, skip_completed=args.skip_completed)

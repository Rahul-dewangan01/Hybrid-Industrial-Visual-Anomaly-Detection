"""
generate_all_charts.py — Generates the 10 Overall Research Comparison Charts.

Saves high-resolution PNGs (300 DPI) to 03_Results/experimental_study/overall_analysis/charts/:
  Chart 1:  Overall Image-Level AUROC Comparison
  Chart 2:  Overall Pixel-Level AUROC Comparison
  Chart 3:  Overall F1-Score Comparison
  Chart 4:  Performance vs. Inference Time Trade-Off (Scatter)
  Chart 5:  Performance vs. Training/Fit Time (Scatter)
  Chart 6:  Category-Wise Performance Heatmap (Image AUROC)
  Chart 7:  Best Validated Configuration Comparison
  Chart 8:  Overall Computational Footprint Comparison
  Chart 9:  Hybrid Ensemble vs. Individual Models
  Chart 10: Experiment Execution Status Distribution (Project Management)
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

_REPORTING_DIR = os.path.dirname(__file__)
if _REPORTING_DIR not in sys.path:
    sys.path.insert(0, _REPORTING_DIR)

from reporting_utils import (
    load_master_df, get_completed_experiments, REPORT_CONFIG, MODEL_COLORS
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def generate_all_overall_charts() -> dict:
    df_raw = load_master_df()
    df = get_completed_experiments(df_raw)
    out_dir = REPORT_CONFIG["paths"]["overall_charts"]
    os.makedirs(out_dir, exist_ok=True)
    generated = {}

    logger.info("Generating 10 Overall Research Charts...")

    # Model Display Names
    model_labels = {
        "patchcore": "PatchCore",
        "padim": "PaDiM",
        "hybrid_fusion": "Hybrid Fusion",
        "autoencoder": "Conv Autoencoder",
        "dip_optimization": "DIP Optimization"
    }

    # Best configurations for fair comparison:
    # PatchCore: PC-RN50 or PC-CORESET-05
    # PaDiM: PADIM-DIM-100 or PADIM-COV-1e-2
    # Hybrid: HY-03
    # Autoencoder: AE-ARCH-5L or AE-01
    # DIP Optimization: OPT-SLSQP

    # -------------------------------------------------------------
    # Chart 1: Overall Image-Level AUROC Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
    best_exps = {
        "PatchCore (ResNet-50)": df[df["experiment_id"] == "PC-RN50"]["image_auroc"].mean(),
        "Hybrid DL-Heavy (HY-03)": df[df["experiment_id"] == "HY-03"]["image_auroc"].mean(),
        "PaDiM (100-dim)": df[df["experiment_id"] == "PADIM-DIM-100"]["image_auroc"].mean(),
        "Autoencoder (5-Level)": df[df["experiment_id"] == "AE-ARCH-5L"]["image_auroc"].mean(),
        "DIP SLSQP (Pseudo-Opt)": df[df["experiment_id"] == "OPT-SLSQP"]["image_auroc"].mean(),
    }
    c_list = ["#2ca02c", "#9467bd", "#ff7f0e", "#1f77b4", "#d62728"]
    bars = ax.bar(list(best_exps.keys()), list(best_exps.values()), color=c_list, width=0.52, alpha=0.9)
    ax.set_ylim([0.45, 1.05])
    ax.set_ylabel("Macro Image-Level AUROC", fontweight="bold")
    ax.set_title("Chart 1: Overall Image-Level AUROC Comparison (Validated Best Configurations)", fontweight="bold", pad=12)
    ax.axhline(1.0, color="#d0d7de", linestyle="--", linewidth=0.8)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.015, f"{h:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=9.5)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    p1 = os.path.join(out_dir, "chart01_overall_image_auroc.png")
    plt.savefig(p1)
    plt.close()
    generated["chart1"] = p1

    # -------------------------------------------------------------
    # Chart 2: Overall Pixel-Level AUROC Comparison (Localization)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    px_exps = {
        "PatchCore (PC-CORESET-05)": df[df["experiment_id"] == "PC-CORESET-05"]["pixel_auroc"].mean(),
        "PaDiM (PADIM-DIM-100)": df[df["experiment_id"] == "PADIM-DIM-100"]["pixel_auroc"].mean(),
        "Autoencoder (AE-EP-100)": df[df["experiment_id"] == "AE-EP-100"]["pixel_auroc"].mean(),
        "Autoencoder (AE-04 MSE+SSIM)": df[df["experiment_id"] == "AE-04"]["pixel_auroc"].mean(),
    }
    bars = ax.bar(list(px_exps.keys()), list(px_exps.values()), color=["#2ca02c", "#ff7f0e", "#1f77b4", "#3a86ff"], width=0.48, alpha=0.9)
    ax.set_ylim([0.65, 1.02])
    ax.set_ylabel("Macro Pixel-Level AUROC", fontweight="bold")
    ax.set_title("Chart 2: Overall Defect Localization Comparison (Pixel AUROC)", fontweight="bold", pad=12)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.01, f"{h:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=9.5)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    p2 = os.path.join(out_dir, "chart02_overall_pixel_auroc.png")
    plt.savefig(p2)
    plt.close()
    generated["chart2"] = p2

    # -------------------------------------------------------------
    # Chart 3: Overall F1-Score Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
    f1_exps = {
        "PatchCore (PC-RN50)": df[df["experiment_id"] == "PC-RN50"]["f1_score"].mean(),
        "Hybrid Fusion (HY-03)": df[df["experiment_id"] == "HY-03"]["f1_score"].mean(),
        "PaDiM (PADIM-DIM-50)": df[df["experiment_id"] == "PADIM-DIM-50"]["f1_score"].mean(),
        "Autoencoder (AE-ARCH-5L)": df[df["experiment_id"] == "AE-ARCH-5L"]["f1_score"].mean(),
        "DIP Optimization (SLSQP)": df[df["experiment_id"] == "OPT-SLSQP"]["f1_score"].mean(),
    }
    bars = ax.bar(list(f1_exps.keys()), list(f1_exps.values()), color=["#2ca02c", "#9467bd", "#ff7f0e", "#1f77b4", "#d62728"], width=0.5, alpha=0.9)
    ax.set_ylim([0, 1.05])
    ax.set_ylabel("Macro F1-Score", fontweight="bold")
    ax.set_title("Chart 3: Overall F1-Score Comparison at Analytical Normality Thresholds", fontweight="bold", pad=12)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.02, f"{h:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=9.5)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    p3 = os.path.join(out_dir, "chart03_overall_f1_score.png")
    plt.savefig(p3)
    plt.close()
    generated["chart3"] = p3

    # -------------------------------------------------------------
    # Chart 4: Performance vs. Inference Time Scatter
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=300)
    models_to_scatter = ["patchcore", "padim", "hybrid_fusion", "autoencoder", "dip_optimization"]
    for m in models_to_scatter:
        sub = df[df["model"] == m].dropna(subset=["inference_time_s", "image_auroc"])
        if not sub.empty:
            # Latency per image in milliseconds
            sub["ms_per_img"] = (sub["inference_time_s"] / sub["test_samples"].replace(0, 1)) * 1000
            ax.scatter(sub["ms_per_img"], sub["image_auroc"], label=model_labels.get(m, m),
                       color=MODEL_COLORS.get(m, "#333"), alpha=0.75, s=60, edgecolors="none")

    ax.set_xscale("log")
    ax.set_xlabel("Inference Latency per Image (milliseconds, log scale)", fontweight="bold")
    ax.set_ylabel("Image-Level AUROC", fontweight="bold")
    ax.set_title("Chart 4: Performance vs. Inference Latency Trade-Off Across All Runs", fontweight="bold", pad=12)
    ax.set_ylim([0.2, 1.03])
    ax.legend(loc="lower left", framealpha=0.9)
    plt.tight_layout()
    p4 = os.path.join(out_dir, "chart04_performance_vs_inference_time.png")
    plt.savefig(p4)
    plt.close()
    generated["chart4"] = p4

    # -------------------------------------------------------------
    # Chart 5: Performance vs. Training/Fit Time
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=300)
    for m in models_to_scatter:
        sub = df[df["model"] == m].dropna(subset=["training_time_s", "image_auroc"])
        if not sub.empty:
            ax.scatter(sub["training_time_s"] + 0.01, sub["image_auroc"], label=model_labels.get(m, m),
                       color=MODEL_COLORS.get(m, "#333"), alpha=0.75, s=65, edgecolors="none")

    ax.set_xscale("log")
    ax.set_xlabel("Training / Fitting Time (seconds, log scale)", fontweight="bold")
    ax.set_ylabel("Image-Level AUROC", fontweight="bold")
    ax.set_title("Chart 5: Performance vs. Training / Model Construction Cost", fontweight="bold", pad=12)
    ax.set_ylim([0.2, 1.03])
    ax.legend(loc="lower left", framealpha=0.9)
    plt.tight_layout()
    p5 = os.path.join(out_dir, "chart05_performance_vs_training_time.png")
    plt.savefig(p5)
    plt.close()
    generated["chart5"] = p5

    # -------------------------------------------------------------
    # Chart 6: Category-Wise Performance Heatmap (Image AUROC)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    # Pivot best model scores across categories
    heatmap_df = df[df["experiment_id"].isin(["PC-RN50", "PADIM-DIM-100", "HY-03", "OPT-SLSQP", "AE-01"])]
    if not heatmap_df.empty:
        pivot_data = heatmap_df.pivot_table(index="category", columns="model", values="image_auroc", aggfunc="mean")
        pivot_data.rename(columns=model_labels, inplace=True)
        sns.heatmap(pivot_data, annot=True, fmt=".3f", cmap="YlGnBu", cbar_kws={'label': 'Image AUROC'},
                    linewidths=0.5, vmin=0.3, vmax=1.0, ax=ax)
        ax.set_title("Chart 6: Category-Wise Image AUROC Heatmap (Best Configurations)", fontweight="bold", pad=14)
        ax.set_ylabel("MVTec AD Industrial Category", fontweight="bold")
        ax.set_xlabel("Detection Paradigm", fontweight="bold")
        plt.tight_layout()
        p6 = os.path.join(out_dir, "chart06_category_performance_heatmap.png")
        plt.savefig(p6)
        plt.close()
        generated["chart6"] = p6

    # -------------------------------------------------------------
    # Chart 7: Best Configuration Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=300)
    cfg_labels = ["PatchCore\n(ResNet-50)", "Hybrid Fusion\n(HY-03 DL-Heavy)", "PaDiM\n(100-dim)", "Autoencoder\n(AE-ARCH-5L)", "Autoencoder\n(AE-01 MSE)", "DIP\n(SLSQP)"]
    auroc_means = [
        df[df["experiment_id"] == "PC-RN50"]["image_auroc"].mean(),
        df[df["experiment_id"] == "HY-03"]["image_auroc"].mean(),
        df[df["experiment_id"] == "PADIM-DIM-100"]["image_auroc"].mean(),
        df[df["experiment_id"] == "AE-ARCH-5L"]["image_auroc"].mean(),
        df[df["experiment_id"] == "AE-01"]["image_auroc"].mean(),
        df[df["experiment_id"] == "OPT-SLSQP"]["image_auroc"].mean(),
    ]
    f1_means = [
        df[df["experiment_id"] == "PC-RN50"]["f1_score"].mean(),
        df[df["experiment_id"] == "HY-03"]["f1_score"].mean(),
        df[df["experiment_id"] == "PADIM-DIM-100"]["f1_score"].mean(),
        df[df["experiment_id"] == "AE-ARCH-5L"]["f1_score"].mean(),
        df[df["experiment_id"] == "AE-01"]["f1_score"].mean(),
        df[df["experiment_id"] == "OPT-SLSQP"]["f1_score"].mean(),
    ]

    x = np.arange(len(cfg_labels))
    w = 0.35
    ax.bar(x - w/2, auroc_means, width=w, label="Image AUROC", color="#1b4965", alpha=0.9)
    ax.bar(x + w/2, f1_means, width=w, label="F1-Score", color="#f4a261", alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(cfg_labels)
    ax.set_ylim([0, 1.12])
    ax.set_ylabel("Metric Value", fontweight="bold")
    ax.set_title("Chart 7: Performance Ranking of Top Validated Configurations", fontweight="bold", pad=12)
    ax.legend(loc="lower left")
    plt.tight_layout()
    p7 = os.path.join(out_dir, "chart07_best_configuration_comparison.png")
    plt.savefig(p7)
    plt.close()
    generated["chart7"] = p7

    # -------------------------------------------------------------
    # Chart 8: Overall Computational Comparison
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=300)
    avg_train_times = [
        df[df["model"] == "patchcore"]["training_time_s"].mean(),
        df[df["model"] == "padim"]["training_time_s"].mean(),
        df[df["model"] == "autoencoder"]["training_time_s"].mean(),
        df[df["model"] == "dip_optimization"]["training_time_s"].mean(),
    ]
    t_labels = ["PatchCore (Coreset)", "PaDiM (Fit)", "Autoencoder (50 ep)", "DIP Optimization"]
    ax1.bar(t_labels, avg_train_times, color=["#2ca02c", "#ff7f0e", "#1f77b4", "#d62728"], width=0.5, alpha=0.9)
    ax1.set_ylabel("Mean Training / Fit Time (s)", fontweight="bold")
    ax1.set_title("Model Construction Time", fontweight="bold")
    ax1.set_xticklabels(t_labels, rotation=25, ha="right")

    avg_inf_times = [
        df[df["model"] == "patchcore"]["inference_time_s"].mean() * 1000 / 50,  # ~50 test imgs
        df[df["model"] == "padim"]["inference_time_s"].mean() * 1000 / 50,
        df[df["model"] == "autoencoder"]["inference_time_s"].mean() * 1000 / 50,
        df[df["model"] == "dip_optimization"]["inference_time_s"].mean() * 1000 / 50,
    ]
    ax2.bar(t_labels, avg_inf_times, color=["#2ca02c", "#ff7f0e", "#1f77b4", "#d62728"], width=0.5, alpha=0.9)
    ax2.set_ylabel("Latency per Image (ms)", fontweight="bold")
    ax2.set_title("Test Inference Latency per Image", fontweight="bold")
    ax2.set_xticklabels(t_labels, rotation=25, ha="right")

    plt.suptitle("Chart 8: Comprehensive Computational Footprint Comparison", fontweight="bold", y=1.02)
    plt.tight_layout()
    p8 = os.path.join(out_dir, "chart08_computational_footprint.png")
    plt.savefig(p8)
    plt.close()
    generated["chart8"] = p8

    # -------------------------------------------------------------
    # Chart 9: Hybrid vs. Individual Models
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)
    hy_comp = {
        "Hybrid Weighted (HY-03)": df[df["experiment_id"] == "HY-03"]["image_auroc"].mean(),
        "Hybrid Equal (HY-01)": df[df["experiment_id"] == "HY-01"]["image_auroc"].mean(),
        "Standalone PatchCore": df[df["experiment_id"] == "PC-CORESET-05"]["image_auroc"].mean(),
        "Standalone PaDiM": df[df["experiment_id"] == "PADIM-DIM-100"]["image_auroc"].mean(),
        "Standalone Autoencoder": df[df["experiment_id"] == "AE-ARCH-4L"]["image_auroc"].mean(),
        "Standalone DIP": df[df["experiment_id"] == "OPT-SLSQP"]["image_auroc"].mean(),
    }
    bars = ax.bar(list(hy_comp.keys()), list(hy_comp.values()),
                  color=["#7209b7", "#b5179e", "#2ca02c", "#ff7f0e", "#1f77b4", "#d62728"], width=0.52, alpha=0.9)
    ax.set_ylim([0.45, 1.05])
    ax.set_ylabel("Macro Image-Level AUROC", fontweight="bold")
    ax.set_title("Chart 9: Hybrid Ensemble Fusion vs. Standalone Detection Paradigms", fontweight="bold", pad=12)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 0.015, f"{h:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=9.5)
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    p9 = os.path.join(out_dir, "chart09_hybrid_vs_standalone.png")
    plt.savefig(p9)
    plt.close()
    generated["chart9"] = p9

    # -------------------------------------------------------------
    # Chart 10: Overall Experiment Status Distribution
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    status_counts = df_raw["status"].value_counts()
    status_colors = {"completed": "#2a9d8f", "failed": "#e76f51", "planned": "#e9c46a", "running": "#264653"}
    c_status = [status_colors.get(s, "#888") for s in status_counts.index]
    bars = ax.bar(status_counts.index.str.upper(), status_counts.values, color=c_status, width=0.45, alpha=0.9)
    ax.set_ylabel("Number of Experiment Runs", fontweight="bold")
    ax.set_title("Chart 10: Overall Research Study Execution & Completion Status", fontweight="bold", pad=12)
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + (max(status_counts.values)*0.015), f"{h}", ha="center", va="bottom", fontweight="bold", fontsize=10)
    ax.set_ylim([0, max(status_counts.values) * 1.15])
    plt.tight_layout()
    p10 = os.path.join(out_dir, "chart10_execution_status.png")
    plt.savefig(p10)
    plt.close()
    generated["chart10"] = p10

    logger.info("All 10 Overall Charts Generated Successfully!")
    return generated


if __name__ == "__main__":
    generate_all_overall_charts()

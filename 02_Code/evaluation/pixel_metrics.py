"""
Pixel-Level Anomaly Evaluation & Localization Heatmaps.

Evaluates pixel-level AUROC and Average Precision (AP) against the 31 MVTec ground-truth masks.
Generates side-by-side localization comparison figures:
  Input -> Ground Truth Mask -> Autoencoder Error -> PatchCore Heatmap -> PaDiM Heatmap
"""


import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..\.."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import os
import logging

import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve

from utils.config import CHARTS_DIR, OUTPUT_DIR, ensure_dirs

logger = logging.getLogger(__name__)


def evaluate_pixel_metrics(gt_masks, anomaly_maps_dict, cfg=None):
    """Computes pixel-level AUROC and AP for each model that produces anomaly maps.

    Args:
        gt_masks: list of numpy arrays (H, W), binary {0, 1}
        anomaly_maps_dict: dict of model_name -> list of numpy arrays (H, W), continuous scores

    Returns:
        dict of model_name -> dict(pixel_auroc, pixel_ap)
    """
    ensure_dirs()
    # Flatten ground truth across all images
    all_gt = np.concatenate([m.ravel() for m in gt_masks]).astype(int)

    results = {}
    summary_rows = []

    for name, maps in anomaly_maps_dict.items():
        all_pred = np.concatenate([m.ravel() for m in maps]).astype(np.float32)

        if len(np.unique(all_gt)) >= 2:
            pix_auroc = float(roc_auc_score(all_gt, all_pred))
            pix_ap = float(average_precision_score(all_gt, all_pred))
        else:
            pix_auroc = float("nan")
            pix_ap = float("nan")

        results[name] = {
            "pixel_auroc": pix_auroc,
            "pixel_ap": pix_ap,
        }

        summary_rows.append({
            "model": name,
            "pixel_auroc": pix_auroc,
            "pixel_ap": pix_ap,
        })
        logger.info("[Pixel Metrics] %s: Pixel-AUROC=%.4f, Pixel-AP=%.4f", name, pix_auroc, pix_ap)

    df_pix = pd.DataFrame(summary_rows)
    _out_dir = cfg.pixel_metrics_dir if cfg is not None else OUTPUT_DIR
    os.makedirs(_out_dir, exist_ok=True)
    df_pix.to_csv(os.path.join(_out_dir, "pixel_level_metrics.csv"), index=False)
    return results


def plot_side_by_side_localizations(test_images_info, inputs, gt_masks,
                                    ae_maps, patchcore_maps, padim_maps,
                                    n_samples_per_cat=2, cfg=None):
    """Generates side-by-side localization comparison figures.

    Columns:
      1. Original Input Image
      2. Ground Truth Defect Mask
      3. Autoencoder Reconstruction Error Map
      4. PatchCore Distance Heatmap
      5. PaDiM Mahalanobis Distance Heatmap
    """
    _charts_base = cfg.charts_dir if cfg is not None else CHARTS_DIR
    out_dir = os.path.join(_charts_base, "pixel_localization")
    os.makedirs(out_dir, exist_ok=True)

    # Group sample indices by category
    categories = {}
    for idx, info in enumerate(test_images_info):
        cat = info["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(idx)

    selected_indices = []
    # Include anomalous samples first, then good
    anom_cats = [c for c in categories.keys() if c != "good"]
    for cat in anom_cats + (["good"] if "good" in categories else []):
        selected_indices.extend(categories[cat][:n_samples_per_cat])
    if not selected_indices:
        selected_indices = list(range(min(len(test_images_info), 6)))

    n_samples = len(selected_indices)
    fig, axes = plt.subplots(n_samples, 5, figsize=(18, 3.2 * n_samples))
    if n_samples == 1:
        axes = np.expand_dims(axes, 0)

    col_titles = [
        "Input Image",
        "Ground Truth Mask",
        "Autoencoder Error",
        "PatchCore Heatmap",
        "PaDiM Heatmap",
    ]

    for row_idx, sample_idx in enumerate(selected_indices):
        info = test_images_info[sample_idx]
        img_in = inputs[sample_idx]
        gt = gt_masks[sample_idx]
        ae_m = ae_maps[sample_idx]
        pc_m = patchcore_maps[sample_idx]
        padim_m = padim_maps[sample_idx]

        # 1. Input Image
        axes[row_idx, 0].imshow(img_in)
        axes[row_idx, 0].set_ylabel(f"{info['category']}\n{info['image_id']}", fontsize=10, fontweight="bold")
        axes[row_idx, 0].set_xticks([])
        axes[row_idx, 0].set_yticks([])

        # 2. GT Mask
        axes[row_idx, 1].imshow(gt, cmap="gray")
        axes[row_idx, 1].set_xticks([])
        axes[row_idx, 1].set_yticks([])

        # 3. AE Map
        im3 = axes[row_idx, 2].imshow(ae_m, cmap="inferno")
        axes[row_idx, 2].set_xticks([])
        axes[row_idx, 2].set_yticks([])

        # 4. PatchCore Map
        im4 = axes[row_idx, 3].imshow(pc_m, cmap="turbo")
        axes[row_idx, 3].set_xticks([])
        axes[row_idx, 3].set_yticks([])

        # 5. PaDiM Map
        im5 = axes[row_idx, 4].imshow(padim_m, cmap="jet")
        axes[row_idx, 4].set_xticks([])
        axes[row_idx, 4].set_yticks([])

        # Column headers on top row
        if row_idx == 0:
            for col_idx, title in enumerate(col_titles):
                axes[row_idx, col_idx].set_title(title, fontsize=12, fontweight="bold", pad=8)

    fig.suptitle("Anomaly Localization Comparison Across Paradigms", fontsize=15, fontweight="bold", y=1.002)
    fig.tight_layout()
    save_path = os.path.join(out_dir, "localization_comparison_grid.png")
    fig.savefig(save_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved side-by-side localization chart to %s", save_path)

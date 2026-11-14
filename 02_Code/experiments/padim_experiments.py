"""
padim_experiments.py — PaDiM Feature Dimension and Covariance Regularization Experiments.

Experiments:
  Feature Dimensions:
    PADIM-DIM-50:  50 random channels
    PADIM-DIM-100: 100 random channels (Baseline)
    PADIM-DIM-200: 200 random channels

  Covariance Regularization:
    PADIM-COV-1e-4: λ = 1e-4
    PADIM-COV-1e-3: λ = 1e-3
    PADIM-COV-1e-2: λ = 1e-2 (Baseline, ε = 0.01)

Usage:
    python padim_experiments.py --experiment PADIM-DIM-50 --category bottle
    python padim_experiments.py --experiment all_dims --category all
    python padim_experiments.py --experiment all_cov --category bottle
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

import cv2
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score

from experiments.experiment_config import (
    PADIM_FEATURE_DIM_EXPERIMENTS, PADIM_COVARIANCE_EXPERIMENTS,
    DEFAULT_CATEGORIES, PILOT_CATEGORY, GLOBAL_SEED, EXPERIMENT_STUDY_DIR,
)
from experiments.experiment_runner import ExperimentRunner, set_global_seed
from deep_learning.dataset import MVTecDataset
from utils.config import DEVICE, THRESHOLD_K, IMAGE_SIZE

logger = logging.getLogger(__name__)


class PaDiMFlexibleExtractor(nn.Module):
    """Extracts features from layer1, layer2, layer3 of ResNet-18 with configurable channel selection."""

    def __init__(self, n_components=100, seed=GLOBAL_SEED, device=DEVICE):
        super().__init__()
        self.device = device
        self.n_components = n_components

        backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        backbone.eval()
        for p in backbone.parameters():
            p.requires_grad = False

        self.conv1 = backbone.conv1
        self.bn1 = backbone.bn1
        self.relu = backbone.relu
        self.maxpool = backbone.maxpool
        self.layer1 = backbone.layer1
        self.layer2 = backbone.layer2
        self.layer3 = backbone.layer3

        total_dim = 64 + 128 + 256  # 448
        rng = np.random.RandomState(seed)
        self.selected_indices = rng.choice(total_dim, min(n_components, total_dim), replace=False)
        self.to(device)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        f1 = self.layer1(x)  # (B, 64, 64, 64)
        f2 = self.layer2(f1)  # (B, 128, 32, 32)
        f3 = self.layer3(f2)  # (B, 256, 16, 16)

        target_size = f1.shape[-2:]
        f2_up = F.interpolate(f2, size=target_size, mode="bilinear", align_corners=False)
        f3_up = F.interpolate(f3, size=target_size, mode="bilinear", align_corners=False)

        embedding = torch.cat([f1, f2_up, f3_up], dim=1)
        embedding = embedding[:, self.selected_indices, :, :]
        return embedding


def run_padim_experiment(experiment_id: str, category: str):
    """Run one PaDiM experiment for one category."""
    all_configs = {**PADIM_FEATURE_DIM_EXPERIMENTS, **PADIM_COVARIANCE_EXPERIMENTS}
    if experiment_id not in all_configs:
        raise ValueError(f"Unknown PaDiM experiment: {experiment_id}")

    cfg = all_configs[experiment_id]
    is_dim = experiment_id in PADIM_FEATURE_DIM_EXPERIMENTS
    exp_type = "feature_dimension_experiments" if is_dim else "covariance_experiments"
    result_dir = os.path.join(EXPERIMENT_STUDY_DIR, "padim", exp_type)
    os.makedirs(result_dir, exist_ok=True)

    runner = ExperimentRunner(
        experiment_id=experiment_id,
        model="padim",
        experiment_type=f"padim/{exp_type}",
        category=category,
        config=cfg,
        seed=GLOBAL_SEED,
    )

    with runner.context():
        set_global_seed(GLOBAL_SEED)
        n_components = cfg.get("n_components", 100)
        cov_reg = cfg.get("cov_regularization", 0.01)

        extractor = PaDiMFlexibleExtractor(n_components=n_components, seed=GLOBAL_SEED, device=DEVICE)
        extractor.eval()

        train_ds = MVTecDataset(category=category, split="train", image_size=256, augment=False)
        train_loader = DataLoader(train_ds, batch_size=8, shuffle=False)

        t_fit = time.time()
        all_embeddings = []
        with torch.no_grad():
            for batch in train_loader:
                x = batch["image"].to(DEVICE)
                emb = extractor(x)
                all_embeddings.append(emb.cpu().numpy())

        X = np.concatenate(all_embeddings, axis=0)  # (N, C, H, W)
        N, C, H, W = X.shape
        mean = np.mean(X, axis=0)

        X_centered = (X - mean).transpose(2, 3, 0, 1)  # (H, W, N, C)
        inv_cov_arr = np.zeros((H, W, C, C), dtype=np.float32)
        identity = np.eye(C, dtype=np.float32) * float(cov_reg)

        for i in range(H):
            for j in range(W):
                patch_centered = X_centered[i, j]
                cov = np.cov(patch_centered, rowvar=False) + identity
                inv_cov_arr[i, j] = np.linalg.inv(cov)

        fit_time = time.time() - t_fit
        logger.info("PaDiM fitted in %.2fs (Grid: %dx%d, Dims: %d, λ: %g)", fit_time, H, W, C, cov_reg)

        def predict_image(x_img):
            with torch.no_grad():
                emb = extractor(x_img).cpu().numpy()[0]
            diff = (emb - mean).transpose(1, 2, 0)
            dist_map = np.zeros((H, W), dtype=np.float32)
            for i in range(H):
                for j in range(W):
                    d = diff[i, j]
                    dist_map[i, j] = np.sqrt(np.dot(np.dot(d, inv_cov_arr[i, j]), d))
            dist_up = cv2.resize(dist_map, (IMAGE_SIZE[0], IMAGE_SIZE[1]))
            dist_smooth = cv2.GaussianBlur(dist_up, (9, 9), 2.0)
            score = float(np.max(dist_smooth))
            return dist_smooth, score

        # Threshold from training scores (clean zero-leakage)
        train_scores = []
        with torch.no_grad():
            for batch in DataLoader(train_ds, batch_size=1, shuffle=False):
                x = batch["image"].to(DEVICE)
                _, score = predict_image(x)
                train_scores.append(score)

        train_scores = np.array(train_scores)
        threshold = float(np.mean(train_scores) + THRESHOLD_K * np.std(train_scores))

        # Test set evaluation
        test_ds = MVTecDataset(category=category, split="test", image_size=256, augment=False)
        test_loader = DataLoader(test_ds, batch_size=1, shuffle=False)

        t_inf = time.time()
        results = []
        anomaly_maps = []
        gt_masks = []

        for batch in test_loader:
            x = batch["image"].to(DEVICE)
            label = int(batch["label"][0])
            mask = batch["mask"][0, 0].cpu().numpy()
            amap, score = predict_image(x)
            anomaly_maps.append(amap)
            gt_masks.append(mask)
            results.append({
                "true_label": label,
                "anomaly_score": score,
                "predicted_label": int(score >= threshold),
            })

        inference_time = time.time() - t_inf

        y_true = np.array([r["true_label"] for r in results])
        y_scores = np.array([r["anomaly_score"] for r in results])
        y_pred = np.array([r["predicted_label"] for r in results])

        auroc = float(roc_auc_score(y_true, y_scores))
        ap = float(average_precision_score(y_true, y_scores))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))

        all_gt = np.concatenate([m.ravel() for m in gt_masks]).astype(int)
        all_sc = np.concatenate([m.ravel() for m in anomaly_maps])
        pixel_auroc = float(roc_auc_score(all_gt, all_sc)) if len(np.unique(all_gt)) >= 2 else float("nan")

        logger.info("Image-AUROC=%.4f Pixel-AUROC=%.4f F1=%.4f", auroc, pixel_auroc, f1)

        runner.log_metrics(
            image_auroc=auroc, pixel_auroc=pixel_auroc,
            average_precision=ap, precision=prec, recall=rec, f1_score=f1,
            training_samples=len(train_ds), test_samples=len(test_ds),
            training_time_s=fit_time, inference_time_s=inference_time,
        )

        result_csv = os.path.join(result_dir, f"{experiment_id}_{category}_results.csv")
        pd.DataFrame([{
            "experiment_id": experiment_id, "category": category,
            "n_components": n_components, "cov_regularization": cov_reg,
            "image_auroc": auroc, "pixel_auroc": pixel_auroc,
            "f1_score": f1, "average_precision": ap,
            "precision": prec, "recall": rec,
            "fit_time_s": fit_time, "inference_time_s": inference_time,
        }]).to_csv(result_csv, index=False, encoding="utf-8")

    return {"image_auroc": auroc, "pixel_auroc": pixel_auroc, "f1_score": f1}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="PaDiM Experiments")
    parser.add_argument("--experiment", type=str, required=True,
                        help="Experiment ID or 'all_dims' / 'all_cov' / 'all'")
    parser.add_argument("--category", type=str, default=PILOT_CATEGORY,
                        help="Category or 'all'")
    args = parser.parse_args()

    if args.experiment == "all_dims":
        exp_ids = list(PADIM_FEATURE_DIM_EXPERIMENTS.keys())
    elif args.experiment == "all_cov":
        exp_ids = list(PADIM_COVARIANCE_EXPERIMENTS.keys())
    elif args.experiment == "all":
        exp_ids = list(PADIM_FEATURE_DIM_EXPERIMENTS.keys()) + list(PADIM_COVARIANCE_EXPERIMENTS.keys())
    else:
        exp_ids = [args.experiment]

    categories = DEFAULT_CATEGORIES if args.category == "all" else [args.category]

    total = len(exp_ids) * len(categories)
    done = 0
    for exp_id in exp_ids:
        for cat in categories:
            done += 1
            print(f"\n[{done}/{total}] {exp_id} on {cat}...")
            try:
                res = run_padim_experiment(exp_id, cat)
                print(f"  AUROC={res['image_auroc']:.4f}  Pixel-AUROC={res['pixel_auroc']:.4f}  F1={res['f1_score']:.4f}")
            except Exception as e:
                print(f"  FAILED: {e}")

    print(f"\nResults in: {EXPERIMENT_STUDY_DIR}/padim/")

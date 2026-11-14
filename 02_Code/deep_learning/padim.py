"""
PaDiM: A Patch Distribution Modeling Framework for Anomaly Detection and Localization.

Reference: Defard et al., 2021.
Models patch embeddings as multivariate Gaussian distributions per spatial position.
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

import cv2
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score, confusion_matrix

from utils.config import (
    OUTPUT_DIR, THRESHOLD_K, ensure_dirs, IMAGE_SIZE, DEVICE,
)
from deep_learning.dataset import MVTecBottleDataset, MVTecDataset

logger = logging.getLogger(__name__)


# ============================================================
# PaDiM Feature Extractor
# ============================================================

class PaDiMFeatureExtractor(nn.Module):
    """Extracts features from layer1, layer2, layer3 of ResNet-18."""

    def __init__(self, selected_indices=None, n_components=100, seed=42, device=DEVICE):
        super().__init__()
        self.device = device

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
        if selected_indices is None:
            rng = np.random.RandomState(seed)
            self.selected_indices = rng.choice(total_dim, n_components, replace=False)
        else:
            self.selected_indices = selected_indices

        self.to(device)

    def forward(self, x):
        """Extract multi-layer concatenated embedding at 64x64 grid."""
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        f1 = self.layer1(x)  # (B, 64, 64, 64)
        f2 = self.layer2(f1)  # (B, 128, 32, 32)
        f3 = self.layer3(f2)  # (B, 256, 16, 16)

        # Upsample f2 and f3 to 64x64
        target_size = f1.shape[-2:]
        f2_up = F.interpolate(f2, size=target_size, mode="bilinear", align_corners=False)
        f3_up = F.interpolate(f3, size=target_size, mode="bilinear", align_corners=False)

        # Concatenate: (B, 448, 64, 64)
        embedding = torch.cat([f1, f2_up, f3_up], dim=1)

        # Subsample channels with selected indices: (B, 100, 64, 64)
        embedding = embedding[:, self.selected_indices, :, :]
        return embedding


# ============================================================
# PaDiM Model
# ============================================================

class PaDiMDetector:
    """PaDiM Anomaly Detector."""

    def __init__(self, n_components=100, device=DEVICE):
        self.device = device
        self.n_components = n_components
        self.feature_extractor = PaDiMFeatureExtractor(n_components=n_components, device=device)
        self.mean = None  # (C, H, W)
        self.inv_cov = None  # (H, W, C, C)
        self.threshold = None

    def fit(self, train_loader):
        """Fit multivariate Gaussians at each patch location (i, j)."""
        logger.info("Extracting PaDiM patch representations from training set...")
        t0 = time.time()

        all_embeddings = []
        with torch.no_grad():
            for batch in train_loader:
                x = batch["image"].to(self.device)
                emb = self.feature_extractor(x)  # (B, C, H, W)
                all_embeddings.append(emb.cpu().numpy())

        # (N, C, H, W) where N=104, C=100, H=64, W=64
        X = np.concatenate(all_embeddings, axis=0)
        N, C, H, W = X.shape
        logger.info("Fitted patch grid: N=%d, C=%d, Grid=(%d, %d)", N, C, H, W)

        # Compute empirical mean: (C, H, W)
        self.mean = np.mean(X, axis=0)

        # Compute regularized covariance & inverse covariance per spatial position
        # X_perm: (H, W, N, C)
        X_centered = (X - self.mean).transpose(2, 3, 0, 1)  # (H, W, N, C)

        inv_cov_arr = np.zeros((H, W, C, C), dtype=np.float32)
        identity = np.eye(C, dtype=np.float32) * 0.01  # epsilon * I regularizer

        for i in range(H):
            for j in range(W):
                patch_centered = X_centered[i, j]  # (N, C)
                cov = np.cov(patch_centered, rowvar=False) + identity
                inv_cov_arr[i, j] = np.linalg.inv(cov)

        self.inv_cov = inv_cov_arr
        logger.info("PaDiM Gaussian distribution estimation completed in %.1fs", time.time() - t0)

    def predict_image(self, x_img):
        """Compute pixel anomaly map and image score via Mahalanobis distance."""
        with torch.no_grad():
            emb = self.feature_extractor(x_img).cpu().numpy()[0]  # (C, H, W)

        C, H, W = emb.shape
        diff = (emb - self.mean).transpose(1, 2, 0)  # (H, W, C)

        # Compute Mahalanobis distance per patch (i, j)
        # dist[i, j] = sqrt( diff[i, j] @ inv_cov[i, j] @ diff[i, j].T )
        dist_map = np.zeros((H, W), dtype=np.float32)
        for i in range(H):
            for j in range(W):
                d = diff[i, j]
                dist_map[i, j] = np.sqrt(np.dot(np.dot(d, self.inv_cov[i, j]), d))

        # Upscale distance map to original image size (256, 256)
        dist_map_up = cv2.resize(dist_map, (IMAGE_SIZE[0], IMAGE_SIZE[1]))

        # Smooth map
        dist_map_smooth = cv2.GaussianBlur(dist_map_up, (9, 9), 2.0)

        # Image score: max of distance map
        image_score = float(np.max(dist_map_smooth))

        return dist_map_smooth, image_score


# ============================================================
# Pipeline Runner
# ============================================================

def run_padim_pipeline(n_components=100, device=DEVICE, category="bottle"):
    """Execute PaDiM distribution modeling, scoring, and evaluation."""
    ensure_dirs()
    print("\n" + "=" * 60)
    print("PADIM EXPERIMENT (Patch Distribution Modeling)")
    print("=" * 60)

    train_ds = MVTecDataset(category=category, split="train", image_size=256, augment=False)
    train_loader = DataLoader(train_ds, batch_size=8, shuffle=False)

    detector = PaDiMDetector(n_components=n_components, device=device)
    detector.fit(train_loader)

    # 1. Compute training scores for threshold
    logger.info("Computing PaDiM training anomaly scores for threshold...")
    train_scores = []
    with torch.no_grad():
        for batch in DataLoader(train_ds, batch_size=1, shuffle=False):
            x = batch["image"].to(device)
            _, score = detector.predict_image(x)
            train_scores.append(score)

    train_scores = np.array(train_scores)
    mu = np.mean(train_scores)
    sigma = np.std(train_scores)
    threshold = float(mu + THRESHOLD_K * sigma)
    detector.threshold = threshold
    logger.info("PaDiM train scores: mean=%.4f, std=%.4f, threshold(k=%.1f)=%.4f",
                mu, sigma, THRESHOLD_K, threshold)

    # 2. Evaluate test set
    test_ds = MVTecDataset(category=category, split="test", image_size=256, augment=False)
    test_loader = DataLoader(test_ds, batch_size=1, shuffle=False)

    test_results = []
    anomaly_maps = []
    gt_masks = []

    logger.info("Evaluating on test set (%d images)...", len(test_ds))
    for batch in test_loader:
        x = batch["image"].to(device)
        defect_type = batch["category"][0]
        img_id = batch["image_id"][0]
        label = int(batch["label"][0])
        mask = batch["mask"][0, 0].cpu().numpy()

        amap, score = detector.predict_image(x)
        anomaly_maps.append(amap)
        gt_masks.append(mask)

        test_results.append({
            "image_id": img_id,
            "category": defect_type,
            "true_label": label,
            "anomaly_score": score,
            "predicted_label": int(score >= threshold),
        })

    df_res = pd.DataFrame(test_results)
    y_true = df_res["true_label"].values
    y_scores = df_res["anomaly_score"].values
    y_pred = df_res["predicted_label"].values

    auroc = roc_auc_score(y_true, y_scores)
    ap = average_precision_score(y_true, y_scores)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    # Pixel-level AUROC
    all_gt = np.concatenate([m.ravel() for m in gt_masks]).astype(int)
    all_scores = np.concatenate([m.ravel() for m in anomaly_maps])
    if len(np.unique(all_gt)) >= 2:
        pixel_auroc = float(roc_auc_score(all_gt, all_scores))
    else:
        pixel_auroc = float("nan")

    metrics = {
        "auroc": auroc,
        "average_precision": ap,
        "f1": f1,
        "precision": prec,
        "recall": rec,
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
        "fpr": float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0,
        "pixel_auroc": pixel_auroc,
        "threshold": threshold,
    }

    logger.info("PaDiM Metrics: Image-AUROC=%.4f, Pixel-AUROC=%.4f, F1=%.4f, P=%.4f, R=%.4f",
                auroc, pixel_auroc, f1, prec, rec)
    logger.info("Confusion: TP=%d FP=%d TN=%d FN=%d", tp, fp, tn, fn)

    from utils.config import get_category_config as _gcc
    _cfg_pd = _gcc(category)
    _cfg_pd.ensure_output_dirs()
    _out_pd = _cfg_pd.predictions_dir
    df_res.to_csv(os.path.join(_out_pd, "padim_predictions.csv"), index=False)

    return {
        "metrics": metrics,
        "df_results": df_res,
        "test_scores": y_scores,
        "train_scores": train_scores,
        "anomaly_maps": anomaly_maps,
        "gt_masks": gt_masks,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    res = run_padim_pipeline(n_components=100)
    print("\nPaDiM Final Metrics:", res["metrics"])

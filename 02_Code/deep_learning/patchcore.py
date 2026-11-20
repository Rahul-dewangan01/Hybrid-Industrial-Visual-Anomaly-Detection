"""
PatchCore Anomaly Detection Pipeline.

Implements the PatchCore framework (Roth et al., 2022) using pretrained ResNet-18:
  1. Multi-scale feature extraction from intermediate layers (layer2 + layer3).
  2. Coreset subsampling (greedy k-center / random subsampling) for efficient memory bank.
  3. Nearest-neighbor patch anomaly scoring.
  4. Pixel-level anomaly heatmaps and image-level classification.
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
from sklearn.random_projection import SparseRandomProjection

from utils.config import (
    OUTPUT_DIR, THRESHOLD_K, ensure_dirs, IMAGE_SIZE, DEVICE,
)
from deep_learning.dataset import MVTecBottleDataset, MVTecDataset

logger = logging.getLogger(__name__)


# ============================================================
# Feature Extractor
# ============================================================

class ResNet18FeatureExtractor(nn.Module):
    """Extracts and concatenates multi-scale features from layer2 and layer3."""

    def __init__(self, device=DEVICE):
        super().__init__()
        self.device = device
        # Load pretrained ResNet-18
        backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        backbone.eval()
        for param in backbone.parameters():
            param.requires_grad = False

        self.conv1 = backbone.conv1
        self.bn1 = backbone.bn1
        self.relu = backbone.relu
        self.maxpool = backbone.maxpool
        self.layer1 = backbone.layer1
        self.layer2 = backbone.layer2
        self.layer3 = backbone.layer3
        self.to(device)

    def forward(self, x):
        """Extract multi-scale patch features."""
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        feat2 = self.layer2(x)  # (B, 128, H/8, W/8) -> (B, 128, 32, 32)
        feat3 = self.layer3(feat2)  # (B, 256, H/16, W/16) -> (B, 256, 16, 16)

        # Upsample feat3 to match feat2 spatial resolution
        feat3_up = F.interpolate(feat3, size=feat2.shape[-2:], mode="bilinear", align_corners=False)

        # Concatenate features along channel dimension: (B, 128+256=384, 32, 32)
        features = torch.cat([feat2, feat3_up], dim=1)

        # Average pooling to aggregate local neighborhood information (receptive field smoothing)
        features = F.avg_pool2d(features, kernel_size=3, stride=1, padding=1)

        return features


# ============================================================
# Coreset Subsampling
# ============================================================

def subsample_coreset(features, percentage=0.10, seed=42):
    """Subsamples feature vectors using greedy k-center coreset selection.

    Args:
        features: numpy array (N, D)
        percentage: fraction of samples to retain
    """
    n_samples = features.shape[0]
    n_coreset = max(100, int(n_samples * percentage))

    logger.info("Coreset subsampling: selecting %d / %d patches (%.1f%%)...",
                n_coreset, n_samples, percentage * 100)

    # Use Random Projection for fast distance computation if dimension is large
    if features.shape[1] > 64:
        projector = SparseRandomProjection(n_components=64, random_state=seed)
        features_proj = projector.fit_transform(features)
    else:
        features_proj = features

    # Greedy K-Center clustering
    rng = np.random.RandomState(seed)
    first_idx = rng.randint(n_samples)

    if torch.cuda.is_available():
        device = torch.device("cuda")
        feat_t = torch.from_numpy(features_proj).float().to(device)
        selected_indices = [first_idx]
        min_distances = torch.norm(feat_t - feat_t[first_idx], dim=1)

        for step in range(1, n_coreset):
            next_idx = int(torch.argmax(min_distances).item())
            selected_indices.append(next_idx)
            new_dists = torch.norm(feat_t - feat_t[next_idx], dim=1)
            min_distances = torch.minimum(min_distances, new_dists)

            if (step + 1) % 1000 == 0 or (step + 1) == n_coreset:
                logger.info("  Coreset progress: [%d/%d]", step + 1, n_coreset)
    else:
        selected_indices = [first_idx]
        min_distances = np.linalg.norm(features_proj - features_proj[first_idx], axis=1)

        for step in range(1, n_coreset):
            next_idx = int(np.argmax(min_distances))
            selected_indices.append(next_idx)
            new_dists = np.linalg.norm(features_proj - features_proj[next_idx], axis=1)
            min_distances = np.minimum(min_distances, new_dists)

            if (step + 1) % 1000 == 0 or (step + 1) == n_coreset:
                logger.info("  Coreset progress: [%d/%d]", step + 1, n_coreset)

    return features[selected_indices]


# ============================================================
# PatchCore Detector
# ============================================================

class PatchCoreDetector:
    """PatchCore Anomaly Detector."""

    def __init__(self, coreset_percentage=0.05, device=DEVICE):
        self.device = device
        self.coreset_percentage = coreset_percentage
        self.feature_extractor = ResNet18FeatureExtractor(device=device)
        self.memory_bank = None  # torch tensor (M, D)
        self.threshold = None

    def fit(self, train_loader):
        """Build memory bank from normal training images."""
        logger.info("Extracting features from training set for PatchCore memory bank...")
        t0 = time.time()
        patch_list = []

        with torch.no_grad():
            for batch in train_loader:
                x = batch["image"].to(self.device)
                feats = self.feature_extractor(x)  # (B, C, H, W)
                B, C, H, W = feats.shape
                # Reshape to (B*H*W, C)
                patches = feats.permute(0, 2, 3, 1).reshape(-1, C).cpu().numpy()
                patch_list.append(patches)

        all_patches = np.concatenate(patch_list, axis=0)
        logger.info("Extracted %d total patches of dim %d in %.1fs",
                    all_patches.shape[0], all_patches.shape[1], time.time() - t0)

        # Coreset subsampling
        coreset_patches = subsample_coreset(all_patches, percentage=self.coreset_percentage)
        self.memory_bank = torch.from_numpy(coreset_patches).float().to(self.device)
        logger.info("Memory bank constructed: shape %s", tuple(self.memory_bank.shape))

    def predict_image(self, x_img):
        """Compute pixel anomaly map and image score for a single image tensor (1, 3, H, W)."""
        with torch.no_grad():
            feats = self.feature_extractor(x_img)
            _, C, H, W = feats.shape
            patches = feats.permute(0, 2, 3, 1).reshape(-1, C)  # (H*W, C)

            # Compute L2 distances to all memory bank entries in chunks
            # patches: (N, C), memory_bank: (M, C)
            # dist = sqrt(||p - m||^2)
            chunk_size = 256
            min_dists = []
            for i in range(0, patches.shape[0], chunk_size):
                chunk = patches[i:i + chunk_size]
                # (chunk_size, M)
                dists = torch.cdist(chunk, self.memory_bank)
                min_dist, _ = torch.min(dists, dim=1)
                min_dists.append(min_dist)

            min_dists = torch.cat(min_dists).cpu().numpy()

            # Reshape to 2D anomaly map (H, W)
            anomaly_map_coarse = min_dists.reshape(H, W)

            # Upscale anomaly map to original image resolution (256, 256)
            anomaly_map = cv2.resize(anomaly_map_coarse, (IMAGE_SIZE[0], IMAGE_SIZE[1]))

            # Gaussian smoothing
            anomaly_map_smooth = cv2.GaussianBlur(anomaly_map, (9, 9), 2.0)

            # Image-level score: max patch distance
            image_score = float(np.max(anomaly_map_smooth))

            return anomaly_map_smooth, image_score


# ============================================================
# Pipeline Runner
# ============================================================

def run_patchcore_pipeline(coreset_percentage=0.05, device=DEVICE, category="bottle"):
    """Execute PatchCore training, scoring, and evaluation."""
    ensure_dirs()
    print("\n" + "=" * 60)
    print("PATCHCORE EXPERIMENT (Pretrained ResNet-18)")
    print("=" * 60)

    train_ds = MVTecDataset(category=category, split="train", image_size=256, augment=False)
    train_loader = DataLoader(train_ds, batch_size=8, shuffle=False)

    detector = PatchCoreDetector(coreset_percentage=coreset_percentage, device=device)
    detector.fit(train_loader)

    # 1. Compute training scores for threshold
    logger.info("Computing training anomaly scores for threshold...")
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
    logger.info("PatchCore train scores: mean=%.4f, std=%.4f, threshold(k=%.1f)=%.4f",
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

    logger.info("PatchCore Metrics: Image-AUROC=%.4f, Pixel-AUROC=%.4f, F1=%.4f, P=%.4f, R=%.4f",
                auroc, pixel_auroc, f1, prec, rec)
    logger.info("Confusion: TP=%d FP=%d TN=%d FN=%d", tp, fp, tn, fn)

    from utils.config import get_category_config as _gcc
    _cfg_pc = _gcc(category)
    _cfg_pc.ensure_output_dirs()
    _out_pc = _cfg_pc.predictions_dir
    df_res.to_csv(os.path.join(_out_pc, "patchcore_predictions.csv"), index=False)

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
    res = run_patchcore_pipeline(coreset_percentage=0.05)
    print("\nPatchCore Final Metrics:", res["metrics"])

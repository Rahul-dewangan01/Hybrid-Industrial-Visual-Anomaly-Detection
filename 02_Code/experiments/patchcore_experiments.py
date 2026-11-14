"""
patchcore_experiments.py — PatchCore Coreset Size and Backbone Experiments.

Experiments:
  Coreset: PC-CORESET-01/05/10/20
  Backbone: PC-RN18 / PC-RN34 / PC-RN50

Usage:
    python patchcore_experiments.py --experiment PC-CORESET-10 --category bottle
    python patchcore_experiments.py --experiment all_coreset --category all
    python patchcore_experiments.py --experiment all_backbone --category bottle
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
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import pandas as pd
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score
from sklearn.random_projection import SparseRandomProjection

from experiments.experiment_config import (
    PATCHCORE_CORESET_EXPERIMENTS, PATCHCORE_BACKBONE_EXPERIMENTS,
    DEFAULT_CATEGORIES, PILOT_CATEGORY, GLOBAL_SEED, EXPERIMENT_STUDY_DIR,
)
from experiments.experiment_runner import ExperimentRunner, set_global_seed
from deep_learning.dataset import MVTecDataset
from utils.config import DEVICE, THRESHOLD_K, IMAGE_SIZE

logger = logging.getLogger(__name__)


# ============================================================
# Flexible ResNet Feature Extractor (layer2 + layer3)
# ============================================================

class FlexResNetExtractor(nn.Module):
    """Multi-scale feature extractor for ResNet-18/34/50."""

    # Channel counts for layer2 and layer3 per backbone
    _CHANNELS = {
        "resnet18": (128, 256),
        "resnet34": (128, 256),
        "resnet50": (512, 1024),
    }

    def __init__(self, backbone_name: str = "resnet18", device: str = DEVICE):
        super().__init__()
        self.device = device
        self.backbone_name = backbone_name

        if backbone_name == "resnet18":
            backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        elif backbone_name == "resnet34":
            backbone = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)
        elif backbone_name == "resnet50":
            backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        else:
            raise ValueError(f"Unsupported backbone: {backbone_name}")

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
        self.to(device)

        ch2, ch3 = self._CHANNELS[backbone_name]
        self.feature_dim = ch2 + ch3  # e.g. 384 for ResNet-18

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x = self.layer1(x)
        feat2 = self.layer2(x)
        feat3 = self.layer3(feat2)
        feat3_up = F.interpolate(feat3, size=feat2.shape[-2:], mode="bilinear", align_corners=False)
        features = torch.cat([feat2, feat3_up], dim=1)
        features = F.avg_pool2d(features, kernel_size=3, stride=1, padding=1)
        return features


def subsample_coreset(features, percentage, seed=GLOBAL_SEED):
    """Greedy K-Center coreset subsampling, GPU-accelerated."""
    n_samples = features.shape[0]
    n_coreset = max(100, int(n_samples * percentage))
    logger.info("Coreset: selecting %d / %d patches (%.1f%%)...",
                n_coreset, n_samples, percentage * 100)

    if features.shape[1] > 64:
        proj = SparseRandomProjection(n_components=64, random_state=seed)
        fp = proj.fit_transform(features)
    else:
        fp = features

    if torch.cuda.is_available():
        fp_t = torch.from_numpy(fp).float().cuda()
        rng = np.random.RandomState(seed)
        first_idx = int(rng.randint(n_samples))
        sel = [first_idx]
        min_dists = torch.norm(fp_t - fp_t[first_idx], dim=1)

        for step in range(1, n_coreset):
            idx = int(torch.argmax(min_dists).item())
            sel.append(idx)
            new_d = torch.norm(fp_t - fp_t[idx], dim=1)
            min_dists = torch.minimum(min_dists, new_d)
    else:
        rng = np.random.RandomState(seed)
        first_idx = int(rng.randint(n_samples))
        sel = [first_idx]
        min_dists = np.linalg.norm(fp - fp[first_idx], axis=1)

        for step in range(1, n_coreset):
            idx = int(np.argmax(min_dists))
            sel.append(idx)
            new_d = np.linalg.norm(fp - fp[idx], axis=1)
            min_dists = np.minimum(min_dists, new_d)

    return features[sel]


# ============================================================
# PatchCore experiment runner
# ============================================================

def run_patchcore_experiment(experiment_id: str, category: str):
    """Run one PatchCore experiment for one category."""
    all_configs = {**PATCHCORE_CORESET_EXPERIMENTS, **PATCHCORE_BACKBONE_EXPERIMENTS}
    if experiment_id not in all_configs:
        raise ValueError(f"Unknown PatchCore experiment: {experiment_id}")

    cfg = all_configs[experiment_id]
    is_coreset = experiment_id in PATCHCORE_CORESET_EXPERIMENTS
    exp_type = "coreset_experiments" if is_coreset else "backbone_experiments"
    result_dir = os.path.join(EXPERIMENT_STUDY_DIR, "patchcore", exp_type)
    os.makedirs(result_dir, exist_ok=True)

    runner = ExperimentRunner(
        experiment_id=experiment_id,
        model="patchcore",
        experiment_type=f"patchcore/{exp_type}",
        category=category,
        config=cfg,
        seed=GLOBAL_SEED,
    )

    with runner.context():
        set_global_seed(GLOBAL_SEED)
        backbone_name = cfg.get("backbone", "resnet18")
        coreset_pct = cfg.get("coreset_percentage", 0.05)

        # Build extractor
        extractor = FlexResNetExtractor(backbone_name=backbone_name, device=DEVICE)
        extractor.eval()

        # Train loader
        train_ds = MVTecDataset(category=category, split="train", image_size=256, augment=False)
        train_loader = DataLoader(train_ds, batch_size=8, shuffle=False)

        # Build memory bank
        t_fit = time.time()
        patch_list = []
        with torch.no_grad():
            for batch in train_loader:
                x = batch["image"].to(DEVICE)
                feats = extractor(x)
                B, C, H, W = feats.shape
                patches = feats.permute(0, 2, 3, 1).reshape(-1, C).cpu().numpy()
                patch_list.append(patches)

        all_patches = np.concatenate(patch_list, axis=0)
        logger.info("Extracted %d patches of dim %d in %.1fs",
                    all_patches.shape[0], all_patches.shape[1], time.time() - t_fit)

        coreset = subsample_coreset(all_patches, percentage=coreset_pct)
        memory_bank = torch.from_numpy(coreset).float().to(DEVICE)
        logger.info("Memory bank: %s", tuple(memory_bank.shape))
        fit_time = time.time() - t_fit

        def predict_image(x_img):
            with torch.no_grad():
                feats = extractor(x_img)
                _, C, H, W = feats.shape
                patches = feats.permute(0, 2, 3, 1).reshape(-1, C)
                chunk_size = 256
                min_dists = []
                for i in range(0, patches.shape[0], chunk_size):
                    chunk = patches[i:i + chunk_size]
                    dists = torch.cdist(chunk, memory_bank)
                    min_d, _ = torch.min(dists, dim=1)
                    min_dists.append(min_d)
                min_dists = torch.cat(min_dists).cpu().numpy()
                amap_coarse = min_dists.reshape(H, W)
                amap = cv2.resize(amap_coarse, (IMAGE_SIZE[0], IMAGE_SIZE[1]))
                amap_smooth = cv2.GaussianBlur(amap, (9, 9), 2.0)
                score = float(np.max(amap_smooth))
                return amap_smooth, score

        # Threshold from training scores
        train_scores = []
        with torch.no_grad():
            for batch in DataLoader(train_ds, batch_size=1, shuffle=False):
                x = batch["image"].to(DEVICE)
                _, score = predict_image(x)
                train_scores.append(score)

        train_scores = np.array(train_scores)
        threshold = float(np.mean(train_scores) + THRESHOLD_K * np.std(train_scores))
        logger.info("Train scores: mean=%.4f std=%.4f threshold=%.4f",
                    np.mean(train_scores), np.std(train_scores), threshold)

        # Evaluate test set
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

        # Save per-experiment CSV
        result_csv = os.path.join(result_dir, f"{experiment_id}_{category}_results.csv")
        pd.DataFrame([{
            "experiment_id": experiment_id, "category": category,
            "backbone": backbone_name, "coreset_pct": coreset_pct,
            "image_auroc": auroc, "pixel_auroc": pixel_auroc,
            "f1_score": f1, "average_precision": ap,
            "precision": prec, "recall": rec,
            "fit_time_s": fit_time, "inference_time_s": inference_time,
        }]).to_csv(result_csv, index=False, encoding="utf-8")

    return {"image_auroc": auroc, "pixel_auroc": pixel_auroc, "f1_score": f1}


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="PatchCore Experiments")
    parser.add_argument("--experiment", type=str, required=True,
                        help="Experiment ID or 'all_coreset' / 'all_backbone' / 'all'")
    parser.add_argument("--category", type=str, default=PILOT_CATEGORY,
                        help="Category or 'all'")
    args = parser.parse_args()

    if args.experiment == "all_coreset":
        exp_ids = list(PATCHCORE_CORESET_EXPERIMENTS.keys())
    elif args.experiment == "all_backbone":
        exp_ids = list(PATCHCORE_BACKBONE_EXPERIMENTS.keys())
    elif args.experiment == "all":
        exp_ids = list(PATCHCORE_CORESET_EXPERIMENTS.keys()) + list(PATCHCORE_BACKBONE_EXPERIMENTS.keys())
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
                res = run_patchcore_experiment(exp_id, cat)
                print(f"  AUROC={res['image_auroc']:.4f}  Pixel-AUROC={res['pixel_auroc']:.4f}  F1={res['f1_score']:.4f}")
            except Exception as e:
                print(f"  FAILED: {e}")

    print(f"\nResults in: {EXPERIMENT_STUDY_DIR}/patchcore/")

"""
Convolutional Autoencoder for Industrial Anomaly Detection.

Trained strictly on normal training images (104 images).
Reconstruction error serves as both pixel-level anomaly map and
image-level anomaly score.
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
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score, confusion_matrix

from utils.config import (
    OUTPUT_DIR, CHARTS_DIR, THRESHOLD_K,
    ensure_dirs, IMAGE_SIZE, DEVICE, MODELS_DIR,
)
from deep_learning.dataset import MVTecBottleDataset, denormalize

logger = logging.getLogger(__name__)


# ============================================================
# Autoencoder Architecture
# ============================================================

class ConvAutoencoder(nn.Module):
    """4-layer Convolutional Autoencoder for 256x256 RGB images."""

    def __init__(self, latent_dim=128):
        super().__init__()

        # Encoder: 256x256 -> 16x16
        self.encoder = nn.Sequential(
            # 256 -> 128
            nn.Conv2d(3, 32, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.LeakyReLU(0.2, inplace=True),

            # 128 -> 64
            nn.Conv2d(32, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),

            # 64 -> 32
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),

            # 32 -> 16
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
        )

        # Bottleneck: 16x16x256 -> latent -> 16x16x256
        self.bottleneck_enc = nn.Conv2d(256, latent_dim, kernel_size=3, padding=1)
        self.bottleneck_dec = nn.Conv2d(latent_dim, 256, kernel_size=3, padding=1)

        # Decoder: 16x16 -> 256x256
        self.decoder = nn.Sequential(
            # 16 -> 32
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            # 32 -> 64
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            # 64 -> 128
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),

            # 128 -> 256
            nn.ConvTranspose2d(32, 3, kernel_size=4, stride=2, padding=1),
            nn.Sigmoid(),  # Output in [0, 1] range for unnormalized images
        )

    def forward(self, x):
        feat = self.encoder(x)
        latent = self.bottleneck_enc(feat)
        recon_feat = self.bottleneck_dec(latent)
        recon = self.decoder(recon_feat)
        return recon


# ============================================================
# SSIM Loss for PyTorch
# ============================================================

def gaussian_kernel(size=11, sigma=1.5):
    coords = torch.arange(size, dtype=torch.float32) - size // 2
    g = torch.exp(-(coords ** 2) / (2 * sigma ** 2))
    g = g / g.sum()
    kernel2d = g.unsqueeze(1) @ g.unsqueeze(0)
    return kernel2d.unsqueeze(0).unsqueeze(0)


class SSIMLoss(nn.Module):
    """Differentiable SSIM loss for [0, 1] images."""

    def __init__(self, window_size=11, sigma=1.5):
        super().__init__()
        self.window_size = window_size
        k = gaussian_kernel(window_size, sigma)
        self.register_buffer("kernel", k.repeat(3, 1, 1, 1))

    def forward(self, img1, img2):
        c1 = 0.01 ** 2
        c2 = 0.03 ** 2

        mu1 = nn.functional.conv2d(img1, self.kernel, padding=self.window_size // 2, groups=3)
        mu2 = nn.functional.conv2d(img2, self.kernel, padding=self.window_size // 2, groups=3)

        mu1_sq = mu1.pow(2)
        mu2_sq = mu2.pow(2)
        mu1_mu2 = mu1 * mu2

        sigma1_sq = nn.functional.conv2d(img1 * img1, self.kernel, padding=self.window_size // 2, groups=3) - mu1_sq
        sigma2_sq = nn.functional.conv2d(img2 * img2, self.kernel, padding=self.window_size // 2, groups=3) - mu2_sq
        sigma12 = nn.functional.conv2d(img1 * img2, self.kernel, padding=self.window_size // 2, groups=3) - mu1_mu2

        ssim_map = ((2 * mu1_mu2 + c1) * (2 * sigma12 + c2)) / ((mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2))
        return 1.0 - ssim_map.mean()


# ============================================================
# Training
# ============================================================

def train_autoencoder(epochs=30, batch_size=8, lr=1e-3, device=DEVICE, save_dir=None, category="bottle"):
    """Train Convolutional Autoencoder on normal training images for given category."""
    if save_dir is None:
        save_dir = MODELS_DIR
    os.makedirs(save_dir, exist_ok=True)
    model_path = os.path.join(save_dir, f"autoencoder_{category}.pt")

    from deep_learning.dataset import MVTecDataset
    train_ds = MVTecDataset(category=category, split="train", image_size=256, augment=True)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    model = ConvAutoencoder().to(device)
    if os.path.exists(model_path):
        logger.info("Found existing checkpoint at %s, loading saved weights...", model_path)
        ckpt = torch.load(model_path, map_location=device)
        model.load_state_dict(ckpt["model_state_dict"])
        return model, ckpt.get("history", [])

    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    mse_criterion = nn.MSELoss()
    ssim_criterion = SSIMLoss().to(device)

    logger.info("Starting Autoencoder training: %d epochs, %d batches/epoch on %s",
                epochs, len(train_loader), device)

    t0 = time.time()
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        epoch_mse = 0.0
        epoch_ssim = 0.0

        for batch in train_loader:
            x = batch["image"].to(device)
            # Rescale normalized tensor to [0, 1] for reconstruction target
            x_target = denormalize(x).clamp(0, 1)

            optimizer.zero_grad()
            recon = model(x_target)

            loss_mse = mse_criterion(recon, x_target)
            loss_ssim = ssim_criterion(recon, x_target)
            loss = loss_mse + 0.5 * loss_ssim

            loss.backward()
            optimizer.step()

            epoch_loss += loss.item() * x.size(0)
            epoch_mse += loss_mse.item() * x.size(0)
            epoch_ssim += loss_ssim.item() * x.size(0)

        n_samples = len(train_ds)
        loss_avg = epoch_loss / n_samples
        mse_avg = epoch_mse / n_samples
        ssim_avg = epoch_ssim / n_samples

        history.append({"epoch": epoch, "loss": loss_avg, "mse": mse_avg, "ssim_loss": ssim_avg})

        if epoch % 5 == 0 or epoch == epochs:
            logger.info("  Epoch [%d/%d] Loss: %.5f (MSE: %.5f, SSIM_loss: %.5f)",
                        epoch, epochs, loss_avg, mse_avg, ssim_avg)

    elapsed = time.time() - t0
    logger.info("Autoencoder training complete in %.1fs", elapsed)

    torch.save({
        "model_state_dict": model.state_dict(),
        "history": history,
        "epochs": epochs,
    }, model_path)
    logger.info("Model saved to %s", model_path)

    return model, history


# ============================================================
# Anomaly Scoring & Evaluation
# ============================================================

def compute_reconstruction_error(img_tensor, recon_tensor):
    """Compute per-pixel error map and scalar anomaly score."""
    # (3, H, W)
    diff = (img_tensor - recon_tensor).abs().cpu().numpy()
    # Average across RGB channels -> (H, W)
    error_map = np.mean(diff, axis=0)

    # Smooth error map with Gaussian filter
    smoothed_map = cv2.GaussianBlur(error_map, (9, 9), 2.0)

    # Image-level anomaly score: mean of top 1% highest reconstruction errors
    # (robust to small defect localization)
    top_k_pixels = int(0.01 * smoothed_map.size)
    flat_sorted = np.sort(smoothed_map.ravel())
    image_score = float(np.mean(flat_sorted[-top_k_pixels:]))

    return smoothed_map, image_score


def evaluate_autoencoder(model, device=DEVICE, category="bottle"):
    """Evaluate Autoencoder on training normals and test set."""
    model.eval()

    # 1. Score training normals (to determine threshold without test leakage)
    from deep_learning.dataset import MVTecDataset
    train_ds = MVTecDataset(category=category, split="train", image_size=256, augment=False)
    train_loader = DataLoader(train_ds, batch_size=1, shuffle=False)

    train_scores = []
    with torch.no_grad():
        for batch in train_loader:
            x = batch["image"].to(device)
            x_target = denormalize(x).clamp(0, 1)
            recon = model(x_target)
            _, score = compute_reconstruction_error(x_target[0], recon[0])
            train_scores.append(score)

    train_scores = np.array(train_scores)
    mu = np.mean(train_scores)
    sigma = np.std(train_scores)
    threshold = float(mu + THRESHOLD_K * sigma)
    logger.info("Autoencoder train scores: mean=%.5f, std=%.5f, threshold(k=%.1f)=%.5f",
                mu, sigma, THRESHOLD_K, threshold)

    # 2. Score test set
    test_ds = MVTecDataset(category=category, split="test", image_size=256, augment=False)
    test_loader = DataLoader(test_ds, batch_size=1, shuffle=False)

    test_results = []
    anomaly_maps = []
    gt_masks = []
    reconstructions = []
    inputs = []

    with torch.no_grad():
        for i, batch in enumerate(test_loader):
            x = batch["image"].to(device)
            x_target = denormalize(x).clamp(0, 1)
            recon = model(x_target)

            error_map, score = compute_reconstruction_error(x_target[0], recon[0])

            defect_type = batch["category"][0]
            img_id = batch["image_id"][0]
            label = int(batch["label"][0])
            mask = batch["mask"][0, 0].cpu().numpy()

            anomaly_maps.append(error_map)
            gt_masks.append(mask)
            inputs.append(x_target[0].permute(1, 2, 0).cpu().numpy())
            reconstructions.append(recon[0].permute(1, 2, 0).cpu().numpy())

            test_results.append({
                "image_id": img_id,
                "category": defect_type,
                "true_label": label,
                "anomaly_score": score,
                "predicted_label": int(score >= threshold),
            })

    df_test_res = pd.DataFrame(test_results)
    y_true = df_test_res["true_label"].values
    y_scores = df_test_res["anomaly_score"].values
    y_pred = df_test_res["predicted_label"].values

    # Metrics
    auroc = roc_auc_score(y_true, y_scores)
    ap = average_precision_score(y_true, y_scores)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    # Pixel-level AUROC across all test images
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

    logger.info("Autoencoder Results: Image-AUROC=%.4f, Pixel-AUROC=%.4f, F1=%.4f, P=%.4f, R=%.4f",
                auroc, pixel_auroc, f1, prec, rec)
    logger.info("Confusion: TP=%d FP=%d TN=%d FN=%d", tp, fp, tn, fn)

    # Save predictions
    from utils.config import get_category_config
    _cfg = get_category_config(category)
    _cfg.ensure_output_dirs()
    df_test_res.to_csv(os.path.join(_cfg.predictions_dir, "autoencoder_predictions.csv"), index=False)

    return {
        "metrics": metrics,
        "df_results": df_test_res,
        "test_scores": y_scores,
        "train_scores": train_scores,
        "anomaly_maps": anomaly_maps,
        "gt_masks": gt_masks,
        "inputs": inputs,
        "reconstructions": reconstructions,
    }


def run_autoencoder_pipeline(epochs=25, device=DEVICE, category="bottle"):
    """Full Autoencoder train and evaluation pipeline."""
    from utils.config import get_category_config
    cfg = get_category_config(category)
    cfg.ensure_output_dirs()
    print("\n" + "=" * 60)
    print(f"CONVOLUTIONAL AUTOENCODER EXPERIMENT  [{category.upper()}]")
    print("=" * 60)

    model, history = train_autoencoder(epochs=epochs, device=device,
                                       save_dir=str(cfg.model_path.parent) if hasattr(cfg.model_path, "parent") else os.path.dirname(str(cfg.model_path)),
                                       category=category)
    res = evaluate_autoencoder(model, device=device, category=category)
    return res


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    res = run_autoencoder_pipeline(epochs=20)
    print("\nFinal Metrics:", res["metrics"])

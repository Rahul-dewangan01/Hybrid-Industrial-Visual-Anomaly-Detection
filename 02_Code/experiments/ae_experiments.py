"""
ae_experiments.py — Autoencoder Loss, Architecture, and Hyperparameter Experiments.

Experiments:
  Loss:
    AE-01: MSE only
    AE-02: MAE only
    AE-03: SSIM only
    AE-04: MSE + SSIM (current production baseline, re-run at 50 epochs)
    AE-05: MSE + Gradient Loss

  Architecture:
    AE-ARCH-3L: 3-level encoder/decoder
    AE-ARCH-4L: 4-level (baseline)
    AE-ARCH-5L: 5-level encoder/decoder
    AE-LATENT-64/128/256: latent dimension ablation

  Hyperparameters:
    AE-LR-1e4, AE-LR-5e4: learning rate
    AE-EP-20, AE-EP-100: epoch count
    AE-OPT-ADAMW: optimizer

Usage:
    python ae_experiments.py --experiment AE-01 --category bottle
    python ae_experiments.py --experiment AE-01 --category all
    python ae_experiments.py --experiment all_loss --category bottle  # all 5 loss experiments
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
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score
from sklearn.metrics import precision_score, recall_score

from experiments.experiment_config import (
    AE_LOSS_EXPERIMENTS, AE_ARCH_EXPERIMENTS, AE_HYPERPARAM_EXPERIMENTS,
    DEFAULT_CATEGORIES, PILOT_CATEGORY, GLOBAL_SEED, EXPERIMENT_STUDY_DIR,
)
from experiments.experiment_runner import ExperimentRunner, set_global_seed
from deep_learning.dataset import MVTecDataset, denormalize
from deep_learning.autoencoder import ConvAutoencoder, SSIMLoss, compute_reconstruction_error
from utils.config import DEVICE, THRESHOLD_K, get_category_config

logger = logging.getLogger(__name__)

# ============================================================
# Loss Functions
# ============================================================

class GradientLoss(nn.Module):
    """Sobel-based gradient magnitude loss."""

    def __init__(self):
        super().__init__()
        # Sobel kernels
        kx = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32)
        ky = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=torch.float32)
        # (1, 1, 3, 3) for depthwise conv
        self.register_buffer("kx", kx.view(1, 1, 3, 3))
        self.register_buffer("ky", ky.view(1, 1, 3, 3))

    def _sobel_magnitude(self, img):
        """img: (B, C, H, W) in [0,1]. Returns gradient magnitude (B, C, H, W)."""
        B, C, H, W = img.shape
        # Process each channel independently
        img_flat = img.view(B * C, 1, H, W)
        gx = F.conv2d(img_flat, self.kx, padding=1)
        gy = F.conv2d(img_flat, self.ky, padding=1)
        mag = torch.sqrt(gx ** 2 + gy ** 2 + 1e-8)
        return mag.view(B, C, H, W)

    def forward(self, img1, img2):
        """L_grad = mean |G(img1) - G(img2)|"""
        g1 = self._sobel_magnitude(img1)
        g2 = self._sobel_magnitude(img2)
        return (g1 - g2).abs().mean()


def build_loss_fn(loss_name: str, alpha: float, beta: float, gamma: float, device: str):
    """
    Build a composite loss function.

    Returns a callable: loss_fn(recon, target) -> scalar tensor

    Training loss ≠ inference anomaly score (computed separately).
    """
    mse_fn = nn.MSELoss()
    mae_fn = nn.L1Loss()
    ssim_fn = SSIMLoss().to(device)
    grad_fn = GradientLoss().to(device)

    if loss_name == "mse":
        def fn(r, t): return alpha * mse_fn(r, t)
    elif loss_name == "mae":
        def fn(r, t): return alpha * mae_fn(r, t)
    elif loss_name == "ssim":
        def fn(r, t): return beta * ssim_fn(r, t)
    elif loss_name == "mse+ssim":
        def fn(r, t): return alpha * mse_fn(r, t) + beta * ssim_fn(r, t)
    elif loss_name == "mse+gradient":
        def fn(r, t): return alpha * mse_fn(r, t) + gamma * grad_fn(r, t)
    else:
        raise ValueError(f"Unknown loss_name: {loss_name}")

    return fn


# ============================================================
# Flexible Autoencoder Architecture
# ============================================================

class FlexConvAutoencoder(nn.Module):
    """
    Configurable Convolutional Autoencoder.
    Supports 3, 4, or 5 encoder/decoder levels and variable latent dim.

    Input: (B, 3, 256, 256) in [0, 1]
    """

    # Channel progression per level
    _CHANNELS = {
        3: [32, 64, 128],
        4: [32, 64, 128, 256],
        5: [32, 64, 128, 256, 512],
    }

    def __init__(self, encoder_levels: int = 4, latent_dim: int = 128):
        super().__init__()
        assert encoder_levels in (3, 4, 5), "encoder_levels must be 3, 4, or 5"
        channels = self._CHANNELS[encoder_levels]

        # ----- Encoder -----
        enc_layers = []
        in_ch = 3
        for out_ch in channels:
            enc_layers += [
                nn.Conv2d(in_ch, out_ch, kernel_size=4, stride=2, padding=1),
                nn.BatchNorm2d(out_ch),
                nn.LeakyReLU(0.2, inplace=True),
            ]
            in_ch = out_ch
        self.encoder = nn.Sequential(*enc_layers)
        self._enc_out_ch = channels[-1]

        # ----- Bottleneck -----
        self.bottleneck_enc = nn.Conv2d(self._enc_out_ch, latent_dim, kernel_size=3, padding=1)
        self.bottleneck_dec = nn.Conv2d(latent_dim, self._enc_out_ch, kernel_size=3, padding=1)

        # ----- Decoder -----
        dec_channels = list(reversed(channels))  # e.g. [256, 128, 64, 32]
        dec_layers = []
        in_ch = dec_channels[0]
        for i, out_ch in enumerate(dec_channels[1:]):
            dec_layers += [
                nn.ConvTranspose2d(in_ch, out_ch, kernel_size=4, stride=2, padding=1),
                nn.BatchNorm2d(out_ch),
                nn.ReLU(inplace=True),
            ]
            in_ch = out_ch
        # Final layer: out → 3 channels + Sigmoid
        dec_layers += [
            nn.ConvTranspose2d(in_ch, 3, kernel_size=4, stride=2, padding=1),
            nn.Sigmoid(),
        ]
        self.decoder = nn.Sequential(*dec_layers)

    def forward(self, x):
        feat = self.encoder(x)
        latent = self.bottleneck_enc(feat)
        recon_feat = self.bottleneck_dec(latent)
        return self.decoder(recon_feat)


# ============================================================
# Training & Evaluation
# ============================================================

def train_ae_experiment(
    category: str,
    experiment_id: str,
    loss_name: str,
    alpha: float,
    beta: float,
    gamma: float,
    epochs: int,
    lr: float,
    batch_size: int,
    optimizer_name: str,
    encoder_levels: int,
    latent_dim: int,
    device: str,
    checkpoint_path: str,
    force_retrain: bool = False,
):
    """Train autoencoder for one experiment configuration.

    Returns: (model, history, training_time_s)
    """
    # Dataset
    train_ds = MVTecDataset(category=category, split="train", image_size=256, augment=True)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=0, pin_memory=True)

    # Model
    model = FlexConvAutoencoder(encoder_levels=encoder_levels, latent_dim=latent_dim).to(device)

    # Resume if checkpoint exists and not forcing retrain
    if os.path.exists(checkpoint_path) and not force_retrain:
        logger.info("Loading existing checkpoint: %s", checkpoint_path)
        ckpt = torch.load(checkpoint_path, map_location=device)
        model.load_state_dict(ckpt["model_state_dict"])
        return model, ckpt.get("history", []), 0.0

    # Loss function
    loss_fn = build_loss_fn(loss_name, alpha, beta, gamma, device)

    # Optimizer
    if optimizer_name == "adam":
        optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    elif optimizer_name == "adamw":
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_name}")

    logger.info("Training: category=%s, exp=%s, loss=%s, epochs=%d, lr=%s, device=%s",
                category, experiment_id, loss_name, epochs, lr, device)

    t0 = time.time()
    history = []

    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        for batch in train_loader:
            x = batch["image"].to(device)
            x_target = denormalize(x).clamp(0, 1)
            optimizer.zero_grad()
            recon = model(x_target)
            loss = loss_fn(recon, x_target)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * x.size(0)

        avg_loss = epoch_loss / len(train_ds)
        history.append({"epoch": epoch, "loss": avg_loss})

        if epoch % 10 == 0 or epoch == epochs:
            logger.info("  Epoch [%d/%d] Loss: %.6f", epoch, epochs, avg_loss)

    training_time = time.time() - t0
    logger.info("Training complete in %.1fs", training_time)

    torch.save({
        "model_state_dict": model.state_dict(),
        "history": history,
        "epochs": epochs,
        "experiment_id": experiment_id,
        "category": category,
        "config": {
            "loss_name": loss_name, "alpha": alpha, "beta": beta, "gamma": gamma,
            "encoder_levels": encoder_levels, "latent_dim": latent_dim,
            "lr": lr, "optimizer": optimizer_name,
        },
    }, checkpoint_path)
    logger.info("Checkpoint saved: %s", checkpoint_path)

    return model, history, training_time


def evaluate_ae_experiment(model, category: str, device: str):
    """
    Evaluate trained autoencoder on train + test split.

    Inference anomaly score = mean of top 1% reconstruction error pixels.
    (This is DISTINCT from training loss — see architecture audit.)

    Returns: metrics dict, timing info
    """
    model.eval()

    # Score training normals → compute threshold (NO TEST LEAKAGE)
    train_ds = MVTecDataset(category=category, split="train", image_size=256, augment=False)
    train_loader = DataLoader(train_ds, batch_size=1, shuffle=False)

    train_scores = []
    t_inf_start = time.time()
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
    logger.info("Train scores: mean=%.5f std=%.5f threshold(k=%.1f)=%.5f",
                mu, sigma, THRESHOLD_K, threshold)

    # Evaluate test set
    test_ds = MVTecDataset(category=category, split="test", image_size=256, augment=False)
    test_loader = DataLoader(test_ds, batch_size=1, shuffle=False)

    test_results = []
    anomaly_maps = []
    gt_masks = []

    with torch.no_grad():
        for batch in test_loader:
            x = batch["image"].to(device)
            x_target = denormalize(x).clamp(0, 1)
            recon = model(x_target)
            error_map, score = compute_reconstruction_error(x_target[0], recon[0])
            label = int(batch["label"][0])
            mask = batch["mask"][0, 0].cpu().numpy()
            anomaly_maps.append(error_map)
            gt_masks.append(mask)
            test_results.append({
                "true_label": label,
                "anomaly_score": score,
                "predicted_label": int(score >= threshold),
            })

    inference_time = time.time() - t_inf_start

    y_true = np.array([r["true_label"] for r in test_results])
    y_scores = np.array([r["anomaly_score"] for r in test_results])
    y_pred = np.array([r["predicted_label"] for r in test_results])

    auroc = float(roc_auc_score(y_true, y_scores))
    ap = float(average_precision_score(y_true, y_scores))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))

    # Pixel-level AUROC
    all_gt = np.concatenate([m.ravel() for m in gt_masks]).astype(int)
    all_scores = np.concatenate([m.ravel() for m in anomaly_maps])
    if len(np.unique(all_gt)) >= 2:
        pixel_auroc = float(roc_auc_score(all_gt, all_scores))
    else:
        pixel_auroc = float("nan")

    logger.info("Image-AUROC=%.4f Pixel-AUROC=%.4f AP=%.4f F1=%.4f P=%.4f R=%.4f",
                auroc, pixel_auroc, ap, f1, prec, rec)

    return {
        "image_auroc": auroc,
        "pixel_auroc": pixel_auroc,
        "average_precision": ap,
        "f1_score": f1,
        "precision": prec,
        "recall": rec,
        "training_samples": len(train_ds),
        "test_samples": len(test_ds),
        "inference_time_s": inference_time,
        "threshold": threshold,
        "train_scores": train_scores,
    }


# ============================================================
# Run one experiment for one category
# ============================================================

def run_ae_experiment(experiment_id: str, category: str, force_retrain: bool = False):
    """
    Run one AE experiment (from AE_LOSS_EXPERIMENTS, AE_ARCH_EXPERIMENTS, or
    AE_HYPERPARAM_EXPERIMENTS) for one category.
    """
    # Look up config
    all_configs = {**AE_LOSS_EXPERIMENTS, **AE_ARCH_EXPERIMENTS, **AE_HYPERPARAM_EXPERIMENTS}
    if experiment_id not in all_configs:
        raise ValueError(f"Unknown experiment ID: {experiment_id}. "
                         f"Valid: {list(all_configs.keys())}")

    cfg = all_configs[experiment_id]

    # Determine experiment type subdir
    if experiment_id in AE_LOSS_EXPERIMENTS:
        exp_type = "loss_experiments"
    elif experiment_id in AE_ARCH_EXPERIMENTS:
        exp_type = "architecture_experiments"
    else:
        exp_type = "hyperparameter_experiments"

    result_dir = os.path.join(EXPERIMENT_STUDY_DIR, "autoencoder", exp_type)
    os.makedirs(result_dir, exist_ok=True)

    runner = ExperimentRunner(
        experiment_id=experiment_id,
        model="autoencoder",
        experiment_type=f"autoencoder/{exp_type}",
        category=category,
        config=cfg,
        seed=GLOBAL_SEED,
    )

    with runner.context():
        # Training
        model, history, train_time = train_ae_experiment(
            category=category,
            experiment_id=experiment_id,
            loss_name=cfg.get("loss", "mse+ssim"),
            alpha=cfg.get("alpha", 1.0),
            beta=cfg.get("beta", 0.5),
            gamma=cfg.get("gamma", 0.0),
            epochs=cfg.get("epochs", 50),
            lr=cfg.get("lr", 1e-3),
            batch_size=cfg.get("batch_size", 8),
            optimizer_name=cfg.get("optimizer", "adam"),
            encoder_levels=cfg.get("encoder_levels", 4),
            latent_dim=cfg.get("latent_dim", 128),
            device=DEVICE,
            checkpoint_path=runner.checkpoint_path(),
            force_retrain=force_retrain,
        )

        # Evaluation
        metrics = evaluate_ae_experiment(model, category=category, device=DEVICE)

        # Log to master CSV
        runner.log_metrics(
            image_auroc=metrics["image_auroc"],
            pixel_auroc=metrics["pixel_auroc"],
            average_precision=metrics["average_precision"],
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1_score=metrics["f1_score"],
            training_samples=metrics["training_samples"],
            test_samples=metrics["test_samples"],
            training_time_s=train_time,
            inference_time_s=metrics["inference_time_s"],
        )

        # Save per-experiment CSV
        import pandas as pd
        result_csv = os.path.join(result_dir, f"{experiment_id}_{category}_results.csv")
        pd.DataFrame([{
            "experiment_id": experiment_id,
            "category": category,
            "description": cfg.get("description", ""),
            "image_auroc": metrics["image_auroc"],
            "pixel_auroc": metrics["pixel_auroc"],
            "f1_score": metrics["f1_score"],
            "average_precision": metrics["average_precision"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "training_time_s": train_time,
            "inference_time_s": metrics["inference_time_s"],
            "threshold": metrics["threshold"],
        }]).to_csv(result_csv, index=False, encoding="utf-8")
        logger.info("Per-experiment results saved: %s", result_csv)

    return metrics


# ============================================================
# CLI Entry Point
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(description="Autoencoder Experiments")
    parser.add_argument(
        "--experiment", type=str, required=True,
        help="Experiment ID (e.g., AE-01) or 'all_loss' / 'all_arch' / 'all_hyperparam' / 'all'",
    )
    parser.add_argument(
        "--category", type=str, default=PILOT_CATEGORY,
        help="Category name or 'all' to run all 12 categories",
    )
    parser.add_argument(
        "--force-retrain", action="store_true",
        help="Force retraining even if checkpoint exists",
    )
    args = parser.parse_args()

    # Resolve experiment IDs
    if args.experiment == "all_loss":
        exp_ids = list(AE_LOSS_EXPERIMENTS.keys())
    elif args.experiment == "all_arch":
        exp_ids = list(AE_ARCH_EXPERIMENTS.keys())
    elif args.experiment == "all_hyperparam":
        exp_ids = list(AE_HYPERPARAM_EXPERIMENTS.keys())
    elif args.experiment == "all":
        exp_ids = (list(AE_LOSS_EXPERIMENTS.keys()) +
                   list(AE_ARCH_EXPERIMENTS.keys()) +
                   list(AE_HYPERPARAM_EXPERIMENTS.keys()))
    else:
        exp_ids = [args.experiment]

    # Resolve categories
    categories = DEFAULT_CATEGORIES if args.category == "all" else [args.category]

    total = len(exp_ids) * len(categories)
    done = 0
    for exp_id in exp_ids:
        for cat in categories:
            done += 1
            print(f"\n[{done}/{total}] Running {exp_id} on {cat}...")
            try:
                result = run_ae_experiment(exp_id, cat, force_retrain=args.force_retrain)
                print(f"  Image-AUROC={result['image_auroc']:.4f}  "
                      f"Pixel-AUROC={result['pixel_auroc']:.4f}  "
                      f"F1={result['f1_score']:.4f}")
            except Exception as e:
                print(f"  FAILED: {e}")

    print(f"\nDone. Results saved to: {EXPERIMENT_STUDY_DIR}")

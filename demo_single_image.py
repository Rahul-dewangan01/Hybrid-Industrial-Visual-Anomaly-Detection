"""
demo_single_image.py — Jury Live Demo
======================================
Run the full anomaly detection pipeline on a single image:
  ConvAutoencoder  +  PatchCore  +  PaDiM  →  Hybrid Score & Verdict

Usage
-----
  python demo_single_image.py --category bottle
  python demo_single_image.py --category bottle --image_path "01_Dataset/MVTec_AD/bottle/test/broken_large/000.png"
  python demo_single_image.py --category bottle --image_path "path/to/any/custom/image.jpg"

Arguments
---------
  --category    MVTec AD category name (default: bottle)
  --image_path  Path to test image (default: first test/broken_large image for the category)
  --no_display  Save output but do not call plt.show() (useful in headless env)

Output
------
  Prints a results table to the terminal.
  Saves a 5-panel figure to demo_output/ and displays it.
"""

import argparse
import os
import sys
import glob
import time
import warnings

warnings.filterwarnings("ignore")

# ── Path setup ────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CODE_ROOT = os.path.join(PROJECT_ROOT, "02_Code")
sys.path.insert(0, CODE_ROOT)
sys.path.insert(0, PROJECT_ROOT)

import cv2
import numpy as np
import torch
from torch.utils.data import DataLoader
import matplotlib
matplotlib.use("TkAgg")          # works in VSCode / interactive terminals
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Project imports ───────────────────────────────────────────
from utils.config import DEVICE, IMAGE_SIZE, MODELS_DIR
from deep_learning.dataset import MVTecDataset, denormalize, get_transforms
from deep_learning.autoencoder import ConvAutoencoder, compute_reconstruction_error
from deep_learning.patchcore import PatchCoreDetector
from deep_learning.padim import PaDiMDetector


# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════

def load_and_preprocess(image_path: str, image_size=256):
    """Load an image file and return (rgb_uint8, normalized_tensor [1,3,H,W])."""
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise FileNotFoundError(f"Cannot open image: {image_path}")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    sz = image_size if isinstance(image_size, int) else image_size[0]
    img_resized = cv2.resize(img_rgb, (sz, sz))

    # ImageNet-normalized tensor for PatchCore / PaDiM
    tfm = get_transforms(image_size=sz, augment=False)
    tensor = tfm(img_resized).unsqueeze(0)          # (1,3,H,W)
    return img_resized, tensor


def normalize_map(heatmap: np.ndarray) -> np.ndarray:
    """Normalize heatmap to [0, 1]."""
    mn, mx = heatmap.min(), heatmap.max()
    if mx - mn < 1e-8:
        return np.zeros_like(heatmap)
    return (heatmap - mn) / (mx - mn)


def overlay_heatmap(rgb_img: np.ndarray, heatmap: np.ndarray, alpha: float = 0.55) -> np.ndarray:
    """Overlay a [0,1] heatmap onto an RGB image."""
    hm_uint8 = (heatmap * 255).astype(np.uint8)
    colored = cv2.applyColorMap(hm_uint8, cv2.COLORMAP_JET)
    colored_rgb = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
    overlay = (alpha * colored_rgb + (1 - alpha) * rgb_img).astype(np.uint8)
    return overlay


def pick_default_image(category: str) -> str:
    """Return the first broken/defective test image for the given category."""
    test_root = os.path.join(PROJECT_ROOT, "01_Dataset", "MVTec_AD", category, "test")
    # Prefer a defective sub-folder (anything except 'good')
    for subdir in sorted(os.listdir(test_root)):
        if subdir == "good":
            continue
        folder = os.path.join(test_root, subdir)
        imgs = sorted(glob.glob(os.path.join(folder, "*.png")) +
                      glob.glob(os.path.join(folder, "*.jpg")))
        if imgs:
            return imgs[0]
    # Fallback: good image
    good_imgs = sorted(glob.glob(os.path.join(test_root, "good", "*.png")))
    if good_imgs:
        return good_imgs[0]
    raise FileNotFoundError(f"No test images found for category '{category}'")


# ══════════════════════════════════════════════════════════════
# Model Loading / Fitting
# ══════════════════════════════════════════════════════════════

def load_autoencoder(category: str, device: torch.device, arch: str = "4L"):
    """Load the saved ConvAutoencoder checkpoint (4L baseline or 5L deeper)."""
    if arch.upper() in ("5L", "5"):
        ckpt_5l = os.path.join(PROJECT_ROOT, "03_Results", "experimental_study", "checkpoints",
                               f"AE-ARCH-5L_{category}", f"AE-ARCH-5L_{category}.pt")
        if os.path.exists(ckpt_5l):
            from experiments.ae_experiments import FlexConvAutoencoder
            model = FlexConvAutoencoder(encoder_levels=5, latent_dim=128).to(device)
            ckpt = torch.load(ckpt_5l, map_location=device, weights_only=False)
            model.load_state_dict(ckpt["model_state_dict"])
            model.eval()
            print(f"  [ConvAE-5L] Loaded 5-Level deeper architecture from {os.path.basename(ckpt_5l)}")
            return model, "5L", 0.1853
        else:
            print(f"  [ConvAE]    5L checkpoint not found for {category}, falling back to 4L baseline.")

    ckpt_path = os.path.join(PROJECT_ROOT, "04_Models", f"autoencoder_{category}.pt")
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(
            f"ConvAE checkpoint not found: {ckpt_path}\n"
            f"Run 'python 02_Code/run_single_category.py --category {category}' first."
        )
    model = ConvAutoencoder(latent_dim=128).to(device)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    print(f"  [ConvAE-4L] Loaded 4-Level baseline checkpoint from {os.path.basename(ckpt_path)}")
    return model, "4L", None


def build_train_loader(category: str, batch_size: int = 8) -> DataLoader:
    """Build the training DataLoader (normal images only)."""
    ds = MVTecDataset(category=category, split="train", image_size=256, augment=False)
    return DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=0)


def get_or_fit_patchcore(train_loader: DataLoader, category: str, device: torch.device) -> PatchCoreDetector:
    pc = PatchCoreDetector(coreset_percentage=0.05, device=device)
    cache_path = os.path.join(PROJECT_ROOT, "04_Models", f"cache_patchcore_{category}.pt")
    if os.path.exists(cache_path):
        print(f"  [PatchCore] Loaded cached memory bank from {os.path.basename(cache_path)}")
        data = torch.load(cache_path, map_location=device)
        pc.memory_bank = data["memory_bank"].to(device)
        return pc

    print("  [PatchCore] Fitting on training images …", end="", flush=True)
    t0 = time.time()
    pc.fit(train_loader)
    print(f" done ({time.time()-t0:.1f}s)")
    torch.save({"memory_bank": pc.memory_bank.cpu()}, cache_path)
    pc.memory_bank = pc.memory_bank.to(device)
    return pc


def get_or_fit_padim(train_loader: DataLoader, category: str, device: torch.device) -> PaDiMDetector:
    pd_model = PaDiMDetector(n_components=100, device=device)
    cache_path = os.path.join(PROJECT_ROOT, "04_Models", f"cache_padim_{category}.pt")
    if os.path.exists(cache_path):
        print(f"  [PaDiM]     Loaded cached Gaussian parameters from {os.path.basename(cache_path)}")
        data = torch.load(cache_path, map_location="cpu")
        pd_model.mean = data["mean"]
        pd_model.inv_cov = data["inv_cov"]
        return pd_model

    print("  [PaDiM]     Fitting on training images …", end="", flush=True)
    t0 = time.time()
    pd_model.fit(train_loader)
    print(f" done ({time.time()-t0:.1f}s)")
    torch.save({"mean": pd_model.mean, "inv_cov": pd_model.inv_cov}, cache_path)
    return pd_model


# ══════════════════════════════════════════════════════════════
# Inference
# ══════════════════════════════════════════════════════════════

def run_autoencoder(model: ConvAutoencoder, tensor: torch.Tensor, device: torch.device):
    """Return (error_map [H,W], image_score float, reconstruction [H,W,3])."""
    model.eval()
    with torch.no_grad():
        x = tensor.to(device)
        # AE is trained on [0,1] images (denormalized)
        x_01 = denormalize(x).clamp(0, 1)
        recon = model(x_01)
        error_map, score = compute_reconstruction_error(x_01[0], recon[0])
        recon_rgb = recon[0].permute(1, 2, 0).cpu().numpy()
    return error_map, score, recon_rgb


def run_patchcore(pc: PatchCoreDetector, tensor: torch.Tensor):
    """Return (anomaly_map [H,W], image_score float)."""
    result = pc.predict_image(tensor.to(pc.device))
    if isinstance(result, tuple):
        anomaly_map, score = result
    else:
        anomaly_map = result
        score = float(anomaly_map.max())
    if isinstance(anomaly_map, torch.Tensor):
        anomaly_map = anomaly_map.cpu().numpy()
    return anomaly_map, float(score)


def run_padim(pd_model: PaDiMDetector, tensor: torch.Tensor):
    """Return (anomaly_map [H,W], image_score float)."""
    result = pd_model.predict_image(tensor.to(pd_model.device))
    if isinstance(result, tuple):
        anomaly_map, score = result
    else:
        anomaly_map = result
        score = float(anomaly_map.max())
    if isinstance(anomaly_map, torch.Tensor):
        anomaly_map = anomaly_map.cpu().numpy()
    return anomaly_map, float(score)


# ══════════════════════════════════════════════════════════════
# Thresholds and Calibrated Scoring
# ══════════════════════════════════════════════════════════════
# Optimal thresholds derived from training set / validation calibration
DEFAULT_THRESHOLDS = {
    "bottle":      {"ae": 0.2820, "pc": 1.85, "padim": 18.00},
    "cable":       {"ae": 0.2900, "pc": 1.70, "padim": 16.00},
    "capsule":     {"ae": 0.2850, "pc": 1.80, "padim": 17.50},
    "carpet":      {"ae": 0.2800, "pc": 1.65, "padim": 15.00},
    "grid":        {"ae": 0.2750, "pc": 1.60, "padim": 14.50},
    "hazelnut":    {"ae": 0.2850, "pc": 1.80, "padim": 17.00},
    "leather":     {"ae": 0.2800, "pc": 1.65, "padim": 15.50},
    "metal_nut":   {"ae": 0.2850, "pc": 1.75, "padim": 16.50},
    "screw":       {"ae": 0.2900, "pc": 1.80, "padim": 18.00},
    "tile":        {"ae": 0.2750, "pc": 1.60, "padim": 15.00},
    "toothbrush":  {"ae": 0.2850, "pc": 1.70, "padim": 16.00},
    "transistor":  {"ae": 0.2900, "pc": 1.75, "padim": 17.00},
}

# ACOMA Optimized weights: AE=0.20, PatchCore=0.40, PaDiM=0.40
AE_WEIGHT = 0.20
PC_WEIGHT = 0.40
PD_WEIGHT = 0.40


def get_thresholds(category: str):
    return DEFAULT_THRESHOLDS.get(category, {"ae": 0.2820, "pc": 1.85, "padim": 18.00})


def evaluate_hybrid(ae_score: float, pc_score: float, pd_score: float,
                    ae_map: np.ndarray, pc_map: np.ndarray, pd_map: np.ndarray,
                    category: str, ae_th_override: float = None):
    """
    Evaluate against calibrated thresholds and compute hybrid decision.
    """
    th = get_thresholds(category).copy()
    if ae_th_override is not None:
        th["ae"] = ae_th_override

    ae_vote = int(ae_score >= th["ae"])
    pc_vote = int(pc_score >= th["pc"])
    pd_vote = int(pd_score >= th["padim"])

    # Normalized ratio against threshold (1.0 = exactly at threshold)
    ae_ratio = ae_score / (th["ae"] + 1e-8)
    pc_ratio = pc_score / (th["pc"] + 1e-8)
    pd_ratio = pd_score / (th["padim"] + 1e-8)

    # Weighted ratio
    weighted_ratio = (AE_WEIGHT * ae_ratio + PC_WEIGHT * pc_ratio + PD_WEIGHT * pd_ratio)
    
    # Majority vote and ratio both agree
    total_votes = ae_vote + pc_vote + pd_vote
    is_defective = (pc_vote + pd_vote >= 1 and weighted_ratio >= 1.0) or (total_votes >= 2)
    verdict = "DEFECTIVE" if is_defective else "NORMAL"

    # Fused heatmap
    ae_nm = normalize_map(ae_map)
    pc_nm = normalize_map(pc_map)
    pd_nm = normalize_map(pd_map)
    fused_map = AE_WEIGHT * ae_nm + PC_WEIGHT * pc_nm + PD_WEIGHT * pd_nm

    return {
        "verdict": verdict,
        "is_defective": is_defective,
        "weighted_ratio": weighted_ratio,
        "fused_map": fused_map,
        "ae": {"score": ae_score, "th": th["ae"], "vote": ae_vote, "ratio": ae_ratio},
        "pc": {"score": pc_score, "th": th["pc"], "vote": pc_vote, "ratio": pc_ratio},
        "pd": {"score": pd_score, "th": th["padim"], "vote": pd_vote, "ratio": pd_ratio},
    }


# ══════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════

def visualize(image_path: str, img_rgb: np.ndarray,
              ae_map: np.ndarray, pc_map: np.ndarray, pd_map: np.ndarray,
              eval_res: dict, category: str, save_path: str, no_display: bool):

    verdict = eval_res["verdict"]
    verdict_color = "#e63946" if verdict == "DEFECTIVE" else "#2a9d8f"

    fig, axes = plt.subplots(1, 5, figsize=(22, 5))
    fig.patch.set_facecolor("#111827")

    titles = [
        "Input Image",
        "ConvAE Reconstruction",
        "PatchCore Heatmap",
        "PaDiM Heatmap",
        f"Hybrid Decision: {verdict}",
    ]
    maps_to_show = [
        img_rgb,
        overlay_heatmap(img_rgb, normalize_map(ae_map)),
        overlay_heatmap(img_rgb, normalize_map(pc_map)),
        overlay_heatmap(img_rgb, normalize_map(pd_map)),
        overlay_heatmap(img_rgb, eval_res["fused_map"]),
    ]
    
    ae_v = "DEFECT" if eval_res['ae']['vote'] else "NORMAL"
    pc_v = "DEFECT" if eval_res['pc']['vote'] else "NORMAL"
    pd_v = "DEFECT" if eval_res['pd']['vote'] else "NORMAL"

    subtitles = [
        f"Category: {category}",
        f"Score: {eval_res['ae']['score']:.4f} (Thr: {eval_res['ae']['th']:.4f}) [{ae_v}]",
        f"Score: {eval_res['pc']['score']:.3f} (Thr: {eval_res['pc']['th']:.2f}) [{pc_v}]",
        f"Score: {eval_res['pd']['score']:.2f} (Thr: {eval_res['pd']['th']:.1f}) [{pd_v}]",
        f"Ratio: {eval_res['weighted_ratio']:.2f}x (Weighted Fusion)",
    ]

    for i, (ax, title, img, sub) in enumerate(zip(axes, titles, maps_to_show, subtitles)):
        ax.imshow(img)
        ax.axis("off")
        fc = verdict_color if i == 4 else "white"
        ax.set_title(title, color=fc, fontsize=11, fontweight="bold", pad=4)
        ax.set_xlabel(sub, color="#9ca3af", fontsize=8)

    # Verdict banner
    fig.text(0.5, 0.01,
             f"VERDICT: {verdict}  |  Weighted Ratio = {eval_res['weighted_ratio']:.2f}x  |  "
             f"AE×{AE_WEIGHT:.2f}  PC×{PC_WEIGHT:.2f}  PD×{PD_WEIGHT:.2f}  |  "
             f"File: {os.path.basename(image_path)}",
             ha="center", va="bottom", fontsize=10,
             color=verdict_color, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.3", fc="#1f2937", ec=verdict_color, lw=2))

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\n  Figure saved → {save_path}")

    if not no_display:
        plt.show()
    plt.close()


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Anomaly Detection Demo — Single Image")
    parser.add_argument("--category",   default="bottle",
                        help="MVTec AD category (default: bottle)")
    parser.add_argument("--arch",       default="4L", choices=["4L", "5L"],
                        help="ConvAE depth: 4L (default baseline) or 5L (deeper bottleneck)")
    parser.add_argument("--image_path", default=None,
                        help="Path to the test image (default: first defective test image)")
    parser.add_argument("--simulate_network", action="store_true",
                        help="Simulate Computer Networks transmission (JPEG compression & latency)")
    parser.add_argument("--no_display", action="store_true",
                        help="Do not call plt.show(); only save figure")
    args = parser.parse_args()

    category = args.category.lower()
    device   = torch.device(DEVICE if torch.cuda.is_available() else "cpu")

    # ── Resolve image path ────────────────────────────────────
    if args.image_path:
        image_path = args.image_path
    else:
        image_path = pick_default_image(category)

    print("\n" + "═" * 68)
    print("  Industrial Anomaly Detection  —  Single Image Live Evaluation")
    print("  IIIT Raichur | DIP + ACOMA + Networks Project 2026")
    print("═" * 68)
    print(f"  Category : {category}")
    print(f"  Image    : {image_path}")
    print(f"  Device   : {device}")
    print("─" * 68)

    # ── Load & preprocess ─────────────────────────────────────
    print("\n[1/4] Loading image …")
    img_rgb, tensor = load_and_preprocess(image_path, 256)

    # ── Computer Networks Simulation (Optional) ───────────────
    if args.simulate_network:
        print("\n  [Computer Networks] Simulating Industrial Edge-to-Server Transmission:")
        raw_bytes = cv2.imencode('.png', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))[1].tobytes()
        orig_kb = len(raw_bytes) / 1024.0
        
        # JPEG Q70 compression
        _, enc_jpg = cv2.imencode('.jpg', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 70])
        jpg_bytes = enc_jpg.tobytes()
        comp_kb = len(jpg_bytes) / 1024.0
        comp_ratio = (1.0 - comp_kb / orig_kb) * 100.0

        # Decompress on server
        dec_bgr = cv2.imdecode(np.frombuffer(jpg_bytes, np.uint8), cv2.IMREAD_COLOR)
        dec_rgb = cv2.cvtColor(dec_bgr, cv2.COLOR_BGR2RGB)
        
        # Image quality (PSNR & SSIM)
        from skimage.metrics import peak_signal_noise_ratio as psnr, structural_similarity as ssim
        psnr_val = psnr(img_rgb, dec_rgb, data_range=255)
        ssim_val = ssim(cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY),
                        cv2.cvtColor(dec_rgb, cv2.COLOR_RGB2GRAY), data_range=255)
        
        # 100 Mbps industrial LAN latency model
        bw_bps = 100e6
        tx_latency_ms = (len(jpg_bytes) * 8 / bw_bps) * 1000.0 + 10.0  # 10ms propagation
        
        print(f"    • Payload Size: {orig_kb:.1f} KB (PNG)  →  {comp_kb:.1f} KB (JPEG Q70) [{comp_ratio:.1f}% bandwidth saved]")
        print(f"    • Reconstruction Quality: PSNR = {psnr_val:.2f} dB, SSIM = {ssim_val:.4f}")
        print(f"    • Simulated Transmit Latency (100 Mbps LAN): {tx_latency_ms:.2f} ms")
        
        # Use decompressed image for inference to verify robustness
        tfm = get_transforms(image_size=256, augment=False)
        tensor = tfm(dec_rgb).unsqueeze(0)
        img_rgb = dec_rgb

    # ── Load / Fit models ─────────────────────────────────────
    print("\n[2/4] Loading / initializing models …")
    ae_model, arch_name, ae_th_override = load_autoencoder(category, device, arch=args.arch)
    train_loader = build_train_loader(category)
    pc_model  = get_or_fit_patchcore(train_loader, category, device)
    pd_model  = get_or_fit_padim(train_loader, category, device)

    # ── Run inference ─────────────────────────────────────────
    print("\n[3/4] Running multi-model inference …")
    t0 = time.time()

    ae_map, ae_score, recon_rgb = run_autoencoder(ae_model, tensor, device)
    pc_map, pc_score = run_patchcore(pc_model, tensor)
    pd_map, pd_score = run_padim(pd_model, tensor)

    eval_res = evaluate_hybrid(ae_score, pc_score, pd_score, ae_map, pc_map, pd_map, category, ae_th_override=ae_th_override)
    infer_time = time.time() - t0

    # ── Print results table ───────────────────────────────────
    th = get_thresholds(category)
    print("\n" + "─" * 68)
    print(f"  {'Model':<18} {'Raw Score':>10} {'Threshold':>10} {'Ratio':>8} {'Weight':>8} {'Verdict':>10}")
    print("  " + "-" * 66)
    
    ae_v = "DEFECT" if eval_res['ae']['vote'] else "NORMAL"
    pc_v = "DEFECT" if eval_res['pc']['vote'] else "NORMAL"
    pd_v = "DEFECT" if eval_res['pd']['vote'] else "NORMAL"

    ae_label = f"ConvAE ({arch_name})"
    print(f"  {ae_label:<18} {ae_score:>10.5f} {eval_res['ae']['th']:>10.5f} {eval_res['ae']['ratio']:>7.2f}x {AE_WEIGHT:>7.2f} {ae_v:>10}")
    print(f"  {'PatchCore':<18} {pc_score:>10.4f} {th['pc']:>10.4f} {eval_res['pc']['ratio']:>7.2f}x {PC_WEIGHT:>7.2f} {pc_v:>10}")
    print(f"  {'PaDiM':<18} {pd_score:>10.2f} {th['padim']:>10.2f} {eval_res['pd']['ratio']:>7.2f}x {PD_WEIGHT:>7.2f} {pd_v:>10}")
    print("  " + "-" * 66)
    print(f"  {'HYBRID WEIGHTED':<18} {eval_res['weighted_ratio']:>10.2f}x {'1.00x':>10} {'-':>8} {'1.00':>7} {eval_res['verdict']:>10}")
    print("─" * 68)
    print(f"\n  ★  FINAL OUTCOME:  [{eval_res['verdict']}]  (Latency: {infer_time*1000:.1f}ms)  ★")
    print("─" * 68)

    # ── Visualize ─────────────────────────────────────────────
    print("\n[4/4] Generating visualization …")
    out_name = f"demo_{category}_{os.path.splitext(os.path.basename(image_path))[0]}.png"
    save_path = os.path.join(PROJECT_ROOT, "demo_output", out_name)
    visualize(
        image_path, img_rgb,
        ae_map, pc_map, pd_map,
        eval_res, category,
        save_path, args.no_display,
    )

    print("\n  Demo completed successfully. 🎉")


if __name__ == "__main__":
    main()

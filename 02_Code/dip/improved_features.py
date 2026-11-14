"""
Improved Feature Extraction Module.

Adds enhanced preprocessing, median reference, and additional features
(LBP, Local Entropy, Gradient Magnitude, Edge Density) on top of the
original 7 DIP features.
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
from skimage.metrics import structural_similarity as sk_ssim
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from skimage.filters.rank import entropy as sk_entropy
from skimage.morphology import disk
from scipy.ndimage import uniform_filter

from utils.config import (
    IMAGE_SIZE, FEATURE_NAMES, OUTPUT_DIR,
    CANNY_THRESHOLD1, CANNY_THRESHOLD2,
    DEFECT_AREA_THRESHOLD, ensure_dirs,
    get_train_images, get_test_images,
)

logger = logging.getLogger(__name__)

# ---- Extended feature names ----
EXTENDED_FEATURE_NAMES = FEATURE_NAMES + [
    "lbp_difference",
    "local_entropy_difference",
    "gradient_magnitude_difference",
    "edge_density_difference",
]


# ============================================================
# Improved Preprocessing
# ============================================================

def preprocess_image(img_bgr_uint8, size=IMAGE_SIZE):
    """Enhanced preprocessing: resize, denoise, CLAHE illumination normalization.

    Returns float64 BGR image in [0, 1].
    """
    # Resize
    img = cv2.resize(img_bgr_uint8, size)

    # Mild Gaussian denoising (preserves defect edges)
    img = cv2.GaussianBlur(img, (3, 3), 0.5)

    # CLAHE illumination normalization on L-channel (LAB space)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    return img.astype(np.float64) / 255.0


def load_and_preprocess_improved(image_path, size=IMAGE_SIZE):
    """Load image with improved preprocessing."""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")
    return preprocess_image(img, size)


# ============================================================
# Reference Images (Mean + Median)
# ============================================================

def compute_reference_images(train_paths, size=IMAGE_SIZE):
    """Compute both mean and median reference from training normals.

    Returns:
        mean_ref:   float64 BGR [0,1]
        median_ref: float64 BGR [0,1]
    """
    logger.info("Computing mean + median reference from %d training images ...", len(train_paths))
    images = []
    for p in train_paths:
        img = cv2.imread(p, cv2.IMREAD_COLOR)
        if img is None:
            continue
        images.append(preprocess_image(img, size))

    if len(images) == 0:
        raise RuntimeError("No valid training images found.")

    stack = np.array(images)  # (N, H, W, 3)
    mean_ref = np.mean(stack, axis=0)
    median_ref = np.median(stack, axis=0)
    logger.info("Reference images computed from %d images.", len(images))
    return mean_ref, median_ref


# ============================================================
# Original 7 Features (preserved)
# ============================================================

def _pixel_difference(img, ref):
    return float(np.mean(np.abs(img - ref)))

def _ssim(img, ref):
    img_u8 = (img * 255).astype(np.uint8)
    ref_u8 = (ref * 255).astype(np.uint8)
    score = sk_ssim(ref_u8, img_u8, channel_axis=2, data_range=255)
    return float(score)

def _color_difference(img, ref):
    dists = []
    for c in range(3):
        h_img = cv2.calcHist([(img * 255).astype(np.uint8)], [c], None, [32], [0, 256])
        h_ref = cv2.calcHist([(ref * 255).astype(np.uint8)], [c], None, [32], [0, 256])
        cv2.normalize(h_img, h_img)
        cv2.normalize(h_ref, h_ref)
        corr = cv2.compareHist(h_img, h_ref, cv2.HISTCMP_CORREL)
        dists.append(1.0 - corr)
    return float(np.mean(dists))

def _edge_difference(img, ref):
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    edges_img = cv2.Canny(gray_img, CANNY_THRESHOLD1, CANNY_THRESHOLD2).astype(np.float64) / 255.0
    edges_ref = cv2.Canny(gray_ref, CANNY_THRESHOLD1, CANNY_THRESHOLD2).astype(np.float64) / 255.0
    return float(np.mean(np.abs(edges_img - edges_ref)))

def _glcm_contrast(gray_u8):
    quantised = (gray_u8 // 4).astype(np.uint8)
    glcm = graycomatrix(quantised, distances=[1], angles=[0], levels=64, symmetric=True, normed=True)
    return float(graycoprops(glcm, "contrast")[0, 0])

def _texture_difference(img, ref):
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    return float(abs(_glcm_contrast(gray_img) - _glcm_contrast(gray_ref)))

def _frequency_difference(img, ref):
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float64)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float64)
    fft_img = np.fft.fft2(gray_img)
    fft_ref = np.fft.fft2(gray_ref)
    mag_img = np.log1p(np.abs(np.fft.fftshift(fft_img)))
    mag_ref = np.log1p(np.abs(np.fft.fftshift(fft_ref)))
    def norm01(x):
        mn, mx = x.min(), x.max()
        return (x - mn) / (mx - mn + 1e-12)
    return float(np.mean(np.abs(norm01(mag_img) - norm01(mag_ref))))

def _defect_area(img, ref, threshold=DEFECT_AREA_THRESHOLD):
    diff = np.mean(np.abs(img - ref), axis=2)
    return float(np.mean(diff > threshold))


# ============================================================
# New Features
# ============================================================

def _lbp_difference(img, ref):
    """LBP histogram chi-squared distance."""
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)

    radius, n_points = 2, 16
    lbp_img = local_binary_pattern(gray_img, n_points, radius, method='uniform')
    lbp_ref = local_binary_pattern(gray_ref, n_points, radius, method='uniform')

    n_bins = n_points + 2
    hist_img, _ = np.histogram(lbp_img.ravel(), bins=n_bins, range=(0, n_bins), density=True)
    hist_ref, _ = np.histogram(lbp_ref.ravel(), bins=n_bins, range=(0, n_bins), density=True)

    # Chi-squared distance
    denom = hist_img + hist_ref + 1e-12
    chi2 = float(np.sum((hist_img - hist_ref) ** 2 / denom))
    return chi2


def _local_entropy_difference(img, ref):
    """Mean absolute difference of local entropy maps."""
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)

    ent_img = sk_entropy(gray_img, disk(5))
    ent_ref = sk_entropy(gray_ref, disk(5))

    return float(np.mean(np.abs(ent_img.astype(np.float64) - ent_ref.astype(np.float64))))


def _gradient_magnitude_difference(img, ref):
    """Mean absolute difference of Sobel gradient magnitudes."""
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)

    gx_img = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=3)
    gy_img = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1, ksize=3)
    mag_img = np.sqrt(gx_img**2 + gy_img**2)

    gx_ref = cv2.Sobel(gray_ref, cv2.CV_64F, 1, 0, ksize=3)
    gy_ref = cv2.Sobel(gray_ref, cv2.CV_64F, 0, 1, ksize=3)
    mag_ref = np.sqrt(gx_ref**2 + gy_ref**2)

    # Normalize to [0, 1]
    max_val = max(mag_img.max(), mag_ref.max(), 1e-12)
    return float(np.mean(np.abs(mag_img / max_val - mag_ref / max_val)))


def _edge_density_difference(img, ref):
    """Absolute difference of edge pixel density."""
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)

    edges_img = cv2.Canny(gray_img, CANNY_THRESHOLD1, CANNY_THRESHOLD2)
    edges_ref = cv2.Canny(gray_ref, CANNY_THRESHOLD1, CANNY_THRESHOLD2)

    density_img = np.mean(edges_img > 0)
    density_ref = np.mean(edges_ref > 0)

    return float(abs(density_img - density_ref))


# ============================================================
# Combined Feature Extraction
# ============================================================

def extract_extended_features(img, ref):
    """Extract all 11 features (7 original + 4 new)."""
    return {
        "pixel_difference": _pixel_difference(img, ref),
        "ssim": _ssim(img, ref),
        "color_difference": _color_difference(img, ref),
        "edge_difference": _edge_difference(img, ref),
        "texture_difference": _texture_difference(img, ref),
        "frequency_difference": _frequency_difference(img, ref),
        "defect_area": _defect_area(img, ref),
        "lbp_difference": _lbp_difference(img, ref),
        "local_entropy_difference": _local_entropy_difference(img, ref),
        "gradient_magnitude_difference": _gradient_magnitude_difference(img, ref),
        "edge_density_difference": _edge_density_difference(img, ref),
    }


# ============================================================
# Batch Extraction
# ============================================================

def run_improved_feature_extraction(ref_type="mean", save=True, cfg=None):
    """Run improved feature extraction for all test and train images.

    Args:
        ref_type: "mean" or "median"
        save:     persist CSVs to disk
        cfg:      CategoryConfig (from config.get_category_config). If None,
                  falls back to the legacy bottle-only helpers.

    Returns:
        df_test, df_train, ref, ref_type_used
    """
    if cfg is not None:
        cfg.ensure_output_dirs()
        train_paths = cfg.get_train_images()
        test_images = cfg.get_test_images()
        output_dir  = cfg.features_dir
    else:
        ensure_dirs()
        train_paths = get_train_images()
        test_images = get_test_images()
        output_dir  = OUTPUT_DIR
    logger.info("Improved extraction: %d train, %d test, ref=%s",
                len(train_paths), len(test_images), ref_type)

    mean_ref, median_ref = compute_reference_images(train_paths)
    ref = mean_ref if ref_type == "mean" else median_ref

    # Extract test features
    test_rows = []
    for i, (img_path, category, img_id) in enumerate(test_images):
        try:
            img = load_and_preprocess_improved(img_path)
            feats = extract_extended_features(img, ref)
            row = {"image_id": img_id, "category": category, "image_path": img_path}
            row.update(feats)
            test_rows.append(row)
            if (i + 1) % 10 == 0 or (i + 1) == len(test_images):
                logger.info("  [%d/%d] test features for %s/%s", i+1, len(test_images), category, img_id)
        except Exception as e:
            logger.error("Error processing %s: %s", img_path, e)

    df_test = pd.DataFrame(test_rows)

    # Extract train features
    train_rows = []
    for i, img_path in enumerate(train_paths):
        try:
            img = load_and_preprocess_improved(img_path)
            feats = extract_extended_features(img, ref)
            row = {"image_id": os.path.basename(img_path), "category": "good", "image_path": img_path}
            row.update(feats)
            train_rows.append(row)
            if (i + 1) % 20 == 0 or (i + 1) == len(train_paths):
                logger.info("  [%d/%d] train features", i+1, len(train_paths))
        except Exception as e:
            logger.error("Error processing train %s: %s", img_path, e)

    df_train = pd.DataFrame(train_rows)

    if save:
        os.makedirs(output_dir, exist_ok=True)
        df_test.to_csv(os.path.join(output_dir, f"improved_test_features_{ref_type}.csv"), index=False)
        df_train.to_csv(os.path.join(output_dir, f"improved_train_features_{ref_type}.csv"), index=False)
        logger.info("Improved features saved to %s", output_dir)

    return df_test, df_train, ref, ref_type


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    for rt in ["mean", "median"]:
        print(f"\n--- Reference type: {rt} ---")
        df_t, df_tr, _, _ = run_improved_feature_extraction(ref_type=rt)
        print(f"Test: {df_t.shape}, Train: {df_tr.shape}")

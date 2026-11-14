"""
Feature Extraction Module for Industrial Anomaly Detection.

Extracts 7 DIP-based features by comparing test images against a reference
image computed from training normal images.

Features:
  1. pixel_difference   – mean absolute pixel difference (normalised 0-1)
  2. ssim               – structural similarity index (1 = identical)
  3. color_difference    – colour histogram correlation distance
  4. edge_difference     – mean absolute Canny-edge difference
  5. texture_difference  – GLCM contrast difference
  6. frequency_difference – FFT magnitude spectrum difference
  7. defect_area         – fraction of pixels exceeding a threshold
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
from skimage.metrics import structural_similarity as sk_ssim
from skimage.feature import graycomatrix, graycoprops

from utils.config import (
    IMAGE_SIZE,
    FEATURE_NAMES,
    CANNY_THRESHOLD1,
    CANNY_THRESHOLD2,
    DEFECT_AREA_THRESHOLD,
    OUTPUT_DIR,
    get_train_images,
    get_test_images,
    ensure_dirs,
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Reference image
# ------------------------------------------------------------------

def compute_reference_image(train_paths: list, size: tuple = IMAGE_SIZE) -> np.ndarray:
    """Compute mean image from training normal images.

    Returns:
        np.float64 array, shape (H, W, 3), values in [0, 1].
    """
    logger.info("Computing reference image from %d training images ...", len(train_paths))
    accumulator = None
    count = 0
    for p in train_paths:
        img = cv2.imread(p, cv2.IMREAD_COLOR)
        if img is None:
            logger.warning("Could not read %s – skipping.", p)
            continue
        img = cv2.resize(img, size).astype(np.float64) / 255.0
        if accumulator is None:
            accumulator = np.zeros_like(img)
        accumulator += img
        count += 1
    if count == 0:
        raise RuntimeError("No valid training images found.")
    reference = accumulator / count
    logger.info("Reference image computed from %d images.", count)
    return reference


# ------------------------------------------------------------------
# Individual feature functions
# ------------------------------------------------------------------

def _pixel_difference(img: np.ndarray, ref: np.ndarray) -> float:
    """Mean absolute pixel difference (0-1 scale)."""
    return float(np.mean(np.abs(img - ref)))


def _ssim(img: np.ndarray, ref: np.ndarray) -> float:
    """Structural similarity (uses skimage, multichannel)."""
    # Convert to uint8 for SSIM computation
    img_u8 = (img * 255).astype(np.uint8)
    ref_u8 = (ref * 255).astype(np.uint8)
    score = sk_ssim(ref_u8, img_u8, channel_axis=2, data_range=255)
    return float(score)


def _color_difference(img: np.ndarray, ref: np.ndarray) -> float:
    """Color histogram correlation distance.

    Computes per-channel histograms (32 bins) and returns
    1 - mean(correlation) so that higher = more different.
    """
    dists = []
    for c in range(3):
        h_img = cv2.calcHist([(img * 255).astype(np.uint8)], [c], None, [32], [0, 256])
        h_ref = cv2.calcHist([(ref * 255).astype(np.uint8)], [c], None, [32], [0, 256])
        cv2.normalize(h_img, h_img)
        cv2.normalize(h_ref, h_ref)
        corr = cv2.compareHist(h_img, h_ref, cv2.HISTCMP_CORREL)
        dists.append(1.0 - corr)
    return float(np.mean(dists))


def _edge_difference(img: np.ndarray, ref: np.ndarray) -> float:
    """Mean absolute difference of Canny edge maps."""
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    edges_img = cv2.Canny(gray_img, CANNY_THRESHOLD1, CANNY_THRESHOLD2).astype(np.float64) / 255.0
    edges_ref = cv2.Canny(gray_ref, CANNY_THRESHOLD1, CANNY_THRESHOLD2).astype(np.float64) / 255.0
    return float(np.mean(np.abs(edges_img - edges_ref)))


def _glcm_contrast(gray_u8: np.ndarray) -> float:
    """GLCM contrast for a single grayscale image."""
    # Quantise to 64 levels for speed
    quantised = (gray_u8 // 4).astype(np.uint8)
    glcm = graycomatrix(quantised, distances=[1], angles=[0], levels=64, symmetric=True, normed=True)
    return float(graycoprops(glcm, "contrast")[0, 0])


def _texture_difference(img: np.ndarray, ref: np.ndarray) -> float:
    """Absolute difference of GLCM contrast values."""
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    c_img = _glcm_contrast(gray_img)
    c_ref = _glcm_contrast(gray_ref)
    return float(abs(c_img - c_ref))


def _frequency_difference(img: np.ndarray, ref: np.ndarray) -> float:
    """Mean absolute difference of FFT magnitude spectra (grayscale)."""
    gray_img = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float64)
    gray_ref = cv2.cvtColor((ref * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float64)

    fft_img = np.fft.fft2(gray_img)
    fft_ref = np.fft.fft2(gray_ref)

    mag_img = np.abs(np.fft.fftshift(fft_img))
    mag_ref = np.abs(np.fft.fftshift(fft_ref))

    # Log-scale to compress dynamic range, then normalise
    mag_img = np.log1p(mag_img)
    mag_ref = np.log1p(mag_ref)

    # Normalise each to 0-1
    def norm01(x):
        mn, mx = x.min(), x.max()
        return (x - mn) / (mx - mn + 1e-12)

    return float(np.mean(np.abs(norm01(mag_img) - norm01(mag_ref))))


def _defect_area(img: np.ndarray, ref: np.ndarray, threshold: float = DEFECT_AREA_THRESHOLD) -> float:
    """Fraction of pixels whose difference exceeds threshold."""
    diff = np.mean(np.abs(img - ref), axis=2)  # per-pixel mean across channels
    return float(np.mean(diff > threshold))


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def extract_features(img: np.ndarray, ref: np.ndarray) -> dict:
    """Extract all 7 features for a single image vs reference.

    Args:
        img: float64 BGR image in [0,1], shape (H, W, 3).
        ref: float64 BGR reference in [0,1], same shape.

    Returns:
        dict with keys = FEATURE_NAMES.
    """
    return {
        "pixel_difference": _pixel_difference(img, ref),
        "ssim": _ssim(img, ref),
        "color_difference": _color_difference(img, ref),
        "edge_difference": _edge_difference(img, ref),
        "texture_difference": _texture_difference(img, ref),
        "frequency_difference": _frequency_difference(img, ref),
        "defect_area": _defect_area(img, ref),
    }


def load_and_preprocess(image_path: str, size: tuple = IMAGE_SIZE) -> np.ndarray:
    """Load an image from disk and return float64 BGR in [0,1]."""
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")
    return cv2.resize(img, size).astype(np.float64) / 255.0


def extract_features_for_image(image_path: str, ref: np.ndarray) -> dict:
    """Convenience: load image, extract features."""
    img = load_and_preprocess(image_path)
    return extract_features(img, ref)


# ------------------------------------------------------------------
# Batch extraction
# ------------------------------------------------------------------

def run_feature_extraction(save: bool = True) -> pd.DataFrame:
    """Run feature extraction for all test images.

    Returns a DataFrame with columns:
        image_id, category, image_path, + FEATURE_NAMES
    """
    ensure_dirs()
    train_paths = get_train_images()
    test_images = get_test_images()
    logger.info("Found %d training and %d test images.", len(train_paths), len(test_images))

    ref = compute_reference_image(train_paths)

    rows = []
    t0 = time.time()
    for i, (img_path, category, img_id) in enumerate(test_images):
        try:
            feats = extract_features_for_image(img_path, ref)
            row = {"image_id": img_id, "category": category, "image_path": img_path}
            row.update(feats)
            rows.append(row)
            if (i + 1) % 10 == 0 or (i + 1) == len(test_images):
                logger.info("  [%d/%d] extracted features for %s/%s",
                            i + 1, len(test_images), category, img_id)
        except Exception as e:
            logger.error("Error processing %s: %s", img_path, e)

    elapsed = time.time() - t0
    logger.info("Feature extraction completed in %.1f s", elapsed)

    df = pd.DataFrame(rows)

    if save:
        out_path = os.path.join(OUTPUT_DIR, "bottle_features.csv")
        df.to_csv(out_path, index=False)
        logger.info("Features saved to %s", out_path)

    return df, ref


def run_train_feature_extraction(ref: np.ndarray, save: bool = True) -> pd.DataFrame:
    """Extract features for training images (leave-one-out style).

    For each training image, compute features against the reference.
    This provides the 'normal' score distribution for threshold setting.
    """
    train_paths = get_train_images()
    rows = []
    t0 = time.time()
    for i, img_path in enumerate(train_paths):
        try:
            feats = extract_features_for_image(img_path, ref)
            row = {
                "image_id": os.path.basename(img_path),
                "category": "good",
                "image_path": img_path,
            }
            row.update(feats)
            rows.append(row)
            if (i + 1) % 20 == 0 or (i + 1) == len(train_paths):
                logger.info("  [%d/%d] train features extracted", i + 1, len(train_paths))
        except Exception as e:
            logger.error("Error processing train image %s: %s", img_path, e)

    elapsed = time.time() - t0
    logger.info("Training feature extraction completed in %.1f s", elapsed)

    df = pd.DataFrame(rows)
    if save:
        out_path = os.path.join(OUTPUT_DIR, "bottle_train_features.csv")
        df.to_csv(out_path, index=False)
        logger.info("Training features saved to %s", out_path)

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    df_test, ref = run_feature_extraction()
    df_train = run_train_feature_extraction(ref)
    print(f"\nTest features shape: {df_test.shape}")
    print(f"Train features shape: {df_train.shape}")
    print(df_test.head())

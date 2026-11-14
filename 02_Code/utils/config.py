"""
Configuration module for the Industrial Anomaly Detection Pipeline.

Supports dynamic per-category configuration for all 15 MVTec AD categories.
All module-level constants default to 'bottle' for backward compatibility.

Usage:
    # Module-level (bottle defaults, backward-compatible):
    from utils.config import DEVICE, DATA_ROOT, get_train_images, get_test_images

    # Per-category (multi-category pipeline):
    from utils.config import get_category_config
    cfg = get_category_config("cable")
    cfg.train_dir, cfg.test_dir, cfg.output_dir, cfg.get_train_images(), ...
"""


import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..\.."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import os
import torch
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ============================================================
# Hardware
# ============================================================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============================================================
# Root Paths  (config.py lives at 02_Code/utils/ → go up 2 levels)
# ============================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_ROOT    = os.path.join(PROJECT_ROOT, "01_Dataset", "MVTec_AD")
RESULTS_DIR  = os.path.join(PROJECT_ROOT, "03_Results")
MODELS_DIR   = os.path.join(PROJECT_ROOT, "04_Models")

# ============================================================
# Categories
# ============================================================
# Full list of 15 MVTec AD categories
ALL_CATEGORIES: List[str] = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill",
    "screw", "tile", "toothbrush", "transistor",
    "wood", "zipper",
]

# Categories skipped because they have no training (normal) images
SKIP_CATEGORIES: List[str] = ["pill", "wood", "zipper"]

# Categories that are valid for unsupervised training
VALID_CATEGORIES: List[str] = [c for c in ALL_CATEGORIES if c not in SKIP_CATEGORIES]

# ============================================================
# Image settings
# ============================================================
IMAGE_SIZE       = (256, 256)
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}

# ============================================================
# Feature names
# ============================================================
FEATURE_NAMES = [
    "pixel_difference",
    "ssim",
    "color_difference",
    "edge_difference",
    "texture_difference",
    "frequency_difference",
    "defect_area",
]

EXTENDED_FEATURE_NAMES = FEATURE_NAMES + [
    "lbp_difference",
    "local_entropy_difference",
    "gradient_magnitude_difference",
    "edge_density_difference",
]

# Feature extraction parameters
CANNY_THRESHOLD1    = 50
CANNY_THRESHOLD2    = 150
DEFECT_AREA_THRESHOLD = 0.05
LBP_RADIUS          = 3
LBP_N_POINTS        = 24   # 8 * LBP_RADIUS

# ============================================================
# Detector / Scoring
# ============================================================
THRESHOLD_K   = 2.0   # decision boundary: mean + k * std of train scores
EQUAL_WEIGHTS = {f: 1.0 / len(FEATURE_NAMES) for f in FEATURE_NAMES}

# ============================================================
# Optimization
# ============================================================
OPTIMIZATION_METHODS  = ["Steepest Descent", "Conjugate Gradient", "BFGS", "Trust Region"]
OPTIMIZATION_MAX_ITER = 500
OPTIMIZATION_TOL      = 1e-8

# ============================================================
# Compression / Network simulation
# ============================================================
JPEG_QUALITIES       = [95, 75, 50]
COMPRESSION_SETTINGS = ["Original (PNG)"] + [f"JPEG Q{q}" for q in JPEG_QUALITIES]

NETWORK_BANDWIDTH_MBPS = 10.0
NETWORK_BANDWIDTH_BPS  = NETWORK_BANDWIDTH_MBPS * 1e6
NETWORK_LATENCY_MS     = 50.0
NETWORK_LATENCY_S      = NETWORK_LATENCY_MS / 1000.0


# ============================================================
# Per-Category Configuration  (the main new object)
# ============================================================

@dataclass
class CategoryConfig:
    """
    All paths and helpers for a single MVTec AD category.

    Attributes
    ----------
    category    : str   – e.g. "bottle"
    data_dir    : str   – 01_Dataset/MVTec_AD/<category>
    train_dir   : str   – .../train/good
    test_dir    : str   – .../test
    gt_dir      : str   – .../ground_truth  (may not exist for all categories)
    output_dir  : str   – 03_Results/<category>
    model_path  : str   – 04_Models/autoencoder_<category>.pt
    test_defect_types : List[str]  – auto-discovered defect sub-folders inside test/
    has_gt_masks      : bool       – True if ground_truth/ folder exists
    """

    category: str

    # Populated in __post_init__
    data_dir:  str = field(init=False)
    train_dir: str = field(init=False)
    test_dir:  str = field(init=False)
    gt_dir:    str = field(init=False)

    output_dir:          str = field(init=False)
    features_dir:        str = field(init=False)
    predictions_dir:     str = field(init=False)
    compression_dir:     str = field(init=False)
    pixel_metrics_dir:   str = field(init=False)
    charts_dir:          str = field(init=False)

    model_path: str = field(init=False)

    test_defect_types: List[str] = field(init=False)
    anomalous_types:   List[str] = field(init=False)
    has_gt_masks:      bool = field(init=False)

    def __post_init__(self):
        # ── Data paths ──────────────────────────────────────────────
        self.data_dir  = os.path.join(DATA_ROOT, self.category)
        self.train_dir = os.path.join(self.data_dir, "train", "good")
        self.test_dir  = os.path.join(self.data_dir, "test")
        self.gt_dir    = os.path.join(self.data_dir, "ground_truth")

        # ── Output paths ─────────────────────────────────────────────
        base = os.path.join(RESULTS_DIR, self.category)
        self.output_dir        = base
        self.features_dir      = os.path.join(base, "features")
        self.predictions_dir   = os.path.join(base, "predictions")
        self.compression_dir   = os.path.join(base, "compression")
        self.pixel_metrics_dir = os.path.join(base, "pixel_metrics")
        self.charts_dir        = os.path.join(base, "charts")

        # ── Model path ───────────────────────────────────────────────
        self.model_path = os.path.join(MODELS_DIR, f"autoencoder_{self.category}.pt")

        # ── Discover test sub-folders dynamically ────────────────────
        if os.path.isdir(self.test_dir):
            all_subs = sorted(
                d for d in os.listdir(self.test_dir)
                if os.path.isdir(os.path.join(self.test_dir, d))
            )
        else:
            all_subs = []

        self.test_defect_types = all_subs
        self.anomalous_types   = [d for d in all_subs if d != "good"]
        self.has_gt_masks      = os.path.isdir(self.gt_dir)

    # ── Helper methods ───────────────────────────────────────────────

    def ensure_output_dirs(self) -> None:
        """Create all output directories for this category."""
        dirs = [
            self.output_dir, self.features_dir, self.predictions_dir,
            self.compression_dir, self.pixel_metrics_dir, self.charts_dir,
            os.path.join(self.charts_dir, "basic"),
            os.path.join(self.charts_dir, "comprehensive"),
            os.path.join(self.charts_dir, "feature_analysis"),
            os.path.join(self.charts_dir, "pixel_localization"),
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

    def get_train_images(self) -> List[str]:
        """Return sorted list of normal training image paths."""
        if not os.path.isdir(self.train_dir):
            return []
        return [
            os.path.join(self.train_dir, f)
            for f in sorted(os.listdir(self.train_dir))
            if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
        ]

    def get_test_images(self) -> List[Tuple[str, str, str]]:
        """
        Return list of (image_path, defect_type, filename) for all test images.
        Normal images have defect_type == 'good'.
        """
        images = []
        for defect_type in self.test_defect_types:
            sub_dir = os.path.join(self.test_dir, defect_type)
            for fname in sorted(os.listdir(sub_dir)):
                if os.path.splitext(fname)[1].lower() in IMAGE_EXTENSIONS:
                    images.append((os.path.join(sub_dir, fname), defect_type, fname))
        return images

    def get_gt_mask_path(self, defect_type: str, filename: str) -> Optional[str]:
        """
        Return the ground-truth mask path for a test image, or None if unavailable.
        Tries both <name>_mask.png and <name>.png conventions.
        """
        if not self.has_gt_masks or defect_type == "good":
            return None
        base = os.path.splitext(filename)[0]
        for candidate in (f"{base}_mask.png", filename):
            path = os.path.join(self.gt_dir, defect_type, candidate)
            if os.path.exists(path):
                return path
        return None

    def summary(self) -> str:
        """Return a compact text summary of this category's dataset."""
        train_n = len(self.get_train_images())
        test_n  = len(self.get_test_images())
        return (
            f"[{self.category}]  train={train_n}  test={test_n}  "
            f"defect_types={self.anomalous_types}  gt_masks={self.has_gt_masks}"
        )


# ============================================================
# Factory function
# ============================================================

def get_category_config(category: str) -> CategoryConfig:
    """
    Return a fully-populated CategoryConfig for the given MVTec AD category.

    Example:
        cfg = get_category_config("cable")
        images = cfg.get_train_images()
        cfg.ensure_output_dirs()
    """
    return CategoryConfig(category=category)


def list_valid_categories() -> List[str]:
    """Return all categories that have training images present on disk."""
    valid = []
    for cat in ALL_CATEGORIES:
        train_dir = os.path.join(DATA_ROOT, cat, "train", "good")
        if os.path.isdir(train_dir) and any(
            os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
            for f in os.listdir(train_dir)
        ):
            valid.append(cat)
    return valid


# ============================================================
# Backward-compatible module-level helpers (default: bottle)
# ============================================================
_DEFAULT_CFG = CategoryConfig(category="bottle")

BOTTLE_DIR           = _DEFAULT_CFG.data_dir
TRAIN_DIR            = _DEFAULT_CFG.train_dir
TEST_DIR             = _DEFAULT_CFG.test_dir
GT_DIR               = _DEFAULT_CFG.gt_dir
TEST_CATEGORIES      = _DEFAULT_CFG.test_defect_types
ANOMALOUS_CATEGORIES = _DEFAULT_CFG.anomalous_types
OUTPUT_DIR           = _DEFAULT_CFG.output_dir
CHARTS_DIR           = _DEFAULT_CFG.charts_dir
REPORTS_DIR          = os.path.join(RESULTS_DIR, "bottle", "reports")


def ensure_dirs() -> None:
    """Create output dirs for the default bottle category (backward compat)."""
    _DEFAULT_CFG.ensure_output_dirs()


def get_train_images() -> List[str]:
    """Return training image paths for bottle (backward compat)."""
    return _DEFAULT_CFG.get_train_images()


def get_test_images() -> List[Tuple[str, str, str]]:
    """Return test image tuples for bottle (backward compat)."""
    return _DEFAULT_CFG.get_test_images()


# ============================================================
# Self-test
# ============================================================
if __name__ == "__main__":
    print(f"DEVICE       : {DEVICE}")
    print(f"PROJECT_ROOT : {PROJECT_ROOT}")
    print(f"DATA_ROOT    : {DATA_ROOT}")
    print()

    valid = list_valid_categories()
    print(f"Valid categories ({len(valid)}): {valid}")
    print()

    for cat in valid:
        cfg = get_category_config(cat)
        print(cfg.summary())

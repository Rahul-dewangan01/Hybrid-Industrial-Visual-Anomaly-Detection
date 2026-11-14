"""
PyTorch Dataset for MVTec AD — generalized for any category.

Provides:
    MVTecDataset(category, split, image_size, augment)
        → works for all 15 MVTec AD categories.

    MVTecBottleDataset   → alias for backward compatibility.
    get_dataloader(...)  → convenience wrapper.
    denormalize(tensor)  → reverse ImageNet normalization for visualization.
"""


import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..\.."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from typing import List, Tuple, Optional

from utils.config import get_category_config, IMAGE_EXTENSIONS, IMAGE_SIZE

# ============================================================
# ImageNet normalization constants
# ============================================================
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


# ============================================================
# Transforms
# ============================================================
def get_transforms(image_size: int = 256, augment: bool = False) -> transforms.Compose:
    """
    Return a torchvision transform pipeline.

    Training augmentation is mild (flip, small rotation, slight color jitter)
    to avoid introducing artificial defect-like artifacts.
    """
    base = [
        transforms.ToPILImage(),
        transforms.Resize((image_size, image_size)),
    ]
    if augment:
        base += [
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=5),
            transforms.ColorJitter(brightness=0.1, contrast=0.1),
        ]
    base += [
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
    return transforms.Compose(base)


# ============================================================
# Main Dataset Class
# ============================================================
class MVTecDataset(Dataset):
    """
    Generic MVTec AD dataset supporting any of the 15 categories.

    Parameters
    ----------
    category   : str   – MVTec AD category name, e.g. 'bottle', 'cable'.
    split      : str   – 'train' or 'test'.
    image_size : int   – Target square size after resize (default 256).
    augment    : bool  – Apply training augmentation (only meaningful for split='train').

    Returns (via __getitem__)
    ---------
    dict with keys:
        'image'      : FloatTensor (3, H, W) – ImageNet-normalized.
        'label'      : int  – 0 = normal, 1 = anomalous.
        'mask'       : FloatTensor (1, H, W) – pixel GT mask (zeros if unavailable).
        'category'   : str  – defect sub-type, e.g. 'broken_large', or 'good'.
        'image_id'   : str  – filename.
        'image_path' : str  – absolute path to source image.
    """

    def __init__(
        self,
        category: str = "bottle",
        split: str = "train",
        image_size: int = 256,
        augment: bool = False,
    ):
        self.category   = category
        self.split      = split
        self.image_size = image_size
        self.cfg        = get_category_config(category)
        self.transform  = get_transforms(image_size, augment and split == "train")

        # Build sample list: [(path, defect_type, filename), ...]
        if split == "train":
            self.samples: List[Tuple[str, str, str]] = [
                (p, "good", os.path.basename(p))
                for p in self.cfg.get_train_images()
            ]
        else:
            self.samples = self.cfg.get_test_images()

        if not self.samples:
            raise FileNotFoundError(
                f"No {split} images found for category '{category}'. "
                f"Check that {self.cfg.train_dir if split=='train' else self.cfg.test_dir} exists."
            )

    # ── Standard Dataset interface ──────────────────────────────────

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> dict:
        img_path, defect_type, img_id = self.samples[idx]

        # Load & convert BGR → RGB
        bgr = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if bgr is None:
            raise OSError(f"Cannot read image: {img_path}")
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        img_tensor = self.transform(rgb)
        label      = 0 if defect_type == "good" else 1

        # Ground-truth pixel mask (zeros if normal or mask not found)
        mask = torch.zeros(1, self.image_size, self.image_size, dtype=torch.float32)
        if label == 1:
            mask_path = self.cfg.get_gt_mask_path(defect_type, img_id)
            if mask_path is not None:
                m   = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                m   = cv2.resize(m, (self.image_size, self.image_size),
                                 interpolation=cv2.INTER_NEAREST)
                mask = torch.from_numpy((m > 127).astype(np.float32)).unsqueeze(0)

        return {
            "image":      img_tensor,
            "label":      label,
            "mask":       mask,
            "category":   defect_type,
            "image_id":   img_id,
            "image_path": img_path,
        }

    # ── Convenience properties ──────────────────────────────────────

    @property
    def n_normal(self) -> int:
        return sum(1 for _, t, _ in self.samples if t == "good")

    @property
    def n_anomalous(self) -> int:
        return sum(1 for _, t, _ in self.samples if t != "good")

    def __repr__(self) -> str:
        return (
            f"MVTecDataset(category='{self.category}', split='{self.split}', "
            f"n={len(self)}, normal={self.n_normal}, anomalous={self.n_anomalous})"
        )


# ============================================================
# Backward-compatible alias
# ============================================================
class MVTecBottleDataset(MVTecDataset):
    """Drop-in alias: behaves exactly like MVTecDataset(category='bottle', ...)."""

    def __init__(self, split: str = "train", image_size: int = 256, augment: bool = False):
        super().__init__(category="bottle", split=split,
                         image_size=image_size, augment=augment)


# ============================================================
# Convenience DataLoader factory
# ============================================================
def get_dataloader(
    category:   str = "bottle",
    split:      str = "train",
    batch_size: int = 8,
    image_size: int = 256,
    augment:    bool = False,
    shuffle:    Optional[bool] = None,
    num_workers: int = 0,
) -> DataLoader:
    """
    Return a DataLoader for the given category and split.

    Parameters
    ----------
    category    : MVTec AD category name.
    split       : 'train' or 'test'.
    batch_size  : Samples per batch.
    image_size  : Target image size (square).
    augment     : Apply augmentation (train only).
    shuffle     : Default True for train, False for test.
    num_workers : DataLoader workers (0 = main process, safe on Windows).
    """
    if shuffle is None:
        shuffle = (split == "train")
    ds = MVTecDataset(category=category, split=split,
                      image_size=image_size, augment=augment)
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle,
                      num_workers=num_workers, pin_memory=True)


# ============================================================
# Utility: reverse ImageNet normalization (for visualization)
# ============================================================
def denormalize(tensor: torch.Tensor) -> torch.Tensor:
    """
    Reverse ImageNet normalization.

    Input  : (3, H, W) or (B, 3, H, W) normalized tensor.
    Output : same shape, pixel values in [0, 1].
    """
    mean = torch.tensor(IMAGENET_MEAN, dtype=tensor.dtype, device=tensor.device)
    std  = torch.tensor(IMAGENET_STD,  dtype=tensor.dtype, device=tensor.device)
    if tensor.dim() == 3:          # (C, H, W)
        mean = mean.view(3, 1, 1)
        std  = std.view(3, 1, 1)
    else:                          # (B, C, H, W)
        mean = mean.view(1, 3, 1, 1)
        std  = std.view(1, 3, 1, 1)
    return (tensor * std + mean).clamp(0.0, 1.0)


# ============================================================
# Self-test
# ============================================================
if __name__ == "__main__":
    from utils.config import list_valid_categories

    for cat in list_valid_categories():
        try:
            train_ds = MVTecDataset(category=cat, split="train")
            test_ds  = MVTecDataset(category=cat, split="test")
            print(f"  {train_ds}")
            print(f"  {test_ds}")

            # Quick sanity: load one batch
            loader = get_dataloader(cat, split="train", batch_size=4)
            batch  = next(iter(loader))
            assert batch["image"].shape == (4, 3, 256, 256), "Unexpected image shape"
            assert batch["mask"].shape  == (4, 1, 256, 256), "Unexpected mask shape"
            print(f"  → Batch OK: images {batch['image'].shape}\n")
        except Exception as e:
            print(f"  [{cat}] FAILED: {e}\n")

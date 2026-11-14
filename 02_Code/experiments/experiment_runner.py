"""
experiment_runner.py — Unified experiment runner with logging, checkpointing,
seed control, and CSV tracking for all experimental study phases.

Usage:
    from experiments.experiment_runner import ExperimentRunner
    runner = ExperimentRunner(experiment_id="AE-01", model="autoencoder",
                              experiment_type="loss_experiments", category="bottle")
    with runner.context():
        # run experiment
        runner.log_metrics(auroc=0.95, pixel_auroc=0.80, ...)
"""

import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import csv
import json
import logging
import os
import random
import time
import traceback
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np
import torch

from experiments.experiment_config import (
    EXPERIMENT_STUDY_DIR, CHECKPOINTS_DIR, LOGS_DIR, VIZ_DIR,
    GLOBAL_SEED, TRACKER_COLUMNS,
)

logger = logging.getLogger(__name__)

MASTER_CSV = os.path.join(EXPERIMENT_STUDY_DIR, "master_experiment_results.csv")


def set_global_seed(seed: int = GLOBAL_SEED):
    """Fix all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def _ensure_master_csv():
    """Create the master CSV tracker if it doesn't exist."""
    if not os.path.exists(MASTER_CSV):
        os.makedirs(os.path.dirname(MASTER_CSV), exist_ok=True)
        with open(MASTER_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=TRACKER_COLUMNS)
            writer.writeheader()
        logger.info("Created master experiment tracker: %s", MASTER_CSV)


def append_to_master_csv(row: Dict[str, Any]):
    """Append one experiment result row to the master CSV."""
    _ensure_master_csv()
    with open(MASTER_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKER_COLUMNS, extrasaction="ignore")
        writer.writerow(row)


class ExperimentRunner:
    """
    Context manager and logger for a single experiment run.

    Handles:
    - Seed setting
    - Log file creation per experiment
    - GPU memory tracking
    - Timing
    - Writing results to master CSV
    - Checkpoint path management
    """

    def __init__(
        self,
        experiment_id: str,
        model: str,
        experiment_type: str,
        category: str,
        config: Optional[Dict[str, Any]] = None,
        seed: int = GLOBAL_SEED,
    ):
        self.experiment_id = experiment_id
        self.model = model
        self.experiment_type = experiment_type
        self.category = category
        self.config = config or {}
        self.seed = seed

        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.status = "planned"
        self.metrics: Dict[str, Any] = {}
        self.notes = ""

        # Set up log file
        os.makedirs(LOGS_DIR, exist_ok=True)
        log_fname = f"{experiment_id}_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_path = os.path.join(LOGS_DIR, log_fname)

        # Set up checkpoint dir
        self.checkpoint_dir = os.path.join(CHECKPOINTS_DIR, f"{experiment_id}_{category}")
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def _setup_file_logger(self):
        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(fmt)
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        self._file_handler = file_handler

    def _teardown_file_logger(self):
        if hasattr(self, "_file_handler"):
            logging.getLogger().removeHandler(self._file_handler)
            self._file_handler.close()

    @contextmanager
    def context(self):
        """Context manager that times the experiment and handles exceptions."""
        set_global_seed(self.seed)
        self._setup_file_logger()
        self.start_time = time.time()
        self.status = "running"
        logger.info("=" * 60)
        logger.info("EXPERIMENT: %s | Category: %s | Model: %s",
                    self.experiment_id, self.category, self.model)
        logger.info("Config: %s", json.dumps(self.config, indent=2))
        logger.info("Seed: %d", self.seed)
        logger.info("=" * 60)

        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

        try:
            yield self
            self.status = "completed"
        except Exception as e:
            self.status = "failed"
            self.notes = f"Exception: {type(e).__name__}: {e}\n{traceback.format_exc()}"
            logger.error("Experiment FAILED: %s", self.notes)
            raise
        finally:
            self.end_time = time.time()
            self._write_result()
            self._teardown_file_logger()

    def log_metrics(
        self,
        image_auroc: float = float("nan"),
        pixel_auroc: float = float("nan"),
        average_precision: float = float("nan"),
        precision: float = float("nan"),
        recall: float = float("nan"),
        f1_score: float = float("nan"),
        training_samples: int = 0,
        test_samples: int = 0,
        training_time_s: float = 0.0,
        inference_time_s: float = 0.0,
        notes: str = "",
    ):
        """Record experiment metrics."""
        self.metrics = {
            "image_auroc": image_auroc,
            "pixel_auroc": pixel_auroc,
            "average_precision": average_precision,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "training_samples": training_samples,
            "test_samples": test_samples,
            "training_time_s": training_time_s,
            "inference_time_s": inference_time_s,
        }
        if notes:
            self.notes = notes
        logger.info("Metrics: %s", json.dumps({
            k: round(v, 4) if isinstance(v, float) else v
            for k, v in self.metrics.items()
        }))

    def _write_result(self):
        """Write result row to master CSV."""
        elapsed = (self.end_time - self.start_time) if self.end_time and self.start_time else 0.0

        # GPU memory
        gpu_mb = float("nan")
        if torch.cuda.is_available():
            try:
                gpu_mb = torch.cuda.max_memory_allocated() / 1024 ** 2
            except Exception:
                pass

        config_str = json.dumps({
            k: v for k, v in self.config.items()
            if isinstance(v, (int, float, str, bool))
        })

        row = {
            "experiment_id": self.experiment_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": self.model,
            "category": self.category,
            "experiment_type": self.experiment_type,
            "configuration": config_str,
            "literature_reference": self.config.get("literature", ""),
            "evidence_type": self.config.get("evidence_type", ""),
            "hypothesis": self.config.get("hypothesis", ""),
            "training_samples": self.metrics.get("training_samples", 0),
            "test_samples": self.metrics.get("test_samples", 0),
            "image_auroc": self.metrics.get("image_auroc", float("nan")),
            "pixel_auroc": self.metrics.get("pixel_auroc", float("nan")),
            "average_precision": self.metrics.get("average_precision", float("nan")),
            "precision": self.metrics.get("precision", float("nan")),
            "recall": self.metrics.get("recall", float("nan")),
            "f1_score": self.metrics.get("f1_score", float("nan")),
            "training_time_s": self.metrics.get("training_time_s", elapsed),
            "inference_time_s": self.metrics.get("inference_time_s", 0.0),
            "gpu_memory_mb": gpu_mb,
            "model_size_mb": float("nan"),
            "status": self.status,
            "notes": self.notes,
        }

        try:
            append_to_master_csv(row)
            logger.info("Result written to master CSV. Status: %s", self.status)
        except Exception as e:
            logger.error("Failed to write result to CSV: %s", e)

    def checkpoint_path(self, suffix: str = "") -> str:
        """Return path for saving a model checkpoint for this experiment."""
        fname = f"{self.experiment_id}_{self.category}{suffix}.pt"
        return os.path.join(self.checkpoint_dir, fname)

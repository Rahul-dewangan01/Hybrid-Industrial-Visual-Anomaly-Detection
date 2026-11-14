"""
Computer Networks Module for Industrial Anomaly Detection.

Simulates the impact of lossy/lossless JPEG image compression on anomaly detection
performance across network bandwidth (10 Mbps) and latency (50 ms) constraints.
"""

from .compression_network import (
    compress_image,
    compute_image_quality,
    run_compression_experiment,
)

__all__ = [
    "compress_image",
    "compute_image_quality",
    "run_compression_experiment",
]

"""
Compression & Network Simulation Experiment.

Tests how JPEG compression affects anomaly detection accuracy and
simulates network transmission latency.
"""


import sys as _sys, os as _os
_proj_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..\.."))
_code_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), ".."))
for _p in [_proj_root, _code_root]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)

import os
import io
import time
import logging
import tempfile

import cv2
import numpy as np
import pandas as pd

from utils.config import (
    JPEG_QUALITIES, COMPRESSION_SETTINGS,
    NETWORK_BANDWIDTH_BPS, NETWORK_LATENCY_S,
    IMAGE_SIZE, OUTPUT_DIR, ensure_dirs,
    get_test_images, FEATURE_NAMES,
)
from dip.feature_extraction import load_and_preprocess, extract_features
from dip.baseline_detector import (
    compute_anomaly_score, compute_threshold, evaluate,
)

logger = logging.getLogger(__name__)


def compress_image(img_uint8, quality=None, fmt="png"):
    """Compress image to bytes and return (encoded_bytes, encode_time, decode_time, decoded_img)."""
    if fmt == "png":
        params = [cv2.IMWRITE_PNG_COMPRESSION, 1]
        ext = ".png"
    else:
        params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        ext = ".jpg"

    t0 = time.time()
    success, encoded = cv2.imencode(ext, img_uint8, params)
    encode_time = time.time() - t0

    if not success:
        raise RuntimeError(f"Failed to encode image as {fmt}")

    encoded_bytes = encoded.tobytes()
    file_size = len(encoded_bytes)

    t0 = time.time()
    decoded = cv2.imdecode(np.frombuffer(encoded_bytes, np.uint8), cv2.IMREAD_COLOR)
    decode_time = time.time() - t0

    return encoded_bytes, file_size, encode_time, decode_time, decoded


def compute_image_quality(original, decoded):
    """Compute PSNR and SSIM between original and decoded images."""
    from skimage.metrics import structural_similarity as sk_ssim, peak_signal_noise_ratio
    psnr = peak_signal_noise_ratio(original, decoded, data_range=255)
    gray_o = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    gray_d = cv2.cvtColor(decoded, cv2.COLOR_BGR2GRAY)
    ssim_val = sk_ssim(gray_o, gray_d, data_range=255)
    return psnr, ssim_val


def run_compression_experiment(reference, df_train, baseline_result, cfg=None):
    """Run compression/network simulation on all test images.

    For each compression setting and each test image:
      1. Encode the image
      2. Record file size
      3. Decode
      4. Run detector
      5. Record timings
      6. Compare metrics
    """
    _out = cfg.compression_dir if cfg is not None else OUTPUT_DIR
    if cfg is not None:
        cfg.ensure_output_dirs()
    else:
        ensure_dirs()
    feature_stats = baseline_result["feature_stats"]
    weights = baseline_result["weights"]
    threshold = baseline_result["threshold"]
    y_true = baseline_result["y_true"]

    test_images = cfg.get_test_images() if cfg is not None else get_test_images()

    print("\n" + "=" * 60)
    print("STEP 4: COMPRESSION & NETWORK SIMULATION")
    print("=" * 60)
    print(f"  Test images: {len(test_images)}")
    print(f"  Compression settings: {COMPRESSION_SETTINGS}")
    print(f"  Network bandwidth: {NETWORK_BANDWIDTH_BPS/1e6:.0f} Mbps")
    print(f"  Network latency: {NETWORK_LATENCY_S*1000:.0f} ms")

    # Settings: (label, format, quality)
    settings = [("Original (PNG)", "png", None)]
    for q in JPEG_QUALITIES:
        settings.append((f"JPEG Q{q}", "jpg", q))

    all_rows = []
    per_setting_scores = {}

    for setting_label, fmt, quality in settings:
        logger.info("Processing: %s ...", setting_label)
        scores = []
        setting_rows = []

        for img_path, category, img_id in test_images:
            # Load original
            original_uint8 = cv2.resize(cv2.imread(img_path), IMAGE_SIZE)
            original_size = os.path.getsize(img_path)

            # Compress
            encoded_bytes, compressed_size, enc_time, dec_time, decoded_uint8 = \
                compress_image(original_uint8, quality, fmt)

            # Image quality metrics
            psnr_val, ssim_quality = compute_image_quality(original_uint8, decoded_uint8)

            # Run detector on decoded image
            decoded_f = decoded_uint8.astype(np.float64) / 255.0
            ref_f = reference

            t_inf = time.time()
            features = extract_features(decoded_f, ref_f)
            score = compute_anomaly_score(features, weights, feature_stats)
            inference_time = time.time() - t_inf

            scores.append(score)

            # Network simulation
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            transmission_time = (compressed_size * 8) / NETWORK_BANDWIDTH_BPS
            total_latency = NETWORK_LATENCY_S + transmission_time + enc_time + dec_time + inference_time

            row = {
                "setting": setting_label,
                "image_id": img_id,
                "category": category,
                "is_anomaly": 0 if category == "good" else 1,
                "original_size_bytes": original_size,
                "compressed_size_bytes": compressed_size,
                "compression_ratio": compression_ratio,
                "psnr_db": psnr_val,
                "ssim_quality": ssim_quality,
                "anomaly_score": score,
                "encoding_time_s": enc_time,
                "decoding_time_s": dec_time,
                "inference_time_s": inference_time,
                "transmission_time_s": transmission_time,
                "network_latency_s": NETWORK_LATENCY_S,
                "total_latency_s": total_latency,
            }
            setting_rows.append(row)
            all_rows.append(row)

        per_setting_scores[setting_label] = np.array(scores)

        # Evaluate this setting
        y_scores = np.array(scores)
        metrics = evaluate(y_true, y_scores, threshold)

        avg_size = np.mean([r["compressed_size_bytes"] for r in setting_rows])
        avg_ratio = np.mean([r["compression_ratio"] for r in setting_rows])
        avg_latency = np.mean([r["total_latency_s"] for r in setting_rows])

        logger.info("  %s: AUROC=%.4f F1=%.4f AvgSize=%.0f AvgRatio=%.2f AvgLatency=%.4fs",
                    setting_label,
                    metrics.get("auroc", float("nan")),
                    metrics["f1"], avg_size, avg_ratio, avg_latency)

    # Save detailed results
    df_compression = pd.DataFrame(all_rows)
    comp_path = os.path.join(_out, "compression_results.csv")
    df_compression.to_csv(comp_path, index=False)
    logger.info("Compression results saved to %s", comp_path)

    # Summary table
    print("\n  Compression Summary:")
    print(f"  {'Setting':<18} {'AUROC':>7} {'F1':>7} {'AvgSize':>10} {'Ratio':>7} {'Latency':>10}")
    print("  " + "-" * 62)

    summary_rows = []
    for setting_label, _, _ in settings:
        s_rows = [r for r in all_rows if r["setting"] == setting_label]
        y_s = per_setting_scores[setting_label]
        m = evaluate(y_true, y_s, threshold)
        avg_sz = np.mean([r["compressed_size_bytes"] for r in s_rows])
        avg_r = np.mean([r["compression_ratio"] for r in s_rows])
        avg_lat = np.mean([r["total_latency_s"] for r in s_rows])
        avg_psnr = np.mean([r["psnr_db"] for r in s_rows])
        avg_ssim = np.mean([r["ssim_quality"] for r in s_rows])

        print(f"  {setting_label:<18} "
              f"{m.get('auroc', float('nan')):>7.4f} "
              f"{m['f1']:>7.4f} "
              f"{avg_sz:>10.0f} "
              f"{avg_r:>7.2f}x "
              f"{avg_lat:>9.4f}s")

        summary_rows.append({
            "setting": setting_label,
            "auroc": m.get("auroc", float("nan")),
            "f1": m["f1"],
            "precision": m["precision"],
            "recall": m["recall"],
            "avg_compressed_size": avg_sz,
            "avg_compression_ratio": avg_r,
            "avg_psnr_db": avg_psnr,
            "avg_ssim": avg_ssim,
            "avg_total_latency_s": avg_lat,
            "tp": m["tp"], "fp": m["fp"], "tn": m["tn"], "fn": m["fn"],
        })

    df_summary = pd.DataFrame(summary_rows)
    summary_path = os.path.join(_out, "compression_summary.csv")
    df_summary.to_csv(summary_path, index=False)
    logger.info("Compression summary saved to %s", summary_path)

    return {
        "df_detail": df_compression,
        "df_summary": df_summary,
        "per_setting_scores": per_setting_scores,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from dip.feature_extraction import (
        run_feature_extraction, run_train_feature_extraction,
        compute_reference_image,
    )
    from dip.baseline_detector import run_baseline_detection
    from utils.config import get_train_images

    df_test, ref = run_feature_extraction()
    df_train = run_train_feature_extraction(ref)
    baseline = run_baseline_detection(df_train, df_test)
    run_compression_experiment(ref, df_train, baseline)

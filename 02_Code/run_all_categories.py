"""
Main Entry Point: Multi-Category Benchmark Orchestrator.

Iterates across all 12 valid MVTec AD categories, executes the 11-stage
pipeline for each on GPU/CPU, and aggregates cross-category AUROC and F1
performance matrices, summary heatmaps, and global leaderboards.

Usage:
    python 02_Code/run_all_categories.py
    python 02_Code/run_all_categories.py --categories bottle,cable,tile
    python 02_Code/run_all_categories.py --skip-completed
"""

import os
import sys

# Ensure project root and code directory are on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CODE_DIR = os.path.join(PROJECT_ROOT, "02_Code")
for p in [PROJECT_ROOT, CODE_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from utils.run_all_categories import run_all, parse_args

if __name__ == "__main__":
    args = parse_args()
    cats = args.categories.split(",") if args.categories else None
    run_all(categories=cats, skip_completed=args.skip_completed)

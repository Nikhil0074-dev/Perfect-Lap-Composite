"""
main.py
-------
Entry point for the Perfect Lap Composite analysis pipeline.

Usage:
    python main.py                      # full run with visualizations
    python main.py --no-plots           # skip chart generation
    python main.py --generate-data      # regenerate sample data then run
"""

import argparse
import os
import sys
import time

# Ensure src/ is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from preprocess      import preprocess
from segment_analysis import analyse
from perfect_lap     import run as build_perfect_lap
from comparison      import run as run_comparison
from visualization   import generate_all


def banner(text: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  {text}")
    print(f"{'─' * 50}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Perfect Lap Composite Analysis")
    parser.add_argument("--no-plots",      action="store_true", help="Skip chart generation")
    parser.add_argument("--generate-data", action="store_true", help="Regenerate sample data first")
    args = parser.parse_args()

    t0 = time.perf_counter()

    # ── Optionally regenerate sample data ────────────────────────────────────
    if args.generate_data or not os.path.exists("data/telemetry.csv"):
        banner("Generating sample data")
        os.chdir(os.path.dirname(__file__) or ".")
        import subprocess
        subprocess.run([sys.executable, "data/generate_data.py"], check=True)

    # ── Step 1: Preprocess ───────────────────────────────────────────────────
    banner("Step 1 — Data preprocessing")
    df_raw, df_seg = preprocess("data/telemetry.csv")

    # ── Step 2: Segment analysis ─────────────────────────────────────────────
    banner("Step 2 — Segment analysis")
    best_segments, sector_summ = analyse(df_seg)

    # ── Step 3: Perfect lap ──────────────────────────────────────────────────
    banner("Step 3 — Perfect lap construction")
    perfect_lap = build_perfect_lap(df_seg, best_segments)

    # ── Step 4: Comparison ───────────────────────────────────────────────────
    banner("Step 4 — Lap comparison")
    results = run_comparison(perfect_lap, df_seg)

    # ── Step 5: Visualizations ───────────────────────────────────────────────
    if not args.no_plots:
        banner("Step 5 — Visualization")
        generate_all(
            df_raw,
            results["mini_sector_comparison"],
            results["sector_comparison"],
            results["driver_comparison"],
        )

    elapsed = time.perf_counter() - t0
    banner(f"Pipeline complete in {elapsed:.2f}s")


if __name__ == "__main__":
    main()

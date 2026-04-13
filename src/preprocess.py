"""
preprocess.py
-------------
Step 1: Load, clean, and validate telemetry data.
- Remove duplicate rows
- Drop rows with missing critical fields
- Normalize timestamps per lap (start each lap at 0.0)
- Validate numeric ranges
- Compute per-lap mini-sector times from raw telemetry
"""

import pandas as pd
import numpy as np


REQUIRED_COLUMNS = [
    "lap_id", "lap_type", "lap_num", "mini_sector",
    "timestamp", "distance", "speed", "throttle", "brake",
    "gear", "gps_x", "gps_y", "mini_sector_time"
]

NUMERIC_RANGES = {
    "speed":    (0.0, 400.0),
    "throttle": (0.0, 1.0),
    "brake":    (0.0, 1.0),
    "gear":     (1, 8),
}


def load_telemetry(filepath: str) -> pd.DataFrame:
    """Load telemetry CSV and perform basic validation."""
    df = pd.read_csv(filepath)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Telemetry file is missing columns: {missing}")

    before = len(df)
    df = df.drop_duplicates()
    df = df.dropna(subset=["lap_id", "mini_sector", "timestamp", "speed"])
    after = len(df)
    if before != after:
        print(f"  [preprocess] Removed {before - after} invalid/duplicate rows.")

    return df


def validate_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Clip numeric columns to valid physical ranges."""
    for col, (lo, hi) in NUMERIC_RANGES.items():
        if col in df.columns:
            out_of_range = ((df[col] < lo) | (df[col] > hi)).sum()
            if out_of_range:
                print(f"  [preprocess] Clipping {out_of_range} out-of-range values in '{col}'.")
            df[col] = df[col].clip(lo, hi)
    return df


def normalize_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize timestamps so each lap starts at 0.0."""
    df = df.copy()
    lap_start = df.groupby("lap_id")["timestamp"].transform("min")
    df["timestamp_norm"] = df["timestamp"] - lap_start
    return df


def compute_mini_sector_times(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each (lap_id, mini_sector) group, take the max recorded
    mini_sector_time as the authoritative time for that segment.
    Returns a clean pivot: one row per (lap_id, mini_sector).
    """
    seg_times = (
        df.groupby(["lap_id", "lap_type", "lap_num", "mini_sector"])["mini_sector_time"]
        .max()
        .reset_index()
        .rename(columns={"mini_sector_time": "seg_time"})
    )
    return seg_times


def preprocess(telemetry_path: str = "data/telemetry.csv") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Full preprocessing pipeline.

    Returns
    -------
    df_raw : cleaned, normalized raw telemetry
    df_seg : per (lap_id, mini_sector) segment times
    """
    print("[preprocess] Loading telemetry...")
    df = load_telemetry(telemetry_path)
    df = validate_ranges(df)
    df = normalize_timestamps(df)
    df_seg = compute_mini_sector_times(df)

    print(f"[preprocess] Done. {len(df)} telemetry rows | "
          f"{df['lap_id'].nunique()} laps | "
          f"{df['mini_sector'].nunique()} mini-sectors.")
    return df, df_seg


if __name__ == "__main__":
    df_raw, df_seg = preprocess()
    print(df_seg.head(10).to_string(index=False))

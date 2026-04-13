"""
segment_analysis.py
-------------------
Step 2: For each mini-sector, identify the single fastest time
recorded across all laps and sessions.

Produces:
  - best_segments  : DataFrame with (mini_sector, best_time, source_lap_id, source_lap_type)
  - sector_summary : aggregated S1 / S2 / S3 comparison table
"""

import pandas as pd


# Map mini-sectors to the three standard F1 sectors
MINI_TO_SECTOR = {ms: ("S1" if ms <= 6 else "S2" if ms <= 12 else "S3")
                  for ms in range(1, 19)}


def find_best_segments(df_seg: pd.DataFrame) -> pd.DataFrame:
    """
    For every mini-sector, return the row with the minimum seg_time.

    Parameters
    ----------
    df_seg : DataFrame with columns [lap_id, lap_type, lap_num, mini_sector, seg_time]

    Returns
    -------
    DataFrame with columns:
        mini_sector | best_time | source_lap_id | source_lap_type | source_lap_num
    """
    idx = df_seg.groupby("mini_sector")["seg_time"].idxmin()
    best = df_seg.loc[idx].copy().reset_index(drop=True)
    best = best.rename(columns={
        "seg_time":  "best_time",
        "lap_id":    "source_lap_id",
        "lap_type":  "source_lap_type",
        "lap_num":   "source_lap_num",
    })
    best = best.sort_values("mini_sector").reset_index(drop=True)
    best["sector"] = best["mini_sector"].map(MINI_TO_SECTOR)
    return best


def sector_summary(best_segments: pd.DataFrame, df_seg: pd.DataFrame) -> pd.DataFrame:
    """
    Compare perfect-lap sector times against the actual best qualifying sector.

    Returns a summary table per standard sector (S1, S2, S3).
    """
    best_segments = best_segments.copy()
    best_segments["sector"] = best_segments["mini_sector"].map(MINI_TO_SECTOR)

    # Perfect times per standard sector
    perfect_by_sector = (
        best_segments.groupby("sector")["best_time"]
        .sum()
        .reset_index()
        .rename(columns={"best_time": "perfect_time"})
    )

    # Actual qualifying lap — best total time across qualifying laps
    qual_seg = df_seg[df_seg["lap_type"] == "qualifying"].copy()
    qual_seg["sector"] = qual_seg["mini_sector"].map(MINI_TO_SECTOR)
    qual_lap_times = (
        qual_seg.groupby(["lap_id", "sector"])["seg_time"].sum().reset_index()
    )
    # Find the single fastest qualifying lap overall
    best_qual_lap_id = (
        qual_seg.groupby("lap_id")["seg_time"].sum().idxmin()
    )
    qual_best = qual_lap_times[qual_lap_times["lap_id"] == best_qual_lap_id][["sector", "seg_time"]]
    qual_best = qual_best.rename(columns={"seg_time": "qualifying_time"})

    summary = perfect_by_sector.merge(qual_best, on="sector")
    summary["delta"] = summary["qualifying_time"] - summary["perfect_time"]
    summary["delta_pct"] = (summary["delta"] / summary["perfect_time"] * 100).round(3)
    return summary.sort_values("sector").reset_index(drop=True)


def analyse(df_seg: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Run full segment analysis.

    Returns
    -------
    best_segments : one row per mini-sector
    summary       : one row per standard sector
    """
    print("[segment_analysis] Finding best mini-sector times...")
    best = find_best_segments(df_seg)
    summ = sector_summary(best, df_seg)

    print("[segment_analysis] Done.")
    print("\nBest segments (first 6):")
    print(best[["mini_sector", "sector", "best_time", "source_lap_type", "source_lap_num"]]
          .head(6).to_string(index=False))
    print("\nSector summary:")
    print(summ.to_string(index=False))
    return best, summ


if __name__ == "__main__":
    from preprocess import preprocess
    _, df_seg = preprocess()
    best_segments, summary = analyse(df_seg)

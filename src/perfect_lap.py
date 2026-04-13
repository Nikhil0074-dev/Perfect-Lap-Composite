"""
perfect_lap.py
--------------
Step 3: Construct the theoretical Perfect Lap.

Perfect Lap Time = Sum of best mini-sector times across all sessions.

This module produces:
  - A PerfectLap dataclass summarising times
  - A detailed per-mini-sector breakdown saved to output/perfect_lap_results.csv
"""

import os
from dataclasses import dataclass, field
import pandas as pd


@dataclass
class PerfectLap:
    total_time: float
    mini_sector_breakdown: pd.DataFrame = field(repr=False)
    qualifying_time: float = 0.0
    time_saved: float = 0.0

    def format_time(self, seconds: float) -> str:
        """Convert raw seconds to m:ss.mmm string."""
        minutes = int(seconds // 60)
        secs = seconds - minutes * 60
        return f"{minutes}:{secs:06.3f}"

    def summary(self) -> str:
        lines = [
            "=" * 45,
            "         PERFECT LAP COMPOSITE RESULT",
            "=" * 45,
            f"  Perfect Lap Time  : {self.format_time(self.total_time)}",
            f"  Qualifying Lap    : {self.format_time(self.qualifying_time)}",
            f"  Time Saved        : {self.time_saved:+.3f}s",
            "=" * 45,
        ]
        return "\n".join(lines)


def build_perfect_lap(
    best_segments: pd.DataFrame,
    df_seg: pd.DataFrame,
) -> PerfectLap:
    """
    Construct the PerfectLap object.

    Parameters
    ----------
    best_segments : output of segment_analysis.find_best_segments()
    df_seg        : cleaned per-segment times from preprocess()
    """
    perfect_time = float(best_segments["best_time"].sum())

    # Best qualifying lap time
    qual_lap_totals = (
        df_seg[df_seg["lap_type"] == "qualifying"]
        .groupby("lap_id")["seg_time"]
        .sum()
    )
    qualifying_time = float(qual_lap_totals.min()) if not qual_lap_totals.empty else 0.0
    time_saved = qualifying_time - perfect_time

    breakdown = best_segments[[
        "mini_sector", "sector", "best_time",
        "source_lap_type", "source_lap_num"
    ]].copy()
    breakdown["cumulative_time"] = breakdown["best_time"].cumsum()

    return PerfectLap(
        total_time=perfect_time,
        mini_sector_breakdown=breakdown,
        qualifying_time=qualifying_time,
        time_saved=time_saved,
    )


def save_results(perfect_lap: PerfectLap, output_dir: str = "output") -> None:
    """Save the mini-sector breakdown CSV."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "perfect_lap_results.csv")
    perfect_lap.mini_sector_breakdown.to_csv(path, index=False)
    print(f"[perfect_lap] Results saved → {path}")


def run(df_seg: pd.DataFrame, best_segments: pd.DataFrame) -> PerfectLap:
    print("[perfect_lap] Building perfect lap...")
    pl = build_perfect_lap(best_segments, df_seg)
    print(pl.summary())
    save_results(pl)
    return pl


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")
    from preprocess import preprocess
    from segment_analysis import analyse

    _, df_seg = preprocess()
    best_segments, _ = analyse(df_seg)
    run(df_seg, best_segments)

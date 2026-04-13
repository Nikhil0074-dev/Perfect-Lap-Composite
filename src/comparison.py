"""
comparison.py
-------------
Step 4: Compare the Perfect Lap against the actual best qualifying lap
at the mini-sector and standard-sector levels.

Produces:
  - per_mini_sector_comparison : side-by-side time table with delta
  - sector_comparison          : S1/S2/S3 level summary
  - driver_comparison          : multi-driver version (if multiple lap_types used as proxies)
"""

import pandas as pd
from perfect_lap import PerfectLap


def per_mini_sector_comparison(
    perfect_lap: PerfectLap,
    df_seg: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build a row-by-row comparison of the best qualifying mini-sector times
    versus the perfect-lap mini-sector times.
    """
    # Identify the best qualifying lap
    qual = df_seg[df_seg["lap_type"] == "qualifying"].copy()
    best_qual_id = qual.groupby("lap_id")["seg_time"].sum().idxmin()
    qual_best = qual[qual["lap_id"] == best_qual_id][["mini_sector", "seg_time"]].copy()
    qual_best = qual_best.rename(columns={"seg_time": "qualifying_time"})

    perfect = perfect_lap.mini_sector_breakdown[
        ["mini_sector", "sector", "best_time", "source_lap_type", "source_lap_num"]
    ].copy()

    comp = perfect.merge(qual_best, on="mini_sector", how="left")
    comp["delta"] = comp["qualifying_time"] - comp["best_time"]
    comp["delta_pct"] = (comp["delta"] / comp["best_time"] * 100).round(3)
    comp = comp.sort_values("mini_sector").reset_index(drop=True)
    return comp


def sector_comparison(comp: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the mini-sector comparison up to S1/S2/S3."""
    return (
        comp.groupby("sector")
        .agg(
            perfect_time=("best_time", "sum"),
            qualifying_time=("qualifying_time", "sum"),
            delta=("delta", "sum"),
        )
        .assign(delta_pct=lambda df: (df["delta"] / df["perfect_time"] * 100).round(3))
        .reset_index()
        .sort_values("sector")
    )


def driver_comparison(df_seg: pd.DataFrame) -> pd.DataFrame:
    """
    Treat each lap_type as a 'driver' (fp1=Driver A, fp2=Driver B, qualifying=Driver C)
    and build a perfect-lap time for each.  Useful for multi-driver setups.
    """
    rows = []
    for lap_type, grp in df_seg.groupby("lap_type"):
        idx = grp.groupby("mini_sector")["seg_time"].idxmin()
        best_per_ms = grp.loc[idx, "seg_time"].sum()
        actual_best = grp.groupby("lap_id")["seg_time"].sum().min()
        rows.append({
            "driver_or_session": lap_type,
            "theoretical_best": round(best_per_ms, 4),
            "actual_best_lap": round(actual_best, 4),
            "potential_gain": round(actual_best - best_per_ms, 4),
        })
    return pd.DataFrame(rows).sort_values("theoretical_best").reset_index(drop=True)


def run(perfect_lap: PerfectLap, df_seg: pd.DataFrame) -> dict:
    print("[comparison] Running lap comparisons...")

    ms_comp = per_mini_sector_comparison(perfect_lap, df_seg)
    s_comp  = sector_comparison(ms_comp)
    d_comp  = driver_comparison(df_seg)

    print("\nMini-sector comparison (first 6 rows):")
    print(ms_comp[["mini_sector","sector","best_time","qualifying_time","delta"]].head(6).to_string(index=False))

    print("\nStandard sector comparison:")
    print(s_comp.to_string(index=False))

    print("\nSession / driver comparison:")
    print(d_comp.to_string(index=False))

    return {
        "mini_sector_comparison": ms_comp,
        "sector_comparison": s_comp,
        "driver_comparison": d_comp,
    }


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")
    from preprocess import preprocess
    from segment_analysis import analyse
    from perfect_lap import run as build_perfect_lap

    _, df_seg = preprocess()
    best_segments, _ = analyse(df_seg)
    pl = build_perfect_lap(df_seg, best_segments)
    run(pl, df_seg)

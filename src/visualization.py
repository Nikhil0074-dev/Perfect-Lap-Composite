"""
visualization.py
----------------
Step 5: Generate all charts and save to output/graphs/.

Charts produced:
  1. sector_bar_chart.png       – S1/S2/S3 perfect vs qualifying
  2. mini_sector_bar_chart.png  – all 18 mini-sectors
  3. speed_vs_distance.png      – speed trace comparison
  4. time_delta.png             – cumulative time delta
  5. time_loss_heatmap.png      – 18-cell colour heatmap
  6. driver_comparison.png      – session/driver bar chart
"""

import os
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend for scripting
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

warnings.filterwarnings("ignore")

OUTPUT_DIR = os.path.join("output", "graphs")

# ── Colour palette ──────────────────────────────────────────────────────────
C_PERFECT  = "#22c55e"   # green
C_QUAL     = "#E24B4A"   # red
C_DELTA    = "#EF9F27"   # amber
C_BG       = "#0f0f0f"   # dark background
C_GRID     = "#2a2a2a"
C_TEXT     = "#e0e0e0"
C_TEXT2    = "#9a9a9a"

STYLE = {
    "axes.facecolor":    C_BG,
    "figure.facecolor":  C_BG,
    "axes.edgecolor":    C_GRID,
    "axes.labelcolor":   C_TEXT,
    "xtick.color":       C_TEXT2,
    "ytick.color":       C_TEXT2,
    "text.color":        C_TEXT,
    "grid.color":        C_GRID,
    "grid.linestyle":    "--",
    "grid.linewidth":    0.5,
    "axes.titlesize":    12,
    "axes.labelsize":    10,
    "axes.titleweight":  "bold",
    "font.family":       "monospace",
}


def _apply_style():
    plt.rcParams.update(STYLE)


def _save(fig: plt.Figure, name: str) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  [viz] Saved → {path}")


# ── 1. Sector bar chart ──────────────────────────────────────────────────────
def sector_bar_chart(sector_comp: pd.DataFrame) -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(8, 4))

    x = np.arange(len(sector_comp))
    w = 0.35
    bars_p = ax.bar(x - w/2, sector_comp["perfect_time"],  w, color=C_PERFECT, label="Perfect Lap",  zorder=3)
    bars_q = ax.bar(x + w/2, sector_comp["qualifying_time"], w, color=C_QUAL,    label="Qualifying",   zorder=3)

    for bar in bars_p:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{bar.get_height():.3f}s", ha="center", va="bottom", fontsize=7.5, color=C_PERFECT)
    for bar in bars_q:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{bar.get_height():.3f}s", ha="center", va="bottom", fontsize=7.5, color=C_QUAL)

    ax.set_xticks(x)
    ax.set_xticklabels(sector_comp["sector"])
    ax.set_ylabel("Time (s)")
    ax.set_title("Sector Comparison — Perfect Lap vs Qualifying")
    ax.legend(framealpha=0.2, fontsize=9)
    ax.yaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
    _save(fig, "sector_bar_chart.png")


# ── 2. Mini-sector bar chart ─────────────────────────────────────────────────
def mini_sector_bar_chart(ms_comp: pd.DataFrame) -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(14, 5))

    x = np.arange(len(ms_comp))
    w = 0.4
    ax.bar(x - w/2, ms_comp["best_time"],       w, color=C_PERFECT, label="Perfect",    zorder=3)
    ax.bar(x + w/2, ms_comp["qualifying_time"], w, color=C_QUAL,    label="Qualifying", zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels([f"MS{i}" for i in ms_comp["mini_sector"]], rotation=45, fontsize=8)
    ax.set_ylabel("Time (s)")
    ax.set_title("Mini-Sector Times — Perfect Lap vs Qualifying")
    ax.legend(framealpha=0.2, fontsize=9)
    ax.yaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
    _save(fig, "mini_sector_bar_chart.png")


# ── 3. Speed vs distance ─────────────────────────────────────────────────────
def speed_vs_distance(df_raw: pd.DataFrame) -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(12, 4))

    qual = df_raw[df_raw["lap_type"] == "qualifying"]
    best_lap_id = qual.groupby("lap_id")["timestamp"].max().idxmin()

    # Perfect composite – average best telemetry per distance bucket
    all_laps = df_raw.copy()
    all_laps["dist_bucket"] = (all_laps["distance"] // 100) * 100
    perfect_trace = all_laps.groupby("dist_bucket")["speed"].min().reset_index()

    qual_trace = (
        qual[qual["lap_id"] == best_lap_id][["distance", "speed"]]
        .sort_values("distance")
    )

    ax.plot(perfect_trace["dist_bucket"], perfect_trace["speed"],
            color=C_PERFECT, lw=1.8, label="Perfect Lap", zorder=3)
    ax.plot(qual_trace["distance"], qual_trace["speed"],
            color=C_QUAL, lw=1.2, ls="--", alpha=0.8, label="Qualifying", zorder=2)

    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Speed vs Distance")
    ax.legend(framealpha=0.2, fontsize=9)
    ax.yaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
    _save(fig, "speed_vs_distance.png")


# ── 4. Cumulative time delta ─────────────────────────────────────────────────
def time_delta_chart(ms_comp: pd.DataFrame) -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(12, 4))

    deltas = ms_comp["delta"].values
    cumulative = np.cumsum(deltas)
    x = ms_comp["mini_sector"].values

    ax.axhline(0, color=C_TEXT2, lw=0.8, ls="--")
    ax.fill_between(x, 0, cumulative, where=(cumulative >= 0),
                    alpha=0.15, color=C_QUAL, interpolate=True)

    colors = [C_PERFECT if d < 0.05 else C_DELTA if d < 0.1 else C_QUAL for d in deltas]
    ax.scatter(x, cumulative, color=colors, s=45, zorder=5)
    ax.plot(x, cumulative, color=C_DELTA, lw=1.5, zorder=4)

    # Final delta annotation
    ax.annotate(
        f"Total: +{cumulative[-1]:.3f}s",
        xy=(x[-1], cumulative[-1]),
        xytext=(-30, 15), textcoords="offset points",
        fontsize=9, color=C_QUAL,
        arrowprops=dict(arrowstyle="->", color=C_QUAL, lw=0.8),
    )

    ax.set_xlabel("Mini-Sector")
    ax.set_ylabel("Cumulative Delta (s)")
    ax.set_title("Cumulative Time Delta — Qualifying vs Perfect Lap")
    ax.set_xticks(x)
    ax.set_xticklabels([f"MS{i}" for i in x], rotation=45, fontsize=8)
    ax.yaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
    _save(fig, "time_delta.png")


# ── 5. Time-loss heatmap ─────────────────────────────────────────────────────
def time_loss_heatmap(ms_comp: pd.DataFrame) -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(12, 3))

    n = len(ms_comp)
    deltas = ms_comp["delta"].values.reshape(1, n)

    cmap = LinearSegmentedColormap.from_list(
        "rg", [C_PERFECT, C_DELTA, C_QUAL], N=256
    )
    im = ax.imshow(deltas, cmap=cmap, aspect="auto",
                   vmin=0, vmax=max(0.001, deltas.max()))

    ax.set_xticks(range(n))
    ax.set_xticklabels([f"MS{i}" for i in ms_comp["mini_sector"]], fontsize=8)
    ax.set_yticks([])
    ax.set_title("Mini-Sector Time-Loss Heatmap (green = fast, red = slow)")

    for i in range(n):
        ax.text(i, 0, f"{ms_comp['delta'].iloc[i]*1000:.0f}ms",
                ha="center", va="center", fontsize=7, color="white")

    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", pad=0.35, fraction=0.05)
    cbar.ax.tick_params(labelsize=8, colors=C_TEXT2)
    cbar.set_label("Time lost (s)", fontsize=8, color=C_TEXT2)
    _save(fig, "time_loss_heatmap.png")


# ── 6. Driver / session comparison ───────────────────────────────────────────
def driver_comparison_chart(driver_comp: pd.DataFrame) -> None:
    _apply_style()
    fig, ax = plt.subplots(figsize=(8, 4))

    sessions = driver_comp["driver_or_session"]
    x = np.arange(len(sessions))
    w = 0.35

    ax.bar(x - w/2, driver_comp["theoretical_best"], w, color=C_PERFECT, label="Theoretical best", zorder=3)
    ax.bar(x + w/2, driver_comp["actual_best_lap"],  w, color=C_QUAL,    label="Actual best lap",  zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(sessions, fontsize=9)
    ax.set_ylabel("Lap Time (s)")
    ax.set_title("Session Comparison — Theoretical vs Actual Best Lap")
    ax.legend(framealpha=0.2, fontsize=9)
    ax.yaxis.grid(True, zorder=0)
    ax.set_axisbelow(True)
    _save(fig, "driver_comparison.png")


# ── Master runner ─────────────────────────────────────────────────────────────
def generate_all(
    df_raw: pd.DataFrame,
    ms_comp: pd.DataFrame,
    sector_comp: pd.DataFrame,
    driver_comp: pd.DataFrame,
) -> None:
    print("[visualization] Generating charts...")
    sector_bar_chart(sector_comp)
    mini_sector_bar_chart(ms_comp)
    speed_vs_distance(df_raw)
    time_delta_chart(ms_comp)
    time_loss_heatmap(ms_comp)
    driver_comparison_chart(driver_comp)
    print(f"[visualization] All charts saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "src")
    from preprocess import preprocess
    from segment_analysis import analyse
    from perfect_lap import run as build_perfect_lap
    from comparison import run as run_comparison

    df_raw, df_seg = preprocess()
    best_segments, _ = analyse(df_seg)
    pl = build_perfect_lap(df_seg, best_segments)
    results = run_comparison(pl, df_seg)

    generate_all(
        df_raw,
        results["mini_sector_comparison"],
        results["sector_comparison"],
        results["driver_comparison"],
    )

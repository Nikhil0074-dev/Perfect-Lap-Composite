# Perfect Lap Composite - Telemetry-Based Analysis

A data-driven system that reconstructs a driver's theoretical fastest lap
by combining the best mini-sector times recorded across a full race(F1 race) weekend.

---

## Project Structure

```
perfect-lap-analysis/
│
├── data/
│   ├── generate_data.py      ← generates sample telemetry.csv & laps.csv
│   ├── telemetry.csv         ← raw telemetry (auto-generated)
│   └── laps.csv              ← lap metadata (auto-generated)
│
├── src/
│   ├── preprocess.py         ← Step 1: clean, normalize, segment
│   ├── segment_analysis.py   ← Step 2: find best mini-sector times
│   ├── perfect_lap.py        ← Step 3: construct perfect lap
│   ├── comparison.py         ← Step 4: compare vs qualifying
│   └── visualization.py      ← Step 5: generate all charts
│
├── output/
│   ├── perfect_lap_results.csv
│   └── graphs/               ← all .png charts saved here
│
├── notebook/
│   └── analysis.ipynb        ← interactive Jupyter walkthrough
│
├── main.py                   ← pipeline entry point
├── requirements.txt
└── README.md
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full pipeline (generates data automatically)
python main.py --generate-data

# 3. Or open the notebook
jupyter notebook notebook/analysis.ipynb
```

---

## Pipeline Overview

```
Step 1  preprocess.py     → Clean telemetry, normalize timestamps, compute mini-sector times
Step 2  segment_analysis.py → Find minimum time per mini-sector across all laps/sessions
Step 3  perfect_lap.py    → Sum best segments → theoretical perfect lap time
Step 4  comparison.py     → Compare perfect lap vs actual qualifying lap (delta analysis)
Step 5  visualization.py  → Generate 6 charts: bar, speed trace, delta, heatmap, driver comparison
```

### Perfect Lap Formula

```
Perfect Lap Time = Σ min(mini_sector_i_time)  for i in 1..18
```

---

## Output Charts

| File | Description |
|------|-------------|
| `sector_bar_chart.png` | S1/S2/S3 — perfect vs qualifying |
| `mini_sector_bar_chart.png` | All 18 mini-sectors side by side |
| `speed_vs_distance.png` | Speed trace across track distance |
| `time_delta.png` | Cumulative time delta per mini-sector |
| `time_loss_heatmap.png` | Colour-coded time loss per segment |
| `driver_comparison.png` | Theoretical vs actual best per session |

---

## Sample Output

```
=============================================
         PERFECT LAP COMPOSITE RESULT
=============================================
  Perfect Lap Time  : 1:28.452
  Qualifying Lap    : 1:29.103
  Time Saved        : +0.651s
=============================================
```

---

## Key Concepts

- **Mini-sector**: Track divided into 18 segments (~250–320 m each)
- **Perfect Lap**: Theoretical construct - not physically achievable in a single lap
- **Delta**: Time difference between the perfect lap and the actual qualifying lap
- **Heatmap**: Visual tool to identify which segments have the most recoverable time

---

## Future Scope

- Real-time telemetry ingestion (WebSocket / live feed)
- Multi-driver corner-by-corner comparison
- ML-based lap improvement prediction
- Integration with racing simulators (ACC, iRacing)

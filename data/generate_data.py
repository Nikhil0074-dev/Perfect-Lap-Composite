"""
Script to generate realistic sample telemetry and lap data for testing.
Run this once to create data/telemetry.csv and data/laps.csv
"""
import csv
import math
import random

random.seed(42)

LAP_TYPES = ["fp1", "fp2", "qualifying"]
LAPS_PER_TYPE = {"fp1": 8, "fp2": 8, "qualifying": 3}
NUM_MINI_SECTORS = 18
TRACK_LENGTH = 5000  # metres

# Base mini-sector lengths (metres)
SECTOR_LENGTHS = [260, 290, 310, 280, 250, 270, 300, 320, 290,
                  260, 280, 310, 270, 290, 260, 300, 310, 280]

# Base speeds per mini-sector (km/h)
BASE_SPEEDS = [280, 305, 315, 290, 260, 250, 310, 320, 315,
               300, 290, 280, 320, 335, 310, 290, 265, 305]

# Base time per mini-sector (seconds)
BASE_TIMES = [s / (v / 3.6) for s, v in zip(SECTOR_LENGTHS, BASE_SPEEDS)]


def jitter(val, pct=0.03):
    return val * (1 + random.uniform(-pct, pct))


telemetry_rows = []
lap_rows = []
lap_id = 0

for lap_type in LAP_TYPES:
    n_laps = LAPS_PER_TYPE[lap_type]
    for lap_num in range(1, n_laps + 1):
        lap_id += 1
        timestamp = 0.0
        distance = 0.0
        lap_time = 0.0
        gear_base = [3, 4, 5, 4, 3, 3, 5, 6, 5, 4, 4, 4, 6, 7, 5, 4, 3, 5]

        for ms in range(NUM_MINI_SECTORS):
            ms_time = jitter(BASE_TIMES[ms], pct=0.025)
            ms_length = SECTOR_LENGTHS[ms]
            n_points = max(4, ms_length // 60)
            speed_base = BASE_SPEEDS[ms]

            for pt in range(n_points):
                frac = pt / n_points
                speed = jitter(speed_base * (0.95 + 0.1 * math.sin(math.pi * frac)), pct=0.01)
                throttle = max(0.0, min(1.0, jitter(0.75 + 0.2 * math.sin(math.pi * frac), pct=0.05)))
                brake = max(0.0, min(1.0, 1.0 - throttle - random.uniform(0, 0.1)))
                gear = gear_base[ms] + (1 if frac > 0.6 else 0)
                gear = max(1, min(8, gear))
                x = distance * math.cos(distance / 800)
                y = distance * math.sin(distance / 800)

                telemetry_rows.append({
                    "lap_id": lap_id,
                    "lap_type": lap_type,
                    "lap_num": lap_num,
                    "mini_sector": ms + 1,
                    "timestamp": round(timestamp + frac * ms_time, 4),
                    "distance": round(distance + frac * ms_length, 2),
                    "speed": round(speed, 2),
                    "throttle": round(throttle, 3),
                    "brake": round(brake, 3),
                    "gear": gear,
                    "gps_x": round(x, 2),
                    "gps_y": round(y, 2),
                    "mini_sector_time": round(ms_time, 4),
                })

            timestamp += ms_time
            distance += ms_length
            lap_time += ms_time

        lap_rows.append({
            "lap_id": lap_id,
            "lap_type": lap_type,
            "lap_num": lap_num,
            "lap_time": round(lap_time, 4),
        })

# Write telemetry.csv
with open("data/telemetry.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=telemetry_rows[0].keys())
    writer.writeheader()
    writer.writerows(telemetry_rows)

# Write laps.csv
with open("data/laps.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=lap_rows[0].keys())
    writer.writeheader()
    writer.writerows(lap_rows)

print(f"Generated {len(telemetry_rows)} telemetry rows across {lap_id} laps.")
print("Files written: data/telemetry.csv, data/laps.csv")

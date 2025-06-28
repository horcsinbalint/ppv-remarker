import csv
import sys

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def read_data(log_file):
    timestamps = []
    byte_counts = []
    try:
        with open(log_file, "r") as f:
            reader = csv.DictReader(f)
            raw_timestamps = []
            for row in reader:
                ts = float(row["timestamp"])
                raw_timestamps.append(ts)
                bc = float(row["byte_count"])
                byte_counts.append(bc/1000000)
            if raw_timestamps:
                min_ts = min(raw_timestamps)
                timestamps = [ts - min_ts for ts in raw_timestamps]
    except Exception:
        pass
    return timestamps, byte_counts

IS_PDF = "--pdf" in sys.argv
if IS_PDF:
    sys.argv.remove("--pdf")

if len(sys.argv) < 2:
    print("Usage: python plot_data_rate.py <log_file1.csv> [<log_file2.csv> ...] [--pdf]")
    sys.exit(1)

log_files = sys.argv[1:]

fig, ax = plt.subplots(figsize=(10, 5))
lines = []
for _ in log_files:
    line, = ax.plot([], [])
    lines.append(line)
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Received data (MB)")
ax.set_title("Received data over time")
ax.grid(True)
plt.tight_layout()

def update(frame):
    for idx, log_file in enumerate(log_files):
        timestamps, byte_counts = read_data(log_file)
        lines[idx].set_data(timestamps, byte_counts)
    ax.relim()
    if not IS_PDF:
        ax.autoscale_view()
    ax.legend(log_files)
    return lines

if not IS_PDF:
    ani = FuncAnimation(fig, update, interval=1000)

if IS_PDF:
    update(fig)
    ax.autoscale_view()

if IS_PDF:
    plt.savefig("bytes_sent.pdf")
    plt.savefig("img/received_data.svg")
else:
    plt.show()
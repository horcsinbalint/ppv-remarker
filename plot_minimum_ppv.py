import csv
import datetime

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def read_data():
    timestamps = []
    new_regs = []
    try:
        with open("reg_history.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                timestamps.append(datetime.datetime.fromtimestamp(float(row["timestamp"])))
                new_regs.append(float(row["new_reg"]))
    except FileNotFoundError:
        print("[ERROR] 'reg_history.csv' not found. Run a simulation (e.g., 'make controller') to generate it.")
    except Exception as e:
        print(f"[ERROR] Could not read 'reg_history.csv': {e}")
    return timestamps, new_regs

fig, ax = plt.subplots(figsize=(10, 5))
line, = ax.plot([], [])
ax.set_xlabel("Time")
ax.set_ylabel("Minimum PPV")
ax.set_title("Minimum PPV over Time")
plt.tight_layout()

def update(frame):
    timestamps, new_regs = read_data()
    line.set_data(timestamps, new_regs)
    ax.relim()
    ax.autoscale_view()
    return line,

ani = FuncAnimation(fig, update, interval=1000)

plt.show()

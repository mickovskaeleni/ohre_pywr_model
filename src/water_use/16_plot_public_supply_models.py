import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "outputs"

INPUT_PATH = (
    OUTPUT_DIR /
    "public_supply_model_v2.csv"
)

# ======================================================
# LOAD
# ======================================================

print("Loading model results...")

df = pd.read_csv(INPUT_PATH)

# ======================================================
# PLOT 1
# PER-CAPITA DEMAND
# ======================================================

plt.figure(figsize=(10, 6))

plt.plot(
    df["YEAR"],
    df["OBSERVED_Q"],
    marker="o",
    label="Observed q(t)"
)

plt.plot(
    df["YEAR"],
    df["PREDICTED_Q"],
    linestyle="--",
    label="Linear trend q(t)"
)

plt.xlabel("Year")
plt.ylabel("Per-capita abstraction")
plt.title(
    "Observed vs modelled per-capita abstraction"
)

plt.grid(True)
plt.legend()

plot1 = (
    OUTPUT_DIR /
    "public_supply_per_capita_trend.png"
)

plt.savefig(
    plot1,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ======================================================
# PLOT 2
# DEMAND MODEL
# ======================================================

plt.figure(figsize=(10, 6))

plt.plot(
    df["YEAR"],
    df["TOTAL_MVM"],
    marker="o",
    label="Observed abstraction"
)

plt.plot(
    df["YEAR"],
    df["PREDICTED_MVM_V2"],
    linestyle="--",
    label="Model V2"
)

plt.xlabel("Year")
plt.ylabel("MVM")
plt.title(
    "Observed vs modelled public water abstractions"
)

plt.grid(True)
plt.legend()

plot2 = (
    OUTPUT_DIR /
    "public_supply_model_v2_fit.png"
)

plt.savefig(
    plot2,
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ======================================================
# REPORT
# ======================================================

print("\nSaved:")
print(plot1)
print(plot2)

print("\nDone.")
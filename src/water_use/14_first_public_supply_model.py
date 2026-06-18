import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.metrics import r2_score, mean_absolute_error

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "outputs"

POP_PATH = (
    OUTPUT_DIR /
    "pilot_population_2000_2022.csv"
)

MVM_PATH = (
    OUTPUT_DIR /
    "public_supply_yearly_mvm.csv"
)

# ======================================================
# LOAD
# ======================================================

print("Loading population...")

pop = pd.read_csv(
    POP_PATH
)

print("Loading observed MVM...")

mvm = pd.read_csv(
    MVM_PATH
)

# ======================================================
# STANDARDIZE
# ======================================================

pop["YEAR"] = pd.to_numeric(
    pop["YEAR"],
    errors="coerce"
)

mvm["YEAR"] = pd.to_numeric(
    mvm["YEAR"],
    errors="coerce"
)

# ======================================================
# MERGE
# ======================================================

df = pop.merge(
    mvm,
    on="YEAR",
    how="inner"
)

print(
    "\nYears available:",
    len(df)
)

# ======================================================
# FIRST MODEL
# ======================================================

# q = average annual abstraction per person

q = (
    df["TOTAL_MVM"].sum()
    /
    df["POPULATION"].sum()
)

print(
    f"\nPer-capita coefficient q = {q:.6f}"
)

# ======================================================
# PREDICTION
# ======================================================

df["PREDICTED_MVM"] = (
    df["POPULATION"] * q
)

# ======================================================
# PERFORMANCE
# ======================================================

r2 = r2_score(
    df["TOTAL_MVM"],
    df["PREDICTED_MVM"]
)

mae = mean_absolute_error(
    df["TOTAL_MVM"],
    df["PREDICTED_MVM"]
)

rmse = np.sqrt(
    np.mean(
        (
            df["TOTAL_MVM"]
            - df["PREDICTED_MVM"]
        ) ** 2
    )
)

# ======================================================
# PER CAPITA SERIES
# ======================================================

df["OBSERVED_PER_CAPITA"] = (
    df["TOTAL_MVM"]
    / df["POPULATION"]
)

# ======================================================
# SAVE
# ======================================================

output_path = (
    OUTPUT_DIR /
    "public_supply_first_model.csv"
)

df.to_csv(
    output_path,
    index=False
)

# ======================================================
# REPORT
# ======================================================

print("\n====================")
print("MODEL PERFORMANCE")
print("====================")

print(
    f"R²   : {r2:.4f}"
)

print(
    f"MAE  : {mae:.2f}"
)

print(
    f"RMSE : {rmse:.2f}"
)

print(
    "\nAverage per-capita demand:"
)

print(
    df["OBSERVED_PER_CAPITA"]
    .mean()
)

print("\n====================")
print("FIRST YEARS")
print("====================")

print(
    df[
        [
            "YEAR",
            "POPULATION",
            "TOTAL_MVM",
            "PREDICTED_MVM",
            "OBSERVED_PER_CAPITA"
        ]
    ].head()
)

print(
    "\nSaved:"
)

print(output_path)

print("\nDone.")
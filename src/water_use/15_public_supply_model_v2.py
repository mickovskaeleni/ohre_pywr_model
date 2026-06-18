import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "outputs"

INPUT_PATH = (
    OUTPUT_DIR /
    "public_supply_first_model.csv"
)

# ======================================================
# LOAD
# ======================================================

print("Loading V1 results...")

df = pd.read_csv(INPUT_PATH)

# ======================================================
# OBSERVED q(t)
# ======================================================

df["OBSERVED_Q"] = (
    df["TOTAL_MVM"]
    /
    df["POPULATION"]
)

# ======================================================
# FIT TREND
# ======================================================

X = df[["YEAR"]]

y = df["OBSERVED_Q"]

model = LinearRegression()

model.fit(X, y)

a = model.intercept_
b = model.coef_[0]

print("\n====================")
print("q(t) MODEL")
print("====================")

print(f"Intercept = {a:.6f}")
print(f"Slope     = {b:.8f}")

# ======================================================
# PREDICT q(t)
# ======================================================

df["PREDICTED_Q"] = (
    model.predict(X)
)

# ======================================================
# PREDICT DEMAND
# ======================================================

df["PREDICTED_MVM_V2"] = (
    df["POPULATION"]
    *
    df["PREDICTED_Q"]
)

# ======================================================
# PERFORMANCE
# ======================================================

r2 = r2_score(
    df["TOTAL_MVM"],
    df["PREDICTED_MVM_V2"]
)

mae = mean_absolute_error(
    df["TOTAL_MVM"],
    df["PREDICTED_MVM_V2"]
)

rmse = np.sqrt(
    np.mean(
        (
            df["TOTAL_MVM"]
            -
            df["PREDICTED_MVM_V2"]
        ) ** 2
    )
)

# ======================================================
# SAVE
# ======================================================

output_path = (
    OUTPUT_DIR /
    "public_supply_model_v2.csv"
)

df.to_csv(
    output_path,
    index=False
)

# ======================================================
# REPORT
# ======================================================

print("\n====================")
print("V2 PERFORMANCE")
print("====================")

print(f"R²   : {r2:.4f}")
print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")

print("\n====================")
print("FIRST YEARS")
print("====================")

print(
    df[
        [
            "YEAR",
            "OBSERVED_Q",
            "PREDICTED_Q",
            "TOTAL_MVM",
            "PREDICTED_MVM_V2"
        ]
    ].head()
)

print("\nSaved:")
print(output_path)

print("\nDone.")
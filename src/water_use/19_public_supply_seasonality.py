import pandas as pd

from pathlib import Path

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "outputs"

MONTHLY_PATH = (
    OUTPUT_DIR /
    "public_supply_monthly_mvm.csv"
)

# ======================================================
# LOAD
# ======================================================

print("Loading monthly public supply MVM...")

monthly = pd.read_csv(
    MONTHLY_PATH
)

# ======================================================
# DATE
# ======================================================

monthly["DTM"] = pd.to_datetime(
    monthly["DTM"]
)

monthly["YEAR"] = (
    monthly["DTM"]
    .dt.year
)

monthly["MONTH"] = (
    monthly["DTM"]
    .dt.month
)

# ======================================================
# MONTHLY PATTERN
# ======================================================

monthly_pattern = (
    monthly
    .groupby("MONTH")
    .agg(
        AVG_MVM=("TOTAL_MVM", "mean"),
        STD_MVM=("TOTAL_MVM", "std"),
        N_MONTHS=("TOTAL_MVM", "count")
    )
    .reset_index()
)

# ======================================================
# SEASONAL FACTORS
# ======================================================

overall_mean = (
    monthly_pattern["AVG_MVM"]
    .mean()
)

monthly_pattern["SEASONAL_FACTOR"] = (
    monthly_pattern["AVG_MVM"]
    / overall_mean
)

# ======================================================
# MONTH NAMES
# ======================================================

month_names = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}

monthly_pattern["MONTH_NAME"] = (
    monthly_pattern["MONTH"]
    .map(month_names)
)

# ======================================================
# SORT
# ======================================================

monthly_pattern = (
    monthly_pattern
    .sort_values("MONTH")
)

# ======================================================
# RESULTS
# ======================================================

print("\n====================")
print("PUBLIC SUPPLY SEASONALITY")
print("====================")

print(
    monthly_pattern[
        [
            "MONTH_NAME",
            "AVG_MVM",
            "SEASONAL_FACTOR"
        ]
    ]
)

print("\nAverage factor:")

print(
    round(
        monthly_pattern[
            "SEASONAL_FACTOR"
        ].mean(),
        4
    )
)

print("\nSummer/Winter ratio:")

summer = monthly_pattern[
    monthly_pattern["MONTH"].isin([6,7,8])
]["AVG_MVM"].mean()

winter = monthly_pattern[
    monthly_pattern["MONTH"].isin([12,1,2])
]["AVG_MVM"].mean()

print(
    round(
        summer / winter,
        3
    )
)

# ======================================================
# SAVE
# ======================================================

output_path = (
    OUTPUT_DIR /
    "public_supply_seasonality.csv"
)

monthly_pattern.to_csv(
    output_path,
    index=False
)

print("\nSaved:")

print(output_path)

print("\nDone.")
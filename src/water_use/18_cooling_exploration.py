import pandas as pd
import pyreadr

from pathlib import Path

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"

DESC_PATH = (
    PROCESSED_DIR /
    "water_use_data_descriptive_treated_w_2009.rds"
)

PILOT_TS_PATH = (
    PROCESSED_DIR /
    "pilot_abstractions_timeseries.csv"
)

# ======================================================
# LOAD
# ======================================================

print("Loading descriptive data...")

desc = pyreadr.read_r(
    DESC_PATH
)[None]

print("Loading pilot abstractions...")

pilot_ts = pd.read_csv(
    PILOT_TS_PATH
)

# ======================================================
# PILOT IDS
# ======================================================

pilot_ids = pilot_ts["ID"].unique()

pilot_desc = desc[
    desc["ID"].isin(pilot_ids)
].copy()

print(
    f"\nPilot abstractions: {len(pilot_desc):,}"
)

# ======================================================
# DIAGNOSTICS
# ======================================================

print("\n====================")
print("OD_P_CHL DIAGNOSTIC")
print("====================")

print(
    pilot_desc["OD_P_CHL"]
    .describe()
)

print("\nValue counts:")

print(
    pilot_desc["OD_P_CHL"]
    .value_counts(
        dropna=False
    )
    .head(20)
)

print("\n====================")
print("OD_C_CHL DIAGNOSTIC")
print("====================")

print(
    pilot_desc["OD_C_CHL"]
    .describe()
)

print("\nValue counts:")

print(
    pilot_desc["OD_C_CHL"]
    .value_counts(
        dropna=False
    )
    .head(20)
)

# ======================================================
# FILTER COOLING USERS
# ======================================================

cooling = pilot_desc[
    (
        pilot_desc["OD_P_CHL"]
        .fillna(0) > 0
    )
    |
    (
        pilot_desc["OD_C_CHL"]
        .fillna(0) > 0
    )
].copy()

print("\n====================")
print("COOLING USERS")
print("====================")

print(
    f"Rows: {len(cooling):,}"
)

print(
    f"Unique IDs: {cooling['ID'].nunique():,}"
)

# ======================================================
# JOIN TO TIMESERIES
# ======================================================

merged = pilot_ts.merge(
    cooling[
        [
            "ID",
            "NAZICO",
            "OBEC",
            "OD_P_CHL",
            "OD_C_CHL"
        ]
    ],
    on="ID",
    how="inner"
)

print(
    f"Rows after join: {len(merged):,}"
)

# ======================================================
# DATE
# ======================================================

merged["DTM"] = pd.to_datetime(
    merged["DTM"]
)

merged["YEAR"] = (
    merged["DTM"]
    .dt.year
)

# ======================================================
# YEARLY TREND
# ======================================================

yearly = (
    merged
    .groupby("YEAR")["MVM"]
    .sum()
    .reset_index()
)

# ======================================================
# TOP USERS
# ======================================================

top_users = (
    merged
    .groupby(
        [
            "ID",
            "NAZICO",
            "OBEC"
        ]
    )["MVM"]
    .sum()
    .reset_index()
    .sort_values(
        "MVM",
        ascending=False
    )
)

# ======================================================
# CONCENTRATION
# ======================================================

user_totals = (
    top_users["MVM"]
    .sort_values(
        ascending=False
    )
    .reset_index(drop=True)
)

total_volume = user_totals.sum()

top5_share = (
    user_totals.head(5).sum()
    /
    total_volume
    * 100
)

top10_share = (
    user_totals.head(10).sum()
    /
    total_volume
    * 100
)

# ======================================================
# RESULTS
# ======================================================

print("\n====================")
print("COOLING SUMMARY")
print("====================")

print(
    f"Total volume: {total_volume:,.0f}"
)

print(
    f"Top 5 share: {top5_share:.1f}%"
)

print(
    f"Top 10 share: {top10_share:.1f}%"
)

print("\n====================")
print("TOP 20 USERS")
print("====================")

print(
    top_users.head(20)
)

print("\n====================")
print("YEARLY TREND")
print("====================")

print(
    yearly.head()
)

print(
    yearly.tail()
)

# ======================================================
# SAVE
# ======================================================

top_users.to_csv(
    OUTPUT_DIR /
    "cooling_top_users.csv",
    index=False
)

yearly.to_csv(
    OUTPUT_DIR /
    "cooling_yearly_trend.csv",
    index=False
)

print("\nSaved:")
print(
    OUTPUT_DIR /
    "cooling_top_users.csv"
)

print(
    OUTPUT_DIR /
    "cooling_yearly_trend.csv"
)

print("\nDone.")
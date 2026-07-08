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
OUTPUT_DIR.mkdir(exist_ok=True)

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

pilot_ids = pilot_ts["ID"].unique()

pilot_desc = desc[
    desc["ID"].isin(
        pilot_ids
    )
].copy()

# ======================================================
# KEEP INDUSTRIAL TECHNOLOGY
# ======================================================

industrial = pilot_desc[
    pilot_desc["OD_PR_T"].fillna(0) > 0
].copy()

print(
    "\nIndustrial technology records:",
    len(industrial)
)

print(
    "Unique IDs:",
    industrial["ID"].nunique()
)

# ======================================================
# KEEP LATEST RECORD
# ======================================================

latest = (
    industrial
    .sort_values("ROK")
    .groupby("ID")
    .tail(1)
)

# ======================================================
# CLEAN TEXT
# ======================================================

for col in ["OBOR_FIN", "FIN_SEKCE", "NAZICO"]:

    if col in latest.columns:

        latest[col] = (
            latest[col]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

# ======================================================
# SUMMARY BY FIN_SEKCE
# ======================================================

print("\n====================")
print("FIN_SEKCE")
print("====================")

fin = (
    latest
    .groupby("FIN_SEKCE")
    .agg(
        N_IDS=("ID", "nunique"),
        TOTAL_OD_PR_T=("OD_PR_T", "sum")
    )
    .reset_index()
    .sort_values(
        "TOTAL_OD_PR_T",
        ascending=False
    )
)

print(fin)

# ======================================================
# SUMMARY BY OBOR_FIN
# ======================================================

print("\n====================")
print("OBOR_FIN")
print("====================")

obor = (
    latest
    .groupby("OBOR_FIN")
    .agg(
        N_IDS=("ID", "nunique"),
        TOTAL_OD_PR_T=("OD_PR_T", "sum")
    )
    .reset_index()
    .sort_values(
        "TOTAL_OD_PR_T",
        ascending=False
    )
)

print(obor)

# ======================================================
# FULL TABLE
# ======================================================

result = latest[
    [
        "ID",
        "NAZICO",
        "OBEC",
        "OD_PR_T",
        "FIN_SEKCE",
        "OBOR_FIN"
    ]
].sort_values(
    "OD_PR_T",
    ascending=False
)

print("\n====================")
print("INDUSTRIAL TECHNOLOGY USERS")
print("====================")

print(result)

# ======================================================
# SAVE
# ======================================================

result.to_csv(
    OUTPUT_DIR /
    "industrial_classification.csv",
    index=False
)

fin.to_csv(
    OUTPUT_DIR /
    "industrial_fin_sekce_summary.csv",
    index=False
)

obor.to_csv(
    OUTPUT_DIR /
    "industrial_obor_fin_summary.csv",
    index=False
)

print("\nSaved:")
print(
    OUTPUT_DIR /
    "industrial_classification.csv"
)

print(
    OUTPUT_DIR /
    "industrial_fin_sekce_summary.csv"
)

print(
    OUTPUT_DIR /
    "industrial_obor_fin_summary.csv"
)

print("\nDone.")
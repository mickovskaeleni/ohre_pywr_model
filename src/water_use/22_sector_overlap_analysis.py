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
    desc["ID"].isin(pilot_ids)
].copy()

# ======================================================
# KEEP LATEST RECORD
# ======================================================

latest = (
    pilot_desc
    .sort_values("ROK")
    .groupby("ID")
    .tail(1)
)

# ======================================================
# SECTOR VARIABLES
# ======================================================

sector_cols = [
    "OD_VER_V",
    "OD_PR_T",
    "OD_OST",
    "OD_P_CHL",
    "OD_C_CHL",
    "OD_ZAVL",
    "OD_ZIV_V",
    "OD_PLZ_PMV"
]

sector_names = {
    "OD_VER_V":"Public Supply",
    "OD_PR_T":"Industrial Technology",
    "OD_OST":"Other Industry",
    "OD_P_CHL":"Once-through Cooling",
    "OD_C_CHL":"Circulating Cooling",
    "OD_ZAVL":"Irrigation",
    "OD_ZIV_V":"Livestock",
    "OD_PLZ_PMV":"Mineral Waters"
}

# ======================================================
# COUNT ACTIVE SECTORS
# ======================================================

for c in sector_cols:
    latest[c] = pd.to_numeric(
        latest[c],
        errors="coerce"
    ).fillna(0)

latest["N_ACTIVE_SECTORS"] = (
    latest[sector_cols] > 0
).sum(axis=1)

# ======================================================
# BUILD SUMMARY TABLE
# ======================================================

records = []

for _, row in latest.iterrows():

    active = []

    for col in sector_cols:

        if row[col] > 0:
            active.append(
                sector_names[col]
            )

    records.append({

        "ID": row["ID"],
        "NAZICO": row["NAZICO"],
        "OBEC": row["OBEC"],
        "N_ACTIVE_SECTORS": len(active),
        "SECTORS": "; ".join(active)

    })

summary = pd.DataFrame(records)

# ======================================================
# SAVE
# ======================================================

summary.to_csv(
    OUTPUT_DIR /
    "abstraction_sector_overlap.csv",
    index=False
)

# ======================================================
# REPORT
# ======================================================

print("\n==============================")
print("SECTOR OVERLAP")
print("==============================")

counts = (
    summary["N_ACTIVE_SECTORS"]
    .value_counts()
    .sort_index()
)

for n, c in counts.items():

    pct = 100*c/len(summary)

    print(
        f"{n} sector(s): {c} abstractions ({pct:.1f}%)"
    )

print("\n==============================")
print("MULTI-SECTOR ABSTRACTIONS")
print("==============================")

print(

    summary[
        summary["N_ACTIVE_SECTORS"]>1
    ]
    .sort_values(
        "N_ACTIVE_SECTORS",
        ascending=False
    )

)

print("\nSaved:")
print(
    OUTPUT_DIR /
    "abstraction_sector_overlap.csv"
)

print("\nDone.")
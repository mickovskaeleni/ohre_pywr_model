import pandas as pd
from pathlib import Path

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "outputs"
RAW_DIR = BASE_DIR / "data" / "raw"

PILOT_PATH = (
    OUTPUT_DIR /
    "pilot_municipalities_clean.csv"
)

POPULATION_PATH = (
    RAW_DIR /
    "population_by_municipalities.csv"
)

# ======================================================
# LOAD
# ======================================================

print("Loading pilot municipalities...")

pilot = pd.read_csv(PILOT_PATH)

print("Loading population dataset...")

pop = pd.read_csv(
    POPULATION_PATH,
    sep=None,
    engine="python"
)

# ======================================================
# DETECT MUNICIPALITY COLUMN
# ======================================================

print("\nPopulation columns:")
print(pop.columns.tolist())

# ======================================================
# MUNICIPALITY COLUMN
# ======================================================

MUNICIPALITY_COLUMN = (
    "Region and municipalities-Municipality"
)

# ======================================================
# REMOVE EMPTY MUNICIPALITIES
# ======================================================

pop = pop[
    pop[MUNICIPALITY_COLUMN].notna()
].copy()

# ======================================================
# CLEAN NAMES
# ======================================================

pilot["OBEC_CLEAN"] = (
    pilot["OBEC"]
    .astype(str)
    .str.strip()
    .str.title()
)

pop["OBEC_CLEAN"] = (
    pop[MUNICIPALITY_COLUMN]
    .astype(str)
    .str.strip()
    .str.title()
)

# ======================================================
# MATCH
# ======================================================

matched = pilot.merge(
    pop,
    on="OBEC_CLEAN",
    how="inner"
)

unmatched = pilot[
    ~pilot["OBEC_CLEAN"].isin(
        matched["OBEC_CLEAN"]
    )
]

# ======================================================
# SAVE
# ======================================================

matched_path = (
    OUTPUT_DIR /
    "pilot_municipalities_matched.csv"
)

unmatched_path = (
    OUTPUT_DIR /
    "pilot_municipalities_unmatched.csv"
)

matched.to_csv(
    matched_path,
    index=False
)

unmatched.to_csv(
    unmatched_path,
    index=False
)

# ======================================================
# REPORT
# ======================================================

print("\n====================")
print("MATCH RESULTS")
print("====================")

print(
    "Pilot municipalities:",
    len(pilot)
)

print(
    "Matched:",
    matched["OBEC_CLEAN"].nunique()
)

print(
    "Unmatched:",
    len(unmatched)
)

match_rate = (
    matched["OBEC_CLEAN"].nunique()
    / len(pilot)
    * 100
)

print(
    f"Match rate: {match_rate:.1f}%"
)

print("\n====================")
print("UNMATCHED")
print("====================")

print(
    unmatched.head(50)
)

print("\nSaved:")
print(matched_path)
print(unmatched_path)
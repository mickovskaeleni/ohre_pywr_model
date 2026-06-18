import pandas as pd
from pathlib import Path

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "outputs"
RAW_DIR = BASE_DIR / "data" / "raw"

MATCHED_PATH = (
    OUTPUT_DIR /
    "pilot_municipalities_matched.csv"
)

POPULATION_PATH = (
    RAW_DIR /
    "population_by_municipalities.csv"
)

# ======================================================
# LOAD
# ======================================================

print("Loading matched municipalities...")

matched = pd.read_csv(
    MATCHED_PATH
)

print("Loading population dataset...")

pop = pd.read_csv(
    POPULATION_PATH,
    sep=None,
    engine="python"
)

# ======================================================
# COLUMN NAMES
# ======================================================

MUNICIPALITY_COL = (
    "Region and municipalities-Municipality"
)

YEAR_COL = "Years"

VALUE_COL = "Hodnota"

INDICATOR_COL = "Indicator"

# ======================================================
# CLEAN MUNICIPALITY NAMES
# ======================================================

matched["OBEC_CLEAN"] = (
    matched["OBEC_CLEAN"]
    .astype(str)
    .str.strip()
    .str.title()
)

pop["OBEC_CLEAN"] = (
    pop[MUNICIPALITY_COL]
    .astype(str)
    .str.strip()
    .str.title()
)

# ======================================================
# CHECK INDICATORS
# ======================================================

print("\nAvailable indicators:")

print(
    pop[INDICATOR_COL]
    .drop_duplicates()
    .tolist()
)

# ======================================================
# KEEP POPULATION ONLY
# ======================================================

population = pop[
    pop[INDICATOR_COL]
    .str.contains(
        "Population",
        case=False,
        na=False
    )
].copy()

print(
    "\nRows after population filter:",
    len(population)
)

# ======================================================
# KEEP PILOT MUNICIPALITIES
# ======================================================

population = population[
    population["OBEC_CLEAN"].isin(
        matched["OBEC_CLEAN"]
    )
].copy()

print(
    "Rows after municipality filter:",
    len(population)
)

# ======================================================
# NUMERIC
# ======================================================

population[VALUE_COL] = (
    population[VALUE_COL]
    .astype(str)
    .str.replace(" ", "", regex=False)
)

population[VALUE_COL] = pd.to_numeric(
    population[VALUE_COL],
    errors="coerce"
)

population[YEAR_COL] = pd.to_numeric(
    population[YEAR_COL],
    errors="coerce"
)

# ======================================================
# AGGREGATE
# ======================================================

pilot_population = (
    population
    .groupby(YEAR_COL)[VALUE_COL]
    .sum()
    .reset_index()
)

pilot_population = pilot_population.rename(
    columns={
        YEAR_COL: "YEAR",
        VALUE_COL: "POPULATION"
    }
)

pilot_population = (
    pilot_population
    .sort_values("YEAR")
)

# ======================================================
# SAVE
# ======================================================

output_path = (
    OUTPUT_DIR /
    "pilot_population_2000_2022.csv"
)

pilot_population.to_csv(
    output_path,
    index=False
)

# ======================================================
# PRINT
# ======================================================

print("\n====================")
print("PILOT POPULATION")
print("====================")

print(
    pilot_population.head()
)

print(
    pilot_population.tail()
)

print(
    "\nYears:",
    pilot_population["YEAR"].min(),
    "-",
    pilot_population["YEAR"].max()
)

print(
    "\nSaved:"
)

print(output_path)

print("\nDone.")
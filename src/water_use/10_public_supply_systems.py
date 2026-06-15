import pandas as pd

from pathlib import Path

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "outputs"

INPUT_PATH = (
    OUTPUT_DIR /
    "public_supply_contributors.csv"
)

# ======================================================
# LOAD
# ======================================================

print("Loading contributors...")

df = pd.read_csv(INPUT_PATH)

print(
    "Rows:",
    len(df)
)

# ======================================================
# SYSTEM CLASSIFICATION
# ======================================================

def classify_system(name):

    if pd.isna(name):
        return "UNKNOWN"

    name = str(name).upper()

    if "CHEVAK" in name:
        return "CHEVAK"

    if "VAK K" in name:
        return "VAK_KARLOVY_VARY"

    if "VOSS" in name:
        return "VOSS"

    if "KMS" in name:
        return "KMS_KRASLICE"

    if "NEJDEK" in name:
        return "NEJDEK"

    if "ROTAVA" in name:
        return "ROTAVA"

    return "OTHER"

# ======================================================
# ASSIGN SYSTEM
# ======================================================

df["SYSTEM"] = (
    df["NAZICO"]
    .apply(classify_system)
)

# ======================================================
# AGGREGATE
# ======================================================

systems = (
    df.groupby("SYSTEM")
    .agg(
        TOTAL_MVM=("TOTAL_MVM", "sum"),
        N_IDS=("ID", "nunique")
    )
    .reset_index()
)

systems = systems.sort_values(
    "TOTAL_MVM",
    ascending=False
)

# ======================================================
# SHARES
# ======================================================

total_volume = (
    systems["TOTAL_MVM"]
    .sum()
)

systems["SHARE_%"] = (
    100
    * systems["TOTAL_MVM"]
    / total_volume
)

systems["CUM_SHARE_%"] = (
    systems["SHARE_%"]
    .cumsum()
)

# ======================================================
# SAVE SYSTEM TABLE
# ======================================================

systems_path = (
    OUTPUT_DIR /
    "public_supply_systems.csv"
)

systems.to_csv(
    systems_path,
    index=False
)

# ======================================================
# SAVE ID MAPPING
# ======================================================

mapping_path = (
    OUTPUT_DIR /
    "public_supply_id_to_system.csv"
)

df.to_csv(
    mapping_path,
    index=False
)

# ======================================================
# PRINT
# ======================================================

print("\n====================")
print("SYSTEMS")
print("====================")

print(systems)

print(
    "\nSaved:"
)

print(systems_path)
print(mapping_path)

print("\nDone.")
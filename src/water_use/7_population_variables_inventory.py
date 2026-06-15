import pandas as pd
import geopandas as gpd
import pyreadr

from pathlib import Path
from shapely.geometry import Point

# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

PILOT_PATH = (
    PROCESSED_DIR /
    "southwest_pilot_swbs.csv"
)

SWB_PATH = (
    RAW_DIR /
    "SWB_ohre" /
    "ohre.shp"
)

DESC_PATH = (
    PROCESSED_DIR /
    "water_use_data_descriptive_treated_w_2009.rds"
)

# ======================================================
# LOAD PILOT
# ======================================================

print("Loading pilot...")

pilot = pd.read_csv(
    PILOT_PATH
)

print(
    "Pilot SWBs:",
    len(pilot)
)

# ======================================================
# LOAD SWBs
# ======================================================

print("Loading SWBs...")

swb = gpd.read_file(
    SWB_PATH
)

pilot_swb = swb[
    swb["UPOV_ID"].isin(
        pilot["UPOV_ID"]
    )
].copy()

# ======================================================
# LOAD DESCRIPTIVE DATA
# ======================================================

print("Loading descriptive data...")

desc = pyreadr.read_r(
    DESC_PATH
)[None]

print(
    "Rows:",
    len(desc)
)

# ======================================================
# CREATE POINTS
# ======================================================

desc_xy = desc[
    ["ID", "X", "Y"]
].copy()

desc_xy = desc_xy.dropna(
    subset=["X", "Y"]
)

geometry = [
    Point(xy)
    for xy in zip(
        desc_xy["X"],
        desc_xy["Y"]
    )
]

points = gpd.GeoDataFrame(
    desc_xy,
    geometry=geometry,
    crs="EPSG:5514"
)

points = points.to_crs(
    pilot_swb.crs
)

# ======================================================
# SPATIAL JOIN
# ======================================================

print("Finding pilot abstractions...")

pilot_points = gpd.sjoin(
    points,
    pilot_swb[
        [
            "UPOV_ID",
            "geometry"
        ]
    ],
    how="inner",
    predicate="within"
)

pilot_ids = (
    pilot_points["ID"]
    .drop_duplicates()
)

print(
    "Unique pilot IDs:",
    len(pilot_ids)
)

# ======================================================
# KEEP ONLY PILOT RECORDS
# ======================================================

pilot_desc = desc[
    desc["ID"].isin(
        pilot_ids
    )
].copy()

print(
    "Pilot records:",
    len(pilot_desc)
)

# ======================================================
# KEEP ONLY PUBLIC SUPPLY
# ======================================================

public_supply = pilot_desc[
    pilot_desc["OD_VER_V"].fillna(0) > 0
].copy()

print(
    "Public supply records:",
    len(public_supply)
)

print(
    "Unique public supply IDs:",
    public_supply["ID"].nunique()
)

# ======================================================
# POPULATION VARIABLES
# ======================================================

population_vars = [
    "POC_CELK",
    "POC_NAP_OB",
    "POCOBJ"
]

results = []

print("\n====================")
print("POPULATION VARIABLES")
print("====================")

for var in population_vars:

    if var not in public_supply.columns:
        continue

    non_null = public_supply[var].notna().sum()

    pct_non_null = round(
        100 * non_null / len(public_supply),
        2
    )

    unique_ids = (
        public_supply[
            public_supply[var].notna()
        ]["ID"]
        .nunique()
    )

    results.append(
        {
            "Variable": var,
            "NonNullRows": non_null,
            "PercentNonNull": pct_non_null,
            "UniqueIDs": unique_ids
        }
    )

    print(f"\n{var}")
    print("Non-null rows:", non_null)
    print("Percent:", pct_non_null)
    print("Unique IDs:", unique_ids)

# ======================================================
# SAVE SUMMARY
# ======================================================

summary = pd.DataFrame(
    results
)

summary_path = (
    OUTPUT_DIR /
    "population_variable_summary_pilot.csv"
)

summary.to_csv(
    summary_path,
    index=False
)

# ======================================================
# EXAMPLES
# ======================================================

example_cols = [
    "ID",
    "ROK",
    "NAZICO",
    "OBEC",
    "OD_VER_V",
    "POC_CELK",
    "POC_NAP_OB",
    "POCOBJ"
]

example_cols = [
    c for c in example_cols
    if c in public_supply.columns
]

examples = public_supply[
    public_supply[
        population_vars
    ]
    .notna()
    .any(axis=1)
].copy()

examples = examples[
    example_cols
]

examples_path = (
    OUTPUT_DIR /
    "population_variable_examples_pilot.csv"
)

examples.to_csv(
    examples_path,
    index=False
)

# ======================================================
# TOP PUBLIC SUPPLY ABSTRACTIONS
# ======================================================

inventory = (
    public_supply
    .groupby("ID")
    .agg(
        TOTAL_OD_VER_V=("OD_VER_V", "max")
    )
    .reset_index()
)

latest = (
    public_supply
    .sort_values("ROK")
    .groupby("ID")
    .tail(1)
)

inventory = inventory.merge(
    latest[
        [
            "ID",
            "NAZICO",
            "OBEC",
            "POC_CELK",
            "POC_NAP_OB",
            "POCOBJ"
        ]
    ],
    on="ID",
    how="left"
)

inventory = inventory.sort_values(
    "TOTAL_OD_VER_V",
    ascending=False
)

inventory_path = (
    OUTPUT_DIR /
    "public_supply_population_inventory.csv"
)

inventory.to_csv(
    inventory_path,
    index=False
)

print("\n====================")
print("TOP 20 PUBLIC SUPPLY IDS")
print("====================")

print(
    inventory.head(20)
)

print("\nSaved:")
print(summary_path)
print(examples_path)
print(inventory_path)

print("\nDone.")
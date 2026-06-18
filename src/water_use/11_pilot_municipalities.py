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
# PILOT IDS
# ======================================================

pilot_points = gpd.sjoin(
    points,
    pilot_swb[
        ["UPOV_ID", "geometry"]
    ],
    how="inner",
    predicate="within"
)

pilot_ids = (
    pilot_points["ID"]
    .drop_duplicates()
)

print(
    "Pilot abstraction IDs:",
    len(pilot_ids)
)

# ======================================================
# PILOT RECORDS
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
# CLEAN MUNICIPALITY NAMES
# ======================================================

pilot_desc["OBEC_CLEAN"] = (
    pilot_desc["OBEC"]
    .astype(str)
    .str.strip()
    .str.title()
)

pilot_desc["OBEC_CLEAN"] = (
    pilot_desc["OBEC_CLEAN"]
    .replace("Nan", pd.NA)
)

# ======================================================
# MUNICIPALITY LIST
# ======================================================

municipalities = (
    pilot_desc[
        ["OBEC_CLEAN"]
    ]
    .dropna()
    .drop_duplicates()
    .sort_values("OBEC_CLEAN")
    .reset_index(drop=True)
)

municipalities = municipalities.rename(
    columns={
        "OBEC_CLEAN": "OBEC"
    }
)

# ======================================================
# MUNICIPALITY COUNTS
# ======================================================

municipality_counts = (
    pilot_desc
    .dropna(subset=["OBEC_CLEAN"])
    .groupby("OBEC_CLEAN")
    .agg(
        N_RECORDS=("ID", "count"),
        N_ABSTRACTIONS=("ID", "nunique")
    )
    .reset_index()
    .rename(
        columns={
            "OBEC_CLEAN": "OBEC"
        }
    )
    .sort_values(
        "N_ABSTRACTIONS",
        ascending=False
    )
)

# ======================================================
# SAVE
# ======================================================

municipality_path = (
    OUTPUT_DIR /
    "pilot_municipalities_clean.csv"
)

counts_path = (
    OUTPUT_DIR /
    "pilot_municipality_counts_clean.csv"
)

municipalities.to_csv(
    municipality_path,
    index=False
)

municipality_counts.to_csv(
    counts_path,
    index=False
)

# ======================================================
# PRINT
# ======================================================

print("\n====================")
print("PILOT MUNICIPALITIES")
print("====================")

print(
    municipalities.head(50)
)

print(
    "\nTotal municipalities:",
    len(municipalities)
)

print("\n====================")
print("TOP MUNICIPALITIES")
print("====================")

print(
    municipality_counts.head(20)
)

print("\nSaved:")

print(municipality_path)
print(counts_path)

print("\nDone.")
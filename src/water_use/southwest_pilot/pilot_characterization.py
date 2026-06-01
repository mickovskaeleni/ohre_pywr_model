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

print("Loading pilot region...")

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

print(
    "Pilot polygons:",
    len(pilot_swb)
)


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

print(
    "Columns:",
    len(desc.columns)
)

pd.set_option(
    "display.max_columns",
    None
)

print("\n=== FIRST 10 RECORDS ===")

print(
    desc.head(10)
)


# ======================================================
# KEEP COORDINATES
# ======================================================

desc_xy = desc[
    [
        "ID",
        "X",
        "Y"
    ]
].copy()

desc_xy = desc_xy.dropna(
    subset=["X", "Y"]
)


# ======================================================
# CREATE POINTS
# ======================================================

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

print("\nSpatial join...")

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

print(
    "Rows inside pilot:",
    len(pilot_points)
)


# ======================================================
# DIAGNOSTICS
# ======================================================

print("\n====================")
print("PILOT DIAGNOSTICS")
print("====================")

print(
    "Records:",
    len(pilot_points)
)

print(
    "Unique abstraction IDs:",
    pilot_points["ID"].nunique()
)

print(
    "Unique coordinates:",
    pilot_points[
        ["X", "Y"]
    ]
    .drop_duplicates()
    .shape[0]
)

print("\nRecords per abstraction ID:")

print(
    pilot_points
    .groupby("ID")
    .size()
    .describe()
)


# ======================================================
# INSPECT ONE ID
# ======================================================

sample_id = (
    pilot_points["ID"]
    .drop_duplicates()
    .sample(1, random_state=42)
    .iloc[0]
)

print("\n====================")
print("SAMPLE ABSTRACTION ID")
print("====================")

print(
    "ID:",
    sample_id
)

sample_records = desc[
    desc["ID"] == sample_id
]

print(
    "\nNumber of rows:",
    len(sample_records)
)

cols_to_show = [
    "ROK",
    "ID",
    "X",
    "Y",
    "OBEC",
    "NAZICO",
    "PML_S",
    "PMM3_ROK",
    "PMM3_MES"
]

print(
    sample_records[
        cols_to_show
    ]
    .sort_values("ROK")
)

# ======================================================
# DONE
# ======================================================

print("\nDone.")
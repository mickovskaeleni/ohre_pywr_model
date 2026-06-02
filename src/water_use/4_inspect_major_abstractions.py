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

TIME_SERIES_PATH = (
    PROCESSED_DIR /
    "water_use_data_time_series_w_2009.rds"
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

print("Finding abstraction IDs in pilot...")

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
    "Unique abstraction IDs:",
    len(pilot_ids)
)


# ======================================================
# LOAD TIME SERIES
# ======================================================

print("Loading time-series data...")

ts = pyreadr.read_r(
    TIME_SERIES_PATH
)[None]

ts["MVM"] = pd.to_numeric(
    ts["MVM"],
    errors="coerce"
)

ts["YEAR"] = pd.to_datetime(
    ts["DTM"]
).dt.year

ts = ts[
    ts["ID"].isin(
        pilot_ids
    )
]


# ======================================================
# TOP 20 IDS
# ======================================================

abstractions = (
    ts.groupby("ID")
    .agg(
        TOTAL_MVM=("MVM", "sum"),
        N_YEARS=("YEAR", "nunique")
    )
    .reset_index()
)

abstractions = abstractions.sort_values(
    "TOTAL_MVM",
    ascending=False
)

top20 = abstractions.head(20)


# ======================================================
# LATEST DESCRIPTIVE RECORD
# ======================================================

latest_desc = (
    desc.sort_values("ROK")
    .groupby("ID")
    .tail(1)
)

latest_desc = latest_desc[
    latest_desc["ID"].isin(
        top20["ID"]
    )
]


# ======================================================
# MERGE
# ======================================================

result = top20.merge(
    latest_desc,
    on="ID",
    how="left"
)


# ======================================================
# SELECT COLUMNS
# ======================================================

cols = [
    "ID",
    "ROK",
    "NAZICO",
    "OBEC",
    "X",
    "Y",
    "TOTAL_MVM",
    "N_YEARS"
]

available_cols = [
    c for c in cols
    if c in result.columns
]

result = result[
    available_cols
]


# ======================================================
# OUTPUT
# ======================================================

pd.set_option(
    "display.max_columns",
    None
)

pd.set_option(
    "display.max_colwidth",
    120
)

print("\n====================")
print("TOP 20 MAJOR ABSTRACTIONS")
print("====================")

print(result)

print("\nDone.")
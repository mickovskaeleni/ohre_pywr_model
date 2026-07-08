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

TS_PATH = (
    PROCESSED_DIR /
    "water_use_data_time_series_w_2009.rds"
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
# PUBLIC SUPPLY IDS
# ======================================================

pilot_desc = desc[
    desc["ID"].isin(
        pilot_ids
    )
].copy()

livestock_supply_ids = (
    pilot_desc[
        pilot_desc["OD_ZIV_V"].fillna(0) > 0
    ]["ID"]
    .drop_duplicates()
)

print(
    "Livestock supply IDs:",
    len(livestock_supply_ids)
)

# ======================================================
# LOAD TIME SERIES
# ======================================================

print("Loading time series...")

ts = pyreadr.read_r(
    TS_PATH
)[None]

ts["DTM"] = pd.to_datetime(
    ts["DTM"]
)

# ======================================================
# KEEP PUBLIC SUPPLY IDS
# ======================================================

livestock_ts = ts[
    ts["ID"].isin(
        livestock_supply_ids
    )
].copy()

print(
    "Time series rows:",
    len(livestock_ts)
)

# ======================================================
# CLEAN MVM
# ======================================================

livestock_ts["MVM"] = pd.to_numeric(
    livestock_ts["MVM"],
    errors="coerce"
)

livestock_ts = livestock_ts[
    livestock_ts["MVM"].notna()
]

# ======================================================
# MONTHLY TIMESERIES
# ======================================================

monthly = (
    livestock_ts
    .groupby("DTM")
    .agg(
        TOTAL_MVM=("MVM", "sum"),
        N_IDS=("ID", "nunique")
    )
    .reset_index()
    .sort_values("DTM")
)

# ======================================================
# YEARLY TIMESERIES
# ======================================================

livestock_ts["YEAR"] = (
    livestock_ts["DTM"]
    .dt.year
)

yearly = (
    livestock_ts
    .groupby("YEAR")
    .agg(
        TOTAL_MVM=("MVM", "sum"),
        N_IDS=("ID", "nunique")
    )
    .reset_index()
)

# ======================================================
# SAVE
# ======================================================

monthly_path = (
    OUTPUT_DIR /
    "livestock_monthly_mvm.csv"
)

yearly_path = (
    OUTPUT_DIR /
    "livestock_yearly_mvm.csv"
)

monthly.to_csv(
    monthly_path,
    index=False
)

yearly.to_csv(
    yearly_path,
    index=False
)

# ======================================================
# PRINT
# ======================================================

print("\n====================")
print("MONTHLY TIMESERIES")
print("====================")

print(
    monthly.head()
)

print("\n====================")
print("YEARLY TIMESERIES")
print("====================")

print(
    yearly
)

print(
    "\nSaved:"
)

print(monthly_path)
print(yearly_path)

print("\nDone.")
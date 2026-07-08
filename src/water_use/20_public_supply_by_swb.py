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

TIME_SERIES_PATH = (
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

print(
    "Pilot SWBs:",
    len(pilot)
)

# ======================================================
# LOAD SWBS
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
    [
        "ID",
        "X",
        "Y"
    ]
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

print("Spatial join...")

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

# ======================================================
# ID -> SWB MAPPING
# ======================================================

id_swb = (
    pilot_points[
        [
            "ID",
            "UPOV_ID"
        ]
    ]
    .drop_duplicates()
)

print(
    "Mapped IDs:",
    len(id_swb)
)

# ======================================================
# PUBLIC SUPPLY IDS
# ======================================================

pilot_desc = desc[
    desc["ID"].isin(
        id_swb["ID"]
    )
].copy()

public_supply_ids = (
    pilot_desc[
        pilot_desc["OD_VER_V"]
        .fillna(0) > 0
    ]["ID"]
    .drop_duplicates()
)

print(
    "Public supply IDs:",
    len(public_supply_ids)
)

# ======================================================
# LOAD TIME SERIES
# ======================================================

print("Loading time series...")

ts = pyreadr.read_r(
    TIME_SERIES_PATH
)[None]

ts["MVM"] = pd.to_numeric(
    ts["MVM"],
    errors="coerce"
)

ts = ts[
    ts["ID"].isin(
        public_supply_ids
    )
]

print(
    "Rows:",
    len(ts)
)

# ======================================================
# MERGE SWB
# ======================================================

ts = ts.merge(
    id_swb,
    on="ID",
    how="left"
)

# ======================================================
# AGGREGATE BY SWB
# ======================================================

swb_demand = (
    ts.groupby("UPOV_ID")
    .agg(
        TOTAL_MVM=("MVM", "sum"),
        N_IDS=("ID", "nunique")
    )
    .reset_index()
)

swb_demand = swb_demand.sort_values(
    "TOTAL_MVM",
    ascending=False
)

# ======================================================
# SHARES
# ======================================================

total_demand = (
    swb_demand["TOTAL_MVM"]
    .sum()
)

swb_demand["SHARE_%"] = (
    100
    * swb_demand["TOTAL_MVM"]
    / total_demand
)

# ======================================================
# RESULTS
# ======================================================

print("\n====================")
print("PUBLIC SUPPLY BY SWB")
print("====================")

print(
    swb_demand.head(20)
)

print("\nTotal demand:")

print(
    round(total_demand, 2)
)

# ======================================================
# SAVE
# ======================================================

output_path = (
    OUTPUT_DIR /
    "public_supply_by_swb.csv"
)

swb_demand.to_csv(
    output_path,
    index=False
)

print("\nSaved:")

print(output_path)

print("\nDone.")
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

SWB_DEMAND_PATH = (
    OUTPUT_DIR /
    "public_supply_by_swb.csv"
)

# ======================================================
# SETTINGS
# ======================================================

TOP_N_SWBS = 5

# ======================================================
# LOAD SWB DEMAND
# ======================================================

print("Loading SWB demand...")

swb_demand = pd.read_csv(
    SWB_DEMAND_PATH
)

top_swbs = (
    swb_demand
    .head(TOP_N_SWBS)
    ["UPOV_ID"]
    .tolist()
)

print("\nTop SWBs:")

for swb in top_swbs:
    print(swb)

# ======================================================
# LOAD PILOT
# ======================================================

pilot = pd.read_csv(
    PILOT_PATH
)

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

print("\nLoading descriptive data...")

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

id_swb = (
    pilot_points[
        [
            "ID",
            "UPOV_ID"
        ]
    ]
    .drop_duplicates()
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

# ======================================================
# LOAD TIMESERIES
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

# ======================================================
# MERGE SWB
# ======================================================

ts = ts.merge(
    id_swb,
    on="ID",
    how="left"
)

# ======================================================
# ABSTRACTION TOTALS
# ======================================================

abstraction_totals = (
    ts.groupby("ID")
    .agg(
        TOTAL_MVM=("MVM", "sum")
    )
    .reset_index()
)

# ======================================================
# LATEST DESCRIPTIVE RECORD
# ======================================================

latest_desc = (
    pilot_desc
    .sort_values("ROK")
    .groupby("ID")
    .tail(1)
)

# ======================================================
# MERGE
# ======================================================

result = (
    abstraction_totals
    .merge(
        latest_desc[
            [
                "ID",
                "NAZICO",
                "OBEC",
                "OD_VER_V"
            ]
        ],
        on="ID",
        how="left"
    )
    .merge(
        id_swb,
        on="ID",
        how="left"
    )
)

# ======================================================
# INSPECT TOP SWBS
# ======================================================

for swb_id in top_swbs:

    print("\n")
    print("=" * 60)
    print(f"SWB: {swb_id}")
    print("=" * 60)

    subset = (
        result[
            result["UPOV_ID"] == swb_id
        ]
        .sort_values(
            "TOTAL_MVM",
            ascending=False
        )
    )

    print(
        subset[
            [
                "ID",
                "NAZICO",
                "OBEC",
                "TOTAL_MVM",
                "OD_VER_V"
            ]
        ]
    )

    print("\nSummary:")

    print(
        f"Abstractions: {subset['ID'].nunique()}"
    )

    print(
        f"Total MVM: {subset['TOTAL_MVM'].sum():,.0f}"
    )

# ======================================================
# SAVE
# ======================================================

result.to_csv(
    OUTPUT_DIR /
    "public_supply_abstractions_with_swb.csv",
    index=False
)

print("\nSaved:")
print(
    OUTPUT_DIR /
    "public_supply_abstractions_with_swb.csv"
)

print("\nDone.")
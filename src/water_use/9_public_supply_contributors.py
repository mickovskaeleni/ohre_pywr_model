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

pilot = pd.read_csv(PILOT_PATH)

# ======================================================
# LOAD SWBs
# ======================================================

swb = gpd.read_file(SWB_PATH)

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

public_supply_ids = (
    pilot_desc[
        pilot_desc["OD_VER_V"].fillna(0) > 0
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
    TS_PATH
)[None]

ts["MVM"] = pd.to_numeric(
    ts["MVM"],
    errors="coerce"
)

# ======================================================
# KEEP ONLY PUBLIC SUPPLY IDS
# ======================================================

public_ts = ts[
    ts["ID"].isin(
        public_supply_ids
    )
].copy()

public_ts = public_ts[
    public_ts["MVM"].notna()
]

# ======================================================
# TOTAL MVM BY ID
# ======================================================

contributors = (
    public_ts
    .groupby("ID")
    .agg(
        TOTAL_MVM=("MVM", "sum")
    )
    .reset_index()
)

# ======================================================
# METADATA
# ======================================================

latest = (
    pilot_desc
    .sort_values("ROK")
    .groupby("ID")
    .tail(1)
)

contributors = contributors.merge(
    latest[
        [
            "ID",
            "NAZICO",
            "OBEC"
        ]
    ],
    on="ID",
    how="left"
)

# ======================================================
# SHARES
# ======================================================

contributors = contributors.sort_values(
    "TOTAL_MVM",
    ascending=False
)

total_volume = (
    contributors["TOTAL_MVM"]
    .sum()
)

contributors["SHARE_%"] = (
    100
    * contributors["TOTAL_MVM"]
    / total_volume
)

contributors["CUM_SHARE_%"] = (
    contributors["SHARE_%"]
    .cumsum()
)

contributors["RANK"] = (
    range(
        1,
        len(contributors) + 1
    )
)

# ======================================================
# SAVE FULL TABLE
# ======================================================

full_path = (
    OUTPUT_DIR /
    "public_supply_contributors.csv"
)

contributors.to_csv(
    full_path,
    index=False
)

# ======================================================
# SAVE TOP 20
# ======================================================

top20_path = (
    OUTPUT_DIR /
    "public_supply_top20_contributors.csv"
)

contributors.head(20).to_csv(
    top20_path,
    index=False
)

# ======================================================
# PRINT
# ======================================================

print("\n====================")
print("TOP 20 CONTRIBUTORS")
print("====================")

print(
    contributors[
        [
            "RANK",
            "ID",
            "NAZICO",
            "OBEC",
            "TOTAL_MVM",
            "SHARE_%",
            "CUM_SHARE_%"
        ]
    ].head(20)
)

print("\n====================")
print("CONCENTRATION")
print("====================")

for n in [1, 3, 5, 10, 20, 50]:

    if n <= len(contributors):

        share = (
            contributors
            .head(n)["SHARE_%"]
            .sum()
        )

        print(
            f"Top {n}: {share:.2f}%"
        )

print("\nSaved:")

print(full_path)
print(top20_path)

print("\nDone.")
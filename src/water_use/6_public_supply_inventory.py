import pandas as pd
import geopandas as gpd
import pyreadr

from pathlib import Path
from shapely.geometry import Point


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

PILOT_PATH = PROCESSED_DIR / "southwest_pilot_swbs.csv"
SWB_PATH = RAW_DIR / "SWB_ohre" / "ohre.shp"

DESC_PATH = (
    PROCESSED_DIR /
    "water_use_data_descriptive_treated_w_2009.rds"
)

print("Loading pilot...")

pilot = pd.read_csv(PILOT_PATH)

print("Loading SWBs...")

swb = gpd.read_file(SWB_PATH)

pilot_swb = swb[
    swb["UPOV_ID"].isin(
        pilot["UPOV_ID"]
    )
].copy()

print("Loading descriptive data...")

desc = pyreadr.read_r(
    DESC_PATH
)[None]

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

print("Spatial join...")

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

pilot_desc = desc[
    desc["ID"].isin(
        pilot_ids
    )
].copy()

# Keep only records that report public supply

public_supply = pilot_desc[
    pilot_desc["OD_VER_V"].fillna(0) > 0
].copy()

print(
    "Public supply records:",
    len(public_supply)
)

inventory = (
    public_supply
    .groupby("ID")
    .agg(
        TOTAL_OD_VER_V=("OD_VER_V", "max"),
        N_YEARS=("ROK", "nunique"),
        FIRST_YEAR=("ROK", "min"),
        LAST_YEAR=("ROK", "max")
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
            "X",
            "Y"
        ]
    ],
    on="ID",
    how="left"
)

inventory = inventory.sort_values(
    "TOTAL_OD_VER_V",
    ascending=False
)

inventory.to_csv(
    OUTPUT_DIR /
    "public_supply_inventory.csv",
    index=False
)

print("\nTop 20 public supply abstractions:\n")

print(
    inventory.head(20)
)

print(
    "\nUnique public supply IDs:",
    len(inventory)
)
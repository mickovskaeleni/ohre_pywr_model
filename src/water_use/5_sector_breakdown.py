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
    "Unique abstraction IDs:",
    len(pilot_ids)
)


# ======================================================
# KEEP PILOT RECORDS
# ======================================================

pilot_desc = desc[
    desc["ID"].isin(
        pilot_ids
    )
].copy()


# ======================================================
# LATEST RECORD PER ID
# ======================================================

latest = (
    pilot_desc
    .sort_values("ROK")
    .groupby("ID")
    .tail(1)
)

print(
    "Latest records:",
    len(latest)
)


# ======================================================
# SECTOR VARIABLES
# ======================================================

sector_map = {
    "OD_VER_V": "Public Water Supply",
    "OD_PR_T": "Industrial Technology",
    "OD_OST": "Other Industry",
    "OD_P_CHL": "Once-through Cooling",
    "OD_C_CHL": "Circulating Cooling",
    "OD_ZAVL": "Irrigation",
    "OD_ZIV_V": "Livestock",
    "OD_PLZ_PMV": "Mineral Waters"
}


# ======================================================
# BUILD SUMMARY
# ======================================================

results = []

for col, sector in sector_map.items():

    if col not in latest.columns:
        continue

    values = pd.to_numeric(
        latest[col],
        errors="coerce"
    )

    total_volume = values.fillna(0).sum()

    n_ids = (
        values.fillna(0) > 0
    ).sum()

    results.append(
        {
            "Sector": sector,
            "Variable": col,
            "Total_Reported_Volume": round(
                total_volume,
                3
            ),
            "Reporting_IDs": int(
                n_ids
            )
        }
    )


sector_summary = pd.DataFrame(
    results
)

sector_summary = sector_summary.sort_values(
    "Total_Reported_Volume",
    ascending=False
)


# ======================================================
# SHARE %
# ======================================================

total_all = (
    sector_summary[
        "Total_Reported_Volume"
    ]
    .sum()
)

sector_summary[
    "Share_%"
] = round(
    100
    * sector_summary[
        "Total_Reported_Volume"
    ]
    / total_all,
    2
)


# ======================================================
# SAVE
# ======================================================

output_path = (
    OUTPUT_DIR /
    "sector_breakdown.csv"
)

sector_summary.to_csv(
    output_path,
    index=False
)


# ======================================================
# OUTPUT
# ======================================================

pd.set_option(
    "display.max_columns",
    None
)

print("\n====================")
print("SECTOR BREAKDOWN")
print("====================")

print(
    sector_summary
)

print(
    "\nSaved to:",
    output_path
)

print("\nDone.")
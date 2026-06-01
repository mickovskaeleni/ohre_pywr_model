import pandas as pd
import geopandas as gpd
import pyreadr
import matplotlib.pyplot as plt

from pathlib import Path
from collections import defaultdict


# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "outputs"

SWB_PATH = (
    RAW_DIR /
    "SWB_ohre" /
    "ohre.shp"
)

TABA_PATH = (
    RAW_DIR /
    "SWB_ohre" /
    "TABA.rds"
)


# ======================================================
# LOAD SWBs
# ======================================================

print("Loading SWBs...")

swb = gpd.read_file(SWB_PATH)

print("SWBs:", len(swb))


# ======================================================
# LOAD TABA
# ======================================================

print("Loading TABA...")

taba = pyreadr.read_r(TABA_PATH)[None]

taba = taba.rename(
    columns={
        "from": "FROM",
        "to": "TO"
    }
)

print("Edges:", len(taba))


# ======================================================
# BUILD GRAPH
# ======================================================

upstream_dict = defaultdict(list)

for _, row in taba.iterrows():

    upstream_dict[
        row["TO"]
    ].append(
        row["FROM"]
    )


def get_all_upstream(
    node,
    visited=None
):

    if visited is None:
        visited = set()

    if node in visited:
        return visited

    visited.add(node)

    for up in upstream_dict.get(node, []):

        get_all_upstream(
            up,
            visited
        )

    return visited


# ======================================================
# RESERVOIR SWBs
# ======================================================

BREZOVA_SWB = "OHL_0460"
STANOVICE_SWB = "OHL_0045_J"


# ======================================================
# UPSTREAM SYSTEMS
# ======================================================

brezova_upstream = get_all_upstream(
    BREZOVA_SWB
)

stanovice_upstream = get_all_upstream(
    STANOVICE_SWB
)


print("\n=== PILOT REGIONS ===")

print(
    "Stanovice:",
    len(stanovice_upstream),
    "SWBs"
)

print(
    "Brezova:",
    len(brezova_upstream),
    "SWBs"
)


# ======================================================
# CREATE SUBSETS
# ======================================================

brezova_basin = swb[
    swb["UPOV_ID"].isin(
        brezova_upstream
    )
]

stanovice_basin = swb[
    swb["UPOV_ID"].isin(
        stanovice_upstream
    )
]


# ======================================================
# RESERVOIR LOCATIONS
# ======================================================

reservoirs = pd.DataFrame({
    "name": [
        "Brezova",
        "Stanovice"
    ],
    "lon": [
        12.853,
        12.887
    ],
    "lat": [
        50.199,
        50.169
    ]
})

reservoir_gdf = gpd.GeoDataFrame(
    reservoirs,
    geometry=gpd.points_from_xy(
        reservoirs.lon,
        reservoirs.lat
    ),
    crs="EPSG:4326"
)

reservoir_gdf = reservoir_gdf.to_crs(
    swb.crs
)


# ======================================================
# PLOT
# ======================================================

fig, ax = plt.subplots(
    figsize=(14, 10)
)

swb.plot(
    ax=ax,
    color="#eeeeee",
    edgecolor="grey",
    linewidth=0.3
)

# Brezova
brezova_basin.plot(
    ax=ax,
    color="#4F81BD",
    alpha=0.5,
    edgecolor="black",
    linewidth=1
)

# Stanovice
stanovice_basin.plot(
    ax=ax,
    color="#08306B",
    alpha=0.8,
    edgecolor="black",
    linewidth=1
)

reservoir_gdf.plot(
    ax=ax,
    color="red",
    markersize=100,
    zorder=20
)

for _, row in reservoir_gdf.iterrows():

    ax.text(
        row.geometry.x,
        row.geometry.y,
        row["name"],
        fontsize=11,
        fontweight="bold",
        color="black"
    )

ax.set_title(
    "Candidate Pilot Regions\nStanovice vs Brezova",
    fontsize=16
)

ax.axis("off")

plt.savefig(
    OUTPUT_DIR /
    "reservoir_pilot_regions.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(
    "\nSaved:",
    OUTPUT_DIR /
    "reservoir_pilot_regions.png"
)
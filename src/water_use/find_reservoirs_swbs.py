import pandas as pd
import geopandas as gpd
from pathlib import Path


# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"

SWB_PATH = (
    RAW_DIR /
    "SWB_ohre" /
    "ohre.shp"
)


# ======================================================
# LOAD SWBs
# ======================================================

print("Loading SWBs...")

swb = gpd.read_file(SWB_PATH)

print("SWBs:", len(swb))


# ======================================================
# RESERVOIR COORDINATES
# ======================================================

# Replace with your exact coordinates
reservoirs = pd.DataFrame({
    "name": [
        "Brezova Reservoir",
        "Stanovice Reservoir"
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


# ======================================================
# CREATE POINTS
# ======================================================

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
# FIND SWBs
# ======================================================

print("Finding containing SWBs...")

reservoir_swb = gpd.sjoin(
    reservoir_gdf,
    swb[
        [
            "UPOV_ID",
            "geometry"
        ]
    ],
    how="left",
    predicate="within"
)


# ======================================================
# RESULTS
# ======================================================

print("\n=== RESERVOIR -> SWB ===")

print(
    reservoir_swb[
        [
            "name",
            "UPOV_ID"
        ]
    ]
)


# ======================================================
# OPTIONAL MAP
# ======================================================

ax = swb.plot(
    figsize=(12, 10),
    color="lightgrey",
    edgecolor="grey",
    linewidth=0.3
)

reservoir_gdf.plot(
    ax=ax,
    color="red",
    markersize=80
)

for _, row in reservoir_gdf.iterrows():

    ax.text(
        row.geometry.x,
        row.geometry.y,
        row["name"],
        fontsize=10,
        fontweight="bold"
    )

ax.set_title(
    "Reservoir Locations"
)

ax.axis("off")

print("\nDone.")

import pyreadr

TABA_PATH = (
    RAW_DIR /
    "SWB_ohre" /
    "TABA.rds"
)

taba = pyreadr.read_r(
    TABA_PATH
)[None]

taba = taba.rename(
    columns={
        "from": "FROM",
        "to": "TO"
    }
)

for target in ["OHL_0460", "OHL_0045_J"]:

    print("\n====================")
    print(target)
    print("====================")

    print("\nDirect upstream:")

    print(
        taba[
            taba["TO"] == target
        ][["FROM", "TO"]]
    )

    print("\nDirect downstream:")

    print(
        taba[
            taba["FROM"] == target
        ][["FROM", "TO"]]
    )

# ======================================================
# BUILD UPSTREAM GRAPH
# ======================================================

from collections import defaultdict

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
# UPSTREAM SYSTEM SIZE
# ======================================================

brezova_upstream = get_all_upstream(
    "OHL_0460"
)

stanovice_upstream = get_all_upstream(
    "OHL_0045_J"
)

print("\n====================")
print("UPSTREAM SYSTEM SIZE")
print("====================")

print(
    "Brezova:",
    len(brezova_upstream),
    "SWBs"
)

print(
    "Stanovice:",
    len(stanovice_upstream),
    "SWBs"
)

print(
    "Additional SWBs between them:",
    len(brezova_upstream)
    - len(stanovice_upstream)
)


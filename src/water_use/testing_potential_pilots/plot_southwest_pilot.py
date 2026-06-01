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

OUTPUT_FILE = (
    OUTPUT_DIR /
    "southwest_pilot_region.png"
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

taba = pyreadr.read_r(
    TABA_PATH
)[None]

taba = taba.rename(
    columns={
        "from": "FROM",
        "to": "TO"
    }
)

print("Edges:", len(taba))


# ======================================================
# BUILD UPSTREAM GRAPH
# ======================================================

upstream_dict = defaultdict(list)

for _, row in taba.iterrows():

    upstream_dict[
        row["TO"]
    ].append(
        row["FROM"]
    )


# ======================================================
# RECURSIVE FUNCTION
# ======================================================

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
# SOUTHWEST PILOT
# ======================================================

PILOT_OUTLET = "OHL_0500"

pilot_swbs = get_all_upstream(
    PILOT_OUTLET
)

print(
    "\nSouthwest Pilot SWBs:",
    len(pilot_swbs)
)


pilot = swb[
    swb["UPOV_ID"].isin(
        pilot_swbs
    )
]


# ======================================================
# RESERVOIRS
# ======================================================

reservoirs = gpd.GeoDataFrame(
    {
        "name": [
            "Brezova",
            "Stanovice"
        ]
    },
    geometry=gpd.points_from_xy(
        [12.85323631864757,
         12.887670087910328],
        [50.19986853366447,
         50.16960648270714]
    ),
    crs="EPSG:4326"
)

reservoirs = reservoirs.to_crs(
    swb.crs
)


# ======================================================
# CITIES
# ======================================================

cities = gpd.GeoDataFrame(
    {
        "city": [
            "Cheb",
            "Karlovy Vary"
        ]
    },
    geometry=gpd.points_from_xy(
        [
            12.370776234196052,
            12.870845561916695
        ],
        [
            50.07962080678717,
            50.23167681741822
        ]
    ),
    crs="EPSG:4326"
)

cities = cities.to_crs(
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
    color="#e6e6e6",
    edgecolor="grey",
    linewidth=0.3
)

pilot.plot(
    ax=ax,
    color="#2171B5",
    edgecolor="black",
    linewidth=0.8,
    alpha=0.7
)

reservoirs.plot(
    ax=ax,
    color="red",
    markersize=80,
    zorder=20
)

cities.plot(
    ax=ax,
    color="black",
    markersize=40,
    zorder=20
)


# reservoir labels
for _, row in reservoirs.iterrows():

    ax.text(
        row.geometry.x,
        row.geometry.y,
        row["name"],
        fontsize=10,
        fontweight="bold"
    )


# city labels
for _, row in cities.iterrows():

    ax.text(
        row.geometry.x,
        row.geometry.y,
        row["city"],
        fontsize=10,
        fontweight="bold"
    )


ax.set_title(
    f"Southwest Pilot Region\nOutlet = {PILOT_OUTLET}",
    fontsize=16
)

ax.axis("off")


plt.savefig(
    OUTPUT_FILE,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(
    "\nSaved:",
    OUTPUT_FILE
)
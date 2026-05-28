import pandas as pd
import geopandas as gpd
import pyreadr
import matplotlib.pyplot as plt
from shapely.geometry import Point
from pathlib import Path
from collections import defaultdict


# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

SWB_PATH = (
    RAW_DIR / "SWB_ohre" / "ohre.shp"
)

TABA_PATH = (
    RAW_DIR / "SWB_ohre" / "TABA.rds"
)

TIME_SERIES_PATH = (
    PROCESSED_DIR / "water_use_data_time_series_w_2009.rds"
)

DESC_PATH = (
    PROCESSED_DIR / "water_use_data_descriptive_treated_w_2009.rds"
)


# ======================================================
# LOAD SWBs
# ======================================================

print("Loading SWB polygons...")

swb = gpd.read_file(SWB_PATH)

print("SWB polygons:", len(swb))


# ======================================================
# LOAD TABA
# ======================================================

print("Loading TABA connectivity...")

taba = pyreadr.read_r(TABA_PATH)[None]

taba = taba.rename(
    columns={
        "from": "FROM",
        "to": "TO"
    }
)

print("Edges:", len(taba))


# ======================================================
# LOAD TIME SERIES
# ======================================================

print("Loading time-series data...")

ts = pyreadr.read_r(TIME_SERIES_PATH)[None]

print("Time-series rows:", len(ts))


# ======================================================
# LOAD DESCRIPTIVE DATA
# ======================================================

print("Loading descriptive data...")

desc = pyreadr.read_r(DESC_PATH)[None]

print("Descriptive rows:", len(desc))


# ======================================================
# SELECT RELEVANT COLUMNS
# ======================================================

desc = desc[
    [
        "ID",
        "X",
        "Y"
    ]
].copy()


ts = ts[
    [
        "ID",
        "DTM",
        "MVM"
    ]
].copy()


# ======================================================
# CLEANING
# ======================================================

print("Cleaning data...")

desc = desc.dropna(
    subset=["X", "Y"]
)

ts["MVM"] = pd.to_numeric(
    ts["MVM"],
    errors="coerce"
)


# ======================================================
# CREATE POINTS
# ======================================================

print("Creating abstraction points...")

geometry = [
    Point(xy)
    for xy in zip(desc["X"], desc["Y"])
]

points = gpd.GeoDataFrame(
    desc,
    geometry=geometry,
    crs="EPSG:5514"
)

points = points.to_crs(
    swb.crs
)

print("Points:", len(points))


# ======================================================
# SPATIAL JOIN
# ======================================================

print("Spatially linking abstractions to SWBs...")

joined = gpd.sjoin(
    points,
    swb[["UPOV_ID", "geometry"]],
    how="inner",
    predicate="within"
)

print(
    "Points inside Ohre basin:",
    len(joined)
)


# ======================================================
# MERGE WITH MVM
# ======================================================

joined = joined.merge(
    ts,
    on="ID",
    how="left"
)


# ======================================================
# AGGREGATE ABSTRACTIONS
# ======================================================

print("Aggregating abstraction intensity...")

# extract year
ts["YEAR"] = pd.to_datetime(
    ts["DTM"]
).dt.year


# yearly abstraction per ID
yearly_mvm = (
    ts.groupby(["ID", "YEAR"])["MVM"]
    .sum()
    .reset_index()
)


# average annual abstraction per ID
avg_yearly_mvm = (
    yearly_mvm.groupby("ID")["MVM"]
    .mean()
    .reset_index()
)

avg_yearly_mvm = avg_yearly_mvm.rename(
    columns={
        "MVM": "AVG_YEARLY_MVM"
    }
)


# merge back
joined = joined.merge(
    avg_yearly_mvm,
    on="ID",
    how="left"
)


# aggregate to SWBs
swb_mvm = (
    joined.groupby("UPOV_ID")["AVG_YEARLY_MVM"]
    .sum()
    .reset_index()
)

swb_mvm = swb_mvm.rename(
    columns={
        "AVG_YEARLY_MVM": "MVM"
    }
)

swb = swb.merge(
    swb_mvm,
    on="UPOV_ID",
    how="left"
)

swb["MVM"] = swb["MVM"].fillna(0)


# ======================================================
# BUILD GRAPH
# ======================================================

print("Building routing graph...")

upstream_dict = defaultdict(list)

for _, row in taba.iterrows():

    upstream_dict[
        row["TO"]
    ].append(
        row["FROM"]
    )


# ======================================================
# RECURSIVE UPSTREAM TRACING
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
# CALCULATE CANDIDATE METRICS
# ======================================================

print("Calculating candidate metrics...")

candidate_rows = []

for swb_id in swb["UPOV_ID"]:

    upstream_nodes = get_all_upstream(swb_id)

    n_upstream = len(upstream_nodes)

    subsystem = swb[
        swb["UPOV_ID"].isin(upstream_nodes)
    ]

    total_mvm = subsystem["MVM"].sum()

    candidate_rows.append(
        {
            "UPOV_ID": swb_id,
            "n_upstream": n_upstream,
            "total_mvm": total_mvm
        }
    )

candidate_df = pd.DataFrame(candidate_rows)


# ======================================================
# SIMPLE PILOT SCORE
# ======================================================

candidate_df["pilot_score"] = (
    (
        candidate_df["total_mvm"] /
        candidate_df["total_mvm"].max()
    ) * 0.6
    +
    (
        candidate_df["n_upstream"] /
        candidate_df["n_upstream"].max()
    ) * 0.4
)


# avoid giant central systems
candidate_df = candidate_df[
    candidate_df["n_upstream"] < 40
]

candidate_df = candidate_df.sort_values(
    "pilot_score",
    ascending=False
)


# ======================================================
# SELECT TOP 6
# ======================================================

top_candidates = candidate_df.head(6)

print("\n=== TOP 6 PILOT CANDIDATES ===")
print(top_candidates)


# ======================================================
# CREATE LABELS
# ======================================================

top_candidates = top_candidates.reset_index(drop=True)

top_candidates["candidate_name"] = [
    "Candidate A",
    "Candidate B",
    "Candidate C",
    "Candidate D",
    "Candidate E",
    "Candidate F"
]


# ======================================================
# PLOT
# ======================================================

print("Generating candidate map...")

fig, ax = plt.subplots(
    figsize=(16, 12)
)


# base SWBs
swb.plot(
    ax=ax,
    color="#d9d9d9",
    edgecolor="grey",
    linewidth=0.3
)


# ======================================================
# PLOT CANDIDATE SUBSYSTEMS
# ======================================================

candidate_colors = [
    "#08306B",  # very dark blue
    "#08519C",
    "#2171B5",
    "#4292C6",
    "#6BAED6",
    "#C6DBEF"   # very light blue
]

for idx, row in top_candidates.iterrows():

    outlet = row["UPOV_ID"]

    upstream_nodes = get_all_upstream(outlet)

    subsystem = swb[
        swb["UPOV_ID"].isin(upstream_nodes)
    ]

    subsystem.plot(
        ax=ax,
        color=candidate_colors[idx],
        edgecolor="black",
        linewidth=0.7,
        alpha=0.6
    )

    # outlet polygon
    outlet_geom = swb[
        swb["UPOV_ID"] == outlet
    ].geometry.iloc[0]

    # representative point
    label_point = outlet_geom.representative_point()

    ax.text(
        label_point.x,
        label_point.y,
        row["candidate_name"],
        fontsize=13,
        fontweight="bold",
        color="black",
        bbox=dict(
            facecolor="white",
            edgecolor="none",
            alpha=0.8,
            pad=1
        ),
        zorder=20
    )


# ======================================================
# PLOT ABSTRACTIONS
# ======================================================

joined["MVM_plot"] = (
    joined["MVM"]
    .fillna(0)
    .clip(lower=0)
)

joined["MVM_plot"] = (
    joined["MVM_plot"] + 1
) ** 0.3


joined.plot(
    ax=ax,
    column="MVM_plot",
    cmap="YlOrRd",
    markersize=joined["MVM_plot"] * 1.2,
    alpha=0.7,
    edgecolor="none",
    legend=True,
    legend_kwds={
        "label": "Relative abstraction intensity"
    }
)

# ======================================================
# ADD REFERENCE CITIES
# ======================================================

cities = pd.DataFrame({
    "city": [
        "Cheb",
        "Karlovy Vary",
        "Chomutov",
        "Most",
        "Usti n. Labem"
    ],
    "lon": [
        12.3739,
        12.8717,
        13.4178,
        13.6362,
        14.0323
    ],
    "lat": [
        50.0796,
        50.2319,
        50.4605,
        50.5030,
        50.6607
    ]
})


city_gdf = gpd.GeoDataFrame(
    cities,
    geometry=gpd.points_from_xy(
        cities.lon,
        cities.lat
    ),
    crs="EPSG:4326"
)


# project to SWB CRS
city_gdf = city_gdf.to_crs(
    swb.crs
)


# plot cities
city_gdf.plot(
    ax=ax,
    color="black",
    markersize=40,
    zorder=10
)


# labels
for _, row in city_gdf.iterrows():

    ax.text(
        row.geometry.x,
        row.geometry.y,
        row["city"],
        fontsize=10,
        fontweight="bold",
        color="black"
    )

# ======================================================
# FINALIZE
# ======================================================

ax.set_title(
    "Candidate Pilot Regions\n"
    "(Hydrological Structure + Water Abstractions)",
    fontsize=20
)

ax.axis("off")

plot_path = (
    OUTPUT_DIR /
    "candidate_pilot_regions.png"
)

plt.savefig(
    plot_path,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved: {plot_path}")

plt.show()


# ======================================================
# DONE
# ======================================================

print("\nDONE.")
print(
    "Candidate pilot regions identified."
)
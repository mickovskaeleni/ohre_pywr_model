import pandas as pd
import pyreadr
import geopandas as gpd
import matplotlib.pyplot as plt


def plot_taba_connectivity():

    print("=== LOAD WATERES DOMAIN ===")

    wateres = pyreadr.read_r(
        "data/raw/WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
    )[None]

    # keep only inflow at outlet
    wateres = wateres[
        (wateres["var"] == "inflow") &
        (wateres["loc"] == "outlet")
    ]

    domain_ids = set(wateres["UPOV_ID"])

    print(f"SWB basins: {len(domain_ids)}")


    print("\n=== LOAD TABA CONNECTIVITY ===")

    taba = pyreadr.read_r(
        "data/raw/SWB_ohre/TABA.rds"
    )[None]


    print("Filtering connectivity using FROM only...")

    # correct filtering according to Petr
    edges = taba[
        taba["FROM"].isin(domain_ids)
    ][["FROM", "TO"]].drop_duplicates()

    print(f"Filtered edges: {len(edges)}")


    print("\n=== LOAD SWB SHAPEFILE ===")

    gdf = gpd.read_file(
        "data/raw/SWB_ohre/ohre.shp"
    )

    # keep only model domain
    gdf = gdf[gdf["UPOV_ID"].isin(domain_ids)]

    print(f"Loaded polygons: {len(gdf)}")


    print("\n=== BUILD CENTROIDS ===")

    gdf["centroid"] = gdf.geometry.centroid

    centroids = {
        row["UPOV_ID"]: row["centroid"]
        for _, row in gdf.iterrows()
    }


    print("\n=== PLOT NETWORK ===")

    fig, ax = plt.subplots(figsize=(18, 12))

    # basin polygons
    gdf.plot(
        ax=ax,
        color="lightblue",
        edgecolor="gray",
        linewidth=0.5
    )

    # directional arrows
    # connectivity lines with small directional arrows
    for _, row in edges.iterrows():

        from_id = row["FROM"]
        to_id = row["TO"]

        if from_id in centroids and to_id in centroids:

            p1 = centroids[from_id]
            p2 = centroids[to_id]

            x1, y1 = p1.x, p1.y
            x2, y2 = p2.x, p2.y

            # draw connection line
            ax.plot(
                [x1, x2],
                [y1, y2],
                color="blue",
                linewidth=0.8,
                alpha=0.7
            )

            # small arrow in the middle
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2

            dx = (x2 - x1) * 0.15
            dy = (y2 - y1) * 0.15

            ax.quiver(
                mx,
                my,
                dx,
                dy,
                angles="xy",
                scale_units="xy",
                scale=1,
                color="blue",
                width=0.002
            )

    # optional labels
    for basin_id, point in centroids.items():

        ax.text(
            point.x,
            point.y,
            basin_id,
            fontsize=4,
            color="black"
        )

    plt.title(
        "Directed River Connectivity of the Ohře Basin\n"
        "(Flow Direction from TABA Topology)",
        fontsize=18
    )

    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_taba_connectivity()
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from src.config import OUTPUT_DIR, SHAPEFILE_PATH


def plot_network():

    print("Loading SWB shapefile...")
    basins = gpd.read_file(SHAPEFILE_PATH)

    basins = basins[~basins["UPOV_ID"].str.endswith("_H0")].copy()

    print("Loading river edges...")
    edges = pd.read_csv("data/processed/river_edges.csv")

    # compute centroids for arrow plotting
    basins["centroid"] = basins.geometry.centroid

    centroid_dict = basins.set_index("UPOV_ID")["centroid"].to_dict()
    area_dict = basins.set_index("UPOV_ID")["AREA_NEW"].to_dict()

    print("Preparing figure...")

    fig, ax = plt.subplots(figsize=(12, 12))

    # plot basin polygons
    basins.plot(
        ax=ax,
        color="#d9f0ff",
        edgecolor="gray",
        linewidth=0.4
    )

    for _, row in edges.iterrows():

        up = row["upstream"]
        down = row["downstream"]

        if up not in basins["UPOV_ID"].values or down not in basins["UPOV_ID"].values:
            continue

        up_geom = basins.loc[basins["UPOV_ID"] == up].geometry.values[0]
        down_geom = basins.loc[basins["UPOV_ID"] == down].geometry.values[0]

        # centroids
        p1 = up_geom.centroid
        p2 = down_geom.centroid

        # intersection of basin borders
        border = up_geom.boundary.intersection(down_geom.boundary)

        if border.is_empty:
            target = p2
        else:
            target = border.centroid

        width = area_dict.get(up, 1) / basins["AREA_NEW"].max()
        width = 0.5 + 2 * width

        ax.annotate(
            "",
            xy=(target.x, target.y),
            xytext=(p1.x, p1.y),
            arrowprops=dict(
                arrowstyle="->",
                color="#0050a0",
                linewidth=width,
                alpha=0.7
            )
        )
    

    # plot SWB outlet points
    basins["centroid"].plot(
        ax=ax,
        color="black",
        markersize=2
    )

    ax.set_title(
        "Reconstructed River Network of the Ohře Basin\n"
        "(SWB Topology Used in Pywr Model)",
        fontsize=14
    )

    ax.axis("off")

    plt.tight_layout()

    output_file = OUTPUT_DIR / "ohre_river_network.png"

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    print(f"Figure saved to: {output_file}")

    plt.show()


if __name__ == "__main__":
    plot_network()
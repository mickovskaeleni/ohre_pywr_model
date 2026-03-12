import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from src.config import SHAPEFILE_PATH


def plot_network():

    print("Loading SWB shapefile...")
    basins = gpd.read_file(SHAPEFILE_PATH)

    basins = basins[~basins["UPOV_ID"].str.endswith("_H0")].copy()

    print("Loading river edges...")
    edges = pd.read_csv("data/processed/river_edges.csv")

    # compute centroids for arrows
    basins["centroid"] = basins.geometry.centroid

    print("Plotting network...")

    fig, ax = plt.subplots(figsize=(10, 10))

    basins.plot(
        ax=ax,
        color="lightblue",
        edgecolor="gray",
        linewidth=0.5
    )

    for _, row in edges.iterrows():

        up = row["upstream"]
        down = row["downstream"]

        if up not in centroid_dict or down not in centroid_dict:
            continue

        p1 = centroid_dict[up]
        p2 = centroid_dict[down]

        ax.annotate(
            "",
            xy=(p2.x, p2.y),
            xytext=(p1.x, p1.y),
            arrowprops=dict(
                arrowstyle="->",
                color="red",
                linewidth=0.7,
                alpha=0.6
            )
        )

    ax.set_title("Ohře Basin SWB River Network")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_network()
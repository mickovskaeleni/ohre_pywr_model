import geopandas as gpd
import pandas as pd
from src.config import SHAPEFILE_PATH

def build_connectivity():

    network = gpd.read_file(SHAPEFILE_PATH)

    # remove artificial basins
    network = network[~network["UPOV_ID"].str.endswith("_H0")].copy()

    edges = []

    for i, basin in network.iterrows():

        neighbors = network[network.geometry.touches(basin.geometry)]

        neighbors = network[network.geometry.touches(basin.geometry)]
        neighbors = neighbors[neighbors["UPOV_ID"] != basin["UPOV_ID"]]

        if len(neighbors) > 0:

            downstream = neighbors.loc[neighbors["AREA_NEW"].idxmax()]

            edges.append({
                "upstream": basin["UPOV_ID"],
                "downstream": downstream["UPOV_ID"]
            })

    edges_df = pd.DataFrame(edges).drop_duplicates()

    edges_df.to_csv("data/processed/river_edges.csv", index=False)

    print("Edges found:", len(edges_df))

    return edges_df


if __name__ == "__main__":
    build_connectivity()
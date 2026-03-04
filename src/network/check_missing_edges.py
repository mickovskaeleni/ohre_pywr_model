import geopandas as gpd
import pandas as pd

from src.config import SHAPEFILE_PATH

def check_missing_edges():

    print("Loading shapefile...")
    network = gpd.read_file(SHAPEFILE_PATH)

    # remove artificial basins
    network = network[~network["UPOV_ID"].str.endswith("_H0")].copy()

    print("Total basins:", len(network))

    print("Loading edges...")
    edges = pd.read_csv("data/processed/river_edges.csv")

    upstream_set = set(edges["upstream"])
    basin_set = set(network["UPOV_ID"])

    missing = basin_set - upstream_set

    print("Basins without downstream connection:", len(missing))
    print(list(missing)[:20])

    return missing


if __name__ == "__main__":
    check_missing_edges()
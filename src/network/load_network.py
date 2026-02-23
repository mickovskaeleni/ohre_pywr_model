import geopandas as gpd
import pandas as pd

def load_shapefile(path):
    gdf = gpd.read_file(path)
    return gdf

def load_ids(path):
    ids = pd.read_csv(path)
    return ids

if __name__ == "__main__":
    shp_path = "data/raw/SWB_ohre/ohre.shp"
    ids_path = "data/raw/SWB_ohre/IDs_list.csv"

    network = load_shapefile(shp_path)
    ids = load_ids(ids_path)

    print(network.head())
    print(ids.head())

    print(network.geometry.type.value_counts())
    print(network.crs)
    print(network.is_valid.all())
    print(network.columns)

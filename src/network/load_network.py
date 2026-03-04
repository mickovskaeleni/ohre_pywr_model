from src.config import SHAPEFILE_PATH, IDS_PATH, WATERES_FILE

import geopandas as gpd
import pandas as pd
import pyreadr

def load_shapefile(path):
    gdf = gpd.read_file(path)
    return gdf

def load_ids(path):
    ids = pd.read_csv(path)
    return ids

def load_wateres(path):
    result = pyreadr.read_r(path)
    df = list(result.values())[0]   # extract dataframe
    return df

if __name__ == "__main__":
    shp_path = SHAPEFILE_PATH
    ids_path = IDS_PATH
    wateres_path = WATERES_FILE

    network = load_shapefile(shp_path)
    ids = load_ids(ids_path)
    wateres = load_wateres(wateres_path)

    print(wateres['UPOV_ID'].unique()[:10])

    #print(network.head())
    #print(ids.head())

    #print(network.geometry.type.value_counts())
    #print(network.crs)
    #print(network.is_valid.all())
    #print(network.columns)

    #print(network[['UPOV_ID','AREA_NEW']].sort_values('AREA_NEW').head(10))
    #print(network[['UPOV_ID','AREA_NEW']].sort_values('AREA_NEW').tail(10))
    #network = network[~network['UPOV_ID'].str.endswith('_H0')].copy()
    #print(len(network))
    #print(network['AREA_NEW'].min(), network['AREA_NEW'].max())
    print(network.columns)
    print(network[["UPOV_ID","KTGUPOV_Z","KTG_UPOV","UPMU_Z","U_PMU"]].head(20))

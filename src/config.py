from pathlib import Path

# Project root (one level above src/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Specific datasets
WATERES_FILE = RAW_DATA_DIR / "WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
BILAN_FILE = RAW_DATA_DIR / "WRI_bilan_SWB_subset_T_P_RM_BF_ET_PET_daily_1981_2024.rds"

SHAPEFILE_PATH = RAW_DATA_DIR / "SWB_ohre" / "ohre.shp"
IDS_PATH = RAW_DATA_DIR / "SWB_ohre" / "IDs_list.csv"

OUTPUT_DIR = PROJECT_ROOT / "outputs"

# src/inflow/inspect_wateres.py

import pyreadr

file_path = "data/raw/WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
result = pyreadr.read_r(file_path)

df = result[None]

print(df.columns)
print(df.head())

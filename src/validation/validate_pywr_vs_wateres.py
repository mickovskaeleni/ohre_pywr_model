import pandas as pd
import pyreadr
import matplotlib.pyplot as plt
import numpy as np

from src.network.build_pywr_network import build_pywr_network
from pywr.recorders import NumpyArrayNodeRecorder

print("Loading WATERES data...")

result = pyreadr.read_r(
    "data/raw/WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
)

wateres = result[None]
wateres["DTM"] = pd.to_datetime(wateres["DTM"])

wateres = wateres[wateres["var"] == "inflow"]

# --------------------------------------------------
# Aggregate basin inflow from WATERES
# --------------------------------------------------

wateres_total = (
    wateres.groupby("DTM")["value"]
    .sum()
    .reset_index()
)

# --------------------------------------------------
# Run Pywr model
# --------------------------------------------------
model, basin_outlet = build_pywr_network()

# attach recorder
rec = NumpyArrayNodeRecorder(model, basin_outlet)

print("Running model...")
model.run()

# NOW data exists
pywr_flow = np.array(rec.data)

print("WATERES length:", len(wateres_total))
print("Pywr length:", len(pywr_flow))

from sklearn.metrics import r2_score, mean_squared_error

print("R²:", r2_score(wateres_total["value"], pywr_flow))
print("RMSE:", np.sqrt(mean_squared_error(wateres_total["value"], pywr_flow)))

# --------------------------------------------------
# Plot comparison
# --------------------------------------------------

plt.figure(figsize=(12,5))

plt.plot(
    wateres_total["DTM"],
    wateres_total["value"],
    label="WATERES total inflow",
    alpha=0.7
)

plt.plot(
    wateres_total["DTM"],
    pywr_flow,
    label="Pywr outlet flow",
    alpha=0.7
)

plt.legend()
plt.title("Validation: WATERES Inflow vs Pywr Outlet Flow")
plt.xlabel("Time")
plt.ylabel("Discharge")

plt.tight_layout()
plt.show()


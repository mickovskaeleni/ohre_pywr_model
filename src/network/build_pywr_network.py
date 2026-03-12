import pandas as pd

from pywr.model import Model
from pywr.nodes import Input, Output, Link


def build_pywr_network():

    print("Loading river edges...")
    edges = pd.read_csv("data/processed/river_edges.csv")

    model = Model()

    reaches = {}

    # --------------------------------------------------
    # Create river reaches (one per SWB)
    # --------------------------------------------------
    print("Creating SWB reaches...")

    swb_ids = set(edges["upstream"]).union(set(edges["downstream"]))

    for swb in swb_ids:
        reaches[swb] = Link(model, name=swb)

    # --------------------------------------------------
    # Connect reaches
    # --------------------------------------------------
    print("Connecting river network...")

    for _, row in edges.iterrows():

        upstream = row["upstream"]
        downstream = row["downstream"]

        reaches[upstream].connect(reaches[downstream])

    # --------------------------------------------------
    # Create basin outlet
    # --------------------------------------------------
    print("Creating basin outlet...")

    basin_outlet = Output(model, name="basin_outlet")

    # downstream basins are those that appear in downstream column
    upstream_set = set(edges["upstream"])
    downstream_set = set(edges["downstream"])

    terminal_basins = downstream_set - upstream_set

    # if detection fails, attach everything safely
    if len(terminal_basins) == 0:
        terminal_basins = swb_ids

    for basin in terminal_basins:
        reaches[basin].connect(basin_outlet)

    # --------------------------------------------------
    # Temporary inflows (for validation only)
    # --------------------------------------------------
    print("Adding temporary inflows...")

    for swb in swb_ids:

        inflow = Input(model, name=f"inflow_{swb}")
        inflow.connect(reaches[swb])

    return model


if __name__ == "__main__":

    model = build_pywr_network()

    print("Checking model structure...")
    model.check()

    print("✅ Pywr river network successfully built.")

    print("Running model...")
    model.run()

    print("✅ Model run completed.")
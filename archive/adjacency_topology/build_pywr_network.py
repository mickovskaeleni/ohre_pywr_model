from xml.parsers.expat import model

import pandas as pd
import pyreadr

from pywr.model import Model
from pywr.nodes import Input, Output, Link, Storage
from pywr.timestepper import Timestepper
from pywr.parameters import ArrayIndexedParameter
from pywr.parameters import DataFrameParameter



def build_pywr_network():

    print("Loading river edges...")
    edges = pd.read_csv("data/processed/river_edges.csv")

    print("Loading WATERES inflows...")

    result = pyreadr.read_r(
        "data/raw/WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
    )

    wateres = result[None]
    wateres["DTM"] = pd.to_datetime(wateres["DTM"])
    # keep only inflow variable
    wateres = wateres[
        (wateres["var"] == "inflow") &
        (wateres["loc"] == "outlet")
    ]

    model = Model()

    model.timestepper = Timestepper(
        start=pd.Timestamp("1991-01-01"),
        end=pd.Timestamp("2020-12-31"),
        delta=pd.Timedelta(days=1)
    )

    RES_UP = "OHL_0730"
    RES_DOWN = "OHL_0030"

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

        if upstream == RES_UP and downstream == RES_DOWN:

            reservoir = Storage(
                model,
                name="reservoir_test",
                max_volume=1000,
                initial_volume=500
            )

            release = Link(model, name="reservoir_release")

            reaches[upstream].connect(reservoir)
            reservoir.connect(release)
            release.connect(reaches[downstream])

        else:
            reaches[upstream].connect(reaches[downstream])

    # --------------------------------------------------
    # Create basin outlet
    # --------------------------------------------------
    print("Creating basin outlet...")

    basin_outlet = Output(
        model,
        name="basin_outlet",
        cost=-1,
        max_flow=1e9
    )

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
    # Attach WATERES inflows
    # --------------------------------------------------
    print("Attaching WATERES inflows...")

    for swb in swb_ids:

        swb_data = wateres[wateres["UPOV_ID"] == swb]

        if swb_data.empty:
            continue

        swb_data = swb_data.sort_values("DTM")
        swb_data = swb_data.drop_duplicates(subset="DTM")

        ts = swb_data.set_index("DTM")["value"].to_frame()
        ts = ts.asfreq("D")

        param = DataFrameParameter(model, ts)

        inflow = Input(model, name=f"inflow_{swb}")
        inflow.max_flow = param

        inflow.connect(reaches[swb])

    return model, basin_outlet


if __name__ == "__main__":

    model, basin_outlet= build_pywr_network()

    print("Checking model structure...")
    model.check()
    print("✅ Pywr river network successfully built.")

    print("Running model...")
    model.run()
    print("✅ Model run completed.")

    total_inflow = sum(
        node.flow.sum() for node in model.nodes if node.name.startswith("inflow")
    )

    total_outflow = basin_outlet.flow.sum()

    print(f"Total inflow: {total_inflow}")
    print(f"Total outflow: {total_outflow}")
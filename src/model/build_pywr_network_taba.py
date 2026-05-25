import pandas as pd
import pyreadr

from pywr.model import Model
from pywr.nodes import Input, Output, Link, Storage
from pywr.timestepper import Timestepper
from pywr.parameters import DataFrameParameter


def build_pywr_network_taba():

    # ==================================================
    # LOAD PROCESSED CONNECTIVITY
    # ==================================================
    print("Loading processed TABA connectivity...")

    edges = pd.read_csv(
        "data/processed/river_edges_taba.csv"
    )

    basin_types = pd.read_csv(
        "data/processed/basin_types_taba.csv"
    )

    print(f"Connectivity edges: {len(edges)}")


    # ==================================================
    # LOAD WATERES INFLOWS
    # ==================================================
    print("\nLoading WATERES inflows...")

    result = pyreadr.read_r(
        "data/raw/WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
    )

    wateres = result[None]

    # convert dates
    wateres["DTM"] = pd.to_datetime(
        wateres["DTM"]
    )

    # keep only inflow at outlet
    wateres = wateres[
        (wateres["var"] == "inflow") &
        (wateres["loc"] == "outlet")
    ]

    # model domain
    domain_ids = set(
        wateres["UPOV_ID"]
    )

    print(f"SWB basins: {len(domain_ids)}")


    # ==================================================
    # CREATE PYWR MODEL
    # ==================================================
    model = Model()

    model.timestepper = Timestepper(
        start=pd.Timestamp("1991-01-01"),
        end=pd.Timestamp("2020-12-31"),
        delta=pd.Timedelta(days=1)
    )


    # ==================================================
    # TEST RESERVOIR LOCATION
    # ==================================================
    # Prototype reservoir inserted into the routed
    # river network to test:
    #
    # - storage dynamics
    # - delayed routing
    # - infrastructure integration
    #
    # Water flow:
    #
    # upstream SWB
    #      ↓
    # reservoir storage
    #      ↓
    # release node
    #      ↓
    # downstream SWB
    # ==================================================
    RES_UP = "OHL_0225_J"
    RES_DOWN = "OHL_0230"


    # ==================================================
    # CREATE RIVER REACHES
    # ==================================================
    print("\nCreating SWB reaches...")

    reaches = {}

    for swb in domain_ids:

        reaches[swb] = Link(
            model,
            name=swb
        )


    # ==================================================
    # CONNECT REACHES
    # ==================================================
    print("Connecting TABA river network...")

    internal_connections = 0
    reservoir_inserted = False

    for _, row in edges.iterrows():

        upstream = row["FROM"]
        downstream = row["TO"]

        # --------------------------------------------------
        # ONLY CONNECT INTERNAL SWBs
        # --------------------------------------------------
        # If downstream basin exists in the model domain,
        # create routed river connection.
        # --------------------------------------------------
        if downstream in reaches:

            # --------------------------------------------------
            # INSERT TEST RESERVOIR
            # --------------------------------------------------
            if (
                upstream == RES_UP and
                downstream == RES_DOWN
            ):

                print(
                    f"Inserting test reservoir between "
                    f"{RES_UP} -> {RES_DOWN}"
                )

                # storage node
                reservoir = Storage(
                    model,
                    name="reservoir_test",
                    max_volume=50000,
                    initial_volume=0
                )

                # release node
                release = Link(
                    model,
                    name="reservoir_release"
                )

                release.max_flow = 5

                # connect routing
                reaches[upstream].connect(
                    reservoir
                )

                reservoir.connect(
                    release
                )

                release.connect(
                    reaches[downstream]
                )

                reservoir_inserted = True

            # --------------------------------------------------
            # STANDARD ROUTING
            # --------------------------------------------------
            else:

                reaches[upstream].connect(
                    reaches[downstream]
                )

            internal_connections += 1

    print(
        f"Internal routed connections: "
        f"{internal_connections}"
    )

    print(
        f"Reservoir inserted: "
        f"{reservoir_inserted}"
    )


    # ==================================================
    # CREATE BASIN OUTLET
    # ==================================================
    print("\nCreating basin outlet...")

    basin_outlet = Output(
        model,
        name="basin_outlet",
        cost=-1,
        max_flow=1e9
    )


    # ==================================================
    # CONNECT TERMINAL BASINS
    # ==================================================
    print("Connecting terminal basins...")

    terminal_basins = basin_types[
        basin_types["type"] == "terminal"
    ]["SWB"].tolist()

    print(
        f"Terminal basins: "
        f"{len(terminal_basins)}"
    )

    for basin in terminal_basins:

        reaches[basin].connect(
            basin_outlet
        )


    # ==================================================
    # ATTACH WATERES INFLOWS
    # ==================================================
    print("\nAttaching WATERES inflows...")

    inflow_count = 0

    for swb in domain_ids:

        swb_data = wateres[
            wateres["UPOV_ID"] == swb
        ]

        # skip empty inflow series
        if swb_data.empty:
            continue

        # sort dates
        swb_data = swb_data.sort_values(
            "DTM"
        )

        # remove duplicates
        swb_data = swb_data.drop_duplicates(
            subset="DTM"
        )

        # create daily time series
        ts = swb_data.set_index(
            "DTM"
        )["value"].to_frame()

        ts = ts.asfreq("D")

        # create Pywr parameter
        param = DataFrameParameter(
            model,
            ts
        )

        # create inflow node
        inflow = Input(
            model,
            name=f"inflow_{swb}"
        )

        inflow.max_flow = param

        # connect inflow
        inflow.connect(
            reaches[swb]
        )

        inflow_count += 1

    print(
        f"Inflows attached: "
        f"{inflow_count}"
    )


    # ==================================================
    # RETURN MODEL
    # ==================================================
    return model, basin_outlet


if __name__ == "__main__":

    print(
        "=== BUILDING PYWR NETWORK "
        "USING PROCESSED TABA TOPOLOGY ==="
    )

    model, basin_outlet = (
        build_pywr_network_taba()
    )

    print("\nChecking model structure...")

    model.check()

    print(
        "✅ Pywr river network successfully built."
    )

    print("\nRunning model...")

    model.run()

    print("✅ Model run completed.")


    # ==================================================
    # SIMPLE MASS BALANCE CHECK
    # ==================================================
    total_inflow = sum(
        node.flow.sum()
        for node in model.nodes
        if node.name.startswith("inflow")
    )

    total_outflow = basin_outlet.flow.sum()

    print(
        f"\nTotal inflow: "
        f"{total_inflow}"
    )

    print(
        f"Total outflow: "
        f"{total_outflow}"
    )
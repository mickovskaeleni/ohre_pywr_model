import pyreadr
import pandas as pd
from pywr.model import Model
from pywr.nodes import Input, Output, Link
from pywr.parameters import DataFrameParameter


def load_wateres(path):
    result = pyreadr.read_r(path)
    df = result[None]
    return df


def build_backbone_model(df):
    model = Model()

    # Define timestep first (important for parameter alignment)
    model.timestepper.start = df["DTM"].min()
    model.timestepper.end = df["DTM"].max()
    model.timestepper.delta = pd.Timedelta(days=1)

    # Create common basin outlet
    outlet = Output(model, name="basin_outlet")

    # Unique SWB IDs
    swb_ids = df["UPOV_ID"].unique()

    for swb in swb_ids:
        swb_df = df[df["UPOV_ID"] == swb]

        # Create clean time series (datetime index + single column)
        ts = swb_df.set_index("DTM")["value"].to_frame()

        # Sort and explicitly assign daily frequency
        ts = ts.sort_index()
        ts = ts.asfreq("D")

        # Create time-varying parameter
        param = DataFrameParameter(model, ts)

        # Create inflow node
        inflow = Input(model, name=f"inflow_{swb}")
        inflow.max_flow = param

        # Connect inflow to basin outlet
        link = Link(model, name=f"link_{swb}")

        inflow.connect(link)
        link.connect(outlet)

    return model


if __name__ == "__main__":

    print("Loading WATERES data...")
    wateres_path = "data/raw/WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
    df = load_wateres(wateres_path)

    print("Filtering inflow variable...")
    df = df[(df["var"] == "inflow") & (df["loc"] == "outlet")].copy()

    print("Converting DTM to datetime...")
    df["DTM"] = pd.to_datetime(df["DTM"])

    print("Building backbone model...")
    model = build_backbone_model(df)

    print("Checking model...")
    model.check()

    print("Running model...")
    model.run()

    print("✅ Backbone model built and executed successfully.")

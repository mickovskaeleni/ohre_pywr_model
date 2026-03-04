import pandas as pd
import pyreadr

from pywr.model import Model
from pywr.nodes import Input, Output, Link
from pywr.parameters import DataFrameParameter

from src.config import WATERES_FILE


def load_wateres():

    print("Loading WATERES dataset...")

    result = pyreadr.read_r(WATERES_FILE)
    df = result[None]

    # keep only routed inflow at basin outlets
    df = df[(df["var"] == "inflow") & (df["loc"] == "outlet")].copy()

    df["DTM"] = pd.to_datetime(df["DTM"])

    return df


def build_model(df):

    print("Building Pywr model...")

    model = Model()

    # define simulation period
    model.timestepper.start = df["DTM"].min()
    model.timestepper.end = df["DTM"].max()
    model.timestepper.delta = pd.Timedelta(days=1)

    reaches = {}

    swb_ids = df["UPOV_ID"].unique()

    # create river reaches
    for swb in swb_ids:
        reaches[swb] = Link(model, name=swb)

    # create basin outlet
    basin_outlet = Output(model, name="basin_outlet")

    # connect everything to outlet (temporary routing)
    for swb in swb_ids:
        reaches[swb].connect(basin_outlet)

    # attach WATERES inflows
    print("Attaching WATERES inflows...")

    for swb in swb_ids:

        swb_df = df[df["UPOV_ID"] == swb]

        ts = (
            swb_df
            .set_index("DTM")["value"]
            .sort_index()
            .to_frame()
        )

        param = DataFrameParameter(model, ts)

        inflow = Input(model, name=f"inflow_{swb}")
        inflow.max_flow = param

        inflow.connect(reaches[swb])

    return model


if __name__ == "__main__":

    df = load_wateres()

    model = build_model(df)

    print("Checking model...")
    model.check()

    print("Running model...")
    model.run()

    print("✅ WATERES inflows successfully attached.")
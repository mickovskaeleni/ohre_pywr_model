import pandas as pd
import pyreadr
import matplotlib.pyplot as plt
from src.config import WATERES_FILE, OUTPUT_DIR


def load_inflow():
    result = pyreadr.read_r(WATERES_FILE)
    df = result[None]

    df = df[(df["var"] == "inflow") & (df["loc"] == "outlet")].copy()
    df["DTM"] = pd.to_datetime(df["DTM"])

    return df


def validate_structure(df):
    print("\n--- BASIC STRUCTURE CHECK ---")

    print(f"Number of unique SWBs: {df['UPOV_ID'].nunique()}")
    print(f"Date range: {df['DTM'].min()} to {df['DTM'].max()}")

    duplicates = df.duplicated(subset=["UPOV_ID", "DTM"]).sum()
    print(f"Duplicate (SWB, date) rows: {duplicates}")

    missing_values = df["value"].isna().sum()
    print(f"Total NaN values: {missing_values}")

    print("\n--- CHECK PER SWB ---")

    expected_days = pd.date_range(df["DTM"].min(), df["DTM"].max(), freq="D")

    for swb, group in df.groupby("UPOV_ID"):
        group = group.set_index("DTM").sort_index()
        missing_days = expected_days.difference(group.index)

        if len(missing_days) > 0:
            print(f"{swb}: missing {len(missing_days)} days")

    print("Structure validation complete.\n")


def aggregate_basin_inflow(df):
    basin = df.groupby("DTM")["value"].sum().sort_index()
    return basin


def plot_basin_inflow(series):
    OUTPUT_DIR.mkdir(exist_ok=True)

    plt.figure(figsize=(12, 5))
    plt.plot(series.index, series.values)
    plt.title("Total Basin Inflow (Sum of SWB Routed Discharge)")
    plt.xlabel("Date")
    plt.ylabel("Discharge")
    plt.tight_layout()

    output_path = OUTPUT_DIR / "basin_total_inflow.png"
    plt.savefig(output_path)
    plt.close()

    print(f"Hydrograph saved to: {output_path}")


if __name__ == "__main__":

    print("Loading inflow data...")
    df = load_inflow()

    validate_structure(df)

    print("Aggregating basin inflow...")
    basin_series = aggregate_basin_inflow(df)

    print("\n--- BASIC STATISTICS ---")
    print(basin_series.describe())

    plot_basin_inflow(basin_series)

    print("✅ Validation completed.")

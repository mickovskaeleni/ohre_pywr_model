import pandas as pd
import pyreadr
import matplotlib.pyplot as plt
import numpy as np

from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error

from pywr.recorders import NumpyArrayNodeRecorder

from src.model.build_pywr_network_taba import (
    build_pywr_network_taba
)


def validate_pywr_vs_wateres_taba():

    # ==================================================
    # BUILD MODEL
    # ==================================================
    print("Building TABA Pywr model...")

    model, basin_outlet = (
        build_pywr_network_taba()
    )

    # --------------------------------------------------
    # Attach outlet recorder
    # --------------------------------------------------
    rec = NumpyArrayNodeRecorder(
        model,
        basin_outlet
    )

    print("Running model...")

    model.run()

    print("✅ Model simulation completed.")

    # extract recorded flow
    pywr_flow = np.array(rec.data)


    # ==================================================
    # LOAD WATERES DATA
    # ==================================================
    print("\nLoading WATERES reference inflow...")

    result = pyreadr.read_r(
        "data/raw/WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
    )

    wateres = result[None]

    wateres["DTM"] = pd.to_datetime(
        wateres["DTM"]
    )

    # keep only inflow at outlet
    wateres = wateres[
        (wateres["var"] == "inflow") &
        (wateres["loc"] == "outlet")
    ]


    # ==================================================
    # AGGREGATE WATERES INFLOW
    # ==================================================
    print("Aggregating WATERES inflow...")

    wateres_total = (
        wateres
        .groupby("DTM")["value"]
        .sum()
        .reset_index()
    )

    print(
        f"WATERES length: {len(wateres_total)}"
    )

    print(
        f"Pywr length: {len(pywr_flow)}"
    )


    # ==================================================
    # VALIDATION METRICS
    # ==================================================
    print("\nCalculating validation metrics...")

    r2 = r2_score(
        wateres_total["value"],
        pywr_flow
    )

    rmse = np.sqrt(
        mean_squared_error(
            wateres_total["value"],
            pywr_flow
        )
    )

    print(f"R²: {r2}")
    print(f"RMSE: {rmse}")


    # ==================================================
    # PLOT VALIDATION
    # ==================================================
    print("\nGenerating validation plot...")

    plt.figure(figsize=(16, 6))

    # WATERES reference
    plt.plot(
        wateres_total["DTM"],
        wateres_total["value"],
        label="WATERES total inflow",
        linewidth=1,
        alpha=0.7
    )

    # Pywr routed discharge
    plt.plot(
        wateres_total["DTM"],
        pywr_flow,
        label="Pywr outlet discharge",
        linewidth=1,
        alpha=0.7
    )

    plt.title(
        "Validation of TABA-based Pywr Routing\n"
        "against WATERES Aggregated Inflow",
        fontsize=16
    )

    plt.xlabel("Date")
    plt.ylabel("Discharge")

    plt.legend()

    plt.tight_layout()

    # save figure
    output_file = (
        "outputs/validation_wateres_vs_pywr_taba.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    print(
        f"✅ Validation figure saved to: "
        f"{output_file}"
    )

    plt.show()


if __name__ == "__main__":

    print(
        "=== VALIDATING TABA PYWR ROUTING ==="
    )

    validate_pywr_vs_wateres_taba()

    print("\n✅ Validation completed.")
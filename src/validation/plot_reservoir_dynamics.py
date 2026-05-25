import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pywr.recorders import (
    NumpyArrayNodeRecorder
)

from src.model.build_pywr_network_taba import (
    build_pywr_network_taba
)


def plot_reservoir_dynamics():

    print(
        "=== ANALYZING RESERVOIR DYNAMICS ==="
    )

    # ==================================================
    # BUILD MODEL
    # ==================================================
    model, basin_outlet = (
        build_pywr_network_taba()
    )

    # ==================================================
    # GET IMPORTANT NODES
    # ==================================================
    upstream_node = model.nodes[
        "inflow_OHL_0225_J"
    ]

    release_node = model.nodes[
        "reservoir_release"
    ]

    downstream_node = model.nodes[
        "OHL_0230"
    ]

    reservoir_node = model.nodes[
        "reservoir_test"
    ]


    # ==================================================
    # ATTACH RECORDERS
    # ==================================================
    print("Attaching recorders...")

    upstream_rec = (
        NumpyArrayNodeRecorder(
            model,
            upstream_node
        )
    )

    release_rec = (
        NumpyArrayNodeRecorder(
            model,
            release_node
        )
    )

    downstream_rec = (
        NumpyArrayNodeRecorder(
            model,
            downstream_node
        )
    )

    reservoir_storage_rec = (
        NumpyArrayNodeRecorder(
            model,
            reservoir_node
        )
    )


    # ==================================================
    # RUN MODEL
    # ==================================================
    print("Running model...")

    model.run()

    print("✅ Simulation completed.")


    # ==================================================
    # CREATE TIME INDEX
    # ==================================================
    dates = pd.date_range(
        start="1991-01-01",
        end="2020-12-31",
        freq="D"
    )


    # ==================================================
    # EXTRACT DATA
    # ==================================================
    upstream_flow = np.array(
        upstream_rec.data
    )

    release_flow = np.array(
        release_rec.data
    )

    downstream_flow = np.array(
        downstream_rec.data
    )

    reservoir_storage = np.array(
        reservoir_storage_rec.data
    )


    # ==================================================
    # PLOT 1 — INFLOW VS RELEASE
    # ==================================================
    plt.figure(figsize=(16, 6))

    plt.plot(
        dates,
        upstream_flow,
        label="Reservoir inflow",
        linewidth=1
    )

    plt.plot(
        dates,
        release_flow,
        label="Reservoir release",
        linewidth=1
    )

    plt.title(
        "Reservoir Inflow vs Release",
        fontsize=16
    )

    plt.xlabel("Date")
    plt.ylabel("Discharge")

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        "outputs/reservoir_inflow_vs_release.png",
        dpi=300,
        bbox_inches="tight"
    )

    print(
        "✅ Saved: "
        "outputs/reservoir_inflow_vs_release.png"
    )

    plt.show()


if __name__ == "__main__":

    plot_reservoir_dynamics()
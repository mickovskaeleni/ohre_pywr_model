import pandas as pd
import pyreadr


def build_connectivity_taba():

    # ==================================================
    # LOAD WATERES DOMAIN
    # ==================================================
    print("Loading WATERES domain...")

    result = pyreadr.read_r(
        "data/raw/WRI_wateres_SWB_subset_deficit_inflow_yield_1991_2020.rds"
    )

    wateres = result[None]

    # keep only inflow at outlet
    wateres = wateres[
        (wateres["var"] == "inflow") &
        (wateres["loc"] == "outlet")
    ]

    domain_ids = set(wateres["UPOV_ID"])

    print(f"SWB basins in domain: {len(domain_ids)}")


    # ==================================================
    # LOAD TABA TOPOLOGY
    # ==================================================
    print("\nLoading TABA topology...")

    taba = pyreadr.read_r(
        "data/raw/from_petr/TABA.rds"
    )[None]

    print(f"TABA rows: {len(taba)}")


    # ==================================================
    # FILTER CONNECTIVITY
    # ==================================================
    # IMPORTANT:
    # Keep all upstream SWBs that belong to the
    # Ohře WATERES domain.
    #
    # Downstream basins may leave the domain.
    # ==================================================
    print("\nFiltering connectivity...")

    edges = taba[
        taba["FROM"].isin(domain_ids)
    ][["FROM", "TO"]].drop_duplicates()

    print(f"Filtered edges: {len(edges)}")


    # ==================================================
    # CLASSIFY BASINS
    # ==================================================
    print("\nClassifying basins...")

    basin_types = []

    for swb in domain_ids:

        # all downstream targets for this SWB
        downstreams = edges[
            edges["FROM"] == swb
        ]["TO"].tolist()

        # --------------------------------------------------
        # INTERNAL BASIN
        # --------------------------------------------------
        if any(d in domain_ids for d in downstreams):

            basin_type = "internal"

        # --------------------------------------------------
        # TERMINAL / DOMAIN EXIT BASIN
        # --------------------------------------------------
        else:

            basin_type = "terminal"

        basin_types.append({
            "SWB": swb,
            "type": basin_type
        })

    basin_types = pd.DataFrame(basin_types)

    print(
        basin_types["type"].value_counts()
    )


    # ==================================================
    # SAVE OUTPUTS
    # ==================================================
    print("\nSaving outputs...")

    edges.to_csv(
        "data/processed/river_edges_taba.csv",
        index=False
    )

    basin_types.to_csv(
        "data/processed/basin_types_taba.csv",
        index=False
    )

    print("✅ Saved:")
    print(" - data/processed/river_edges_taba.csv")
    print(" - data/processed/basin_types_taba.csv")


if __name__ == "__main__":

    print("=== BUILDING TABA CONNECTIVITY ===")

    build_connectivity_taba()

    print("\n✅ TABA connectivity preprocessing completed.")
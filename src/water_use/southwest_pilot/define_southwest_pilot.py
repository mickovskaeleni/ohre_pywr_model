import pandas as pd
import pyreadr

from pathlib import Path
from collections import defaultdict


# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

TABA_PATH = (
    RAW_DIR /
    "SWB_ohre" /
    "TABA.rds"
)

OUTPUT_PATH = (
    PROCESSED_DIR /
    "southwest_pilot_swbs.csv"
)


# ======================================================
# SETTINGS
# ======================================================

PILOT_OUTLET = "OHL_0500"


# ======================================================
# LOAD TABA
# ======================================================

print("Loading TABA...")

taba = pyreadr.read_r(
    TABA_PATH
)[None]

taba = taba.rename(
    columns={
        "from": "FROM",
        "to": "TO"
    }
)

print("Edges:", len(taba))


# ======================================================
# BUILD GRAPH
# ======================================================

upstream_dict = defaultdict(list)

for _, row in taba.iterrows():

    upstream_dict[
        row["TO"]
    ].append(
        row["FROM"]
    )


# ======================================================
# TRACE UPSTREAM
# ======================================================

def get_all_upstream(
    node,
    visited=None
):

    if visited is None:
        visited = set()

    if node in visited:
        return visited

    visited.add(node)

    for up in upstream_dict.get(node, []):

        get_all_upstream(
            up,
            visited
        )

    return visited


# ======================================================
# DEFINE PILOT
# ======================================================

pilot_swbs = get_all_upstream(
    PILOT_OUTLET
)

pilot_swbs = sorted(
    list(pilot_swbs)
)

pilot_df = pd.DataFrame(
    {
        "UPOV_ID": pilot_swbs
    }
)


# ======================================================
# SAVE
# ======================================================

pilot_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ======================================================
# SUMMARY
# ======================================================

print("\n====================")
print("SOUTHWEST PILOT")
print("====================")

print("Outlet:", PILOT_OUTLET)

print(
    "Number of SWBs:",
    len(pilot_df)
)

print(
    "\nSaved to:",
    OUTPUT_PATH
)

print("\nDone.")
import pyreadr
from pathlib import Path


# ======================================================
# PATHS
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TABA_PATH = (
    BASE_DIR /
    "data" /
    "raw" /
    "SWB_ohre" /
    "TABA.rds"
)


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


# ======================================================
# BUILD DOWNSTREAM DICT
# ======================================================

downstream_dict = {}

for _, row in taba.iterrows():

    downstream_dict[
        row["FROM"]
    ] = row["TO"]


# ======================================================
# TRACE FUNCTION
# ======================================================

def trace_downstream(start_node):

    path = [start_node]

    current = start_node

    visited = set()

    while current in downstream_dict:

        if current in visited:

            print("Loop detected.")
            break

        visited.add(current)

        current = downstream_dict[current]

        path.append(current)

    return path


# ======================================================
# CANDIDATES
# ======================================================

candidates = [
    "OHL_0240",  # F
    "OHL_0270",  # E
    "OHL_0045_J",  # Stanovice
    "OHL_0460"     # Brezova
]


# ======================================================
# RUN
# ======================================================

for candidate in candidates:

    print("\n====================")
    print(candidate)
    print("====================")

    path = trace_downstream(
        candidate
    )

    for node in path:

        print(node)
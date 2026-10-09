#!/usr/bin/env python3
"""Write a JSON catalogue of four-face SU(2) recoupling labels."""

import argparse
import json
from pathlib import Path

from lqg_scattering.labels import (
    compositions, enumerate_range, enumerate_total_area, intermediate_labels,
)
from project_paths import DASHBOARD_ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-j", type=int, default=5)
    parser.add_argument("--output", type=Path, default=DASHBOARD_ROOT / "fl-volume-allowed-labels.json")
    args = parser.parse_args()
    data = enumerate_range(args.max_j)
    args.output.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    for row in data["totals"]:
        print(
            "J={areaLabelJ}: closure sectors={closureSectors}, "
            "four-face sectors={fourNonzeroFaceSectors}, "
            "strict-polygon sectors={strictPolygonSectors}, "
            "strict-polygon intertwiner states={strictPolygonIntertwinerDimension}".format(**row)
        )

if __name__ == "__main__":
    main()

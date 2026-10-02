#!/usr/bin/env python3
"""Enumerate four-valent SU(2) spin and recoupling labels at fixed total J.

These are finite quantum labels, not a finite list of classical polyhedron
shapes. At fixed nonzero face areas, the classical tetrahedron shape space is
continuous; this file records the separate discrete coupling basis.
"""

import argparse
import json
from pathlib import Path


def compositions(total, parts, minimum=0):
    """Yield ordered integer compositions with each entry at least minimum."""
    if parts == 1:
        if total >= minimum:
            yield (total,)
        return
    largest = total - minimum * (parts - 1)
    for first in range(minimum, largest + 1):
        for rest in compositions(total - first, parts - 1, minimum):
            yield (first,) + rest


def intermediate_labels(twice_spins):
    """Return allowed 2k labels for ((j0,j1)k,(j2,j3)k) coupling."""
    m0, m1, m2, m3 = twice_spins
    lower01, upper01 = abs(m0 - m1), m0 + m1
    lower23, upper23 = abs(m2 - m3), m2 + m3
    return [
        twice_k
        for twice_k in range(lower01, upper01 + 1, 2)
        if lower23 <= twice_k <= upper23
        and (twice_k - lower23) % 2 == 0
    ]


def enumerate_total_area(j_total):
    """Enumerate labelled spin sectors and their exact recoupling channels."""
    twice_total = 2 * j_total
    records = []
    for twice_spins in compositions(twice_total, 4, minimum=0):
        # The polygon inequality is necessary and sufficient for closed face
        # vectors: no one face area may exceed the sum of the other three.
        if max(twice_spins) > j_total:
            continue
        channels = intermediate_labels(twice_spins)
        if not channels:
            continue
        records.append(
            {
                "twiceSpins": list(twice_spins),
                "spins": [value / 2 for value in twice_spins],
                "intermediateTwiceK": channels,
                "intermediateK": [value / 2 for value in channels],
                "intertwinerDimension": len(channels),
                "allFacesNonzero": all(value > 0 for value in twice_spins),
                "strictPolygonInequality": max(twice_spins) < j_total,
            }
        )

    active_faces = [row for row in records if row["allFacesNonzero"]]
    nondegenerate = [row for row in active_faces if row["strictPolygonInequality"]]
    return {
        "areaLabelJ": j_total,
        "orderedLegs": [0, 1, 2, 3],
        "closureSectors": len(records),
        "closureIntertwinerDimension": sum(row["intertwinerDimension"] for row in records),
        "fourNonzeroFaceSectors": len(active_faces),
        "fourNonzeroFaceIntertwinerDimension": sum(
            row["intertwinerDimension"] for row in active_faces
        ),
        "strictPolygonSectors": len(nondegenerate),
        "strictPolygonIntertwinerDimension": sum(
            row["intertwinerDimension"] for row in nondegenerate
        ),
        "sectors": records,
    }


def enumerate_range(max_j):
    if max_j < 1:
        raise ValueError("max_j must be at least 1")
    totals = [enumerate_total_area(j) for j in range(1, max_j + 1)]
    return {
        "schemaVersion": 1,
        "model": "Four labelled SU(2) legs with total spin J=sum_i j_i",
        "spinConvention": "twiceSpins[i]=2*j_i is a nonnegative integer; total twice-spin is 2J",
        "closureCriterion": "max_i(j_i) <= sum_{r != i}(j_r); strict inequality excludes the collinear closure boundary but does not remove planar configurations",
        "basisConvention": "A recoupling basis couples (j0,j1) and (j2,j3) through the same intermediate spin k; k advances in integer steps.",
        "interpretation": "Finite quantum spin and intertwiner labels only. Classical shapes at fixed face areas form a continuum, so they require a stated mesh or an analytic parametrization. This is not Thurston's lattice classification of special sphere triangulations.",
        "thurstonReference": "https://arxiv.org/abs/math/9801088",
        "totals": [
            {key: value for key, value in row.items() if key != "sectors"}
            for row in totals
        ],
        "areaSectors": totals,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-j", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("dashboard/fl-volume-allowed-labels.json"))
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

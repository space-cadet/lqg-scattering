#!/usr/bin/env python3
"""Probe both orders of the large-J and flat-shape limits for T5c."""

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np

from fl_volume_shape_scan import closed_equal_area_normals, four_point_cross_ratio
from fl_volume_validation import GAMMA, fixed_area_state, spinors_from_normals
from t5c_input_geometry_scan import (
    GEOMETRY_MATCHING_FACTORS,
    classical_volume_from_faces,
    volume_moments,
)
from project_paths import RESULTS_ROOT


def sample(area_label, phi):
    x = 1.0 / math.sqrt(3.0)
    normals = closed_equal_area_normals(x, phi)
    fractions = np.full(4, 0.25)
    face_vectors = fractions[:, None] * normals
    classical_volume = classical_volume_from_faces(face_vectors)
    classical_project = GAMMA**1.5 * classical_volume
    unit_spinors = spinors_from_normals(normals)
    weighted_spinors = math.sqrt(0.5) * unit_spinors
    closure_matrix = sum(
        np.outer(z, z.conj()) for z in weighted_spinors
    )
    space, state = fixed_area_state(area_label, spinors=weighted_spinors)
    moments = volume_moments(state, space)
    normalized = {}
    for operator in ("rs", "al"):
        factor = GEOMETRY_MATCHING_FACTORS[operator]
        mean = moments[operator]["meanProjectUnits"] / area_label**1.5
        sd = math.sqrt(moments[operator]["varianceProjectUnitsSquared"]) / area_label**1.5
        mean *= factor
        sd *= factor
        normalized[operator] = {
            "geometryMatchedMeanOverJ32": mean,
            "geometryMatchedSDOverJ32": sd,
            "absoluteDifferenceOverJ32": abs(mean - classical_project),
            "ratioToClassical": (
                None if classical_project <= 1e-14 else mean / classical_project
            ),
        }
    cross_ratio = four_point_cross_ratio(unit_spinors)
    return {
        "J": area_label,
        "phiRadians": phi,
        "classicalVolumeAtUnitTotalArea": classical_volume,
        "classicalVolumeProjectUnitsAtUnitTotalArea": classical_project,
        "normalClosureResidual": float(np.linalg.norm(normals.sum(axis=0))),
        "weightedSpinorClosureMatrixError": float(
            np.linalg.norm(closure_matrix - np.eye(2))
        ),
        "faceNormalCrossRatioReal": float(cross_ratio.real),
        "faceNormalCrossRatioImag": float(cross_ratio.imag),
        "rs": normalized["rs"],
        "al": normalized["al"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--j-values", nargs="+", type=int, default=[2, 4, 6])
    parser.add_argument(
        "--phi-values", nargs="+", type=float,
        default=[0.0, 0.05, math.pi / 2.0],
        help="radians on the fixed-x path; phi=0 is exactly flat",
    )
    parser.add_argument("--output", type=Path,
                        default=RESULTS_ROOT / "t5c_degenerate_limits_results.json")
    args = parser.parse_args()
    if any(j < 1 for j in args.j_values):
        parser.error("all J values must be positive integers")
    if any(phi < 0.0 or phi > math.pi / 2.0 for phi in args.phi_values):
        parser.error("phi values must lie in [0, pi/2]")

    rows = [sample(J, phi) for J in args.j_values for phi in args.phi_values]
    result = {
        "model": "equal-area FL family; x=1/sqrt(3), phi approaches the flat boundary 0",
        "runtime": {"python": sys.version.split()[0], "numpy": np.__version__},
        "areaFractions": [0.25] * 4,
        "jValues": args.j_values,
        "phiValuesRadians": args.phi_values,
        "fixedGeometryMatchingFactors": GEOMETRY_MATCHING_FACTORS,
        "limitProtocol": {
            "largeJFirst": "At each fixed positive phi, inspect J growth; then take phi toward zero.",
            "degenerateFirst": "At fixed J, use the exact phi=0 state; then inspect its J dependence.",
            "boundaryRatios": "Omitted at zero classical volume; compare absolute normalized values.",
        },
        "results": rows,
    }
    encoded = json.dumps(result, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()

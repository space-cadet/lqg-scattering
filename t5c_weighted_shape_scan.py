#!/usr/bin/env python3
"""Sample unequal-area tetrahedron shapes at fixed face-area fractions."""

import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np

from fl_volume_shape_scan import four_point_cross_ratio
from fl_volume_validation import GAMMA, fixed_area_state, spinors_from_normals
from t5c_covariance_probe import tetrahedron_from_face_vectors
from t5c_input_geometry_scan import (
    GEOMETRY_MATCHING_FACTORS,
    classical_volume_from_faces,
    circumsphere_shape_data,
    closed_face_vectors_from_shape,
    expected_face_spins,
    flux_correlation_geometry,
    volume_moments,
)


def shape_record(area_fractions, diagonal, phi, area_labels):
    faces = closed_face_vectors_from_shape(area_fractions, diagonal, phi)
    areas = np.linalg.norm(faces, axis=1)
    normals = faces / areas[:, None]
    unit_spinors = spinors_from_normals(normals)
    weighted_spinors = np.sqrt(2.0 * np.asarray(area_fractions))[:, None] * unit_spinors
    closure_matrix = sum(np.outer(z, z.conj()) for z in weighted_spinors)
    vertices, coordinate_volume, reconstructed = tetrahedron_from_face_vectors(faces)
    classical_volume = classical_volume_from_faces(faces)
    if abs(coordinate_volume - classical_volume) > 1e-10:
        raise ArithmeticError("coordinate and face-vector volumes disagree")
    cross_ratio = four_point_cross_ratio(unit_spinors)

    results = []
    for J in area_labels:
        space, state = fixed_area_state(J, spinors=weighted_spinors)
        means = expected_face_spins(state)
        target = J * np.asarray(area_fractions)
        moments = volume_moments(state, space)
        covariance = flux_correlation_geometry(state, space, normals)
        row = {
            "J": J,
            "maxMeanFaceSpinError": float(np.max(np.abs(means - target))),
            "meanFaceSpins": means.tolist(),
            "covarianceGeometry": covariance,
        }
        for operator in ("rs", "al"):
            factor = GEOMETRY_MATCHING_FACTORS[operator]
            mean = moments[operator]["meanProjectUnits"] / J**1.5
            sd = math.sqrt(moments[operator]["varianceProjectUnitsSquared"]) / J**1.5
            mean *= factor
            sd *= factor
            target_volume = GAMMA**1.5 * classical_volume
            row[operator] = {
                "geometryMatchedMeanOverJ32": mean,
                "geometryMatchedSDOverJ32": sd,
                "classicalVolumeProjectUnitsAtUnitTotalArea": target_volume,
                "absoluteDifferenceOverJ32": abs(mean - target_volume),
                "ratioToClassical": mean / target_volume,
            }
        results.append(row)

    return {
        "pairDiagonalAtUnitTotalArea": diagonal,
        "bendAngleRadians": phi,
        "faceAreaFractions": list(area_fractions),
        "faceNormalCrossRatioReal": float(cross_ratio.real),
        "faceNormalCrossRatioImag": float(cross_ratio.imag),
        "vertexCircumsphereShape": circumsphere_shape_data(vertices),
        "faceAreaClosureResidual": float(np.linalg.norm(faces.sum(axis=0))),
        "weightedSpinorClosureMatrixError": float(
            np.linalg.norm(closure_matrix - np.eye(2))
        ),
        "classicalVolumeAtUnitTotalArea": classical_volume,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--j-values", nargs="+", type=int, default=[2, 4])
    parser.add_argument("--diagonal-fractions", nargs="+", type=float,
                        default=[0.25, 0.5, 0.75])
    parser.add_argument("--phi-degrees", nargs="+", type=float,
                        default=[45.0, 90.0, 135.0])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if any(j < 1 for j in args.j_values):
        parser.error("all J values must be positive integers")
    if any(not 0.0 < value < 1.0 for value in args.diagonal_fractions):
        parser.error("diagonal fractions must lie strictly between zero and one")
    if any(not 0.0 < value < 180.0 for value in args.phi_degrees):
        parser.error("bend angles must lie strictly between zero and 180 degrees")

    areas = [0.32, 0.18, 0.30, 0.20]
    lower = max(abs(areas[0] - areas[1]), abs(areas[2] - areas[3]))
    upper = min(areas[0] + areas[1], areas[2] + areas[3])
    diagonals = [
        lower + f * (upper - lower) for f in args.diagonal_fractions
    ]
    bends = [math.radians(value) for value in args.phi_degrees]
    cases = [
        shape_record(areas, d, phi, args.j_values)
        for d in diagonals for phi in bends
    ]
    result = {
        "model": "weighted FL fixed-area states for a closed tetrahedron family",
        "runtime": {"python": sys.version.split()[0], "numpy": np.__version__},
        "areaFractions": areas,
        "shapeParameters": {
            "diagonal": "|F0+F1| at unit total area",
            "bendAngle": "rotation of the F2,F3 pair around the common diagonal",
            "diagonalFractionsWithinAllowedInterval": args.diagonal_fractions,
            "bendAnglesDegrees": args.phi_degrees,
        },
        "fixedGeometryMatchingFactors": GEOMETRY_MATCHING_FACTORS,
        "results": cases,
        "interpretationLimits": [
            "This is a small unequal-area shape grid, not a convergence study.",
            "Both the face-spinor cross-ratio and vertex circumsphere cross-ratio are recorded with metric data.",
            "AL uses the existing (+,-,+,-) tangent-sign convention.",
        ],
    }
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare positive FL volumes with the classical input tetrahedron.

This first T5c driver takes tetrahedron vertices as the geometry source,
derives closed outward face-area vectors, and constructs weighted FL spinors
from the resulting area fractions and normals. Results use the repository's
project normalization and the existing fixed AL sign convention.
"""

import itertools
import json
import math
from pathlib import Path
import sys

import numpy as np

from lqg_scattering.conventions import GAMMA
from lqg_scattering.fl_volume import N, ORIENTATIONS
from lqg_scattering.intertwiners import fixed_area_state
from lqg_scattering.observables import (
    expected_face_spins, flux_correlation_geometry, volume_moments,
)
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.tetrahedra import (
    GEOMETRY_MATCHING_FACTORS, circumsphere_shape_data, classical_volume_from_faces,
    face_area_vectors,
)
from lqg_scattering.positivity import ashtekar_lewandowski_volume, rovelli_smolin_volume
from project_paths import RESULTS_ROOT


TRIPLES = tuple(itertools.combinations(range(N), 3))
AL_SIGNS = dict(zip(TRIPLES, ORIENTATIONS))


def geometry_case(name, vertices):
    faces = face_area_vectors(vertices)
    areas = np.linalg.norm(faces, axis=1)
    total_area = float(areas.sum())
    fractions = areas / total_area
    normals = faces / areas[:, None]
    unit_faces = fractions[:, None] * normals
    closure = float(np.linalg.norm(unit_faces.sum(axis=0)))
    classical_volume = classical_volume_from_faces(unit_faces)
    coordinate_volume = abs(float(np.linalg.det(
        np.asarray(vertices)[1:] - np.asarray(vertices)[0]
    ))) / 6.0
    unit_coordinate_volume = coordinate_volume / total_area**1.5
    if abs(classical_volume - unit_coordinate_volume) > 1e-11:
        raise ArithmeticError("face-vector and coordinate volumes disagree")

    unit_spinors = spinors_from_normals(normals)
    weighted_spinors = np.sqrt(2.0 * fractions)[:, None] * unit_spinors
    closure_matrix = sum(
        np.outer(z, z.conj()) for z in weighted_spinors
    )
    closure_matrix_error = float(np.linalg.norm(closure_matrix - np.eye(2)))
    return {
        "name": name,
        "vertices": np.asarray(vertices, dtype=float).tolist(),
        "sphereShapeData": circumsphere_shape_data(vertices),
        "faceAreaFractions": fractions.tolist(),
        "faceNormals": normals.tolist(),
        "faceAreaClosureResidual": closure,
        "spinorClosureMatrixMaxError": closure_matrix_error,
        "classicalVolumeAtUnitTotalArea": classical_volume,
        "classicalVolumeProjectUnitsAtUnitTotalArea": GAMMA**1.5 * classical_volume,
        "weightedSpinors": weighted_spinors,
    }


def evaluate_case(case, area_labels):
    fractions = np.asarray(case["faceAreaFractions"])
    spinors = np.asarray(case["weightedSpinors"], dtype=complex)
    normals = np.asarray(case["faceNormals"], dtype=float)
    rows = []
    for J in area_labels:
        space, state = fixed_area_state(J, spinors=spinors)
        means = expected_face_spins(state)
        target = J * fractions
        if np.max(np.abs(means - target)) > 2e-11:
            raise ArithmeticError(
                f"weighted FL mean-spin check failed at J={J}: {means} vs {target}"
            )
        moments = volume_moments(state, space)
        covariance = flux_correlation_geometry(state, space, normals)
        # Check the moment calculation against the established expectation API.
        direct_rs = rovelli_smolin_volume(state, space)
        direct_al = ashtekar_lewandowski_volume(state, space, AL_SIGNS)
        if abs(moments["rs"]["meanProjectUnits"] - direct_rs) > 2e-11:
            raise ArithmeticError("RS moment mean disagrees with volume API")
        if abs(moments["al"]["meanProjectUnits"] - direct_al) > 2e-11:
            raise ArithmeticError("AL moment mean disagrees with volume API")

        Jscale = J**1.5
        row = {
            "J": J,
            "meanFaceSpins": means.tolist(),
            "maxMeanFaceSpinError": float(np.max(np.abs(means - target))),
            "covarianceGeometry": covariance,
            "classicalVolumeProjectUnitsAtJ": (
                case["classicalVolumeProjectUnitsAtUnitTotalArea"] * Jscale
            ),
        }
        for key, label in (("rs", "RS"), ("al", "AL")):
            mean = moments[key]["meanProjectUnits"]
            variance = moments[key]["varianceProjectUnitsSquared"]
            normalized_mean = mean / Jscale
            normalized_sd = math.sqrt(variance) / Jscale
            classical = case["classicalVolumeProjectUnitsAtUnitTotalArea"]
            geometry_factor = GEOMETRY_MATCHING_FACTORS[key]
            geometry_mean = geometry_factor * normalized_mean
            geometry_sd = geometry_factor * normalized_sd
            row[f"{key}MeanProjectUnits"] = mean
            row[f"{key}VarianceProjectUnitsSquared"] = variance
            row[f"{key}MeanOverJ32"] = normalized_mean
            row[f"{key}SDOverJ32"] = normalized_sd
            row[f"{key}GeometryMatchedMeanOverJ32"] = geometry_mean
            row[f"{key}GeometryMatchedSDOverJ32"] = geometry_sd
            row[f"{key}GeometryMatchedAbsoluteDifferenceOverJ32"] = abs(
                geometry_mean - classical
            )
            row[f"{key}RawToClassicalRatio"] = normalized_mean / classical
            row[f"{key}ToClassicalRatio"] = geometry_mean / classical
        rows.append(row)
    return rows


def main():
    parser = __import__("argparse").ArgumentParser()
    parser.add_argument("--j-max", type=int, default=5)
    parser.add_argument("--output", type=Path,
                        default=RESULTS_ROOT / "t5c_input_geometry_results.json")
    args = parser.parse_args()
    if args.j_max < 1:
        parser.error("--j-max must be positive")

    regular = np.array([
        [1.0, 1.0, 1.0], [1.0, -1.0, -1.0],
        [-1.0, 1.0, -1.0], [-1.0, -1.0, 1.0],
    ])
    unequal = np.array([
        [0.0, 0.0, 0.0], [1.8, 0.1, 0.0],
        [0.15, 0.9, 0.1], [0.2, 0.25, 1.1],
    ])
    cases = [
        geometry_case("regular", regular),
        geometry_case("unequal_skew", unequal),
    ]
    labels = list(range(1, args.j_max + 1))
    result = {
        "model": "Freidel-Livine fixed-area state with weighted coherent spinors",
        "runtime": {"python": sys.version.split()[0], "numpy": np.__version__},
        "normalization": {
            "volumeOperator": "gamma^(3/2) times the repository positive RS/AL operator",
            "gamma": GAMMA,
            "hbar": 1.0,
            "classicalVolume": "gamma^(3/2) sqrt(2/9 |det(F1,F2,F3)|), with no fitted shape factor",
            "fixedGeometryMatchingFactors": GEOMETRY_MATCHING_FACTORS,
            "factorDerivation": "For a closed 4-valent vertex and signs (+,-,+,-), the raw RS operator is 4 sqrt(|q|), the raw AL operator is 2 sqrt(|q|), and tetrahedron volume is sqrt(2/9) sqrt(|q|).",
            "scaleRelations": "V = R_circumradius^3 * V_at_unit_circumradius = A_total^(3/2) * V_at_unit_total_area.",
            "shapeCoordinates": "The ordered vertex cross-ratio is recorded on the unit circumsphere; the six normalized chord lengths retain the Euclidean similarity shape needed for volume.",
            "alOrientationSignsByLexicographicTriple": [
                AL_SIGNS[t] for t in TRIPLES
            ],
        },
        "areaLabelsJ": labels,
        "cases": [
            {key: value for key, value in case.items() if key != "weightedSpinors"}
            | {"results": evaluate_case(case, labels)}
            for case in cases
        ],
        "interpretationLimits": [
            "The two geometries validate weighted inputs and establish a pilot, not a shape-uniform classical limit.",
            "AL values use the existing fixed sign convention and remain embedding-dependent.",
            "Area labels J are integers in this exact Fock implementation.",
        ],
    }
    encoded = json.dumps(result, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()

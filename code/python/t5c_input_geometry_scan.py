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

from coherent_states import expectation, su2_ops
from fl_volume_validation import GAMMA, N, ORIENTATIONS, fixed_area_state, spinors_from_normals
from positivity import (
    _active_vertex_blocks,
    _dot_ops,
    _triple_matrix_block,
    ashtekar_lewandowski_volume,
    rovelli_smolin_volume,
)
from project_paths import RESULTS_ROOT


TRIPLES = tuple(itertools.combinations(range(N), 3))
AL_SIGNS = dict(zip(TRIPLES, ORIENTATIONS))
ZERO_FACTOR = 64.0 * np.finfo(float).eps
GEOMETRY_MATCHING_FACTORS = {
    # V_class = sqrt(2/9) sqrt(|det(F1,F2,F3)|). On a closed 4-valent
    # vertex the repository RS sum is 4 sqrt(|q|), while this AL sign map
    # gives sqrt(|4 q|) = 2 sqrt(|q|).
    "rs": math.sqrt(2.0) / 12.0,
    "al": math.sqrt(2.0) / 6.0,
}


def face_area_vectors(vertices):
    """Return outward face-area vectors, ordered by opposite vertex."""
    points = np.asarray(vertices, dtype=float)
    if points.shape != (4, 3):
        raise ValueError("vertices must have shape (4, 3)")
    faces = np.zeros((4, 3), dtype=float)
    for opposite in range(4):
        ids = [i for i in range(4) if i != opposite]
        p0, p1, p2 = points[ids]
        area_vector = 0.5 * np.cross(p1 - p0, p2 - p0)
        face_center = (p0 + p1 + p2) / 3.0
        if np.dot(area_vector, face_center - points[opposite]) < 0.0:
            area_vector = -area_vector
        faces[opposite] = area_vector
    return faces


def closed_face_vectors_from_shape(area_fractions, diagonal, phi):
    """Construct closed tetrahedral face vectors at fixed area fractions.

    The diagonal is |F0+F1| in unit-total-area variables. It and the bend
    angle phi give two shape coordinates after quotienting common rotations.
    """
    areas = np.asarray(area_fractions, dtype=float)
    if areas.shape != (4,) or np.any(areas <= 0.0):
        raise ValueError("area_fractions must contain four positive values")
    if not np.isclose(areas.sum(), 1.0, atol=1e-12, rtol=0.0):
        raise ValueError("area_fractions must sum to one")
    lower = max(abs(areas[0] - areas[1]), abs(areas[2] - areas[3]))
    upper = min(areas[0] + areas[1], areas[2] + areas[3])
    if not lower < diagonal < upper:
        raise ValueError(f"diagonal must lie strictly between {lower} and {upper}")

    d = float(diagonal)
    z0 = (d * d + areas[0] ** 2 - areas[1] ** 2) / (2.0 * d)
    z1 = d - z0
    z2 = (areas[3] ** 2 - areas[2] ** 2 - d * d) / (2.0 * d)
    z3 = -d - z2
    r0_squared = areas[0] ** 2 - z0 * z0
    r2_squared = areas[2] ** 2 - z2 * z2
    if min(r0_squared, r2_squared) <= 0.0:
        raise ValueError("shape lies on a degenerate pair-triangle boundary")
    r0, r2 = math.sqrt(r0_squared), math.sqrt(r2_squared)
    c, s = math.cos(phi), math.sin(phi)
    faces = np.array([
        [r0, 0.0, z0],
        [-r0, 0.0, z1],
        [r2 * c, r2 * s, z2],
        [-r2 * c, -r2 * s, z3],
    ])
    if np.max(np.abs(np.linalg.norm(faces, axis=1) - areas)) > 1e-11:
        raise ArithmeticError("constructed face-vector lengths miss area labels")
    if np.linalg.norm(faces.sum(axis=0)) > 1e-11:
        raise ArithmeticError("constructed face vectors failed closure")
    return faces


def classical_volume_from_faces(face_vectors):
    """Tetrahedron volume from any three faces meeting at a vertex."""
    faces = np.asarray(face_vectors, dtype=float)
    if faces.shape != (4, 3):
        raise ValueError("face_vectors must have shape (4, 3)")
    closure = np.linalg.norm(faces.sum(axis=0))
    if closure > 1e-10:
        raise ValueError(f"face vectors do not close: {closure:.3e}")
    determinant = abs(float(np.linalg.det(faces[[1, 2, 3]])))
    return math.sqrt((2.0 / 9.0) * determinant)


def circumsphere_shape_data(vertices):
    """Return unit-sphere vertices, their complex cross-ratio, and chords."""
    points = np.asarray(vertices, dtype=float)
    edges = points[1:] - points[0]
    center = np.linalg.solve(
        2.0 * edges,
        np.sum(points[1:] ** 2, axis=1) - float(np.dot(points[0], points[0])),
    )
    radius = float(np.linalg.norm(points[0] - center))
    if radius <= 0.0:
        raise ValueError("tetrahedron has a zero circumradius")
    sphere_points = (points - center) / radius

    # Pick a stereographic pole that is not close to any vertex.
    axes = np.vstack((np.eye(3), -np.eye(3)))
    pole = axes[int(np.argmax(np.min(1.0 + sphere_points @ axes.T, axis=0)))]
    seed = np.eye(3)[int(np.argmin(np.abs(pole)))]
    e1 = np.cross(pole, seed)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(pole, e1)
    denominator = 1.0 + sphere_points @ pole
    if np.min(denominator) <= 1e-12:
        raise ArithmeticError("stereographic projection hit its pole")
    z = (sphere_points @ e1 + 1j * (sphere_points @ e2)) / denominator
    cross_ratio = ((z[0] - z[2]) * (z[1] - z[3])) / (
        (z[0] - z[3]) * (z[1] - z[2])
    )
    chords = {
        f"{i}{j}": float(np.linalg.norm(sphere_points[i] - sphere_points[j]))
        for i, j in itertools.combinations(range(4), 2)
    }
    return {
        "circumcenter": center.tolist(),
        "circumradius": radius,
        "unitSphereVertices": sphere_points.tolist(),
        "tetrahedronVolumeAtUnitCircumradius": abs(float(np.linalg.det(
            sphere_points[1:] - sphere_points[0]
        ))) / 6.0,
        "unitSphereRadiusResidual": float(np.max(np.abs(
            np.linalg.norm(sphere_points, axis=1) - 1.0
        ))),
        "vertexCrossRatioReal": float(cross_ratio.real),
        "vertexCrossRatioImag": float(cross_ratio.imag),
        "unitSphereChordDistances": chords,
    }


def expected_face_spins(state):
    """Return <j_i> using the occupation probabilities in the FL state."""
    means = np.zeros(N, dtype=float)
    norm2 = 0.0
    for occupation, amplitude in state.items():
        probability = float(abs(amplitude) ** 2)
        norm2 += probability
        for edge in range(N):
            means[edge] += probability * 0.5 * (
                occupation[2 * edge] + occupation[2 * edge + 1]
            )
    return means / norm2


def flux_correlation_geometry(state, space, normals):
    """Summarize covariance closure and its match to input shape labels."""
    gram = np.zeros((N, N), dtype=float)
    for i in range(N):
        def casimir(occupation, edge=i):
            spin = (occupation[2 * edge] + occupation[2 * edge + 1]) / 2.0
            return [(occupation, spin * (spin + 1.0))]

        gram[i, i] = expectation(state, casimir, space).real
        for j in range(i + 1, N):
            value = expectation(
                state, _dot_ops(su2_ops(i), su2_ops(j)), space
            ).real
            gram[i, j] = gram[j, i] = value
    rms = np.sqrt(np.maximum(np.diag(gram), 0.0))
    normalized = gram / np.outer(rms, rms)
    input_gram = np.asarray(normals) @ np.asarray(normals).T
    return {
        "closureResidual": float(np.linalg.norm(gram @ np.ones(N))),
        "minimumEigenvalue": float(np.min(np.linalg.eigvalsh(gram))),
        "rmsFaceAreaFractions": (rms / rms.sum()).tolist(),
        "maxNormalizedCorrelationError": float(
            np.max(np.abs(normalized - input_gram))
        ),
        "fluxGram": gram.tolist(),
    }


def positive_sqrt_abs(matrix):
    """Hermitian sqrt(abs(M)), using the repository's zero-mode cutoff."""
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.conj().T))
    scale = max(1.0, float(np.max(np.abs(values))))
    values[np.abs(values) <= ZERO_FACTOR * scale] = 0.0
    return (vectors * np.sqrt(np.abs(values))[None, :]) @ vectors.conj().T


def volume_moments(state, space):
    """Return means and variances of the RS and fixed-sign AL operators."""
    norm2 = float(np.vdot(space.vec(state), space.vec(state)).real)
    moments = {"rs": [0.0, 0.0], "al": [0.0, 0.0]}
    for basis, vector in _active_vertex_blocks(space, state):
        q_matrices = {
            triple: _triple_matrix_block(space, basis, triple)
            for triple in TRIPLES
        }
        rs_matrix = sum((positive_sqrt_abs(q) for q in q_matrices.values()),
                        np.zeros_like(next(iter(q_matrices.values()))))
        al_q = sum((AL_SIGNS[t] * q_matrices[t] for t in TRIPLES),
                   np.zeros_like(rs_matrix))
        al_matrix = positive_sqrt_abs(al_q)
        for key, operator in (("rs", rs_matrix), ("al", al_matrix)):
            applied = operator @ vector
            moments[key][0] += float(np.vdot(vector, applied).real)
            moments[key][1] += float(np.vdot(applied, applied).real)

    scale = GAMMA**1.5
    output = {}
    for key, (first, second) in moments.items():
        mean = first / norm2
        variance = max(0.0, second / norm2 - mean * mean)
        output[key] = {
            "meanProjectUnits": scale * mean,
            "varianceProjectUnitsSquared": scale**2 * variance,
        }
    return output


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

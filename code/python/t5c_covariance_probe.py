#!/usr/bin/env python3
"""Probe T5c: reconstruct a tetrahedron from FL-state flux correlations.

This is a pilot, not a complete classical-limit analysis.  For a gauge
invariant FL fixed-area state, one-point fluxes vanish.  The symmetric Gram
matrix G_ij = <J_i . J_j> instead obeys closure and can define four closed
face-area vectors.  We reconstruct that covariance geometry, then compare
its volume (in the same gamma^(3/2) project units) with the signed-mean proxy
and the specified positive RS/AL expectations.

The probe uses the equal-area tetrahedron family already defined for the
volume shape scan, J=1..3, and fixed AL orientation signs (1,-1,1,-1).
Changing the AL embedding, extending the J range, and interpreting the
covariance geometry as a full twisted-geometry reconstruction remain open.
"""

import itertools
import json
import math
from pathlib import Path

import numpy as np

from coherent_states import GAMMA, expectation, su2_ops
from fl_volume_shape_scan import closed_equal_area_normals
from fl_volume_validation import fixed_area_state, spinors_from_normals
from positivity import (
    _dot_ops,
    ashtekar_lewandowski_volume,
    rovelli_smolin_volume,
    spin_vectors,
    volume_operator,
)
from project_paths import RESULTS_ROOT


N = 4
TRIPLES = tuple(itertools.combinations(range(N), 3))
AL_SIGNS = (1, -1, 1, -1)
SHAPES = {
    "regular": (1.0 / math.sqrt(3.0), math.pi / 2.0),
    "bent": (0.5, math.pi / 3.0),
}


def flux_gram(state, space):
    """Return G_ij=<J_i.J_j>, including local Casimirs on the diagonal."""
    gram = np.zeros((N, N), dtype=float)
    for i in range(N):
        def casimir(occupation, edge=i):
            spin = (occupation[2 * edge] + occupation[2 * edge + 1]) / 2.0
            return [(occupation, spin * (spin + 1.0))]

        gram[i, i] = expectation(state, casimir, space).real
        for j in range(i + 1, N):
            value = expectation(state, _dot_ops(su2_ops(i), su2_ops(j)), space).real
            gram[i, j] = gram[j, i] = value
    return gram


def tetrahedron_from_face_vectors(face_vectors):
    """Recover vertices and volume from four closed tetrahedral area vectors."""
    faces = np.asarray(face_vectors, dtype=float)
    if faces.shape != (4, 3):
        raise ValueError("expected four three-dimensional face vectors")
    if np.linalg.norm(faces.sum(axis=0)) > 1e-8:
        raise ValueError("face-area vectors do not close")

    # The chosen three faces meet at one vertex.  An O(3) reflection preserves
    # the Gram matrix and fixes the sign convention used by the dual formula.
    triple = faces[[1, 2, 3]].copy()
    determinant = float(np.linalg.det(triple))
    if determinant > 0.0:
        faces[:, 2] *= -1.0
        triple[:, 2] *= -1.0
        determinant = -determinant
    if determinant >= -1e-12:
        raise ValueError("covariance geometry is degenerate")

    dual_scale = math.sqrt(-8.0 * determinant)
    edges = np.array(
        [
            4.0 * np.cross(triple[1], triple[2]) / dual_scale,
            4.0 * np.cross(triple[2], triple[0]) / dual_scale,
            4.0 * np.cross(triple[0], triple[1]) / dual_scale,
        ]
    )
    vertices = np.vstack((np.zeros(3), edges))
    volume = abs(float(np.linalg.det(edges))) / 6.0

    # Check that the reconstructed tetrahedron has the requested outward
    # area vectors, with face i opposite vertex i.
    reconstructed = np.zeros((4, 3))
    for opposite in range(4):
        ids = [index for index in range(4) if index != opposite]
        p0, p1, p2 = vertices[ids]
        area_vector = 0.5 * np.cross(p1 - p0, p2 - p0)
        face_center = (p0 + p1 + p2) / 3.0
        if np.dot(area_vector, face_center - vertices[opposite]) < 0.0:
            area_vector = -area_vector
        reconstructed[opposite] = area_vector
    return vertices, volume, reconstructed


def reconstruct_from_gram(gram):
    """Factor a rank-three closed Gram matrix and reconstruct its tetrahedron."""
    values, vectors = np.linalg.eigh(0.5 * (gram + gram.T))
    scale = max(1.0, float(np.max(np.abs(values))))
    tol = 128.0 * np.finfo(float).eps * scale
    if values[0] < -tol or abs(values[0]) > 1e-8 * scale:
        raise ValueError(f"Gram matrix is not closed/positive semidefinite: {values}")
    if values[1] <= tol:
        raise ValueError("Gram matrix has fewer than three nondegenerate directions")

    face_vectors = vectors[:, 1:] * np.sqrt(values[1:])[None, :]
    vertices, volume_j_units, reconstructed = tetrahedron_from_face_vectors(face_vectors)
    gram_error = float(np.max(np.abs(reconstructed @ reconstructed.T - gram)))
    return {
        "gramEigenvalues": values.tolist(),
        "rmsFaceAreasJUnits": np.sqrt(np.maximum(np.diag(gram), 0.0)).tolist(),
        "verticesJUnits": vertices.tolist(),
        "volumeJUnits": volume_j_units,
        "volumeProjectUnits": volume_j_units * GAMMA**1.5,
        "reconstructedFaceGramMaxAbsError": gram_error,
    }


def evaluate_shape(name, J):
    x, phi = SHAPES[name]
    normals = closed_equal_area_normals(x, phi)
    spinors = spinors_from_normals(normals)
    space, state = fixed_area_state(J, spinors=spinors)

    gram = flux_gram(state, space)
    diag = np.sqrt(np.maximum(np.diag(gram), 0.0))
    normalized_gram = gram / np.outer(diag, diag)
    label_gram = normals @ normals.T
    max_shape_error = float(np.max(np.abs(normalized_gram - label_gram)))
    geometry = reconstruct_from_gram(gram)

    _, q_mean = volume_operator(state, space)
    signed_proxy = GAMMA**1.5 * math.sqrt(abs(q_mean.real))
    rs_volume = rovelli_smolin_volume(state, space)
    al_volume = ashtekar_lewandowski_volume(
        state, space, dict(zip(TRIPLES, AL_SIGNS))
    )
    mean_fluxes = spin_vectors(state, space)

    return {
        "shape": name,
        "x": x,
        "phiRadians": phi,
        "J": J,
        "K": 2 * J,
        "stateSupportSize": len(state),
        "maxOnePointFluxNorm": float(np.max(np.linalg.norm(mean_fluxes, axis=1))),
        "fluxGram": gram.tolist(),
        "fluxGramClosureMaxAbs": float(np.max(np.abs(gram.sum(axis=1)))),
        "normalizedGramMaxAbsDifferenceFromInputNormals": max_shape_error,
        "covarianceGeometry": geometry,
        "signedTripleMeanQ012": q_mean.real,
        "signedMeanProxyProjectUnits": signed_proxy,
        "positiveRSProjectUnits": rs_volume,
        "positiveALProjectUnits": al_volume,
    }


def main():
    records = [
        evaluate_shape(shape, J)
        for shape in SHAPES
        for J in (1, 2, 3)
    ]
    output = {
        "title": "T5c pilot: FL-state flux-covariance tetrahedron reconstruction",
        "status": "exploratory; not a large-J or full twisted-geometry result",
        "units": "J-unit geometric volumes multiplied by gamma^(3/2), hbar=1",
        "definitions": {
            "fluxGram": "G_ij = <sum_a J_i^a J_j^a>; diagonal entries use <j_i(j_i+1)>",
            "covarianceGeometry": "tetrahedron whose four oriented area-vector Gram matrix is G",
            "signedMeanProxy": "gamma^(3/2) sqrt(abs(<q_012>))",
            "positiveVolumes": "project-normalized RS and AL expectations; AL signs held at (1,-1,1,-1)",
            "shapeError": "max absolute difference between normalized G and the input face-normal Gram matrix",
        },
        "records": records,
    }
    path = RESULTS_ROOT / "t5c_covariance_probe_results.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({
        "output": str(path),
        "records": [
            {
                "shape": r["shape"], "J": r["J"],
                "closure": r["fluxGramClosureMaxAbs"],
                "shapeError": r["normalizedGramMaxAbsDifferenceFromInputNormals"],
                "Vclassical": r["covarianceGeometry"]["volumeProjectUnits"],
                "Vproxy": r["signedMeanProxyProjectUnits"],
                "VRS": r["positiveRSProjectUnits"], "VAL": r["positiveALProjectUnits"],
            } for r in records
        ],
    }, indent=2))


if __name__ == "__main__":
    main()

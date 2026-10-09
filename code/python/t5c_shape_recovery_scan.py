#!/usr/bin/env python3
"""Shape and boundary-approach covariance recovery follow-up for T5c.

For the N=4 Freidel-Livine fixed-area family, compute
G_ij = <J_i . J_j> on selected nondegenerate equal-area tetrahedron shapes
for J=1..6, including finite approaches to three degenerate boundaries.
Compare the normalized covariance Gram matrix with the input normal Gram
matrix, and retain closure, spectrum, and reconstructed-Gram diagnostics.
Positive RS/AL expectations are recomputed for five interior shapes at
J=1..3.
"""

import itertools
import json
import math
from pathlib import Path

import numpy as np

from lqg_scattering.coherent_states import GAMMA
from lqg_scattering.intertwiners import fixed_area_state
from lqg_scattering.observables import flux_gram
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.tetrahedra import closed_equal_area_normals, reconstruct_from_gram
from lqg_scattering.positivity import (
    ashtekar_lewandowski_volume,
    rovelli_smolin_volume,
    spin_vectors,
    volume_operator,
)
from project_paths import RESULTS_ROOT


SHAPES = {
    "regular": (1.0 / math.sqrt(3.0), math.pi / 2.0),
    "bent_60": (0.5, math.pi / 3.0),
    "bent_120": (0.5, 2.0 * math.pi / 3.0),
    "x065_bent_60": (0.65, math.pi / 3.0),
    "low_x020": (0.2, math.pi / 2.0),
    "x_030_phi90": (0.3, math.pi / 2.0),
    "x_015_phi90": (0.15, math.pi / 2.0),
    "x_0075_phi90": (0.075, math.pi / 2.0),
    "x_070_phi90": (0.7, math.pi / 2.0),
    "x_085_phi90": (0.85, math.pi / 2.0),
    "x_0925_phi90": (0.925, math.pi / 2.0),
    "phi_0p5": (1.0 / math.sqrt(3.0), 0.5),
    "phi_0p25": (1.0 / math.sqrt(3.0), 0.25),
    "phi_0p125": (1.0 / math.sqrt(3.0), 0.125),
}
J_VALUES = (1, 2, 3, 4, 5, 6)
VOLUME_J_VALUES = (1, 2, 3)
VOLUME_SHAPES = {
    "regular",
    "bent_60",
    "bent_120",
    "x065_bent_60",
    "low_x020",
}
TRIPLES = tuple(itertools.combinations(range(4), 3))
AL_SIGNS = (1, -1, 1, -1)


def evaluate_shape(shape_name, J):
    x, phi = SHAPES[shape_name]
    normals = closed_equal_area_normals(x, phi)
    spinors = spinors_from_normals(normals)
    space, state = fixed_area_state(J, spinors=spinors)

    gram = flux_gram(state, space)
    rms_lengths = np.sqrt(np.maximum(np.diag(gram), 0.0))
    normalized_gram = gram / np.outer(rms_lengths, rms_lengths)
    input_normal_gram = normals @ normals.T
    eig = np.linalg.eigvalsh(0.5 * (gram + gram.T))
    geometry = reconstruct_from_gram(gram)

    record = {
        "shape": shape_name,
        "x": x,
        "phiRadians": phi,
        "J": J,
        "K_Fock": 2 * J,
        "ambientFockDimension": space.dim,
        "stateSupportSize": len(state),
        "stateNormSquared": float(sum(abs(a) ** 2 for a in state.values())),
        "fluxGram": gram.tolist(),
        "inputNormalGram": input_normal_gram.tolist(),
        "normalizedFluxGram": normalized_gram.tolist(),
        "fluxGramEigenvalues": eig.tolist(),
        "closureMaxAbs": float(np.max(np.abs(gram.sum(axis=1)))),
        "normalizedShapeMaxAbsError": float(
            np.max(np.abs(normalized_gram - input_normal_gram))
        ),
        "reconstructedFaceGramMaxAbsError": geometry[
            "reconstructedFaceGramMaxAbsError"
        ],
        "rmsFaceAreasJUnits": geometry["rmsFaceAreasJUnits"],
        "covarianceVolumeProjectUnits": geometry["volumeProjectUnits"],
    }
    if J in VOLUME_J_VALUES and shape_name in VOLUME_SHAPES:
        _, q_mean = volume_operator(state, space)
        record["maxOnePointFluxNorm"] = float(
            np.max(np.linalg.norm(spin_vectors(state, space), axis=1))
        )
        record["volumeObservablesProjectUnits"] = {
            "signedTripleMeanQ012": float(q_mean.real),
            "signedMeanProxy": float(GAMMA**1.5 * math.sqrt(abs(q_mean.real))),
            "positiveRS": float(rovelli_smolin_volume(state, space)),
            "positiveAL": float(
                ashtekar_lewandowski_volume(
                    state, space, dict(zip(TRIPLES, AL_SIGNS))
                )
            ),
            "ALOrientationSigns": list(AL_SIGNS),
        }
    return record


def main():
    records = [
        evaluate_shape(name, J)
        for name in SHAPES
        for J in J_VALUES
    ]
    for name in SHAPES:
        subset = sorted(
            (r for r in records if r["shape"] == name), key=lambda r: r["J"]
        )
        input_gram = np.asarray(subset[0]["inputNormalGram"])
        first_correction = np.asarray(subset[0]["normalizedFluxGram"]) - input_gram
        for row in subset:
            scaled_correction = (
                np.asarray(row["normalizedFluxGram"]) - input_gram
            ) * (row["J"] + 5) / 6.0
            row["normalizedGramAffineIn1overJMaxAbsResidual"] = float(
                np.max(np.abs(scaled_correction - first_correction))
            )
    output = {
        "title": "T5c shape and boundary-approach covariance recovery scan",
        "status": "exploratory shape-recovery calculation",
        "stateFamily": "N=4 Freidel-Livine fixed-area state",
        "shapeFamily": "closed equal-face-area normals parameterized by x and phi",
        "JValues": list(J_VALUES),
        "volumeObservableShapes": sorted(VOLUME_SHAPES),
        "volumeObservableJValues": list(VOLUME_J_VALUES),
        "boundaryApproaches": [
            {
                "parameter": "x",
                "fixedPhiRadians": math.pi / 2,
                "values": [0.3, 0.15, 0.075],
                "limit": "x -> 0",
            },
            {
                "parameter": "x",
                "fixedPhiRadians": math.pi / 2,
                "values": [0.7, 0.85, 0.925],
                "limit": "x -> 1",
            },
            {
                "parameter": "phi",
                "fixedX": 1.0 / math.sqrt(3.0),
                "valuesRadians": [0.5, 0.25, 0.125],
                "limit": "phi -> 0",
            },
        ],
        "shapes": {
            name: {"x": x, "phiRadians": phi}
            for name, (x, phi) in SHAPES.items()
        },
        "method": {
            "fluxGram": "G_ij = <J_i . J_j>, with <j_i(j_i+1)> on the diagonal",
            "shapeError": "max abs difference between normalized G and input normal Gram",
            "matrixInterpolation": "compare (H_J-H_input)*(J+5)/6 with H_1-H_input",
            "scope": "shape recovery for J=1..6; volume observables for five interior shapes at J=1..3",
        },
        "limitations": [
            "boundary approaches use finite nondegenerate samples, not exact degenerate endpoints",
            "finite J range does not establish a classical limit",
            "existing positive RS/AL comparisons remain the J=1,2,3 pilot",
            "the covariance factorization is a candidate geometry map, not a proven general map",
        ],
        "records": records,
    }
    output_path = RESULTS_ROOT / "t5c_shape_recovery_results.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    for name in SHAPES:
        subset = [r for r in records if r["shape"] == name]
        errors = [r["normalizedShapeMaxAbsError"] for r in subset]
        print(
            f"{name}: shape error J=1 {errors[0]:.6g}; "
            f"J={J_VALUES[-1]} {errors[-1]:.6g}; "
            f"max closure {max(r['closureMaxAbs'] for r in subset):.2e}"
        )
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()

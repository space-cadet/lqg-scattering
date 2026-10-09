"""Positive RS/AL volume checks on real-plane U(N) coherent states (T1b)."""

import itertools
import json

import numpy as np

from lqg_scattering.coherent_states import FockSpace, perelomov_state, plane_to_Z
from lqg_scattering.fl_volume import ORIENTATIONS, direct_tensor_volumes
from lqg_scattering.grassmannian import plane_to_plucker
from lqg_scattering.positivity import (
    GAMMA,
    ashtekar_lewandowski_volume,
    is_positive_plane,
    rovelli_smolin_volume,
    volume_operator,
)


REFERENCE_OCCUPATIONS = np.array(
    [[1, 1], [1, 1], [1, 0], [1, 0]], dtype=int
)
PLANES = {
    "positive_real_plane": np.array(
        [[1.0, 0.0, -1.0, -2.0], [0.0, 1.0, 1.0, 1.0]]
    ),
    "off_cell_real_plane": np.array(
        [[1.0, 0.0, -2.0, -1.0], [0.0, 1.0, 1.0, 1.0]]
    ),
}


def evaluate(name, plane):
    k_max = int(REFERENCE_OCCUPATIONS.sum())
    space = FockSpace(4, k_max)
    state, space = perelomov_state(
        plane_to_Z(plane),
        k_max=k_max,
        ref_occupations=REFERENCE_OCCUPATIONS,
        space=space,
    )
    proxy, q_mean = volume_operator(state, space, triple=(0, 1, 2))
    triples = tuple(itertools.combinations(range(4), 3))
    orientation_map = dict(zip(triples, ORIENTATIONS))
    rs = rovelli_smolin_volume(state, space)
    al = ashtekar_lewandowski_volume(state, space, orientation_map)
    direct_rs, direct_al, max_q_difference = direct_tensor_volumes(space, state)
    vector = space.vec(state)
    pairs, minors = plane_to_plucker(plane)

    return {
        "name": name,
        "plane": plane.tolist(),
        "strictlyPositiveCell": bool(is_positive_plane(plane)),
        "pluckerMinors": {
            f"M{i + 1}{j + 1}": [float(value.real), float(value.imag)]
            for (i, j), value in zip(pairs, minors)
        },
        "referenceOccupations": REFERENCE_OCCUPATIONS.tolist(),
        "totalBosonsK": k_max,
        "stateDimension": space.dim,
        "stateNormSquared": float(np.vdot(vector, vector).real),
        "maximumImaginaryAmplitude": float(np.max(np.abs(vector.imag))),
        "q012": [float(q_mean.real), float(q_mean.imag)],
        "signedMeanProxyProjectUnits": float(proxy),
        "positiveRSProjectUnits": float(rs),
        "positiveALProjectUnits": float(al),
        "directTensorRSProjectUnits": float(direct_rs),
        "directTensorALProjectUnits": float(direct_al),
        "maxTripleMatrixDifference": float(max_q_difference),
        "rsExpectationDifference": float(abs(rs - direct_rs)),
        "alExpectationDifference": float(abs(al - direct_al)),
        "gamma": GAMMA,
        "hbar": 1.0,
        "alOrientationSignsLexicographic": list(ORIENTATIONS),
    }


def main():
    print(json.dumps([evaluate(name, plane) for name, plane in PLANES.items()], indent=2))


if __name__ == "__main__":
    main()

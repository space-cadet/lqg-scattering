"""Fixed-area FL positive-volume evaluation and independent tensor checks."""

import itertools

import numpy as np

from .positivity import (
    active_vertex_blocks,
    positive_sqrt_expectation,
    triple_matrix_block,
    ashtekar_lewandowski_volume,
    rovelli_smolin_volume,
    volume_operator,
)
from .conventions import GAMMA, TETRAHEDRON_ORIENTATIONS
from .intertwiners import fixed_area_state
from .tetrahedra import TETRAHEDRON_NORMALS

N = 4
TRIPLES = tuple(itertools.combinations(range(N), 3))
ORIENTATIONS = TETRAHEDRON_ORIENTATIONS
NORMALS = TETRAHEDRON_NORMALS


def direct_tensor_q(basis, triple):
    """Build q_ijk from local spin-j matrices and their tensor products."""
    spins = [
        int(basis[0][2 * edge] + basis[0][2 * edge + 1])
        for edge in range(N)
    ]
    local = []
    for twice_j in spins:
        j, dimension = twice_j / 2, twice_j + 1
        raising = np.zeros((dimension, dimension), dtype=complex)
        for n_a in range(dimension - 1):
            raising[n_a + 1, n_a] = np.sqrt((twice_j - n_a) * (n_a + 1))
        lowering = raising.conj().T
        local.append(
            (
                (raising + lowering) / 2,
                (raising - lowering) / (2j),
                np.diag([n_a - j for n_a in range(dimension)]),
            )
        )

    embedded = {}
    for axis in range(3):
        for edge in range(N):
            factors = [np.eye(twice_j + 1) for twice_j in spins]
            factors[edge] = local[edge][axis]
            matrix = factors[0]
            for factor in factors[1:]:
                matrix = np.kron(matrix, factor)
            embedded[edge, axis] = matrix

    tensor_basis = list(itertools.product(*[range(s + 1) for s in spins]))
    tensor_index = {occupation: index for index, occupation in enumerate(tensor_basis)}
    selected = [tensor_index[tuple(occupation[::2])] for occupation in basis]

    epsilon = np.zeros((3, 3, 3))
    epsilon[0, 1, 2] = epsilon[1, 2, 0] = epsilon[2, 0, 1] = 1
    epsilon[0, 2, 1] = epsilon[2, 1, 0] = epsilon[1, 0, 2] = -1
    matrix = np.zeros((len(selected), len(selected)), dtype=complex)
    i, j, k = triple
    for a, b, c in itertools.product(range(3), repeat=3):
        if epsilon[a, b, c]:
            product = embedded[i, a] @ embedded[j, b] @ embedded[k, c]
            matrix += epsilon[a, b, c] * product[np.ix_(selected, selected)]
    return matrix

def direct_tensor_volumes(space, state):
    """Evaluate RS/AL roots using direct products of local spin-j matrices."""
    vector = space.vec(state)
    rs_total = al_total = 0.0
    max_matrix_difference = 0.0

    for basis, local_state in active_vertex_blocks(space, state):
        q_matrices = []
        for triple in TRIPLES:
            q_direct = direct_tensor_q(basis, triple)
            q_project = triple_matrix_block(space, basis, triple)
            max_matrix_difference = max(
                max_matrix_difference,
                float(np.max(np.abs(q_direct - q_project))),
            )
            q_matrices.append(q_direct)

            rs_total += positive_sqrt_expectation(q_direct, local_state)

        q_al = sum(sign * q for sign, q in zip(ORIENTATIONS, q_matrices))
        al_total += positive_sqrt_expectation(q_al, local_state)

    scale = GAMMA**1.5
    return scale * rs_total, scale * al_total, max_matrix_difference

def evaluate_area(area_label, direct_check=False, spinors=None):
    space, state = fixed_area_state(area_label, spinors=spinors)
    orientation_map = dict(zip(TRIPLES, ORIENTATIONS))
    project_rs = rovelli_smolin_volume(state, space)
    project_al = ashtekar_lewandowski_volume(state, space, orientation_map)
    result = {
        "areaLabelJ": area_label,
        "flAreaOverLp2": area_label,
        "rsPositiveVolumeProjectUnits": project_rs,
        "alPositiveVolumeProjectUnits": project_al,
    }

    if direct_check:
        direct_rs, direct_al, matrix_difference = direct_tensor_volumes(space, state)
        result.update(
            {
                "directTensorRS": direct_rs,
                "directTensorAL": direct_al,
                "maxTripleMatrixDifference": matrix_difference,
                "rsDifference": abs(project_rs - direct_rs),
                "alDifference": abs(project_al - direct_al),
            }
        )

    return result

__all__ = [
    "N", "GAMMA", "TRIPLES", "ORIENTATIONS", "NORMALS",
    "direct_tensor_q", "direct_tensor_volumes", "evaluate_area",
]

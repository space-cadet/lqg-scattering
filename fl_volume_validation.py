#!/usr/bin/env python3
"""FL Eq. (38) regular-tetrahedron positive-volume checks and area sweep."""

import itertools
import json
import numpy as np

from coherent_states import FockSpace, _edge_ops
from positivity import (
    _active_vertex_blocks,
    _triple_matrix_block,
    ashtekar_lewandowski_volume,
    rovelli_smolin_volume,
    volume_operator,
)

N = 4
GAMMA = 0.2375
TRIPLES = tuple(itertools.combinations(range(N), 3))
ORIENTATIONS = (1, -1, 1, -1)
NORMALS = np.array(
    [[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]],
    dtype=float,
) / np.sqrt(3)


def spinors_from_normals(normals):
    """Return normalized SU(2) spinors whose Bloch vectors are ``normals``."""
    normals = np.asarray(normals, dtype=float)
    if normals.shape != (N, 3):
        raise ValueError(f"normals must have shape ({N}, 3), got {normals.shape}")
    lengths = np.linalg.norm(normals, axis=1)
    if np.any(lengths == 0.0):
        raise ValueError("face normals must be nonzero")
    normals = normals / lengths[:, None]
    spinors = []
    for x, y, z in normals:
        theta, phi = np.arccos(z), np.arctan2(y, x)
        spinors.append(
            [np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)]
        )
    return np.asarray(spinors)


def regular_tetrahedron_spinors():
    return spinors_from_normals(NORMALS)


def fixed_area_state(area_label, spinors=None):
    """Build normalized (F_z^dagger)^J|0> for J=area_label."""
    spinors = (
        regular_tetrahedron_spinors()
        if spinors is None
        else np.asarray(spinors, dtype=complex)
    )
    if spinors.shape != (N, 2):
        raise ValueError(f"spinors must have shape ({N}, 2), got {spinors.shape}")

    def bracket(left, right):
        return left[0] * right[1] - left[1] * right[0]

    # Eq. (40): F_z^dagger = sum_(i<j) [z_j|z_i> F_ij^dagger.
    coefficients = {
        (i, j): bracket(spinors[j], spinors[i])
        for i, j in itertools.combinations(range(N), 2)
    }
    space = FockSpace(N, 2 * area_label)

    def apply_pair(state, i, j):
        out = {}
        create_ai = _edge_ops("adag", i, N)
        create_bj = _edge_ops("bdag", j, N)
        create_aj = _edge_ops("adag", j, N)
        create_bi = _edge_ops("bdag", i, N)
        for occupation, amplitude in state.items():
            for intermediate, factor_1 in create_bj(occupation):
                for result, factor_2 in create_ai(intermediate):
                    out[result] = out.get(result, 0j) + amplitude * factor_1 * factor_2
            for intermediate, factor_1 in create_bi(occupation):
                for result, factor_2 in create_aj(intermediate):
                    out[result] = out.get(result, 0j) - amplitude * factor_1 * factor_2
        return out

    state = {(0,) * (2 * N): 1.0 + 0.0j}
    for _ in range(area_label):
        updated = {}
        for (i, j), coefficient in coefficients.items():
            for occupation, amplitude in apply_pair(state, i, j).items():
                updated[occupation] = (
                    updated.get(occupation, 0j) + coefficient * amplitude
                )
        state = updated

    norm = np.linalg.norm(space.vec(state))
    return space, {
        occupation: amplitude / norm for occupation, amplitude in state.items()
    }


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

    for basis, local_state in _active_vertex_blocks(space, state):
        q_matrices = []
        for triple in TRIPLES:
            q_direct = direct_tensor_q(basis, triple)
            q_project = _triple_matrix_block(space, basis, triple)
            max_matrix_difference = max(
                max_matrix_difference,
                float(np.max(np.abs(q_direct - q_project))),
            )
            q_matrices.append(q_direct)

            eigenvalues, eigenvectors = np.linalg.eigh(q_direct)
            weights = np.abs(eigenvectors.conj().T @ local_state) ** 2
            rs_total += float(np.dot(weights, np.sqrt(np.abs(eigenvalues))))

        q_al = sum(sign * q for sign, q in zip(ORIENTATIONS, q_matrices))
        eigenvalues, eigenvectors = np.linalg.eigh(q_al)
        weights = np.abs(eigenvectors.conj().T @ local_state) ** 2
        al_total += float(np.dot(weights, np.sqrt(np.abs(eigenvalues))))

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


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="calculate area labels J=1 through J=5 and print JSON",
    )
    args = parser.parse_args()

    if args.sweep:
        results = [evaluate_area(j, direct_check=True) for j in range(1, 6)]
        print(json.dumps(results, indent=2))
        return

    result = evaluate_area(2, direct_check=True)
    q_mean = volume_operator(fixed_area_state(2)[1], fixed_area_state(2)[0],
                             triple=(0, 1, 2))[1]
    print(f"closure residual: {np.linalg.norm(NORMALS.sum(axis=0)):.3e}")
    print(f"<q_012>: {q_mean.real:.15g}{q_mean.imag:+.3g}i")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

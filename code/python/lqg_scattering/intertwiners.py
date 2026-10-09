"""Fixed-area Freidel-Livine intertwiner state construction."""

import itertools

import numpy as np

from .coherent_states import FockSpace, schwinger_edge_operator as _edge_ops
from .spinors import spinors_from_normals
from .tetrahedra import TETRAHEDRON_NORMALS

def regular_tetrahedron_spinors():
    return spinors_from_normals(TETRAHEDRON_NORMALS)

def fixed_area_state(area_label, spinors=None):
    """Build normalized (F_z^dagger)^J|0> for J=area_label."""
    spinors = (
        regular_tetrahedron_spinors()
        if spinors is None
        else np.asarray(spinors, dtype=complex)
    )
    if spinors.ndim != 2 or spinors.shape[1] != 2:
        raise ValueError(f"spinors must have shape (n, 2), got {spinors.shape}")
    n_edges = spinors.shape[0]

    def bracket(left, right):
        return left[0] * right[1] - left[1] * right[0]

    # Eq. (40): F_z^dagger = sum_(i<j) [z_j|z_i> F_ij^dagger.
    coefficients = {
        (i, j): bracket(spinors[j], spinors[i])
        for i, j in itertools.combinations(range(n_edges), 2)
    }
    space = FockSpace(n_edges, 2 * area_label)

    def apply_pair(state, i, j):
        out = {}
        create_ai = _edge_ops("adag", i, n_edges)
        create_bj = _edge_ops("bdag", j, n_edges)
        create_aj = _edge_ops("adag", j, n_edges)
        create_bi = _edge_ops("bdag", i, n_edges)
        for occupation, amplitude in state.items():
            for intermediate, factor_1 in create_bj(occupation):
                for result, factor_2 in create_ai(intermediate):
                    out[result] = out.get(result, 0j) + amplitude * factor_1 * factor_2
            for intermediate, factor_1 in create_bi(occupation):
                for result, factor_2 in create_aj(intermediate):
                    out[result] = out.get(result, 0j) - amplitude * factor_1 * factor_2
        return out

    state = {(0,) * (2 * n_edges): 1.0 + 0.0j}
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

__all__ = ["regular_tetrahedron_spinors", "fixed_area_state"]

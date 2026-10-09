"""Variable-face singlet RS blocks and independent local-spin checks.

Face spins are twice-integers. Catalogue sampling and serialization remain
in the variable-face driver; tensor and oscillator checks stay independent.
"""
from functools import lru_cache
import itertools
import math
import numpy as np
from .coherent_states import su2_ops
from .positivity import dot_operator
from .singlets import (ABS_TOL, GAMMA, action_matrix, occupation_basis,
                       independent_local_q, singlet_paths, sequential_basis, root_abs)

def max_abs(array):
    return float(np.max(abs(array))) if np.size(array) else 0.0


def dense_tensor_q(occupations, spins, triple):
    """Direct local tensor matrix elements, independent of oscillator actions."""
    local = []
    for spin in spins:
        raising = np.diag([math.sqrt((a+1)*(spin-a)) for a in range(spin)], -1)
        lowering = raising.T
        local.append(((raising+lowering)/2, (raising-lowering)/(2j),
                      np.diag(np.arange(spin+1)-spin/2)))
    aa = np.asarray(occupations)[:, ::2]
    q = np.zeros((len(aa), len(aa)), complex)
    permutations = ((0, 1, 2, 1), (1, 2, 0, 1), (2, 0, 1, 1),
                    (0, 2, 1, -1), (2, 1, 0, -1), (1, 0, 2, -1))
    for a, b, c, sign in permutations:
        term = np.full(q.shape, complex(sign))
        axes = dict(zip(triple, (a, b, c)))
        for face, spin in enumerate(spins):
            matrix = local[face][axes[face]] if face in axes else np.eye(spin+1)
            term *= matrix[aa[:, face, None], aa[None, :, face]]
        q += term
    return q


@lru_cache(maxsize=None)
def canonical_operators(spins):
    occupations = occupation_basis(spins)
    pairs = tuple(itertools.combinations(range(len(spins)), 2))
    triples = tuple(itertools.combinations(range(len(spins)), 3))
    dots = {p: action_matrix(occupations, dot_operator(su2_ops(p[0]), su2_ops(p[1])))
            for p in pairs}
    paths = singlet_paths(spins)
    _, basis, _ = sequential_basis(spins, paths, occupations)
    checks = {"epsilon_vs_commutator": 0.0, "dense_tensor_vs_commutator": 0.0,
              "magnetic_root_projection": 0.0}
    direct_volume = np.zeros((len(paths), len(paths)), complex)
    for i, j, k in triples:
        q = (1j*(dots[i, j]@dots[j, k]-dots[j, k]@dots[i, j])).toarray()
        epsilon = independent_local_q(occupations, spins, (i, j, k)).toarray()
        tensor = dense_tensor_q(occupations, spins, (i, j, k))
        checks["epsilon_vs_commutator"] = max(checks["epsilon_vs_commutator"], max_abs(q-epsilon))
        checks["dense_tensor_vs_commutator"] = max(checks["dense_tensor_vs_commutator"], max_abs(q-tensor))
        projected = basis.conj().T@tensor@basis
        projected_root = root_abs(projected)[0]
        magnetic_root = basis.conj().T@root_abs(tensor)[0]@basis
        checks["magnetic_root_projection"] = max(checks["magnetic_root_projection"],
                                                 max_abs(projected_root-magnetic_root))
        direct_volume += GAMMA**1.5*magnetic_root
    assert max(checks.values()) < ABS_TOL, checks
    return occupations, dots, direct_volume, basis, checks


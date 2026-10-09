"""Total SU(2) spin and closure diagnostics in fixed-number Fock bases.

Spin is dimensionless (hbar=1). Inputs are normalized dense kets or density
matrices in the supplied occupation ordering; no singlet projection occurs.
Sector decomposition diagonalizes local-occupation/magnetic blocks, with an
explicit dense-block limit. It never forms a full dense spin eigensystem.
"""
import math

import numpy as np
from scipy.linalg import eigvalsh
from scipy.sparse import csr_matrix

from .fixed_k import single_edge_operators
from .singlets import ABS_TOL


def total_spin_operators(occupations, index, n_sites):
    """Build total Jx, Jy, Jz, J+/J-, and J² in a complete fixed-number basis.

    occupations and index normally come from build_fixed_number_model.
    Local occupations and total magnetic number label invariant J² blocks.
    """
    if (isinstance(n_sites, (bool, np.bool_))
            or not isinstance(n_sites, (int, np.integer)) or n_sites < 1):
        raise ValueError("n_sites must be a positive integer")
    occupations = np.asarray(occupations)
    if (occupations.ndim != 2 or occupations.shape[1] != 2 * n_sites
            or len(occupations) == 0 or not np.issubdtype(occupations.dtype, np.integer)
            or np.any(occupations < 0)):
        raise ValueError("occupations must be nonnegative integer rows with two modes per site")
    if np.any(occupations.sum(axis=1) != occupations[0].sum()):
        raise ValueError("occupations must belong to one fixed-number sector")
    if len(index) != len(occupations) or any(
            index.get(tuple(int(x) for x in row)) != i for i, row in enumerate(occupations)):
        raise ValueError("occupation lookup does not match the basis ordering")
    expected = math.comb(int(occupations[0].sum()) + 2*n_sites - 1, 2*n_sites - 1)
    if len(occupations) != expected:
        raise ValueError("a complete fixed-number basis is required, without magnetic or spin projection")
    local = single_edge_operators(occupations, index, n_sites)
    zero = csr_matrix((len(occupations), len(occupations)), dtype=complex)
    z = sum((ops[0] for ops in local), zero)
    plus = sum((ops[1] for ops in local), zero)
    minus = sum((ops[2] for ops in local), zero)
    x, y = (plus + minus) / 2, (plus - minus) / (2j)
    squared = (z @ z + (plus @ minus + minus @ plus) / 2).tocsr()
    blocks = {}
    for row, state in enumerate(occupations):
        counts = tuple(int(v) for v in state[::2] + state[1::2])
        twice_m = int(np.sum(state[::2] - state[1::2]))
        blocks.setdefault((counts, twice_m), []).append(row)
    return {
        "x": x.tocsr(), "y": y.tocsr(), "z": z.tocsr(),
        "plus": plus.tocsr(), "minus": minus.tocsr(), "squared": squared,
        "dimension": len(occupations),
        "n_bosons": int(occupations[0].sum()),
        "blocks": tuple(np.asarray(rows, dtype=int) for rows in blocks.values()),
    }


def _validated_state(state, dimension):
    state = np.asarray(state, dtype=complex)
    if not np.all(np.isfinite(state)):
        raise ValueError("state contains nonfinite values")
    if state.shape == (dimension,):
        norm = float(np.vdot(state, state).real)
    elif state.shape == (dimension, dimension):
        if np.max(abs(state - state.conj().T)) > ABS_TOL:
            raise ValueError("density matrix must be Hermitian")
        norm = float(np.trace(state).real)
        minimum = eigvalsh(state, subset_by_index=(0, 0))[0]
        if minimum < -ABS_TOL:
            raise ValueError("density matrix must be positive semidefinite")
    else:
        raise ValueError("state must be a ket vector or square density matrix matching the basis")
    if abs(norm - 1) > ABS_TOL:
        raise ValueError("state must have unit squared norm or unit trace")
    return state, norm


def _expectation(state, operator):
    value = (np.vdot(state, operator @ state) if state.ndim == 1
             else np.trace(operator @ state))
    if abs(value.imag) > ABS_TOL * max(1., abs(value.real)):
        raise ValueError("Hermitian readout has a nonreal expectation")
    return float(value.real)


def _sector_probabilities(state, operators, max_block_dimension):
    if (isinstance(max_block_dimension, (bool, np.bool_))
            or not isinstance(max_block_dimension, (int, np.integer)) or max_block_dimension < 1):
        raise ValueError("max_block_dimension must be a positive integer")
    probabilities = {twice_j: 0. for twice_j in range(
        operators["n_bosons"] % 2, operators["n_bosons"] + 1, 2)}
    for rows in operators["blocks"]:
        if len(rows) > max_block_dimension:
            raise ValueError(f"spin block dimension {len(rows)} exceeds limit {max_block_dimension}")
        matrix = operators["squared"][rows][:, rows].toarray()
        values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2)
        twice_js = np.rint(np.sqrt(np.maximum(1. + 4*values, 0.)) - 1).astype(int)
        eigenvalues = twice_js * (twice_js + 2) / 4
        if (np.max(abs(values - eigenvalues)) > ABS_TOL * max(1., np.max(abs(values)))
                or any(int(label) not in probabilities for label in twice_js)):
            raise ValueError("J² eigensystem does not match the allowed spin sectors")
        if state.ndim == 1:
            weights = abs(vectors.conj().T @ state[rows])**2
        else:
            block = state[np.ix_(rows, rows)]
            weights = np.real(np.diag(vectors.conj().T @ block @ vectors))
        for label, weight in zip(twice_js, weights):
            probabilities[int(label)] += float(weight)
    if min(probabilities.values()) < -ABS_TOL or abs(sum(probabilities.values()) - 1) > ABS_TOL:
        raise ValueError("spin-sector probabilities are not normalized and nonnegative")
    cleaned = {twice_j: max(0., probability) for twice_j, probability in probabilities.items()}
    total = sum(cleaned.values())
    return {twice_j / 2: probability / total for twice_j, probability in cleaned.items()}


def spin_sector_probabilities(state, operators, *, max_block_dimension=512):
    """Return P(J), including zero-weight allowed sectors, without postselection.

    Each local-occupation/magnetic block is diagonalized separately. The
    dense-block limit is explicit; the routine raises rather than truncates.
    """
    state, _ = _validated_state(state, operators["dimension"])
    return _sector_probabilities(state, operators, max_block_dimension)


def closure_diagnostics(state, operators, *, max_block_dimension=512):
    """Return mean total spin, mean J², singlet weight, and P(J).

    Zero mean spin alone is not closure. An exact singlet has mean J²=0 and
    singlet weight=1. Density matrices are checked for trace and positivity;
    eigenvalue validation of a dense density matrix can be costly.
    """
    state, norm = _validated_state(state, operators["dimension"])
    probabilities = _sector_probabilities(state, operators, max_block_dimension)
    squared = _expectation(state, operators["squared"])
    return {
        "norm_or_trace": norm,
        "mean_total_spin_vector": {axis: _expectation(state, operators[axis]) for axis in ("x", "y", "z")},
        "mean_total_spin_squared": squared,
        "rms_closure_defect": math.sqrt(max(0., squared)) if squared > (
            64 * np.finfo(float).eps * max(
                1., (operators["n_bosons"] / 2) * (operators["n_bosons"] / 2 + 1))) else 0.,
        "singlet_weight": probabilities.get(0., 0.),
        "total_spin_probabilities": probabilities,
    }

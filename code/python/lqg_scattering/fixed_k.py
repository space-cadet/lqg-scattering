"""Fixed-total-boson Schwinger bases and sparse operator builders."""

import itertools

import numpy as np
import scipy.sparse as sp


def fixed_number_basis(n, k):
    """All occupation vectors of length 2n with sum exactly k (stars/bars)."""
    m = 2 * n
    occ = []
    for bars in itertools.combinations(range(k + m - 1), m - 1):
        prev = -1
        state = []
        for b in list(bars) + [k + m - 1]:
            state.append(b - prev - 1)
            prev = b
        occ.append(state)
    occ = np.array(occ, dtype=np.int64)
    assert np.all(occ.sum(axis=1) == k)
    index = {tuple(int(x) for x in o): i for i, o in enumerate(occ)}
    return occ, index

def occupation_index(index, state):
    return index[tuple(int(x) for x in state)]

def uN_generator(occ, index, z, n):
    """A = sum_ij Z_ij E_ij with E_ij = a_i^dag a_j + b_i^dag b_j."""
    dim = len(occ)
    rows, cols, data = [], [], []
    na = occ[:, 0::2]
    nb = occ[:, 1::2]
    for i in range(n):
        for j in range(n):
            zij = z[i, j]
            if abs(zij) == 0:
                continue
            if i == j:
                d = (na[:, i] + nb[:, i]) * zij
                rows.extend(range(dim))
                cols.extend(range(dim))
                data.extend(d.tolist())
                continue
            # a-part: donor edge j needs na_j > 0
            m = na[:, j] > 0
            cols_a = np.nonzero(m)[0]
            if len(cols_a):
                tgt = occ[cols_a].copy()
                tgt[:, 2 * i] += 1
                tgt[:, 2 * j] -= 1
                fac = np.sqrt(na[cols_a, j] * (na[cols_a, i] + 1)) * zij
                for c, trow, f in zip(cols_a, tgt, fac):
                    rows.append(occupation_index(index, trow))
                    cols.append(int(c))
                    data.append(complex(f))
            # b-part
            m = nb[:, j] > 0
            cols_b = np.nonzero(m)[0]
            if len(cols_b):
                tgt = occ[cols_b].copy()
                tgt[:, 2 * i + 1] += 1
                tgt[:, 2 * j + 1] -= 1
                fac = np.sqrt(nb[cols_b, j] * (nb[cols_b, i] + 1)) * zij
                for c, trow, f in zip(cols_b, tgt, fac):
                    rows.append(occupation_index(index, trow))
                    cols.append(int(c))
                    data.append(complex(f))
    return sp.csr_matrix((data, (rows, cols)), shape=(dim, dim), dtype=complex)

def single_edge_operators(occ, index, n):
    """Per-edge Jz (diag), J+, J- as sparse matrices (each col <= 1 nnz)."""
    dim = len(occ)
    na = occ[:, 0::2]
    nb = occ[:, 1::2]
    ops = []
    for e in range(n):
        jz = sp.diags(0.5 * (na[:, e] - nb[:, e]).astype(float), format="csr")
        # J+ = a^dag b
        m = nb[:, e] > 0
        cb = np.nonzero(m)[0]
        rp, cp_, dp = [], [], []
        for c in cb:
            t = occ[c].copy()
            t[2 * e] += 1
            t[2 * e + 1] -= 1
            rp.append(occupation_index(index, t))
            cp_.append(int(c))
            dp.append(np.sqrt((na[c, e] + 1) * nb[c, e]))
        jp = sp.csr_matrix((dp, (rp, cp_)), shape=(dim, dim), dtype=complex)
        # J- = b^dag a
        m = na[:, e] > 0
        cb = np.nonzero(m)[0]
        rp, cp_, dp = [], [], []
        for c in cb:
            t = occ[c].copy()
            t[2 * e] -= 1
            t[2 * e + 1] += 1
            rp.append(occupation_index(index, t))
            cp_.append(int(c))
            dp.append(np.sqrt(na[c, e] * (nb[c, e] + 1)))
        jm = sp.csr_matrix((dp, (rp, cp_)), shape=(dim, dim), dtype=complex)
        ops.append((jz, jp, jm))
    return ops

def pairwise_grasp(ops, i, j):
    jzi, jpi, jmi = ops[i]
    jzj, jpj, jmj = ops[j]
    return jzi @ jzj + 0.5 * (jpi @ jmj + jmi @ jpj)

def normalized_exponential(A, ref_idx, dimension, tol=1e-13, max_terms=500):
    """Apply a Taylor exponential to a basis vector with a required stop test.

    Returns the normalized state and number of terms used. Raises when the
    requested term cap is reached before the relative increment tolerance.
    """
    vector = np.zeros(dimension, dtype=complex)
    vector[ref_idx] = 1.0
    result = vector.copy()
    term = vector.copy()
    for iteration in range(1, max_terms + 1):
        term = (A @ term) / iteration
        increment = float(np.linalg.norm(term))
        result_norm = float(np.linalg.norm(result))
        result = result + term
        if increment < tol * max(1.0, result_norm):
            return result / np.linalg.norm(result), iteration
    raise RuntimeError(f"Taylor exponential did not converge in {max_terms} terms")


# Historical helper names remain available while study adapters migrate.
build_fixed_k_basis = fixed_number_basis
idx_of = occupation_index
build_A = uN_generator
single_edge_ops = single_edge_operators
jdot = pairwise_grasp

__all__ = [
    "fixed_number_basis", "occupation_index", "uN_generator",
    "single_edge_operators", "pairwise_grasp", "normalized_exponential",
    "build_fixed_k_basis", "idx_of", "build_A", "single_edge_ops", "jdot",
]

"""Reusable sparse Schwinger-boson Fock spaces and grasp operators."""

import math

import numpy as np
import scipy.sparse as sp

from .conventions import GAMMA, HBAR


def bounded_compositions(nvars, maxsum):
    """Return occupation tuples with ``nvars`` modes and total at most ``maxsum``."""
    out = []
    buf = [0] * nvars

    def rec(position, remaining):
        if position == nvars - 1:
            for value in range(remaining + 1):
                buf[position] = value
                out.append(tuple(buf))
            return
        for value in range(remaining + 1):
            buf[position] = value
            rec(position + 1, remaining - value)

    rec(0, maxsum)
    return out


class SparseSchwingerSpace:
    """Schwinger Fock space truncated to at most ``K_max`` bosons.

    Sparse matrices for ``E_ij``, the local SU(2) generators, and
    ``J_i . J_j`` are built once and reused by state and thermal studies.
    """

    def __init__(self, N, K_max):
        self.N = N
        self.K_max = K_max
        self.occs = np.asarray(bounded_compositions(2 * N, K_max), dtype=np.int64)
        self.dim = len(self.occs)
        self.index = {tuple(int(x) for x in occ): i
                      for i, occ in enumerate(self.occs)}
        self.energy = self.occs.sum(axis=1).astype(float)
        self.edge_total = np.stack(
            [self.occs[:, 2 * edge] + self.occs[:, 2 * edge + 1]
             for edge in range(N)], axis=1).astype(float)

        def ladder(edge, dag, species):
            offset = 2 * edge + species
            rows, cols, data = [], [], []
            for col, occ in enumerate(self.occs):
                number = int(occ[offset])
                if dag:
                    target = occ.copy()
                    target[offset] += 1
                    target = tuple(int(x) for x in target)
                    if target in self.index:
                        rows.append(self.index[target])
                        cols.append(col)
                        data.append(math.sqrt(number + 1))
                elif number:
                    target = occ.copy()
                    target[offset] -= 1
                    rows.append(self.index[tuple(int(x) for x in target)])
                    cols.append(col)
                    data.append(math.sqrt(number))
            return sp.csr_matrix((data, (rows, cols)),
                                 shape=(self.dim, self.dim))

        adag = [[ladder(edge, True, species) for edge in range(N)]
                for species in range(2)]
        annihilate = [[ladder(edge, False, species) for edge in range(N)]
                      for species in range(2)]

        self.E = {
            (i, j): adag[0][i] @ annihilate[0][j]
            + adag[1][i] @ annihilate[1][j]
            for i in range(N) for j in range(N)
        }

        self.Jz, self.Jp, self.Jm = [], [], []
        for edge in range(N):
            z = sp.diags(
                0.5 * (self.occs[:, 2 * edge] - self.occs[:, 2 * edge + 1]),
                format="csr",
            )
            self.Jz.append(z)
            self.Jp.append(adag[0][edge] @ annihilate[1][edge])
            self.Jm.append(adag[1][edge] @ annihilate[0][edge])

        self.A = {
            (i, j): self.Jz[i] @ self.Jz[j]
            + 0.5 * (self.Jp[i] @ self.Jm[j] + self.Jm[i] @ self.Jp[j])
            for i in range(N) for j in range(N)
        }

    def amat(self, Z):
        """Return ``sum_ij Z_ij E_ij`` as a CSR matrix."""
        out = sp.csr_matrix((self.dim, self.dim), dtype=complex)
        for (i, j), operator in self.E.items():
            value = Z[i, j]
            if value != 0:
                out = out + value * operator
        return out

    def taylor_exp(self, A, ref_vec, K, tol=1e-13):
        """Apply ``exp(A)`` to a reference vector and return state and terms."""
        return normalized_taylor_exp(A, ref_vec, K, tol=tol)

    def ref_vec(self, ref_occupations):
        """Return the unit vector for an ``(N, 2)`` occupation array."""
        occupation = tuple(int(x) for pair in ref_occupations for x in pair)
        vector = np.zeros(self.dim, dtype=complex)
        vector[self.index[occupation]] = 1.0
        return vector


def normalized_taylor_exp(A, ref_vec, K, tol=1e-12):
    """Apply ``exp(A)`` to a reference vector and return it with term count."""
    result = ref_vec.copy()
    term = ref_vec.copy()
    for n in range(1, 8 * K + 50):
        term = (A @ term) / n
        result = result + term
        if np.linalg.norm(term) < tol * max(1.0, float(np.linalg.norm(result))):
            return result / np.linalg.norm(result), n
    raise RuntimeError("Perelomov Taylor exponential did not converge")


def q_operator(space, triple=(0, 1, 2)):
    """Return the Hermitian triple grasp ``i[J_i.J_j, J_j.J_k]``."""
    i, j, k = triple
    Aij, Ajk = space.A[(i, j)], space.A[(j, k)]
    return 1j * (Aij @ Ajk - Ajk @ Aij)


def volume_on_vec(vec, space, triple=(0, 1, 2), gamma=GAMMA, hbar=HBAR):
    """Return the signed-grasp mean proxy ``(sqrt(|<q>|), <q>)``.

    This state-level proxy is not the expectation of the positive spectral
    volume operator implemented by the closed-basis studies.
    """
    i, j, k = triple
    Aij, Ajk = space.A[(i, j)], space.A[(j, k)]
    v_ij, v_jk = Aij @ vec, Ajk @ vec
    q_vec = 1j * (Aij @ v_jk - Ajk @ v_ij)
    q_expectation = complex(vec.conj() @ q_vec)
    volume = (gamma * hbar) ** 1.5 * float(np.sqrt(abs(q_expectation)))
    return volume, q_expectation

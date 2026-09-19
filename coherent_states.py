"""U(N) coherent states in Loop Quantum Gravity via Schwinger bosons.

Each edge i = 1..N of the spin network carries a pair of harmonic
oscillators a_i, b_i with [a, a^dagger] = [b, b^dagger] = 1. The Schwinger
representation of su(2),

    J_i^z = (a_i^dagger a_i - b_i^dagger b_i) / 2,
    J_i^+ = a_i^dagger b_i,

maps the Fock states |n_a, n_b> to the spin-j representation with
j = (n_a + n_b)/2. The u(N) Lie algebra acts through

    E_ij = a_i^dagger a_j + b_i^dagger b_j,        [E_ij, E_kl] = delta_jk E_il - delta_li E_kj,

under which the states decompose into irreps of fixed total occupation
K = sum_i (n_a,i + n_b,i).

Coherent states: following the U(N) framework of Freidel, Krasnov and
Livine, a Perelomov coherent state labeled by an N x N complex matrix Z is

    |Z> = (1/sqrt(N(Z))) exp(sum_{ij} Z_ij E_ij) |ref>,

where |ref> is a lowest-weight reference state (Schwinger bosons on a
chosen set of edges). The reference is created from the empty vacuum by
the raising monomials prod_i (a_i^dagger)^{k_i}; the U(N) exponential
then redistributes the bosons. Because the E_ij conserve the total boson
number K, the exponential is evaluated as a Taylor series that terminates
exactly on the finite Fock space with K bosons.

The momentum map from the Grassmannian Gr(2, N) to u(N)*: given a 2-plane
spanned by orthonormal vectors a, b in C^N, the coherent state is labeled
by

    Z_ij = a_i conj(b_j) - b_i conj(a_j)   (anti-Hermitian, Z = -Z^dagger),

the classical u(N) generator of the projector onto the plane.

Only numpy is used.
"""

import itertools
import math

import numpy as np

# Barbero-Immirzi parameter (standard LQG value).
GAMMA = 0.2375


class FockSpace:
    """Schwinger Fock space on N edges truncated by total boson number.

    Basis states are flat occupation tuples (n_a1, n_b1, ..., n_aN, n_bN)
    with sum(n) <= K_max. This truncation is invariant under the u(N)
    generators E_ij = a_i^dagger a_j + b_i^dagger b_j (they conserve the
    total boson number K = sum_i (n_a,i + n_b,i)), so the algebra closes
    on the finite space. Dimension = binom(2N + K_max, 2N).
    """

    def __init__(self, N, K_max):
        self.N = N
        self.K_max = K_max
        self.occupations = np.array(
            [occ for occ in itertools.product(range(K_max + 1), repeat=2 * N)
             if sum(occ) <= K_max],
            dtype=int,
        )
        self.dim = len(self.occupations)
        self.index = {tuple(int(x) for x in occ): i for i, occ in enumerate(self.occupations)}

    def vec(self, state_dict):
        """Convert {occupation_tuple: amplitude} to a dense vector."""
        v = np.zeros(self.dim, dtype=complex)
        for occ, amp in state_dict.items():
            v[self.index[tuple(occ)]] = amp
        return v

    def dict(self, vec):
        """Convert a dense vector to {occupation_tuple: amplitude},
        dropping entries below 1e-12."""
        out = {}
        for i, amp in enumerate(vec):
            if abs(amp) > 1e-12:
                out[tuple(int(x) for x in self.occupations[i])] = complex(amp)
        return out

    def apply(self, op, vec):
        """Apply an occupation-space operator.

        op(occ) must return a list of (occ_new, factor) pairs such that
        op |occ> = sum factor |occ_new>.
        """
        out = np.zeros(self.dim, dtype=complex)
        nz = np.nonzero(vec)[0]
        for i in nz:
            occ = tuple(int(x) for x in self.occupations[i])
            for occ_new, factor in op(occ):
                out[self.index[tuple(occ_new)]] += factor * vec[i]
        return out


def _edge_ops(kind, edge, N):
    """Occupation-space action of the four single-edge oscillator ops.

    kind in {'adag', 'a', 'bdag', 'b'} on the given edge (0-based).
    """
    off = 2 * edge

    def op(occ):
        na, nb = occ[off], occ[off + 1]
        if kind == "adag":
            return [(occ[:off] + (na + 1, nb) + occ[off + 2:], np.sqrt(na + 1))]
        if kind == "a":
            if na == 0:
                return []
            return [(occ[:off] + (na - 1, nb) + occ[off + 2:], np.sqrt(na))]
        if kind == "bdag":
            return [(occ[:off] + (na, nb + 1) + occ[off + 2:], np.sqrt(nb + 1))]
        if nb == 0:
            return []
        return [(occ[:off] + (na, nb - 1) + occ[off + 2:], np.sqrt(nb))]

    return op


def schwinger_state(occupations):
    """Normalized Schwinger boson state from a list of N (n_a, n_b) pairs.

    |{n_a, n_b}> = prod_i (a_i^dagger)^{n_a,i} (b_i^dagger)^{n_b,i}
                   / sqrt(prod_i n_a,i! n_b,i!) |0>.

    This state is normalized to unity; since the occupation basis itself
    consists of normalized Fock states, the amplitude of the single
    occupied basis vector is exactly 1 (the factorials are already the
    normalization of the basis vectors, not extra amplitudes).

    Parameters
    ----------
    occupations : array-like, shape (N, 2)
        (n_a, n_b) per edge.

    Returns
    -------
    state : dict
        {occupation_tuple: amplitude} with unit amplitude.
    """
    occ = np.asarray(occupations, dtype=int)
    if occ.ndim != 2 or occ.shape[1] != 2:
        raise ValueError(f"occupations must have shape (N, 2), got {occ.shape}")
    flat = tuple(int(x) for pair in occ for x in pair)
    return {flat: 1.0 + 0.0j}


def uN_generators(N, k_max):
    """u(N) generators E_ij = a_i^dagger a_j + b_i^dagger b_j as
    occupation-space operators.

    Returns
    -------
    E : dict mapping (i, j) (0-based) to operator functions usable with
        FockSpace.apply.
    """
    ops = {}
    for i in range(N):
        for j in range(N):
            ai, aj = _edge_ops("adag", i, N), _edge_ops("a", j, N)
            bi, bj = _edge_ops("bdag", i, N), _edge_ops("b", j, N)

            def make(ai=ai, aj=aj, bi=bi, bj=bj):
                def op(occ):
                    return ai(occ) if False else [
                        *[(o, f) for o, f in _combine(aj, ai, occ)],
                        *[(o, f) for o, f in _combine(bj, bi, occ)],
                    ]
                return op

            ops[(i, j)] = make()
    return ops


def _combine(lower, raise_, occ):
    """Composed action raise_ (lower |occ>): lower first, then raise on
    each surviving branch."""
    out = []
    for occ1, f1 in lower(occ):
        for occ2, f2 in raise_(occ1):
            out.append((occ2, f1 * f2))
    return out


def verify_uN_algebra(N, k_max, n_tests=200, tol=1e-8, seed=0):
    """Numerically verify [E_ij, E_kl] = delta_jk E_il - delta_li E_kj on
    random basis states of the truncated Fock space."""
    rng = np.random.default_rng(seed)
    space = FockSpace(N, k_max)
    E = uN_generators(N, k_max)
    max_err = 0.0
    for _ in range(n_tests):
        i = int(rng.integers(0, space.dim))
        vec = np.zeros(space.dim, dtype=complex)
        vec[i] = 1.0
        for _ in range(4):
            i, j, k, l = rng.integers(0, N, size=4)
            lhs = space.apply(E[i, j], space.apply(E[k, l], vec)) - space.apply(
                E[k, l], space.apply(E[i, j], vec)
            )
            rhs = space.apply(E[i, l], vec) * (1.0 if j == k else 0.0) - space.apply(
                E[k, j], vec
            ) * (1.0 if l == i else 0.0)
            max_err = max(max_err, float(np.max(np.abs(lhs - rhs))))
    return max_err < tol, max_err


def _exponential_state(E, Z, ref_vec, space, tol=1e-12):
    """exp(sum_ij Z_ij E_ij) |ref> by Taylor series.

    The E_ij conserve the total boson number, so on the finite Fock space
    with K bosons the series terminates; we stop when the norm increment
    falls below tol.
    """
    # total boson number of the reference (all nonzero components share it)
    nz = np.nonzero(ref_vec)[0]
    K = int(sum(space.occupations[nz[0]]))

    def A(vec):
        out = np.zeros_like(vec)
        for (i, j), op in E.items():
            if abs(Z[i, j]) > 0:
                out = out + Z[i, j] * space.apply(op, vec)
        return out

    result = ref_vec.copy()
    term = ref_vec.copy()
    for n in range(1, 2 * K + 4):
        term = A(term) / n
        inc = float(np.linalg.norm(term))
        result = result + term
        if inc < tol * max(1.0, float(np.linalg.norm(result))):
            break
    return result / np.linalg.norm(result)


def perelomov_state(Z, k_max, ref_occupations=None, space=None):
    """Perelomov U(N) coherent state |Z> = exp(Z.E) |ref>.

    Parameters
    ----------
    Z : array-like, shape (N, N), complex
        Label matrix (anti-Hermitian Z = -Z^dagger for the Grassmannian
        momentum map, but any matrix is accepted).
    k_max : int
        Truncation: at most k_max bosons in total (all edges).
    ref_occupations : array-like, shape (N, 2), optional
        Boson numbers creating the reference state from the empty vacuum,
        prod_i (a_i^dagger)^{k_i}|0> with k_i = n_a + n_b. Default: one
        a-boson on edge 0, i.e. the N=1 lowest-weight tower generated
        from a single occupied edge. (With the empty vacuum the
        exponential acts trivially — see module docstring.)
    space : FockSpace, optional
        Reuse an existing space.

    Returns
    -------
    state : dict
        {occupation_tuple: amplitude}, unit normalized.
    space : FockSpace
        The space the state lives in.
    """
    Z = np.asarray(Z, dtype=complex)
    N = Z.shape[0]
    if space is None:
        space = FockSpace(N, k_max)
    if ref_occupations is None:
        ref = np.zeros((N, 2), dtype=int)
        ref[0, 0] = 1  # single a-boson on edge 0
    else:
        ref = np.asarray(ref_occupations, dtype=int)
        if int(ref[:, 0].sum() + ref[:, 1].sum()) > k_max:
            raise ValueError("reference occupations exceed k_max")
    ref_vec = space.vec(schwinger_state(ref))
    E = uN_generators(N, space.K_max)
    vec = _exponential_state(E, Z, ref_vec, space)
    return space.dict(vec), space


def number_operator(edge):
    """n_i = a_i^dagger a_i + b_i^dagger b_i on the given edge."""
    adag, a = _edge_ops("adag", edge, edge + 1), _edge_ops("a", edge, edge + 1)
    bdag, b = _edge_ops("bdag", edge, edge + 1), _edge_ops("b", edge, edge + 1)
    na, nb = 2 * edge, 2 * edge + 1

    def op(occ):
        return [(occ, float(occ[na] + occ[nb]))]

    return op


def su2_ops(edge):
    """Schwinger su(2) generators on one edge: returns dict with
    'z', 'plus', 'minus', and the Casimir-consistent 'minus dagger' ops."""
    adag, a = _edge_ops("adag", edge, edge + 1), _edge_ops("a", edge, edge + 1)
    bdag, b = _edge_ops("bdag", edge, edge + 1), _edge_ops("b", edge, edge + 1)

    def jz(occ):
        return [(occ, 0.5 * (occ[2 * edge] - occ[2 * edge + 1]))]

    def jp(occ):
        return _combine(b, adag, occ)  # a^dagger b

    def jm(occ):
        return _combine(a, bdag, occ)  # b^dagger a

    return {"z": jz, "plus": jp, "minus": jm}


def expectation(state, op, space):
    """<psi|op|psi> for a normalized dict state."""
    vec = space.vec(state)
    return complex(vec.conj() @ space.apply(op, vec))


def area_expectation(state, edge, space, gamma=GAMMA, hbar=1.0):
    """Area of edge i: A_i = gamma * hbar * (a_i^dagger a_i + b_i^dagger b_i)."""
    return float(np.real(gamma * hbar * expectation(state, number_operator(edge), space)))


def area_uncertainty(state, edge, space, gamma=GAMMA, hbar=1.0):
    """Delta A_i = sqrt(<A_i^2> - <A_i>^2)."""
    n = number_operator(edge)
    n2 = lambda occ: [(o, f * (o[2 * edge] + o[2 * edge + 1]))
                      for o, f in n(occ)]
    mean2 = (gamma * hbar) ** 2 * float(np.real(expectation(state, n2, space)))
    mean = area_expectation(state, edge, space, gamma, hbar)
    return float(np.sqrt(max(mean2 - mean * mean, 0.0)))


def plane_to_Z(plane):
    """Momentum map Gr(2, N) -> u(N)*: orthonormalize the two rows of the
    plane to (a, b) and return Z_ij = a_i conj(b_j) - b_i conj(a_j).

    Z is anti-Hermitian, Z = -Z^dagger, and its image lies on the coadjoint
    orbit of the plane's orthogonal projector.
    """
    plane = np.asarray(plane, dtype=complex)
    if plane.ndim != 2 or plane.shape[0] != 2:
        raise ValueError(f"plane must have shape (2, N), got {plane.shape}")
    a, b = plane
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-14 or nb < 1e-14:
        raise ValueError("degenerate plane")
    a = a / na
    b = b - a * (a.conj() @ b)
    nb = np.linalg.norm(b)
    if nb < 1e-14:
        raise ValueError("plane rows are parallel")
    b = b / nb
    return np.outer(a, b.conj()) - np.outer(b, a.conj())


def example_N3():
    """N = 3 example: plane -> Z -> Perelomov state -> areas.

    Picks a 2-plane in C^3, builds the U(3) coherent state labeled by its
    momentum-map image, and checks that the expectation values of the area
    operators are positive and reproduce the classical column norms of the
    plane at large occupation.
    """
    print("=== N = 3 example: U(3) coherent state from a Gr(2, 3) plane ===\n")

    plane = np.array(
        [[1.0, 0.5 + 0.3j, 0.2 - 0.1j],
         [0.1, 1.0,        0.4 + 0.2j]],
        dtype=complex,
    )
    Z = plane_to_Z(plane)
    print("Plane (2x3):")
    for row in plane:
        print("  " + "  ".join(f"{z:+.3f}" for z in row))
    print(f"\nMomentum-map label Z_ij = a_i conj(b_j) - b_i conj(a_j):")
    for row in Z:
        print("  " + "  ".join(f"{z:+.3f}" for z in row))
    print(f"  anti-Hermiticity |Z + Z^dagger|_max = {np.max(np.abs(Z + Z.conj().T)):.3e}")

    # Build coherent states at two occupation scales.
    for k in (2, 6):
        ref = np.zeros((3, 2), dtype=int)
        ref[0, 0] = k  # k a-bosons on edge 0: spin j = k/2 there
        state, space = perelomov_state(3.0 * Z, k_max=2 * k, ref_occupations=ref)
        n_mean = [area_expectation(state, i, space) / GAMMA for i in range(3)]
        norms = [float(np.linalg.norm(plane[:, i])) for i in range(3)]
        print(f"\nPerelomov state, reference occupation k = {k} "
              f"(Fock dim {space.dim}):")
        print(f"  <A_i>/gamma = <n_i> (quantum): {[f'{a:.4f}' for a in n_mean]}")
        print(f"  |column_i| (classical): {[f'{n:.4f}' for n in norms]}")
        print(f"  all areas positive: {all(a > 0 for a in n_mean)}")
        print(f"  closure sum_i <n_i> = {sum(n_mean):.4f} "
              f"(= total boson number {k})")
        print(f"  relative spread max/min: {max(n_mean)/min(n_mean):.3f} vs "
              f"classical {max(norms)/min(norms):.3f}")
    return {"plane": plane, "Z": Z}


def _test():
    ok_alg, err = verify_uN_algebra(3, 3)
    print(f"u(3) algebra, max |commutator - rhs| = {err:.3e}, ok = {ok_alg}")
    assert ok_alg

    # Single-edge Fock state sanity: |1,2> has norm 1, J^z = (1-2)/2.
    st = schwinger_state([[1, 2]])
    space = FockSpace(1, 3)
    vec = space.vec(st)
    assert abs(np.linalg.norm(vec) - 1) < 1e-12
    assert abs(expectation(st, su2_ops(0)["z"], space) - (-0.5)) < 1e-12

    # Exponential from empty vacuum is trivial (E_ij annihilate |0>).
    Z0 = np.zeros((3, 3), dtype=complex)
    Z0[0, 1] = 1.0
    st0, _ = perelomov_state(Z0, k_max=2, ref_occupations=np.zeros((3, 2), int))
    assert len(st0) == 1

    # Round trip of momentum map through a random plane and state covariance
    # is exercised in correspondence.py; here check Z is anti-Hermitian.
    rng = np.random.default_rng(1)
    plane = rng.normal(size=(2, 4)) + 1j * rng.normal(size=(2, 4))
    Z = plane_to_Z(plane)
    assert np.max(np.abs(Z + Z.conj().T)) < 1e-12

    example_N3()
    print("\nAll coherent_states.py tests passed.")


if __name__ == "__main__":
    _test()

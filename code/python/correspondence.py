"""The LQG-Grassmannian correspondence: from geometry to kinematics.

This module implements the inverse maps of Phases 1-2 and identifies the
dictionary between scattering invariants of the N-leg massless amplitude
and geometric invariants of the Gr(2, N) plane / U(N) coherent state:

kinematics (spinor helicity)  <->  Gr(2, N) plane  <->  U(N) coherent state

Key identifications (real section, mu = conj(lambda)):
    * column i of the plane = holomorphic spinor lambda_i
    * momentum p_i^mu = lambda_i conj(lambda_i)^T sigma^mu / 2, null
    * Mandelstam invariant s_ij = (p_i + p_j)^2 = |<ij>|^2 = |M_ij|^2,
      the squared modulus of the Plucker coordinate M_ij
    * energy E_i = |lambda_i|^2 = norm of column i ("area" of edge i)
    * the coherent state's covariance <E_ij> ~ k * (projector onto the
      plane), so the plane is recovered as the top-2 eigenspace of <E>.

Only numpy is used.
"""

import itertools

import numpy as np

from coherent_states import (
    FockSpace,
    expectation,
    plane_to_Z,
    perelomov_state,
    uN_generators,
)
from grassmannian import (
    momentum_from_spinors,
    plane_to_plucker,
    spinors_to_plane,
)


def kinematics_from_plane(plane):
    """Extract N null momenta from a Gr(2, N) plane (real section).

    Column i is the spinor lambda_i; the momentum is reconstructed as
    p_i^mu = (1/2) Tr(lambda_i conj(lambda_i)^T sigma^mu). Each p_i is
    null and future-directed with E_i = |lambda_i|^2. Momentum
    conservation sum_i p_i = 0 is NOT automatic on the real section; it
    holds only for special planes (checked by check_momentum_conservation
    with complexified mu).

    Parameters
    ----------
    plane : array-like, shape (2, N)

    Returns
    -------
    lambdas : ndarray, shape (N, 2)
    momenta : ndarray, shape (N, 4), real null 4-vectors
    """
    plane = np.asarray(plane, dtype=complex)
    lambdas = plane.T.copy()
    momenta = np.array(
        [np.real_if_close(momentum_from_spinors(lam), tol=1000) for lam in lambdas]
    ).astype(float)
    return lambdas, momenta


def plane_from_coherent_state(state, space):
    """Recover the Gr(2, N) plane from a U(N) coherent state.

    For a Perelomov state built from a plane spanned by orthonormal rows
    (a, b) with k bosons per edge, the covariance matrix of the u(N)
    generators approximates k times the orthogonal projector onto the
    plane:

        <E_ij> ~ k (a_i conj(a_j) + b_i conj(b_j)).

    The plane is therefore the 2-dimensional eigenspace of the Hermitian
    matrix <E> with the largest eigenvalues. Returns the 2 x N plane
    whose rows are the two dominant eigenvectors.
    """
    N = space.N
    E = uN_generators(N, space.K_max)
    C = np.zeros((N, N), dtype=complex)
    for (i, j), op in E.items():
        C[i, j] = expectation(state, op, space)
    C = 0.5 * (C + C.conj().T)  # remove numerical anti-Hermitian part
    evals, evecs = np.linalg.eigh(C)
    order = np.argsort(evals)[::-1]
    plane = evecs[:, order[:2]].conj().T  # rows = top-2 eigenvectors
    return plane, evals[order]


def scattering_invariants(momenta):
    """Mandelstam invariants s_ij = (p_i + p_j)^2 for all pairs i < j.

    Parameters
    ----------
    momenta : array-like, shape (N, 4), real null momenta

    Returns
    -------
    pairs : list of (i, j)
    s : ndarray, shape (N choose 2,)
    """
    p = np.asarray(momenta, dtype=float)
    metric = np.diag([1.0, -1.0, -1.0, -1.0])
    pairs = list(itertools.combinations(range(p.shape[0]), 2))
    s = np.array([float((p[i] + p[j]) @ metric @ (p[i] + p[j])) for i, j in pairs])
    return pairs, s


def geometric_invariants(plane):
    """Geometric observables of the Gr(2, N) plane:

    * Plucker coordinates M_ij (the 2x2 minors),
    * edge "areas": column norms |lambda_i| (classical area of edge i),
    * total scale sqrt(sum_i |lambda_i|^2).

    Returns
    -------
    dict with keys 'pairs', 'plucker', 'column_norms', 'scale'.
    """
    plane = np.asarray(plane, dtype=complex)
    pairs, minors = plane_to_plucker(plane)
    norms = np.linalg.norm(plane, axis=0)
    return {
        "pairs": pairs,
        "plucker": minors,
        "column_norms": norms,
        "scale": float(np.sqrt(np.sum(norms**2))),
    }


def map_invariants(momenta, plane=None, verbose=True):
    """Map scattering invariants to geometric invariants.

    For the real section the dictionary is exact and diagonal:

        s_ij = (p_i + p_j)^2 = |<lambda_i lambda_j>|^2 = |M_ij|^2,

    i.e. each Mandelstam invariant is the squared modulus of one Plucker
    coordinate. This function verifies the identity numerically. If only
    momenta are given, the plane is reassembled from their spinors.

    Returns
    -------
    dict with 'pairs', 's', 'plucker', 'max_deviation' (of s from |M|^2).
    """
    if plane is None:
        from grassmannian import null_momentum_to_spinor

        lambdas = np.array([null_momentum_to_spinor(p) for p in momenta])
        plane = spinors_to_plane(lambdas)
    _, s = scattering_invariants(momenta)
    geo = geometric_invariants(plane)
    dev = float(np.max(np.abs(s - np.abs(geo["plucker"]) ** 2)))
    if verbose:
        print("s_ij vs |M_ij|^2:")
        for (i, j), sv, m in zip(geo["pairs"], s, geo["plucker"]):
            print(f"  s_{i + 1}{j + 1} = {sv:+.6f}   |M_{i + 1}{j + 1}|^2 = "
                  f"{abs(m) ** 2:+.6f}")
        print(f"  max |s_ij - |M_ij|^2| = {dev:.3e}")
    return {
        "pairs": geo["pairs"],
        "s": s,
        "plucker": geo["plucker"],
        "max_deviation": dev,
    }


def example_N4_full():
    """Complete N = 4 round trip: kinematics -> plane -> Z -> coherent
    state -> covariance -> plane -> kinematics.

    Uses real positive-energy kinematics p_i = lambda_i conj(lambda_i)
    (so the plane is a positive configuration); momentum conservation is
    checked on the complexified data separately in grassmannian.example_n4.
    """
    print("=== N = 4 full correspondence round trip ===\n")

    lambdas = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
            [1.0, 2.0],
        ],
        dtype=complex,
    )
    plane = spinors_to_plane(lambdas)
    _, momenta = kinematics_from_plane(plane)

    print("Kinematics (real section, p_i = lambda_i conj(lambda_i)):")
    for i, p in enumerate(momenta):
        print(f"  p{i + 1} = {p}   E_{i + 1} = {p[0]:.3f}")

    res = map_invariants(momenta, plane)

    Z = plane_to_Z(plane)
    print(f"\nMomentum-map label Z (anti-Hermitian): "
          f"max |Z + Z^dagger| = {np.max(np.abs(Z + Z.conj().T)):.3e}")

    # Coherent state with k bosons per edge reference on edge 0.
    k = 3
    ref = np.zeros((4, 2), dtype=int)
    ref[0, 0] = k
    state, space = perelomov_state(2.0 * Z, k_max=k, ref_occupations=ref)
    print(f"\nPerelomov state built (reference occupation k = {k}, "
          f"Fock dim {space.dim})")

    plane_back, evals = plane_from_coherent_state(state, space)
    # Compare with the classical projector: eigenvalues should be ~0 and ~k.
    print(f"covariance <E> eigenvalues: {[f'{e:.4f}' for e in evals]}")

    # Gauge-invariant comparison: principal angles between the two planes,
    # from the singular values of the 2x2 Gram matrix of the row spaces.
    G = plane @ plane_back.conj().T
    svals = np.linalg.svd(G, compute_uv=False)
    svals = np.clip(svals, 0.0, 1.0)
    angles = np.arccos(svals)
    print(f"principal angles plane vs. recovered plane (rad): "
          f"{[f'{a:.4f}' for a in angles]}")

    _, momenta_back = kinematics_from_plane(plane_back)
    pairs, s_back = scattering_invariants(momenta_back)
    s_ratio = np.sqrt(s_back / res["s"])
    print(f"s-channel ratios sqrt(s_back/s) for all pairs: "
          f"{[f'{r:.4f}' for r in s_ratio]}")
    return {
        "plane": plane,
        "Z": Z,
        "state": state,
        "space": space,
        "principal_angles": angles,
        "s": res["s"],
        "s_back": s_back,
    }


def _test():
    # Real kinematics: s_ij = |M_ij|^2 exactly.
    rng = np.random.default_rng(7)
    for _ in range(20):
        lambdas = rng.normal(size=(4, 2)) + 1j * rng.normal(size=(4, 2))
        plane = spinors_to_plane(lambdas)
        _, momenta = kinematics_from_plane(plane)
        res = map_invariants(momenta, plane, verbose=False)
        assert res["max_deviation"] < 1e-10, res["max_deviation"]
    print("s_ij = |M_ij|^2 verified on 20 random real N=4 configurations")

    # Round trip: plane -> state -> plane recovers the same invariants.
    out = example_N4_full()
    assert max(out["principal_angles"]) < 0.3, out["principal_angles"]
    print("\nAll correspondence.py tests passed.")


if __name__ == "__main__":
    _test()

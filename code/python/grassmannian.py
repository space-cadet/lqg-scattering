"""U(N) coherent states in Loop Quantum Gravity and the kinematic space of
massless scattering on the Grassmannian Gr(2, N).

Correspondence
--------------
A (complexified) null momentum p^mu defines, through the Pauli map

    P_{a adot} = p_mu sigma^mu_{a adot},   sigma^mu = (1, sigma_x, sigma_y, sigma_z),

a rank-one 2x2 matrix (det P = p^2 = 0), which factorizes into two
two-component spinors,

    P_{a adot} = lambda_a mu_{adot}.

In the LQG coherent-state picture lambda is the holomorphic spinor network
data and mu its antiholomorphic conjugate; on the real (Lorentzian) section
mu = conj(lambda). Collecting N holomorphic spinors as the columns of a 2xN
matrix C gives a 2-plane in C^N, i.e. a point of the Grassmannian Gr(2, N),
the kinematic space of the N-leg amplitude.

Momentum conservation sum_i p_i^mu = 0 is equivalently the 2x2 matrix
identity

    sum_i lambda_i mu_i^T = 0.

Note on the real section: if mu_i = conj(lambda_i) this becomes a sum of
positive-semidefinite Hermitian matrices, which vanishes only in the trivial
configuration. Non-trivial real momentum configurations are recovered after
imposing the conservation constraint on the complexified data and
intersecting with the real section; the example below therefore works with
genuine complex kinematics, as in the standard treatments.

The Gr(2, N) element is invariant under per-column rescalings
lambda_i -> t_i lambda_i (t_i in C*), the little-group / U(1)^N redundancy
familiar from both the spinor-helicity and LQG coherent-state viewpoints.

Only numpy is used.
"""

import itertools

import numpy as np

# Pauli matrices, with sigma^0 the identity.
SIGMA = (
    np.eye(2, dtype=complex),
    np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex),
    np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex),
    np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex),
)


def null_momentum_to_spinor(p):
    """Convert a real null 4-vector to a two-component spinor.

    Parameters
    ----------
    p : array-like, shape (4,)
        Null momentum (E, px, py, pz), metric (+, -, -, -), p^2 = 0,
        future-directed (E >= 0).

    Returns
    -------
    lam : ndarray, shape (2,), complex
        Spinor lambda such that p_{a adot} = lambda_a conj(lambda_adot).
        Defined up to an overall phase.

    Raises
    ------
    ValueError
        If p is not null within numerical tolerance or is past-directed.
    """
    p = np.asarray(p, dtype=float)
    if p.shape != (4,):
        raise ValueError(f"p must have shape (4,), got {p.shape}")
    if p[0] < 0.0:
        raise ValueError("momentum must be future-directed (E >= 0)")

    E, px, py, pz = p
    p2 = E * E - px * px - py * py - pz * pz
    if abs(p2) > 1e-10 * max(1.0, E * E):
        raise ValueError(f"momentum is not null: p^2 = {p2}")

    # P = p_mu sigma^mu = [[E + pz, px - i py],
    #                      [px + i py, E - pz]]  =  lam lam^dagger.
    # Factorize explicitly, pivoting on whichever diagonal entry is
    # nonzero so the construction is stable on the z-axis.
    if E + pz > 1e-14 * max(1.0, E):
        lam0 = np.sqrt(E + pz)
        lam1 = (px + 1.0j * py) / lam0
    else:
        lam1 = np.sqrt(E - pz)
        lam0 = (px - 1.0j * py) / lam1
    return np.array([lam0, lam1], dtype=complex)


def momentum_from_spinors(lam, mu=None):
    """Reconstruct a (possibly complex) null 4-vector from its spinors.

    p^mu = (1/2) Tr(lambda mu^T sigma^mu). With mu = conj(lambda) this is
    the real-section momentum lambda_a conj(lambda_adot).

    Parameters
    ----------
    lam : array-like, shape (2,)
        Holomorphic spinor.
    mu : array-like, shape (2,), optional
        Antiholomorphic spinor; defaults to conj(lam).

    Returns
    -------
    p : ndarray, shape (4,), complex
    """
    lam = np.asarray(lam, dtype=complex)
    if mu is None:
        mu = lam.conj()
    else:
        mu = np.asarray(mu, dtype=complex)
    P = np.outer(lam, mu)
    return np.array([0.5 * np.trace(P @ s) for s in SIGMA])


def spinors_to_plane(lambdas):
    """Assemble N spinors into the 2xN matrix of a 2-plane in C^N.

    Parameters
    ----------
    lambdas : array-like, shape (N, 2) or (2, N)
        The N spinors. A (N, 2) array is interpreted as a list of N
        spinors; a (2, N) array is taken literally as the plane matrix.

    Returns
    -------
    plane : ndarray, shape (2, N), complex
        Matrix C whose i-th column is lambda_i. Its row space is a
        2-plane, i.e. a point of Gr(2, N), defined up to GL(2) action on
        the rows and C* rescaling of each column.
    """
    arr = np.asarray(lambdas, dtype=complex)
    if arr.ndim != 2:
        raise ValueError(f"lambdas must be 2-dimensional, got {arr.ndim}")
    if arr.shape[0] == 2 and arr.shape[1] != 2:
        return arr.copy()
    if arr.shape[1] == 2:
        return arr.T.copy()
    raise ValueError(
        f"cannot interpret shape {arr.shape} as N spinors or a 2xN plane"
    )


def check_momentum_conservation(plane, mu_plane=None, tol=1e-8):
    """Verify momentum conservation from the Gr(2, N) plane data.

    Momentum conservation sum_i p_i^mu = 0 is equivalent, in spinor
    variables, to the vanishing of the 2x2 complex matrix

        M = sum_i lambda_i mu_i^T = 0.

    On the real section (mu_plane = conj(plane)) this is a sum of
    positive-semidefinite Hermitian matrices and vanishes only for the
    trivial configuration; non-trivial configurations require complex
    kinematics, as produced in example_n4().

    Parameters
    ----------
    plane : array-like, shape (2, N)
        Plane matrix C whose columns are the holomorphic spinors lambda_i.
    mu_plane : array-like, shape (2, N), optional
        Plane matrix for the antiholomorphic spinors mu_i; defaults to
        conj(plane).
    tol : float
        Tolerance on the largest entry of M.

    Returns
    -------
    conserved : bool
    residual : float
        max abs entry of M.
    M : ndarray, shape (2, 2), complex
        The summed matrix sum_i lambda_i mu_i^T.
    """
    plane = np.asarray(plane, dtype=complex)
    if plane.ndim != 2 or plane.shape[0] != 2:
        raise ValueError(f"plane must have shape (2, N), got {plane.shape}")
    mu = plane.conj() if mu_plane is None else np.asarray(mu_plane, dtype=complex)
    if mu.shape != plane.shape:
        raise ValueError(f"mu_plane shape {mu.shape} != plane shape {plane.shape}")
    M = plane @ mu.T
    residual = float(np.max(np.abs(M)))
    return residual < tol, residual, M


def plane_to_plucker(plane):
    """Compute the Plucker coordinates of the 2-plane.

    The Plucker embedding Gr(2, N) -> P(C^(N choose 2) - 1) sends the
    plane spanned by the columns of C to its 2x2 minors

        M_{ij} = C_{1i} C_{2j} - C_{1j} C_{2i},   i < j.

    They satisfy the Plucker relations; for N = 4 the single relation is
    M12 M34 - M13 M24 + M14 M23 = 0.

    Parameters
    ----------
    plane : array-like, shape (2, N)

    Returns
    -------
    pairs : list of tuple (i, j), i < j
        Indices labeling each minor, in lexicographic order.
    minors : ndarray, shape (N choose 2,), complex
        The Plucker coordinates M_{ij} in the same order.
    """
    plane = np.asarray(plane, dtype=complex)
    if plane.ndim != 2 or plane.shape[0] != 2:
        raise ValueError(f"plane must have shape (2, N), got {plane.shape}")
    n = plane.shape[1]
    pairs = list(itertools.combinations(range(n), 2))
    minors = np.array(
        [plane[0, i] * plane[1, j] - plane[0, j] * plane[1, i]
         for i, j in pairs],
        dtype=complex,
    )
    return pairs, minors


def example_n4():
    """Explicit N = 4 example with momentum conservation.

    Uses complex kinematics built directly from spinors satisfying

        sum_i lambda_i mu_i^T = 0,

    so each reconstructed momentum p_i^mu = (1/2) Tr(lambda_i mu_i^T sigma^mu)
    is null (det = p_i^2 = 0) and the total momentum is conserved by
    construction. Prints all data and returns it as a dict.
    """
    # Holomorphic spinors lambda_i (columns of the Gr(2, 4) plane).
    lambdas = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
            [1.0, 2.0],
        ],
        dtype=complex,
    )
    # Antiholomorphic spinors mu_i, chosen so that sum_i lambda_i mu_i^T = 0:
    #   lambda1 mu1^T + ... + lambda4 mu4^T = [[0, 0], [0, 0]].
    mus = np.array(
        [
            [-2.0, -1.0],
            [-3.0, -2.0],
            [1.0, 0.0],
            [1.0, 1.0],
        ],
        dtype=complex,
    )

    print("=== N = 4 example: U(N) coherent states <-> Gr(2, 4) ===\n")

    plane = spinors_to_plane(lambdas)
    mu_plane = spinors_to_plane(mus)

    print("Spinors (holomorphic lambda_i, antiholomorphic mu_i):")
    for i in range(4):
        print(f"  lambda{i + 1} = {lambdas[i]}")
    for i in range(4):
        print(f"  mu{i + 1}    = {mus[i]}")

    # Momenta reconstructed from the spinor factorization p_{a adot} = lambda_a mu_adot.
    momenta = np.array(
        [momentum_from_spinors(lam, mu) for lam, mu in zip(lambdas, mus)]
    )
    print("\nComplex null momenta p_i^mu = (1/2) Tr(lambda_i mu_i^T sigma^mu):")
    for i, p in enumerate(momenta):
        print(f"  p{i + 1} = {p}   (p{i + 1}^2 = {p[0]**2 - p[1]**2 - p[2]**2 - p[3]**2:.3e})")
    total = momenta.sum(axis=0)
    print(f"  sum    = {total}")

    print(f"\nGr(2, 4) element (2x4 plane matrix C, columns = lambda_i):")
    for row in plane:
        print("  " + "  ".join(f"{z:+.3f}" for z in row))

    conserved, residual, M = check_momentum_conservation(plane, mu_plane)
    print(f"\nMomentum conservation sum_i lambda_i mu_i^T = 0:")
    print(f"  M = {M.tolist()}")
    print(f"  conserved={conserved}, residual={residual:.3e}")

    pairs, minors = plane_to_plucker(plane)
    print("\nPlucker coordinates M_{ij} = C_{1i} C_{2j} - C_{1j} C_{2i}:")
    for (i, j), m in zip(pairs, minors):
        print(f"  M_{i + 1}{j + 1} = {m:+.3f}")

    # The single Plucker relation for Gr(2, 4).
    pl = dict(zip(pairs, minors))
    plucker_rel = (
        pl[(0, 1)] * pl[(2, 3)] - pl[(0, 2)] * pl[(1, 3)] + pl[(0, 3)] * pl[(1, 2)]
    )
    print(f"\nPlucker relation M12 M34 - M13 M24 + M14 M23 = "
          f"{plucker_rel:.3e} (should vanish)")

    return {
        "lambdas": lambdas,
        "mus": mus,
        "momenta": momenta,
        "plane": plane,
        "mu_plane": mu_plane,
        "conserved": conserved,
        "residual": residual,
        "plucker_pairs": pairs,
        "plucker": minors,
        "plucker_relation": plucker_rel,
    }


if __name__ == "__main__":
    example_n4()

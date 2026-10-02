"""Positivity and the amplituhedron: the positive Grassmannian Gr+(2, N).

The positive Grassmannian Gr+(k, N) is the set of planes whose Plucker
coordinates can all be made real and positive by GL(k) and column-rescaling
(gauge) transformations. For Gr(2, N) every top cell has this property once
a gauge is fixed, and Gr+(2, N) fibers over the "positive region" of
kinematic space — the domain where all Mandelstam invariants s_ij > 0 —
which is the momentum-twistor image of the amplituhedron's external
data.

Canonical gauge for Gr(2, 4): any plane with M_12 != 0 can be brought to

    C = [[1, 0, -c, -d],
         [0, 1,  a,  b]],        a, b, c, d real,

whose minors are M_12 = 1, M_13 = a, M_14 = b, M_23 = c, M_24 = d,
M_34 = ad - bc. Positivity is therefore the cell

    Gr+(2, 4) = {(a, b, c, d) in R_+^4 : ad - bc > 0},

a 4-dimensional convex cone (ad - bc > 0 is an open convex condition in
log-coordinates). Through the dictionary of correspondence.py,

    s_ij = |M_ij|^2,

the positive cell maps to the region of kinematic space with all s_ij > 0
(the amplituhedron's positive kinematics), with s_12 = 1 fixing the scale.

The signed triple-grasp operator of a 4-valent vertex is built from the
Schwinger angular momenta J_i. With q = i[J_1.J_2, J_2.J_3], this module
reports the square-root-of-mean proxy

    V_proxy = (gamma * hbar)^{3/2} sqrt(|<q>|),

which differs from the expectation of a positive volume operator such as
<sqrt(|q|)>. Real planes have <q> = 0 by amplitude reality, including real
planes outside the positive cell. This does not imply q annihilates the
state or that positive quantum volume is zero.

Only numpy is used.
"""

import itertools

import numpy as np

from coherent_states import (
    GAMMA,
    expectation,
    plane_to_Z,
    perelomov_state,
    su2_ops,
)
from correspondence import kinematics_from_plane, scattering_invariants
from grassmannian import plane_to_plucker


def realify_plane(plane, tol=1e-9):
    """Find column phases that make all Plucker coordinates real.

    Column rescaling lambda_i -> e^{i theta_i} lambda_i rotates each minor
    by e^{i(theta_i + theta_j)}. The plane is gauge-real iff the phase
    system  theta_i + theta_j = -arg M_ij  (all pairs) is consistent; for
    a decomposable 2-plane this always holds, so consistency is a
    numerical check here (it would fail for non-rank-2 antisymmetric
    data).

    Returns
    -------
    real_plane : ndarray, shape (2, N), complex
        plane @ diag(e^{i theta}); all its minors are real up to tol.
    info : dict with 'minors_real', 'phase_residual', 'theta'.
    """
    plane = np.asarray(plane, dtype=complex)
    n = plane.shape[1]
    pairs, minors = plane_to_plucker(plane)
    M = dict(zip(pairs, minors))

    # Spanning-tree solve of theta_i + theta_j = -arg M_ij from vertex 0,
    # then mod-2pi consistency on all remaining pairs. (A naive least
    # squares solve of the angle equations fails because angles wrap:
    # theta_i + theta_j may differ from -angle(M_ij) by 2 pi k.)
    theta = np.zeros(n)
    for j in range(1, n):
        theta[j] = -np.angle(M[(0, j)])
    residuals = []
    for (i, j), m in zip(pairs, minors):
        rho = (np.angle(m) + theta[i] + theta[j] + np.pi) % (2 * np.pi) - np.pi
        residuals.append(rho)
    residuals = np.array(residuals)
    # The true solution differs from the tree guess by t_i with
    # rho_ij = -(t_i + t_j); this small system is consistent exactly when
    # the plane is gauge-real. Solve it and validate.
    A = np.zeros((len(pairs), n))
    for r, (i, j) in enumerate(pairs):
        A[r, i] = A[r, j] = 1.0
    t, _, _, _ = np.linalg.lstsq(A, -residuals, rcond=None)
    fit = A @ t + residuals
    fit = (fit + np.pi) % (2 * np.pi) - np.pi
    phase_residual = float(np.max(np.abs(fit)))
    theta = theta + t
    D = np.exp(1j * theta)
    real_plane = plane * D[np.newaxis, :]
    _, minors_re = plane_to_plucker(real_plane)
    info = {
        "minors_real": np.real(minors_re),
        "phase_residual": phase_residual,
        "theta": theta,
    }
    return real_plane, info


def _sign_consistent(signs, n, tol=1e-9):
    """Can vertex sign flips s_i = +-1 make s_i s_j sign(M_ij) = +1 for
    all pairs? Equivalent: every triangle has product of signs +1."""
    S = np.ones((n, n))
    for (i, j), m in signs:
        S[i, j] = S[j, i] = 1.0 if m > tol else (-1.0 if m < -tol else 0.0)
    if np.any(S == 0.0):
        return False
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if S[i, j] * S[j, k] * S[k, i] < 0:
                    return False
    return True


def is_positive_plane(plane, tol=1e-9, return_info=False):
    """Check whether a 2-plane lies in the top cell of the positive
    Grassmannian Gr+(2, N): do there exist gauge transformations
    (GL(2) left-multiplication and nonvanishing column rescalings) making
    every Plucker coordinate real and positive in the standard ordering?

    Test (necessary and sufficient for the top cell):
      1. all minors nonvanishing (strict cell point);
      2. the minor phases are gauged away by column phases
         (residual imaginary part ~ 0 after realify_plane);
      3. the realified minors have a consistent sign structure: vertex
         sign flips (negative real column rescalings) make them all equal,
         and a final overall sign flip makes them all positive.

    Returns
    -------
    positive : bool
    info : dict (if return_info) with 'real_plane', 'minors_real',
        'phase_residual'.
    """
    plane = np.asarray(plane, dtype=complex)
    n = plane.shape[1]
    pairs, minors = plane_to_plucker(plane)
    if np.any(np.abs(minors) < tol):
        return (False, {"reason": "vanishing minor"}) if return_info else False
    real_plane, info = realify_plane(plane)
    if info["phase_residual"] > tol:
        return (False, info) if return_info else False
    signs = list(zip(pairs, info["minors_real"]))
    positive = _sign_consistent(signs, n, tol)
    info["real_plane"] = real_plane
    if return_info:
        info["positive"] = positive
        return positive, info
    return positive


def canonical_gauge(plane, tol=1e-10):
    """Bring a Gr(2, N) plane to [I_2 | A] gauge using pivot columns (0,1).

    Requires the (0,1) minor to be nonvanishing (guaranteed for a
    strictly positive plane after realification). Column order is
    preserved.

    Returns
    -------
    gauge : ndarray, shape (2, N), complex
    pivot_minor : complex
    """
    plane = np.asarray(plane, dtype=complex)
    B = plane[:, :2]
    det = B[0, 0] * B[1, 1] - B[0, 1] * B[1, 0]
    if abs(det) < tol:
        raise ValueError("pivot minor M_12 vanishes; plane not in top cell")
    gauge = np.linalg.inv(B) @ plane
    gauge[np.abs(gauge) < tol] = 0.0
    return gauge, det


def positive_region_N4(a=None, b=None, c=None, d=None, seed=None):
    """Explicit parameterization of Gr+(2, 4).

    With no arguments returns the canonical form and a random interior
    point (via seed); with arguments returns the plane for the given
    positive parameters, requiring a, b, c, d > 0 and ad - bc > 0.

    Returns
    -------
    plane : ndarray, shape (2, 4)
    params : dict with the (a, b, c, d) parameters.
    """
    if a is None:
        rng = np.random.default_rng(seed)
        while True:
            x = rng.uniform(0.05, 3.0, size=4)
            if x[0] * x[3] > x[1] * x[2]:
                a, b, c, d = x
                break
    params = {"a": float(a), "b": float(b), "c": float(c), "d": float(d)}
    if min(a, b, c, d) <= 0:
        raise ValueError("Gr+(2,4) parameters must be positive")
    if a * d - b * c <= 0:
        raise ValueError("Gr+(2,4) requires ad - bc > 0")
    plane = np.array(
        [[1.0, 0.0, -c, -d],
         [0.0, 1.0, a, b]],
        dtype=float,
    )
    return plane, params


def kinematics_from_positive_plane(plane):
    """Extract kinematics from a positive plane and check s_ij > 0.

    On the real section p_i = lambda_i conj(lambda_i) all momenta are
    future-directed null; the Mandelstam invariants are s_ij = |M_ij|^2
    and are strictly positive iff the plane is strictly positive. Note:
    momentum conservation sum_i p_i = 0 cannot hold on the real section
    (it is a sum of positive-energy null vectors), so this returns the
    positive-region kinematics without imposing conservation — the
    amplituhedron's external data live in exactly such a positive
    momentum-twistor space.

    Returns
    -------
    dict with 'lambdas', 'momenta', 'pairs', 's', 'all_positive',
    'energies'.
    """
    positive, info = is_positive_plane(plane, return_info=True)
    if not positive:
        raise ValueError("plane is not in the top cell of Gr+(2, N)")
    gauge, _ = canonical_gauge(info["real_plane"])
    lambdas, momenta = kinematics_from_plane(gauge)
    pairs, s = scattering_invariants(momenta)
    return {
        "lambdas": lambdas,
        "momenta": momenta,
        "pairs": pairs,
        "s": s,
        "all_positive": positive and bool(np.all(s > 0)),
        "energies": momenta[:, 0],
    }


def _dot_ops(Ji, Jj):
    """J_i . J_j = Jz_i Jz_j + (1/2)(J+_i J-_j + J-_i J+_j) as an
    occupation-space operator built from single-edge su(2) actions."""
    from coherent_states import _combine

    def zizj(occ):
        out = []
        for o1, f1 in Ji["z"](occ):
            for o2, f2 in Jj["z"](o1):
                out.append((o2, f1 * f2))
        return out

    def hPiMj(occ):  # (1/2) J+_i J-_j
        return [(o, 0.5 * f) for o, f in _combine(Jj["minus"], Ji["plus"], occ)]

    def hMiPj(occ):  # (1/2) J-_i J+_j
        return [(o, 0.5 * f) for o, f in _combine(Jj["plus"], Ji["minus"], occ)]

    def op(occ):
        out = {}
        for o, f in zizj(occ) + hPiMj(occ) + hMiPj(occ):
            out[o] = out.get(o, 0.0) + f
        return list(out.items())

    return op


def volume_operator(state, space, gamma=GAMMA, hbar=1.0, triple=(0, 1, 2)):
    """Signed-mean triple-grasp proxy of an n-valent coherent state.

    Uses the De Pietri / Rovelli-Smolin commutator on a triple of edges
    (i, j, k): q = i[J_i.J_j, J_j.J_k],
    V_proxy = (gamma*hbar)^{3/2} sqrt(|<q>|).

    For a 4-valent vertex there is a single independent triple up to
    symmetry (the default (0, 1, 2)); for n > 4 several inequivalent
    triples exist. This function does not combine them into a positive
    full-vertex volume operator.

    Note the two exact zero mechanisms (see module discussion):
    * all-a/b references freeze the spins and give <q> = 0;
    * real planes give real amplitudes and <q> = 0 for ANY triple.

    Returns
    -------
    V_proxy : float
    q_expectation : complex
    """
    if space.N < 3:
        raise ValueError("volume needs at least a 3-valent vertex")
    # The U(N) exponential conserves N_a and N_b separately, so a reference
    # containing only a-bosons (N_b = 0) freezes every spin along +z and
    # the chiral commutator has zero expectation. A reference with both
    # oscillator types (a genuine spin-network vertex occupation) is needed.
    i, j, k = triple
    J = [su2_ops(e) for e in range(space.N)]
    J12, J23 = _dot_ops(J[i], J[j]), _dot_ops(J[j], J[k])

    # q = i [J12, J23]; expectation on the state.
    vec = space.vec(state)
    v12 = space.apply(J12, vec)
    v23 = space.apply(J23, vec)
    q12_23 = 1j * (space.apply(J12, v23) - space.apply(J23, v12))
    q_exp = complex(vec.conj() @ q12_23)
    V = (gamma * hbar) ** 1.5 * float(np.sqrt(abs(q_exp)))
    return V, q_exp


def _q_action(triple):
    """Return the action of q_ijk = i[J_i.J_j, J_j.J_k] on one occupation."""
    i, j, k = triple
    Ji, Jj, Jk = su2_ops(i), su2_ops(j), su2_ops(k)
    A, B = _dot_ops(Ji, Jj), _dot_ops(Jj, Jk)

    def compose(left, right, occ):
        out = {}
        for mid, f1 in right(occ):
            for final, f2 in left(mid):
                out[final] = out.get(final, 0.0) + f1 * f2
        return out

    def q(occ):
        ab, ba = compose(A, B, occ), compose(B, A, occ)
        return [(o, 1j * (ab.get(o, 0.0) - ba.get(o, 0.0)))
                for o in (ab.keys() | ba.keys())]
    return q


def _active_vertex_blocks(space, state):
    """Group basis states by edge spins and total magnetic sector."""
    vec = space.vec(state)
    keys = []
    for occ in space.occupations:
        edge_spins = tuple(int(occ[2 * e] + occ[2 * e + 1])
                           for e in range(space.N))
        total_a = int(sum(occ[::2]))
        keys.append((edge_spins, total_a))
    active = {keys[i] for i in np.flatnonzero(np.abs(vec) > 1e-14)}
    blocks = []
    for key in sorted(active):
        indices = [i for i, k in enumerate(keys) if k == key]
        if len(indices) > 512:
            raise ValueError(
                f"active fixed-spin block has dimension {len(indices)}; "
                "exact dense volume evaluation is capped at 512"
            )
        basis = [tuple(int(x) for x in space.occupations[i]) for i in indices]
        blocks.append((basis, vec[indices]))
    return blocks


def _triple_matrix_block(space, basis, triple):
    action = _q_action(triple)
    index = {occ: i for i, occ in enumerate(basis)}
    matrix = np.zeros((len(basis), len(basis)), dtype=complex)
    for col, occ in enumerate(basis):
        for out, value in action(occ):
            row = index.get(tuple(out))
            if row is None:
                if abs(value) > 1e-12:
                    raise ValueError("triple grasp left its fixed-spin sector")
                continue
            matrix[row, col] += value
    # Catch convention or assembly errors before applying spectral functions.
    if not np.allclose(matrix, matrix.conj().T, atol=2e-11, rtol=0.0):
        raise ValueError("triple-grasp matrix is not Hermitian")
    return matrix


def _positive_sqrt_expectation(matrix, vector):
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    weights = np.abs(eigenvectors.conj().T @ vector) ** 2
    return float(np.dot(weights, np.sqrt(np.abs(eigenvalues))))


def rovelli_smolin_volume(state, space, gamma=GAMMA, hbar=1.0, scale=None):
    """Exact dense-sector expectation of the Rovelli–Smolin vertex volume.

    In the repository normalization, V_RS = scale * sum_{i<j<k}
    sqrt(|q_ijk|), where q_ijk = i[J_i.J_j, J_j.J_k]. `scale` defaults to
    (gamma*hbar)**1.5; pass an explicit convention-dependent prefactor when
    comparing with a different normalization. Dense diagonalization is used
    separately in the invariant edge-spin/magnetic blocks populated by state.
    """
    prefactor = (gamma * hbar) ** 1.5 if scale is None else float(scale)
    state_norm2 = float(np.vdot(space.vec(state), space.vec(state)).real)
    if state_norm2 <= 0:
        raise ValueError("volume expectation requires a nonzero state")
    blocks = _active_vertex_blocks(space, state)
    total = 0.0
    for basis, vector in blocks:
        for triple in itertools.combinations(range(space.N), 3):
            qmat = _triple_matrix_block(space, basis, triple)
            total += _positive_sqrt_expectation(qmat, vector)
    return prefactor * total / state_norm2


def ashtekar_lewandowski_volume(state, space, orientation_signs,
                                gamma=GAMMA, hbar=1.0, scale=None):
    """Exact dense-sector expectation of the Ashtekar–Lewandowski volume.

    `orientation_signs` maps each lexicographically ordered edge triple to
    its tangent determinant sign (-1, 0, +1). The vertex operator is the
    positive square root of the absolute value of their signed q-sum.
    """
    prefactor = (gamma * hbar) ** 1.5 if scale is None else float(scale)
    state_vec = space.vec(state)
    state_norm2 = float(np.vdot(state_vec, state_vec).real)
    if state_norm2 <= 0:
        raise ValueError("volume expectation requires a nonzero state")
    triples = list(itertools.combinations(range(space.N), 3))
    if set(orientation_signs) != set(triples):
        raise ValueError("orientation_signs must define every edge triple")
    if any(sign not in (-1, 0, 1) for sign in orientation_signs.values()):
        raise ValueError("orientation signs must be -1, 0, or +1")
    total = 0.0
    for basis, vector in _active_vertex_blocks(space, state):
        qsum = np.zeros((len(basis), len(basis)), dtype=complex)
        for triple in triples:
            sign = orientation_signs[triple]
            if sign:
                qsum += sign * _triple_matrix_block(space, basis, triple)
        if not np.allclose(qsum, qsum.conj().T, atol=3e-11, rtol=0.0):
            raise ValueError("Ashtekar–Lewandowski vertex operator is not Hermitian")
        total += _positive_sqrt_expectation(qsum, vector)
    return prefactor * total / state_norm2


def volume_vs_s(a=None, b=None, c=None, d=None, ref_occupations=None,
                scales=None, verbose=True):
    """Relate the signed-mean proxy of the 4-valent vertex to the scattering
    invariant s on Gr+(2, 4).

    Two regimes are scanned and compared:

    * ON Gr+: with the canonical positive plane, the Perelomov state has
      real amplitudes (Z real antisymmetric for real planes) and the
      signed mean vanishes identically, so the proxy is zero at every scale.

    * OFF Gr+: adding a fixed complex perturbation dC (violating the
      minor-phase cocycle, so the plane is genuinely complex) makes V
      nonzero for this perturbation. Scaling the plane, C -> sqrt(t) C, rescales s_ij -> t^2
      s_ij, but V is UNCHANGED: the momentum-map label Z is built from
      orthonormalized rows and is invariant under the global rescaling
      (GL(2) gauge). Hence there is no functional V(s) at fixed quantum
      occupation — the signed mean probes the complex shape of the plane,
      not its energy scale.

    Returns
    -------
    dict with keys 'positive' and 'complex', each containing 's', 'V',
    'exponent' (log-log slope of V vs s; 0 = scale-invariant).
    """
    if scales is None:
        scales = np.geomspace(0.25, 4.0, 7)
    if ref_occupations is None:
        # genuine vertex occupations: j = 1 on edges 0,1 and j = 1/2 on
        # edges 2,3 (both oscillator types present)
        ref_occupations = np.array([[1, 1], [1, 1], [1, 0], [1, 0]])
    k = int(np.sum(ref_occupations))
    plane0, params = positive_region_N4(a, b, c, d)
    # fixed complex perturbation with a nontrivial minor-phase cocycle
    dC = np.array([[0, 0, 0.3j, 0.2j], [0, 0, -0.5, 0.3j]])
    complex0 = plane0 + dC

    out = {}
    for label, base in (("positive", plane0), ("complex", complex0)):
        s_list, v_list = [], []
        for t in scales:
            plane = np.sqrt(t) * base
            _, minors = plane_to_plucker(plane)
            s12 = abs(minors[0]) ** 2  # s_12 = |M_12|^2 (exact dictionary)
            Z = plane_to_Z(plane)
            state, space = perelomov_state(
                Z, k_max=k, ref_occupations=ref_occupations
            )
            V, q = volume_operator(state, space)
            s_list.append(s12)
            v_list.append(V)
            if verbose:
                print(f"  {label:8s} t={t:5.2f}  s12={s12:8.4f}  "
                      f"V/(gamma*hbar)^1.5={V / GAMMA ** 1.5:10.6f}   "
                      f"<q>={q.real:+.6f}")
        s_arr, v_arr = np.array(s_list), np.array(v_list)
        exponent = float(np.polyfit(np.log(s_arr), np.log(v_arr), 1)[0])
        if verbose:
            print(f"  {label:8s} log-log exponent of V vs s: {exponent:.3f}")
        out[label] = {"s": s_arr, "V": v_arr, "exponent": exponent}
    out["params"] = params
    return out


def positive_plane_curve(N, seed=None, t_min=0.2, t_max=3.0):
    """Random positive plane in Gr+(2, N) from a convex polygon.

    Columns lambda_i = (t_i, t_i^2) with 0 < t_1 < ... < t_N give minors

        M_ij = t_i t_j (t_j - t_i) > 0   for i < j,

    so the plane is strictly positive (points on a parabola are vertices
    of a strictly convex polygon; this is the standard moment-curve
    construction of the top cell). Returns the real positive plane.
    """
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(t_min, t_max, size=N))
    return np.stack([t, t * t])


def spin_vectors(state, space):
    """Expectation values <J_i^a>, a = x, y, z, for every edge.

    Returns ndarray of shape (N, 3). Because the U(N) exponential
    conserves N_a and N_b separately, <J_i^+> = <J_i^-> = 0 identically:
    every vector lies exactly on the z axis (collinear, hence coplanar).
    """
    from coherent_states import expectation as _exp

    def jx(e):
        J = su2_ops(e)
        return lambda occ: ([(o, 0.5 * f) for o, f in J["plus"](occ)]
                            + [(o, 0.5 * f) for o, f in J["minus"](occ)])

    def jy(e):
        J = su2_ops(e)
        return lambda occ: ([(o, 0.5 / 1j * f) for o, f in J["plus"](occ)]
                            + [(o, -0.5 / 1j * f) for o, f in J["minus"](occ)])

    out = []
    for e in range(space.N):
        out.append([
            _exp(state, jx(e), space).real,
            _exp(state, jy(e), space).real,
            _exp(state, su2_ops(e)["z"], space).real,
        ])
    return np.array(out)


def coplanarity(normals):
    """Max over triples of |det[n_i, n_j, n_k]| for unit normals.

    0 = all normals coplanar (or collinear); 1 = maximally non-coplanar.
    """
    n = np.asarray(normals, dtype=float)
    norms = np.linalg.norm(n, axis=1)
    n = n / np.where(norms[:, None] == 0, 1.0, norms[:, None])
    worst = 0.0
    for i in range(len(n)):
        for j in range(i + 1, len(n)):
            for k in range(j + 1, len(n)):
                worst = max(worst, abs(float(np.linalg.det(
                    np.stack([n[i], n[j], n[k]])))))
    return worst


def vertex_reference(N, triple=(0, 1, 2)):
    """Reference occupation for an n-valent volume probe: one a-boson on
    every edge, plus one b-boson on the volume triple (K = N + 3).

    The b-bosons must sit on the triple's edges (the all-a mechanism
    freezes the chiral commutator otherwise). Keeping K = N + 3 leaves
    the Fock space small enough for n = 5, 6.
    """
    ref = np.zeros((N, 2), dtype=int)
    ref[:, 0] = 1
    ref[list(triple), 1] = 1
    return ref


def volume_vs_perturbation(N, epsilons=None, ref_occupations=None,
                           triple=(0, 1, 2), seed=0, verbose=True):
    """Signed-mean proxy response to a complex perturbation of a positive plane.

    Starts from a random real positive plane C0 in Gr+(2, N) and adds a
    fixed random imaginary perturbation scaled by epsilon:

        C(eps) = C0 + i * eps * dC,    dC real, generic.

    For eps = 0 the plane is real and <q> vanishes by amplitude reality.
    The fit measures the response for this chosen perturbation and reference;
    it does not identify the positive cell as the full zero locus.

    Returns
    -------
    dict with 'epsilon', 'V', 'q', 'coplanarity', 'exponent'
    (log-log slope of V vs eps), and 'V_on_positive'.
    """
    if epsilons is None:
        epsilons = np.geomspace(1e-4, 1.0, 5)
    if ref_occupations is None:
        ref_occupations = vertex_reference(N, triple)
    k = int(np.sum(ref_occupations))
    C0 = positive_plane_curve(N, seed=seed)
    rng = np.random.default_rng(seed + 1)
    dC = rng.normal(size=(2, N))
    # make sure the perturbation genuinely violates the phase cocycle
    assert not is_positive_plane(C0 + 1j * 0.5 * dC / np.abs(dC).max())

    eps_list, v_list, q_list, cop_list = [], [], [], []
    V0 = None
    for eps in epsilons:
        C = C0 + 1j * eps * dC
        Z = plane_to_Z(C)
        state, space = perelomov_state(Z, k_max=k,
                                       ref_occupations=ref_occupations)
        V, q = volume_operator(state, space, triple=triple)
        cop = coplanarity(spin_vectors(state, space))
        if eps == epsilons[0]:
            V0 = V
        eps_list.append(float(eps))
        v_list.append(V)
        q_list.append(q.real)
        cop_list.append(cop)
        if verbose:
            print(f"  N={N} eps={eps:8.4f}  V/(gamma*hbar)^1.5="
                  f"{V / GAMMA ** 1.5:10.6f}  <q>={q.real:+.6f}  "
                  f"max|det normals|={cop:.3e}")
    eps_arr, v_arr = np.array(eps_list), np.array(v_list)
    exponent = float(np.polyfit(np.log(eps_arr), np.log(v_arr), 1)[0])
    if verbose:
        print(f"  N={N}: V ~ eps^{exponent:.3f} (linear <q> predicts 0.5); "
              f"V(eps=0 limit) = {V0 / GAMMA ** 1.5:.2e}")
    return {
        "epsilon": eps_arr,
        "V": v_arr,
        "q": np.array(q_list),
        "coplanarity": np.array(cop_list),
        "exponent": exponent,
    }


def example_higher_n(N, seed=0, verbose=True):
    """Higher-n positivity/proxy summary for one random Gr+(2, N) plane.

    Checks, for a random positive plane: (a) positivity accepted; (b) all
    face normals (spin expectation vectors) are collinear on the z axis,
    hence coplanar; (c) the signed mean on the real plane vanishes for
    every triple; (d) the chosen complex perturbation gives nonzero mean.
    """
    C0 = positive_plane_curve(N, seed=seed)
    ok, _ = is_positive_plane(C0, return_info=True)
    triples = [(0, 1, 2)] + ([(0, 1, N - 1)] if N > 4 else [])
    ref = vertex_reference(N, triple=(0, 1, 2))
    k = int(ref.sum())
    state, space = perelomov_state(plane_to_Z(C0), k_max=k,
                                   ref_occupations=ref)
    normals = spin_vectors(state, space)
    cop = coplanarity(normals)
    volumes = {}
    for triple in triples:
        V, q = volume_operator(state, space, triple=triple)
        volumes[triple] = V
    if verbose:
        print(f"N={N}: positive={ok}, max|det normals|={cop:.3e}, "
              f"<J_i> z-components={np.round(normals[:, 2], 3)}")
        for triple, V in volumes.items():
            print(f"     triple {triple}: V/(gamma*hbar)^1.5 = "
                  f"{V / GAMMA ** 1.5:.3e}")
    return {
        "positive": ok,
        "coplanarity": cop,
        "normals": normals,
        "volumes": volumes,
        "state": state,
        "space": space,
        "plane": C0,
    }


def _test_higher_n():
    print("\n=== Higher-n positivity and volume (n = 5, 6) ===")
    results = {}
    for N in (5, 6):
        res = example_higher_n(N, seed=42 + N)
        results[N] = res
        assert res["positive"], "moment-curve plane must be positive"
        assert res["coplanarity"] < 1e-12, "normals must stay z-aligned"
        assert all(V < 1e-8 for V in res["volumes"].values()), \
            "signed-mean proxy must vanish on these real planes"
        scan = volume_vs_perturbation(N, seed=42 + N)
        results[N]["scan"] = scan
        assert 0.25 < scan["exponent"] < 0.9, scan["exponent"]
        assert np.all(np.diff(scan["V"]) > -1e-12), "V must grow with eps"
        assert np.all(scan["coplanarity"] < 1e-12), \
            "normals remain collinear even off Gr+"
    print("\nHigher-n tests passed: V = 0 on Gr+(2, n) for n = 5, 6 "
          "(any triple), V ~ eps^{1/2} off it, normals always collinear.")
    return results


def _test():
    # 1. Positive planes are detected; non-positive planes are rejected.
    plane, params = positive_region_N4(1.0, 2.0, 0.5, 1.5)
    ok, info = is_positive_plane(plane, return_info=True)
    assert ok, info
    minors = info["minors_real"]
    assert np.all(minors > 0)
    rng = np.random.default_rng(3)
    n_pos = 0
    for _ in range(50):
        pl = rng.normal(size=(2, 4)) + 1j * rng.normal(size=(2, 4))
        if is_positive_plane(pl):
            n_pos += 1
    print(f"positivity check: canonical positive plane accepted; "
          f"{n_pos}/50 generic complex planes (expected ~0) accepted")

    # Gauge invariance: multiply by random GL(2) and column phases/rescalings.
    pl = plane.copy()
    g = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    d = np.exp(1j * rng.uniform(0, 2 * np.pi, size=4)) * rng.uniform(0.1, 3, size=4)
    pl_gauged = g @ pl * d[np.newaxis, :]
    ok_g, info_g = is_positive_plane(pl_gauged, return_info=True)
    assert ok_g, "positivity must be gauge-invariant"
    print("positivity check: invariant under GL(2) and column rescalings")

    # 2. Boundary of the cell: ad - bc = 0 is rejected.
    pl = np.array([[1.0, 0, -1.0, -1.0], [0.0, 1.0, 1.0, 1.0]])
    assert not is_positive_plane(pl)
    print("positivity check: cell boundary ad-bc=0 correctly rejected")

    # 3. Kinematics from positive planes: all s_ij > 0.
    kin = kinematics_from_positive_plane(plane)
    assert kin["all_positive"] and np.all(kin["s"] > 0)
    print(f"positive kinematics: s_ij = {[f'{s:.3f}' for s in kin['s']]}, "
          f"all > 0: True; energies = {[f'{e:.3f}' for e in kin['energies']]}")
    # s = |M|^2 cross-check
    _, minors = plane_to_plucker(plane)
    assert np.max(np.abs(kin["s"] - np.abs(minors) ** 2)) < 1e-12

    # 4. Signed-mean proxy: zero for real planes (including one outside the
    #    positive cell) by amplitude reality, and zero for the all-a control.
    ref_vertex = np.array([[1, 1], [1, 1], [1, 0], [1, 0]])
    state, space = perelomov_state(
        plane_to_Z(plane), k_max=6, ref_occupations=ref_vertex
    )
    V, q = volume_operator(state, space)
    print(f"signed-mean proxy (positive plane, vertex reference): "
          f"V/(gamma*hbar)^1.5 = {V / GAMMA ** 1.5:.3e} (zero)")
    assert V < 1e-8

    real_off_cell = np.array([[1.0, 0.0, -2.0, -1.0],
                              [0.0, 1.0, 1.0, 1.0]])
    assert not is_positive_plane(real_off_cell)
    state_r, space_r = perelomov_state(
        plane_to_Z(real_off_cell), k_max=6, ref_occupations=ref_vertex
    )
    V_r, q_r = volume_operator(state_r, space_r)
    assert abs(q_r) < 1e-12 and V_r < 1e-8

    dC = np.array([[0, 0, 0.3j, 0.2j], [0, 0, -0.5, 0.3j]])
    state_c, space_c = perelomov_state(
        plane_to_Z(plane + dC), k_max=6, ref_occupations=ref_vertex
    )
    V_c, q_c = volume_operator(state_c, space_c)
    print(f"signed-mean proxy (complex plane, vertex reference): "
          f"V/(gamma*hbar)^1.5 = {V_c / GAMMA ** 1.5:.6f} (nonzero)")
    assert V_c > 1e-6

    state_a, space_a = perelomov_state(
        plane_to_Z(plane + dC), k_max=3,
        ref_occupations=np.array([[3, 0], [0, 0], [0, 0], [0, 0]]),
    )
    V_a, _ = volume_operator(state_a, space_a)
    print(f"signed-mean proxy (complex plane, all-a reference): V = {V_a:.6f} "
          f"(zero by the N_b = 0 spin-freezing mechanism)")
    assert V_a == 0.0

    # 5. Volume vs s: vanishes on Gr+; scale-invariant off Gr+.
    print("\nvolume_vs_s scan (fixed shape, scaled plane):")
    out = volume_vs_s(1.0, 2.0, 0.5, 1.5)
    assert np.all(out["positive"]["V"] < 1e-8), "V must vanish on Gr+"
    assert abs(out["complex"]["exponent"]) < 0.05, \
        "V must be scale-invariant (exponent 0), got " \
        f"{out['complex']['exponent']}"
    assert np.all(out["complex"]["V"] > 1e-6), "proxy expected nonzero for this perturbation"

    print("\nAll positivity.py tests passed.")


if __name__ == "__main__":
    _test()
    _test_higher_n()

"""Kinematic polyhedron via all-incoming Minkowski (T5a' / T6-kinematic).

Reversed construction (the plane's own column-momenta generically do NOT
close under any sign assignment, so momenta come first):

1. generate physical on-shell massless kinematics with exact conservation
   (2->2 for n=4, 2->3 for n=5, CM frame) for a chosen channel, i.e. the
   in/out assignment (eps_i = +1 incoming, -1 outgoing);
2. map to spinors -> real plane C0 (on-cell up to gauge phases);
3. kinematic polyhedron from (A_i = E_i, n_i = eps_i pvec_i / E_i), which
   closes exactly: sum A_i n_i = sum eps_i pvec_i = 0;
4. reconstruct the convex polytope (support numbers via least-squares on
   facet areas through halfspace intersection) and read off adjacency:
   facets sharing an edge; local triples = triples meeting at a vertex.

Only numpy/scipy used.
"""

import itertools

import numpy as np
from scipy.optimize import least_squares


def gen_kinematics_2to2(rng, E=1.0):
    """2->2 massless scattering in CM: returns (momenta (4,4), eps (4,)).
    Channel s: legs 0,1 incoming; 2,3 outgoing. Outgoing pair at random
    direction (uniform cos theta, uniform phi)."""
    c = rng.uniform(-1.0, 1.0)
    phi = rng.uniform(0.0, 2 * np.pi)
    s = np.sqrt(max(0.0, 1.0 - c * c))
    d = np.array([s * np.cos(phi), s * np.sin(phi), c])
    p = np.zeros((4, 4))
    p[0] = [E, 0, 0, E]
    p[1] = [E, 0, 0, -E]
    p[2] = [E, E * d[0], E * d[1], E * d[2]]
    p[3] = [E, -E * d[0], -E * d[1], -E * d[2]]
    return p, np.array([1.0, 1.0, -1.0, -1.0])


def permute_channel_2to2(p, channel):
    """Reassign which legs are incoming/outgoing. channel in 's','t','u':
    s: 01->23, t: 02->13, u: 03->12. Momenta rows stay put; only eps moves
    (the polyhedron is built from (eps, p), so this changes its shape)."""
    eps = np.ones(4)
    pairs = {"s": (0, 1), "t": (0, 2), "u": (0, 3)}[channel]
    eps[list(pairs)] = 1.0
    mask = np.ones(4, bool)
    mask[list(pairs)] = False
    eps[mask] = -1.0
    return p, eps


def gen_kinematics_2to3(rng, E=1.0, incoming=(0, 1)):
    """2->3 massless in CM (total P=(2E,0,0,0)). Outgoing energies from
    Dirichlet(1,1,1)*2E; directions from the momentum-triangle constraint
    (rejection-sample triangle inequalities), then a random rotation."""
    while True:
        Eo = rng.dirichlet([1.0, 1.0, 1.0]) * 2 * E
        E3, E4, E5 = Eo
        cos_t = (E5 * E5 - E3 * E3 - E4 * E4) / (2 * E3 * E4)
        if abs(cos_t) <= 1.0:
            break
    s = np.sqrt(max(0.0, 1.0 - cos_t * cos_t))
    v3 = np.array([0.0, 0.0, E3])
    v4 = np.array([E4 * s, 0.0, E4 * cos_t])
    v5 = -(v3 + v4)
    assert abs(np.linalg.norm(v5) - E5) < 1e-9
    # random rotation
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    if np.linalg.det(q) < 0:
        q[:, 0] = -q[:, 0]
    v3, v4, v5 = q @ v3, q @ v4, q @ v5
    p = np.zeros((5, 4))
    p[0] = [E, 0, 0, E]
    p[1] = [E, 0, 0, -E]
    p[2] = [E3, *v3]
    p[3] = [E4, *v4]
    p[4] = [E5, *v5]
    eps = -np.ones(5)
    eps[list(incoming)] = 1.0
    return p, eps


def minkowski_data(momenta, eps):
    """(A_i, n_i) with A_i = E_i, n_i = eps_i pvec_i / E_i. Returns areas,
    normals, closure residual |sum A_i n_i|."""
    E = momenta[:, 0]
    assert np.all(E > 0)
    n = (eps[:, None] * momenta[:, 1:]) / E[:, None]
    assert np.allclose(np.linalg.norm(n, axis=1), 1.0)
    residual = float(np.linalg.norm((E[:, None] * n).sum(axis=0)))
    return E.copy(), n, residual


def _triple_vertices(normals, h, feas_tol=1e-9):
    """Candidate vertices of P(h) = {x : n_i.x <= h_i}: for every triple
    of independent facet normals, the triple-plane intersection point,
    kept iff it satisfies all halfspaces. Crash-free for any h (unlike
    qhull halfspace intersection, which fails on unbounded/symmetric
    intermediate guesses). Returns (vertices (m,3), incident (m,n) bool)."""
    normals = np.asarray(normals, float)
    h = np.asarray(h, float)
    n = len(normals)
    verts, inc = [], []
    for (i, j, k) in itertools.combinations(range(n), 3):
        N = normals[[i, j, k]]
        if abs(np.linalg.det(N)) < 1e-10:
            continue
        v = np.linalg.solve(N, h[[i, j, k]])
        if np.all(normals @ v <= h + feas_tol):
            verts.append(v)
            inc.append(np.abs(normals @ v - h) < 1e-7)
    if not verts:
        return np.zeros((0, 3)), np.zeros((0, n), bool)
    verts = np.array(verts)
    inc = np.array(inc)
    # dedupe concurrent vertices (4+ planes through one point)
    keep = np.ones(len(verts), bool)
    for a in range(len(verts)):
        if not keep[a]:
            continue
        for b in range(a + 1, len(verts)):
            if np.linalg.norm(verts[a] - verts[b]) < 1e-7:
                keep[b] = False
                inc[a] = inc[a] | inc[b]
    return verts[keep], inc[keep]


def _facet_areas(normals, h):
    """Facet areas of P(h) from triple-intersection vertices: per facet,
    order incident vertices angularly in the facet plane, shoelace."""
    normals = np.asarray(normals, float)
    verts, inc = _triple_vertices(normals, h)
    areas = np.zeros(len(normals))
    for i, ni in enumerate(normals):
        pts = verts[inc[:, i]]
        if len(pts) < 3:
            continue
        e1 = pts[1] - pts[0]
        e1 = e1 / np.linalg.norm(e1)
        e2 = np.cross(ni, e1)
        e2 = e2 / np.linalg.norm(e2)
        xy = np.stack([pts @ e1, pts @ e2], axis=1)
        c = xy.mean(axis=0)
        ang = np.arctan2(xy[:, 1] - c[1], xy[:, 0] - c[0])
        xy = xy[np.argsort(ang)]
        areas[i] = 0.5 * abs(float(np.sum(
            xy[:, 0] * np.roll(xy[:, 1], -1)
            - np.roll(xy[:, 0], -1) * xy[:, 1])))
    return areas


def reconstruct(normals, areas, tol=1e-6):
    """Solve support numbers h with facet areas == areas. Returns (h,
    max area residual). Tiny Tikhonov on (h-1) fixes the 3 translation
    flat directions without biasing areas (checked via the residual)."""
    normals = np.asarray(normals, float)
    areas = np.asarray(areas, float)
    n = len(areas)

    def fun(h):
        # No positivity guard: the algebraic area map is well-defined for
        # any h, and the min-norm solution may translate the origin just
        # outside one facet (one slightly negative support number).
        # Adjacency read off at the end is translation-invariant.
        pred = _facet_areas(normals, h)
        return np.append(pred - areas, 1e-6 * (h - 1.0))

    sol = least_squares(fun, np.sqrt(areas / areas.mean()),
                        xtol=1e-10, ftol=1e-10,
                        gtol=1e-10, max_nfev=500)
    h = sol.x
    resid = float(np.max(np.abs(_facet_areas(normals, h) - areas)))
    assert resid < tol, f"area residual {resid:.2e} exceeds {tol:.0e}"
    return h, resid


def adjacency(normals, h):
    """Local triples: sets of 3 facets meeting at a vertex of P(h),
    from the triple-intersection vertices. Returns (local_triples
    sorted list, n_vertices)."""
    _, inc = _triple_vertices(np.asarray(normals, float),
                              np.asarray(h, float), feas_tol=1e-7)
    local = set()
    for row in inc:
        idx = tuple(int(i) for i in np.nonzero(row)[0])
        if len(idx) >= 3:
            for t in itertools.combinations(idx, 3):
                local.add(t)
    return sorted(local), len(inc)



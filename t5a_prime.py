"""T5a': kinematic-polyhedron local chirality (child of T5a M-sweep).

Reversed construction (plane column-momenta generically do not close, so
kinematics come first):

  per (n, channel, plane seed):
  1. generate physical on-shell massless kinematics with EXACT conservation
     (2->2 CM for n=4; 2->3 CM for n=5) for the channel's in/out assignment;
  2. spinors -> plane C0 (generically off-cell already; column phases
     cannot realify it -- the minor-phase cocycle is gauge-invariant),
     state measured on C = C0 + fixed dC (floor on off-cell distance);
     engine validated by an explicit-commutator red-team check;
  3. kinematic polyhedron from all-incoming Minkowski (A_i = E_i,
     n_i = eps_i pvec_i / E_i) -> adjacency FROZEN before looking at q;
  4. quantum state from C = C0 + i*dC with FIXED dC (same row-1 pattern as
     the T5a sweep), M = 0 reference (sector fixed to isolate adjacency);
  5. q_ijk on all triples; sign-agreement + net chi_V on ALL vs LOCAL.

n=4: CM 2->2 normals are planar (rank 2) -> no 3D polyhedron exists, and
tetrahedron combinatorics would make local == all triples anyway. The n=4
arm therefore reports the all-triples verdict per channel (s/t/u) to test
channel-(in)dependence. Genuine subsetting needs n >= 5.
n=5: all C(5,2) = 10 incoming pairs; rows keep fixed identity, reference
fixed, so each pair gives a different parallel-facet pair / local set.

Only numpy/scipy used. Reuses the T5a fixed-K engine (t5a_mag_sweep) and
grassmannian spinor map.
"""

import itertools
import json
import time

import numpy as np

import minkowski as mk
import t5a_mag_sweep as m
from grassmannian import null_momentum_to_spinor, spinors_to_plane

N4, K4 = 4, 6
N5, K5 = 5, 8
REF4 = [(1, 1), (1, 1), (1, 0), (1, 0)]            # K=6, M=0 (Rust-test convention)
REF5 = [(1, 1), (1, 1), (1, 0), (1, 0), (0, 2)]    # K=8, M=0 spread
NPLANE4 = 20
NPLANE5 = 8
PAIRS5 = list(itertools.combinations(range(5), 2))  # 10 incoming pairs


def fixed_dC(n):
    """The T5a sweep's fixed imaginary perturbation (row-1 pattern)."""
    dC = np.zeros((2, n), dtype=complex)
    dC[1, :] = 1j * 0.35 * (np.arange(n) + 0.5)
    return dC


def plane_from_momenta(momenta):
    """2-plane with the spinor columns. NOTE: scattering-spinor planes
    are generically OFF-cell (their minor-phase cocycle is gauge- and
    GL(2)-invariant and nontrivial), so no realification is possible;
    the state is measured on C0 + fixed dC (floor on off-cell distance)
    while the polyhedron comes from the underlying conserved (eps, p)."""
    lambdas = np.array([null_momentum_to_spinor(p) for p in momenta])
    return spinors_to_plane(lambdas)


def relabel_incoming(p, eps, pair):
    """Put the incoming pair's momenta/eps into the pair's rows by
    permuting rows of a canonical (0,1)-incoming event. Canonical event
    has incoming in rows 0,1: permute rows so rows pair[0],pair[1] hold
    them, i.e. apply permutation sending (0,1) -> pair."""
    a, b = pair
    perm = list(range(len(p)))
    # build permutation with perm[0]=a, perm[1]=b (rows of new event =
    # old rows reordered): new[i] = old[inv[i]]; want new[a]=old[0],
    # new[b]=old[1].
    rest_old = [i for i in range(len(p)) if i not in (0, 1)]
    rest_new = [i for i in range(len(p)) if i not in (a, b)]
    new2old = {}
    new2old[a], new2old[b] = 0, 1
    for nn, oo in zip(rest_new, rest_old):
        new2old[nn] = oo
    order = [new2old[i] for i in range(len(p))]
    return p[order], eps[order]


def perelomov_converged(A, ref_idx, dim, tol=1e-13, cap=500):
    """Taylor exp(A)|ref>/norm with convergence REQUIRED (the inherited
    engine's fixed 2K+8 cap truncates at K=8: 24 terms vs ~40 needed --
    verified against dense expm; both legacy references share a 15-term
    truncation). Raises if the cap is hit."""
    v0 = np.zeros(dim, dtype=complex)
    v0[ref_idx] = 1.0
    result = v0.copy()
    term = v0.copy()
    for it in range(1, cap + 1):
        term = (A @ term) / it
        inc = float(np.linalg.norm(term))
        res = float(np.linalg.norm(result))
        result = result + term
        if inc < tol * max(1.0, res):
            return result / np.linalg.norm(result), it
    raise RuntimeError(f"Taylor did not converge in {cap} terms")


def measure(n, K, C, ref, edge_ops, pairs_cache):
    """q_ijk on all triples for state built from plane C."""
    occ, index = pairs_cache["basis"]
    A = m.build_A(occ, index, m.plane_to_z(C), n)
    flat = [x for pr in ref for x in pr]
    v, _ = perelomov_converged(A, m.idx_of(index, flat), len(occ))
    w = {ij: mat @ v for ij, mat in pairs_cache["jdot"].items()}
    triples = [(i, j, k) for i in range(n) for j in range(i + 1, n)
               for k in range(j + 1, n)]
    qs = []
    for (i, j, k) in triples:
        znum = complex(np.vdot(w[(i, j)], w[(j, k)]))
        qs.append(-2.0 * znum.imag)
    return triples, qs


def setup_engine(n, K):
    occ, index = m.build_fixed_k_basis(n, K)
    ops = m.single_edge_ops(occ, index, n)
    jdot = {}
    for i in range(n):
        for j in range(i + 1, n):
            jdot[(i, j)] = m.jdot(ops, i, j)
    return {"basis": (occ, index), "jdot": jdot, "ops": ops}


def sign_agree(qs, tol=1e-9):
    live = [q for q in qs if abs(q) > tol]
    if not live:
        return 0.0, 0, 0, len(qs)
    pos = sum(1 for q in live if q > 0)
    return max(pos, len(live) - pos) / len(live), pos, len(live) - pos, len(qs)


def main():
    t0 = time.time()
    rng = np.random.default_rng(20260919)
    DC4, DC5 = fixed_dC(4), fixed_dC(5)
    out = {"runs": []}

    for n, K, ref, cache in ((N4, K4, REF4, setup_engine(N4, K4)),
                             (N5, K5, REF5, setup_engine(N5, K5))):
        print(f"=== n={n} K={K} ref={ref} "
              f"basis dim={len(cache['basis'][0])} ===", flush=True)
        calib_done = False
        if n == 4:
            channels = ["s", "t", "u"]
        else:
            channels = [f"in{a}{b}" for (a, b) in PAIRS5]
        for ch in channels:
            agree_all, agree_loc, chi_all, chi_loc = [], [], [], []
            nloc_list, locsets = [], set()
            for s in range(NPLANE4 if n == 4 else NPLANE5):
                if n == 4:
                    p, _ = mk.gen_kinematics_2to2(rng)
                    p, eps = mk.permute_channel_2to2(p, ch)
                    local = None
                else:
                    p0, e0 = mk.gen_kinematics_2to3(rng)
                    a, b = PAIRS5[channels.index(ch)]
                    p, eps = relabel_incoming(p0, e0, (a, b))
                    A, nn, cres = mk.minkowski_data(p, eps)
                    assert cres < 1e-9, cres
                    h, ares = mk.reconstruct(nn, A)
                    local, _ = mk.adjacency(nn, h)
                    locsets.add(tuple(local))
                C0 = plane_from_momenta(p)
                dC = DC4 if n == 4 else DC5
                if not calib_done:
                    # red-team: explicit commutator on triple (0,1,2)
                    occ, index = cache["basis"]
                    A = m.build_A(occ, index, m.plane_to_z(C0 + dC), n)
                    flat = [x for pr in ref for x in pr]
                    v, nterms = perelomov_converged(
                        A, m.idx_of(index, flat), len(occ))
                    A01 = cache["jdot"][(0, 1)]
                    A12 = cache["jdot"][(1, 2)]
                    qm = 1j * (A01 @ A12 - A12 @ A01)
                    qe = complex(np.vdot(v, qm @ v))
                    w01, w12 = A01 @ v, A12 @ v
                    qi = -2.0 * complex(np.vdot(w01, w12)).imag
                    assert abs(qe.imag) < 1e-9, qe
                    assert abs(qe.real - qi) < 1e-9, (qe, qi)
                    print(f"  red-team: explicit {qe.real:.6e} vs "
                          f"identity {qi:.6e} (match) ", flush=True)
                    calib_done = True
                triples, qs = measure(n, K, C0 + dC, ref, None, cache)
                if max(abs(q) for q in qs) < 1e-9:
                    print(f"  plane {s}: too close to cell "
                          f"(max|q|={max(abs(q) for q in qs):.1e}), skipped",
                          flush=True)
                    continue
                ag, *_ = sign_agree(qs)
                agree_all.append(ag)
                chi_all.append(float(sum(qs)))
                if local is None:
                    agree_loc.append(float("nan"))
                    chi_loc.append(float("nan"))
                    nloc_list.append(len(triples))
                else:
                    idx = [triples.index(t) for t in local]
                    ql = [qs[i] for i in idx]
                    agl, *_ = sign_agree(ql)
                    agree_loc.append(agl)
                    chi_loc.append(float(sum(ql)))
                    nloc_list.append(len(local))
            rec = {"n": n, "channel": ch,
                   "n_planes": len(agree_all),
                   "mean_agree_all": float(np.mean(agree_all)),
                   "mean_agree_local": float(np.nanmean(agree_loc)),
                   "mean_chi_all": float(np.mean(np.abs(chi_all))),
                   "mean_chi_local": float(np.nanmean(np.abs(chi_loc))),
                   "mean_n_local": float(np.mean(nloc_list)),
                   "distinct_local_sets": [list(s) for s in locsets],
                   "agree_all": agree_all, "agree_local": agree_loc}
            out["runs"].append(rec)
            print(f"  {ch}: planes={len(agree_all)} "
                  f"agree_all={rec['mean_agree_all']:.3f} "
                  f"agree_local={rec['mean_agree_local']:.3f} "
                  f"n_local~{rec['mean_n_local']:.1f} "
                  f"sets={len(locsets)}", flush=True)

    with open("t5a_prime_results.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"TOTAL {time.time()-t0:.1f}s wrote t5a_prime_results.json",
          flush=True)
    print("SUMMARY " + json.dumps(
        [{k: r[k] for k in ("n", "channel", "mean_agree_all",
                            "mean_agree_local", "mean_n_local")}
         for r in out["runs"]]), flush=True)


if __name__ == "__main__":
    main()

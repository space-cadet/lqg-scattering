"""T5a magnetization sweep: fixed plane and n, vary reference magnetization M.

Fixes one complex (off-cell) plane on n=5 edges (moment-curve positive
plane, seed 1000, plus a fixed imaginary perturbation of the second row
that breaks the minor-phase cocycle -- the same construction as the T5a
driver) and sweeps the Perelomov reference occupation at fixed total
boson number K=8, i.e. magnetization M = (N_a - N_b)/2 in -4..+4,
including a spread-vs-concentrated b-boson control pair at M=0.

For every reference, computes q_ijk = i<[A_ij, A_jk]> on all C(n,3)
triples via q = -2 Im <A_ij psi | A_jk psi> (A_ij = J_i.J_j Schwinger),
then reports sign-agreement fraction, |q| stats, and Pearson correlation
of the |q| / signed-q triple-vectors against the M=0 spread baseline.

Probe (not established fact): handedness may emerge only at |M|>0,
i.e. sign-agreement -> 1 away from M=0.

Fixed-K Fock space with scipy.sparse; dim C(K+2n-1,2n-1) = C(17,9) =
24310 for n=5, K=8. Only numpy/scipy used.
"""

import itertools
import json
import time

import numpy as np
import scipy.sparse as sp

N = 5
K = 8
PLANE_SEED = 1000
TOL = 1e-13
NONZERO_TOL = 1e-9

# Reference occupations: (label, [(na, nb) x N]). All sum to K=8.
CONFIGS = [
    ("M=+4_all-a",      [(2, 0)] * 3 + [(1, 0)] * 2),
    ("M=+3",            [(2, 0), (2, 0), (1, 1), (1, 0), (1, 0)]),
    ("M=+2",            [(2, 0), (1, 1), (1, 1), (1, 0), (1, 0)]),
    ("M=+1",            [(1, 1), (1, 1), (1, 1), (1, 0), (1, 0)]),
    ("M=0_spread",      [(1, 1), (1, 1), (1, 0), (1, 0), (0, 2)]),
    ("M=0_concentrated",[(1, 0), (1, 0), (1, 0), (1, 0), (0, 4)]),
    ("M=-1",            [(1, 1), (1, 1), (1, 1), (0, 1), (0, 1)]),
    ("M=-2",            [(0, 2), (1, 1), (1, 1), (0, 1), (0, 1)]),
    ("M=-3",            [(0, 2), (0, 2), (1, 1), (0, 1), (0, 1)]),
    ("M=-4_all-b",      [(0, 2)] * 3 + [(0, 1)] * 2),
]


def build_fixed_k_basis(n, k):
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
    index = {bytes(o.astype(np.uint8).tobytes()): i for i, o in enumerate(occ)}
    return occ, index


def idx_of(index, state):
    return index[bytes(np.asarray(state, dtype=np.uint8).tobytes())]


def moment_curve_plane(n, seed):
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(0.2, 3.0, size=n))
    return np.stack([t, t * t]).astype(complex)


def fixed_complex_plane(n, seed):
    c0 = moment_curve_plane(n, seed)
    c = c0.copy()
    c[1, :] = c[1, :] + 1j * 0.35 * (np.arange(n) + 0.5)
    return c


def plane_to_z(plane):
    a, b = plane[0].copy(), plane[1].copy()
    a = a / np.linalg.norm(a)
    b = b - a * (a.conj() @ b)
    b = b / np.linalg.norm(b)
    return np.outer(a, b.conj()) - np.outer(b, a.conj())


def build_A(occ, index, z, n):
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
                    rows.append(idx_of(index, trow))
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
                    rows.append(idx_of(index, trow))
                    cols.append(int(c))
                    data.append(complex(f))
    return sp.csr_matrix((data, (rows, cols)), shape=(dim, dim), dtype=complex)


def perelomov(A, ref_idx, dim, tol=TOL):
    v0 = np.zeros(dim, dtype=complex)
    v0[ref_idx] = 1.0
    result = v0.copy()
    term = v0.copy()
    for it in range(1, 2 * K + 8):
        term = (A @ term) / it
        inc = float(np.linalg.norm(term))
        res = float(np.linalg.norm(result))
        result = result + term
        if inc < tol * max(1.0, res):
            break
    return result / np.linalg.norm(result)


def single_edge_ops(occ, index, n):
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
            rp.append(idx_of(index, t))
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
            rp.append(idx_of(index, t))
            cp_.append(int(c))
            dp.append(np.sqrt(na[c, e] * (nb[c, e] + 1)))
        jm = sp.csr_matrix((dp, (rp, cp_)), shape=(dim, dim), dtype=complex)
        ops.append((jz, jp, jm))
    return ops


def jdot(ops, i, j):
    jzi, jpi, jmi = ops[i]
    jzj, jpj, jmj = ops[j]
    return jzi @ jzj + 0.5 * (jpi @ jmj + jmi @ jpj)


def sign_agreement(qs, tol=NONZERO_TOL):
    live = [q for q in qs if abs(q) > tol]
    if not live:
        return 0.0, 0, 0, len(qs)
    pos = sum(1 for q in live if q > 0)
    return max(pos, len(live) - pos) / len(live), pos, len(live) - pos, len(qs)


def pearson(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    mx, my = x.mean(), y.mean()
    vx, vy = ((x - mx) ** 2).sum(), ((y - my) ** 2).sum()
    if vx == 0 or vy == 0:
        return float("nan")
    return float(((x - mx) * (y - my)).sum() / np.sqrt(vx * vy))


def main():
    t_start = time.time()
    print(f"T5a magnetization sweep: n={N} K={K} plane_seed={PLANE_SEED}")
    occ, index = build_fixed_k_basis(N, K)
    dim = len(occ)
    print(f"fixed-K basis dim={dim}")
    plane = fixed_complex_plane(N, PLANE_SEED)
    z = plane_to_z(plane)
    print(f"plane row0={np.array2string(plane[0], precision=3)}")
    print(f"plane row1={np.array2string(plane[1], precision=3)}")
    print(f"Z anti-Hermiticity |Z+Z^dag|max={np.max(np.abs(z + z.conj().T)):.2e}")

    t0 = time.time()
    A = build_A(occ, index, z, N)
    print(f"A built nnz={A.nnz} ({time.time()-t0:.1f}s)")
    t0 = time.time()
    ops = single_edge_ops(occ, index, N)
    print(f"edge ops built ({time.time()-t0:.1f}s)")
    pairs = {}
    for i in range(N):
        for j in range(i + 1, N):
            pairs[(i, j)] = jdot(ops, i, j)
    triples = [(i, j, k) for i in range(N) for j in range(i + 1, N)
               for k in range(j + 1, N)]

    # validate each config sums to K, record M
    for label, ref in CONFIGS:
        tot = sum(a + b for a, b in ref)
        na = sum(a for a, _ in ref)
        nb = sum(b for _, b in ref)
        assert tot == K, (label, tot)
        assert (na - nb) % 2 == 0

    results = []
    for label, ref in CONFIGS:
        na = sum(a for a, _ in ref)
        nb = sum(b for _, b in ref)
        mag = (na - nb) / 2
        flat = [x for pair in ref for x in pair]
        ref_idx = idx_of(index, flat)
        t1 = time.time()
        v = perelomov(A, ref_idx, dim)
        w = {}
        for (i, j), mat in pairs.items():
            w[(i, j)] = mat @ v
        qs = []
        for (i, j, k) in triples:
            znum = complex(np.vdot(w[(i, j)], w[(j, k)]))
            qs.append(-2.0 * znum.imag)
        agree, pos, neg, total = sign_agreement(qs)
        aq = np.abs(qs)
        results.append({"label": label, "M": mag, "ref": ref,
                        "q": qs, "agree": agree, "pos": pos, "neg": neg,
                        "max_abs": float(aq.max()),
                        "mean_abs": float(aq.mean())})
        print(f"{label:18s} M={mag:+.0f} ref={ref} time={time.time()-t1:.1f}s")
        print(f"  sign-agreement={agree:.4f} ({pos} pos + {neg} neg of {total}) "
              f"max|q|={aq.max():.3e} mean|q|={aq.mean():.3e}")
        for (t, q) in zip(triples, qs):
            print(f"    q_{t[0]+1}{t[1]+1}{t[2]+1}={q:+.6e}")

    base = next(r for r in results if r["label"] == "M=0_spread")
    print("--- correlation vs M=0_spread baseline ---")
    for r in results:
        r_abs = pearson(np.abs(r["q"]), np.abs(base["q"]))
        r_sg = pearson(r["q"], base["q"])
        r["pearson_abs_vs_base"] = r_abs
        r["pearson_signed_vs_base"] = r_sg
        print(f"  {r['label']:18s} Pearson|q|={r_abs:+.4f} signed={r_sg:+.4f}")

    with open("t5a_mag_results.json", "w") as f:
        json.dump({"n": N, "k": K, "plane_seed": PLANE_SEED,
                   "triples": triples,
                   "results": [{k: v for k, v in r.items()} for r in results]},
                  f, indent=1)
    print(f"TOTAL time={time.time()-t_start:.1f}s wrote t5a_mag_results.json")
    print("SUMMARY " + json.dumps(
        [{"label": r["label"], "M": r["M"], "agree": round(r["agree"], 4),
          "max_abs": f"{r['max_abs']:.3e}", "mean_abs": f"{r['mean_abs']:.3e}",
          "r_abs": round(r["pearson_abs_vs_base"], 4)
          if r["pearson_abs_vs_base"] == r["pearson_abs_vs_base"] else None}
         for r in results]))


if __name__ == "__main__":
    main()

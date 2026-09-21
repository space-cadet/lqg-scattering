"""T7e -- Complexified momenta in the TFD: eps-scaling of the two-sided correlator.

C(eps) = C0 + eps*dC with the T5b convention dC[1,i] = 1j*0.35*(i+0.5),
eps = 1e-6, 1e-4, 1e-2, 0.1, 1.0. At each eps the off-cell Perelomov state
(converged Taylor 8K+50 + assert) feeds a coherent two-sided state
  |Psi(beta,eps)> = sum_n d_n |n>_L |n>_R, d_n ~ c_n(eps) e^{-beta E_n/2},
and <q_L q_R> = sum_{nm} d_n^* d_m (q_nm)^2 (complex amplitudes -- this is
where R-conjugation bites, unlike the diagonal ensembles of T7a/T7b).

R-conjugation handling (explicit): the R leg is built from the conjugate
plane C* and checked numerically against conjugating the R amplitudes of the
C-built state (they coincide: momentum map + Taylor both commute with
conjugation). The <q_L q_R> observable itself is conjugation-invariant
((q_nm)^2 real symmetric) -- verified numerically.

Sweep beta = 0.5, 1, 5 at each eps; compare eps-scaling of |corr| against
single-copy |q|, pure <q^2>, dephased Tr(rho q^2), and T5b V ~ eps^0.5.

Conventions match T7a/T7b/T5b. Reuses t7a_thermal. Writes t7e_results.json.
"""

import json

import numpy as np

import t7a_thermal as T7a

GAMMA = T7a.GAMMA
TRIPLE = T7a.TRIPLE
SEEDS = {4: 11, 5: 12}
EPSS = [1e-6, 1e-4, 1e-2, 0.1, 1.0]
BETAS = [0.5, 1.0, 5.0]


def fixed_perturbation(N):
    dC = np.zeros((2, N), dtype=complex)
    for i in range(N):
        dC[1, i] = 1j * 0.35 * (i + 0.5)
    return dC


def fit_power(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    m = y > 0
    alpha, logc = np.polyfit(np.log(x[m]), np.log(y[m]), 1)
    yp = alpha * np.log(x[m]) + logc
    ss_res = float(np.sum((np.log(y[m]) - yp) ** 2))
    ss_tot = float(np.sum((np.log(y[m]) - np.log(y[m]).mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    lx, ly = np.log(x[m]), np.log(y[m])
    slopes = ((ly[1:] - ly[:-1]) / (lx[1:] - lx[:-1])).tolist()
    return {"alpha": float(alpha), "prefactor": float(np.exp(logc)),
            "r2": float(r2), "local_slopes": [float(s) for s in slopes]}


def sweep_n(N, seed, epss, betas, t5b):
    C0 = T7a.positive_plane_curve(N, seed=seed)
    dC = fixed_perturbation(N)
    ref = T7a.vertex_reference(N, TRIPLE)
    K = int(ref.sum())
    space = T7a.OpSpace(N, K)
    E = space.energy
    ref_v = space.ref_vec(ref)
    print(f"--- n={N}: dim={space.dim}, K={K}, seed={seed} ---", flush=True)

    q_op = T7a.q_operator(space, triple=TRIPLE).tocsr()
    coo = q_op.tocoo()
    rows, cols, data = coo.row, coo.col, coo.data
    data2 = (data * data).real  # (q_nm)^2, real (q imaginary)
    assert np.abs((data * data).imag).max() < 1e-18
    q2diag = np.asarray(
        q_op.conj().multiply(q_op).sum(axis=1)).real.flatten()
    q2diag = np.maximum(q2diag, 0.0)

    eps_rows = []
    for eps in epss:
        C = C0 + eps * dC
        Z = T7a.plane_to_Z(C)
        psi, iters = space.taylor_exp(space.amat(Z), ref_v, K)
        # R-conjugation equivalence: Perelomov(C*) vs conj(Perelomov(C))
        psi_star, _ = space.taylor_exp(
            space.amat(T7a.plane_to_Z(C.conj())), ref_v, K)
        # global phase alignment before comparing
        ov = np.vdot(psi_star, psi.conj())
        conj_diff = float(np.linalg.norm(psi_star - ov * psi.conj()))
        V_sc, q_sc = T7a.volume_on_vec(psi, space, triple=TRIPLE)
        qv = q_op @ psi
        q2_pure = float(np.vdot(qv, qv).real)
        w = np.abs(psi) ** 2
        q2_deph = float(w @ q2diag)
        corr_b = {}
        for beta in betas:
            d = psi * np.exp(-beta * E / 2)
            d = d / np.linalg.norm(d)
            c = np.sum(d.conj()[rows] * d[cols] * data2)
            assert abs(c.imag) < 1e-9 * max(1.0, abs(c.real)), (eps, beta, c)
            # conjugation invariance: corr(d*) == corr(d)
            c2 = np.sum(d[rows] * d.conj()[cols] * data2)
            assert abs(c.real - c2.real) < 1e-12 * max(1.0, abs(c.real))
            corr_b[str(beta)] = float(c.real)
        spread = max(corr_b.values()) - min(corr_b.values())
        eps_rows.append({"eps": eps, "taylor_iters": iters,
                         "conj_diff": conj_diff,
                         "V_sc": V_sc, "q_real": q_sc.real,
                         "q_imag": q_sc.imag,
                         "q_abs": abs(q_sc), "q2_pure": q2_pure,
                         "q2_deph": q2_deph, "corr": corr_b,
                         "corr_beta_spread": spread})
        print(f"  eps={eps:.0e} iters={iters} conj_diff={conj_diff:.1e} "
              f"V_sc={V_sc:.4e} |q|={abs(q_sc):.4e} "
              f"q2_pure={q2_pure:.6e} q2_deph={q2_deph:.6e} "
              f"corr={['%+.3e' % corr_b[str(b)] for b in betas]} "
              f"spread={spread:.1e}", flush=True)

    assert all(r["conj_diff"] < 1e-9 for r in eps_rows), "R-conjugation check"
    # beta-flatness (fixed-K support: e^{-beta E/2} constant on support)
    assert all(r["corr_beta_spread"] < 1e-9 * max(1.0, abs(r["q2_pure"]))
               for r in eps_rows), "beta-flatness check"

    eps = np.array([r["eps"] for r in eps_rows])
    V = np.array([r["V_sc"] for r in eps_rows])
    qabs = np.array([r["q_abs"] for r in eps_rows])
    c1 = np.array([r["corr"]["1.0"] for r in eps_rows])
    q2p = np.array([r["q2_pure"] for r in eps_rows])
    fV = fit_power(eps, V)
    fq = fit_power(eps, qabs)
    # change-relative-to-on-cell fits (corr/q2 tend to nonzero constants)
    dcorr = np.abs(c1 - c1[0])
    dq2p = np.abs(q2p - q2p[0])
    fcorr = fit_power(eps[1:], dcorr[1:])
    fq2p = fit_power(eps[1:], dq2p[1:])
    print(f"  fit V_sc ~ eps^{fV['alpha']:.4f} R2={fV['r2']:.4f} "
          f"(T5b replication; T5b alpha={t5b['alpha']:.4f})", flush=True)
    print(f"  fit |q| ~ eps^{fq['alpha']:.4f} R2={fq['r2']:.4f} "
          f"(expect ~1.0 = 2x T5b)", flush=True)
    print(f"  fit |dcorr| ~ eps^{fcorr['alpha']:.4f} R2={fcorr['r2']:.4f} "
          f"slopes=" + " ".join(f"{s:.2f}" for s in fcorr["local_slopes"]),
          flush=True)
    print(f"  fit |dq2pure| ~ eps^{fq2p['alpha']:.4f} R2={fq2p['r2']:.4f} "
          f"slopes=" + " ".join(f"{s:.2f}" for s in fq2p["local_slopes"]),
          flush=True)

    # direct comparison at shared eps grid points with T5b
    shared = []
    for e_t5b, v_t5b in zip(t5b["eps"], t5b["V"]):
        for r in eps_rows:
            if abs(e_t5b - r["eps"]) / r["eps"] < 1e-9:
                shared.append({"eps": r["eps"], "V_t7e": r["V_sc"],
                               "V_t5b": v_t5b,
                               "ratio": r["V_sc"] / v_t5b if v_t5b > 0
                               else None})
    for s in shared:
        print(f"  eps={s['eps']:.0e}: V_t7e={s['V_t7e']:.4e} "
              f"V_t5b={s['V_t5b']:.4e} ratio={s['ratio']:.4f}", flush=True)

    return {"dim": space.dim, "K": K, "seed": seed, "rows": eps_rows,
            "fit_V": fV, "fit_qabs": fq, "fit_dcorr": fcorr,
            "fit_dq2pure": fq2p, "t5b_alpha": t5b["alpha"],
            "t5b_shared": shared}


def main():
    with open("t5b_results.json") as f:
        t5b = json.load(f)["n"]
    print(f"T7e complexified TFD: triple={list(TRIPLE)} epss={EPSS} "
          f"betas={BETAS}", flush=True)
    out = {"triple": list(TRIPLE), "gamma": GAMMA, "epss": EPSS,
           "betas": BETAS, "n": {}}
    for N in (4, 5):
        out["n"][str(N)] = sweep_n(N, SEEDS[N], EPSS, BETAS, t5b[str(N)])
    with open("t7e_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote t7e_results.json", flush=True)

    print("\n=== T7e verdict ===", flush=True)
    for Ns in ("4", "5"):
        d = out["n"][Ns]
        print(f"n={Ns}: V-fit alpha={d['fit_V']['alpha']:.4f} "
              f"(T5b {d['t5b_alpha']:.4f}); |q|-fit {d['fit_qabs']['alpha']:.4f}; "
              f"dcorr-fit {d['fit_dcorr']['alpha']:.4f} "
              f"slopes=" + " ".join(f"{s:.2f}"
                                    for s in d["fit_dcorr"]["local_slopes"])
              + "; corr beta-flat (spread<=1e-9); R-conjugation no-op for "
              "<qLqR>, verified.", flush=True)
    print("RESULT: eps-scaling measured; beta-flatness and conjugation verdicts "
          "above -- see t7e_notes.md.", flush=True)


if __name__ == "__main__":
    main()

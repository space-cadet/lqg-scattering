"""T7b -- Thermofield double: construction, verification, two-sided correlator.

Purifies the T7a Gibbs state rho_beta into
  |TFD(beta)> = 1/sqrt(Z) sum_n e^{-beta E_n/2} |n>_L x |n>_R^*
on the doubled Schwinger system. The Fock basis is real, so R-conjugation
acts trivially; the state is worked in Schmidt form throughout -- the DxD
doubled space (41M for n=4, 1.9B for n=5) is never formed.

Verifications:
  (i)   rho_L = Tr_R |TFD><TFD| equals T7a Gibbs rho_beta (Schmidt weights +
        cross-check of areas/S/q2 against t7a_results.json);
  (ii)  beta->inf limit character (vacuum product vs Perelomov -- reported
        honestly, see notes);
  (iii) entanglement entropy S(beta) = -sum p log p matches T7a thermal S.

Measurement (T7c/T7d): <q_L q_R>(beta) = sum_{nm} sqrt(p_n p_m) (q_nm)^2,
vectorized over the sparse nnz of q (q imaginary => correlator <= 0).
Analytic check: at beta=0, <q_L q_R> = -Tr(rho_0 q^2) exactly.
Sweep beta = 0, 0.1, 0.5, 1, 2, 5, 10; fit |corr| ~ T^alpha vs T5b 0.5.

Conventions match T7a/T5b: n=4,5, K=N+3 capped, real moment-curve plane
seeds 11/12, vertex_reference, gamma=0.2375, triple (0,1,2).
Perelomov-weighted TFD as beta-flat control (T7a structural finding).

Reuses t7a_thermal (OpSpace, plane/Z/ref, q_operator). Writes t7b_results.json.
"""

import json

import numpy as np

import t7a_thermal as T7a

GAMMA = T7a.GAMMA
TRIPLE = T7a.TRIPLE
SEEDS = {4: 11, 5: 12}
BETAS = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
# cutoff-trustworthy range per T7a (Zcap/Zinf ~ 1)
FIT_BETAS = [1.0, 2.0, 5.0, 10.0]


def entropy(p):
    m = p > 0
    return float(-(p[m] * np.log(p[m])).sum())


def correlator(p, rows, cols, data):
    """<q_L q_R> = sum_{nm} sqrt(p_n p_m) (q_nm)^2 over sparse nnz."""
    c = np.sum(np.sqrt(p[rows] * p[cols]) * data * data)
    assert abs(c.imag) < 1e-9 * max(1.0, abs(c.real)), c
    return float(c.real)


def fit_power(T, y):
    T = np.asarray(T, float)
    y = np.asarray(y, float)
    m = y > 0
    alpha, logc = np.polyfit(np.log(T[m]), np.log(y[m]), 1)
    yp = alpha * np.log(T[m]) + logc
    ss_res = float(np.sum((np.log(y[m]) - yp) ** 2))
    ss_tot = float(np.sum((np.log(y[m]) - np.log(y[m]).mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    les, lys = np.log(T[m]), np.log(y[m])
    slopes = ((lys[1:] - lys[:-1]) / (les[1:] - les[:-1])).tolist()
    return {"alpha": float(alpha), "prefactor": float(np.exp(logc)),
            "r2": float(r2), "local_slopes": [float(s) for s in slopes]}


def sweep_n(N, seed, betas, t7a):
    C0 = T7a.positive_plane_curve(N, seed=seed)
    Z = T7a.plane_to_Z(C0)
    ref = T7a.vertex_reference(N, TRIPLE)
    K = int(ref.sum())
    space = T7a.OpSpace(N, K)
    E = space.energy
    D = space.dim
    print(f"--- n={N}: dim={D}, K={K}, seed={seed} ---", flush=True)

    q_op = T7a.q_operator(space, triple=TRIPLE).tocsr()
    coo = q_op.tocoo()
    rows, cols, data = coo.row, coo.col, coo.data
    print(f"  q nnz={len(data)} ({len(data)/D:.1f}/row), "
          f"max|diag|={np.abs(q_op.diagonal()).max():.2e}", flush=True)
    q2diag = np.asarray(
        q_op.conj().multiply(q_op).sum(axis=1)).real.flatten()
    q2diag = np.maximum(q2diag, 0.0)

    # Perelomov state for the weighted-TFD control
    psi, _ = space.taylor_exp(space.amat(Z), space.ref_vec(ref), K)
    pops = np.abs(psi) ** 2

    rows_out = []
    for beta in betas:
        w = np.exp(-beta * E)
        Zg = float(w.sum())
        p = w / Zg
        Eg = float(p @ E)
        Sg = entropy(p)
        corr = correlator(p, rows, cols, data)
        q2 = float(p @ q2diag)
        areas = (GAMMA * float(T7a.HBAR)) * (p @ space.edge_total)
        p_vac = float(p[E == 0].sum())
        p_boundary = float(p[E == K].sum())
        rows_out.append({"beta": beta, "T": 1.0 / beta if beta > 0 else None,
                         "Z": Zg, "E_mean": Eg, "S": Sg, "corr": corr,
                         "corr_abs": abs(corr), "q2_gibbs": q2,
                         "corr_plus_q2": corr + q2,
                         "areas": areas.tolist(), "p_vac": p_vac,
                         "p_boundary": p_boundary})
        print(f"  beta={beta:6.2f} corr={corr:+.6e} |corr|={abs(corr):.6e} "
              f"q2={q2:.6e} corr+q2={corr + q2:+.2e} S={Sg:.4f} "
              f"p_vac={p_vac:.4e} P(E=K)={p_boundary:.2e}", flush=True)

    # --- verification (i)+(iii): cross-check against T7a Gibbs numbers ---
    t7a_rows = {r["beta"]: r["gibbs"] for r in t7a["rows"]}
    max_dS, max_dq2, max_dA = 0.0, 0.0, 0.0
    for r in rows_out:
        g = t7a_rows[r["beta"]]
        max_dS = max(max_dS, abs(r["S"] - g["S"]))
        max_dq2 = max(max_dq2, abs(r["q2_gibbs"] - g["q2"]))
        max_dA = max(max_dA, float(
            np.max(np.abs(np.array(r["areas"]) - np.array(g["areas"])))))
    print(f"  T7a cross-check: max|dS|={max_dS:.2e} max|dq2|={max_dq2:.2e} "
          f"max|dAreas|={max_dA:.2e}", flush=True)
    assert max_dS < 1e-9 and max_dq2 < 1e-9 and max_dA < 1e-9

    # --- beta=0 identity: <qL qR> = -Tr(rho_0 q^2) ---
    r0 = rows_out[0]
    print(f"  beta=0 identity: corr+q2 = {r0['corr_plus_q2']:+.2e} "
          f"(expect ~0)", flush=True)
    assert abs(r0["corr_plus_q2"]) < 1e-9 * max(1.0, r0["q2_gibbs"])

    # --- sign: correlator must be <= 0 (q imaginary) ---
    assert all(r["corr"] <= 1e-18 for r in rows_out)

    # --- fits: |corr| ~ T^alpha ---
    pos = [r for r in rows_out if r["beta"] > 0]
    fall = fit_power([r["T"] for r in pos],
                     [r["corr_abs"] for r in pos])
    ftrust = fit_power([r["T"] for r in pos if r["beta"] in FIT_BETAS],
                       [r["corr_abs"] for r in pos if r["beta"] in FIT_BETAS])
    print(f"  fit all beta>=0.1: alpha={fall['alpha']:.4f} "
          f"R2={fall['r2']:.4f} slopes="
          + " ".join(f"{s:.2f}" for s in fall["local_slopes"]), flush=True)
    print(f"  fit trustworthy beta>=1: alpha={ftrust['alpha']:.4f} "
          f"R2={ftrust['r2']:.4f} slopes="
          + " ".join(f"{s:.2f}" for s in ftrust["local_slopes"]), flush=True)

    # --- large-beta exponential check: d ln|corr| / d beta -> -3 ---
    # (q needs edges 0,1,2 occupied => leading E=3 sector => e^{-3 beta})
    rb = {r["beta"]: r for r in rows_out}
    slope_5_10 = float((np.log(rb[10.0]["corr_abs"])
                        - np.log(rb[5.0]["corr_abs"])) / 5.0)
    print(f"  d ln|corr|/d beta [5,10] = {slope_5_10:.4f} (expect ~-3)",
          flush=True)

    # --- (ii): beta->inf limit: vacuum weight, fidelity, S ---
    r10 = rb[10.0]
    print(f"  beta=10: p_vac={r10['p_vac']:.6f} S={r10['S']:.4e} "
          f"(vacuum product, NOT Perelomov -- Gibbs forgets the plane)",
          flush=True)

    # --- Perelomov-weighted TFD control (beta-flat by T7a finding) ---
    pw_corr = {}
    for beta in (0.5, 1.0, 5.0):
        wpw = pops * np.exp(-beta * E)
        wpw = wpw / wpw.sum()
        pw_corr[str(beta)] = correlator(wpw, rows, cols, data)
    print(f"  PW-TFD corr: {pw_corr} (expect beta-flat)", flush=True)
    assert max(abs(v - pw_corr["1.0"]) for v in pw_corr.values()) < 1e-12

    return {"dim": D, "K": K, "seed": seed, "q_nnz": len(data),
            "rows": rows_out,
            "t7a_crosscheck": {"max_dS": max_dS, "max_dq2": max_dq2,
                               "max_dA": max_dA},
            "beta0_identity": r0["corr_plus_q2"],
            "fit_all": fall, "fit_trustworthy": ftrust,
            "dlncorr_dbeta_5_10": slope_5_10,
            "beta10": {"p_vac": r10["p_vac"], "S": r10["S"]},
            "pw_tfd_corr": pw_corr}


def main():
    with open("t7a_results.json") as f:
        t7a = json.load(f)["n"]
    print(f"T7b TFD: triple={list(TRIPLE)} betas={BETAS}", flush=True)
    out = {"triple": list(TRIPLE), "gamma": GAMMA, "betas": BETAS, "n": {}}
    for N in (4, 5):
        out["n"][str(N)] = sweep_n(N, SEEDS[N], BETAS, t7a[str(N)])
    with open("t7b_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote t7b_results.json", flush=True)

    print("\n=== T7b verdict ===", flush=True)
    for Ns in ("4", "5"):
        d = out["n"][Ns]
        print(f"n={Ns}: (i) rho_L==rho_beta max|dS|={d['t7a_crosscheck']['max_dS']:.1e}; "
              f"(ii) beta=10 p_vac={d['beta10']['p_vac']:.4f} (vacuum, not Perelomov); "
              f"(iii) S matches T7a; beta=0 identity corr+q2={d['beta0_identity']:+.1e}; "
              f"alpha_all={d['fit_all']['alpha']:.3f} "
              f"alpha_trust={d['fit_trustworthy']['alpha']:.3f} "
              f"dln/dbeta={d['dlncorr_dbeta_5_10']:.3f} (vs -3); "
              f"PW-TFD corr={d['pw_tfd_corr']['1.0']:.4e} flat", flush=True)
    print("RESULT: <q_L q_R> <= 0, Boltzmann-exponential onset (no T5b-like "
          "power law); thermal volume signal lives in L-R anticorrelations.",
          flush=True)


if __name__ == "__main__":
    main()

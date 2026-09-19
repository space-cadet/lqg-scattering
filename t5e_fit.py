"""T5e fit: merge raw sweep JSONs, log-log fit V ~ K^alpha per family.

Reads t5e_raw_uniform.json / t5e_raw_vertex.json / t5e_raw_seed42.json
(written by the t5e Rust binary), prints the fit evidence block, and writes
t5e_results.json. Only numpy is used.
"""

import json

import numpy as np


def loglog_fit(K, V):
    K = np.asarray(K, float)
    V = np.asarray(V, float)
    m = V > 0
    alpha, logc = np.polyfit(np.log(K[m]), np.log(V[m]), 1)
    y = np.log(V[m])
    yp = alpha * np.log(K[m]) + logc
    ss_res = float(np.sum((y - yp) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    lk, lV = np.log(K[m]), np.log(V[m])
    local = ((lV[1:] - lV[:-1]) / (lk[1:] - lk[:-1])).tolist()
    return {"alpha": float(alpha), "prefactor": float(np.exp(logc)),
            "r2": float(r2), "local_slopes": [float(s) for s in local],
            "n_points": int(m.sum())}


def load(name):
    with open(name) as f:
        return json.load(f)


def main():
    uni = load("t5e_raw_uniform.json")
    vtx = load("t5e_raw_vertex.json")
    s42 = load("t5e_raw_seed42.json")

    def KV(d):
        pts = d["points"]
        return [p["K"] for p in pts], [p["V"] for p in pts]

    Ku, Vu = KV(uni)
    Kv, Vv = KV(vtx)
    K4, V4 = KV(s42)

    # primary: uniform seed-11, shape-uniform M=0 even-m subset (K=8,16,24)
    m0 = [(k, v) for k, v in zip(Ku, Vu) if k in (8, 16, 24)]
    fit_all_uni = loglog_fit(Ku, Vu)
    fit_m0 = loglog_fit([k for k, _ in m0], [v for _, v in m0])
    fit_vtx = loglog_fit(Kv, Vv)
    fit_s42 = loglog_fit(K4, V4)
    # consistency: <q> slope should be ~2x the V slope (V ~ sqrt|q|)
    qu = [abs(p["q"]) for p in uni["points"]]
    fit_q = loglog_fit(Ku, qu)

    print("=== T5e fit: V ~ K^alpha ===")
    for name, f in (("uniform seed11 all-K", fit_all_uni),
                    ("uniform seed11 M=0 even-m (8,16,24)", fit_m0),
                    ("vertex seed11", fit_vtx),
                    ("uniform seed42", fit_s42)):
        print(f"  {name}: alpha={f['alpha']:+.4f} R2={f['r2']:.4f} "
              f"local={[f'{s:+.3f}' for s in f['local_slopes']]}")
    print(f"  <q> slope (uniform seed11) = {fit_q['alpha']:+.4f} "
          f"(expect ~2x V-slope if V=sqrt|q| holds)")

    out = {"experiment": "T5e large-K semiclassics",
           "hypothesis_probe": "alpha ~ 1.5",
           "families": {"uniform_seed11": uni, "vertex_seed11": vtx,
                        "uniform_seed42": s42},
           "fits": {"uniform_all": fit_all_uni, "uniform_M0_even": fit_m0,
                    "vertex": fit_vtx, "seed42": fit_s42,
                    "q_uniform": fit_q}}
    with open("t5e_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote t5e_results.json")


if __name__ == "__main__":
    main()

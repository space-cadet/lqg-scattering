"""T5e fit: merge raw sweep JSONs, log-log fit V ~ K^alpha per family.

Reads the T5e raw sweep JSONs from results/ (written by the T5e Rust binary),
prints the fit evidence block, and writes results/t5e_results.json. Only
numpy is used.
"""

import json

import numpy as np
from project_paths import RESULTS_ROOT
from lqg_scattering.analysis import fit_power


def loglog_fit(K, V):
    """Add the study's point count to the shared power-law summary."""
    return {**fit_power(K, V), "n_points": int(np.count_nonzero(np.asarray(V) > 0))}


def load(name):
    with (RESULTS_ROOT / name).open() as f:
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
    with (RESULTS_ROOT / "t5e_results.json").open("w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {RESULTS_ROOT / 't5e_results.json'}")


if __name__ == "__main__":
    main()

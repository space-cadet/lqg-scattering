"""T5b — Perturbation response of the signed-mean proxy.

Question: perturb a positive real Gr(2,N) plane and measure the response
of sqrt(|<q>|) for this fixed family. This is not a positive volume-operator
expectation. Fit the proxy's eps exponent for this family.
  - alpha describes only this perturbation and reference state.

Protocol (per experiments.md section T5b + user spec):
  C(eps) = C0 + eps * delta_C,
    C0      = real positive plane (moment curve, fixed seed),
    delta_C = FIXED purely imaginary perturbation, second row only:
              delta_C[1, i] = 1j * 0.35 * (i + 0.5).
  Sweep eps geometrically 1e-6 .. 1.0 at n = 4 and n = 5.
  At each eps: Perelomov U(N) coherent state |Z(C(eps))>, reference =
  vertex_reference (genuine spin-network occupation: one a-boson per edge
  + one b-boson on each edge of the volume triple -- NOT all-a, which
  freezes <q> = 0), K = N + 3.
  Measure V = (gamma*hbar)^1.5 * sqrt(|<q>|),
    <q> = <i [A_ij, A_jk]>, A_ij = J_i . J_j (Schwinger), triple (0,1,2).
  Fit log-log slope alpha of V vs eps.

Controls:
  - eps = 0 (real plane) -> <q> = 0 analytically (real amplitudes).
  - all-a reference at eps = 1 -> <q> = 0 (spin-freezing control).

Formulas follow coherent_states.py / positivity.py of the lqg-scattering
reference implementation exactly (momentum-map Z, Taylor-exponential
Perelomov state, De Pietri / Rovelli-Smolin commutator). Operators are
built once per N as scipy.sparse CSR matrices on the occupation basis;
only the matrix elements (not the physics) differ from the reference.

Only numpy + scipy are used. Writes results/t5b_results.json.
"""

import itertools
import json

import numpy as np
from lqg_scattering.coherent_states import plane_to_Z
from lqg_scattering.positivity import positive_plane_curve as _positive_plane_curve
from lqg_scattering.positivity import vertex_reference
from project_paths import RESULTS_ROOT
from lqg_scattering.conventions import DEFAULT_TRIPLE, GAMMA, HBAR
from lqg_scattering.schwinger import SparseSchwingerSpace, normalized_taylor_exp, volume_on_vec
from lqg_scattering.analysis import fit_power

TRIPLE = DEFAULT_TRIPLE


class OpSpace(SparseSchwingerSpace):
    """T5b adapter preserving its vector-only Taylor helper."""

    @staticmethod
    def taylor_exp(A, ref_vec, K, tol=1e-12):
        return normalized_taylor_exp(A, ref_vec, K, tol=tol)[0]


# --------------------------------------------------------------------------
# Grassmannian side
# --------------------------------------------------------------------------

def positive_plane_curve(N, seed=0, t_min=0.2, t_max=3.0):
    """T5b's deterministic defaults for the shared positive-plane helper."""
    return _positive_plane_curve(N, seed=seed, t_min=t_min, t_max=t_max)


def fixed_perturbation(N):
    """FIXED purely imaginary perturbation, second row only:
    delta_C[1, i] = 1j * 0.35 * (i + 0.5)."""
    dC = np.zeros((2, N), dtype=complex)
    for i in range(N):
        dC[1, i] = 1j * 0.35 * (i + 0.5)
    return dC


# --------------------------------------------------------------------------
# T5b sweep
# --------------------------------------------------------------------------

def sweep_n(N, epsilons, seed, triple=TRIPLE):
    C0 = positive_plane_curve(N, seed=seed)
    dC = fixed_perturbation(N)
    ref = vertex_reference(N, triple)
    K = int(ref.sum())
    space = OpSpace(N, K)
    print(f"--- n={N}: Fock dim={space.dim}, K={K}, "
          f"ref a={ref[:, 0].tolist()} b={ref[:, 1].tolist()} ---",
          flush=True)
    ref_v = space.ref_vec(ref)
    rows = []
    for eps in epsilons:
        Z = plane_to_Z(C0 + eps * dC)
        vec = space.taylor_exp(space.amat(Z), ref_v, K)
        V, q = volume_on_vec(vec, space, triple=triple)
        rows.append((float(eps), V, complex(q)))
        print(f"  eps={eps:.1e}  V={V:.6e}  "
              f"V/(gh)^1.5={V / GAMMA ** 1.5:.6e}  "
              f"<q>={q.real:+.6e}{q.imag:+.6e}j", flush=True)
    return {"C0": C0, "dC": dC, "rows": rows, "dim": space.dim, "K": K,
            "space": space, "ref": ref}


def loglog_fit(eps, V):
    """Keep the historical tuple result while using the shared fit."""
    fit = fit_power(eps, V)
    return fit["alpha"], fit["prefactor"], fit["r2"]


def main():
    epsilons = np.geomspace(1e-6, 1.0, 13)  # 1e-6 .. 1.0, 13 points
    triple = TRIPLE
    out = {"epsilons": epsilons.tolist(), "triple": list(triple),
           "gamma": GAMMA, "hbar": HBAR,
           "state_engine": "Taylor exponential with convergence assertion",
           "state_tol": 1e-12, "state_max_terms_rule": "8*K+49",
           "observable": "(gamma*hbar)^1.5*sqrt(abs(<q>))",
           "n": {}}

    for N, seed in ((4, 11), (5, 12)):
        res = sweep_n(N, epsilons, seed=seed, triple=triple)
        eps = [r[0] for r in res["rows"]]
        V = [r[1] for r in res["rows"]]
        q = [r[2] for r in res["rows"]]
        alpha, c, r2 = loglog_fit(eps, V)
        les, lVs = np.log(eps), np.log(np.maximum(V, 1e-300))
        slopes = ((np.array(lVs[1:]) - np.array(lVs[:-1]))
                  / (np.array(les[1:]) - np.array(les[:-1]))).tolist()
        print(f"n={N}: V ~ eps^{alpha:.4f}  (C={c:.4e}, R^2={r2:.6f})",
              flush=True)
        print(f"n={N}: consecutive log-log slopes: "
              + " ".join(f"{s:.3f}" for s in slopes), flush=True)

        # --- controls ---
        space = res["space"]
        ref = res["ref"]
        K = int(ref.sum())
        vec0 = space.taylor_exp(space.amat(plane_to_Z(res["C0"])),
                                space.ref_vec(ref), K)
        V0, _ = volume_on_vec(vec0, space, triple=triple)
        ref_alla = np.zeros((N, 2), dtype=int)
        ref_alla[:, 0] = 1
        space_a = OpSpace(N, int(ref_alla.sum()))
        veca = space_a.taylor_exp(
            space_a.amat(plane_to_Z(res["C0"] + 1.0 * res["dC"])),
            space_a.ref_vec(ref_alla), int(ref_alla.sum()))
        Va, _ = volume_on_vec(veca, space_a, triple=triple)
        print(f"n={N} controls: V(eps=0, vertex ref)={V0:.3e} (expect 0); "
              f"V(eps=1, all-a ref)={Va:.3e} (expect 0)", flush=True)
        assert V0 < 1e-8, f"real-plane volume must vanish, got {V0}"
        assert Va < 1e-12, f"all-a volume must vanish, got {Va}"

        out["n"][str(N)] = {
            "seed": seed, "dim": res["dim"], "K": K,
            "eps": eps, "V": V,
            "q_real": [float(x.real) for x in q],
            "q_imag": [float(x.imag) for x in q],
            "alpha": alpha, "prefactor": c, "r2": r2,
            "local_slopes": slopes,
            "V_eps0": V0, "V_alla_eps1": Va,
        }

    with (RESULTS_ROOT / "t5b_results.json").open("w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {RESULTS_ROOT / 't5b_results.json'}", flush=True)

    print("\n=== T5b verdict ===", flush=True)
    for Ns in ("4", "5"):
        d = out["n"][Ns]
        print(f"n={Ns}: alpha={d['alpha']:.4f}, R^2={d['r2']:.6f}, "
              f"V(1e-6)={d['V'][0]:.3e}, V(1)={d['V'][-1]:.3e}", flush=True)
    print("For this perturbation and reference, the signed-mean proxy has "
          "a near-half exponent; broader claims require other controls.",
          flush=True)


if __name__ == "__main__":
    main()

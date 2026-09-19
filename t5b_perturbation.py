"""T5b — Perturbation response V(epsilon).

Physics question: turn on a small chirality-breaking perturbation eps of a
positive (real) Gr(2,N) plane and measure V(eps). Fit V ~ eps^alpha.
  - alpha < 1  -> chirality turns on arbitrarily softly (no barrier).
  - alpha >= 1 or a threshold -> chirality is "quantized" / barrier-like.

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
  - eps = 0 (real plane) -> V == 0 exactly (real Fock amplitudes).
  - all-a reference at eps = 1 -> V == 0 (spin-freezing mechanism).

Formulas follow coherent_states.py / positivity.py of the lqg-scattering
reference implementation exactly (momentum-map Z, Taylor-exponential
Perelomov state, De Pietri / Rovelli-Smolin commutator). Operators are
built once per N as scipy.sparse CSR matrices on the occupation basis;
only the matrix elements (not the physics) differ from the reference.

Only numpy + scipy are used. Writes t5b_results.json next to this script.
"""

import itertools
import json

import numpy as np
import scipy.sparse as sp

GAMMA = 0.2375
HBAR = 1.0
TRIPLE = (0, 1, 2)


# --------------------------------------------------------------------------
# Occupation basis + sparse operators
# --------------------------------------------------------------------------

def _bounded_compositions(nvars, maxsum):
    """All nvars-tuples of nonneg ints with sum <= maxsum (stars/bars)."""
    out = []
    buf = [0] * nvars

    def rec(p, rem):
        if p == nvars - 1:
            for v in range(rem + 1):
                buf[p] = v
                out.append(tuple(buf))
            return
        for v in range(rem + 1):
            buf[p] = v
            rec(p + 1, rem - v)

    rec(0, maxsum)
    return out


class OpSpace:
    """Schwinger Fock space (total bosons <= K_max) with sparse operators.

    E_ij = a_i^dagger a_j + b_i^dagger b_j, J_i su(2) generators, and
    A_ij = J_i . J_j are precomputed once as CSR matrices.
    """

    def __init__(self, N, K_max):
        self.N = N
        self.K_max = K_max
        occs = _bounded_compositions(2 * N, K_max)
        self.dim = len(occs)
        self.index = {occ: i for i, occ in enumerate(occs)}

        def ladder(edge, dag, species):
            # species 0 -> a, 1 -> b; returns CSR matrix of the 1-body op
            off = 2 * edge + species
            rows, cols, data = [], [], []
            for c, occ in enumerate(occs):
                n = occ[off]
                if dag:
                    lst = list(occ)
                    lst[off] = n + 1
                    tgt = tuple(lst)
                    if tgt in self.index:
                        rows.append(self.index[tgt])
                        cols.append(c)
                        data.append(np.sqrt(n + 1))
                elif n > 0:
                    lst = list(occ)
                    lst[off] = n - 1
                    rows.append(self.index[tuple(lst)])
                    cols.append(c)
                    data.append(np.sqrt(n))
            return sp.csr_matrix((data, (rows, cols)),
                                 shape=(self.dim, self.dim))

        self.E = {}
        adag = [ladder(e, True, 0) for e in range(N)]
        a = [ladder(e, False, 0) for e in range(N)]
        bdag = [ladder(e, True, 1) for e in range(N)]
        b = [ladder(e, False, 1) for e in range(N)]
        for i in range(N):
            for j in range(N):
                self.E[(i, j)] = adag[i] @ a[j] + bdag[i] @ b[j]

        self.Jz, self.Jp, self.Jm = [], [], []
        for e in range(N):
            z = sp.diags(
                [0.5 * (occ[2 * e] - occ[2 * e + 1]) for occ in occs],
                format="csr")
            self.Jz.append(z)
            self.Jp.append(adag[e] @ b[e])    # a^dagger b
            self.Jm.append(bdag[e] @ a[e])    # b^dagger a

        self.A = {}
        for i in range(N):
            for j in range(N):
                self.A[(i, j)] = (self.Jz[i] @ self.Jz[j]
                                  + 0.5 * (self.Jp[i] @ self.Jm[j]
                                           + self.Jm[i] @ self.Jp[j]))

    def amat(self, Z):
        """A(Z) = sum_ij Z_ij E_ij as CSR."""
        out = sp.csr_matrix((self.dim, self.dim), dtype=complex)
        for (i, j), Eij in self.E.items():
            z = Z[i, j]
            if z != 0:
                out = out + z * Eij
        return out

    def ref_vec(self, ref_occupations):
        v = np.zeros(self.dim, dtype=complex)
        v[self.index[tuple(int(x) for pair in ref_occupations
                           for x in pair)]] = 1.0
        return v

    @staticmethod
    def taylor_exp(A, ref_vec, K, tol=1e-12):
        result = ref_vec.copy()
        term = ref_vec.copy()
        for n in range(1, 2 * K + 4):
            term = (A @ term) / n
            inc = float(np.linalg.norm(term))
            result = result + term
            if inc < tol * max(1.0, float(np.linalg.norm(result))):
                break
        return result / np.linalg.norm(result)


def volume_on_vec(vec, space, triple=(0, 1, 2), gamma=GAMMA, hbar=HBAR):
    i, j, k = triple
    Aij, Ajk = space.A[(i, j)], space.A[(j, k)]
    v_ij = Aij @ vec
    v_jk = Ajk @ vec
    q_vec = 1j * (Aij @ v_jk - Ajk @ v_ij)
    q_exp = complex(vec.conj() @ q_vec)
    V = (gamma * hbar) ** 1.5 * float(np.sqrt(abs(q_exp)))
    return V, q_exp


# --------------------------------------------------------------------------
# Grassmannian side
# --------------------------------------------------------------------------

def positive_plane_curve(N, seed=0, t_min=0.2, t_max=3.0):
    """Real positive plane: columns (t_i, t_i^2), minors > 0."""
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(t_min, t_max, size=N))
    return np.stack([t, t * t])


def plane_to_Z(plane):
    """Momentum map Gr(2,N) -> u(N)*: Z = a b^dagger - b a^dagger."""
    plane = np.asarray(plane, dtype=complex)
    a, b = plane
    a = a / np.linalg.norm(a)
    b = b - a * (a.conj() @ b)
    nb = np.linalg.norm(b)
    if nb < 1e-14:
        raise ValueError("plane rows are parallel")
    b = b / nb
    return np.outer(a, b.conj()) - np.outer(b, a.conj())


def vertex_reference(N, triple=(0, 1, 2)):
    """One a-boson per edge + one b-boson on each triple edge (K = N+3)."""
    ref = np.zeros((N, 2), dtype=int)
    ref[:, 0] = 1
    ref[list(triple), 1] = 1
    return ref


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
    eps = np.asarray(eps, float)
    V = np.asarray(V, float)
    m = V > 0
    alpha, logc = np.polyfit(np.log(eps[m]), np.log(V[m]), 1)
    y = np.log(V[m])
    yp = alpha * np.log(eps[m]) + logc
    ss_res = float(np.sum((y - yp) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(alpha), float(np.exp(logc)), float(r2)


def main():
    epsilons = np.geomspace(1e-6, 1.0, 13)  # 1e-6 .. 1.0, 13 points
    triple = TRIPLE
    out = {"epsilons": epsilons.tolist(), "triple": list(triple),
           "gamma": GAMMA, "hbar": HBAR, "n": {}}

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

    with open("t5b_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote t5b_results.json", flush=True)

    print("\n=== T5b verdict ===", flush=True)
    for Ns in ("4", "5"):
        d = out["n"][Ns]
        print(f"n={Ns}: alpha={d['alpha']:.4f}, R^2={d['r2']:.6f}, "
              f"V(1e-6)={d['V'][0]:.3e}, V(1)={d['V'][-1]:.3e}", flush=True)
    print("alpha ~ 0.5 with clean single power law => chirality turns on "
          "smoothly (no threshold/barrier); alpha >= 1 or slope drift at "
          "small eps would indicate quantization/barrier.", flush=True)


if __name__ == "__main__":
    main()

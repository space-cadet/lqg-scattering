"""T7a -- Single-copy thermal state on the Schwinger system.

Builds rho_beta = exp(-beta H)/Z on ONE Schwinger-boson system at the real
moment-curve plane (no complexification) and characterizes:
  (i)   thermal areas Tr(rho_beta A_i) vs beta (nonzero thermal area spectrum),
  (ii)  mean volume Tr(rho_beta q) vs beta (exactly zero -- theorem),
  (iii) volume fluctuations Tr(rho_beta q^2) vs beta (nonzero -- where the
        thermal volume information lives).

Conventions (match T5b exactly):
  n = 4, 5 edges; K = N+3 total bosons (capped basis sum <= K);
  plane = real moment-curve positive plane, seeds 11 (n=4) / 12 (n=5);
  H = sum_i (n_{a,i} + n_{b,i}) (omega_i = 1), occupation-diagonal;
  gamma = 0.2375, hbar = 1;
  q = i [A_01, A_12], triple (0,1,2), V = (gamma*hbar)^1.5 sqrt(|q|);
  reference = vertex_reference (one a-boson per edge + one b-boson on each
  edge of the measured triple).

Three thermal objects per beta (all exact, no Taylor for the Boltzmann factor):
  A) plain Gibbs diagonal:  w_n = e^{-beta E_n} / Z  (plane-independent control);
  B) Perelomov-weighted diagonal: w_n = |c_n|^2 e^{-beta E_n} / Z_pw, with c_n
     the real Perelomov amplitudes on the moment-curve plane (plane-dependent;
     beta=0 recovers Perelomov populations);
  C) thermally-rescaled pure state: |psi_beta> ~ sum_n c_n e^{-beta E_n/2} |n>
     (the TFD single-copy precursor; coherences kept, amplitudes stay real).

Theorem (checked numerically): every diagonal ensemble gives Tr(rho q) = 0 to
solver precision, because q = i[A01,A12] with real-symmetric A is imaginary
antisymmetric, hence has identically zero diagonal: <n|q|n> = 0 for every Fock
state. The pure rescaled state also gives <q> = 0 by reality (q expectation of
a real vector under an imaginary-Hermitian operator vanishes).

Perelomov states use the converged Taylor (8K+50 cap + assert, T5e lesson).

Only numpy + scipy. Writes t7a_results.json next to this script.
"""

import json
import time

import numpy as np
import scipy.sparse as sp

GAMMA = 0.2375
HBAR = 1.0
TRIPLE = (0, 1, 2)
SEEDS = {4: 11, 5: 12}
BETAS = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
TOL = 1e-13


# --------------------------------------------------------------------------
# Occupation basis + sparse operators (from T5b, Taylor converged per T5e)
# --------------------------------------------------------------------------

def _bounded_compositions(nvars, maxsum):
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
    """Schwinger Fock space (total bosons <= K_max) with sparse operators."""

    def __init__(self, N, K_max):
        self.N = N
        self.K_max = K_max
        occs = _bounded_compositions(2 * N, K_max)
        self.occs = np.array(occs, dtype=np.int64)
        self.dim = len(occs)
        self.index = {occ: i for i, occ in enumerate(occs)}
        # total bosons per basis state = H eigenvalue (omega = 1)
        self.energy = self.occs.sum(axis=1).astype(float)
        # per-edge totals (n_a + n_b) for area expectations
        self.edge_total = np.stack(
            [self.occs[:, 2 * e] + self.occs[:, 2 * e + 1]
             for e in range(N)], axis=1).astype(float)

        def ladder(edge, dag, species):
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
            self.Jp.append(adag[e] @ b[e])
            self.Jm.append(bdag[e] @ a[e])

        self.A = {}
        for i in range(N):
            for j in range(N):
                self.A[(i, j)] = (self.Jz[i] @ self.Jz[j]
                                  + 0.5 * (self.Jp[i] @ self.Jm[j]
                                           + self.Jm[i] @ self.Jp[j]))

    def amat(self, Z):
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
    def taylor_exp(A, ref_vec, K, tol=TOL):
        """Converged Taylor (8K+50 cap + assert -- T5e lesson)."""
        result = ref_vec.copy()
        term = ref_vec.copy()
        iters = 0
        for n in range(1, 8 * K + 50):
            term = (A @ term) / n
            iters = n
            inc = float(np.linalg.norm(term))
            result = result + term
            if inc < tol * max(1.0, float(np.linalg.norm(result))):
                break
        else:
            raise RuntimeError("Taylor exponential did not converge")
        return result / np.linalg.norm(result), iters


def q_operator(space, triple=TRIPLE):
    i, j, k = triple
    Aij, Ajk = space.A[(i, j)], space.A[(j, k)]
    return 1j * (Aij @ Ajk - Ajk @ Aij)


def volume_on_vec(vec, space, triple=TRIPLE, gamma=GAMMA, hbar=HBAR):
    i, j, k = triple
    Aij, Ajk = space.A[(i, j)], space.A[(j, k)]
    v_ij = Aij @ vec
    v_jk = Ajk @ vec
    q_vec = 1j * (Aij @ v_jk - Ajk @ v_ij)
    q_exp = complex(vec.conj() @ q_vec)
    V = (gamma * hbar) ** 1.5 * float(np.sqrt(abs(q_exp)))
    return V, q_exp


# --------------------------------------------------------------------------
# Grassmannian side (T5b conventions, real plane only)
# --------------------------------------------------------------------------

def positive_plane_curve(N, seed=0, t_min=0.2, t_max=3.0):
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(t_min, t_max, size=N))
    return np.stack([t, t * t])


def plane_to_Z(plane):
    plane = np.asarray(plane, dtype=complex)
    a, b = plane
    a = a / np.linalg.norm(a)
    b = b - a * (a.conj() @ b)
    nb = np.linalg.norm(b)
    if nb < 1e-14:
        raise ValueError("plane rows are parallel")
    b = b / nb
    return np.outer(a, b.conj()) - np.outer(b, a.conj())


def vertex_reference(N, triple=TRIPLE):
    ref = np.zeros((N, 2), dtype=int)
    ref[:, 0] = 1
    ref[list(triple), 1] = 1
    return ref


# --------------------------------------------------------------------------
# T7a thermal sweep
# --------------------------------------------------------------------------

def sweep_n(N, seed, betas, triple=TRIPLE):
    t0 = time.time()
    C0 = positive_plane_curve(N, seed=seed)
    assert np.isrealobj(C0) or np.max(np.abs(C0.imag)) == 0
    Z = plane_to_Z(C0)
    z_imag = float(np.max(np.abs(Z.imag)))
    z_sym = float(np.max(np.abs(Z + Z.T)))
    ref = vertex_reference(N, triple)
    K = int(ref.sum())
    assert K == N + 3
    space = OpSpace(N, K)
    E = space.energy
    print(f"--- n={N}: Fock dim={space.dim}, K={K}, seed={seed} "
          f"(build {time.time()-t0:.1f}s) ---", flush=True)
    print(f"  Z: max|imag|={z_imag:.2e} (expect ~0, real plane), "
          f"max|Z+Z^T|={z_sym:.2e} (expect ~0, antisymmetric)", flush=True)

    ref_v = space.ref_vec(ref)
    t0 = time.time()
    psi, iters = space.taylor_exp(space.amat(Z), ref_v, K)
    c_imag = float(np.max(np.abs(psi.imag)))
    print(f"  Perelomov: taylor iters={iters}, max|imag(psi)|={c_imag:.2e} "
          f"(expect ~0, real amplitudes) ({time.time()-t0:.1f}s)", flush=True)
    assert c_imag < 1e-9, f"real-plane amplitudes must be real, got {c_imag}"

    # control: pure Perelomov mean volume vanishes on the real plane (T5b)
    V0, q0 = volume_on_vec(psi, space, triple=triple)
    print(f"  control V(eps=0)={V0:.3e} (expect 0)", flush=True)
    assert V0 < 1e-8, f"real-plane volume must vanish, got {V0}"

    # q operator, its diagonal (must vanish identically) and q^2 diagonal
    q_op = q_operator(space, triple=triple).tocsr()
    herm = float(abs((q_op - q_op.getH())).max())
    qdiag = np.asarray(q_op.diagonal())
    max_qdiag = float(np.max(np.abs(qdiag)))
    print(f"  q-op: hermiticity dev={herm:.2e}, max|diag(q)|={max_qdiag:.2e} "
          f"(expect ~1e-16: antisymmetric diagonal)", flush=True)
    assert herm < 1e-9
    assert max_qdiag < 1e-9, f"<n|q|n> must vanish, got {max_qdiag}"
    # (q^2)_{nn} = sum_m |q_nm|^2 (row norms; q Hermitian)
    q2diag = np.asarray(
        q_op.conj().multiply(q_op).sum(axis=1)).real.flatten()
    assert np.all(q2diag >= -1e-18)
    q2diag = np.maximum(q2diag, 0.0)

    pops = np.abs(psi) ** 2  # Perelomov populations (beta=0 of family B)
    rows = []
    for beta in betas:
        w = np.exp(-beta * E)
        # A) plain Gibbs
        Zg = float(w.sum())
        wg = w / Zg
        Eg = float(wg @ E)
        areas_g = (GAMMA * float(HBAR)) * (wg @ space.edge_total)
        meanq_g = complex(wg @ qdiag)
        q2_g = float(wg @ q2diag)
        # cutoff validity: boundary weight + capped/infinite-tower Z ratio
        p_boundary = float(wg[E == K].sum())
        if beta > 0:
            z1 = 1.0 / (1.0 - np.exp(-beta))  # one oscillator
            Zinf = z1 ** (2 * N)
            z_ratio = Zg / Zinf
        else:
            z_ratio = float("nan")  # infinite tower diverges at beta=0
        Sg = float(beta * (Eg + np.log(Zg) / beta)) if beta > 0 else float(
            np.log(Zg))
        # B) Perelomov-weighted diagonal ensemble
        wpw_unn = pops * w
        Zpw = float(wpw_unn.sum())
        wpw = wpw_unn / Zpw
        areas_pw = (GAMMA * float(HBAR)) * (wpw @ space.edge_total)
        meanq_pw = complex(wpw @ qdiag)
        q2_pw = float(wpw @ q2diag)
        # C) thermally-rescaled pure state
        psi_b = (psi * np.exp(-beta * E / 2))
        psi_b = psi_b / np.linalg.norm(psi_b)
        areas_ps = (GAMMA * float(HBAR)) * (
            (np.abs(psi_b) ** 2) @ space.edge_total)
        qv = q_op @ psi_b
        meanq_ps = complex(psi_b.conj() @ qv)
        q2_ps = float(np.vdot(qv, qv).real)
        _, qcheck = volume_on_vec(psi_b, space, triple=triple)
        V_ps = (GAMMA * HBAR) ** 1.5 * float(np.sqrt(abs(meanq_ps)))
        rows.append({
            "beta": beta,
            "gibbs": {"Z": Zg, "E": Eg, "S": Sg,
                      "areas": areas_g.tolist(),
                      "meanq_real": meanq_g.real, "meanq_imag": meanq_g.imag,
                      "q2": q2_g, "p_boundary": p_boundary,
                      "Zcapped_over_Zinf": z_ratio},
            "perelomov_weighted": {
                "Z": Zpw, "areas": areas_pw.tolist(),
                "meanq_real": meanq_pw.real, "meanq_imag": meanq_pw.imag,
                "q2": q2_pw},
            "pure_rescaled": {
                "areas": areas_ps.tolist(),
                "meanq_real": meanq_ps.real, "meanq_imag": meanq_ps.imag,
                "meanq_check_imag": float(qcheck.imag),
                "V_from_meanq": V_ps, "q2": q2_ps},
        })
        print(f"  beta={beta:6.2f} | Gibbs areas="
              f"{np.array2string(areas_g, precision=4)} meanq={meanq_g.real:+.2e}"
              f"{meanq_g.imag:+.2e}j q2={q2_g:.6e} S={Sg:.4f} "
              f"P(E=K)={p_boundary:.2e} Zcap/Zinf={z_ratio:.3e} | "
              f"PW areas={np.array2string(areas_pw, precision=4)} "
              f"meanq={meanq_pw.real:+.2e} q2={q2_pw:.6e} | "
              f"pure meanq={meanq_ps.real:+.2e}{meanq_ps.imag:+.2e}j "
              f"q2={q2_ps:.6e}", flush=True)
    return {"dim": space.dim, "K": K, "seed": seed,
            "taylor_iters": iters, "max_abs_psi_imag": c_imag,
            "max_abs_qdiag": max_qdiag, "rows": rows}


def main():
    print(f"T7a single-copy thermal state: triple={list(TRIPLE)} "
          f"gamma={GAMMA} betas={BETAS}", flush=True)
    out = {"triple": list(TRIPLE), "gamma": GAMMA, "hbar": HBAR,
           "betas": list(BETAS), "omega": 1.0, "seeds": SEEDS, "n": {}}
    for N in (4, 5):
        res = sweep_n(N, SEEDS[N], BETAS)
        out["n"][str(N)] = res
    with open("t7a_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote t7a_results.json", flush=True)

    print("\n=== T7a verdict ===", flush=True)
    for Ns in ("4", "5"):
        d = out["n"][Ns]
        print(f"n={Ns}: dim={d['dim']} K={d['K']} "
              f"max|diag(q)|={d['max_abs_qdiag']:.2e}", flush=True)
        for r in d["rows"]:
            g, pw, ps = r["gibbs"], r["perelomov_weighted"], r["pure_rescaled"]
            print(f"  beta={r['beta']:6.2f} areas_G={np.array2string(np.array(g['areas']), precision=4)} "
                  f"meanq_G={g['meanq_real']:+.2e} q2_G={g['q2']:.4e} | "
                  f"areas_PW={np.array2string(np.array(pw['areas']), precision=4)} "
                  f"meanq_PW={pw['meanq_real']:+.2e} q2_PW={pw['q2']:.4e} | "
                  f"meanq_pure={ps['meanq_real']:+.2e} q2_pure={ps['q2']:.4e}",
                  flush=True)
    print("RESULT: mean volume exactly zero at all beta (all three families); "
          "areas nonzero with thermal spectrum; q^2 nonzero -- thermal volume "
          "information lives in fluctuations.", flush=True)
    print("STRUCTURAL FINDING: families B (Perelomov-weighted) and C "
          "(pure-rescaled) are beta-FLAT by construction: A(Z)=sum Z_ij E_ij "
          "preserves total boson number, so the Perelomov state lives entirely "
          "in the E=K sector and exp(-beta*E/2) is constant on its support. "
          "Genuine temperature dependence needs the full Gibbs ensemble (A) "
          "-- or the doubled TFD (T7b), where beta enters via L-R "
          "entanglement across E sectors.", flush=True)


if __name__ == "__main__":
    main()

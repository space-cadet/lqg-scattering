"""Two calculations of P(q,S) for the uniform four-face, two-FL J=1 squeeze.

Method A: explicit coupling of spins of face groups (1,2) and (3,4).
Method B: magnetic probabilities from oscillator occupation moments, followed
by P(q,S)=(2S+1)[W_q(S)-W_q(S+1)].
Independent small-sector checks use per-mode matrix exponentials and ordinary
Schwinger Casimir projectors. Agent: GPT 6.1 Sol, 2026-10-08.
"""
from pathlib import Path
from math import comb, exp, sqrt, fsum
from functools import lru_cache
import csv
import json
import platform
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.special import gammaln

N = 4
BETAS = (0.5, 1.0, 2.0, 4.0, 8.0)  # b=beta*hbar*omega
QMAX = 160
SMALL_QMAX = 4
PAIR_CUTOFFS = (40, 64)
ABS_TOL = 2e-12
INDEPENDENT_TOL = 2e-11
OUT = Path(__file__).resolve().parents[2] / "results" / "thermal-j1-spin"


def coupling_data(q):
    """Enumerate all group-spin couplings without magnetic counting."""
    arrays = [[] for _ in range(5)]
    for a in range(q + 1):
        for sa2 in range(a % 2, a + 1, 2):
            sb2 = np.arange((q-a) % 2, q-a+1, 2)
            sa = sa2 / 2
            f = (a/2-sa)*(a/2+sa+1)
            low = (np.abs(sa2-sb2)-q % 2)//2
            high = (sa2+sb2-q % 2)//2+1
            arrays[0].append(low)
            arrays[1].append(high)
            arrays[2].append((sa2+1)*(sb2+1))
            arrays[3].append(np.full(len(sb2), a))
            arrays[4].append(np.full(len(sb2), f))
    return tuple(np.concatenate(parts) for parts in arrays)


def recoupling_probabilities(q, b, data=None):
    low, high, multiplicity, a, f = coupling_data(q) if data is None else data
    x = exp(-b)
    eta = -np.expm1(-b)
    h = eta**2*f/2-eta*x*a/2+x*x
    # Each (s_A,s_B) contributes once to every S in its coupling interval.
    size = q//2+2
    weights = multiplicity*h*h
    changes = (np.bincount(low, weights=weights, minlength=size)
               - np.bincount(high, weights=weights, minlength=size))
    spin_counts = np.cumsum(changes)[:-1]
    s2 = np.arange(q % 2, q+1, 2)
    return eta**8*exp(-b*(q-2))*(s2+1)*spin_counts


def magnetic_weight(q, m2, b):
    """Sum squared occupation amplitudes using stars-and-bars moments.

    Coefficient operator: C_q=eta^4*t^(q-2)(uX+vA+wI),
    X=F^dagger F, A=number on faces 1,2. Compute trace of its square
    at fixed magnetic number without recoupling or Casimir eigenvectors.
    """
    if abs(m2) > q or (q+m2) % 2:
        return 0.0
    na = (q+m2)//2
    nb = q-na
    dimension = comb(na+3, 3)*comb(nb+3, 3)
    p = na*nb
    # Uniform compositions of each species over four faces.
    mean_a = q/2
    mean_a2 = (3*q*q+2*q-p)/10
    mean_x = p/8
    mean_xa = p*(3*q+4)/40
    mean_x2 = p*(6*p+9*q+26)/200
    eta = -np.expm1(-b)
    x = exp(-b)
    u, v, w = eta**2/2, -eta*x/2, x*x
    mean_square = fsum((u*u*mean_x2, v*v*mean_a2, w*w,
                        2*u*v*mean_xa, 2*u*w*mean_x, 2*v*w*mean_a))
    return eta**8*exp(-b*(q-2))*dimension*mean_square


def magnetic_probabilities(q, b):
    s2 = np.arange(q % 2, q+1, 2)
    return np.array([(twice_s+1)*(magnetic_weight(q, int(twice_s), b)
                     - magnetic_weight(q, int(twice_s)+2, b)) for twice_s in s2])


@lru_cache(None)
def occupations(q, modes=8):
    if modes == 1:
        return ((q,),)
    return tuple((n,)+rest for n in range(q+1) for rest in occupations(q-n, modes-1))


@lru_cache(None)
def sector_operators(q):
    basis = np.array(occupations(q))
    index = {tuple(n): i for i, n in enumerate(basis)}
    plus = np.zeros((len(basis), len(basis)))
    for col, state in enumerate(basis):
        for a in (0, 2, 4, 6):
            if state[a+1]:
                dest = state.copy()
                dest[a] += 1
                dest[a+1] -= 1
                plus[index[tuple(dest)], col] += sqrt((state[a]+1)*state[a+1])
    m = basis[:, ::2].sum(axis=1)-q/2
    generators = ((plus+plus.T)/2, (plus-plus.T)/(2j), np.diag(m))
    casimir = sum(g@g for g in generators)
    vals, vecs = np.linalg.eigh(casimir)
    projectors = []
    for s2 in range(q % 2, q+1, 2):
        s = s2/2
        v = vecs[:, np.isclose(vals, s*(s+1), atol=1e-10, rtol=0)]
        projectors.append(v)
    assert sum(v.shape[1] for v in projectors) == len(basis)
    return basis, generators, projectors


def reference_input():
    return [((1,0,0,1,0,0,0,0), 1/sqrt(2)),
            ((0,1,1,0,0,0,0,0), -1/sqrt(2))]


def mode_squeezes(b, cutoff):
    """Bounded two-mode exponentials, independent of the coefficient polynomial."""
    theta = np.arctanh(exp(-b/2))
    result = {}
    for n in (0, 1):
        for m in (0, 1):
            difference = n-m
            pairs = [(k+max(difference, 0), k+max(-difference, 0)) for k in range(cutoff+1)]
            plus = np.zeros((cutoff+1, cutoff+1))
            for k in range(cutoff):
                plus[k+1, k] = sqrt((pairs[k][0]+1)*(pairs[k][1]+1))
            unitary = expm(theta*(plus-plus.T))
            column = pairs.index((n,m))
            table = np.zeros((cutoff+2, cutoff+2))
            for k, pair in enumerate(pairs):
                table[pair] = unitary[k, column]
            result[n,m] = table
    return result


def coefficient_from_modes(q, tables, input_state=None):
    basis = sector_operators(q)[0]
    state = reference_input() if input_state is None else input_state
    C = np.zeros((len(basis), len(basis)), complex)
    for left, fl in state:
        for right, fr in state:
            contribution = np.full(C.shape, fl*np.conjugate(fr), complex)
            for mode in range(8):
                contribution *= tables[left[mode],right[mode]][basis[:,mode,None],basis[None,:,mode]]
            C += contribution
    return C


def coefficient_polynomial(q, b):
    basis = sector_operators(q)[0]
    F = np.zeros((len(occupations(q-2)), len(basis))) if q >= 2 else None
    if F is not None:
        index = {n: i for i,n in enumerate(occupations(q-2))}
        for col, n in enumerate(basis):
            for a, c, sign in ((0,3,1), (1,2,-1)):
                if n[a] and n[c]:
                    dest = n.copy()
                    dest[a] -= 1
                    dest[c] -= 1
                    F[index[tuple(dest)],col] += sign*sqrt(n[a]*n[c])
    FF = F.T@F if F is not None else np.zeros((len(basis),len(basis)))
    x = exp(-b)
    eta = -np.expm1(-b)
    A = np.diag(basis[:,:4].sum(axis=1))
    return eta**4*exp(-b*(q-2)/2)*(eta**2*FF/2-eta*x*A/2+x*x*np.eye(len(basis)))


def tail_bound(b, power=0, return_log=False):
    """Upper bound beyond QMAX from a positive polynomial occupation envelope.

    |uX+vA+w| <= u*q(q+2)/4+|v|q+w; multiply by g_q.
    The geometric ratio bound also covers weighting by q**power.
    """
    q = QMAX+1
    x = exp(-b)
    eta = -np.expm1(-b)
    u, v, w = eta**2/2, -eta*x/2, x*x
    envelope = u*q*(q+2)/4+abs(v)*q+w
    log_dimension = gammaln(q+8)-gammaln(8)-gammaln(q+1)
    log_first = 8*np.log(eta)-b*(q-2)+log_dimension+2*np.log(envelope)+power*np.log(q)
    ratio = x*(q+8)/(q+1)*((q+1)/q)**(4+power)
    assert ratio < 1
    log_bound = float(log_first-np.log1p(-ratio))
    return log_bound if return_log else exp(log_bound)


def small_sector_checks(b):
    low, high = [mode_squeezes(b, cutoff) for cutoff in PAIR_CUTOFFS]
    maxima = {name: 0.0 for name in ("pair_cutoff_coefficient_difference", "polynomial_coefficient_difference",
               "casimir_probability_difference", "magnetic_occupation_difference", "combined_closure_relative_residual")}
    for q in range(SMALL_QMAX+1):
        basis, generators, projectors = sector_operators(q)
        C = coefficient_from_modes(q, high)
        D = coefficient_from_modes(q, low)
        maxima["pair_cutoff_coefficient_difference"] = max(maxima["pair_cutoff_coefficient_difference"], float(np.max(abs(C-D))))
        maxima["polynomial_coefficient_difference"] = max(maxima["polynomial_coefficient_difference"], float(np.max(abs(C-coefficient_polynomial(q,b)))))
        rho = C@C.conj().T
        direct = np.array([np.trace(v.conj().T@rho@v).real for v in projectors])
        maxima["casimir_probability_difference"] = max(maxima["casimir_probability_difference"], float(np.max(abs(direct-recoupling_probabilities(q,b)))))
        m2 = 2*basis[:,::2].sum(axis=1)-q
        diagonal = np.sum(abs(C)**2, axis=1)
        for M2 in range(-q,q+1,2):
            weight = float(diagonal[m2==M2].sum())
            maxima["magnetic_occupation_difference"] = max(maxima["magnetic_occupation_difference"], abs(weight-magnetic_weight(q,M2,b)))
        residual = sum(np.linalg.norm(g@C-C@g)**2 for g in generators)/max(np.linalg.norm(C)**2,1e-300)
        maxima["combined_closure_relative_residual"] = max(maxima["combined_closure_relative_residual"], float(residual))
    assert maxima["combined_closure_relative_residual"] < 1e-20
    assert all(value < INDEPENDENT_TOL for key,value in maxima.items() if key != "combined_closure_relative_residual"), maxima
    return maxima


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_probs = {b: [] for b in BETAS}
    max_difference = 0.0
    min_probability = 0.0
    rows = []
    for q in range(QMAX+1):
        data = coupling_data(q)
        for b in BETAS:
            a = recoupling_probabilities(q,b,data)
            m = magnetic_probabilities(q,b)
            error = float(np.max(abs(a-m)))
            max_difference = max(max_difference,error)
            min_probability = min(min_probability,float(a.min()),float(m.min()))
            assert error < ABS_TOL, (q,b,error)
            assert min(a.min(),m.min()) > -ABS_TOL
            all_probs[b].append(a)
            p_q = float(a.sum())
            for s2, pa, pm in zip(range(q % 2,q+1,2),a,m):
                rows.append((b,q,s2/2,float(pa),float(pm),float(pa-pm),float(pa/p_q) if p_q else 0.0))
        if q in (0,40,80,120,160):
            print(f"Compared both methods through q={q}", flush=True)
    summaries = []
    for b in BETAS:
        probs = all_probs[b]
        norm = fsum(float(p.sum()) for p in probs)
        mean_q = fsum(q*float(p.sum()) for q,p in enumerate(probs))
        analytic_mean_q = 2+12/np.expm1(b)
        closure = fsum(float(np.dot((np.arange(q % 2,q+1,2)/2)*(np.arange(q % 2,q+1,2)/2+1),p)) for q,p in enumerate(probs))
        bounds = {f"q_power_{k}": tail_bound(b,k) for k in (0,1,2)}
        log_bounds = {f"q_power_{k}": tail_bound(b,k,return_log=True)/np.log(10) for k in (0,1,2)}
        assert abs(1-norm) <= bounds["q_power_0"]+ABS_TOL
        assert abs(mean_q-analytic_mean_q) <= bounds["q_power_1"]+ABS_TOL*max(1,analytic_mean_q)
        independent = small_sector_checks(b)
        summaries.append({"beta_hbar_omega": b, "retained_probability": norm,
                          "mean_q_retained": mean_q, "mean_q_analytic": float(analytic_mean_q),
                          "mean_per_copy_closure_casimir_retained": closure,
                          "singlet_probability_retained": fsum(float(probs[q][0]) for q in range(0,QMAX+1,2)),
                          "tail_upper_bounds": bounds, "tail_log10_upper_bounds": log_bounds,
                          "tail_bound_underflow": bounds["q_power_0"] == 0,
                          "independent_checks": independent})
        print(f"b={b:g}: PASS; normalization={norm:.16g}; mean q={mean_q:.8g}; tail bound={bounds['q_power_0']:.3g}",flush=True)
    with (OUT/"j1_spin_method_comparison.csv").open("w",newline="") as handle:
        writer = csv.writer(handle,lineterminator="\n")
        writer.writerow(("beta_hbar_omega","q_bosons_per_copy","total_spin_S","P_q_S_recoupling","P_q_S_magnetic","difference","P_S_given_q"))
        writer.writerows(rows)
    report = {"agent": "GPT 6.1 Sol", "date": "2026-10-08", "initial_J": 1, "faces": N,
              "input": "normalized F12^dagger vacuum in each copy, conjugate paired",
              "support": "full oscillator Fock space, no per-copy singlet projection",
              "observable": "ordinary per-copy resultant spin",
              "q_max": QMAX,"beta_hbar_omega_values": BETAS,"abs_tolerance": ABS_TOL,
              "independent_abs_tolerance": INDEPENDENT_TOL,"pair_matrix_cutoffs": PAIR_CUTOFFS,
              "independent_check_q_max": SMALL_QMAX,"max_method_absolute_difference": max_difference,
              "min_computed_probability": min_probability,"temperature_results": summaries,
              "python": platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__}
    (OUT/"j1_spin_method_summary.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(f"PASS: maximum method difference={max_difference:.3g}; wrote {len(rows)} comparison rows.")


if __name__ == "__main__":
    main()

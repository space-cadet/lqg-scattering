"""Spin distribution in one copy of the N=4, initial-J=0 squeezed vacuum.

At fixed boson number q the reduced density matrix is I_q / dim(H_q).
Spin multiplicity is D(q,M=S)-D(q,M=S+1), where D counts magnetic states.
No separate singlet projection. All spin operators are in units hbar=1.
Agent: GPT 6.1 Sol. Recorded 2026-10-08.
"""
from pathlib import Path
from math import comb, sqrt
from fractions import Fraction
import csv
import json
import platform

import numpy as np
import scipy
from scipy.stats import nbinom
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

N = 4
B = 1.0  # beta*hbar*omega; frozen before evaluating the figure
QMAX = 26  # previously established tail <= 1e-6 at B=1
OUT = Path(__file__).resolve().parents[2] / "figures" / "thermal-spin-sectors"


def magnetic_dimension(q, twice_m):
    if abs(twice_m) > q or (q + twice_m) % 2:
        return 0
    a = (q + twice_m) // 2
    b = q - a
    return comb(a + N - 1, N - 1) * comb(b + N - 1, N - 1)


def weyl_dimension(q, twice_s):
    weights = [(q + twice_s) // 2, (q - twice_s) // 2] + [0] * (N - 2)
    result = Fraction(1)
    for i in range(N):
        for j in range(i + 1, N):
            result *= Fraction(weights[i] - weights[j] + j - i, j - i)
    assert result.denominator == 1
    return result.numerator


def occupations(total, modes):
    if modes == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for rest in occupations(total - first, modes - 1):
                yield (first,) + rest


def independent_spectrum(q):
    """Direct Schwinger G^2 matrices, independent of representation counting."""
    basis = list(occupations(q, 2 * N))
    index = {state: i for i, state in enumerate(basis)}
    plus = np.zeros((len(basis), len(basis)))
    m = np.zeros(len(basis))
    for col, state in enumerate(basis):
        m[col] = sum(state[::2]) - q / 2
        for face in range(N):
            a, b = 2 * face, 2 * face + 1
            if state[b]:
                dest = list(state)
                dest[a] += 1
                dest[b] -= 1
                plus[index[tuple(dest)], col] += sqrt((state[a] + 1) * state[b])
    casimir = np.diag(m * m) + (plus @ plus.T + plus.T @ plus) / 2
    values = np.linalg.eigvalsh(casimir)
    result = {}
    for twice_s in range(q % 2, q + 1, 2):
        s = twice_s / 2
        result[twice_s] = int(np.count_nonzero(np.isclose(values, s * (s + 1), atol=1e-10, rtol=0)))
    assert sum(result.values()) == len(basis)
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    q_values = np.arange(QMAX + 1)
    p_q = nbinom.pmf(q_values, 2 * N, -np.expm1(-B))
    conditional = np.zeros((QMAX + 1, QMAX + 1))
    mean_s, casimir_mean, rows = [], [], []
    for q in q_values:
        dimension = comb(int(q) + 2 * N - 1, 2 * N - 1)
        counts = {}
        for twice_s in range(int(q) % 2, int(q) + 1, 2):
            multiplicity = magnetic_dimension(int(q), twice_s) - magnetic_dimension(int(q), twice_s + 2)
            assert multiplicity == weyl_dimension(int(q), twice_s)
            count = (twice_s + 1) * multiplicity
            counts[twice_s] = count
            prob = count / dimension
            conditional[twice_s, q] = prob
            rows.append((int(q), q / 2, twice_s / 2, multiplicity, count, dimension, prob, p_q[q], prob * p_q[q]))
        assert sum(counts.values()) == dimension
        assert abs(conditional[:, q].sum() - 1) < 1e-14
        if q <= 4:
            assert independent_spectrum(int(q)) == counts
        spins = np.arange(QMAX + 1) / 2
        mean_s.append(float(spins @ conditional[:, q]))
        casimir_mean.append(float((spins * (spins + 1)) @ conditional[:, q]))
        expected = 3 * q * (q + 2 * N) / (4 * (2 * N + 1))
        assert abs(casimir_mean[-1] - expected) < 1e-12

    tail = float(nbinom.sf(QMAX, 2 * N, -np.expm1(-B)))
    joint = conditional * p_q[None, :]
    assert abs(joint.sum() + tail - 1) < 2e-14
    assert tail <= 1e-6
    assert nbinom.sf(QMAX - 1, 2 * N, -np.expm1(-B)) > 1e-6
    plt.rcParams.update({"font.size": 10, "axes.labelsize": 11, "axes.titlesize": 11,
                         "legend.fontsize": 9, "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.3), layout="constrained")
    extent = (-.5, QMAX + .5, -.25, QMAX / 2 + .25)
    im = axes[0].imshow(np.ma.masked_equal(conditional, 0), origin="lower", aspect="auto",
                        extent=extent, cmap="viridis", vmin=0, vmax=1, interpolation="none")
    axes[0].set_title(r"Spin distribution at fixed $q$")
    fig.colorbar(im, ax=axes[0], label=r"$P(S\mid q)$", shrink=.84)
    im = axes[1].imshow(np.ma.masked_equal(joint, 0), origin="lower", aspect="auto",
                        extent=extent, cmap="magma", norm=LogNorm(vmin=1e-8, vmax=.1), interpolation="none")
    axes[1].set_title(r"Thermal weight: $\beta\hbar\omega=1$")
    fig.colorbar(im, ax=axes[1], label=r"$P(q,S)$ (log scale)", shrink=.84)
    for ax in axes[:2]:
        ax.set(xlabel=r"Bosons in one copy $q$", ylabel=r"Total spin of that copy $S$", ylim=(-.25, QMAX / 2 + .25))
        ax.set_facecolor("#eeeeee")
        ax.plot(q_values, q_values / 2, color="#45a7db", ls="--", lw=1.2)
    axes[2].plot(q_values, mean_s, color="#0072B2", lw=2, label=r"Mean $\langle S\rangle_q$")
    axes[2].plot(q_values, np.sqrt(casimir_mean), color="#D55E00", ls="-.", lw=2,
                 label=r"Closure magnitude $\sqrt{\langle S(S+1)\rangle_q}$")
    axes[2].plot(q_values, q_values / 2, color="#666666", ls="--", label=r"Maximum spin $q/2$")
    axes[2].set(xlabel=r"Bosons in one copy $q$", ylabel="Spin / angular-momentum magnitude", title="Conditional means and closure", xlim=(0, QMAX), ylim=(0, QMAX / 2 + .5))
    axes[2].legend(frameon=False, loc="upper left")
    axes[2].grid(alpha=.2)
    axes[2].spines[["top", "right"]].set_visible(False)
    fig.suptitle(r"Four-face squeezed vacuum: initial area $J_{\rm in}=0$" + "\nOrdinary per-copy spin; no singlet projection. Grey cells have zero probability.", fontsize=12)
    fig.savefig(OUT / "thermal_vacuum_spin.pdf")
    fig.savefig(OUT / "thermal_vacuum_spin.png", dpi=300)
    plt.close(fig)
    with (OUT / "thermal_vacuum_spin.csv").open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("q_bosons_per_copy", "area_label", "total_spin_S", "spin_multiplicity", "spin_sector_dimension", "occupation_sector_dimension", "P_S_given_q", "P_q", "P_q_S"))
        writer.writerows(rows)
    summary = {"agent": "GPT 6.1 Sol", "date": "2026-10-08", "initial_J": 0,
               "faces": N, "beta_hbar_omega": B, "q_max": QMAX, "discarded_probability": tail,
               "support": "full oscillator Fock space; no separate per-copy singlet projection",
               "observable": "ordinary resultant spin of one copy, not combined or transformed spin",
               "conditional_state": "I_q / binomial(q+2N-1, 2N-1)",
               "analytic_casimir_mean": "3q(q+2N)/(4(2N+1))",
               "checks": ["magnetic counting equals Weyl dimension at every plotted q,S",
                          "all spin counts sum to exact occupation-sector dimension",
                          "direct Schwinger Casimir eigenspectra q=0,1,2,3,4",
                          "analytic conditional Casimir mean at every q",
                          "joint normalization including exact omitted tail; minimal q cutoff"],
               "python": platform.python_version(), "numpy": np.__version__,
               "scipy": scipy.__version__, "matplotlib": matplotlib.__version__,
               "mean_S_by_q": mean_s, "mean_casimir_by_q": casimir_mean}
    (OUT / "thermal_vacuum_spin_summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(f"PASS: spin decomposition, independent q<=4 Casimir spectra, moments, normalization; tail={tail:.3g}")
    print(f"Figure: {OUT / 'thermal_vacuum_spin.png'}")


if __name__ == "__main__":
    main()

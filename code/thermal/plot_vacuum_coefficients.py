"""Exact N=4, J=0 squeezed-vacuum occupation coefficients; no FL pilot data.

b = beta*hbar*omega, t = exp(-b/2), q = bosons per copy.
Each matched occupation vector has amplitude (1-t**2)**N * t**q.
Sector probability includes binomial(q+2*N-1, 2*N-1) multiplicity.
"""
from pathlib import Path
import csv
import json
import platform
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import gammaln
from scipy.stats import nbinom
import scipy

OUT = Path(__file__).resolve().parents[2] / "figures" / "thermal-area-sectors"
OUT.mkdir(parents=True, exist_ok=True)
N = 4
B_VALUES = (2.0, 1.0, 0.5, 0.25)
Q = np.arange(241)
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7")
STYLES = ("-", "--", "-.", ":")
plt.rcParams.update({"font.size": 10, "axes.labelsize": 11,
                     "axes.titlesize": 11, "legend.fontsize": 9,
                     "pdf.fonttype": 42, "ps.fonttype": 42})
fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), layout="constrained")
rows = []
summaries = []
for b, color, style in zip(B_VALUES, COLORS, STYLES):
    x = np.exp(-b)
    success = -np.expm1(-b)
    coefficient = success**N * np.exp(-b*Q/2)
    log_mult = gammaln(Q+2*N)-gammaln(2*N)-gammaln(Q+1)
    probability = np.exp(log_mult + 2*np.log(coefficient))
    tail = nbinom.sf(Q, 2*N, success)
    assert np.allclose(probability, nbinom.pmf(Q, 2*N, success), rtol=2e-12)
    long_q = np.arange(2001)
    weights = nbinom.pmf(long_q, 2*N, success)
    assert abs(weights.sum()-1) < 2e-12
    mean = 2*N*x/success
    assert abs(np.dot(long_q, weights)-mean) < 2e-10
    assert np.all(np.diff(tail) <= 0)
    cutoff = int(nbinom.ppf(1-1e-6, 2*N, success))
    assert nbinom.sf(cutoff, 2*N, success) <= 1e-6
    assert cutoff == 0 or nbinom.sf(cutoff-1, 2*N, success) > 1e-6
    print(f"b={b:g}: mean q={mean:.3f}; smallest cutoff for tail <=1e-6: {cutoff}")
    summaries.append({"beta_hbar_omega": b, "mean_q": float(mean),
                      "mode_q": int(np.argmax(probability)),
                      "cutoff_tail_1e_minus_6": cutoff,
                      "tail_at_cutoff": float(nbinom.sf(cutoff, 2*N, success))})
    label = rf"$b={b:g}$"
    axes[0].semilogy(Q, coefficient, color=color, ls=style, label=label)
    axes[1].plot(Q, probability, color=color, ls=style, label=label)
    axes[2].semilogy(Q, tail, color=color, ls=style, label=label)
    rows.extend((b, int(q), c, p, e) for q,c,p,e in zip(Q, coefficient, probability, tail))

axes[0].set(title="Individual matched-basis amplitude", xlabel=r"Bosons per copy $q$",
            ylabel=r"$C_{\mathbf{n},\mathbf{n}}$, $|\mathbf{n}|=q$", xlim=(0,100), ylim=(1e-14,1))
axes[1].set(title="Total occupation-sector probability", xlabel=r"Bosons per copy $q$",
            ylabel=r"$p_q$ (includes multiplicity)", xlim=(0,100), ylim=(0,None))
axes[2].set(title="Probability discarded by a cutoff", xlabel=r"Maximum retained occupation $q_{\max}$",
            ylabel=r"$\Pr(q>q_{\max})$", xlim=(0,200), ylim=(1e-10,1))
axes[2].axhline(1e-6, color="#666666", lw=1, ls="--")
axes[2].text(196, 1.5e-6, r"$10^{-6}$", ha="right", color="#555555")
for ax in axes:
    ax.grid(True, alpha=.2)
    ax.spines[["top", "right"]].set_visible(False)
axes[1].legend(title=r"$b=\beta\hbar\omega$", frameon=False)
fig.suptitle("Exact squeezed vacuum: four faces, initial J = 0\nSmaller b means higher temperature; q/2 is the total area label", fontsize=12)
fig.savefig(OUT/"thermal_coefficients_vacuum.pdf")
fig.savefig(OUT/"thermal_coefficients_vacuum.png", dpi=300)
with (OUT/"thermal_coefficients_vacuum.csv").open("w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(("beta_hbar_omega", "bosons_per_copy", "individual_amplitude", "sector_probability", "tail_probability"))
    writer.writerows(rows)
with (OUT/"thermal_coefficients_vacuum_summary.json").open("w") as f:
    json.dump({"construction": "same-mode two-copy squeezed vacuum",
               "hilbert_space": "full oscillator Fock space, no per-copy singlet projection",
               "initial_J": 0, "faces": N, "modes_per_copy": 2*N,
               "q_min": int(Q[0]), "q_max": int(Q[-1]), "q_step": 1,
               "normalization_check_q_max": 2000, "tail_tolerance": 1e-6,
               "python": platform.python_version(), "numpy": np.__version__,
               "scipy": scipy.__version__, "matplotlib": matplotlib.__version__,
               "temperature_results": summaries}, f, indent=2, allow_nan=False)
    f.write("\n")
print("PASS: coefficient/multiplicity formula, normalization, mean, monotone tails, minimal cutoffs.")

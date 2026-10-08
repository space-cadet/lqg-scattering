"""Plot the saved J=1 method comparison; no rerun of the physics calculation.

Agent: GPT 6.1 Sol, 2026-10-08. Exports vector PDF and 300-DPI PNG.
"""
from pathlib import Path
import csv
import json
import hashlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results" / "thermal-j1-spin"
OUT = ROOT / "figures" / "thermal-j1-spin"
Q_DISPLAY = 60
SPIN_DISPLAY = 20
MAP_FLOOR = 1e-10
COLORS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#333333")
STYLES = ("-", "--", "-.", ":", "-")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = json.loads((DATA / "j1_spin_method_summary.json").read_text())
    betas = report["beta_hbar_omega_values"]
    qmax = report["q_max"]
    shape = (qmax+1, qmax+1)
    a = {b: np.zeros(shape) for b in betas}
    m = {b: np.zeros(shape) for b in betas}
    csv_path = DATA / "j1_spin_method_comparison.csv"
    with csv_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            b = float(row["beta_hbar_omega"])
            q = int(row["q_bosons_per_copy"])
            s2 = int(round(2*float(row["total_spin_S"])))
            a[b][s2, q] = float(row["P_q_S_recoupling"])
            m[b][s2, q] = float(row["P_q_S_magnetic"])
    diagnostics = []
    for entry in report["temperature_results"]:
        b = entry["beta_hbar_omega"]
        assert np.min(a[b]) >= 0 and np.min(m[b]) >= 0
        assert abs(a[b].sum()-entry["retained_probability"]) < 2e-14
        assert abs(a[b][0].sum()-entry["singlet_probability_retained"]) < 2e-14
        assert np.max(abs(a[b]-m[b])) < report["abs_tolerance"]
        diagnostics.append({"beta_hbar_omega": b,
                            "occupation_probability_outside_display": float(a[b][:,Q_DISPLAY+1:].sum()),
                            "spin_probability_outside_display": float(a[b][2*SPIN_DISPLAY+1:,:].sum()),
                            "map_probability_below_display_floor_in_window": float(a[b][:Q_DISPLAY+1,:Q_DISPLAY+1][a[b][:Q_DISPLAY+1,:Q_DISPLAY+1] < MAP_FLOOR].sum()),
                            "singlet_probability": float(a[b][0].sum())})

    plt.rcParams.update({"font.size": 10, "axes.labelsize": 11, "axes.titlesize": 11,
                         "legend.fontsize": 9, "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1,3,figsize=(12,4.0),layout="constrained")
    q = np.arange(qmax+1)
    spin = q/2
    for b, color, style in zip(betas, COLORS, STYLES):
        label = rf"$b={b:g}$"
        pq_a, pq_m = a[b].sum(axis=0), m[b].sum(axis=0)
        ps_a, ps_m = a[b].sum(axis=1), m[b].sum(axis=1)
        axes[0].plot(q,pq_a,color=color,ls=style,lw=1.8,label=label)
        sample = np.arange(0,Q_DISPLAY+1,3)
        axes[0].plot(q[sample],pq_m[sample],color=color,ls="none",marker="o",ms=3.5,mfc="none")
        axes[1].plot(spin,ps_a,color=color,ls=style,lw=1.8)
        sample = np.arange(0,2*SPIN_DISPLAY+1,2)
        axes[1].plot(spin[sample],ps_m[sample],color=color,ls="none",marker="o",ms=3.5,mfc="none")
    axes[0].set(title="Occupation distribution",xlabel=r"Bosons in one copy $q$",ylabel=r"$p_q=\sum_S P(q,S)$",xlim=(-.5,Q_DISPLAY),ylim=(0,None))
    axes[1].set(title="Ordinary per-copy total spin",xlabel=r"Resultant spin $S$",ylabel=r"$P(S)=\sum_q P(q,S)$",xlim=(-.25,SPIN_DISPLAY),ylim=(0,None))
    axes[0].legend(title=r"$b=\beta\hbar\omega$",frameon=False)
    temp = np.array([1/b for b in betas])
    singlet = np.array([a[b][0].sum() for b in betas])
    order = np.argsort(temp)
    axes[2].plot(temp[order],singlet[order],color="#555555",ls="--",lw=1)
    for b,color in zip(betas,COLORS):
        axes[2].plot(1/b,a[b][0].sum(),"o",color=color,ms=6)
    axes[2].set(title="Probability of separate closure",xlabel=r"Temperature $k_B T/(\hbar\omega)=1/b$",ylabel=r"$\Pr(S=0)$ in one copy",xlim=(0,2.08),ylim=(0,1.04))
    axes[2].text(.95,.88,"Points: calculated temperatures\nDashed line: guide to the eye",transform=axes[2].transAxes,ha="right",va="top",fontsize=8.5)
    for ax in axes:
        ax.grid(alpha=.2)
        ax.spines[["top","right"]].set_visible(False)
    fig.suptitle(r"Four-face two-FL squeezed state: initial area $J_{\rm in}=1$"+"\nLines: spin coupling; open circles: magnetic counting. Smaller b means higher temperature.",fontsize=12)
    fig.savefig(OUT/"j1_spin_temperature.pdf")
    fig.savefig(OUT/"j1_spin_temperature.png",dpi=300)
    plt.close(fig)

    fig, axes = plt.subplots(2,2,figsize=(8.2,6.6),layout="constrained",sharex=True,sharey=True)
    for ax,b in zip(axes.flat,(.5,1.,2.,8.)):
        window = a[b][:Q_DISPLAY+1,:Q_DISPLAY+1]
        image = ax.imshow(np.ma.masked_less(window,MAP_FLOOR),origin="lower",aspect="auto",
                          extent=(-.5,Q_DISPLAY+.5,-.25,Q_DISPLAY/2+.25),
                          norm=LogNorm(vmin=MAP_FLOOR,vmax=1),cmap="magma",interpolation="none")
        ax.set_facecolor("#eeeeee")
        ax.set_title(rf"$b={b:g}$; $\Pr(S=0)={a[b][0].sum():.4f}$")
        ax.set_xlabel(r"Bosons in one copy $q$")
        ax.set_ylabel(r"Resultant spin $S$")
        ax.plot(np.arange(Q_DISPLAY+1),np.arange(Q_DISPLAY+1)/2,color="#0072B2",ls="--",lw=1)
    fig.colorbar(image,ax=axes.ravel().tolist(),label=r"Joint probability $P(q,S)$ (log scale)",shrink=.9)
    fig.suptitle(r"Spin and occupation together: initial $J_{\rm in}=1$"+"\nOrdinary per-copy spin; no singlet projection. Grey: probability below $10^{-10}$ or forbidden.",fontsize=11)
    fig.savefig(OUT/"j1_spin_joint_maps.pdf")
    fig.savefig(OUT/"j1_spin_joint_maps.png",dpi=300)
    plt.close(fig)
    metadata = {"agent":"GPT 6.1 Sol","date":"2026-10-08","source_csv":str(csv_path.relative_to(ROOT)),
                "source_csv_sha256":hashlib.sha256(csv_path.read_bytes()).hexdigest(),
                "q_calculated_max":qmax,"q_display_max":Q_DISPLAY,"spin_display_max":SPIN_DISPLAY,
                "joint_map_probability_floor":MAP_FLOOR,"temperature_results":diagnostics,
                "max_method_difference":report["max_method_absolute_difference"],
                "normalization":"original joint probabilities; no display renormalization",
                "checks":["nonnegative arrays","marginal normalization against calculation summary",
                          "singlet probabilities against summary","agreement of input method arrays"],
                "matplotlib":matplotlib.__version__}
    (OUT/"j1_spin_plot_summary.json").write_text(json.dumps(metadata,indent=2,allow_nan=False)+"\n")
    print("PASS: plotted arrays, normalization, singlet marginals, and method agreement.")
    print("Exported two vector PDFs and two 300-DPI PNGs.")
    print(f"Largest occupation probability outside q<=60: {max(d['occupation_probability_outside_display'] for d in diagnostics):.3g}")


if __name__ == "__main__":
    main()

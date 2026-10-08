"""Plot saved complete-basis volumes; no physics calculation is rerun."""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/"results"/"closed-basis-volume"
OUT = ROOT/"figures"/"closed-basis-volume"


def main():
    summary = json.loads((DATA/"summary.json").read_text())
    stats = []
    hashes = []
    for report in summary["areas"]:
        path = DATA/report["states_csv"]
        with path.open() as handle:
            states = list(csv.DictReader(handle))
        assert len(states) == report["basis_states"]
        mean = np.array([float(s["rs_mean"]) for s in states])
        seconds = np.array([float(s["rs_second_moment"]) for s in states])
        active = np.array([s["all_four_faces_active"] == "True" for s in states])
        assert np.isclose(mean.mean(), report["equal_weight_closed_rs_mean"], rtol=0, atol=2e-13)
        variance = seconds.mean()-mean.mean()**2
        assert variance >= -2e-13
        stats.append({"K": report["K"], "mean_all": float(mean.mean()),
                      "sd_all": float(np.sqrt(max(0, variance))), "mean_active": float(mean[active].mean()),
                      "active_states": int(active.sum()),
                      "nonzero_expectation_fraction": float((mean > summary["absolute_tolerance"]).mean())})
        hashes.append({"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "axes.titlesize": 12,
                         "legend.fontsize": 9, "pdf.fonttype": 42, "ps.fonttype": 42})
    k = np.array([s["K"] for s in stats])
    mean = np.array([s["mean_all"] for s in stats])
    active = np.array([s["mean_active"] for s in stats])
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), layout="constrained")
    for y, label, color, marker, style in [(mean, "All closed states", "#0072B2", "o", "-"),
                                          (active, "Four active faces", "#D55E00", "s", "--")]:
        axes[0].plot(k, y, label=label, color=color, marker=marker, ls=style, lw=1.7)
        axes[1].plot(k, summary["units"]["geometric_rs_factor"]*y/k**1.5,
                     label=label, color=color, marker=marker, ls=style, lw=1.7)
    axes[0].set(title="Equal-weight fixed-area volume", ylabel=r"$\mathrm{Tr}(V_{\mathrm{RS}})/d$ (raw units)")
    axes[1].set(title="Area-normalized mean", ylabel=r"$\kappa_{\mathrm{RS}}\langle V\rangle/K^{3/2}$")
    for ax in axes:
        ax.set(xlabel=r"Total linear area $K$", xticks=k, ylim=(0, None))
        ax.tick_params(axis="x", labelsize=9)
        ax.grid(alpha=.25); ax.legend()
    fig.savefig(OUT/"fixed_area_ensemble_volume.pdf")
    fig.savefig(OUT/"fixed_area_ensemble_volume.png", dpi=300)
    plt.close(fig)
    low = [a for a in summary["areas"] if a["K"] <= 4]
    fig, axes = plt.subplots(1, len(low), figsize=(10.4, 3.6), layout="constrained", squeeze=False)
    for ax, report in zip(axes[0], low):
        with (DATA/report["states_csv"]).open() as handle:
            states = list(csv.DictReader(handle))
        values = np.array([float(s["rs_mean"]) for s in states])
        spreads = np.array([float(s["rs_sd"]) for s in states])
        indices = np.arange(1, len(states)+1)
        ax.plot(indices, values, "o", color="#0072B2", ms=3, label=r"$\langle V\rangle$")
        ax.plot(indices, spreads, "x", color="#D55E00", ms=3, label=r"$\sigma_V$")
        ax.set(title=f"K = {report['K']}: {len(states)} basis states", xlabel="Basis-state index",
               ylim=(-.015, .8)); ax.grid(alpha=.25)
    axes[0, 0].set_ylabel("RS volume (raw project units)")
    axes[0, 0].legend()
    fig.savefig(OUT/"basis_state_volumes_k2_k4.pdf")
    fig.savefig(OUT/"basis_state_volumes_k2_k4.png", dpi=300)
    plt.close(fig)
    (OUT/"plot_summary.json").write_text(json.dumps({"sources": hashes, "statistics": stats,
        "png_dpi": 300, "physics_rerun": False,
        "interpretation": "Equal-weight traces and recoupling basis expectations; not FL coherent-state curves or canonical-temperature results.",
        "checks": ["row counts", "ensemble means match metadata", "nonnegative ensemble variance"],
        "matplotlib": matplotlib.__version__}, indent=2)+"\n")
    print("OK: saved-data checks and two PDF/300-DPI PNG exports completed.")


if __name__ == "__main__":
    main()

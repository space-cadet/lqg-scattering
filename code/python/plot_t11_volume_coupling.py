"""Publication-size plots for the T11 positive-volume-coupling screen."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results/t11-volume-coupling"
OUT = DATA


def read_csv(name):
    with (DATA / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    thermal = read_csv("thermal_scan.csv")
    summaries = read_csv("summary.csv")
    references = read_csv("fl_reference_readouts.csv")
    colors = {-1.0: "#0072B2", 0.0: "#555555", 1.0: "#D55E00"}
    linestyles = {-1.0: "-", 0.0: "--", 1.0: "-."}
    labels = {-1.0: r"$α_V=-1$ (volume-favoring)",
              0.0: r"$α_V=0$ (baseline)",
              1.0: r"$α_V=+1$ (volume-penalizing)"}
    plt.rcParams.update({
        "font.size": 8.2,
        "axes.labelsize": 8.8,
        "axes.titlesize": 9.0,
        "legend.fontsize": 7.2,
        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.0,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.2))
    ax_v, ax_gv, ax_p0, ax_overlap = axes.flat

    # Thermal mean volume, plus the prepared-state readout references.
    for alpha in (-1.0, 0.0, 1.0):
        finite = [r for r in thermal if float(r["alpha_V"]) == alpha
                  and r["beta_t"] not in ("0.0", "inf")]
        beta = np.asarray([float(r["beta_t"]) for r in finite])
        mean_v = np.asarray([float(r["mean_volume_project_units"]) for r in finite])
        ax_v.plot(beta, mean_v, color=colors[alpha], linestyle=linestyles[alpha],
                  linewidth=1.7, label=labels[alpha])
        ground = next(r for r in thermal if float(r["alpha_V"]) == alpha
                      and r["beta_t"] == "inf")
        ax_v.scatter([1300], [float(ground["mean_volume_project_units"])],
                     marker="X", s=34, color=colors[alpha], zorder=5)
    ref_by_label = {r["reference"]: float(r["volume_mean_project_units"])
                    for r in references if float(r["alpha_V"]) == 0.0}
    ax_v.axhline(ref_by_label["regular"], color="#777777", linestyle=":", linewidth=1.0,
                 label="Regular FL reference")
    ax_v.axhline(ref_by_label["flat_boundary"], color="#999999", linestyle=(0, (4, 2)),
                 linewidth=1.0, label="Flat-boundary FL control")
    ax_v.set_xscale("log")
    ax_v.set_xlim(7e-4, 2e3)
    ax_v.set_ylim(0, 0.67)
    ax_v.set_xlabel(r"Inverse temperature, $\beta t$")
    ax_v.set_ylabel(r"Thermal mean $\langle V_{\rm RS}\rangle$ (project units)")
    ax_v.set_title("Thermal volume response")
    ax_v.grid(True, which="major", alpha=0.25)
    ax_v.grid(True, which="minor", axis="x", alpha=0.10)
    ax_v.text(0.03, 0.96, r"$\beta t=0$: 0.17556 for all three Hamiltonians",
              transform=ax_v.transAxes, va="top", fontsize=7.5)
    ax_v.legend(loc="best", frameon=True, ncol=1)
    ax_v.scatter([], [], marker="X", s=30, color="#333333", label=r"$\beta\to\infty$")
    handles, legend_labels = ax_v.get_legend_handles_labels()
    ax_v.legend(handles, legend_labels, loc="best", frameon=True, ncol=1)

    alphas = np.asarray([-1.0, 0.0, 1.0])
    summary_by_alpha = {float(r["alpha_V"]): r for r in summaries}
    ground_v = [float(summary_by_alpha[a]["ground_mean_volume_project_units"]) for a in alphas]
    ax_gv.plot(alphas, ground_v, color="#222222", marker="o", linewidth=1.5, markersize=5)
    ax_gv.set_xticks(alphas, [r"$-1$", r"$0$", r"$+1$"])
    ax_gv.set_xlabel(r"Volume coupling $\alpha_V$")
    ax_gv.set_ylabel(r"Ground-space mean $\langle V_{\rm RS}\rangle$")
    ax_gv.set_title("Ground-space volume")
    ax_gv.set_ylim(0, 0.67)
    ax_gv.grid(True, alpha=0.25)
    for x, y in zip(alphas, ground_v):
        ax_gv.annotate(f"{y:.3f}", (x, y), xytext=(0, 7), textcoords="offset points",
                       ha="center", fontsize=7.7)

    ground_p0 = [float(summary_by_alpha[a]["ground_probability_zero_volume"]) for a in alphas]
    ax_p0.plot(alphas, ground_p0, color="#7A5195", marker="s", linewidth=1.5, markersize=5)
    ax_p0.set_xticks(alphas, [r"$-1$", r"$0$", r"$+1$"])
    ax_p0.set_xlabel(r"Volume coupling $\alpha_V$")
    ax_p0.set_ylabel(r"Ground-space probability $P(V=0)$")
    ax_p0.set_title("Weight in the volume kernel")
    ax_p0.set_ylim(-0.03, 1.03)
    ax_p0.grid(True, alpha=0.25)
    for x, y in zip(alphas, ground_p0):
        ax_p0.annotate(f"{y:.4g}", (x, y), xytext=(0, 7), textcoords="offset points",
                       ha="center", fontsize=7.7)

    width = 0.32
    regular_overlap = []
    flat_overlap = []
    for alpha in alphas:
        rows = [r for r in references if float(r["alpha_V"]) == alpha]
        regular_overlap.append(float(next(r for r in rows if r["reference"] == "regular")
                                     ["ground_subspace_overlap_probability"]))
        flat_overlap.append(float(next(r for r in rows if r["reference"] == "flat_boundary")
                                  ["ground_subspace_overlap_probability"]))
    ax_overlap.bar(alphas - width / 2, regular_overlap, width, color="#009E73",
                   edgecolor="#222222", linewidth=0.5, label="Regular FL")
    ax_overlap.bar(alphas + width / 2, flat_overlap, width, color="#E69F00",
                   edgecolor="#222222", linewidth=0.5, hatch="//", label="Flat-boundary FL")
    ax_overlap.set_xticks(alphas, [r"$-1$", r"$0$", r"$+1$"])
    ax_overlap.set_xlabel(r"Volume coupling $\alpha_V$")
    ax_overlap.set_ylabel("Probability in ground eigenspace")
    ax_overlap.set_title("Prepared FL reference overlap")
    ax_overlap.set_ylim(0, 0.14)
    ax_overlap.grid(True, axis="y", alpha=0.25)
    ax_overlap.legend(loc="upper left", frameon=True)
    for x, y in zip(alphas - width / 2, regular_overlap):
        ax_overlap.annotate(f"{y:.3g}", (x, y), xytext=(0, 4), textcoords="offset points",
                            ha="center", fontsize=7.3)
    for x, y in zip(alphas + width / 2, flat_overlap):
        ax_overlap.annotate(f"{y:.3g}", (x, y), xytext=(0, 4), textcoords="offset points",
                            ha="center", fontsize=7.3)

    panel_letters = "abcd"
    for letter, ax in zip(panel_letters, axes.flat):
        ax.text(-0.12, 1.04, f"({letter})", transform=ax.transAxes,
                fontweight="bold", va="bottom")
    fig.suptitle(
        r"Tetrahedral $K=4$ singlets at $U/t=20$: $H=H_0+g_VV_{\rm RS}$",
        y=0.995, fontsize=10.5,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97), h_pad=1.6, w_pad=1.35)
    fig.savefig(OUT / "volume_coupling_response.pdf", bbox_inches="tight")
    fig.savefig(OUT / "volume_coupling_response.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Wrote vector PDF and 300-dpi PNG")


if __name__ == "__main__":
    main()

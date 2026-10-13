"""Publication-quality plots for T11's candidate-Hamiltonian comparison."""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "results/t11-candidate-hamiltonians"
COLORS_U = {
    0.0: "#0072B2",
    1.0: "#009E73",
    5.0: "#E69F00",
    20.0: "#D55E00",
}
COLORS_MODEL = {
    "baseline": "#444444",
    "V−": "#0072B2",
    "V+": "#56B4E9",
    "χ−": "#D55E00",
    "χ+": "#CC79A7",
}
ALPHA_STYLES = {-2.0: ":", -1.0: "-", -0.5: "--",
                0.0: "-.", 0.5: "--", 1.0: "-", 2.0: ":"}
def read_csv(name):
    with (DATA / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def save(fig, stem):
    fig.savefig(DATA / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(DATA / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def setup():
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


def plot_ground_state():
    summaries = read_csv("model_summary.csv")
    complete = [
        row for row in summaries
        if row["graph"] == "complete"
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.0))
    axes = axes.flat
    panels = (
        ("positive_volume", "ground_volume_mean_project_units",
         r"$\langle V_{\rm RS}\rangle_0$", "Volume term: ground volume"),
        ("positive_volume", "ground_probability_zero_volume",
         r"$P_0(V_{\rm RS}=0)$", "Volume term: kernel weight"),
        ("signed_grasp", "ground_volume_mean_project_units",
         r"$\langle V_{\rm RS}\rangle_0$", "Signed-grasp term: ground volume"),
        ("signed_grasp", "ground_Q_chi_mean",
         r"$\langle Q_\chi\rangle_0/\Delta Q_\chi$",
         "Signed-grasp term: oriented response"),
    )
    for panel, (candidate, field, ylabel, title) in zip(axes, panels):
        for u in (0.0, 1.0, 5.0, 20.0):
            rows = sorted(
                [
                    row for row in complete
                    if row["candidate"] == candidate
                    and float(row["U_over_t"]) == u
                ],
                key=lambda row: float(row["alpha"]),
            )
            if not rows:
                continue
            alpha = np.asarray([float(row["alpha"]) for row in rows])
            values = np.asarray([float(row[field]) for row in rows])
            if field == "ground_Q_chi_mean":
                span = float(rows[0]["operator_spectral_range"])
                values = values / span
            panel.plot(
                alpha, values, color=COLORS_U[u], linestyle="-",
                marker="o", markersize=3.0, linewidth=1.3,
                label=rf"$U/t={u:g}$",
            )
        panel.set_xlabel(r"Dimensionless coupling $\alpha$")
        panel.set_ylabel(ylabel)
        panel.set_title(title)
        panel.grid(True, alpha=0.25)
        panel.axvline(0, color="#999999", linewidth=0.7, linestyle=":")
    axes[1].set_ylim(-0.03, 1.03)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4,
               frameon=False, bbox_to_anchor=(0.5, 0.985))
    fig.suptitle(
        r"Tetrahedral $K=4$, $J=0$: ground-state response to candidate terms",
        y=1.025, fontsize=10.2,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=1.4, w_pad=1.2)
    save(fig, "candidate_ground_state_response")


def plot_ground_energy_shifts():
    summaries = [
        row for row in read_csv("model_summary.csv")
        if row["graph"] == "complete"
    ]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True)
    for axis, candidate, title in (
        (axes[0], "positive_volume", r"$H_V=H_0+g_VV_{\rm RS}$"),
        (axes[1], "signed_grasp", r"$H_\chi=H_0+\lambda_\chi Q_\chi$"),
    ):
        for u in (0.0, 1.0, 5.0, 20.0):
            rows = sorted(
                [
                    row for row in summaries
                    if row["candidate"] == candidate
                    and float(row["U_over_t"]) == u
                ],
                key=lambda row: float(row["alpha"]),
            )
            baseline = next(
                float(row["ground_energy"]) for row in rows
                if float(row["alpha"]) == 0.0
            )
            axis.plot(
                [float(row["alpha"]) for row in rows],
                [(float(row["ground_energy"]) - baseline) for row in rows],
                color=COLORS_U[u], linestyle="-", marker="o",
                markersize=3.0, linewidth=1.3, label=rf"$U/t={u:g}$",
            )
        axis.axhline(0, color="#777777", linewidth=0.8, linestyle=":")
        axis.axvline(0, color="#999999", linewidth=0.7, linestyle=":")
        axis.set_xlabel(r"Dimensionless coupling $\alpha$")
        axis.set_title(title)
        axis.grid(True, alpha=0.23)
    axes[0].set_ylabel(
        r"Hamiltonian ground-energy shift $(E_0(\alpha)-E_0(0))/t$"
    )
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4,
               frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle(
        r"Ground energy of the Hamiltonian, relative to its $H_0$ baseline",
        y=1.10, fontsize=10.2,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90), w_pad=1.3)
    save(fig, "candidate_ground_energy_shifts")


def plot_thermal_u20():
    rows = read_csv("thermal_scan.csv")
    selected = [
        row for row in rows
        if row["graph"] == "complete"
        and float(row["U_over_t"]) == 20.0
        and row["beta_t"] not in ("inf", "0")
    ]
    curves = {}
    for row in selected:
        alpha = float(row["alpha"])
        family = row["candidate"]
        if alpha not in (-1.0, 0.0, 1.0):
            continue
        if alpha == 0.0 and family == "signed_grasp":
            continue
        label = "baseline" if alpha == 0 else (
            "V−" if family == "positive_volume" and alpha < 0 else
            "V+" if family == "positive_volume" else
            "χ−" if alpha < 0 else "χ+"
        )
        curves.setdefault(label, []).append(row)
    order = ("baseline", "V−", "V+", "χ−", "χ+")
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.0))
    metrics = (
        ("mean_volume_project_units", r"$\langle V_{\rm RS}\rangle$",
         "Thermal positive volume"),
        ("probability_zero_volume", r"$P(V_{\rm RS}=0)$",
         "Volume-kernel probability"),
        ("mean_Q_chi", r"$\langle Q_\chi\rangle/\Delta Q_\chi$",
         "Signed-grasp response"),
        ("conditional_angle_rms_sd", "RMS angular standard deviation",
         "Four-face-conditioned shape fluctuations"),
    )
    styles = {
        "baseline": ("#444444", "-"),
        "V−": ("#0072B2", "-"),
        "V+": ("#56B4E9", "--"),
        "χ−": ("#D55E00", "-"),
        "χ+": ("#CC79A7", "--"),
    }
    for axis, (field, ylabel, title) in zip(axes.flat, metrics):
        for label in order:
            if label not in curves:
                continue
            line_rows = sorted(
                curves[label], key=lambda row: float(row["beta_t"])
            )
            if field == "mean_Q_chi":
                # The dimensionless signed-grasp coupling sets the Q scale.
                row0 = next(
                    row for row in line_rows
                    if float(row["alpha"]) == (-1 if label == "χ−" else 1)
                ) if label in ("χ−", "χ+") else None
                span = 13.856406460551025
                y = np.asarray([
                    float(row[field]) / span for row in line_rows
                ])
                if label not in ("baseline", "χ−", "χ+"):
                    continue
            else:
                y = np.asarray([float(row[field]) for row in line_rows])
            x = np.asarray([float(row["beta_t"]) for row in line_rows])
            color, style = styles[label]
            axis.plot(x, y, color=color, linestyle=style,
                      linewidth=1.4, label=label)
        axis.set_xscale("log")
        axis.set_xlabel(r"Inverse temperature $\beta t$")
        axis.set_ylabel(ylabel)
        axis.set_title(title)
        axis.grid(True, which="both", alpha=0.22)
        if field == "probability_zero_volume":
            axis.set_ylim(-0.03, 1.03)
        if field == "mean_Q_chi":
            axis.axhline(0, color="#888888", linewidth=0.7)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=5,
               frameon=False, bbox_to_anchor=(0.5, 0.985))
    fig.suptitle(
        r"Complete tetrahedral graph, $K=4$, $U/t=20$",
        y=1.025, fontsize=10.2,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94), h_pad=1.4, w_pad=1.2)
    save(fig, "candidate_thermal_response_u20")


def plot_ring_control():
    rows = read_csv("thermal_scan.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8), sharey=True)
    for axis, u in zip(axes, (5.0, 20.0)):
        for graph, alpha, label, color, linestyle in (
            ("complete", 0.0, "Complete, baseline", "#444444", "-"),
            ("ring", 0.0, "Ring, baseline", "#777777", "--"),
            ("complete", -1.0, "Complete, αV=−1", "#0072B2", "-"),
            ("ring", -1.0, "Ring, αV=−1", "#0072B2", "--"),
            ("complete", 1.0, "Complete, αV=+1", "#D55E00", "-"),
            ("ring", 1.0, "Ring, αV=+1", "#D55E00", "--"),
        ):
            curve = sorted(
                [
                    row for row in rows
                    if row["candidate"] == "positive_volume"
                    and row["graph"] == graph
                    and float(row["U_over_t"]) == u
                    and float(row["alpha"]) == alpha
                    and row["beta_t"] not in ("inf", "0")
                ],
                key=lambda row: float(row["beta_t"]),
            )
            axis.plot(
                [float(row["beta_t"]) for row in curve],
                [float(row["mean_volume_project_units"]) for row in curve],
                color=color, linestyle=linestyle, linewidth=1.3,
                label=label,
            )
        axis.set_xscale("log")
        axis.set_xlabel(r"Inverse temperature $\beta t$")
        axis.set_title(rf"$U/t={u:g}$")
        axis.grid(True, which="both", alpha=0.22)
    axes[0].set_ylabel(r"Thermal mean $V_{\rm RS}$ (project units)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle(
        r"Ring hopping as a topology control for $H_0+g_VV_{\rm RS}$",
        y=1.01, fontsize=10.2,
    )
    fig.tight_layout(rect=(0, 0.10, 1, 0.94), w_pad=1.1)
    save(fig, "ring_topology_control")


def plot_early_dynamics():
    rows = read_csv("dynamics_scan.csv")
    schedules = read_csv("dynamics_schedule.csv")
    schedule_by_key = {
        (row["model_id"], row["seed"]): row for row in schedules
        if float(row["U_over_t"]) == 20.0
    }
    # Output identifiers use m/p in place of the signs in alpha.
    by_id = {}
    for row in rows:
        if float(row["U_over_t"]) != 20.0:
            continue
        if row["candidate"] == "positive_volume" and float(row["alpha"]) in (-1.0, 1.0):
            label = "V−" if float(row["alpha"]) < 0 else "V+"
        elif row["candidate"] == "signed_grasp" and float(row["alpha"]) in (-1.0, 1.0):
            label = "χ−" if float(row["alpha"]) < 0 else "χ+"
        elif float(row["alpha"]) == 0.0:
            label = "baseline"
        else:
            continue
        by_id.setdefault((row["model_id"], row["seed"], label), []).append(row)

    seeds = (
        ("regular", r"Regular ($\varphi=90^\circ$)"),
        ("phi_60", r"$\varphi=60^\circ$"),
        ("phi_30", r"$\varphi=30^\circ$"),
        ("phi_10", r"$\varphi=10^\circ$"),
        ("flat_boundary", r"Flat boundary ($\varphi=0^\circ$)"),
    )
    fig, axes = plt.subplots(2, 5, figsize=(13.5, 5.8), sharex=True)
    metrics = (
        ("return_probability", "Return probability"),
        ("mean_volume_project_units", r"$\langle V_{\rm RS}\rangle$"),
    )
    for column, (seed, seed_title) in enumerate(seeds):
        for row_index, (field, title) in enumerate(metrics):
            axis = axes[row_index, column]
            for label in ("baseline", "V−", "V+", "χ−", "χ+"):
                if label == "baseline":
                    model_id = "complete_positive_volume_U20_alphap0"
                elif label in ("V−", "V+"):
                    suffix = "m1" if label == "V−" else "p1"
                    model_id = f"complete_positive_volume_U20_alpha{suffix}"
                else:
                    suffix = "m1" if label == "χ−" else "p1"
                    model_id = f"complete_signed_grasp_U20_alpha{suffix}"
                schedule = schedule_by_key.get((model_id, seed))
                data = by_id.get((model_id, seed, label))
                if schedule is None or data is None:
                    continue
                fastest = float(schedule["fastest_period"])
                dense = sorted([
                    row for row in data
                    if row["time_grid"] == "dense_fast_beat"
                ], key=lambda row: float(row["tau_t_over_hbar"]))
                color = COLORS_MODEL[label]
                linestyle = {
                    "baseline": "-",
                    "V−": "--",
                    "V+": ":",
                    "χ−": "-.",
                    "χ+": (0, (5, 2, 1, 2)),
                }[label]
                axis.plot(
                    [float(row["tau_t_over_hbar"]) / fastest for row in dense],
                    [float(row[field]) for row in dense],
                    color=color, linestyle=linestyle,
                    linewidth=1.3, label=label,
                )
            if row_index == 0:
                axis.set_title(seed_title, fontsize=8.4)
            if row_index == 1:
                axis.set_xlabel("Fastest-beat periods", fontsize=7.7)
            axis.grid(True, alpha=0.22)
            if row_index == 0:
                axis.set_ylim(-0.03, 1.03)
            if column == 0:
                axis.set_ylabel(title)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=5,
               loc="upper center", bbox_to_anchor=(0.5, 1.01))
    fig.suptitle(
        r"Exact early-time evolution, complete graph, $K=4$, $U/t=20$",
        y=1.08, fontsize=10.2,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.91), h_pad=1.4, w_pad=0.6)
    save(fig, "prepared_FL_early_dynamics_u20")


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    setup()
    plot_ground_energy_shifts()
    plot_ground_state()
    plot_thermal_u20()
    plot_ring_control()
    plot_early_dynamics()
    print("Wrote five vector PDF figures and 300-dpi PNG previews.")


if __name__ == "__main__":
    main()

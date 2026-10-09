"""Four-site fixed-area singlet studies for Bose-Hubbard hopping and volume.

K is total linear area, the fixed boson number is 2K, and the Hilbert space
is restricted to total SU(2) spin zero. The first pilot compares the complete
graph with the four-site ring at K=2,3,4 and g=0.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
import time
from pathlib import Path

import numpy as np
import scipy
import sympy

from lqg_scattering.singlets import ABS_TOL, GAMMA, ZERO_FACTOR
from project_paths import PROJECT_ROOT

from lqg_scattering.hamiltonian import (
    SITES, TRIPLES, weak_compositions, magnetic_basis, connected_triples,
    hopping_matrix, expected_closed_dimension, fixed_face_dimension,
    positive_face_dimension, infinite_temperature_counts, build_fixed_k,
)

from lqg_scattering.thermal import (
    grouped_values, thermal_weights, zero_volume_probabilities,
    mean_in_ground_subspace, site_zero_entanglement,
)


BETA_VALUES = (0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
DETAILED_BETA_VALUES = tuple(np.geomspace(1e-3, 1e3, 601))
CASES = (
    {"name": "no_hopping", "t": 0.0, "U": 1.0, "ratio": None},
    {"name": "free", "t": 1.0, "U": 0.0, "ratio": 0.0},
    {"name": "U1", "t": 1.0, "U": 1.0, "ratio": 1.0},
    {"name": "U5", "t": 1.0, "U": 5.0, "ratio": 5.0},
    {"name": "U20", "t": 1.0, "U": 20.0, "ratio": 20.0},
)
GRAPH_EDGES = {
    "complete": tuple(itertools.combinations(range(SITES), 2)),
    "ring": ((0, 1), (1, 2), (2, 3), (0, 3)),
}


def thermal_records(k, graph, case, hamiltonian, volume, active_sites, commutator):
    energies, energy_vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2)
    ground_mask = abs(energies - energies[0]) <= ABS_TOL
    excited = energies[energies > energies[0] + ABS_TOL]
    gap = float(excited[0] - energies[0]) if excited.size else None
    volume_eigenvalues, volume_vectors = np.linalg.eigh((volume + volume.conj().T) / 2)
    volume_eigenvalues = np.where(abs(volume_eigenvalues) <= ZERO_FACTOR * max(
        1.0, float(np.max(abs(volume_eigenvalues)))), 0.0, volume_eigenvalues)
    if float(np.min(volume_eigenvalues)) < -5e-9:
        raise AssertionError("the positive RS volume has a negative eigenvalue")
    outcome_groups = grouped_values(volume_eigenvalues)
    energy_to_volume = abs(volume_vectors.conj().T @ energy_vectors) ** 2
    grouped_energy_to_volume = np.asarray([
        energy_to_volume[group["indices"], :].sum(axis=0) for group in outcome_groups
    ])
    basis_probabilities = abs(energy_vectors) ** 2
    n_values = np.arange(1, SITES + 1)
    n_projectors = np.asarray([active_sites == n for n in n_values], dtype=float)
    energy_n_probabilities = basis_probabilities.T @ n_projectors.T
    volume_n_operators = [volume @ np.diag(projector) for projector in n_projectors]
    energy_vn_means = np.asarray([
        np.real(np.diag(energy_vectors.conj().T @ op @ energy_vectors))
        for op in volume_n_operators
    ])
    energy_v_means = np.real(np.diag(energy_vectors.conj().T @ volume @ energy_vectors))
    energy_v2_means = np.real(np.diag(energy_vectors.conj().T @ (volume @ volume) @ energy_vectors))
    zero_outcomes = [i for i, group in enumerate(outcome_groups)
                     if abs(group["value"]) <= ABS_TOL]
    energy_zero_probabilities = (grouped_energy_to_volume[zero_outcomes].sum(axis=0)
                                 if zero_outcomes else np.zeros(len(energies)))
    ground_weights = ground_mask.astype(float) / int(ground_mask.sum())
    ground_v = float(ground_weights @ energy_v_means)
    ground_v2 = float(ground_weights @ energy_v2_means)
    ground_n = ground_weights @ energy_n_probabilities
    ground_zero = float(ground_weights @ energy_zero_probabilities)
    commutator_norm_f = float(np.linalg.norm(commutator, ord="fro"))
    commutator_norm_2 = float(np.max(abs(np.linalg.eigvalsh(1j * commutator))))
    summary = {
        "K": k, "graph": graph, "case": case["name"], "t": case["t"], "U": case["U"],
        "U_over_t": case["ratio"], "g": 0.0,
        "dimension": len(energies), "ground_energy": float(energies[0]),
        "ground_degeneracy": int(ground_mask.sum()), "gap": gap,
        "ground_mean_volume": ground_v,
        "ground_volume_sd": math.sqrt(max(0.0, ground_v2 - ground_v ** 2)),
        "ground_probability_zero_volume": ground_zero,
        "ground_mean_active_sites": float(ground_n @ n_values),
        "ground_commutator_norm_frobenius": commutator_norm_f,
        "ground_commutator_norm_operator": commutator_norm_2,
    }
    thermodynamics, site_probabilities, volume_distribution = [], [], []
    for beta in (*BETA_VALUES, math.inf):
        weights, log_z = thermal_weights(energies, beta)
        energy_mean = float(weights @ energies)
        energy_variance = float(weights @ (energies ** 2) - energy_mean ** 2)
        entropy = float(-np.sum(weights[weights > 0] * np.log(weights[weights > 0])))
        volume_mean = float(weights @ energy_v_means)
        volume_second = float(weights @ energy_v2_means)
        n_prob = weights @ energy_n_probabilities
        vn_mean = energy_vn_means @ weights
        outcome_probabilities = grouped_energy_to_volume @ weights
        if abs(float(np.sum(n_prob)) - 1.0) > 5e-9:
            raise AssertionError("active-site probabilities do not sum to one")
        if abs(float(np.sum(outcome_probabilities)) - 1.0) > 5e-9:
            raise AssertionError("volume-outcome probabilities do not sum to one")
        thermodynamics.append({
            "K": k, "graph": graph, "case": case["name"], "t": case["t"], "U": case["U"],
            "U_over_t": case["ratio"], "beta": "inf" if math.isinf(beta) else beta,
            "log_partition": log_z,
            "mean_energy": energy_mean,
            "heat_capacity": 0.0 if math.isinf(beta) else beta ** 2 * max(0.0, energy_variance),
            "entropy": entropy,
            "mean_volume": volume_mean,
            "volume_sd": math.sqrt(max(0.0, volume_second - volume_mean ** 2)),
            "probability_zero_volume": float(weights @ energy_zero_probabilities),
            "mean_active_sites": float(n_prob @ n_values),
            "commutator_mean": 0.0,
        })
        for site_count, probability, volume_weight in zip(n_values, n_prob, vn_mean):
            site_probabilities.append({
                "K": k, "graph": graph, "case": case["name"],
                "beta": "inf" if math.isinf(beta) else beta,
                "active_sites": int(site_count), "probability": float(probability),
                "conditional_mean_volume": (float(volume_weight / probability)
                                             if probability > ABS_TOL else None),
            })
        for group_index, group in enumerate(outcome_groups):
            probability = float(outcome_probabilities[group_index])
            volume_distribution.append({
                "K": k, "graph": graph, "case": case["name"],
                "beta": "inf" if math.isinf(beta) else beta,
                "volume": float(group["value"]), "multiplicity": len(group["indices"]),
                "probability": probability,
            })
    return summary, thermodynamics, site_probabilities, volume_distribution, energies, energy_vectors


def k4_thermal_scan(k, graph, case, hamiltonian, volume, active_sites):
    """Dense K=4 scan to resolve the finite-temperature volume crossover."""
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2)
    volume_by_state = np.real(np.diag(vectors.conj().T @ volume @ vectors))
    zero_by_state = zero_volume_probabilities(volume, vectors)
    active_by_state = (abs(vectors) ** 2).T @ active_sites
    beta_grid = (0.0, *DETAILED_BETA_VALUES, math.inf)
    rows = []
    for beta in beta_grid:
        weights, _ = thermal_weights(energies, beta)
        energy_mean = float(weights @ energies)
        volume_mean = float(weights @ volume_by_state)
        covariance = float(weights @ (energies * volume_by_state)
                           - energy_mean * volume_mean)
        rows.append({
            "K": k, "graph": graph, "case": case["name"],
            "U_over_t": case["ratio"], "beta": "inf" if math.isinf(beta) else beta,
            "mean_energy": energy_mean,
            "mean_volume": volume_mean,
            "probability_zero_volume": float(weights @ zero_by_state),
            "mean_active_sites": float(weights @ active_by_state),
            "energy_volume_covariance": 0.0 if math.isinf(beta) else covariance,
            "d_mean_volume_d_beta": 0.0 if math.isinf(beta) else -covariance,
        })
    return rows


def energy_resolved_volume(k, graph, case, hamiltonian, volume, active_sites):
    """Trace observables over each degenerate energy eigenspace."""
    energies, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2)
    volume_by_state = np.real(np.diag(vectors.conj().T @ volume @ vectors))
    zero_by_state = zero_volume_probabilities(volume, vectors)
    active_by_state = (abs(vectors) ** 2).T @ active_sites
    rows = []
    for rank, group in enumerate(grouped_values(energies), start=1):
        indices = group["indices"]
        rows.append({
            "K": k, "graph": graph, "case": case["name"],
            "U_over_t": case["ratio"], "energy_rank": rank,
            "energy": float(np.mean(energies[indices])),
            "energy_above_ground": float(np.mean(energies[indices]) - energies[0]),
            "multiplicity": len(indices),
            "subspace_mean_volume": float(np.mean(volume_by_state[indices])),
            "subspace_probability_zero_volume": float(np.mean(zero_by_state[indices])),
            "subspace_mean_active_sites": float(np.mean(active_by_state[indices])),
        })
    return rows


def calculate_case(k, graph, case, model, selected_triples):
    edges = GRAPH_EDGES[graph]
    hopping = sum((model["bonds"][edge] for edge in edges),
                  np.zeros_like(model["onsite"]))
    hamiltonian = -case["t"] * hopping + case["U"] * model["onsite"]
    volume_terms = [model["volume_by_triple"][triple] for triple in selected_triples]
    volume = sum(volume_terms, np.zeros_like(model["onsite"]))
    h_hermiticity = float(np.max(abs(hamiltonian - hamiltonian.conj().T)))
    v_hermiticity = float(np.max(abs(volume - volume.conj().T)))
    if max(h_hermiticity, v_hermiticity) > 5e-9:
        raise AssertionError("projected Hamiltonian or volume is not Hermitian")
    h_u_comm = model["onsite"] @ volume - volume @ model["onsite"]
    commutator = hamiltonian @ volume - volume @ hamiltonian
    triple_commutators = [hamiltonian @ term - term @ hamiltonian for term in volume_terms]
    decomposition_residual = float(np.max(abs(commutator - sum(
        triple_commutators, np.zeros_like(commutator)
    ))))
    comm_parts = [case["t"] * sum(
        (model["bonds"][edge] @ term - term @ model["bonds"][edge]
         for edge in edges), np.zeros_like(term)
    ) * -1 for term in volume_terms]
    comm_parts_residual = float(np.max(abs(commutator - sum(
        comm_parts, np.zeros_like(commutator)
    ))))
    if max(float(np.max(abs(h_u_comm))), decomposition_residual, comm_parts_residual) > 5e-9:
        raise AssertionError("Hamiltonian-volume commutator identities failed numerically")
    state_summary, thermo, n_probs, v_distribution, energies, vectors = thermal_records(
        k, graph, case, hamiltonian, volume, model["active_sites"], commutator,
    )
    state_summary.update({
        "hamiltonian_hermiticity_max_abs": h_hermiticity,
        "volume_hermiticity_max_abs": v_hermiticity,
        "onsite_volume_commutator_max_abs": float(np.max(abs(h_u_comm))),
        "commutator_decomposition_max_abs": decomposition_residual,
        "commutator_edge_decomposition_max_abs": comm_parts_residual,
        "triple_cancellation_ratio": (
            float(np.linalg.norm(commutator, ord="fro"))
            / sum(float(np.linalg.norm(part, ord="fro")) for part in triple_commutators)
            if sum(float(np.linalg.norm(part, ord="fro")) for part in triple_commutators) > ABS_TOL
            else 0.0
        ),
    })
    ground_mask = abs(energies - energies[0]) <= ABS_TOL
    ground_entropy, ground_purity, reduced_trace_residual = site_zero_entanglement(
        model, vectors, ground_mask
    )
    if reduced_trace_residual > 5e-9:
        raise AssertionError("single-site reduced ground-state density has non-unit trace")
    state_summary["site0_ground_reduced_entropy"] = ground_entropy
    state_summary["site0_ground_reduced_purity"] = ground_purity
    state_summary["site0_ground_reduced_trace_residual"] = reduced_trace_residual
    correlation_rows = []
    closure_correlation_residual = 0.0
    for i in range(SITES):
        local_casimir = model["site_spins"][:, i] / 2
        local_casimir = local_casimir * (local_casimir + 1)
        local_mean = mean_in_ground_subspace(np.diag(local_casimir), vectors, ground_mask)
        pair_sum = 0.0
        for j in range(SITES):
            if i == j:
                continue
            pair = tuple(sorted((i, j)))
            spin_mean = mean_in_ground_subspace(model["spin_dots"][pair], vectors, ground_mask)
            pair_sum += spin_mean
            if i < j:
                number_product = model["site_spins"][:, i] * model["site_spins"][:, j]
                bond_present = pair in edges
                kinetic_mean = mean_in_ground_subspace(model["bonds"][pair], vectors, ground_mask)
                correlation_rows.append({
                    "K": k, "graph": graph, "case": case["name"],
                    "site_i": i, "site_j": j, "bond_present": bond_present,
                    "ground_mean_ninj": mean_in_ground_subspace(
                        np.diag(number_product), vectors, ground_mask
                    ),
                    "ground_mean_Ji_dot_Jj": spin_mean,
                    "ground_bond_kinetic_energy": (-case["t"] * kinetic_mean
                                                     if bond_present else None),
                })
        closure_correlation_residual = max(
            closure_correlation_residual, abs(local_mean + pair_sum)
        )
    if closure_correlation_residual > 5e-8:
        raise AssertionError("ground-state pair correlations violate total-spin closure")
    state_summary["ground_spin_closure_correlation_residual"] = closure_correlation_residual
    reduced_state_row = {
        "K": k, "graph": graph, "case": case["name"],
        "ground_degeneracy": int(ground_mask.sum()),
        "site": 0, "partition": "site 0 | sites 1-3",
        "reduced_entropy_nats": ground_entropy, "reduced_purity": ground_purity,
    }
    edge_triple_rows = []
    for edge in edges:
        for triple in selected_triples:
            edge_h = -case["t"] * model["bonds"][edge]
            comm = edge_h @ model["volume_by_triple"][triple] - model["volume_by_triple"][triple] @ edge_h
            edge_triple_rows.append({
                "K": k, "graph": graph, "case": case["name"],
                "edge": f"{edge[0]}-{edge[1]}",
                "triple": "".join(map(str, triple)),
                "frobenius_norm": float(np.linalg.norm(comm, ord="fro")),
                "maximum_entry": float(np.max(abs(comm))),
            })
    if case["name"] == "no_hopping":
        state_summary["no_hopping_ground_eigenvalue_spread"] = float(
            np.ptp(energies[ground_mask]) if np.any(ground_mask) else 0.0
        )
    energy_levels = [{
        "K": k, "graph": graph, "case": case["name"], "state_index": i + 1,
        "energy": float(energy), "ground_state_member": bool(ground_mask[i]),
    } for i, energy in enumerate(energies)]
    return (state_summary, thermo, n_probs, v_distribution, edge_triple_rows,
            energy_levels, correlation_rows, reduced_state_row, hamiltonian, volume)


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_results(out, summaries, thermodynamics, k4_scan, k4_energy_levels):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), constrained_layout=True)
    colors = {"complete": "#345995", "ring": "#e07a5f"}
    markers = {"complete": "o", "ring": "s"}
    line_styles = {"complete": "--", "ring": "-"}
    for ax, k in zip(axes, (2, 3, 4)):
        rows = [row for row in summaries if row["K"] == k and row["U_over_t"] is not None]
        for graph in ("ring", "complete"):
            series = sorted((row for row in rows if row["graph"] == graph),
                            key=lambda row: row["U_over_t"])
            x = [row["U_over_t"] for row in series]
            ax.plot(x, [row["ground_energy"] for row in series], marker=markers[graph],
                    color=colors[graph], label=graph, linestyle=line_styles[graph],
                    markerfacecolor="none" if graph == "complete" else colors[graph],
                    markersize=7 if graph == "complete" else 4.5,
                    markeredgewidth=1.4 if graph == "complete" else 0.8,
                    zorder=3 if graph == "complete" else 2)
        ax.set_xscale("symlog", linthresh=0.5)
        ax.set_title(f"K={k}", fontsize=9)
        ax.set_xlabel("U/t", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Ground energy (t=1)", fontsize=8)
    axes[-1].legend(frameon=False, fontsize=7)
    fig.suptitle("Four-site closed-sector ground energy", fontsize=10)
    fig.savefig(out / "ground_energy_vs_repulsion.png", dpi=300)
    fig.savefig(out / "ground_energy_vs_repulsion.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), constrained_layout=True)
    for ax, k in zip(axes, (2, 3, 4)):
        complete = {row["U_over_t"]: row["ground_energy"] for row in summaries
                    if row["K"] == k and row["graph"] == "complete"
                    and row["U_over_t"] is not None}
        ring = {row["U_over_t"]: row["ground_energy"] for row in summaries
                if row["K"] == k and row["graph"] == "ring"
                and row["U_over_t"] is not None}
        ratios = sorted(complete, key=float)
        differences = [complete[ratio] - ring[ratio] for ratio in ratios]
        ax.plot(ratios, differences, color="#6c5b7b", marker="D", markersize=4.5,
                linewidth=1.2)
        ax.axhline(0.0, color="0.4", linestyle=":", linewidth=0.9)
        ax.set_xscale("symlog", linthresh=0.5)
        ax.set_xlim(left=0.0)
        ax.set_title(f"K={k}", fontsize=9)
        ax.set_xlabel("U/t", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.25)
        if k == 2:
            ax.set_ylim(-5e-4, 5e-4)
            ax.text(0.05, 0.08, "coincident to numerical precision",
                    transform=ax.transAxes, fontsize=7)
    axes[0].set_ylabel(r"$E_0$(complete) $-$ $E_0$(ring)", fontsize=8)
    fig.suptitle("Graph dependence of the ground-state energy", fontsize=10)
    fig.savefig(out / "ground_energy_graph_difference.png", dpi=300)
    fig.savefig(out / "ground_energy_graph_difference.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), constrained_layout=True)
    for ax, k in zip(axes, (2, 3, 4)):
        for graph in ("ring", "complete"):
            rows = [row for row in thermodynamics
                    if row["K"] == k and row["case"] == "U5" and row["beta"] != "inf"]
            rows = sorted((row for row in rows if row["graph"] == graph),
                          key=lambda row: row["beta"])
            ax.plot([row["beta"] for row in rows], [row["mean_volume"] for row in rows],
                    marker=markers[graph], color=colors[graph], label=graph,
                    linestyle=line_styles[graph],
                    markerfacecolor="none" if graph == "complete" else colors[graph],
                    markersize=7 if graph == "complete" else 4.5,
                    markeredgewidth=1.4 if graph == "complete" else 0.8,
                    zorder=3 if graph == "complete" else 2)
        ax.set_xscale("symlog", linthresh=0.1)
        ax.set_title(f"K={k}", fontsize=9)
        ax.set_xlabel(r"Inverse temperature $\beta/t$", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel(r"Thermal mean $\langle V\rangle$", fontsize=8)
    axes[-1].legend(frameon=False, fontsize=7)
    fig.suptitle("Volume in the fixed-K Gibbs state (U/t=5)", fontsize=10)
    fig.savefig(out / "thermal_volume_u5.png", dpi=300)
    fig.savefig(out / "thermal_volume_u5.pdf")
    plt.close(fig)

    if not k4_scan:
        return

    case_specs = (("no_hopping", "t=0, U=1"), ("free", "U/t=0"),
                  ("U1", "U/t=1"), ("U5", "U/t=5"), ("U20", "U/t=20"))
    fig, axes = plt.subplots(2, 5, figsize=(16.5, 6.6), sharex=True)
    for column, (case_name, title) in enumerate(case_specs):
        for graph in ("ring", "complete"):
            rows = [row for row in k4_scan
                    if row["case"] == case_name and row["graph"] == graph
                    and row["beta"] != "inf"]
            rows.sort(key=lambda row: row["beta"])
            beta = [row["beta"] for row in rows]
            axes[0, column].plot(
                beta, [row["mean_volume"] for row in rows],
                color=colors[graph], linestyle=line_styles[graph],
                marker=markers[graph], markerfacecolor=(
                    "none" if graph == "complete" else colors[graph]
                ), markersize=5, markevery=60,
                label=graph,
            )
            zero_temperature = next(
                row for row in k4_scan
                if row["case"] == case_name and row["graph"] == graph
                and row["beta"] == "inf"
            )
            axes[0, column].axhline(
                zero_temperature["mean_volume"], color=colors[graph],
                linestyle=":", linewidth=1.0, alpha=0.8,
            )
            axes[1, column].plot(
                beta, [row["probability_zero_volume"] for row in rows],
                color=colors[graph], linestyle=line_styles[graph],
                marker=markers[graph], markerfacecolor=(
                    "none" if graph == "complete" else colors[graph]
                ), markersize=5, markevery=60,
            )
            axes[1, column].axhline(
                zero_temperature["probability_zero_volume"], color=colors[graph],
                linestyle=":", linewidth=1.0, alpha=0.8,
            )
        axes[0, column].set_title(title, fontsize=9)
        axes[0, column].set_xscale("symlog", linthresh=0.01)
        axes[1, column].set_xscale("symlog", linthresh=0.01)
        axes[1, column].set_xlabel(r"Inverse temperature $\beta/t$", fontsize=8)
        for row in range(2):
            axes[row, column].grid(alpha=0.25)
            axes[row, column].tick_params(labelsize=7)
    axes[0, 0].set_ylabel(r"Thermal mean $\langle V\rangle$", fontsize=8)
    axes[1, 0].set_ylabel(r"Probability $P(V=0)$", fontsize=8)
    axes[0, 0].legend(frameon=False, fontsize=7)
    fig.suptitle("K=4 thermal scan; dotted lines show the beta-to-infinity limit",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out / "k4_thermal_volume_scan.png", dpi=300)
    fig.savefig(out / "k4_thermal_volume_scan.pdf")
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for ax, case_name, title in zip(axes, ("U5", "U20"), ("U/t=5", "U/t=20")):
        for graph in ("ring", "complete"):
            rows = [row for row in k4_energy_levels
                    if row["case"] == case_name and row["graph"] == graph
                    and row["energy_above_ground"] <= 1.5]
            rows.sort(key=lambda row: row["energy_above_ground"])
            ax.scatter(
                [row["energy_above_ground"] for row in rows],
                [row["subspace_mean_volume"] for row in rows],
                color=colors[graph], marker=markers[graph], s=30,
                label=graph,
            )
        ax.set_title(title, fontsize=9)
        ax.set_xlabel(r"Energy above ground $(E-E_0)/t$", fontsize=8)
        ax.grid(alpha=0.25)
        ax.tick_params(labelsize=7)
    axes[0].set_ylabel(r"Mean volume in energy eigenspace", fontsize=8)
    axes[1].legend(frameon=False, fontsize=7)
    fig.suptitle("K=4 low-energy volume spectrum (degenerate levels grouped)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(out / "k4_low_energy_volume_spectrum.png", dpi=300)
    fig.savefig(out / "k4_low_energy_volume_spectrum.pdf")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k-min", type=int, default=2)
    parser.add_argument("--k-max", type=int, default=4)
    parser.add_argument("--output-dir", type=Path,
                        default=PROJECT_ROOT / "results" / "hamiltonian-studies")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    if args.k_min < 2 or args.k_max < args.k_min:
        parser.error("require 2 <= k-min <= k-max")
    started = time.perf_counter()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries, thermo_rows, n_rows, volume_rows, commutator_rows = [], [], [], [], []
    energy_rows, correlation_rows, entanglement_rows = [], [], []
    k4_scan_rows, k4_energy_level_rows = [], []
    operator_records, kinematic_rows = [], []

    for k in range(args.k_min, args.k_max + 1):
        model = build_fixed_k(k)
        kinematic_rows.extend(infinite_temperature_counts(k))
        graph_models = {}
        for graph, edges in GRAPH_EDGES.items():
            selected = connected_triples(edges)
            graph_models[graph] = (selected, sum(
                (model["volume_by_triple"][triple] for triple in selected),
                np.zeros_like(model["onsite"]),
            ))
            operator_records.append({
                **model["metadata"], "graph": graph,
                "edges": [list(edge) for edge in edges],
                "connected_triples": [list(triple) for triple in selected],
            })
            archive = args.output_dir / f"operators_k{k}_{graph}.npz"
            arrays = {
                "occupations_m0": np.asarray(model["occupations_m0"], dtype=np.int16),
                "singlet_basis": model["basis"],
                "onsite_penalty": model["onsite"],
                "active_sites": model["active_sites"],
                "site_boson_numbers": model["site_spins"],
                "volume": graph_models[graph][1],
            }
            arrays.update({f"hopping_{i}_{j}": model["bonds"][(i, j)]
                           for i, j in GRAPH_EDGES["complete"]})
            arrays.update({f"spin_dot_{i}_{j}": model["spin_dots"][(i, j)]
                           for i, j in itertools.combinations(range(SITES), 2)})
            arrays.update({f"volume_triple_{a}{b}{c}": model["volume_by_triple"][(a, b, c)]
                           for a, b, c in TRIPLES})
            np.savez_compressed(archive, **arrays)

        for graph, (selected_triples, _) in graph_models.items():
            for case in CASES:
                result = calculate_case(k, graph, case, model, selected_triples)
                summary, thermo, n_probs, v_dist, edge_terms, levels, correlations, entanglement, hamiltonian, volume = result
                summaries.append(summary)
                thermo_rows.extend(thermo)
                n_rows.extend(n_probs)
                volume_rows.extend(v_dist)
                commutator_rows.extend(edge_terms)
                energy_rows.extend(levels)
                correlation_rows.extend(correlations)
                entanglement_rows.append(entanglement)
                if k == 4:
                    k4_scan_rows.extend(k4_thermal_scan(
                        k, graph, case, hamiltonian, volume, model["active_sites"]
                    ))
                    k4_energy_level_rows.extend(energy_resolved_volume(
                        k, graph, case, hamiltonian, volume, model["active_sites"]
                    ))
                if case["name"] == "U5":
                    archive = args.output_dir / f"operators_k{k}_{graph}.npz"
                    with np.load(archive, allow_pickle=False) as saved:
                        existing = {name: saved[name] for name in saved.files}
                    existing["hamiltonian_u5"] = hamiltonian
                    existing["volume"] = volume
                    np.savez_compressed(archive, **existing)
            print(f"K={k} {graph}: dim={model['metadata']['closed_singlet_dimension']} "
                  f"connected triples={len(selected_triples)}", flush=True)

    write_csv(args.output_dir / "spectra.csv", summaries)
    write_csv(args.output_dir / "energy_levels.csv", energy_rows)
    write_csv(args.output_dir / "thermodynamics.csv", thermo_rows)
    write_csv(args.output_dir / "active_site_probabilities.csv", n_rows)
    write_csv(args.output_dir / "volume_distributions.csv", volume_rows)
    write_csv(args.output_dir / "commutator_edge_triple_terms.csv", commutator_rows)
    write_csv(args.output_dir / "ground_state_correlations.csv", correlation_rows)
    write_csv(args.output_dir / "ground_state_reduced_state.csv", entanglement_rows)
    write_csv(args.output_dir / "kinematic_active_site_counts.csv", kinematic_rows)
    if k4_scan_rows:
        write_csv(args.output_dir / "k4_thermal_volume_scan.csv", k4_scan_rows)
        write_csv(args.output_dir / "k4_energy_resolved_volume.csv", k4_energy_level_rows)
    metadata = {
        "schema_version": 1,
        "model": "Two-component Bose-Hubbard model restricted to the exact four-site SU(2) singlet sector",
        "notation": "K=sum_i j_i; total boson number=2K; local twice-spin equals local boson number",
        "graphs": {name: {"edges": [list(edge) for edge in edges],
                          "connected_triples": [list(triple) for triple in connected_triples(edges)]}
                   for name, edges in GRAPH_EDGES.items()},
        "volume": "V=(gamma*hbar)^(3/2) sum over connected triples sqrt(abs(q_ijk)); gamma=0.2375, hbar=1",
        "triple_rule": "An induced three-site subgraph is connected when it contains at least two edges; triangles are not required.",
        "hamiltonian": "H=-t sum_edges(E_ij+E_ji)+(U/2) sum_i n_i(n_i-1); g=0",
        "cases": list(CASES),
        "beta_values": [*BETA_VALUES, "inf"],
        "k4_detailed_beta_scan": {
            "finite_beta_values": [0.0, "logspace(1e-3,1e3,601)"],
            "includes_zero_temperature_limit": True,
            "records": len(k4_scan_rows),
        },
        "basis": "((j0,j1)k,(j2,j3)k) coupled to total spin zero; Condon-Shortley phases",
        "dimensions": operator_records,
        "infinite_temperature_active_site_counts": kinematic_rows,
        "onsite_commutator_identity": "[H_U,V]=0 because each n_i commutes with all local fluxes",
        "normalization_limit": "Project volume units only; physical regularization remains unresolved.",
        "numerics": {"python": platform.python_version(), "numpy": np.__version__,
                     "scipy": scipy.__version__, "sympy": sympy.__version__,
                     "absolute_tolerance": ABS_TOL,
                     "zero_eigenvalue_cutoff": "64*eps*max(1,max(abs(eigenvalues)))"},
        "elapsed_seconds": time.perf_counter() - started,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    for k in range(args.k_min, args.k_max + 1):
        complete = sorted(row["energy"] for row in energy_rows
                          if row["K"] == k and row["graph"] == "complete"
                          and row["case"] == "no_hopping")
        ring = sorted(row["energy"] for row in energy_rows
                      if row["K"] == k and row["graph"] == "ring"
                      and row["case"] == "no_hopping")
        if len(complete) != len(ring) or np.max(abs(np.asarray(complete) - ring)) > 5e-9:
            raise AssertionError("no-hopping spectra must be graph independent")
        expected_probabilities = {row["active_sites"]: row["probability"]
                                  for row in kinematic_rows if row["K"] == k}
        for row in n_rows:
            if row["K"] == k and row["beta"] == 0.0:
                if abs(row["probability"] - expected_probabilities[row["active_sites"]]) > 5e-9:
                    raise AssertionError("beta=0 active-site distribution disagrees with exact counting")
    for row in k4_scan_rows:
        if row["beta"] == 0.0:
            reference = next(record for record in thermo_rows
                             if record["K"] == 4 and record["graph"] == row["graph"]
                             and record["case"] == row["case"] and record["beta"] == 0.0)
            if max(abs(row["mean_volume"] - reference["mean_volume"]),
                   abs(row["probability_zero_volume"] - reference["probability_zero_volume"])) > 5e-8:
                raise AssertionError("detailed beta=0 volume scan disagrees with the main thermal data")
        if row["beta"] == "inf":
            reference = next(record for record in summaries
                             if record["K"] == 4 and record["graph"] == row["graph"]
                             and record["case"] == row["case"])
            if max(abs(row["mean_volume"] - reference["ground_mean_volume"]),
                   abs(row["probability_zero_volume"]
                       - reference["ground_probability_zero_volume"])) > 5e-8:
                raise AssertionError("detailed zero-temperature scan disagrees with ground-state data")
    if any(row["case"] == "no_hopping" and row["ground_commutator_norm_frobenius"] > 5e-9
           for row in summaries):
        raise AssertionError("the volume commutator must vanish when hopping is absent")
    plot_status = {"status": "skipped", "reason": "requested with --no-plots"}
    if not args.no_plots:
        try:
            plot_results(args.output_dir, summaries, thermo_rows,
                         k4_scan_rows, k4_energy_level_rows)
            plot_status = {"status": "generated"}
        except ModuleNotFoundError as error:
            if error.name != "matplotlib":
                raise
            plot_status = {"status": "skipped", "reason": "matplotlib is not installed"}
    metadata["plots"] = plot_status
    (args.output_dir / "summary.json").write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"K_values": list(range(args.k_min, args.k_max + 1)),
                      "systems": len(summaries),
                      "elapsed_seconds": metadata["elapsed_seconds"],
                      "plots": plot_status,
                      "output": str(args.output_dir)}, indent=2))


if __name__ == "__main__":
    main()

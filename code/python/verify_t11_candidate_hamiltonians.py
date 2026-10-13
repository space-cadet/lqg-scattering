"""Independent spectral, Gibbs-trace, orientation, and evolution checks."""

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.linalg import eigh, expm

from lqg_scattering.singlets import GAMMA, ZERO_FACTOR
from t11_candidate_hamiltonians import (
    ALPHAS,
    INPUT_DIR,
    OUT,
    PAIRS,
    T,
    U_VALUES,
    build_geometry,
    build_model,
    make_reference,
)


ROOT = Path(__file__).resolve().parents[2]
TOL = 2e-10
SELECTED_BETAS = (0.0, 1.0, 10.0, 1000.0, math.inf)


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def close(value, expected):
    return abs(float(value) - float(expected))


def main():
    complete = np.load(INPUT_DIR / "operators_k4_complete.npz")
    ring = np.load(INPUT_DIR / "operators_k4_ring.npz")
    archives = {"complete": complete, "ring": ring}
    geometry = build_geometry(complete)
    model_kwargs = {
        "volume": geometry["volume"],
        "volume_range": geometry["volume_range"],
        "q_chi": geometry["q_chi"],
        "q_range": geometry["q_range"],
    }

    summaries = read_csv(OUT / "model_summary.csv")
    energy_rows = read_csv(OUT / "energy_levels.csv")
    thermal_rows = read_csv(OUT / "thermal_scan.csv")
    outcome_rows = read_csv(OUT / "thermal_volume_outcomes.csv")
    assignment_rows = read_csv(OUT / "thermal_area_assignments_selected.csv")
    state_distribution_rows = read_csv(OUT / "state_volume_distributions.csv")
    dynamics_rows = read_csv(OUT / "dynamics_scan.csv")

    energy_by_model = defaultdict(list)
    for row in energy_rows:
        energy_by_model[row["model_id"]].append(float(row["energy"]))
    thermal_by_key = {
        (row["model_id"], row["beta_t"]): row for row in thermal_rows
    }
    checks = {}
    reconstructed = {}
    q_values, q_vectors = eigh(geometry["q_chi"])
    q_cutoff = ZERO_FACTOR * max(1.0, float(np.max(np.abs(q_values))))
    q_values = np.where(np.abs(q_values) <= q_cutoff, 0.0, q_values)
    volume_from_chirality = (
        q_vectors * (2.0 * GAMMA**1.5 * np.sqrt(np.abs(q_values)))
    ) @ q_vectors.conj().T
    checks["V_RS_function_of_oriented_Qchi"] = float(np.max(np.abs(
        volume_from_chirality - geometry["volume"]
    )))
    checks["V_RS_commutes_with_Qchi"] = float(np.max(np.abs(
        geometry["volume"] @ geometry["q_chi"]
        - geometry["q_chi"] @ geometry["volume"]
    )))

    for summary in summaries:
        model = build_model(
            summary["graph"], summary["candidate"],
            float(summary["U_over_t"]), float(summary["alpha"]),
            model_kwargs, archives,
        )
        numpy_values = np.linalg.eigvalsh(model["hamiltonian"])
        saved_values = np.asarray(energy_by_model[summary["model_id"]])
        checks[f"{summary['model_id']}_numpy_spectrum"] = float(
            np.max(np.abs(numpy_values - saved_values))
        )
        checks[f"{summary['model_id']}_ground_summary"] = close(
            summary["ground_energy"], numpy_values[0]
        )
        if len(numpy_values) != 105:
            raise AssertionError(f"wrong dimension for {summary['model_id']}")
        reconstructed[summary["model_id"]] = model["hamiltonian"]

    for u_over_t in U_VALUES:
        for abs_alpha in (0.5, 1.0, 2.0):
            negative = build_model(
                "complete", "signed_grasp", u_over_t, -abs_alpha,
                model_kwargs, archives,
            )
            positive = build_model(
                "complete", "signed_grasp", u_over_t, abs_alpha,
                model_kwargs, archives,
            )
            checks[
                f"signed_orientation_H_conjugation_U{u_over_t:g}_a{abs_alpha:g}"
            ] = float(np.max(np.abs(
                positive["hamiltonian"].conj() - negative["hamiltonian"]
            )))
            checks[
                f"signed_orientation_spectrum_U{u_over_t:g}_a{abs_alpha:g}"
            ] = float(np.max(np.abs(
                np.linalg.eigvalsh(positive["hamiltonian"])
                - np.linalg.eigvalsh(negative["hamiltonian"])
            )))

    if len(summaries) != 62 or len(energy_rows) != 62 * 105:
        raise AssertionError("static model or spectrum row count is incomplete")

    for summary in summaries:
        key = (summary["model_id"], "0")
        model = build_model(
            summary["graph"], summary["candidate"],
            float(summary["U_over_t"]), 0.0, model_kwargs, archives,
        )
        if float(summary["alpha"]) == 0.0:
            saved = np.asarray(energy_by_model[summary["model_id"]])
            baseline = np.linalg.eigvalsh(model["h0"])
            checks[f"{summary['model_id']}_alpha0_H0"] = float(
                np.max(np.abs(saved - baseline))
            )

    cases = (
        ("complete_positive_volume_U20_alpham1", -1.0),
        ("complete_positive_volume_U20_alphap2", 2.0),
        ("complete_signed_grasp_U1_alpham1", -1.0),
        ("complete_signed_grasp_U20_alphap1", 1.0),
        ("ring_positive_volume_U5_alphap1", 1.0),
    )
    for model_id, _ in cases:
        if model_id not in reconstructed:
            raise AssertionError(f"missing independent-check case {model_id}")
        hamiltonian = reconstructed[model_id]
        energy, vectors = eigh(hamiltonian)
        for beta in SELECTED_BETAS:
            if math.isinf(beta):
                mask = np.abs(energy - energy[0]) <= 1e-12
                rho = vectors[:, mask] @ vectors[:, mask].conj().T / int(mask.sum())
            elif beta == 0.0:
                rho = np.eye(len(energy), dtype=complex) / len(energy)
            else:
                shifted = hamiltonian - energy[0] * np.eye(len(energy))
                boltzmann = expm(-beta * shifted)
                rho = boltzmann / np.trace(boltzmann)
            thermal = thermal_by_key[(model_id, format(beta, ".17g")
                                      if math.isfinite(beta) else "inf")]
            direct_energy = float(np.real(np.trace(rho @ hamiltonian)))
            direct_v = float(np.real(np.trace(rho @ geometry["volume"])))
            direct_pzero = float(np.real(np.trace(rho @ geometry["p_zero"])))
            direct_q = float(np.real(np.trace(rho @ geometry["q012"])))
            direct_qchi = float(np.real(np.trace(rho @ geometry["q_chi"])))
            prefix = f"{model_id}_beta_{beta:g}"
            checks[prefix + "_energy"] = close(
                thermal["mean_energy"], direct_energy
            )
            checks[prefix + "_volume"] = close(
                thermal["mean_volume_project_units"], direct_v
            )
            checks[prefix + "_Pzero"] = close(
                thermal["probability_zero_volume"], direct_pzero
            )
            checks[prefix + "_q012"] = close(
                thermal["mean_signed_q012"], direct_q
            )
            checks[prefix + "_Qchi"] = close(
                thermal["mean_Q_chi"], direct_qchi
            )

    outcome_sums = defaultdict(float)
    for row in outcome_rows:
        outcome_sums[row["model_id"], row["beta_t"]] += float(row["probability"])
    for key, total in outcome_sums.items():
        checks[f"thermal_volume_distribution_{key[0]}_{key[1]}"] = abs(total - 1)
    if len(outcome_sums) != 62 * 6:
        raise AssertionError("selected thermal volume distributions are incomplete")

    assignment_sums = defaultdict(float)
    for row in assignment_rows:
        assignment_sums[row["model_id"], row["beta_t"]] += float(row["probability"])
    for key, total in assignment_sums.items():
        checks[f"thermal_area_assignment_{key[0]}_{key[1]}"] = abs(total - 1)
    if len(assignment_sums) != 62 * 5:
        raise AssertionError("selected thermal area assignments are incomplete")

    state_distribution_sums = defaultdict(float)
    for row in state_distribution_rows:
        state_distribution_sums[
            row["model_id"], row["state_kind"], row["state_label"]
        ] += float(row["probability"])
    for key, total in state_distribution_sums.items():
        checks[f"state_volume_distribution_{key}"] = abs(total - 1)

    # Verify that alpha=0 recovers the previously saved U/t=20 complete case.
    old_summary = read_csv(ROOT / "results/t11-volume-coupling/summary.csv")
    old = next(row for row in old_summary if float(row["alpha_V"]) == 0.0)
    baseline_summary = next(
        row for row in summaries
        if row["graph"] == "complete"
        and row["candidate"] == "positive_volume"
        and float(row["U_over_t"]) == 20
        and float(row["alpha"]) == 0
    )
    checks["prior_positive_volume_ground_energy"] = close(
        baseline_summary["ground_energy"], old["ground_energy"]
    )
    checks["prior_positive_volume_ground_volume"] = close(
        baseline_summary["ground_volume_mean_project_units"],
        old["ground_mean_volume_project_units"],
    )
    checks["prior_positive_volume_ground_Pzero"] = close(
        baseline_summary["ground_probability_zero_volume"],
        old["ground_probability_zero_volume"],
    )

    previous_thermal = read_csv(
        ROOT / "results/hamiltonian-studies/k4_thermal_volume_scan.csv"
    )
    baseline_id = "complete_positive_volume_U20_alphap0"
    for beta in (0.0, 1.0, 10.0, 1000.0, math.inf):
        beta_text = format(beta, ".17g") if math.isfinite(beta) else "inf"
        old_row = next(
            row for row in previous_thermal
            if row["K"] == "4" and row["graph"] == "complete"
            and row["U_over_t"] and float(row["U_over_t"]) == 20.0
            and (
                row["beta"] == "inf" if math.isinf(beta)
                else math.isclose(float(row["beta"]), beta,
                                  rel_tol=0.0, abs_tol=1e-12)
            )
        )
        new_row = thermal_by_key[baseline_id, beta_text]
        checks[f"saved_T11_baseline_beta_{beta:g}_volume"] = close(
            new_row["mean_volume_project_units"], old_row["mean_volume"]
        )
        checks[f"saved_T11_baseline_beta_{beta:g}_Pzero"] = close(
            new_row["probability_zero_volume"],
            old_row["probability_zero_volume"],
        )

    # Exact expm checks for every prepared FL seed, plus a signed-grasp case.
    references = {}
    for phi in (90, 60, 30, 10, 0):
        references[phi] = make_reference(phi, complete)[0]
    dynamic_cases = tuple(
        ("complete_positive_volume_U5_alpham1", phi)
        for phi in (90, 60, 30, 10, 0)
    ) + (("complete_signed_grasp_U20_alphap1", 0),)
    for model_id, phi in dynamic_cases:
        hamiltonian = reconstructed[model_id]
        seed = references[phi]
        seed_label = (
            "regular" if phi == 90 else
            "flat_boundary" if phi == 0 else
            f"phi_{phi}"
        )
        trajectory = [
            row for row in dynamics_rows
            if row["model_id"] == model_id
            and row["seed"] == seed_label
        ]
        if not trajectory:
            raise AssertionError(f"missing trajectory {model_id}")
        for suffix, row in (
            ("early", trajectory[min(37, len(trajectory) - 1)]),
        ):
            tau = float(row["tau_t_over_hbar"])
            state = expm(-1j * tau * hamiltonian) @ seed
            rho = np.outer(state, state.conj())
            check_id = f"{model_id}_{seed_label}_{suffix}"
            checks[f"{check_id}_norm"] = abs(
                float(np.vdot(state, state).real) - 1.0
            )
            checks[f"{check_id}_energy"] = close(
                np.real(np.vdot(state, hamiltonian @ state)),
                row["energy_expectation"],
            )
            checks[f"{check_id}_volume"] = close(
                np.real(np.vdot(state, geometry["volume"] @ state)),
                row["mean_volume_project_units"],
            )
            checks[f"{check_id}_return"] = close(
                abs(np.vdot(seed, state)) ** 2, row["return_probability"]
            )
            checks[f"{check_id}_Pzero"] = close(
                np.real(np.trace(rho @ geometry["p_zero"])),
                row["probability_zero_volume"],
            )

    for metric in ("norm_residual", "energy_residual", "total_area_residual"):
        checks[f"all_dynamics_{metric}"] = max(
            float(row[metric]) for row in dynamics_rows
        )
    schedules = read_csv(OUT / "dynamics_schedule.csv")
    checks["dynamics_horizon_matches_saved_schedule"] = max(
        abs(
            max(float(row["tau_t_over_hbar"]) for row in dynamics_rows
                if row["model_id"] == schedule["model_id"]
                and row["seed"] == schedule["seed"])
            - float(schedule["time_horizon_t_over_hbar"])
        )
        for schedule in schedules
    )

    max_residual = max(checks.values(), default=0.0)
    report = {
        "method": (
            "independent NumPy spectra, SciPy matrix-exponential Gibbs and "
            "time-evolution checks, saved-baseline parity, and probability sums"
        ),
        "check_count": len(checks),
        "checks": checks,
        "max_residual": max_residual,
        "tolerance": TOL,
        "passed": max_residual < TOL,
    }
    (OUT / "verification.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    if max_residual >= TOL:
        raise AssertionError(
            f"independent residual {max_residual:.4g} >= {TOL:.4g}"
        )
    print(
        f"Independent verification passed: {len(checks)} checks; "
        f"max residual={max_residual:.3g}"
    )


if __name__ == "__main__":
    main()

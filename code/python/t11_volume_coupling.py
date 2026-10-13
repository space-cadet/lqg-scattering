"""Test a positive-RS-volume coupling in the tetrahedral K=4 singlet sector."""

import csv
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import eigh, expm

from lqg_scattering.intertwiners import fixed_area_state
from lqg_scattering.singlets import ABS_TOL, GAMMA, ZERO_FACTOR
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.thermal import grouped_values, thermal_weights
from lqg_scattering.tetrahedra import closed_equal_area_normals


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "results/hamiltonian-studies/operators_k4_complete.npz"
OUT = ROOT / "results/t11-volume-coupling"
T = 1.0
U_OVER_T = 20.0
ALPHAS = (-1.0, 0.0, 1.0)
BETAS = (0.0, *np.geomspace(1e-3, 1e3, 601), math.inf)
SELECTED_BETAS = (0.0, 1.0, 10.0, 100.0, 1000.0, math.inf)
REFERENCE_PHI = (90, 0)
TOL = 2e-10


def save_csv(path, rows):
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def make_reference(phi_degrees, archive):
    normals = closed_equal_area_normals(
        1.0 / math.sqrt(3.0), math.radians(phi_degrees)
    )
    _, amplitudes = fixed_area_state(4, spinors=spinors_from_normals(normals))
    magnetic = np.asarray([
        amplitudes.get(tuple(occupation), 0j)
        for occupation in archive["occupations_m0"]
    ])
    basis = archive["singlet_basis"]
    ket = basis.conj().T @ magnetic
    reconstruction = basis @ ket
    residual = float(np.max(np.abs(reconstruction - magnetic)))
    norm_residual = float(abs(np.vdot(ket, ket) - 1.0))
    if max(residual, norm_residual) > TOL:
        raise AssertionError(
            f"FL reference projection failed: {residual=}, {norm_residual=}"
        )
    return ket, normals, residual, norm_residual


def expectation(ket, operator):
    return float(np.real(np.vdot(ket, operator @ ket)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    archive = np.load(INPUT)
    volume = np.asarray(archive["volume"], dtype=complex)
    onsite = np.asarray(archive["onsite_penalty"], dtype=complex)
    edges = tuple((i, j) for i in range(4) for j in range(i + 1, 4))
    hopping_sum = sum(
        (archive[f"hopping_{i}_{j}"] for i, j in edges),
        np.zeros_like(onsite),
    )
    h0 = U_OVER_T * T * onsite - T * hopping_sum
    h0 = (h0 + h0.conj().T) / 2.0
    volume = (volume + volume.conj().T) / 2.0

    volume_eigenvalues, volume_vectors = eigh(volume)
    volume_range = float(volume_eigenvalues[-1] - volume_eigenvalues[0])
    if volume_range <= ABS_TOL:
        raise AssertionError("volume operator has no spectral range")
    volume_cutoff = ZERO_FACTOR * max(1.0, float(np.max(np.abs(volume_eigenvalues))))
    zero_indices = np.flatnonzero(np.abs(volume_eigenvalues) <= volume_cutoff)
    p_zero = volume_vectors[:, zero_indices] @ volume_vectors[:, zero_indices].conj().T
    volume_groups = grouped_values(volume_eigenvalues)
    volume_projectors = []
    for group in volume_groups:
        selected = volume_vectors[:, group["indices"]]
        volume_projectors.append(selected @ selected.conj().T)

    site_numbers = np.asarray(archive["site_boson_numbers"])
    active_count = np.count_nonzero(site_numbers, axis=1).astype(float)
    active_four = (active_count == 4.0).astype(float)
    refs = {}
    reference_validation = {}
    for phi in REFERENCE_PHI:
        ket, normals, projection_residual, norm_residual = make_reference(phi, archive)
        refs[phi] = ket
        reference_validation[f"phi_{phi}_projection_residual"] = projection_residual
        reference_validation[f"phi_{phi}_norm_residual"] = norm_residual

    thermal_rows = []
    selected_volume_rows = []
    reference_rows = []
    energy_rows = []
    summary_rows = []
    validation = {
        "H0_hermiticity_max_abs": float(np.max(np.abs(h0 - h0.conj().T))),
        "V_hermiticity_max_abs": float(np.max(np.abs(volume - volume.conj().T))),
        "V_min_eigenvalue": float(volume_eigenvalues[0]),
        "V_max_eigenvalue": float(volume_eigenvalues[-1]),
        "V_zero_kernel_dimension": int(len(zero_indices)),
        **reference_validation,
    }

    for alpha in ALPHAS:
        g_v = alpha * T / volume_range
        hamiltonian = h0 + g_v * volume
        hamiltonian = (hamiltonian + hamiltonian.conj().T) / 2.0
        energies, energy_vectors = eigh(hamiltonian)
        numpy_energies = np.linalg.eigvalsh(hamiltonian)
        solver_residual = float(np.max(np.abs(energies - numpy_energies)))
        eigen_residual = float(
            np.max(np.abs(hamiltonian @ energy_vectors - energy_vectors * energies))
        )
        groups = grouped_values(energies)
        ground_indices = groups[0]["indices"]
        ground_vectors = energy_vectors[:, ground_indices]
        ground_mask = np.zeros(len(energies), dtype=bool)
        ground_mask[ground_indices] = True
        ground_weights, _ = thermal_weights(energies, math.inf)

        v_by_energy = np.real(np.diag(energy_vectors.conj().T @ volume @ energy_vectors))
        v2_by_energy = np.real(
            np.diag(energy_vectors.conj().T @ volume @ volume @ energy_vectors)
        )
        pzero_by_energy = np.real(
            np.diag(energy_vectors.conj().T @ p_zero @ energy_vectors)
        )
        active_by_energy = (np.abs(energy_vectors) ** 2).T @ active_count
        p_four_by_energy = (np.abs(energy_vectors) ** 2).T @ active_four

        ground_mean_v = float(ground_weights @ v_by_energy)
        ground_second_v = float(ground_weights @ v2_by_energy)
        ground_sd_v = math.sqrt(max(0.0, ground_second_v - ground_mean_v**2))
        ground_pzero = float(ground_weights @ pzero_by_energy)
        ground_mean_active = float(ground_weights @ active_by_energy)
        gap = float(groups[1]["value"] - groups[0]["value"]) if len(groups) > 1 else None

        for phi, ket in refs.items():
            label = "regular" if phi == 90 else "flat_boundary"
            v_mean = expectation(ket, volume)
            v_second = expectation(ket, volume @ volume)
            zero_prob = expectation(ket, p_zero)
            energy_mean = expectation(ket, hamiltonian)
            ground_overlap = float(np.sum(np.abs(ground_vectors.conj().T @ ket) ** 2))
            reference_rows.append({
                "alpha_V": alpha,
                "g_V_energy_per_project_volume": g_v,
                "reference": label,
                "phi_degrees": phi,
                "energy_expectation": energy_mean,
                "volume_mean_project_units": v_mean,
                "volume_sd_project_units": math.sqrt(max(0.0, v_second - v_mean**2)),
                "probability_zero_volume": zero_prob,
                "ground_subspace_overlap_probability": ground_overlap,
            })

        summary = {
            "alpha_V": alpha,
            "g_V_energy_per_project_volume": g_v,
            "t": T,
            "U_over_t": U_OVER_T,
            "dimension": len(energies),
            "ground_energy": float(energies[0]),
            "ground_degeneracy": len(ground_indices),
            "first_gap": gap,
            "ground_mean_volume_project_units": ground_mean_v,
            "ground_sd_volume_project_units": ground_sd_v,
            "ground_probability_zero_volume": ground_pzero,
            "ground_mean_active_faces": ground_mean_active,
            "ground_four_face_probability": float(ground_weights @ p_four_by_energy),
        }
        summary_rows.append(summary)

        for index, energy in enumerate(energies):
            energy_rows.append({
                "alpha_V": alpha,
                "g_V_energy_per_project_volume": g_v,
                "eigenvalue_index": index,
                "energy": float(energy),
                "energy_above_ground": float(energy - energies[0]),
                "ground_member": bool(ground_mask[index]),
            })

        for beta in BETAS:
            weights, _ = thermal_weights(energies, beta)
            mean_energy = float(weights @ energies)
            mean_v = float(weights @ v_by_energy)
            second_v = float(weights @ v2_by_energy)
            cov_ev = float(weights @ (energies * v_by_energy) - mean_energy * mean_v)
            active_mean = float(weights @ active_by_energy)
            row = {
                "alpha_V": alpha,
                        "g_V_energy_per_project_volume": g_v,
                "beta_t": "inf" if math.isinf(beta) else beta * T,
                "mean_energy": mean_energy,
                "mean_volume_project_units": mean_v,
                "sd_volume_project_units": math.sqrt(max(0.0, second_v - mean_v**2)),
                "probability_zero_volume": float(weights @ pzero_by_energy),
                "mean_active_faces": active_mean,
                "four_face_probability": float(weights @ p_four_by_energy),
                "energy_volume_covariance": cov_ev,
            }
            thermal_rows.append(row)

            if math.isinf(beta) or any(beta == selected for selected in SELECTED_BETAS):
                for group_index, (group, projector) in enumerate(
                    zip(volume_groups, volume_projectors)
                ):
                    outcome_probability = float(
                        np.sum(weights * np.real(np.diag(
                            energy_vectors.conj().T @ projector @ energy_vectors
                        )))
                    )
                    selected_volume_rows.append({
                        "alpha_V": alpha,
                        "beta_t": "inf" if math.isinf(beta) else beta * T,
                        "volume_outcome_project_units": max(0.0, group["value"]),
                        "multiplicity": len(group["indices"]),
                        "probability": outcome_probability,
                    })

        validation[f"alpha_{alpha:g}_eigensolver_difference"] = solver_residual
        validation[f"alpha_{alpha:g}_eigen_residual"] = eigen_residual

        # Independent dense matrix-exponential checks at representative temperatures.
        shifted = hamiltonian - energies[0] * np.eye(len(energies))
        for beta in (0.0, 1.0, 20.0, 1000.0):
            if beta == 0.0:
                rho = np.eye(len(energies), dtype=complex) / len(energies)
            else:
                boltzmann = expm(-beta * shifted)
                rho = boltzmann / np.trace(boltzmann)
            expm_v = float(np.real(np.trace(rho @ volume)))
            expm_zero = float(np.real(np.trace(rho @ p_zero)))
            weights, _ = thermal_weights(energies, beta)
            spectral_v = float(weights @ v_by_energy)
            spectral_zero = float(weights @ pzero_by_energy)
            validation[f"alpha_{alpha:g}_beta_{beta:g}_expm_volume_residual"] = abs(
                expm_v - spectral_v
            )
            validation[f"alpha_{alpha:g}_beta_{beta:g}_expm_zero_residual"] = abs(
                expm_zero - spectral_zero
            )

    residual_fields = [
        value for key, value in validation.items()
        if "residual" in key or "hermiticity" in key or "difference" in key
    ]
    validation["max_residual"] = max(residual_fields)
    if validation["max_residual"] > TOL:
        raise AssertionError(f"validation residual exceeds {TOL}: {validation}")

    save_csv(OUT / "summary.csv", summary_rows)
    save_csv(OUT / "thermal_scan.csv", thermal_rows)
    save_csv(OUT / "fl_reference_readouts.csv", reference_rows)
    save_csv(OUT / "volume_distribution_selected.csv", selected_volume_rows)
    save_csv(OUT / "energy_levels.csv", energy_rows)
    (OUT / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")

    protocol = {
        "model": "H0 + g_V V_RS",
        "graph": "complete tetrahedral face adjacency K4; six equal hopping bonds",
        "sector": {"L": 4, "K": 4, "total_spin": 0, "dimension": int(len(h0))},
        "baseline": "H0 = -t sum_edges(Eij+Eji) + U/2 sum_i n_i(n_i-1)",
        "parameters": {
            "t": T,
            "U_over_t": U_OVER_T,
            "alpha_V": list(ALPHAS),
            "definition": "alpha_V = g_V * spectral_range(V_RS) / t",
            "volume_spectral_range_project_units": volume_range,
            "implied_g_V": {str(alpha): alpha * T / volume_range for alpha in ALPHAS},
        },
        "references": {
            "family": "normalized K=4 FL, equal input face areas, x=1/sqrt(3)",
            "phi_degrees": list(REFERENCE_PHI),
            "labels": {"90": "regular", "0": "flat-boundary control"},
        },
        "thermal_grid": "beta*t=0; 601 geomspace values from 1e-3 to 1e3; infinity",
        "units": "volume project units; no physical volume recalibration",
        "tolerance": TOL,
        "runtime": {"python": platform.python_version(), "numpy": np.__version__,
                    "scipy": scipy.__version__},
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
    }
    (OUT / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    provenance_paths = [INPUT, Path(__file__)]
    provenance = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in provenance_paths
    }
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")

    print(f"dimension={len(h0)}, V_range={volume_range:.12g}, max_residual={validation['max_residual']:.3g}")
    for row in summary_rows:
        print(json.dumps(row, sort_keys=True))
    for row in reference_rows:
        print(json.dumps(row, sort_keys=True))


if __name__ == "__main__":
    main()

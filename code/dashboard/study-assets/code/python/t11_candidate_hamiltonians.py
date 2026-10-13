"""Exact K=4 comparison of positive-volume and oriented signed-grasp couplings.

The default run performs the complete static/thermal comparison and the
specified exact energy-basis FL-state evolutions. Outputs are kept in
results/t11-candidate-hamiltonians/.
"""

import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import eigh
from lqg_scattering.geometric_diagnostics import angular_operators
from lqg_scattering.intertwiners import fixed_area_state
from lqg_scattering.singlets import ABS_TOL, GAMMA, ZERO_FACTOR
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.thermal import grouped_values, thermal_weights
from lqg_scattering.tetrahedra import closed_equal_area_normals


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "results/hamiltonian-studies"
OUT = ROOT / "results/t11-candidate-hamiltonians"
T = 1.0
U_VALUES = (0.0, 1.0, 5.0, 20.0)
ALPHAS = (-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0)
RING_U_VALUES = (5.0, 20.0)
RING_ALPHAS = (-1.0, 0.0, 1.0)
REFERENCE_PHI = (90, 60, 30, 10, 0)
THERMAL_BETAS = (0.0, *np.geomspace(1e-3, 1e3, 601), math.inf)
SELECTED_BETAS = (0.0, 1.0, 10.0, 100.0, 1000.0, math.inf)
PAIRS = tuple(itertools.combinations(range(4), 2))
TRIPLES = ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3))
ORIENTATION = {(0, 1, 2): 1, (0, 1, 3): -1,
               (0, 2, 3): 1, (1, 2, 3): -1}
TOL = 2e-10
Q_RESOLUTION = 1e-8
SEED_PROBABILITY_CUTOFF = 1e-12


def save_csv(path, rows):
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def jdump(value):
    return json.dumps(value, separators=(",", ":"), allow_nan=False)


def beta_label(beta):
    return "inf" if math.isinf(beta) else format(float(beta), ".17g")


def clean_matrix(matrix):
    matrix = np.asarray(matrix, dtype=complex)
    return (matrix + matrix.conj().T) / 2.0


def q_from_dots(dots, triple):
    i, j, k = triple
    left = dots[tuple(sorted((i, j)))]
    right = dots[tuple(sorted((j, k)))]
    return clean_matrix(1j * (left @ right - right @ left))


def make_reference(phi_degrees, archive):
    normals = closed_equal_area_normals(
        1.0 / math.sqrt(3.0), math.radians(phi_degrees)
    )
    _, amplitudes = fixed_area_state(
        4, spinors=spinors_from_normals(normals)
    )
    magnetic = np.asarray([
        amplitudes.get(tuple(occupation), 0j)
        for occupation in archive["occupations_m0"]
    ])
    basis = archive["singlet_basis"]
    ket = basis.conj().T @ magnetic
    residual = float(np.max(np.abs(basis @ ket - magnetic)))
    norm_residual = float(abs(np.vdot(ket, ket) - 1.0))
    if max(residual, norm_residual) > TOL:
        raise AssertionError(
            f"FL projection failed at phi={phi_degrees}: "
            f"{residual=}, {norm_residual=}"
        )
    return ket, normals, residual, norm_residual


def weighted_mean(operator, vectors, weights):
    transformed = operator @ vectors
    state_means = np.real(np.einsum("ij,ij->j", vectors.conj(), transformed))
    return float(np.dot(weights, state_means))


def energy_diagonal(operator, eigenvectors):
    transformed = operator @ eigenvectors
    return np.real(np.einsum("ij,ij->j", eigenvectors.conj(), transformed))


def density_basis_probabilities(vectors, weights):
    return np.abs(vectors) ** 2 @ weights


def matrix_groups(values, vectors):
    groups = grouped_values(values)
    records = []
    for group in groups:
        selected = vectors[:, group["indices"]]
        records.append({
            "value": group["value"],
            "indices": group["indices"],
            "vectors": selected,
            "multiplicity": len(group["indices"]),
        })
    return records


def build_geometry(archive):
    numbers = np.asarray(archive["site_boson_numbers"], dtype=int)
    area_values = numbers.astype(float) / 2.0
    active_counts = np.count_nonzero(numbers, axis=1).astype(float)
    four_active = (active_counts == 4.0).astype(float)
    p_four_operator = np.diag(four_active)
    dots = {
        pair: clean_matrix(archive[f"spin_dot_{pair[0]}_{pair[1]}"])
        for pair in PAIRS
    }
    volume = clean_matrix(archive["volume"])
    q_by_triple = {triple: q_from_dots(dots, triple) for triple in TRIPLES}
    q012, q013, q023, q123 = (q_by_triple[x] for x in TRIPLES)
    q_chi = clean_matrix(
        q012 - q013 + q023 - q123
    )

    volume_values, volume_vectors = eigh(volume)
    volume_groups = matrix_groups(volume_values, volume_vectors)
    cutoff = ZERO_FACTOR * max(1.0, float(np.max(np.abs(volume_values))))
    zero_indices = np.flatnonzero(np.abs(volume_values) <= cutoff)
    zero_vectors = volume_vectors[:, zero_indices]
    p_zero = zero_vectors @ zero_vectors.conj().T
    volume_range = float(volume_values[-1] - volume_values[0])

    _, angle_ops = angular_operators(numbers, dots)
    angle_ops = [clean_matrix(op * four_active[None, :]) for op in angle_ops]
    angle_sym = {}
    for i, left in enumerate(angle_ops):
        for j in range(i, len(angle_ops)):
            right = angle_ops[j]
            angle_sym[i, j] = clean_matrix((left @ right + right @ left) / 2.0)

    area_products = {}
    for i, j in itertools.combinations_with_replacement(range(4), 2):
        area_products[i, j] = area_values[:, i] * area_values[:, j]

    assignments = sorted({tuple(int(x) for x in row) for row in numbers})
    assignment_masks = {
        assignment: np.all(numbers == np.asarray(assignment)[None, :], axis=1)
        for assignment in assignments
    }
    return {
        "numbers": numbers,
        "areas": area_values,
        "active_counts": active_counts,
        "four_active": four_active,
        "dots": dots,
        "volume": volume,
        "volume2": clean_matrix(volume @ volume),
        "volume_four": clean_matrix(
            p_four_operator @ volume @ p_four_operator
        ),
        "volume_values": volume_values,
        "volume_vectors": volume_vectors,
        "volume_groups": volume_groups,
        "volume_range": volume_range,
        "zero_vectors": zero_vectors,
        "p_zero": clean_matrix(p_zero),
        "zero_dimension": int(len(zero_indices)),
        "zero_cutoff": float(cutoff),
        "q_by_triple": q_by_triple,
        "q012": q012,
        "q012_2": clean_matrix(q012 @ q012),
        "q_chi": q_chi,
        "q_chi_2": clean_matrix(q_chi @ q_chi),
        "q_range": float(np.ptp(np.linalg.eigvalsh(q_chi))),
        "angle_ops": angle_ops,
        "angle_sym": angle_sym,
        "angle_pairs": tuple(itertools.combinations(range(6), 2)),
        "area_products": area_products,
        "assignments": assignments,
        "assignment_masks": assignment_masks,
    }


def common_state_metadata(model, state_kind, state_label):
    return {
        "model_id": model["model_id"],
        "study_role": model["study_role"],
        "graph": model["graph"],
        "candidate": model["candidate"],
        "U_over_t": model["U_over_t"],
        "alpha": model["alpha"],
        "alpha_definition": model["alpha_definition"],
        "coupling_energy_per_operator_unit": model["coupling"],
        "state_kind": state_kind,
        "state_label": state_label,
    }


def state_readout(model, geometry, vectors, weights, state_kind, state_label,
                  energy, energy_gap, multiplicity):
    weights = np.asarray(weights, dtype=float)
    weights = weights / weights.sum()
    basis_probability = density_basis_probabilities(vectors, weights)
    areas = geometry["areas"]
    mean_area = basis_probability @ areas
    area_covariance = np.empty((4, 4), dtype=float)
    for i in range(4):
        for j in range(i, 4):
            second = float(np.dot(
                basis_probability, geometry["area_products"][i, j]
            ))
            cov = second - mean_area[i] * mean_area[j]
            area_covariance[i, j] = area_covariance[j, i] = cov

    p_four = float(np.dot(basis_probability, geometry["four_active"]))
    volume_mean = weighted_mean(geometry["volume"], vectors, weights)
    volume_second = weighted_mean(geometry["volume2"], vectors, weights)
    zero_probability = weighted_mean(geometry["p_zero"], vectors, weights)
    q_mean = weighted_mean(geometry["q012"], vectors, weights)
    q_second = weighted_mean(geometry["q012_2"], vectors, weights)
    q_chi_mean = weighted_mean(geometry["q_chi"], vectors, weights)
    q_chi_second = weighted_mean(geometry["q_chi_2"], vectors, weights)
    pair_dot_means = [
        weighted_mean(geometry["dots"][pair], vectors, weights)
        for pair in PAIRS
    ]

    angle_means = []
    angle_covariance = np.full((6, 6), np.nan, dtype=float)
    if p_four > 1e-14:
        raw_means = np.asarray([
            weighted_mean(operator, vectors, weights)
            for operator in geometry["angle_ops"]
        ])
        angle_means = (raw_means / p_four).tolist()
        for i in range(6):
            for j in range(i, 6):
                key = (i, j) if i <= j else (j, i)
                second = weighted_mean(
                    geometry["angle_sym"][key], vectors, weights
                ) / p_four
                value = second - angle_means[i] * angle_means[j]
                angle_covariance[i, j] = angle_covariance[j, i] = value

    assignment_rows = []
    for assignment, mask in geometry["assignment_masks"].items():
        probability = float(basis_probability[mask].sum())
        if probability <= 1e-14:
            continue
        assignment_rows.append({
            "twice_spins": " ".join(map(str, assignment)),
            "probability": probability,
        })

    volume_rows = []
    for group in geometry["volume_groups"]:
        volume_vectors = group["vectors"]
        amplitudes = volume_vectors.conj().T @ vectors
        probability = float(np.dot(
            weights, np.sum(np.abs(amplitudes) ** 2, axis=0)
        ))
        selected_vectors = geometry["volume_vectors"][:, group["indices"]]
        projected_vectors = selected_vectors @ (selected_vectors.conj().T @ vectors)
        projected_probability = density_basis_probabilities(
            projected_vectors, weights
        )
        conditional_probability = (
            float(projected_probability @ geometry["four_active"]) / p_four
            if p_four > 1e-14 else math.nan
        )
        volume_rows.append({
            "volume_outcome_project_units": max(0.0, float(group["value"])),
            "multiplicity": group["multiplicity"],
            "probability": probability,
            "four_face_conditioned_probability": conditional_probability,
        })

    row = common_state_metadata(model, state_kind, state_label)
    row.update({
        "energy_expectation": float(energy),
        "energy_above_ground": (
            float(energy_gap) if energy_gap != "" else ""
        ),
        "multiplicity": int(multiplicity),
        "face_area_means": jdump(mean_area.tolist()),
        "face_area_covariance": jdump(area_covariance.tolist()),
        "area_assignment_probabilities": jdump(assignment_rows),
        "active_face_probabilities": jdump({
            str(count): float(basis_probability[
                geometry["active_counts"] == count
            ].sum())
            for count in range(1, 5)
        }),
        "mean_active_faces": float(np.dot(
            basis_probability, geometry["active_counts"]
        )),
        "four_face_probability": p_four,
        "volume_mean_project_units": volume_mean,
        "volume_sd_project_units": math.sqrt(max(
            0.0, volume_second - volume_mean**2
        )),
        "conditional_volume_mean_project_units": (
            weighted_mean(geometry["volume_four"], vectors, weights) / p_four
            if p_four > 1e-14 else ""
        ),
        "probability_zero_volume": zero_probability,
        "signed_q012_mean": q_mean,
        "signed_q012_rms": math.sqrt(max(0.0, q_second)),
        "Q_chi_mean": q_chi_mean,
        "Q_chi_rms": math.sqrt(max(0.0, q_chi_second)),
        "pair_dot_means": jdump(pair_dot_means),
        "four_face_angular_means": jdump(angle_means),
        "four_face_angular_covariance": (
            jdump(angle_covariance.tolist()) if angle_means else ""
        ),
        "four_face_angular_rms_sd": (
            float(np.sqrt(np.mean(np.maximum(
                0.0, np.diag(angle_covariance)
            )))) if angle_means else ""
        ),
    })
    return row, assignment_rows, volume_rows


def build_model(graph, candidate, u_over_t, alpha, operators, archives):
    archive = archives[graph]
    edges = (PAIRS if graph == "complete"
             else ((0, 1), (1, 2), (2, 3), (0, 3)))
    onsite = np.asarray(archive["onsite_penalty"], dtype=complex)
    hopping = sum(
        (archive[f"hopping_{i}_{j}"] for i, j in edges),
        np.zeros_like(onsite),
    )
    h0 = clean_matrix(u_over_t * T * onsite - T * hopping)
    if candidate == "positive_volume":
        operator = operators["volume"]
        span = operators["volume_range"]
        coefficient = alpha * T / span
        alpha_definition = "alpha_V = g_V * spectral_range(V_RS) / t"
        symbol = "g_V"
    elif candidate == "signed_grasp":
        operator = operators["q_chi"]
        span = operators["q_range"]
        coefficient = alpha * T / span
        alpha_definition = "alpha_chi = lambda_chi * spectral_range(Q_chi) / t"
        symbol = "lambda_chi"
    else:
        raise ValueError(candidate)
    hamiltonian = clean_matrix(h0 + coefficient * operator)
    model_id = (
        f"{graph}_{candidate}_U{u_over_t:g}_alpha{alpha:+g}"
        .replace("+", "p").replace("-", "m").replace(".", "p")
    )
    return {
        "model_id": model_id,
        "study_role": ("tetrahedral_candidate" if graph == "complete"
                       else "sparse_topology_control"),
        "graph": graph,
        "candidate": candidate,
        "U_over_t": float(u_over_t),
        "alpha": float(alpha),
        "alpha_definition": alpha_definition,
        "coupling_symbol": symbol,
        "coupling": float(coefficient),
        "operator_range": float(span),
        "t": T,
        "hamiltonian": hamiltonian,
        "h0": h0,
    }


def all_models(operators, archives):
    for candidate in ("positive_volume", "signed_grasp"):
        for u_over_t in U_VALUES:
            for alpha in ALPHAS:
                yield build_model(
                    "complete", candidate, u_over_t, alpha,
                    operators, archives
                )
    for u_over_t in RING_U_VALUES:
        for alpha in RING_ALPHAS:
            yield build_model(
                "ring", "positive_volume", u_over_t, alpha,
                operators, archives
            )


def collect_thermal(model, geometry, energies, eigenvectors):
    probabilities = np.abs(eigenvectors) ** 2
    area_by_energy = probabilities.T @ geometry["areas"]
    count_by_energy = probabilities.T @ geometry["active_counts"]
    p_four_by_energy = probabilities.T @ geometry["four_active"]
    area_product_by_energy = {
        pair: probabilities.T @ values
        for pair, values in geometry["area_products"].items()
    }
    assignment_by_energy = {
        key: probabilities.T @ mask.astype(float)
        for key, mask in geometry["assignment_masks"].items()
    }

    operator_diags = {}
    op_map = {
        "V": geometry["volume"],
        "V2": geometry["volume2"],
        "Vfour": geometry["volume_four"],
        "Pzero": geometry["p_zero"],
        "q012": geometry["q012"],
        "q0122": geometry["q012_2"],
        "Qchi": geometry["q_chi"],
        "Qchi2": geometry["q_chi_2"],
    }
    for index, pair in enumerate(PAIRS):
        op_map[f"D{pair[0]}{pair[1]}"] = geometry["dots"][pair]
    for index, operator in enumerate(geometry["angle_ops"]):
        op_map[f"C{index}"] = operator
    for (i, j), operator in geometry["angle_sym"].items():
        op_map[f"C2_{i}_{j}"] = operator
    for name, operator in op_map.items():
        operator_diags[name] = energy_diagonal(operator, eigenvectors)

    volume_outcome_by_energy = []
    for group in geometry["volume_groups"]:
        amplitudes = group["vectors"].conj().T @ eigenvectors
        volume_outcome_by_energy.append(
            np.sum(np.abs(amplitudes) ** 2, axis=0)
        )
    volume_outcome_by_energy = np.asarray(volume_outcome_by_energy)

    thermal_rows = []
    selected_volume_rows = []
    selected_assignment_rows = []
    for beta in THERMAL_BETAS:
        weights, _ = thermal_weights(energies, beta)
        mean_energy = float(weights @ energies)
        energy_second = float(weights @ (energies**2))
        mean_v = float(weights @ operator_diags["V"])
        mean_v2 = float(weights @ operator_diags["V2"])
        mean_q = float(weights @ operator_diags["q012"])
        mean_q2 = float(weights @ operator_diags["q0122"])
        mean_qchi = float(weights @ operator_diags["Qchi"])
        mean_qchi2 = float(weights @ operator_diags["Qchi2"])
        p_four = float(weights @ p_four_by_energy)
        row = {
            "model_id": model["model_id"],
            "study_role": model["study_role"],
            "graph": model["graph"],
            "candidate": model["candidate"],
            "U_over_t": model["U_over_t"],
            "alpha": model["alpha"],
            "beta_t": beta_label(beta),
            "mean_energy": mean_energy,
            "energy_sd": math.sqrt(max(0.0, energy_second - mean_energy**2)),
            "specific_heat_over_kB": (
                beta**2 * max(0.0, energy_second - mean_energy**2)
                if math.isfinite(beta) else 0.0
            ),
            "energy_volume_covariance": float(
                weights @ (energies * operator_diags["V"])
                - mean_energy * mean_v
            ),
            "mean_volume_project_units": mean_v,
            "sd_volume_project_units": math.sqrt(max(0.0, mean_v2 - mean_v**2)),
            "probability_zero_volume": float(weights @ operator_diags["Pzero"]),
            "conditional_volume_mean_project_units": (
                float(weights @ operator_diags["Vfour"]) / p_four
                if p_four > 1e-14 else ""
            ),
            "mean_signed_q012": mean_q,
            "signed_q012_rms": math.sqrt(max(0.0, mean_q2)),
            "mean_Q_chi": mean_qchi,
            "Q_chi_rms": math.sqrt(max(0.0, mean_qchi2)),
            "mean_active_faces": float(weights @ count_by_energy),
            "four_face_probability": p_four,
        }
        area_means = weights @ area_by_energy
        for i in range(4):
            row[f"face_area_mean_{i}"] = float(area_means[i])
            row[f"face_area_sd_{i}"] = math.sqrt(max(
                0.0,
                float(weights @ area_product_by_energy[i, i])
                - area_means[i] ** 2,
            ))
        for i, j in itertools.combinations_with_replacement(range(4), 2):
            cov = float(weights @ area_product_by_energy[i, j]
                        - area_means[i] * area_means[j])
            row[f"face_area_cov_{i}_{j}"] = cov
        for index, pair in enumerate(PAIRS):
            row[f"D{pair[0]}{pair[1]}_mean"] = float(
                weights @ operator_diags[f"D{pair[0]}{pair[1]}"]
            )
        if p_four > 1e-14:
            angle_means = np.asarray([
                float(weights @ operator_diags[f"C{idx}"]) / p_four
                for idx in range(6)
            ])
            for idx, pair in enumerate(PAIRS):
                row[f"C{pair[0]}{pair[1]}_mean"] = float(angle_means[idx])
                second = float(
                    weights @ operator_diags[f"C2_{idx}_{idx}"] / p_four
                )
                row[f"C{pair[0]}{pair[1]}_sd"] = math.sqrt(max(
                    0.0, second - angle_means[idx] ** 2
                ))
            for i in range(6):
                for j in range(i, 6):
                    second = float(
                        weights @ operator_diags[f"C2_{i}_{j}"] / p_four
                    )
                    cov = second - angle_means[i] * angle_means[j]
                    row[f"C_cov_{i}_{j}"] = cov
            row["conditional_angle_rms_sd"] = float(np.sqrt(np.mean([
                row[f"C{pair[0]}{pair[1]}_sd"] ** 2 for pair in PAIRS
            ])))
        else:
            for pair in PAIRS:
                row[f"C{pair[0]}{pair[1]}_mean"] = ""
                row[f"C{pair[0]}{pair[1]}_sd"] = ""
            for i in range(6):
                for j in range(i, 6):
                    row[f"C_cov_{i}_{j}"] = ""
            row["conditional_angle_rms_sd"] = ""
        thermal_rows.append(row)

        is_selected = any(math.isclose(
            float(beta), selected, rel_tol=0.0, abs_tol=1e-12
        ) for selected in SELECTED_BETAS if math.isfinite(beta))
        if is_selected or math.isinf(beta):
            for group_index, group in enumerate(geometry["volume_groups"]):
                probability = float(weights @ volume_outcome_by_energy[group_index])
                selected_volume_rows.append({
                    "model_id": model["model_id"],
                    "graph": model["graph"],
                    "candidate": model["candidate"],
                    "U_over_t": model["U_over_t"],
                    "alpha": model["alpha"],
                    "beta_t": beta_label(beta),
                    "volume_outcome_project_units": max(0.0, group["value"]),
                    "multiplicity": group["multiplicity"],
                    "probability": probability,
                })
            if is_selected:
                for assignment, by_energy in assignment_by_energy.items():
                    probability = float(weights @ by_energy)
                    if probability <= 1e-14:
                        continue
                    selected_assignment_rows.append({
                        "model_id": model["model_id"],
                        "graph": model["graph"],
                        "candidate": model["candidate"],
                        "U_over_t": model["U_over_t"],
                        "alpha": model["alpha"],
                        "beta_t": beta_label(beta),
                        "twice_spins": " ".join(map(str, assignment)),
                        "probability": probability,
                    })
    return thermal_rows, selected_volume_rows, selected_assignment_rows


def direct_spin_one_grasp_check(geometry):
    """Compare archived triple-grasp spectra with explicit local spin-one matrices."""
    identity = np.eye(3, dtype=complex)
    jplus = np.zeros((3, 3), dtype=complex)
    jplus[0, 1] = math.sqrt(2.0)
    jplus[1, 2] = math.sqrt(2.0)
    jminus = jplus.conj().T
    jz = np.diag([1.0, 0.0, -1.0])
    local = (jplus + jminus) / 2, (jplus - jminus) / (2j), jz
    site_j = []
    for site in range(4):
        components = []
        for component in local:
            result = np.array([[1.0 + 0.0j]])
            for other in range(4):
                result = np.kron(result, component if other == site else identity)
            components.append(result)
        site_j.append(components)
    total = [
        sum((site_j[site][axis] for site in range(4)),
            np.zeros((81, 81), dtype=complex))
        for axis in range(3)
    ]
    total_j2 = sum((operator @ operator for operator in total),
                   np.zeros((81, 81), dtype=complex))
    j2_values, j2_vectors = eigh(clean_matrix(total_j2))
    singlets = j2_vectors[:, np.abs(j2_values) < 1e-9]
    if singlets.shape[1] != 3:
        raise AssertionError("spin-one tensor product should have 3 singlets")
    direct_dots = {}
    for i, j in PAIRS:
        direct_dots[i, j] = sum(
            (site_j[i][axis] @ site_j[j][axis] for axis in range(3)),
            np.zeros((81, 81), dtype=complex),
        )
    direct_q = {}
    for triple in TRIPLES:
        i, j, k = triple
        left = direct_dots[tuple(sorted((i, j)))]
        right = direct_dots[tuple(sorted((j, k)))]
        direct_q[triple] = clean_matrix(1j * (left @ right - right @ left))
    direct_chi = clean_matrix(
        sum((ORIENTATION[triple] * direct_q[triple]
             for triple in TRIPLES), np.zeros((81, 81), dtype=complex))
    )
    direct_q_block = singlets.conj().T @ direct_q[0, 1, 2] @ singlets
    direct_chi_block = singlets.conj().T @ direct_chi @ singlets

    mask = np.all(geometry["numbers"] == 2, axis=1)
    archived_q = geometry["q012"][np.ix_(mask, mask)]
    archived_chi = geometry["q_chi"][np.ix_(mask, mask)]
    q_residual = float(np.max(np.abs(
        np.linalg.eigvalsh(direct_q_block) - np.linalg.eigvalsh(archived_q)
    )))
    chi_residual = float(np.max(np.abs(
        np.linalg.eigvalsh(direct_chi_block) - np.linalg.eigvalsh(archived_chi)
    )))
    return q_residual, chi_residual


def permutation_checks(archive, geometry):
    occupations = np.asarray(archive["occupations_m0"], dtype=int)
    basis = np.asarray(archive["singlet_basis"], dtype=complex)
    index = {tuple(row): i for i, row in enumerate(occupations)}
    results = {}
    for name, permutation, parity in (
        ("odd", (1, 0, 2, 3), -1),
        ("even", (1, 2, 0, 3), 1),
    ):
        target = np.empty_like(occupations)
        for old_site, new_site in enumerate(permutation):
            target[:, 2 * new_site:2 * new_site + 2] = (
                occupations[:, 2 * old_site:2 * old_site + 2]
            )
        target_rows = np.asarray([index[tuple(row)] for row in target])
        permutation_matrix = np.zeros(
            (len(occupations), len(occupations)), dtype=complex
        )
        permutation_matrix[target_rows, np.arange(len(target_rows))] = 1.0
        unitary = basis.conj().T @ permutation_matrix @ basis
        results[f"{name}_unitary"] = float(np.max(np.abs(
            unitary.conj().T @ unitary - np.eye(unitary.shape[0])
        )))
        transformed_q = unitary @ geometry["q_chi"] @ unitary.conj().T
        results[f"{name}_orientation_covariance"] = float(np.max(np.abs(
            transformed_q - parity * geometry["q_chi"]
        )))
        transformed_v = unitary @ geometry["volume"] @ unitary.conj().T
        results[f"{name}_volume_invariance"] = float(np.max(np.abs(
            transformed_v - geometry["volume"]
        )))
    return results


def initialize(archive):
    geometry = build_geometry(archive)
    references = {}
    reference_meta = {}
    for phi in REFERENCE_PHI:
        ket, normals, projection_residual, norm_residual = make_reference(
            phi, archive
        )
        label = "regular" if phi == 90 else (
            "flat_boundary" if phi == 0 else f"phi_{phi}"
        )
        references[phi] = ket
        reference_meta[str(phi)] = {
            "label": label,
            "phi_degrees": phi,
            "input_normal_gram": (normals @ normals.T).tolist(),
            "projection_residual": projection_residual,
            "norm_residual": norm_residual,
        }
    return geometry, references, reference_meta


def run_static(archives, complete_archive, geometry, references):
    model_rows = []
    energy_rows = []
    state_rows = []
    state_distribution_rows = []
    area_assignment_rows = []
    fl_population_rows = []
    thermal_rows = []
    thermal_volume_rows = []
    thermal_area_rows = []
    validation = {}

    for model in all_models(
        {"volume": geometry["volume"], "volume_range": geometry["volume_range"],
         "q_chi": geometry["q_chi"], "q_range": geometry["q_range"]},
        archives,
    ):
        energies, eigenvectors = eigh(model["hamiltonian"])
        groups = matrix_groups(energies, eigenvectors)
        group0 = groups[0]
        gap = groups[1]["value"] - groups[0]["value"] if len(groups) > 1 else math.nan
        eig_residual = float(np.max(np.abs(
            model["hamiltonian"] @ eigenvectors
            - eigenvectors * energies[None, :]
        )))
        orthogonality = float(np.max(np.abs(
            eigenvectors.conj().T @ eigenvectors - np.eye(len(energies))
        )))
        validation[f"{model['model_id']}_eigen_residual"] = eig_residual
        validation[f"{model['model_id']}_orthogonality"] = orthogonality
        ground_vectors = group0["vectors"]
        ground_weights = np.full(group0["multiplicity"],
                                 1.0 / group0["multiplicity"])
        ground_state, _, _ = state_readout(
            model, geometry, ground_vectors, ground_weights, "energy_group",
            "ground", group0["value"], 0.0, group0["multiplicity"]
        )
        model_rows.append({
            "model_id": model["model_id"],
            "study_role": model["study_role"],
            "graph": model["graph"],
            "candidate": model["candidate"],
            "U_over_t": model["U_over_t"],
            "alpha": model["alpha"],
            "alpha_definition": model["alpha_definition"],
            "coupling_symbol": model["coupling_symbol"],
            "coupling_energy_per_operator_unit": model["coupling"],
            "operator_spectral_range": model["operator_range"],
            "dimension": len(energies),
            "ground_energy": float(energies[0]),
            "ground_degeneracy": group0["multiplicity"],
            "first_distinct_gap": float(gap),
            "ground_volume_mean_project_units": ground_state[
                "volume_mean_project_units"
            ],
            "ground_volume_sd_project_units": ground_state[
                "volume_sd_project_units"
            ],
            "ground_probability_zero_volume": ground_state[
                "probability_zero_volume"
            ],
            "ground_four_face_probability": ground_state["four_face_probability"],
            "ground_signed_q012_mean": ground_state["signed_q012_mean"],
            "ground_Q_chi_mean": ground_state["Q_chi_mean"],
        })
        for energy_index, value in enumerate(energies):
            energy_rows.append({
                "model_id": model["model_id"],
                "graph": model["graph"],
                "candidate": model["candidate"],
                "U_over_t": model["U_over_t"],
                "alpha": model["alpha"],
                "eigenvalue_index": energy_index,
                "energy": float(value),
                "energy_above_ground": float(value - energies[0]),
            })

        selected_groups = groups[:3]
        for level_index, group in enumerate(selected_groups):
            state_label = ("ground" if level_index == 0
                           else f"excited_group_{level_index}")
            state_row, assignment_rows, volume_rows = state_readout(
                model, geometry, group["vectors"],
                np.full(group["multiplicity"], 1 / group["multiplicity"]),
                "energy_group", state_label, group["value"],
                group["value"] - energies[0], group["multiplicity"],
            )
            state_rows.append(state_row)
            for row in assignment_rows:
                area_assignment_rows.append({
                    **common_state_metadata(model, "energy_group", state_label),
                    **row,
                })
            for row in volume_rows:
                state_distribution_rows.append({
                    **common_state_metadata(model, "energy_group", state_label),
                    **row,
                })

        for phi, ket in references.items():
            label = "regular" if phi == 90 else (
                "flat_boundary" if phi == 0 else f"phi_{phi}"
            )
            ket_column = ket[:, None]
            reference_row, assignment_rows, volume_rows = state_readout(
                model, geometry, ket_column, np.asarray([1.0]),
                "FL_reference", label,
                weighted_mean(model["hamiltonian"], ket_column, np.asarray([1.0])),
                "", 1,
            )
            state_rows.append(reference_row)
            for row in assignment_rows:
                area_assignment_rows.append({
                    **common_state_metadata(model, "FL_reference", label), **row
                })
            for row in volume_rows:
                state_distribution_rows.append({
                    **common_state_metadata(model, "FL_reference", label), **row
                })
            overlaps = np.abs(eigenvectors.conj().T @ ket) ** 2
            for level_index, group in enumerate(selected_groups):
                fl_population_rows.append({
                    "model_id": model["model_id"],
                    "graph": model["graph"],
                    "candidate": model["candidate"],
                    "U_over_t": model["U_over_t"],
                    "alpha": model["alpha"],
                    "reference": label,
                    "phi_degrees": phi,
                    "energy_group_index": level_index,
                    "energy": group["value"],
                    "degeneracy": group["multiplicity"],
                    "probability_in_group": float(
                        overlaps[group["indices"]].sum()
                    ),
                })
            fl_population_rows.append({
                "model_id": model["model_id"],
                "graph": model["graph"],
                "candidate": model["candidate"],
                "U_over_t": model["U_over_t"],
                "alpha": model["alpha"],
                "reference": label,
                "phi_degrees": phi,
                "energy_group_index": "other",
                "energy": "",
                "degeneracy": "",
                "probability_in_group": float(
                    max(0.0, 1.0 - sum(
                        overlaps[group["indices"]].sum()
                        for group in selected_groups
                    ))
                ),
            })

        thermo, volume_outcomes, area_outcomes = collect_thermal(
            model, geometry, energies, eigenvectors
        )
        thermal_rows.extend(thermo)
        thermal_volume_rows.extend(volume_outcomes)
        thermal_area_rows.extend(area_outcomes)

        if model["alpha"] == 0.0:
            baseline_spectra = np.linalg.eigvalsh(model["h0"])
            validation[f"{model['model_id']}_alpha0_baseline_spectrum"] = float(
                np.max(np.abs(energies - baseline_spectra))
            )

    output_rows = (
        ("model_summary.csv", model_rows),
        ("energy_levels.csv", energy_rows),
        ("state_geometry.csv", state_rows),
        ("state_volume_distributions.csv", state_distribution_rows),
        ("state_area_assignments.csv", area_assignment_rows),
        ("fl_energy_populations.csv", fl_population_rows),
        ("thermal_scan.csv", thermal_rows),
        ("thermal_volume_outcomes.csv", thermal_volume_rows),
        ("thermal_area_assignments_selected.csv", thermal_area_rows),
    )
    for name, rows in output_rows:
        save_csv(OUT / name, rows)
    return validation


def dynamic_operator_map(geometry):
    operators = {
        "V": geometry["volume"],
        "V2": geometry["volume2"],
        "Pzero": geometry["p_zero"],
        "q012": geometry["q012"],
        "q0122": geometry["q012_2"],
        "Qchi": geometry["q_chi"],
        "Qchi2": geometry["q_chi_2"],
        "P4": np.diag(geometry["four_active"]),
        "active_faces": np.diag(geometry["active_counts"]),
        "H_unused": np.zeros_like(geometry["volume"]),
    }
    for i in range(4):
        operators[f"A{i}"] = np.diag(geometry["areas"][:, i])
    for i, j in itertools.combinations_with_replacement(range(4), 2):
        operators[f"A2_{i}_{j}"] = np.diag(
            geometry["area_products"][i, j]
        )
    for index, pair in enumerate(PAIRS):
        operators[f"D{pair[0]}{pair[1]}"] = geometry["dots"][pair]
        operators[f"C{pair[0]}{pair[1]}"] = geometry["angle_ops"][index]
    for (i, j), operator in geometry["angle_sym"].items():
        operators[f"C2_{i}_{j}"] = operator
    return operators


def relevant_dynamic_gaps(energies, coefficients, operator_energy, scales):
    probabilities = np.abs(coefficients) ** 2
    gaps = np.abs(energies[:, None] - energies[None, :])
    upper = np.triu(np.ones(gaps.shape, dtype=bool), 1)
    strength = probabilities[:, None] * probabilities[None, :]
    for name, matrix in operator_energy.items():
        coefficient = np.abs(
            coefficients.conj()[:, None] * coefficients[None, :]
            * matrix
        )
        strength = np.maximum(
            strength, 2.0 * coefficient / max(scales.get(name, 1.0), 1e-30)
        )
    scale = max(1.0, float(energies[-1] - energies[0]))
    selected = upper & (strength >= Q_RESOLUTION) & (
        gaps >= 1e-10 * scale
    )
    values = gaps[selected]
    return values, strength[selected]


def exact_dynamic_series(model, geometry, operators, reference, seed_label):
    energies, eigenvectors = eigh(model["hamiltonian"])
    coefficients = eigenvectors.conj().T @ reference
    operator_energy = {
        name: eigenvectors.conj().T @ operator @ eigenvectors
        for name, operator in operators.items()
        if name != "H_unused"
    }
    scales = {
        "V": max(geometry["volume_range"], 1e-30),
        "V2": max(geometry["volume_range"] ** 2, 1e-30),
        "q012": max(geometry["q_range"] / 4.0, 1e-30),
        "q0122": max((geometry["q_range"] / 4.0) ** 2, 1e-30),
        "Qchi": max(geometry["q_range"], 1e-30),
        "Qchi2": max(geometry["q_range"] ** 2, 1e-30),
        "active_faces": 4.0,
        "P4": 1.0,
    }
    for name in operator_energy:
        if name.startswith("A"):
            scales[name] = 4.0 if not name.startswith("A2") else 16.0
        elif name.startswith("D"):
            scales[name] = 6.0
        elif name.startswith("C"):
            scales[name] = 1.0
        else:
            scales.setdefault(name, 1.0)
    beat_gaps, beat_strengths = relevant_dynamic_gaps(
        energies, coefficients, operator_energy, scales
    )
    if beat_gaps.size == 0:
        raise AssertionError("no resolved energy beats for prepared seed")
    min_gap = float(np.min(beat_gaps))
    max_gap = float(np.max(beat_gaps))
    fastest_period = 2.0 * math.pi / max_gap
    slowest_period = 2.0 * math.pi / min_gap
    dt = fastest_period / 20.0
    tmax = 10.0 * slowest_period
    required_uniform = int(math.ceil(tmax / dt)) + 1
    early_end = 10.0 * fastest_period
    early_times = np.linspace(
        0.0, early_end, int(math.ceil(early_end / dt)) + 1
    )
    log_times = np.geomspace(
        max(early_end, dt), tmax, 900
    ) if tmax > max(early_end, dt) else np.asarray([])
    times = np.unique(np.concatenate((early_times, log_times)))

    amplitudes = np.exp(-1j * np.outer(times, energies)) * coefficients[None, :]
    norm_series = np.sum(np.abs(amplitudes) ** 2, axis=1)
    initial_energy = float(np.dot(np.abs(coefficients) ** 2, energies))
    energy_series = np.abs(amplitudes) ** 2 @ energies
    expectations = {}
    for name, matrix in operator_energy.items():
        operated = amplitudes @ matrix.T
        expectations[name] = np.real(
            np.sum(amplitudes.conj() * operated, axis=1)
        )
    survival_amplitude = np.exp(-1j * np.outer(times, energies)) @ (
        np.abs(coefficients) ** 2
    )
    return_probability = np.abs(survival_amplitude) ** 2
    p_four = expectations["P4"]
    area_means = np.stack(
        [expectations[f"A{i}"] for i in range(4)], axis=1
    )
    rows = []
    for index, tau in enumerate(times):
        row = {
            "model_id": model["model_id"],
            "graph": model["graph"],
            "candidate": model["candidate"],
            "U_over_t": model["U_over_t"],
            "alpha": model["alpha"],
            "seed": seed_label,
            "tau_t_over_hbar": float(tau),
            "time_grid": ("dense_fast_beat" if tau <= early_end * (1 + 1e-12)
                          else "log_spaced_exact_sample"),
            "return_probability": float(return_probability[index]),
            "norm_residual": float(abs(norm_series[index] - 1.0)),
            "energy_expectation": float(energy_series[index]),
            "energy_residual": float(
                abs(energy_series[index] - initial_energy)
            ),
            "total_area_expectation": float(area_means[index].sum()),
            "total_area_residual": float(abs(area_means[index].sum() - 4.0)),
            "closure_total_spin": 0.0,
            "mean_volume_project_units": float(expectations["V"][index]),
            "sd_volume_project_units": math.sqrt(max(
                0.0,
                float(expectations["V2"][index])
                - float(expectations["V"][index]) ** 2,
            )),
            "probability_zero_volume": float(expectations["Pzero"][index]),
            "four_face_probability": float(p_four[index]),
            "mean_active_faces": float(expectations["active_faces"][index]),
            "signed_q012_mean": float(expectations["q012"][index]),
            "signed_q012_rms": math.sqrt(max(
                0.0, float(expectations["q0122"][index])
            )),
            "Q_chi_mean": float(expectations["Qchi"][index]),
            "Q_chi_rms": math.sqrt(max(
                0.0, float(expectations["Qchi2"][index])
            )),
        }
        for i in range(4):
            row[f"face_area_mean_{i}"] = float(area_means[index, i])
            row[f"face_area_sd_{i}"] = math.sqrt(max(
                0.0, float(expectations[f"A2_{i}_{i}"][index])
                - area_means[index, i] ** 2
            ))
        for i, j in itertools.combinations_with_replacement(range(4), 2):
            row[f"face_area_cov_{i}_{j}"] = float(
                expectations[f"A2_{i}_{j}"][index]
                - area_means[index, i] * area_means[index, j]
            )
        if p_four[index] > 1e-14:
            means = np.asarray([
                expectations[f"C{pair[0]}{pair[1]}"][index] / p_four[index]
                for pair in PAIRS
            ])
            for pair_index, pair in enumerate(PAIRS):
                row[f"C{pair[0]}{pair[1]}_mean"] = float(means[pair_index])
                second = (
                    expectations[f"C2_{pair_index}_{pair_index}"][index]
                    / p_four[index]
                )
                row[f"C{pair[0]}{pair[1]}_sd"] = math.sqrt(max(
                    0.0, float(second - means[pair_index] ** 2)
                ))
            for i in range(6):
                for j in range(i, 6):
                    row[f"C_cov_{i}_{j}"] = float(
                        expectations[f"C2_{i}_{j}"][index] / p_four[index]
                        - means[i] * means[j]
                    )
        else:
            for pair in PAIRS:
                row[f"C{pair[0]}{pair[1]}_mean"] = ""
                row[f"C{pair[0]}{pair[1]}_sd"] = ""
            for i in range(6):
                for j in range(i, 6):
                    row[f"C_cov_{i}_{j}"] = ""
        rows.append(row)

    schedule = {
        "model_id": model["model_id"],
        "graph": model["graph"],
        "candidate": model["candidate"],
        "U_over_t": model["U_over_t"],
        "alpha": model["alpha"],
        "seed": seed_label,
        "initial_seed_support_dimension": int(
            np.count_nonzero(np.abs(coefficients) ** 2 > SEED_PROBABILITY_CUTOFF)
        ),
        "resolved_pair_count": int(len(beat_gaps)),
        "resolved_amplitude_threshold": Q_RESOLUTION,
        "seed_probability_cutoff": SEED_PROBABILITY_CUTOFF,
        "minimum_resolved_gap": min_gap,
        "maximum_resolved_gap": max_gap,
        "fastest_period": fastest_period,
        "slowest_period": slowest_period,
        "time_horizon_t_over_hbar": tmax,
        "uniform_grid_dt": dt,
        "uniform_grid_points_required": required_uniform,
        "computed_exact_sample_count": int(len(times)),
        "dense_initial_sample_count": int(len(early_times)),
        "log_spaced_late_sample_count": int(len(log_times)),
        "resolved_beat_strength_min": float(beat_strengths.min()),
    }
    return rows, schedule


def run_dynamics(archives, geometry, references):
    operators = dynamic_operator_map(geometry)
    rows = []
    schedules = []
    models = []
    for u_over_t in (5.0, 20.0):
        h0_model = build_model(
            "complete", "positive_volume", u_over_t, 0.0,
            {"volume": geometry["volume"],
             "volume_range": geometry["volume_range"],
             "q_chi": geometry["q_chi"], "q_range": geometry["q_range"]},
            archives,
        )
        unique_models = [("baseline", h0_model)]
        for alpha in (-1.0, 1.0):
            unique_models.append((
                f"positive_volume_{alpha:+g}",
                build_model(
                    "complete", "positive_volume", u_over_t, alpha,
                    {"volume": geometry["volume"],
                     "volume_range": geometry["volume_range"],
                     "q_chi": geometry["q_chi"], "q_range": geometry["q_range"]},
                    archives,
                ),
            ))
            unique_models.append((
                f"signed_grasp_{alpha:+g}",
                build_model(
                    "complete", "signed_grasp", u_over_t, alpha,
                    {"volume": geometry["volume"],
                     "volume_range": geometry["volume_range"],
                     "q_chi": geometry["q_chi"], "q_range": geometry["q_range"]},
                    archives,
                ),
            ))
        for case, model in unique_models:
            for phi in REFERENCE_PHI:
                seed = references[phi]
                seed_label = (
                    "regular" if phi == 90 else
                    "flat_boundary" if phi == 0 else
                    f"phi_{phi}"
                )
                trajectory_rows, schedule = exact_dynamic_series(
                    model, geometry, operators, seed, seed_label
                )
                rows.extend(trajectory_rows)
                schedules.append({**schedule, "case": case})
                print(
                    f"dynamics completed: U/t={u_over_t:g}, {case}, "
                    f"seed={seed_label}, samples={len(trajectory_rows)}, "
                    f"uniform_points={schedule['uniform_grid_points_required']}",
                    flush=True,
                )
            models.append(case)
    save_csv(OUT / "dynamics_scan.csv", rows)
    save_csv(OUT / "dynamics_schedule.csv", schedules)
    return schedules


def make_protocol(reference_meta, validation):
    return {
        "title": "T11 K=4 tetrahedral candidate-Hamiltonian comparison",
        "sector": {
            "sites": 4, "total_linear_area_K": 4, "total_spin_J": 0,
            "dimension": 105, "hbar": 1.0, "t": T,
        },
        "baseline": (
            "H0 = -t sum_edges(E_ij+E_ji) + U/2 sum_i n_i(n_i-1); "
            "the second term is the on-site repulsion U sum_i binom(n_i,2)"
        ),
        "candidates": {
            "positive_volume": {
                "Hamiltonian": "H = H0 + g_V V_RS",
                "operator": "existing positive RS volume; sum over four connected triples",
                "coupling": "alpha_V = g_V * spectral_range(V_RS) / t",
                "alphas_complete_graph": list(ALPHAS),
                "U_over_t": list(U_VALUES),
                "ring_control": {
                    "U_over_t": list(RING_U_VALUES),
                    "alphas": list(RING_ALPHAS),
                    "meaning": "sparse hopping topology control, not a tetrahedron",
                },
            },
            "signed_grasp": {
                "Hamiltonian": "H = H0 + lambda_chi Q_chi",
                "triple": "q_ijk = i[D_ij,D_jk] = J_i dot (J_j cross J_k)",
                "orientation": {
                    "".join(map(str, triple)): sign
                    for triple, sign in ORIENTATION.items()
                },
                "oriented_operator": "Q_chi = q_012 - q_013 + q_023 - q_123",
                "closure_relation": (
                    "on the four-site singlet space, Q_chi=4*q_012 and "
                    "V_RS=2*gamma^(3/2)*sqrt(abs(Q_chi)) with the existing "
                    "positive-root cutoff"
                ),
                "coupling": "alpha_chi = lambda_chi * spectral_range(Q_chi) / t",
                "alphas": list(ALPHAS),
                "U_over_t": list(U_VALUES),
                "interpretation": (
                    "orientation-sensitive, time-reversal-odd candidate; "
                    "tested as a mathematical model, not assumed physically selected"
                ),
            },
        },
        "prepared_states": {
            "family": "normalized K=4 FL, equal input face areas, x=1/sqrt(3)",
            "phi_degrees": list(REFERENCE_PHI),
            "labels": {str(k): v["label"] for k, v in reference_meta.items()},
            "projection_checks": reference_meta,
        },
        "static_outputs": {
            "full_spectrum": True,
            "low_energy_groups": "first three distinct groups; degenerate groups uniform",
            "thermal_grid": (
                "beta*t=0; 601 geomspace values from 1e-3 to 1e3; "
                "exact uniform ground-subspace mixture at beta=infinity"
            ),
            "readouts": [
                "energy, face-area means/covariances, assignment and active-face probabilities",
                "six pair-dot means, four-face-conditioned angles and full symmetrized covariance",
                "positive-volume mean/variance/kernel probability/outcome distribution",
                "signed q012 and oriented Q_chi means and rms",
                "prepared FL probabilities in the first three energy groups",
            ],
        },
        "dynamics": {
            "complete_graph_only": True,
            "U_over_t": [5.0, 20.0],
            "models": ["baseline", "positive_volume alpha=-1,+1",
                       "signed_grasp alpha=-1,+1"],
            "seeds": [
                "regular phi=90 degrees", "phi=60 degrees", "phi=30 degrees",
                "phi=10 degrees", "flat-boundary phi=0 degrees",
            ],
            "method": "exact finite-dimensional energy-basis phase evolution",
            "resolved_pair_rule": (
                "retain off-diagonal beats whose normalized observable "
                "coefficient is at least 1e-8; use numerical nonzero-gap floor "
                "1e-10 times max(1, bandwidth)"
            ),
            "sampling": (
                "20 samples per fastest resolved beat for the first 10 fastest "
                "periods, then 900 exact logarithmic-time samples through 10 "
                "periods of the slowest resolved beat"
            ),
            "uniform_grid_note": (
                "the uniform grid that also resolves the fastest beat over the "
                "entire slowest-beat horizon is counted and recorded; it is "
                "not materialized when it requires millions or more of points"
            ),
            "tracked": [
                "return probability, volume mean/variance/kernel probability",
                "face areas/covariances and active-face probability",
                "assignment-normalized angular means/covariances",
                "signed grasp means/rms, energy, total area, singlet closure",
            ],
        },
        "volume_units": "project RS units; physical calibration not specified",
        "tolerance": TOL,
        "thermal_grid_count": len(THERMAL_BETAS),
        "model_count": 62,
        "validation_summary": validation,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage", choices=("static", "dynamics", "all"), default="all"
    )
    args = parser.parse_args()
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    archives = {
        graph: np.load(INPUT_DIR / f"operators_k4_{graph}.npz")
        for graph in ("complete", "ring")
    }
    complete_archive = archives["complete"]
    geometry, references, reference_meta = initialize(complete_archive)
    validation = {
        "dimension": int(geometry["volume"].shape[0]),
        "V_hermiticity": float(np.max(np.abs(
            geometry["volume"] - geometry["volume"].conj().T
        ))),
        "Qchi_hermiticity": float(np.max(np.abs(
            geometry["q_chi"] - geometry["q_chi"].conj().T
        ))),
        "Qchi_spectral_range": geometry["q_range"],
        "V_spectral_range_project_units": geometry["volume_range"],
        "V_zero_kernel_dimension": geometry["zero_dimension"],
        "oriented_closure_q012_minus_q013": float(np.max(np.abs(
            geometry["q012"] + geometry["q_by_triple"][0, 1, 3]
        ))),
        "oriented_closure_q012_minus_q023": float(np.max(np.abs(
            geometry["q012"] - geometry["q_by_triple"][0, 2, 3]
        ))),
        "oriented_closure_q012_plus_q123": float(np.max(np.abs(
            geometry["q012"] + geometry["q_by_triple"][1, 2, 3]
        ))),
        "oriented_Qchi_equals_4q012": float(np.max(np.abs(
            geometry["q_chi"] - 4.0 * geometry["q012"]
        ))),
        "V_RS_Qchi_commutator": float(np.max(np.abs(
            geometry["volume"] @ geometry["q_chi"]
            - geometry["q_chi"] @ geometry["volume"]
        ))),
    }
    chirality_values, chirality_vectors = eigh(geometry["q_chi"])
    chirality_cutoff = ZERO_FACTOR * max(
        1.0, float(np.max(np.abs(chirality_values)))
    )
    chirality_values = np.where(
        np.abs(chirality_values) <= chirality_cutoff, 0.0, chirality_values
    )
    volume_from_chirality = (
        chirality_vectors
        * (2.0 * GAMMA**1.5 * np.sqrt(np.abs(chirality_values)))
    ) @ chirality_vectors.conj().T
    validation["V_RS_Qchi_functional_relation"] = float(np.max(np.abs(
        volume_from_chirality - geometry["volume"]
    )))
    validation["direct_spin1_q_spectrum"] , validation[
        "direct_spin1_Qchi_spectrum"
    ] = direct_spin_one_grasp_check(geometry)
    validation.update(permutation_checks(complete_archive, geometry))
    if np.max(np.abs(archives["ring"]["volume"] - archives["complete"]["volume"])) > TOL:
        raise AssertionError("four-site ring and complete V_RS operators differ")
    validation["ring_complete_volume_difference"] = float(np.max(np.abs(
        archives["ring"]["volume"] - archives["complete"]["volume"]
    )))
    if args.stage == "dynamics" and (OUT / "validation.json").exists():
        validation.update(json.loads((OUT / "validation.json").read_text()))

    if args.stage in ("static", "all"):
        static_validation = run_static(
            archives, complete_archive, geometry, references
        )
        validation.update(static_validation)
        (OUT / "validation.json").write_text(
            json.dumps(validation, indent=2) + "\n"
        )
    if args.stage in ("dynamics", "all"):
        schedules = run_dynamics(archives, geometry, references)
        validation["dynamic_schedule_count"] = len(schedules)
        validation["max_required_uniform_dynamic_points"] = max(
            row["uniform_grid_points_required"] for row in schedules
        )
        validation["max_computed_dynamic_samples"] = max(
            row["computed_exact_sample_count"] for row in schedules
        )
        (OUT / "validation.json").write_text(
            json.dumps(validation, indent=2) + "\n"
        )

    protocol = make_protocol(reference_meta, validation)
    (OUT / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
    source_paths = [
        Path(__file__),
        ROOT / "code/python/lqg_scattering/geometric_diagnostics.py",
        ROOT / "code/python/verify_t11_candidate_hamiltonians.py",
        ROOT / "code/python/plot_t11_candidate_hamiltonians.py",
        ROOT / "results/hamiltonian-studies/operators_k4_complete.npz",
        ROOT / "results/hamiltonian-studies/operators_k4_ring.npz",
        ROOT / "results/t11-geometric-interpretation/protocol.json",
    ]
    (OUT / "provenance.json").write_text(json.dumps({
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in source_paths
    }, indent=2) + "\n")
    elapsed = time.time() - started
    residual_values = [
        value for key, value in validation.items()
        if isinstance(value, (int, float))
        and ("residual" in key or "hermiticity" in key or "covariance" in key)
    ]
    max_residual = max(residual_values, default=0.0)
    print(
        f"stage={args.stage}; models={protocol['model_count']}; "
        f"dimension=105; max_residual={max_residual:.3g}; "
        f"elapsed={elapsed:.1f}s"
    )
    if validation.get("dynamic_schedule_count"):
        print(
            "dynamics schedules="
            f"{validation['dynamic_schedule_count']}; "
            "max uniform-grid points="
            f"{validation['max_required_uniform_dynamic_points']}; "
            "max exact samples="
            f"{validation['max_computed_dynamic_samples']}"
        )


if __name__ == "__main__":
    main()

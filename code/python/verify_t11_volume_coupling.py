"""Independent spectral and matrix-exponential checks for T11's V coupling."""

import csv
import json
import math
from pathlib import Path

import numpy as np
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "results/hamiltonian-studies/operators_k4_complete.npz"
OUT = ROOT / "results/t11-volume-coupling"
TOL = 2e-10


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def main():
    archive = np.load(ARCHIVE)
    volume = np.asarray(archive["volume"], dtype=complex)
    onsite = np.asarray(archive["onsite_penalty"], dtype=complex)
    edges = tuple((i, j) for i in range(4) for j in range(i + 1, 4))
    hopping = sum(
        (archive[f"hopping_{i}_{j}"] for i, j in edges), np.zeros_like(onsite)
    )
    h0 = 20.0 * onsite - hopping
    vvals, vvecs = np.linalg.eigh((volume + volume.conj().T) / 2.0)
    v_range = float(vvals[-1] - vvals[0])
    cutoff = 64.0 * np.finfo(float).eps * max(1.0, float(np.max(np.abs(vvals))))
    zero_vectors = vvecs[:, np.abs(vvals) <= cutoff]
    p_zero = zero_vectors @ zero_vectors.conj().T

    energy_rows = read_csv(OUT / "energy_levels.csv")
    thermal_rows = read_csv(OUT / "thermal_scan.csv")
    volume_rows = read_csv(OUT / "volume_distribution_selected.csv")
    saved_levels = {}
    for row in energy_rows:
        saved_levels.setdefault(float(row["alpha_V"]), []).append(float(row["energy"]))

    checks = {}
    beta_set = (0.0, 1.0, 10.0, 100.0, 1000.0, math.inf)
    for alpha in (-1.0, 0.0, 1.0):
        g_v = alpha / v_range
        hamiltonian = h0 + g_v * volume
        eigenvalues = np.linalg.eigvalsh((hamiltonian + hamiltonian.conj().T) / 2.0)
        checks[f"alpha_{alpha:g}_saved_spectrum"] = float(
            np.max(np.abs(eigenvalues - saved_levels[alpha]))
        )
        for beta in beta_set:
            if math.isinf(beta):
                values, vectors = np.linalg.eigh(hamiltonian)
                mask = np.abs(values - values[0]) <= 1e-12
                rho = vectors[:, mask] @ vectors[:, mask].conj().T / int(mask.sum())
            elif beta == 0.0:
                rho = np.eye(len(eigenvalues), dtype=complex) / len(eigenvalues)
            else:
                shifted = hamiltonian - eigenvalues[0] * np.eye(len(eigenvalues))
                boltzmann = expm(-beta * shifted)
                rho = boltzmann / np.trace(boltzmann)
            direct_v = float(np.real(np.trace(rho @ volume)))
            direct_zero = float(np.real(np.trace(rho @ p_zero)))
            row = next(
                item for item in thermal_rows
                if float(item["alpha_V"]) == alpha
                and item["beta_t"] == ("inf" if math.isinf(beta) else str(beta))
            )
            checks[f"alpha_{alpha:g}_beta_{beta:g}_volume"] = abs(
                direct_v - float(row["mean_volume_project_units"])
            )
            checks[f"alpha_{alpha:g}_beta_{beta:g}_zero_probability"] = abs(
                direct_zero - float(row["probability_zero_volume"])
            )

    distribution_sums = {}
    for row in volume_rows:
        key = (row["alpha_V"], row["beta_t"])
        distribution_sums[key] = distribution_sums.get(key, 0.0) + float(row["probability"])
    for key, total in distribution_sums.items():
        checks[f"volume_distribution_sum_{key[0]}_{key[1]}"] = abs(total - 1.0)

    baseline = read_csv(ROOT / "results/hamiltonian-studies/spectra.csv")
    baseline_row = next(
        row for row in baseline
        if row["K"] == "4" and row["graph"] == "complete" and row["U_over_t"] == "20.0"
    )
    alpha_zero_e0 = saved_levels[0.0][0]
    checks["baseline_ground_energy"] = abs(
        alpha_zero_e0 - float(baseline_row["ground_energy"])
    )
    zero_summary = next(row for row in read_csv(OUT / "summary.csv")
                        if float(row["alpha_V"]) == 0.0)
    checks["baseline_ground_volume"] = abs(
        float(zero_summary["ground_mean_volume_project_units"])
        - float(baseline_row["ground_mean_volume"])
    )
    checks["baseline_ground_zero_probability"] = abs(
        float(zero_summary["ground_probability_zero_volume"])
        - float(baseline_row["ground_probability_zero_volume"])
    )

    previous_thermal = read_csv(
        ROOT / "results/hamiltonian-studies/k4_thermal_volume_scan.csv"
    )
    for beta in beta_set:
        beta_string = "inf" if math.isinf(beta) else str(beta)
        previous = next(
            row for row in previous_thermal
            if row["K"] == "4" and row["graph"] == "complete"
            and row["U_over_t"] and float(row["U_over_t"]) == 20.0
            and row["beta"] == beta_string
        )
        current = next(
            row for row in thermal_rows
            if float(row["alpha_V"]) == 0.0 and row["beta_t"] == beta_string
        )
        for field, old_name in (
            ("mean_volume_project_units", "mean_volume"),
            ("probability_zero_volume", "probability_zero_volume"),
            ("mean_active_faces", "mean_active_sites"),
        ):
            checks[f"saved_baseline_beta_{beta:g}_{field}"] = abs(
                float(current[field]) - float(previous[old_name])
            )

    max_residual = max(checks.values())
    report = {
        "method": "independent NumPy eigvalsh and SciPy matrix-exponential Gibbs traces",
        "checks": checks,
        "max_residual": max_residual,
        "tolerance": TOL,
        "passed": max_residual < TOL,
    }
    (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    if max_residual >= TOL:
        raise AssertionError(f"maximum verification residual {max_residual} >= {TOL}")
    print(f"Independent checks passed: {len(checks)} checks; max residual={max_residual:.3g}")


if __name__ == "__main__":
    main()

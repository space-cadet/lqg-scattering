"""Complete fixed-K, variable-N singlet catalogue and positive RS spectra.

K=sum(j_i), J_total=0; faces are labelled and all j_i>0.
Finite blocks are diagonalized numerically, with explicit tolerances.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

import numpy as np
import scipy
import sympy

from lqg_scattering.singlets import (
    ABS_TOL, GAMMA, ZERO_FACTOR, action_matrix, cg, independent_local_q,
    load_block, occupation_basis, pack_blocks, root_abs, save_csr,
)
from project_paths import PROJECT_ROOT as ROOT

from lqg_scattering.labels import (
    compositions, fixed_face_dimension as fixed_n_dimension,
    positive_face_dimension as active_dimension,
)
from lqg_scattering.singlets import (
    singlet_paths, magnetic_singlet_count, sequential_basis, closure_residual,
)
from lqg_scattering.volume_blocks import max_abs, dense_tensor_q, canonical_operators


def positive_compositions(total, length):
    """Compatibility entry point for strictly positive compositions."""
    return compositions(total, length, minimum=1)


def grouped_spectrum(values):
    groups = []
    for value in sorted(float(v) for v in values):
        value = 0.0 if abs(value) <= ABS_TOL else value
        if groups and abs(value-groups[-1]["anchor"]) <= ABS_TOL:
            groups[-1]["values"].append(value)
        else:
            groups.append({"anchor": value, "values": [value]})
    return [{"rs_volume": float(np.mean(g["values"])), "multiplicity": len(g["values"]),
             "within_group_spread": max(g["values"])-min(g["values"])}
            for g in groups]


def calculate_kn(area, n, out):
    started = time.perf_counter()
    arrays, blocks, states, eigenstates = {}, [], [], []
    checks = {name: 0.0 for name in (
        "orthogonality", "closure", "casimir", "prefix_casimir", "hermiticity",
        "invariant_subspace", "epsilon_vs_commutator", "dense_tensor_vs_commutator",
        "magnetic_root_projection", "independent_volume", "eigensystem",
        "trace_moments", "permutation_spectrum", "four_face_previous",
        "analytic_half_spin", "saturated_spin_zero")}
    for spins in positive_compositions(2*area, n):
        paths = singlet_paths(spins)
        independent_dimension = magnetic_singlet_count(spins)
        assert len(paths) == independent_dimension
        if not paths:
            continue
        canonical_spins = tuple(sorted(spins))
        canonical_occ, canonical_dots, direct_v, canonical_b, independent_checks = canonical_operators(canonical_spins)
        occupations, basis, inverse = sequential_basis(spins, paths, canonical_occ)
        d = len(paths)
        label = f"b{len(blocks):04d}"
        dots = {p: canonical_dots[tuple(sorted((inverse[p[0]], inverse[p[1]])))]
                for p in itertools.combinations(range(n), 2)}
        small_dots = {p: basis.conj().T@(matrix@basis) for p, matrix in dots.items()}
        residuals = {"orthogonality": max_abs(basis.conj().T@basis-np.eye(d)),
                     "closure": closure_residual(occupations, basis)}
        casimir = sum(.25*s*(s+2) for s in spins)*np.eye(d)+2*sum(small_dots.values())
        residuals["casimir"] = max_abs(casimir)
        for prefix in range(2, n+1):
            operator = sum(.25*s*(s+2) for s in spins[:prefix])*np.eye(d, dtype=complex)
            operator += 2*sum(matrix for (i, j), matrix in small_dots.items() if j < prefix)
            expected = np.diag([.25*path[prefix-1]*(path[prefix-1]+2) for path in paths])
            residuals["prefix_casimir"] = max(residuals.get("prefix_casimir", 0.0), max_abs(operator-expected))
        volume, q_squares = np.zeros((d, d), complex), np.zeros((d, d), complex)
        for i, j, k in itertools.combinations(range(n), 3):
            q = 1j*(small_dots[i, j]@small_dots[j, k]-small_dots[j, k]@small_dots[i, j])
            full = 1j*(dots[i, j]@dots[j, k]-dots[j, k]@dots[i, j])
            residuals["hermiticity"] = max(residuals.get("hermiticity", 0.0), max_abs(q-q.conj().T))
            residuals["invariant_subspace"] = max(residuals.get("invariant_subspace", 0.0),
                                                 max_abs(full@basis-basis@q))
            arrays[label+f"_q{i}_{j}_{k}"] = q
            volume += GAMMA**1.5*root_abs(q)[0]
            q_squares += q@q
        overlap = canonical_b.conj().T@basis
        residuals["independent_volume"] = max_abs(volume-overlap.conj().T@direct_v@overlap)
        eigenvalues, eigenvectors = np.linalg.eigh((volume+volume.conj().T)/2)
        assert min(eigenvalues) > -ABS_TOL
        residuals["eigensystem"] = max_abs(volume@eigenvectors-eigenvectors*eigenvalues)
        residuals["permutation_spectrum"] = max_abs(eigenvalues-np.linalg.eigvalsh(direct_v))
        gram_values = np.linalg.eigvalsh((q_squares+q_squares.conj().T)/2)
        gram_cutoff = ZERO_FACTOR*max(1.0, max_abs(gram_values))
        kernel_count = int(np.count_nonzero(abs(gram_values) <= gram_cutoff))
        zero_count = int(np.count_nonzero(abs(eigenvalues) <= ABS_TOL))
        assert zero_count == kernel_count, (spins, eigenvalues, gram_values)
        if all(spin == 1 for spin in spins):
            analytic = GAMMA**1.5*math.sqrt(math.sqrt(3)/4)*n*(n*n-4)/12
            residuals["analytic_half_spin"] = max_abs(volume-analytic*np.eye(d))
        if max(spins) == sum(spins)-max(spins):
            assert d == 1
            residuals["saturated_spin_zero"] = max_abs(volume)
        eigenvalues = np.where(abs(eigenvalues) <= ABS_TOL, 0, eigenvalues)
        second = volume@volume
        means, seconds = np.diag(volume).real, np.diag(second).real
        variances = seconds-means**2
        assert min(variances) > -ABS_TOL
        variances = np.where(abs(variances) <= ZERO_FACTOR*max(1.0, max_abs(seconds)), 0, variances)
        residuals["trace_moments"] = max(abs(sum(means)-sum(eigenvalues)),
                                        abs(sum(seconds)-sum(eigenvalues**2)))
        for name, value in {**residuals, **independent_checks}.items():
            checks[name] = max(checks[name], float(value))
        for pair, matrix in small_dots.items():
            arrays[label+f"_dot{pair[0]}_{pair[1]}"] = matrix
        for name, matrix in {"v_rs": volume, "v2_rs": second, "eigenvalues": eigenvalues,
                             "eigenvectors": eigenvectors, "twice_spins": np.asarray(spins),
                             "twice_paths": np.asarray(paths), "occupations_m0": np.asarray(occupations)}.items():
            arrays[label+"_"+name] = matrix
        save_csr(arrays, label+"_basis", basis)
        for col, path in enumerate(paths):
            states.append({"K": area, "N": n, "state_index_at_KN": len(states)+1, "block": label,
                           "twice_spins": json.dumps(spins), "twice_cumulative_spins": json.dumps(path),
                           "J_total": 0, "rs_mean": float(means[col]), "rs_second_moment": float(seconds[col]),
                           "rs_sd": float(math.sqrt(max(0, variances[col])))})
        for col, value in enumerate(eigenvalues):
            eigenstates.append({"K": area, "N": n, "block": label, "eigenvector_column": col,
                                "twice_spins": json.dumps(spins), "rs_eigenvalue": float(value),
                                "zero_volume": bool(value == 0)})
        blocks.append({"id": label, "twice_spins": spins, "twice_cumulative_spins": paths,
                       "singlet_dimension": d, "magnetic_m0_dimension": len(occupations),
                       "rs_eigenvalues": eigenvalues.tolist(), "zero_volume_dimension": zero_count,
                       "common_triple_kernel_dimension": kernel_count})
    assert len(states) == active_dimension(n, area)
    assert len({(s["twice_spins"], s["twice_cumulative_spins"]) for s in states}) == len(states)
    if n == 4:
        previous = ROOT/"results"/"closed-basis-volume"/f"metadata_k{area}.json"
        old = json.loads(previous.read_text())
        old_spectra = {tuple(b["twice_spins"]): b["volume_eigenvalues"]["rs"] for b in old["blocks"]
                       if b["all_faces_active"]}
        checks["four_face_previous"] = max(
            max_abs(np.asarray(b["rs_eigenvalues"])-old_spectra[tuple(b["twice_spins"])]) for b in blocks)
    assert max(checks.values()) < ABS_TOL, checks
    packed = pack_blocks(arrays, [b["id"] for b in blocks])
    archive = out/f"operators_k{area}_n{n}.npz"
    np.savez_compressed(archive, **packed)
    with np.load(archive, allow_pickle=False) as saved:
        assert set(saved.files) == set(packed)
        assert all(np.array_equal(saved[key], value) for key, value in packed.items())
        for index, block in enumerate(blocks):
            for name in ("v_rs", "eigenvalues", "eigenvectors", "twice_paths", "basis_data"):
                assert np.array_equal(load_block(saved, index, name), arrays[block["id"]+"_"+name])
    for kind, rows in (("basis", states), ("eigenstates", eigenstates)):
        with (out/f"{kind}_k{area}_n{n}.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    values = [s["rs_eigenvalue"] for s in eigenstates]
    report = {"K": area, "N": n, "basis_dimension": len(states), "spin_assignments": len(blocks),
              "independent_dimension": active_dimension(n, area), "blocks": blocks,
              "zero_volume_dimension": sum(b["zero_volume_dimension"] for b in blocks),
              "positive_volume_dimension": sum(v > ABS_TOL for v in values),
              "spectrum": grouped_spectrum(values), "equal_weight_mean": float(np.mean(values)),
              "equal_weight_sd": float(np.std(values)), "minimum_positive_volume": min(v for v in values if v > ABS_TOL),
              "maximum_volume": max(values), "checks_max_absolute_residual": checks,
              "maximum_singlet_dimension": max(b["singlet_dimension"] for b in blocks),
              "maximum_magnetic_m0_dimension": max(b["magnetic_m0_dimension"] for b in blocks),
              "archive": archive.name, "archive_bytes": archive.stat().st_size,
              "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
              "basis_csv": f"basis_k{area}_n{n}.csv", "eigenstates_csv": f"eigenstates_k{area}_n{n}.csv",
              "elapsed_seconds": time.perf_counter()-started}
    (out/f"metadata_k{area}_n{n}.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(f"K={area}, N={n}: {len(states)} states, {report['zero_volume_dimension']} zero, "
          f"{report['positive_volume_dimension']} positive; {report['elapsed_seconds']:.2f}s", flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k-min", type=int, default=2)
    parser.add_argument("--k-max", type=int, default=4)
    parser.add_argument("--output-dir", type=Path, default=ROOT/"results"/"variable-n-volume")
    args = parser.parse_args()
    if not 2 <= args.k_min <= args.k_max <= 4:
        parser.error("validated scope requires 2 <= k-min <= k-max <= 4")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    reports = [calculate_kn(area, n, args.output_dir)
               for area in range(args.k_min, args.k_max+1) for n in range(4, 2*area+1)]
    areas = []
    spectrum_rows = []
    for area in range(args.k_min, args.k_max+1):
        selected = [r for r in reports if r["K"] == area]
        values = [v for r in selected for b in r["blocks"] for v in b["rs_eigenvalues"]]
        spectrum = grouped_spectrum(values)
        areas.append({"K": area, "basis_dimension": len(values),
                      "zero_volume_dimension": sum(v == 0 for v in values),
                      "positive_volume_dimension": sum(v > ABS_TOL for v in values),
                      "spectrum": spectrum, "equal_weight_mean": float(np.mean(values)),
                      "equal_weight_sd": float(np.std(values))})
        spectrum_rows.extend({"K": area, "N": "all", **group} for group in spectrum)
        spectrum_rows.extend({"K": area, "N": r["N"], **group} for r in selected for group in r["spectrum"])
    assert [a["basis_dimension"] for a in areas] == [dict([(2, 2), (3, 36), (4, 347)])[a["K"]] for a in areas]
    with (args.output_dir/"spectra.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(spectrum_rows[0]))
        writer.writeheader()
        writer.writerows(spectrum_rows)
    summary = {"schema_version": 1, "date": "2026-10-08", "task": "T10",
               "notation": "K=sum_i j_i=N_bosons/2; resultant J=0",
               "support": "labelled positive-spin faces, 4 <= N <= 2K; one copy, zero temperature",
               "basis": "sequential Condon-Shortley CG coupling: s_1=j_1, s_N=0; intermediate labels ascending",
               "operator": "V_RS=(gamma*hbar)^(3/2) sum_{i<j<k} sqrt(abs(q_ijk)); q_ijk=i[Ji.Jj,Jj.Jk]",
               "units": {"gamma": GAMMA, "hbar": 1, "physical_regularization": "unresolved",
                         "higher_valence_geometric_conversion": "not applied"},
               "absolute_tolerance": ABS_TOL, "spectral_grouping_absolute_tolerance": ABS_TOL,
               "triple_zero_eigenvalue_cutoff": "64*eps*max(1,max(abs(eigenvalues)))",
               "numerical_method": "complete finite-block floating-point diagonalization; no sampling or state truncation",
               "count_checks": "coupling paths, independent M=0 minus M=1 multiplicities, U(N) inclusion-exclusion",
               "areas": areas, "by_KN": [{k: v for k, v in r.items() if k != "blocks"} for r in reports],
               "numpy": np.__version__, "scipy": scipy.__version__, "sympy": sympy.__version__,
               "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output_dir/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()

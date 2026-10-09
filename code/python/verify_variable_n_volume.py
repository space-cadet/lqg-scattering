"""Verify saved variable-N archives and an exact analytic spin-half control."""
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import sympy as sp

from lqg_scattering.singlets import load_block
from project_paths import PROJECT_ROOT as ROOT


def exact_spin_half_triple():
    identity = sp.eye(2)
    axes = (sp.Matrix([[0, 1], [1, 0]])/2,
            sp.Matrix([[0, -sp.I], [sp.I, 0]])/2,
            sp.diag(1, -1)/2)
    embedded = {}
    for face in range(3):
        for axis in range(3):
            factors = [identity]*3
            factors[face] = axes[axis]
            embedded[face, axis] = sp.kronecker_product(*factors)
    permutations = ((0, 1, 2, 1), (1, 2, 0, 1), (2, 0, 1, 1),
                    (0, 2, 1, -1), (2, 1, 0, -1), (1, 0, 2, -1))
    q = sp.zeros(8)
    for a, b, c, sign in permutations:
        q += sign*embedded[0, a]*embedded[1, b]*embedded[2, c]
    spin_squared = sp.zeros(8)
    for axis in range(3):
        total = sum((embedded[face, axis] for face in range(3)), sp.zeros(8))
        spin_squared += total*total
    projector = (sp.Rational(15, 4)*sp.eye(8)-spin_squared)/3
    assert q*q == sp.Rational(3, 16)*projector
    assert projector*projector == projector
    assert q.eigenvals() == {sp.sqrt(3)/4: 2, -sp.sqrt(3)/4: 2, 0: 4}
    return {"arithmetic": "exact SymPy rationals and radicals",
            "triple_eigenvalues": {"0": 4, "+sqrt(3)/4": 2, "-sqrt(3)/4": 2},
            "identity": "q^2=(3/16)P_{J_triple=1/2}",
            "closed_all_half_volume": "(gamma*hbar)^(3/2)*sqrt(sqrt(3)/4)*N*(N^2-4)/12",
            "proof": "P=1/2-(2/3)sum_triple_pairs Ji.Jj; each pair occurs N-2 times; singlet sum_pairs Ji.Jj=-3N/8."}


def main():
    data = ROOT/"results"/"variable-n-volume"
    summary = json.loads((data/"summary.json").read_text())
    tol = summary["absolute_tolerance"]
    epsilon = 64*np.finfo(float).eps
    max_residual = 0.0
    block_count, state_count = 0, 0
    for record in summary["by_KN"]:
        metadata = json.loads((data/f"metadata_k{record['K']}_n{record['N']}.json").read_text())
        archive_path = data/record["archive"]
        assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == record["archive_sha256"]
        all_values = []
        with np.load(archive_path, allow_pickle=False) as archive:
            arrays = {key: archive[key] for key in archive.files}
        for index, block in enumerate(metadata["blocks"]):
            d = block["singlet_dimension"]
            volume = load_block(arrays, index, "v_rs")
            values = load_block(arrays, index, "eigenvalues")
            vectors = load_block(arrays, index, "eigenvectors")
            rebuilt = np.zeros((d, d), complex)
            for i, j, k in itertools.combinations(range(record["N"]), 3):
                q = load_block(arrays, index, f"q{i}_{j}_{k}")
                w, u = np.linalg.eigh(q)
                w[abs(w) <= epsilon*max(1, max(abs(w)))] = 0
                rebuilt += summary["units"]["gamma"]**1.5 * sum(
                    (np.sqrt(abs(value))*np.outer(u[:, col], u[:, col].conj())
                     for col, value in enumerate(w)), np.zeros((d, d), complex))
            residual = max(float(np.max(abs(rebuilt-volume))),
                           float(np.max(abs(vectors.conj().T@vectors-np.eye(d)))),
                           float(np.max(abs(volume-vectors@np.diag(values)@vectors.conj().T))))
            assert residual < tol
            assert np.allclose(values, block["rs_eigenvalues"], rtol=0, atol=tol)
            max_residual = max(max_residual, residual)
            all_values.extend(values)
            block_count += 1
            state_count += d
        assert len(all_values) == record["basis_dimension"]
        assert sum(value == 0 for value in all_values) == record["zero_volume_dimension"]
        assert abs(np.mean(all_values)-record["equal_weight_mean"]) < tol
    source_hashes = []
    for name in ("variable_n_volume.py", "closed_basis_volume.py", "coherent_states.py", "positivity.py",
                 "fl_volume_validation.py", "verify_variable_n_volume.py"):
        path = ROOT/"code"/"python"/name
        source_hashes.append({"path": str(path.relative_to(ROOT)),
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    report = {"exact_analytic_check": exact_spin_half_triple(),
              "saved_archive_blocks_checked": block_count, "eigenstates_checked": state_count,
              "maximum_reconstruction_residual": max_residual, "absolute_tolerance": tol,
              "sources": source_hashes,
              "summary_sha256": hashlib.sha256((data/"summary.json").read_bytes()).hexdigest()}
    (data/"verification.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(f"OK: {block_count} saved blocks, {state_count} eigenstates; max residual {max_residual:.3g}; exact spin-half identity verified.")


if __name__ == "__main__":
    main()

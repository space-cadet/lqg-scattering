"""Positive volumes in a complete four-face singlet recoupling basis.

K is total linear area; resultant spin J is zero. Store complete small
singlet blocks in compressed NPZ, with JSON basis metadata and CSV moments.
Canonical magnetic-space scalar products are shared among permutations.
"""
import argparse
import csv
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

import numpy as np
import scipy
from scipy.sparse import csr_matrix
import sympy
from sympy import Rational
from sympy.physics.wigner import clebsch_gordan

from coherent_states import su2_ops
from fl_volume_labels import enumerate_total_area
from fl_volume_validation import direct_tensor_q
from positivity import _dot_ops, _triple_matrix_block

ROOT = Path(__file__).resolve().parents[2]
PAIRS = tuple(itertools.combinations(range(4), 2))
TRIPLES = tuple(itertools.combinations(range(4), 3))
SIGNS = (1, -1, 1, -1)
GAMMA = 0.2375
ABS_TOL = 2e-10
ZERO_FACTOR = 64 * np.finfo(float).eps


@lru_cache(maxsize=None)
def cg(a, b, c, ma, mb, mc):
    """Condon–Shortley CG coefficients with twice-integer arguments."""
    if ma + mb != mc or abs(mc) > c:
        return 0.0
    return float(clebsch_gordan(*[Rational(x, 2) for x in (a, b, c, ma, mb, mc)]))


def occupation_basis(spins):
    return [tuple(v for a, s in zip(aa, spins) for v in (a, s-a))
            for aa in itertools.product(*[range(s+1) for s in spins])
            if sum(2*a-s for a, s in zip(aa, spins)) == 0]


def action_matrix(basis, action):
    index = {o: i for i, o in enumerate(basis)}
    rows, cols, values = [], [], []
    for col, occ in enumerate(basis):
        for target, amplitude in action(occ):
            if abs(amplitude) == 0:
                continue
            if target not in index:
                raise AssertionError("scalar operator left complete magnetic space")
            rows.append(index[target]); cols.append(col); values.append(amplitude)
    return csr_matrix((values, (rows, cols)), shape=(len(basis), len(basis)), dtype=complex)


def independent_local_q(basis, spins, triple=(0, 1, 2)):
    """Direct epsilon contraction of local spin matrices, without dot commutators."""
    index = {o: i for i, o in enumerate(basis)}
    rows, cols, values = [], [], []
    permutations = [(0, 1, 2, 1), (1, 2, 0, 1), (2, 0, 1, 1),
                    (0, 2, 1, -1), (2, 1, 0, -1), (1, 0, 2, -1)]
    for col, occ in enumerate(basis):
        total = {}
        for aa, bb, cc, sign in permutations:
            partial = {occ: complex(sign)}
            for edge, axis in zip(triple, (aa, bb, cc)):
                updated = {}
                for state, amplitude in partial.items():
                    a, b = state[2*edge:2*edge+2]
                    if axis == 2:
                        updated[state] = updated.get(state, 0j) + amplitude*(a-spins[edge]/2)
                    else:
                        for step, factor in [(1, math.sqrt((a+1)*b)), (-1, math.sqrt(a*(b+1)))]:
                            if not factor:
                                continue
                            target = list(state)
                            target[2*edge] += step; target[2*edge+1] -= step
                            target = tuple(target)
                            coefficient = .5 if axis == 0 else -.5j*step
                            updated[target] = updated.get(target, 0j) + amplitude*coefficient*factor
                partial = updated
            for target, amplitude in partial.items():
                total[target] = total.get(target, 0j) + amplitude
        for target, amplitude in total.items():
            if target not in index:
                assert abs(amplitude) < ABS_TOL
            elif amplitude:
                rows.append(index[target]); cols.append(col); values.append(amplitude)
    return csr_matrix((values, (rows, cols)), shape=(len(basis), len(basis)))


@lru_cache(maxsize=None)
def canonical_data(spins):
    """One complete M=0 magnetic basis and scalar-product matrices per pattern."""
    basis = occupation_basis(spins)
    dots = {p: action_matrix(basis, _dot_ops(su2_ops(p[0]), su2_ops(p[1]))) for p in PAIRS}
    checks = {}
    q012 = 1j*(dots[0, 1]@dots[1, 2]-dots[1, 2]@dots[0, 1])
    difference = q012-independent_local_q(basis, spins)
    checks["q012_sparse_local_spin"] = float(np.max(abs(difference.data))) if difference.nnz else 0.0
    assert checks["q012_sparse_local_spin"] < ABS_TOL
    if sum(spins) <= 8:
        for triple in TRIPLES:
            a, b, c = triple
            q = (1j * (dots[a, b] @ dots[b, c] - dots[b, c] @ dots[a, b])).toarray()
            oscillator = _triple_matrix_block(None, basis, triple)
            tensor = direct_tensor_q(basis, triple)
            checks[f"q{a}{b}{c}_oscillator"] = float(np.max(abs(q-oscillator)))
            checks[f"q{a}{b}{c}_tensor"] = float(np.max(abs(q-tensor)))
        assert max(checks.values(), default=0) < ABS_TOL
    return basis, dots, checks


def coupling_basis(spins, twice_ks, canonical_basis):
    order = sorted(range(4), key=lambda i: (spins[i], i))
    inverse = [order.index(i) for i in range(4)]
    ordered = [tuple(v for i in inverse for v in o[2*i:2*i+2]) for o in canonical_basis]
    result = np.zeros((len(ordered), len(twice_ks)), dtype=complex)
    for row, occ in enumerate(ordered):
        m = [occ[2*i]-occ[2*i+1] for i in range(4)]
        pair_m = m[0]+m[1]
        for col, twice_k in enumerate(twice_ks):
            result[row, col] = (
                cg(spins[0], spins[1], twice_k, m[0], m[1], pair_m)
                * cg(spins[2], spins[3], twice_k, m[2], m[3], -pair_m)
                * (-1)**((twice_k-pair_m)//2) / math.sqrt(twice_k+1))
    return ordered, result, inverse


def root_abs(matrix):
    assert np.max(abs(matrix-matrix.conj().T)) < ABS_TOL
    values, vectors = np.linalg.eigh((matrix+matrix.conj().T)/2)
    cutoff = ZERO_FACTOR * max(1.0, float(np.max(abs(values))))
    values = np.where(abs(values) <= cutoff, 0, values)
    return (vectors * np.sqrt(abs(values))) @ vectors.conj().T, values


def closure_residual(occupations, b):
    """Apply total raising and lowering without using the CG coupling labels."""
    worst = 0.0
    for raising in [True, False]:
        targets = {}
        for row, occ in enumerate(occupations):
            for i in range(4):
                a, bb = occ[2*i:2*i+2]
                amplitude = math.sqrt((a+1)*bb if raising else a*(bb+1))
                if not amplitude:
                    continue
                target = list(occ)
                target[2*i] += 1 if raising else -1
                target[2*i+1] += -1 if raising else 1
                key = tuple(target)
                targets[key] = targets.get(key, np.zeros(b.shape[1], complex)) + amplitude*b[row]
        if targets:
            worst = max(worst, float(np.max(abs(np.asarray(list(targets.values()))))))
    return worst


def save_csr(arrays, name, matrix):
    sparse = csr_matrix(matrix)
    arrays[name+"_data"] = sparse.data
    arrays[name+"_indices"] = sparse.indices
    arrays[name+"_indptr"] = sparse.indptr
    arrays[name+"_shape"] = np.array(sparse.shape)


def pack_blocks(arrays, labels):
    """Ragged arrays: avoid a separate ZIP member for each tiny block."""
    packed = {}
    suffixes = [key[len(labels[0])+1:] for key in arrays if key.startswith(labels[0]+"_")]
    for suffix in suffixes:
        chunks = [arrays[label+"_"+suffix] for label in labels]
        offsets = np.cumsum([0]+[chunk.size for chunk in chunks], dtype=np.int64)
        packed[suffix] = np.concatenate([chunk.reshape(-1) for chunk in chunks])
        packed[suffix+"_offsets"] = offsets
        packed[suffix+"_shapes"] = np.asarray([chunk.shape for chunk in chunks], dtype=np.int64)
    return packed


def load_block(archive, block_index, operator):
    """Recover one stored array; np.load must use allow_pickle=False."""
    offsets = archive[operator+"_offsets"]
    shape = archive[operator+"_shapes"][block_index]
    return archive[operator][offsets[block_index]:offsets[block_index+1]].reshape(shape)


def calculate_area(area, out):
    start = time.perf_counter()
    assignment_records = enumerate_total_area(area)["sectors"]
    arrays, blocks, states = {}, [], []
    maxima = {k: 0.0 for k in ["orthogonality", "closure", "recoupling", "hermiticity",
                               "invariant_subspace", "casimir", "four_valent_closure",
                               "volume_root_projection", "independent_q"]}
    for number, assignment in enumerate(assignment_records):
        spins = tuple(assignment["twiceSpins"])
        twice_ks = assignment["intermediateTwiceK"]
        canonical_spins = tuple(sorted(spins))
        canonical_basis, canonical_dots, checks = canonical_data(canonical_spins)
        occupations, b, inverse = coupling_basis(spins, twice_ks, canonical_basis)
        label = f"b{number:04d}"
        dots = {p: canonical_dots[tuple(sorted((inverse[p[0]], inverse[p[1]])))] for p in PAIRS}
        small_dots = {p: b.conj().T @ (matrix @ b) for p, matrix in dots.items()}
        maxima["orthogonality"] = max(maxima["orthogonality"], float(np.max(abs(b.conj().T@b-np.eye(len(twice_ks))))))
        maxima["closure"] = max(maxima["closure"], closure_residual(occupations, b))
        expected_dot = np.diag([(.25*k*(k+2)-.25*spins[0]*(spins[0]+2)-.25*spins[1]*(spins[1]+2))/2 for k in twice_ks])
        maxima["recoupling"] = max(maxima["recoupling"], float(np.max(abs(small_dots[0, 1]-expected_dot))))
        casimir = sum(.25*s*(s+2) for s in spins)*np.eye(len(twice_ks)) + 2*sum(small_dots.values())
        maxima["casimir"] = max(maxima["casimir"], float(np.max(abs(casimir))))
        qsmall, qfull = [], []
        for i, j, k in TRIPLES:
            full = 1j*(dots[i, j]@dots[j, k]-dots[j, k]@dots[i, j])
            small = 1j*(small_dots[i, j]@small_dots[j, k]-small_dots[j, k]@small_dots[i, j])
            projection = b.conj().T@(full@b)
            maxima["invariant_subspace"] = max(maxima["invariant_subspace"], float(np.max(abs(full@b-b@small))))
            maxima["hermiticity"] = max(maxima["hermiticity"], float(np.max(abs(small-small.conj().T))))
            assert np.max(abs(projection-small)) < ABS_TOL
            arrays[label+f"_q{i}{j}{k}"] = small
            qsmall.append(small); qfull.append(full)
        for sign, q in zip(SIGNS, qsmall):
            maxima["four_valent_closure"] = max(maxima["four_valent_closure"], float(np.max(abs(q-sign*qsmall[0]))))
        maxima["independent_q"] = max(maxima["independent_q"], max(checks.values(), default=0))
        rs = GAMMA**1.5 * sum(root_abs(q)[0] for q in qsmall)
        al = GAMMA**1.5 * root_abs(sum(s*q for s, q in zip(SIGNS, qsmall)))[0]
        # Independent magnetic-space spectral roots at every low-area block.
        if area <= 4:
            full_rs = GAMMA**1.5 * sum(root_abs(q.toarray())[0] for q in qfull)
            full_al = GAMMA**1.5 * root_abs(sum(s*q for s, q in zip(SIGNS, qfull)).toarray())[0]
            maxima["volume_root_projection"] = max(maxima["volume_root_projection"],
                float(np.max(abs(rs-b.conj().T@full_rs@b))), float(np.max(abs(al-b.conj().T@full_al@b))))
        for p, matrix in small_dots.items():
            arrays[label+f"_dot{p[0]}{p[1]}"] = matrix
        arrays[label+"_occupations_m0"] = np.asarray(occupations, dtype=np.int16)
        save_csr(arrays, label+"_basis", b)
        arrays[label+"_twice_k"] = np.asarray(twice_ks, dtype=np.int16)
        moments = {}
        spectrum = {}
        for kind, volume in [("rs", rs), ("al", al)]:
            squared = volume@volume
            eigenvalues, eigenvectors = np.linalg.eigh(volume)
            assert min(eigenvalues) > -ABS_TOL
            arrays[label+f"_v_{kind}"] = volume
            arrays[label+f"_v2_{kind}"] = squared
            arrays[label+f"_v_{kind}_eigenvalues"] = eigenvalues
            arrays[label+f"_v_{kind}_eigenvectors"] = eigenvectors
            means = np.real(np.diag(volume))
            seconds = np.real(np.diag(squared))
            variances = seconds-means**2
            assert min(variances) > -ABS_TOL
            variances = np.where(abs(variances) <= 64*np.finfo(float).eps*max(1.0, float(np.max(seconds))), 0, variances)
            moments[kind] = (means, seconds, np.sqrt(np.maximum(variances, 0)))
            spectrum[kind] = [float(x) for x in eigenvalues]
        for col, twice_k in enumerate(twice_ks):
            row = {"K": area, "state_index_at_K": len(states)+1, "block": label,
                   **dict(zip(["j1", "j2", "j3", "j4"], assignment["spins"])),
                   "k_pair": twice_k/2, "J_total": 0,
                   "all_four_faces_active": assignment["allFacesNonzero"],
                   "q012_mean": float(qsmall[0][col,col].real)}
            for kind, (means, seconds, sd) in moments.items():
                row.update({f"{kind}_mean": float(means[col]), f"{kind}_second_moment": float(seconds[col]),
                            f"{kind}_sd": float(sd[col])})
            states.append(row)
        blocks.append({"id": label, "twice_spins": list(spins), "twice_k": twice_ks,
                       "singlet_dimension": len(twice_ks), "magnetic_m0_dimension": len(occupations),
                       "all_faces_active": assignment["allFacesNonzero"], "volume_eigenvalues": spectrum})
    assert all(v < ABS_TOL for v in maxima.values()), maxima
    expected = (area+1)*(area+2)**2*(area+3)//12
    assert len(states) == expected
    # Analytic four-spin-1/2 positive-volume control and degenerate-face controls.
    if area == 2:
        expected_rs = 4*GAMMA**1.5*math.sqrt(math.sqrt(3)/4)
        assert sum(s["rs_mean"] > ABS_TOL for s in states) == 2
        assert all(abs(s["rs_mean"]-expected_rs) < ABS_TOL for s in states if s["all_four_faces_active"])
    assert all(abs(s["rs_mean"]) < ABS_TOL for s in states if not s["all_four_faces_active"])
    archive = out/f"operators_k{area}.npz"
    packed = pack_blocks(arrays, [block["id"] for block in blocks])
    np.savez_compressed(archive, **packed)
    with np.load(archive, allow_pickle=False) as stored:
        assert set(stored.files) == set(packed)
        assert all(np.array_equal(stored[key], array) for key, array in packed.items())
        for index, block in enumerate(blocks):
            for operator in ["v_rs", "v_al", "q012", "basis_data", "occupations_m0"]:
                assert np.array_equal(load_block(stored, index, operator), arrays[block["id"]+"_"+operator])
    filename = f"states_k{area}.csv"
    with (out/filename).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(states[0])); writer.writeheader(); writer.writerows(states)
    report = {"K": area, "basis_states": len(states), "blocks": blocks,
              "nonzero_volume_basis_states": sum(s["rs_mean"] > ABS_TOL for s in states),
              "maximum_singlet_dimension": max(b["singlet_dimension"] for b in blocks),
              "maximum_magnetic_m0_dimension": max(b["magnetic_m0_dimension"] for b in blocks),
              "equal_weight_closed_rs_mean": sum(s["rs_mean"] for s in states)/len(states),
              "equal_weight_closed_al_mean": sum(s["al_mean"] for s in states)/len(states),
              "checks_max_absolute_residual": maxima,
              "validation": "All-block singlet and scalar checks; independent sparse local-spin q012 per unordered pattern at every K; additional oscillator/dense-tensor and magnetic-space spectral-root checks through K=4.",
              "archive": archive.name, "archive_bytes": archive.stat().st_size,
              "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
              "states_csv": filename, "elapsed_seconds": time.perf_counter()-start}
    (out/f"metadata_k{area}.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(f"K={area}: {len(states)} states, max singlet block {report['maximum_singlet_dimension']}, "
          f"{report['elapsed_seconds']:.2f}s, compressed {report['archive_bytes']} bytes", flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k-min", type=int, default=2)
    parser.add_argument("--k-max", type=int, default=4)
    parser.add_argument("--output-dir", type=Path, default=ROOT/"results"/"closed-basis-volume")
    args = parser.parse_args()
    if not 0 <= args.k_min <= args.k_max:
        parser.error("require 0 <= k-min <= k-max")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    reports = [calculate_area(area, args.output_dir) for area in range(args.k_min, args.k_max+1)]
    summary = {"schema_version": 1, "date": "2026-10-08", "notation": "K=sum_i j_i=N_bosons/2; J_total=0",
               "storage": "Packed ragged singlet blocks in compressed NPZ; CSR basis transforms; no pickle or dropped matrix entries",
               "basis": "Condon–Shortley: ((j1,j2)k,(j3,j4)k) coupled to J=0; k ascending",
               "basis_phase": "sum_m (-1)^(k-m)|k,m>_12|k,-m>_34/sqrt(2k+1)",
               "support": "four labelled faces; zero-spin faces permitted; one copy, zero temperature",
               "units": {"gamma": GAMMA, "hbar": 1, "raw_prefactor": "(gamma*hbar)^(3/2)",
                         "geometric_rs_factor": math.sqrt(2)/12, "geometric_al_factor": math.sqrt(2)/6,
                         "physical_regularization": "unresolved"},
               "triples_zero_based": TRIPLES, "al_signs": SIGNS, "absolute_tolerance": ABS_TOL,
               "zero_eigenvalue_cutoff": "64*eps*max(1,max(abs(eigenvalues)))",
               "numpy": np.__version__, "scipy": scipy.__version__, "sympy": sympy.__version__,
               "areas": [{k:r[k] for k in r if k != "blocks"} for r in reports],
               "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.output_dir/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")


if __name__ == "__main__":
    main()

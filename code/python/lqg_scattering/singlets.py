"""SU(2)-singlet recoupling bases and sparse volume helpers."""

from collections import Counter
from functools import lru_cache
import itertools
import math

import numpy as np
from scipy.sparse import csr_matrix
from sympy import Rational
from sympy.physics.wigner import clebsch_gordan

from .coherent_states import su2_ops
from .conventions import GAMMA
from .fl_volume import direct_tensor_q
from .labels import enumerate_total_area
from .positivity import dot_operator, triple_matrix_block

PAIRS = tuple(itertools.combinations(range(4), 2))
TRIPLES = tuple(itertools.combinations(range(4), 3))
SIGNS = (1, -1, 1, -1)
ABS_TOL = 2e-10
ZERO_FACTOR = 64 * np.finfo(float).eps


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

def canonical_data(spins):
    """One complete M=0 magnetic basis and scalar-product matrices per pattern."""
    basis = occupation_basis(spins)
    dots = {p: action_matrix(basis, dot_operator(su2_ops(p[0]), su2_ops(p[1]))) for p in PAIRS}
    checks = {}
    q012 = 1j*(dots[0, 1]@dots[1, 2]-dots[1, 2]@dots[0, 1])
    difference = q012-independent_local_q(basis, spins)
    checks["q012_sparse_local_spin"] = float(np.max(abs(difference.data))) if difference.nnz else 0.0
    assert checks["q012_sparse_local_spin"] < ABS_TOL
    if sum(spins) <= 8:
        for triple in TRIPLES:
            a, b, c = triple
            q = (1j * (dots[a, b] @ dots[b, c] - dots[b, c] @ dots[a, b])).toarray()
            oscillator = triple_matrix_block(None, basis, triple)
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
            for i in range(len(occ) // 2):
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

__all__ = [
    "PAIRS", "TRIPLES", "SIGNS", "GAMMA", "ABS_TOL", "ZERO_FACTOR",
    "cg", "occupation_basis", "action_matrix", "independent_local_q",
    "canonical_data", "coupling_basis", "root_abs", "closure_residual",
    "save_csr", "pack_blocks", "load_block", "enumerate_total_area",
    "singlet_paths", "magnetic_singlet_count", "sequential_basis",
]


@lru_cache(maxsize=None)
def singlet_paths(spins):
    """Sequential coupling labels (2s_1,...,2s_N), ending at zero."""
    paths = [(spins[0],)]
    for spin in spins[1:]:
        paths = [path+(result,)
                 for path in paths
                 for result in range(abs(path[-1]-spin), path[-1]+spin+1, 2)]
    return tuple(path for path in paths if path[-1] == 0)


def magnetic_singlet_count(spins):
    """Independent multiplicity: dim(M=0)-dim(M=1)."""
    counts = Counter({0: 1})
    for spin in spins:
        updated = Counter()
        for magnetic, multiplicity in counts.items():
            for local in range(-spin, spin+1, 2):
                updated[magnetic+local] += multiplicity
        counts = updated
    return counts[0]-counts[2]


def sequential_basis(spins, paths, canonical_occupations):
    order = sorted(range(len(spins)), key=lambda i: (spins[i], i))
    inverse = [order.index(i) for i in range(len(spins))]
    occupations = [tuple(v for i in inverse for v in occ[2*i:2*i+2])
                   for occ in canonical_occupations]
    basis = np.zeros((len(occupations), len(paths)), complex)
    for row, occ in enumerate(occupations):
        magnetic = [occ[2*i]-occ[2*i+1] for i in range(len(spins))]
        for col, path in enumerate(paths):
            amplitude, cumulative_m = 1.0, magnetic[0]
            for i in range(1, len(spins)):
                amplitude *= cg(path[i-1], spins[i], path[i],
                                cumulative_m, magnetic[i], cumulative_m+magnetic[i])
                cumulative_m += magnetic[i]
                if amplitude == 0:
                    break
            basis[row, col] = amplitude
    return occupations, basis, inverse


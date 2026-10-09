"""Exact small-sector audit of the draft's thermal FL intertwiner.

Apply the draft's same-mode two-copy squeeze to |J,z>_FL,L |0>_R.
Use exact occupation amplitudes, not a Taylor approximation to squeezing.
Report ordinary L/R Gauss defects, the combined dual-copy constraint,
positive RS/AL moments, and a separately labelled double-singlet projection.
The projection is a conditional candidate, not an assumed Gibbs ensemble.
All volume numbers use the existing repository prefactors/sign convention.
"""

import argparse
from datetime import datetime, timezone
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from scipy import sparse
from scipy.linalg import expm

from lqg_scattering.coherent_states import su2_ops
from lqg_scattering.fl_volume import GAMMA, ORIENTATIONS
from lqg_scattering.intertwiners import fixed_area_state
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.tetrahedra import face_area_vectors
from lqg_scattering.positivity import _dot_ops, _q_action, rovelli_smolin_volume, ashtekar_lewandowski_volume
from project_paths import RESULTS_ROOT
from lqg_scattering.labels import compositions

N = 4
MODES = 2 * N
TRIPLES = tuple(itertools.combinations(range(N), 3))
PAIRS = tuple(itertools.combinations(range(N), 2))


def occupations(total, modes=MODES):
    """Compatibility entry point for exact fixed-number occupations."""
    return compositions(total, modes)


def matrix_action(basis, action):
    index = {o: i for i, o in enumerate(basis)}
    out = np.zeros((len(basis), len(basis)), complex)
    for col, occ in enumerate(basis):
        for target, value in action(occ):
            if abs(value) > 1e-14:
                out[index[target], col] += value
    return out


def sqrt_abs(matrix):
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    cutoff = 64 * np.finfo(float).eps * max(1., np.max(np.abs(eigenvalues)))
    values = np.sqrt(np.where(np.abs(eigenvalues) <= cutoff, 0., np.abs(eigenvalues)))
    return (eigenvectors * values) @ eigenvectors.conj().T


@lru_cache(None)
def sector(total):
    basis = list(occupations(total))
    index = {o: i for i, o in enumerate(basis)}
    groups = {}
    for i, o in enumerate(basis):
        counts = tuple(o[2*e] + o[2*e+1] for e in range(N))
        groups.setdefault((counts, sum(o[::2])), []).append(i)
    blocks = []
    for (counts, number_a), indices in groups.items():
        small_basis = [basis[i] for i in indices]
        dots = {pair: matrix_action(small_basis, _dot_ops(su2_ops(pair[0]), su2_ops(pair[1])))
                for pair in PAIRS}
        closure = np.eye(len(indices), dtype=complex) * sum(c*(c+2)/4 for c in counts)
        closure += 2 * sum(dots.values())
        values, vectors = np.linalg.eigh(closure)
        singlets = vectors[:, np.abs(values) < 1e-10] if 2*number_a == total else vectors[:, :0]
        projector = singlets @ singlets.conj().T
        qs = [matrix_action(small_basis, _q_action(t)) for t in TRIPLES]
        assert all(np.allclose(q, q.conj().T, atol=1e-12) for q in qs)
        rs = GAMMA**1.5 * sum(sqrt_abs(q) for q in qs)
        al = GAMMA**1.5 * sqrt_abs(sum(sign*q for sign, q in zip(ORIENTATIONS, qs)))
        blocks.append({'indices': np.array(indices), 'counts': counts, 'P': projector,
                       'rank': singlets.shape[1], 'closure': closure, 'dots': dots,
                       'q': qs[0], 'rs': rs, 'al': al})
    # Ordinary total generators: right copy uses the conjugate/dual action.
    generators = {}
    for kind in ('z', 'plus', 'minus'):
        rows, cols, data = [], [], []
        for col, occ in enumerate(basis):
            for edge in range(N):
                for target, value in su2_ops(edge)[kind](occ):
                    if value:
                        rows.append(index[target]); cols.append(col); data.append(value)
        generators[kind] = sparse.csr_matrix((data, (rows, cols)), shape=(len(basis),)*2)
    return {'basis': basis, 'index': index, 'blocks': blocks, 'generators': generators,
            'singlet_dimension': sum(b['rank'] for b in blocks)}


def project_left(coefficients, total):
    out = np.zeros_like(coefficients)
    for block in sector(total)['blocks']:
        if block['rank']:
            ids = block['indices']
            out[ids] = block['P'] @ coefficients[ids]
    return out


def project_right(coefficients, total):
    out = np.zeros_like(coefficients)
    for block in sector(total)['blocks']:
        if block['rank']:
            ids = block['indices']
            out[:, ids] = coefficients[:, ids] @ block['P'].T
    return out


def readouts(coefficients, left_total, right_total):
    left, right = sector(left_total), sector(right_total)
    out = dict(norm=float(np.vdot(coefficients, coefficients).real), closure_L=0.,
               closure_R=0., combined_dual_closure=0., q=0., q2=0.,
               V_RS=0., V_AL=0., V_RS2=0., V_AL2=0.)
    areas = np.zeros(N)
    gram = np.zeros((N, N))
    def moment(c, operator):
        return float(np.vdot(c, operator @ c).real)
    for block in left['blocks']:
        c = coefficients[block['indices']]
        if not np.any(c):
            continue
        norm = float(np.vdot(c, c).real)
        counts = np.asarray(block['counts'])
        areas += norm * counts / 2  # FL spin-area j_i; boson count is 2 j_i.
        gram[np.diag_indices(N)] += norm * counts*(counts+2)/4
        for i, j in PAIRS:
            gram[i, j] += moment(c, block['dots'][i, j])
            gram[j, i] = gram[i, j]
        out['closure_L'] += moment(c, block['closure'])
        for name, operator in [('q', block['q']), ('V_RS', block['rs']), ('V_AL', block['al'])]:
            out[name] += moment(c, operator)
            second = {'q': 'q2', 'V_RS': 'V_RS2', 'V_AL': 'V_AL2'}[name]
            out[second] += float(np.vdot(operator @ c, operator @ c).real)
    for block in right['blocks']:
        out['closure_R'] += moment(coefficients[:, block['indices']].T, block['closure'].T)
    for kind, factor in [('z', 1.), ('plus', .5), ('minus', .5)]:
        defect = left['generators'][kind] @ coefficients - (right['generators'][kind].T @ coefficients.T).T
        out['combined_dual_closure'] += factor * float(np.vdot(defect, defect).real)
    out['mean_face_spins'] = areas
    out['flux_gram'] = gram
    spectrum = np.linalg.eigvalsh(coefficients.conj().T @ coefficients)
    out['schmidt_weights_unnormalized'] = np.maximum(spectrum, 0.)
    return out


def seed_state(shape, J):
    if shape == 'regular':
        space, state = fixed_area_state(J)
    else:
        vertices = np.array([[0., 0., 0.], [1.3, 0., 0.], [.2, .9, 0.], [.25, .15, .8]])
        faces = face_area_vectors(vertices)
        areas = np.linalg.norm(faces, axis=1)
        fractions = areas / areas.sum()
        spinors = np.sqrt(2*fractions)[:, None] * spinors_from_normals(faces / areas[:, None])
        assert np.linalg.norm(sum(fractions[:, None]*faces/areas[:, None])) < 1e-12
        space, state = fixed_area_state(J, spinors)
    return state


def base_coefficients(seed, K, pairs):
    left, right = sector(K+pairs), sector(pairs)
    coefficients = np.zeros((len(left['basis']), len(right['basis'])), complex)
    for col, r in enumerate(right['basis']):
        for n, amplitude in seed.items():
            o = tuple(a+b for a, b in zip(n, r))
            factor = math.sqrt(math.prod(math.comb(a+b, b) for a, b in zip(n, r)))
            coefficients[left['index'][o], col] += amplitude * factor
    return coefficients


def assemble(parts, K, beta, cutoff):
    x = 0. if beta is None else math.exp(-beta)  # tanh(theta)^2, omega=1.
    result = {key: 0. for key in ('norm', 'closure_L', 'closure_R', 'combined_dual_closure',
                                'q', 'q2', 'V_RS', 'V_AL', 'V_RS2', 'V_AL2')}
    result['mean_face_spins'] = np.zeros(N)
    result['flux_gram'] = np.zeros((N, N))
    weights = []
    for r, part in enumerate(parts[:cutoff+1]):
        scale = (1-x)**(K+MODES) * x**r
        for key in result:
            result[key] += scale * part[key]
        weights.extend(scale*part['schmidt_weights_unnormalized'])
    norm = result['norm']
    assert norm > 0
    for key in result:
        if key != 'norm': result[key] /= norm
    eigenvalues = np.array(weights)/norm
    positive = eigenvalues[eigenvalues > 1e-14]
    result['left_entropy'] = float(-np.dot(positive, np.log(positive)))
    for op in ('RS', 'AL'):
        result[f'variance_V_{op}'] = max(0., result[f'V_{op}2']-result[f'V_{op}']**2)
    G = result['flux_gram']
    result['normalized_flux_gram'] = G/np.sqrt(np.outer(G.diagonal(), G.diagonal()))
    result['mean_total_spin_area'] = float(sum(result['mean_face_spins']))
    result['probability_any_zero_area_face'] = None  # Not inferred from mean areas.
    return result


def validate_squeezing():
    error = 0.
    for n in (0, 1, 2, 4):
        r = np.arange(40)
        raising = np.diag(np.sqrt((r[:-1]+1)*(n+r[:-1]+1)), -1)
        theta = .2
        exact = expm(theta*(raising-raising.T))[:, 0]
        analytic = np.array([math.sqrt(math.comb(n+k, k))*math.tanh(theta)**k/
                             math.cosh(theta)**(n+1) for k in r])
        error = max(error, float(np.max(np.abs(exact-analytic))))
    assert error < 1e-12, error
    return error


def run(cutoff, betas):
    assert cutoff >= 2
    validation = {'squeeze_amplitude_vs_independent_matrix_exponential_error': validate_squeezing()}
    validation['singlet_dimensions_N4_by_total_bosons'] = {
        str(K): sector(K)['singlet_dimension'] for K in range(7)}
    assert [sector(K)['singlet_dimension'] for K in range(7)] == [1, 0, 6, 0, 20, 0, 50]
    cases = []
    for shape, J in itertools.product(('regular', 'unequal_skew'), (1, 2)):
        K = 2*J
        seed = seed_state(shape, J)
        raw_parts, projected_parts = [], []
        for r in range(cutoff+1):
            C = base_coefficients(seed, K, r)
            raw = readouts(C, K+r, r)
            assert abs(raw['norm']-math.comb(K+MODES+r-1, r)) < 1e-8
            assert raw['combined_dual_closure'] < 1e-20 * max(1., raw['norm'])
            projected = project_right(project_left(C, K+r), r)
            raw_parts.append(raw)
            projected_parts.append(readouts(projected, K+r, r))
        control = assemble(raw_parts, K, None, cutoff)
        assert abs(control['norm']-1) < 1e-12 and abs(control['closure_L']) < 1e-12
        from lqg_scattering.coherent_states import FockSpace
        reference_space = FockSpace(N, K)
        reference_rs = rovelli_smolin_volume(seed, reference_space)
        reference_al = ashtekar_lewandowski_volume(seed, reference_space, dict(zip(TRIPLES, ORIENTATIONS)))
        reference_error = max(abs(reference_rs-control['V_RS']), abs(reference_al-control['V_AL']))
        assert reference_error < 1e-12
        rows = []
        for beta in betas:
            raw = assemble(raw_parts, K, beta, cutoff)
            physical = assemble(projected_parts, K, beta, cutoff)
            coarse = assemble(raw_parts, K, beta, cutoff-2)
            projected_coarse = assemble(projected_parts, K, beta, cutoff-2)
            nbar = 1/math.expm1(beta)
            analytic_defect = .75*(K+MODES)*nbar*(nbar+1)
            missing = max(0., 1-raw['norm'])
            assert abs(physical['closure_L']) < 1e-10
            assert abs(physical['closure_R']) < 1e-10
            if beta >= 5:
                assert abs(raw['closure_L']-analytic_defect) < 1e-5*max(1., analytic_defect)
            rows.append({'beta': beta, 'theta': math.atanh(math.exp(-beta/2)),
                         'unprojected_draft': raw, 'double_singlet_conditional_candidate': physical,
                         'exact_untruncated_ordinary_closure_defect': analytic_defect,
                         'unprojected_omitted_probability': missing,
                         'conditional_candidate_omitted_probability_upper_bound': missing/(physical['norm']+missing),
                         'cutoff_minus_two_comparison': {'pair_cutoff': cutoff-2,
                             'draft_closure_difference': raw['closure_L']-coarse['closure_L'],
                             'draft_V_RS_difference': raw['V_RS']-coarse['V_RS'],
                             'candidate_V_RS_difference': physical['V_RS']-projected_coarse['V_RS'],
                             'candidate_entropy_difference': physical['left_entropy']-projected_coarse['left_entropy']}})
        cases.append({'shape': shape, 'J': J, 'seed_bosons': K,
                      'seed_volume_vs_existing_implementation_max_error': reference_error,
                      'zero_temperature_seed': control, 'rows': rows})
        print(f'completed {shape} J={J}', flush=True)
    return {'created_utc': datetime.now(timezone.utc).isoformat(),
            'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'N': N, 'pair_cutoff': cutoff, 'gamma': GAMMA, 'hbar': 1.,
            'area_convention': 'j_i=(n_ai+n_bi)/2; spin area reported without gamma*hbar',
            'AL_orientation_signs_012_013_023_123': list(ORIENTATIONS),
            'right_copy': 'conjugate representation; combined generator J_L-J_R^T',
            'thermal_model': 'draft same-mode Bogoliubov squeeze of physical FL seed and R vacuum',
            'projection_model': 'explicit P_singlet,L x P_singlet,R postselection; not assumed Gibbs',
            'validation': validation, 'cases': cases}


def json_ready(value):
    if isinstance(value, np.ndarray): return value.tolist()
    if isinstance(value, dict): return {k: json_ready(v) for k, v in value.items()}
    if isinstance(value, list): return [json_ready(v) for v in value]
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pair-cutoff', type=int, default=4)
    parser.add_argument('--betas', type=float, nargs='+', default=[3., 4., 5., 8.])
    parser.add_argument('--output', type=Path,
                        default=RESULTS_ROOT / 't7_geometry_thermal_results.json')
    args = parser.parse_args()
    if any(b <= 0 for b in args.betas): parser.error('beta must be positive')
    args.output.write_text(json.dumps(json_ready(run(args.pair_cutoff, args.betas)), indent=2, allow_nan=False)+'\n')
    print(f'wrote {args.output}', flush=True)

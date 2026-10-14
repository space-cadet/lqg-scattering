"""Two independently closed four-face polyhedra at fixed combined linear area.

Units: hbar=1; F_ij^dag = a_i^dag b_j^dag - a_j^dag b_i^dag.
Face labels on the two copies correspond directly. No sewing is imposed.
"""
import itertools
import math

import numpy as np
from scipy import sparse

from .hamiltonian import build_fixed_k
from .intertwiners import fixed_area_state

PAIRS = tuple(itertools.combinations(range(4), 2))


def _area(value):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < 0:
        raise ValueError("area must be a nonnegative integer")
    return int(value)


def create_pair_occupations(source, target, pair):
    """Rectangular oscillator matrix, without projection or truncation."""
    i, j = pair
    if pair not in PAIRS:
        raise ValueError("pair must be an ordered distinct four-face pair")
    index = {tuple(o): row for row, o in enumerate(target)}
    rows, cols, values = [], [], []
    for col, occupation in enumerate(source):
        for a, b, sign in ((2*i, 2*j+1, 1), (2*j, 2*i+1, -1)):
            changed = list(occupation)
            amplitude = sign * math.sqrt((changed[a]+1)*(changed[b]+1))
            changed[a] += 1
            changed[b] += 1
            rows.append(index[tuple(changed)])
            cols.append(col)
            values.append(amplitude)
    return sparse.csr_matrix((values, (rows, cols)), shape=(len(target), len(source)))


def build_exchange_space(total_area):
    """Direct sum of H_k,L tensor H_(K-k),R, including both vacuum endpoints."""
    total_area = _area(total_area)
    local = [build_fixed_k(k) for k in range(total_area+1)]
    creators, residuals = {}, {}
    for k in range(total_area):
        low, high = local[k], local[k+1]
        for pair in PAIRS:
            raw = create_pair_occupations(low['occupations_m0'], high['occupations_m0'], pair)
            image = raw @ low['basis']
            projected = high['basis'].conj().T @ image
            residuals[f'creator_{k}_{pair}'] = float(np.max(abs(image-high['basis'] @ projected)))
            creators[k, pair] = projected
    dimensions = [m['basis'].shape[1] for m in local]
    sizes = [dimensions[k]*dimensions[total_area-k] for k in range(total_area+1)]
    offsets = np.cumsum([0]+sizes)
    sectors = [slice(int(offsets[k]), int(offsets[k+1])) for k in range(total_area+1)]
    dimension = int(offsets[-1])
    channels = {}
    for pair in PAIRS:
        blocks = [[None]*(total_area+1) for _ in range(total_area+1)]
        for k, size in enumerate(sizes):
            blocks[k][k] = sparse.csr_matrix((size, size), dtype=complex)
        for k in range(total_area):
            blocks[k+1][k] = sparse.kron(creators[k, pair], creators[total_area-k-1, pair].conj().T, format='csr')
        channels[pair] = sparse.bmat(blocks, format='csr')
    area = np.concatenate([np.full(size, k, float) for k, size in enumerate(sizes)])
    volumes, dots, faces = {}, {}, {}
    for side in ('L', 'R'):
        volumes[side] = sparse.block_diag([
            sparse.kron(sum(local[k]['volume_by_triple'].values()), sparse.eye(dimensions[total_area-k]))
            if side == 'L' else
            sparse.kron(sparse.eye(dimensions[k]), sum(local[total_area-k]['volume_by_triple'].values()))
            for k in range(total_area+1)], format='csr')
        for pair in PAIRS:
            dots[side, pair] = sparse.block_diag([
                sparse.kron(local[k]['spin_dots'][pair], sparse.eye(dimensions[total_area-k]))
                if side == 'L' else sparse.kron(sparse.eye(dimensions[k]), local[total_area-k]['spin_dots'][pair])
                for k in range(total_area+1)], format='csr')
        for face in range(4):
            faces[side, face] = np.concatenate([
                np.repeat(local[k]['site_spins'][:, face]/2, dimensions[total_area-k])
                if side == 'L' else np.tile(local[total_area-k]['site_spins'][:, face]/2, dimensions[k])
                for k in range(total_area+1)])
    residuals['local_closure'] = max(m['metadata']['singlet_closure_max_abs'] for m in local)
    residuals['local_orthogonality'] = max(m['metadata']['singlet_basis_orthogonality_max_abs'] for m in local)
    return dict(total_area=total_area, local=local, dimensions=dimensions, sectors=sectors,
                dimension=dimension, channels=channels, area_left=area, volumes=volumes,
                dots=dots, faces=faces, residuals=residuals)


def exchange_hamiltonian(space, coupling=1., epsilon_left=0., epsilon_right=0.,
                         repulsion_left=0., repulsion_right=0.):
    """H_X=epsilon_X A_X + U_X A_X(A_X-1)/2, plus corresponding-pair transfer.

    Coupling is either one complex scalar for all six channels or a pair map.
    Energies are finite real numbers. At fixed total area boundedness is exact.
    """
    parameters = np.asarray([epsilon_left, epsilon_right, repulsion_left, repulsion_right])
    if not np.isrealobj(parameters) or not np.all(np.isfinite(parameters)):
        raise ValueError('energy parameters must be finite real numbers')
    coefficients = coupling if isinstance(coupling, dict) else {p: coupling for p in PAIRS}
    if set(coefficients)-set(PAIRS) or not all(np.ndim(g) == 0 and np.isfinite(g) for g in coefficients.values()):
        raise ValueError('couplings must be finite scalars on valid pair channels')
    forward = sum((complex(g)*space['channels'][p] for p, g in coefficients.items()),
                  sparse.csr_matrix((space['dimension'],)*2, dtype=complex))
    left = space['area_left']
    right = space['total_area']-left
    diagonal = epsilon_left*left + epsilon_right*right
    diagonal += .5*(repulsion_left*left*(left-1)+repulsion_right*right*(right-1))
    h = sparse.diags(diagonal) + forward + forward.conj().T
    current = 1j*(forward.conj().T-forward)
    return h.tocsr(), current.tocsr(), forward.tocsr()


def fl_product(space, area_left, spinors_left=None, spinors_right=None):
    """Product FL seed in the shared singlet ordering; no conjugation required."""
    k = _area(area_left)
    if k > space['total_area']:
        raise ValueError('left area exceeds combined area')
    vectors = []
    for area, spinors in ((k, spinors_left), (space['total_area']-k, spinors_right)):
        model = space['local'][area]
        _, state = fixed_area_state(area, spinors=spinors)
        magnetic = np.array([state.get(tuple(o), 0j) for o in model['occupations_m0']])
        vector = model['basis'].conj().T @ magnetic
        if np.linalg.norm(magnetic-model['basis'] @ vector) > 1e-10:
            raise ArithmeticError('FL state left the singlet support')
        vectors.append(vector)
    state = np.zeros(space['dimension'], complex)
    state[space['sectors'][k]] = np.kron(*vectors)
    return state/np.linalg.norm(state)


def readout(space, state, current=None, forward=None):
    """Pure-state area, geometry, pair coherence, and bipartite entropy (nats)."""
    probability = abs(state)**2
    left = float(probability @ space['area_left'])
    result = dict(norm=float(probability.sum()), area_left=left,
                  area_right=space['total_area']-left,
                  area_variance=float(probability @ space['area_left']**2-left**2))
    eigenvalues = []
    for k, section in enumerate(space['sectors']):
        block = state[section].reshape(space['dimensions'][k], space['dimensions'][space['total_area']-k])
        eigenvalues.extend(np.linalg.svd(block, compute_uv=False)**2)
        result[f'p_area_{k}'] = float(np.vdot(block, block).real)
    positive = np.asarray(eigenvalues)
    positive = positive[positive > 0]
    result['entropy_nats'] = float(-np.sum(positive*np.log(positive)))
    for side, operator in space['volumes'].items():
        result[f'volume_{side}'] = float(np.vdot(state, operator @ state).real)
    for (side, pair), operator in space['dots'].items():
        result[f'dot_{side}_{pair[0]}{pair[1]}'] = float(np.vdot(state, operator @ state).real)
    for (side, face), diagonal in space['faces'].items():
        result[f'face_area_{side}_{face}'] = float(probability @ diagonal)
    if current is not None:
        result['current_left'] = float(np.vdot(state, current @ state).real)
    if forward is not None:
        value = np.vdot(state, forward @ state)
        result['weighted_pair_coherence_real'] = float(value.real)
        result['weighted_pair_coherence_imag'] = float(value.imag)
    return result

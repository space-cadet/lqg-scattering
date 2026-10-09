"""Gibbs weights, degenerate-subspace readouts, and Schmidt-form TFD helpers.

Energies passed to thermal_weights must be sorted in ascending order.
site_zero_entanglement reports reduced-state entropy: for a degenerate
zero-temperature Gibbs mixture it is not an entanglement measure.
"""
import math
import numpy as np
from .singlets import ABS_TOL, ZERO_FACTOR

def grouped_values(values, tol=ABS_TOL):
    groups = []
    for index, value in enumerate(values):
        found = next((group for group in groups
                      if abs(value - group["value"]) <= tol), None)
        if found is None:
            groups.append({"value": float(value), "indices": [index]})
        else:
            found["indices"].append(index)
    return groups


def thermal_weights(energies, beta):
    if math.isinf(beta):
        mask = abs(energies - energies[0]) <= ABS_TOL
        weights = mask.astype(float) / int(mask.sum())
        return weights, None
    shifted = np.exp(-beta * (energies - energies[0]))
    weights = shifted / shifted.sum()
    log_z = -beta * energies[0] + math.log(float(shifted.sum()))
    return weights, log_z


def zero_volume_probabilities(volume, state_vectors):
    volume_values, volume_vectors = np.linalg.eigh((volume + volume.conj().T) / 2)
    cutoff = ZERO_FACTOR * max(1.0, float(np.max(abs(volume_values))))
    zero_vectors = volume_vectors[:, abs(volume_values) <= cutoff]
    if zero_vectors.shape[1] == 0:
        return np.zeros(state_vectors.shape[1], dtype=float)
    projector = zero_vectors @ zero_vectors.conj().T
    return np.real(np.diag(state_vectors.conj().T @ projector @ state_vectors))


def mean_in_ground_subspace(operator, eigenvectors, ground_mask):
    ground = eigenvectors[:, ground_mask]
    return float(np.real(np.trace(ground.conj().T @ operator @ ground)) / ground.shape[1])


def site_zero_entanglement(model, eigenvectors, ground_mask):
    """Entropy of site 0 after tracing sites 1--3 in the zero-T Gibbs state."""
    occupations = model["occupations_m0"]
    local_labels = sorted({(state[0], state[1]) for state in occupations})
    rest_labels = sorted({tuple(state[2:]) for state in occupations})
    local_index = {label: index for index, label in enumerate(local_labels)}
    rest_index = {label: index for index, label in enumerate(rest_labels)}
    rho = np.zeros((len(local_labels), len(local_labels)), dtype=complex)
    ground = eigenvectors[:, ground_mask]
    magnetic_ground = model["basis"] @ ground
    for column in range(ground.shape[1]):
        amplitudes = np.zeros((len(local_labels), len(rest_labels)), dtype=complex)
        for row, state in enumerate(occupations):
            amplitudes[local_index[(state[0], state[1])], rest_index[tuple(state[2:])]] = magnetic_ground[row, column]
        rho += amplitudes @ amplitudes.conj().T / ground.shape[1]
    values = np.linalg.eigvalsh((rho + rho.conj().T) / 2)
    values = np.maximum(values, 0.0)
    values /= values.sum()
    entropy = float(-np.sum(values[values > 0] * np.log(values[values > 0])))
    purity = float(np.sum(values ** 2))
    return entropy, purity, float(abs(np.trace(rho) - 1.0))


def entropy(p):
    m = p > 0
    return float(-(p[m] * np.log(p[m])).sum())


def correlator(p, rows, cols, data):
    """<q_L q_R> = sum_{nm} sqrt(p_n p_m) (q_nm)^2 over sparse nnz."""
    c = np.sum(np.sqrt(p[rows] * p[cols]) * data * data)
    assert abs(c.imag) < 1e-9 * max(1.0, abs(c.real)), c
    return float(c.real)


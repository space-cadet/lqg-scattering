"""Reusable flux, covariance, and positive-volume statistics."""

import itertools

import numpy as np

from .coherent_states import expectation, su2_ops
from .positivity import active_vertex_blocks, dot_operator, triple_matrix_block
from .conventions import GAMMA, TETRAHEDRON_ORIENTATIONS

ZERO_FACTOR = 64.0 * np.finfo(float).eps


def flux_gram(state, space):
    """Return G_ij=<J_i.J_j>, including local Casimirs on the diagonal."""
    n_edges = space.N
    gram = np.zeros((n_edges, n_edges), dtype=float)
    for i in range(n_edges):
        def casimir(occupation, edge=i):
            spin = (occupation[2 * edge] + occupation[2 * edge + 1]) / 2.0
            return [(occupation, spin * (spin + 1.0))]

        gram[i, i] = expectation(state, casimir, space).real
        for j in range(i + 1, n_edges):
            value = expectation(state, dot_operator(su2_ops(i), su2_ops(j)), space).real
            gram[i, j] = gram[j, i] = value
    return gram

def expected_face_spins(state):
    """Return <j_i> using the occupation probabilities in the FL state."""
    n_edges = len(next(iter(state))) // 2
    means = np.zeros(n_edges, dtype=float)
    norm2 = 0.0
    for occupation, amplitude in state.items():
        probability = float(abs(amplitude) ** 2)
        norm2 += probability
        for edge in range(n_edges):
            means[edge] += probability * 0.5 * (
                occupation[2 * edge] + occupation[2 * edge + 1]
            )
    return means / norm2

def positive_sqrt_abs(matrix):
    """Hermitian sqrt(abs(M)), using the repository's zero-mode cutoff."""
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.conj().T))
    scale = max(1.0, float(np.max(np.abs(values))))
    values[np.abs(values) <= ZERO_FACTOR * scale] = 0.0
    return (vectors * np.sqrt(np.abs(values))[None, :]) @ vectors.conj().T

def flux_correlation_geometry(state, space, normals):
    """Summarize covariance closure and its match to input face normals."""
    gram = flux_gram(state, space)
    rms = np.sqrt(np.maximum(np.diag(gram), 0.0))
    normalized = gram / np.outer(rms, rms)
    input_gram = np.asarray(normals) @ np.asarray(normals).T
    return {
        "closureResidual": float(np.linalg.norm(gram @ np.ones(space.N))),
        "minimumEigenvalue": float(np.min(np.linalg.eigvalsh(gram))),
        "rmsFaceAreaFractions": (rms / rms.sum()).tolist(),
        "maxNormalizedCorrelationError": float(np.max(np.abs(normalized - input_gram))),
        "fluxGram": gram.tolist(),
    }


def volume_moments(state, space, orientation_signs=None, gamma=GAMMA):
    """Return mean and variance for RS and oriented AL positive volumes.

    ``orientation_signs`` maps triples to embedding signs. The default is the
    repository's four-face tetrahedron convention; other valences must supply
    their own signs explicitly.
    """
    triples = tuple(itertools.combinations(range(space.N), 3))
    if orientation_signs is None:
        if space.N != 4:
            raise ValueError("orientation_signs are required away from valence four")
        orientation_signs = dict(zip(triples, TETRAHEDRON_ORIENTATIONS))
    norm2 = float(np.vdot(space.vec(state), space.vec(state)).real)
    moments = {"rs": [0.0, 0.0], "al": [0.0, 0.0]}
    for basis, vector in active_vertex_blocks(space, state):
        q_matrices = {
            triple: triple_matrix_block(space, basis, triple)
            for triple in triples
        }
        rs_matrix = sum(
            (positive_sqrt_abs(q) for q in q_matrices.values()),
            np.zeros_like(next(iter(q_matrices.values()))),
        )
        al_q = sum(
            (orientation_signs[t] * q_matrices[t] for t in triples),
            np.zeros_like(rs_matrix),
        )
        al_matrix = positive_sqrt_abs(al_q)
        for key, operator in (("rs", rs_matrix), ("al", al_matrix)):
            applied = operator @ vector
            moments[key][0] += float(np.vdot(vector, applied).real)
            moments[key][1] += float(np.vdot(applied, applied).real)

    scale = gamma**1.5
    output = {}
    for key, (first, second) in moments.items():
        mean = first / norm2
        variance = max(0.0, second / norm2 - mean * mean)
        output[key] = {
            "meanProjectUnits": scale * mean,
            "varianceProjectUnitsSquared": scale**2 * variance,
        }
    return output


__all__ = [
    "flux_gram", "expected_face_spins", "flux_correlation_geometry",
    "positive_sqrt_abs", "volume_moments",
]

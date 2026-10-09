"""Explicit coherent-face and closed-tetrahedron initial states.

These constructors return normalized kets in build_fixed_number_model's
occupation ordering. Spin labels are twice-integers; spinors use the local
J=(a^dag,b^dag) Schwinger convention.
"""
import itertools
import math

import numpy as np

from .intertwiners import fixed_area_state


def coherent_face_product(model, twice_spins, spinors):
    """Tensor product of spin-coherent faces in an exact total-number sector.

    A site with ``twice_spins[i]=2*j_i`` is in the normalized state
    ``(z_a a^dag + z_b b^dag)**(2*j_i)/sqrt((2*j_i)!) |0>``.
    A zero label denotes a missing/empty face. This product is not projected
    onto total-spin zero.
    """
    n_sites = model["metadata"]["available_sites"]
    total = model["metadata"]["fixed_boson_number"]
    spins = tuple(twice_spins)
    spinors = np.asarray(spinors, dtype=complex)
    if len(spins) != n_sites or any(
            isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer))
            or value < 0 for value in spins):
        raise ValueError("twice_spins must be nonnegative integer labels, one per site")
    if spinors.shape != (n_sites, 2) or not np.all(np.isfinite(spinors)):
        raise ValueError("spinors must be a finite (n_sites, 2) array")
    if not np.allclose(np.linalg.norm(spinors, axis=1), 1., atol=1e-12, rtol=0):
        raise ValueError("each face spinor must have unit norm")
    if sum(spins) != total:
        raise ValueError("twice-spin labels must sum to the model's boson number")
    vector = np.zeros(model["metadata"]["dimension"], dtype=complex)
    for magnetic in itertools.product(*(range(value + 1) for value in spins)):
        occupation, amplitude = [], 1. + 0j
        for edge, (twice_j, na) in enumerate(zip(spins, magnetic)):
            nb = twice_j - na
            occupation.extend((na, nb))
            amplitude *= math.sqrt(math.comb(twice_j, na))
            amplitude *= spinors[edge, 0] ** na * spinors[edge, 1] ** nb
        row = model["index"].get(tuple(occupation))
        if row is None:
            raise ValueError("basis does not contain the requested spin-coherent product")
        vector[row] = amplitude
    norm = np.linalg.norm(vector)
    if norm <= 0:
        raise ValueError("coherent product has zero norm")
    return vector / norm


def closed_fl_tetrahedron(model, area_label=2, spinors=None):
    """Embed the existing four-face FL coherent intertwiner in a fixed-N basis."""
    n_sites = model["metadata"]["available_sites"]
    bosons = model["metadata"]["fixed_boson_number"]
    if n_sites != 4 or bosons != 2 * area_label:
        raise ValueError("the FL seed requires four sites and boson number 2*area_label")
    _, state = fixed_area_state(area_label, spinors=spinors)
    vector = np.zeros(model["metadata"]["dimension"], dtype=complex)
    for occupation, amplitude in state.items():
        row = model["index"].get(tuple(occupation))
        if row is None:
            raise ValueError("basis does not contain the FL seed support")
        vector[row] = amplitude
    return vector

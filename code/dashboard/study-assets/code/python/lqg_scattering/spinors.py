"""SU(2) spinors and invariants of ordered spinor rays."""

import numpy as np


def spinors_from_normals(normals):
    """Return normalized SU(2) spinors whose Bloch vectors are ``normals``."""
    normals = np.asarray(normals, dtype=float)
    if normals.ndim != 2 or normals.shape[1] != 3:
        raise ValueError(f"normals must have shape (n, 3), got {normals.shape}")
    lengths = np.linalg.norm(normals, axis=1)
    if np.any(lengths == 0.0):
        raise ValueError("face normals must be nonzero")
    normals = normals / lengths[:, None]
    spinors = []
    for x, y, z in normals:
        theta, phi = np.arccos(z), np.arctan2(y, x)
        spinors.append(
            [np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)]
        )
    return np.asarray(spinors)

def spinor_bracket(left, right):
    return left[0] * right[1] - left[1] * right[0]


def face_vectors_from_spinors(spinors):
    """Return z^dagger sigma z/2; vacuum rows give zero face vectors."""
    z=np.asarray(spinors,dtype=complex)
    if z.ndim!=2 or z.shape[1]!=2 or not np.all(np.isfinite(z)):
        raise ValueError('spinors must be a finite (L,2) array')
    product=z[:,0].conj()*z[:,1]
    return np.column_stack((product.real,product.imag,(abs(z[:,0])**2-abs(z[:,1])**2)/2))

def four_point_cross_ratio(spinors):
    """Möbius-invariant cross ratio for the ordered four spinor rays."""
    numerator = spinor_bracket(spinors[0], spinors[2]) * spinor_bracket(
        spinors[1], spinors[3]
    )
    denominator = spinor_bracket(spinors[0], spinors[3]) * spinor_bracket(
        spinors[1], spinors[2]
    )
    if abs(denominator) < 1e-12:
        raise ValueError("sample reached a cross-ratio collision")
    return numerator / denominator

__all__ = ["spinors_from_normals", "face_vectors_from_spinors", "spinor_bracket", "four_point_cross_ratio"]

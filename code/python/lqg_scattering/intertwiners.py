"""Fixed-area Freidel-Livine intertwiner state construction."""

import itertools

import numpy as np

from .coherent_states import FockSpace, schwinger_edge_operator as _edge_ops
from .spinors import spinors_from_normals
from .tetrahedra import TETRAHEDRON_NORMALS

def regular_tetrahedron_spinors():
    return spinors_from_normals(TETRAHEDRON_NORMALS)

def fixed_area_state(area_label, spinors=None):
    """Build normalized (F_z^dagger)^J|0> for J=area_label."""
    spinors = (
        regular_tetrahedron_spinors()
        if spinors is None
        else np.asarray(spinors, dtype=complex)
    )
    if spinors.ndim != 2 or spinors.shape[1] != 2:
        raise ValueError(f"spinors must have shape (n, 2), got {spinors.shape}")
    n_edges = spinors.shape[0]

    def bracket(left, right):
        return left[0] * right[1] - left[1] * right[0]

    # Eq. (40): F_z^dagger = sum_(i<j) [z_j|z_i> F_ij^dagger.
    coefficients = {
        (i, j): bracket(spinors[j], spinors[i])
        for i, j in itertools.combinations(range(n_edges), 2)
    }
    space = FockSpace(n_edges, 2 * area_label)

    def apply_pair(state, i, j):
        out = {}
        create_ai = _edge_ops("adag", i, n_edges)
        create_bj = _edge_ops("bdag", j, n_edges)
        create_aj = _edge_ops("adag", j, n_edges)
        create_bi = _edge_ops("bdag", i, n_edges)
        for occupation, amplitude in state.items():
            for intermediate, factor_1 in create_bj(occupation):
                for result, factor_2 in create_ai(intermediate):
                    out[result] = out.get(result, 0j) + amplitude * factor_1 * factor_2
            for intermediate, factor_1 in create_bi(occupation):
                for result, factor_2 in create_aj(intermediate):
                    out[result] = out.get(result, 0j) - amplitude * factor_1 * factor_2
        return out

    state = {(0,) * (2 * n_edges): 1.0 + 0.0j}
    for _ in range(area_label):
        updated = {}
        for (i, j), coefficient in coefficients.items():
            for occupation, amplitude in apply_pair(state, i, j).items():
                updated[occupation] = (
                    updated.get(occupation, 0j) + coefficient * amplitude
                )
        state = updated

    norm = np.linalg.norm(space.vec(state))
    return space, {
        occupation: amplitude / norm for occupation, amplitude in state.items()
    }

def evolve_fl_spinors(spinors, hopping, time):
    """Exact FL label evolution for H=sum_ij h_ij E_ij, hbar=1.

    This preserves the FL manifold only for quadratic, number-conserving
    hopping. It does not incorporate onsite or spin/pair interactions.
    """
    z=np.asarray(spinors,dtype=complex)
    h=np.asarray(hopping,dtype=complex)
    if z.ndim!=2 or z.shape[1]!=2 or h.shape!=(len(z),len(z)):
        raise ValueError('spinors must be (L,2) and hopping (L,L)')
    if not np.all(np.isfinite(z)) or not np.all(np.isfinite(h)) or not np.isfinite(time):
        raise ValueError('labels, hopping and time must be finite')
    if not np.allclose(h,h.conj().T,atol=1e-12,rtol=0):
        raise ValueError('hopping must be Hermitian')
    energies,vectors=np.linalg.eigh(h)
    return vectors @ (np.exp(-1j*energies*time)[:,None]*(vectors.conj().T @ z))


def fl_face_statistics(area, spinors):
    """Exact single-face binomial moments for a closed fixed-area FL state.

    Normalize Z^dagger Z=I_2. Then n_i is Binomial(K,||z_i||^2),
    and A_i=n_i/2. Joint face occupations are correlated; no independence
    between faces is assumed. The supplied labels must already obey closure.
    """
    if isinstance(area,(bool,np.bool_)) or not isinstance(area,(int,np.integer)) or area<1:
        raise ValueError('area must be a positive integer')
    z=np.asarray(spinors,dtype=complex)
    if z.ndim!=2 or z.shape[1]!=2 or not np.all(np.isfinite(z)):
        raise ValueError('spinors must be finite with shape (L,2)')
    gram=z.conj().T @ z
    scale=np.trace(gram).real/2
    if scale<=0 or not np.allclose(gram,scale*np.eye(2),atol=1e-11,rtol=1e-11):
        raise ValueError('spinors must be nonzero and closed: Z^dagger Z proportional to I')
    z=z/np.sqrt(scale)
    p=np.clip(np.sum(abs(z)**2,axis=1),0.,1.)
    with np.errstate(divide='ignore'):
        active=-np.expm1(area*np.log1p(-p))
    mean=area*p/2
    variance=area*p*(1-p)/4
    return dict(spinors=z, occupation_parameter=p, mean_face_area=mean,
        face_area_variance=variance, active_probability=active,
        expected_active_faces=float(active.sum()),
        area_concentration=float(np.sum(variance+mean**2)/area**2))


__all__ = ["regular_tetrahedron_spinors", "fixed_area_state", "evolve_fl_spinors", "fl_face_statistics"]

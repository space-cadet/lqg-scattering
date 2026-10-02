"""Small exact-sector examples for the RS and AL vertex volume operators."""
import itertools
import numpy as np

from coherent_states import FockSpace
from positivity import (
    ashtekar_lewandowski_volume,
    rovelli_smolin_volume,
    volume_operator,
)


def paired_spin_half_singlet(space):
    """Product of spin singlets on edges (0,1) and (2,3)."""
    state = {}
    for s12, s34 in itertools.product((1, -1), repeat=2):
        p12 = [(1, 0), (0, 1)] if s12 > 0 else [(0, 1), (1, 0)]
        p34 = [(1, 0), (0, 1)] if s34 > 0 else [(0, 1), (1, 0)]
        occ = tuple(x for pair in (*p12, *p34) for x in pair)
        state[occ] = 0.5 * s12 * s34
    return state


def main():
    space = FockSpace(4, 4)
    state = paired_spin_half_singlet(space)
    # Outgoing tangents of a regular tetrahedron; order is 012, 013, 023, 123.
    tangents = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]])
    orientations = {
        triple: int(np.sign(np.linalg.det(tangents[list(triple)])))
        for triple in itertools.combinations(range(4), 3)
    }
    q_mean = volume_operator(state, space, triple=(0, 1, 2))[1]
    rs = rovelli_smolin_volume(state, space)
    al = ashtekar_lewandowski_volume(state, space, orientations)
    # Independent tensor-product SU(2) construction, in the local order
    # |up up up up>, ..., |down down down down>.
    identity = np.eye(2)
    jops = [np.array([[0, 1], [1, 0]], complex) / 2,
            np.array([[0, -1j], [1j, 0]], complex) / 2,
            np.diag([0.5, -0.5])]
    edge_j = {}
    for edge in range(4):
        for axis, operator in enumerate(jops):
            factors = [identity] * 4
            factors[edge] = operator
            embedded = factors[0]
            for factor in factors[1:]:
                embedded = np.kron(embedded, factor)
            edge_j[edge, axis] = embedded
    epsilon = np.zeros((3, 3, 3))
    epsilon[0, 1, 2] = epsilon[1, 2, 0] = epsilon[2, 0, 1] = 1
    epsilon[0, 2, 1] = epsilon[2, 1, 0] = epsilon[1, 0, 2] = -1
    q_tensor = {}
    for i, j, k in itertools.combinations(range(4), 3):
        q_tensor[i, j, k] = sum(
            epsilon[a, b, c] * edge_j[i, a] @ edge_j[j, b] @ edge_j[k, c]
            for a, b, c in itertools.product(range(3), repeat=3)
        )
    psi = np.zeros(16, dtype=complex)
    psi[[5, 10]] = 0.5
    psi[[6, 9]] = -0.5

    def spectral_mean(operator):
        eigenvalues, eigenvectors = np.linalg.eigh(operator)
        return float(np.sum(np.abs(eigenvectors.conj().T @ psi) ** 2
                            * np.sqrt(np.abs(eigenvalues))))

    rs_independent = sum(spectral_mean(q) for q in q_tensor.values()) * (0.2375 ** 1.5)
    q_al = sum(orientations[t] * q_tensor[t] for t in q_tensor)
    al_independent = spectral_mean(q_al) * (0.2375 ** 1.5)
    assert np.isclose(rs, rs_independent, atol=1e-12)
    assert np.isclose(al, al_independent, atol=1e-12)
    print(f"paired spin-1/2 singlet: norm={sum(abs(a)**2 for a in state.values()):.1f}")
    print(f"  <q_012>={q_mean.real:.12g}{q_mean.imag:+.3g}i (old proxy is zero)")
    print(f"  V_RS={rs:.12f}; V_AL={al:.12f} (project normalization)")
    print(f"  independent tensor-product check: RS={rs_independent:.12f}; AL={al_independent:.12f}")

    up4 = {tuple(x for _ in range(4) for x in (1, 0)): 1.0}
    print("collinear |up>^4 product state:")
    print(f"  V_RS={rovelli_smolin_volume(up4, space):.3g}; "
          f"V_AL={ashtekar_lewandowski_volume(up4, space, orientations):.3g}")


if __name__ == "__main__":
    main()

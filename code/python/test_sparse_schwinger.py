import itertools
import math
import unittest

import numpy as np
import scipy.sparse as sp

from lqg_scattering.schwinger import (
    SparseSchwingerSpace,
    normalized_taylor_exp,
    q_operator,
    volume_on_vec,
)
import t5a_mag_sweep
import t5b_perturbation as t5b
import t7a_thermal as t7a
from t5b_perturbation import OpSpace as T5bOpSpace
from t7a_thermal import OpSpace as T7aOpSpace
from lqg_scattering.positivity import positive_plane_curve


class SparseSchwingerTests(unittest.TestCase):
    def test_cutoff_basis_and_u_n_commutator(self):
        space = SparseSchwingerSpace(2, 2)
        self.assertEqual(space.dim, math.comb(6, 4))
        self.assertEqual(len({tuple(row) for row in space.occs}), space.dim)
        self.assertTrue(np.all(space.occs.sum(axis=1) <= 2))

        for i, j, k, l in itertools.product(range(2), repeat=4):
            lhs = space.E[i, j] @ space.E[k, l] - space.E[k, l] @ space.E[i, j]
            rhs = (space.E[i, l] if j == k else 0) - (
                space.E[k, j] if l == i else 0
            )
            np.testing.assert_allclose((lhs - rhs).toarray(), 0.0, atol=1e-13)

    def test_local_su2_and_triple_grasp_are_hermitian(self):
        space = SparseSchwingerSpace(3, 4)
        for edge in range(3):
            np.testing.assert_allclose(
                (space.Jz[edge] @ space.Jp[edge]
                 - space.Jp[edge] @ space.Jz[edge] - space.Jp[edge]).toarray(),
                0.0, atol=1e-13,
            )
            np.testing.assert_allclose(
                (space.Jp[edge] @ space.Jm[edge]
                 - space.Jm[edge] @ space.Jp[edge]
                 - 2 * space.Jz[edge]).toarray(),
                0.0, atol=1e-13,
            )

        q = q_operator(space)
        np.testing.assert_allclose((q - q.getH()).toarray(), 0.0, atol=1e-13)
        vector = np.arange(1, space.dim + 1, dtype=complex)
        vector /= np.linalg.norm(vector)
        volume, mean_q = volume_on_vec(vector, space)
        self.assertTrue(np.isfinite(volume))
        self.assertAlmostEqual(mean_q.imag, 0.0, places=13)

    def test_taylor_helper_and_legacy_adapter_returns(self):
        generator = sp.csr_matrix([[0.0, -0.2], [0.2, 0.0]])
        reference = np.array([1.0, 0.0], dtype=complex)
        expected = np.array([np.cos(0.2), np.sin(0.2)], dtype=complex)
        state, iterations = normalized_taylor_exp(generator, reference, 1)
        np.testing.assert_allclose(state, expected, atol=1e-12)
        self.assertGreater(iterations, 0)

        t5b_value = T5bOpSpace.taylor_exp(generator, reference, 1)
        t7a_value, t7a_iterations = T7aOpSpace.taylor_exp(generator, reference, 1)
        np.testing.assert_allclose(t5b_value, t7a_value, atol=0.0)
        self.assertEqual(iterations, t7a_iterations)

    def test_study_scripts_share_geometry_helpers(self):
        expected = positive_plane_curve(5, seed=12)
        np.testing.assert_array_equal(t5b.positive_plane_curve(5, seed=12), expected)
        np.testing.assert_array_equal(t7a.positive_plane_curve(5, seed=12), expected)
        np.testing.assert_array_equal(
            t5a_mag_sweep.moment_curve_plane(5, seed=12), expected.astype(complex)
        )
        expected_complex = expected.astype(complex)
        expected_complex[1] += 1j * 0.35 * (np.arange(5) + 0.5)
        np.testing.assert_array_equal(
            t5a_mag_sweep.fixed_complex_plane(5, seed=12), expected_complex
        )


if __name__ == "__main__":
    unittest.main()

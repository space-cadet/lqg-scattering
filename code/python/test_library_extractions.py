import itertools
import math
import unittest

import numpy as np

from lqg_scattering.fixed_k import (
    fixed_number_basis, pairwise_grasp, single_edge_operators,
)
from lqg_scattering.fl_volume import evaluate_area
from lqg_scattering.intertwiners import fixed_area_state
from lqg_scattering.minkowski import gen_kinematics_2to2, minkowski_data
from lqg_scattering.observables import expected_face_spins, flux_gram, volume_moments
from lqg_scattering.schwinger import SparseSchwingerSpace, normalized_taylor_exp
from lqg_scattering.spinors import four_point_cross_ratio, spinors_from_normals
from lqg_scattering.tetrahedra import (
    closed_equal_area_normals,
    closed_face_vectors_from_shape,
    reconstruct_from_gram,
    tetrahedron_from_face_vectors,
)


class LibraryExtractionTests(unittest.TestCase):
    def test_fixed_number_operators_are_built_from_an_exact_sector(self):
        n, k = 4, 2
        occupations, index = fixed_number_basis(n, k)
        self.assertEqual(len(occupations), math.comb(k + 2 * n - 1, 2 * n - 1))
        self.assertEqual(len(index), len(occupations))
        np.testing.assert_array_equal(occupations.sum(axis=1), k)

        edge_ops = single_edge_operators(occupations, index, n)
        grasp = pairwise_grasp(edge_ops, 0, 1)
        np.testing.assert_allclose((grasp - grasp.getH()).toarray(), 0.0, atol=1e-13)

    def test_sparse_space_exposes_the_shared_taylor_action(self):
        from scipy.sparse import csr_matrix

        space = SparseSchwingerSpace(1, 1)
        generator = csr_matrix([
            [0.0, -0.2, 0.0],
            [0.2, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ])
        reference = np.array([1.0, 0.0, 0.0], dtype=complex)
        expected, expected_terms = normalized_taylor_exp(generator, reference, 1)
        actual, actual_terms = space.taylor_exp(generator, reference, 1)
        np.testing.assert_allclose(actual, expected, atol=0.0)
        self.assertEqual(actual_terms, expected_terms)

    def test_tetrahedron_geometry_helpers_close_and_reconstruct(self):
        normals = closed_equal_area_normals(0.5, math.pi / 3)
        np.testing.assert_allclose(normals.sum(axis=0), 0.0, atol=1e-14)
        spinors = spinors_from_normals(normals)
        np.testing.assert_allclose(np.linalg.norm(spinors, axis=1), 1.0, atol=1e-14)
        self.assertTrue(np.isfinite(four_point_cross_ratio(spinors)))

        faces = closed_face_vectors_from_shape([0.25] * 4, 0.3, math.pi / 3)
        vertices, volume, reconstructed = tetrahedron_from_face_vectors(faces.copy())
        self.assertGreater(volume, 0.0)
        np.testing.assert_allclose(reconstructed @ reconstructed.T, faces @ faces.T,
                                   atol=1e-11)
        self.assertEqual(vertices.shape, (4, 3))

    def test_scattering_kinematics_closes_in_all_incoming_convention(self):
        momenta, signs = gen_kinematics_2to2(np.random.default_rng(17))
        areas, normals, residual = minkowski_data(momenta, signs)
        self.assertEqual(areas.shape, (4,))
        self.assertEqual(normals.shape, (4, 3))
        self.assertLess(residual, 1e-12)
        np.testing.assert_allclose((areas[:, None] * normals).sum(axis=0), 0.0,
                                   atol=1e-12)

    def test_intertwiner_observables_and_volume_checks_share_the_package(self):
        space, state = fixed_area_state(2)
        self.assertAlmostEqual(sum(abs(value) ** 2 for value in state.values()), 1.0)
        np.testing.assert_allclose(expected_face_spins(state), 0.5, atol=1e-13)

        gram = flux_gram(state, space)
        reconstruction = reconstruct_from_gram(gram)
        self.assertLess(reconstruction["reconstructedFaceGramMaxAbsError"], 1e-11)
        moments = volume_moments(state, space)
        checked = evaluate_area(2, direct_check=True)
        self.assertAlmostEqual(moments["rs"]["meanProjectUnits"],
                               checked["rsPositiveVolumeProjectUnits"], places=11)
        self.assertAlmostEqual(moments["al"]["meanProjectUnits"],
                               checked["alPositiveVolumeProjectUnits"], places=11)
        self.assertLess(checked["maxTripleMatrixDifference"], 1e-11)

    def test_fixed_area_state_constructor_accepts_a_single_triangle(self):
        normals = np.array([
            [1.0, 0.0, 0.0],
            [-0.5, math.sqrt(3.0) / 2.0, 0.0],
            [-0.5, -math.sqrt(3.0) / 2.0, 0.0],
        ])
        spinors = spinors_from_normals(normals) * math.sqrt(2.0 / 3.0)
        closure = sum(np.outer(z, z.conj()) for z in spinors)
        np.testing.assert_allclose(closure, np.eye(2), atol=1e-14)

        space, state = fixed_area_state(1, spinors=spinors)
        self.assertEqual(space.N, 3)
        self.assertAlmostEqual(sum(abs(value) ** 2 for value in state.values()), 1.0)
        self.assertTrue(all(sum(occupation) == 2 for occupation in state))


if __name__ == "__main__":
    unittest.main()

"""Physical invariants and legacy contracts for the extracted study cores."""
import math
import unittest

import numpy as np

from lqg_scattering.analysis import fit_power
from lqg_scattering.conventions import GAMMA
from lqg_scattering.hamiltonian import build_fixed_k, connected_triples
from lqg_scattering.labels import compositions, fixed_face_dimension, positive_face_dimension
from lqg_scattering.singlets import (
    closure_residual, magnetic_singlet_count, occupation_basis,
    sequential_basis, singlet_paths,
)
from lqg_scattering.thermal import correlator, entropy, thermal_weights
from lqg_scattering.volume_blocks import canonical_operators


class ExtractedStudyCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = build_fixed_k(2)

    def test_four_site_operators_preserve_the_singlet_space(self):
        model = self.model
        basis = model['basis']
        self.assertEqual(basis.shape, (100, 20))
        np.testing.assert_allclose(basis.conj().T @ basis, np.eye(20), atol=1e-13)
        self.assertLess(closure_residual(model['occupations_m0'], basis), 1e-13)
        volume = sum(model['volume_by_triple'].values())
        self.assertGreaterEqual(np.linalg.eigvalsh(volume).min(), -1e-13)
        np.testing.assert_allclose(model['onsite'] @ volume - volume @ model['onsite'],
                                   0.0, atol=1e-13)
        hopping = sum(model['bonds'].values())
        np.testing.assert_allclose(hopping, hopping.conj().T, atol=1e-13)
        self.assertGreater(np.linalg.norm(hopping @ volume - volume @ hopping), 0.1)

    def test_connected_triples_include_paths_but_exclude_disconnected_sets(self):
        self.assertEqual(connected_triples(((0, 1), (1, 2), (2, 3))),
                         ((0, 1, 2), (1, 2, 3)))
        self.assertEqual(connected_triples(((0, 1), (2, 3))), ())
        self.assertEqual(len(connected_triples(((0, 1), (1, 2), (2, 3), (0, 3)))), 4)

    def test_counting_matches_independent_magnetic_multiplicities(self):
        for n, k in ((4, 2), (5, 3), (6, 3)):
            all_states = sum(magnetic_singlet_count(s) for s in compositions(2*k, n))
            active_states = sum(magnetic_singlet_count(s)
                                for s in compositions(2*k, n, minimum=1))
            self.assertEqual(all_states, fixed_face_dimension(n, k))
            self.assertEqual(active_states, positive_face_dimension(n, k))

    def test_six_spin_half_volume_matches_analytic_singlet_identity(self):
        spins = (1,) * 6
        occupations, dots, volume, basis, checks = canonical_operators(spins)
        self.assertEqual(len(singlet_paths(spins)), 5)
        self.assertLess(closure_residual(occupations, basis), 1e-13)
        expected = GAMMA**1.5 * math.sqrt(math.sqrt(3)/4) * 6*(6**2-4)/12
        np.testing.assert_allclose(volume, expected * np.eye(5), atol=1e-12)
        self.assertLess(max(checks.values()), 1e-12)

    def test_permuted_unequal_spins_have_closed_orthonormal_recoupling(self):
        spins = (2, 0, 1, 1)
        paths = singlet_paths(spins)
        occupations, basis, _ = sequential_basis(spins, paths, occupation_basis(tuple(sorted(spins))))
        np.testing.assert_allclose(basis.conj().T @ basis, np.eye(len(paths)), atol=1e-13)
        self.assertLess(closure_residual(occupations, basis), 1e-13)

    def test_gibbs_limits_and_energy_shift(self):
        energies = np.array([-2., -2., 3.])
        weights, log_z = thermal_weights(energies, 0.)
        np.testing.assert_allclose(weights, 1/3)
        self.assertAlmostEqual(log_z, math.log(3))
        weights, _ = thermal_weights(energies, math.inf)
        np.testing.assert_array_equal(weights, [0.5, 0.5, 0.])
        a, za = thermal_weights(energies, 10.)
        b, zb = thermal_weights(energies + 1e3, 10.)
        np.testing.assert_array_equal(a, b)
        self.assertAlmostEqual(zb - za, -1e4)

    def test_tfd_entropy_and_imaginary_observable_convention(self):
        probabilities = np.array([0.5, 0.5])
        self.assertAlmostEqual(entropy(probabilities), math.log(2))
        self.assertAlmostEqual(correlator(probabilities, np.array([0, 1]),
                                         np.array([1, 0]), np.array([-1j, 1j])), -1.)

    def test_power_fit_and_legacy_return_contracts(self):
        import t5b_perturbation as t5b
        import t5e_fit as t5e
        import t7b_tfd as t7b
        import t7e_complex_tfd as t7e
        x = np.array([1., 2., 4., 8.])
        y = 3*x**0.5
        result = fit_power(x, y)
        self.assertAlmostEqual(result['alpha'], 0.5)
        self.assertAlmostEqual(result['prefactor'], 3.)
        self.assertAlmostEqual(result['r2'], 1.)
        np.testing.assert_allclose(result['local_slopes'], 0.5, atol=1e-14)
        self.assertEqual(t7b.fit_power(x, y), result)
        self.assertEqual(t7e.fit_power(x, y), result)
        self.assertEqual(t5e.loglog_fit(x, y), {**result, 'n_points': 4})
        self.assertEqual(t5b.loglog_fit(x, y),
                         (result['alpha'], result['prefactor'], result['r2']))


if __name__ == '__main__':
    unittest.main()

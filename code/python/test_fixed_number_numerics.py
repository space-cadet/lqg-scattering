"""Independent spin checks for full fixed-number Hamiltonian numerics."""
import itertools
import math
import unittest

import numpy as np
from scipy.sparse import issparse
from scipy.sparse.linalg import expm_multiply

from lqg_scattering.fixed_k import fixed_number_basis, occupation_index
from lqg_scattering.hamiltonian import (
    assemble_hamiltonian, build_fixed_k, build_fixed_number_model,
)
from lqg_scattering.intertwiners import fixed_area_state
from lqg_scattering.total_spin import (
    closure_diagnostics, spin_sector_probabilities, total_spin_operators,
)


def ket(model, occupation):
    vector = np.zeros(len(model['occupations']), complex)
    vector[model['index'][occupation]] = 1.
    return vector


def spin_operators(model):
    return total_spin_operators(model['occupations'], model['index'],
                                model['metadata']['available_sites'])


class FixedNumberNumericsTests(unittest.TestCase):
    def test_boson_hopping_matches_the_two_particle_dimer(self):
        model = build_fixed_number_model(2, 2, [(1, 0)])
        self.assertEqual(len(model['occupations']), math.comb(5, 3))
        h = assemble_hamiltonian(model, t=2., U=3.)
        self.assertTrue(issparse(h))
        a = model['index'][(2, 0, 0, 0)]
        b = model['index'][(1, 0, 1, 0)]
        c = model['index'][(0, 0, 2, 0)]
        np.testing.assert_allclose(h[[a, b, c]][:, [a, b, c]].toarray(),
            [[3., -2*math.sqrt(2), 0.], [-2*math.sqrt(2), 0., -2*math.sqrt(2)],
             [0., -2*math.sqrt(2), 3.]], atol=1e-14)

    def test_vacuum_and_one_particle_support(self):
        vacuum = build_fixed_number_model(3, 0, [])
        np.testing.assert_array_equal(assemble_hamiltonian(vacuum, 1., 5.).toarray(), [[0.]])
        readout = closure_diagnostics(np.array([1.]), spin_operators(vacuum))
        self.assertEqual(readout['total_spin_probabilities'], {0.: 1.})
        one = build_fixed_number_model(3, 1, [(0, 1), (1, 2)])
        energies = np.linalg.eigvalsh(assemble_hamiltonian(one, 1., 10.).toarray())
        np.testing.assert_allclose(energies, [-math.sqrt(2)]*2 + [0.]*2 + [math.sqrt(2)]*2,
                                   atol=1e-13)

    def test_single_face_has_definite_nonzero_total_spin(self):
        model = build_fixed_number_model(4, 3, [(0, 1)])
        result = closure_diagnostics(ket(model, (3, 0, 0, 0, 0, 0, 0, 0)), spin_operators(model))
        self.assertAlmostEqual(result['mean_total_spin_squared'], 15/4)
        self.assertAlmostEqual(result['mean_total_spin_vector']['z'], 1.5)
        self.assertAlmostEqual(result['total_spin_probabilities'][1.5], 1.)
        self.assertEqual(result['singlet_weight'], 0.)

    def test_zero_magnetization_does_not_imply_closure(self):
        model = build_fixed_number_model(2, 2, [(0, 1)])
        vector = ket(model, (1, 0, 0, 1))
        result = closure_diagnostics(vector, spin_operators(model))
        np.testing.assert_allclose(list(result['mean_total_spin_vector'].values()), 0., atol=1e-14)
        self.assertAlmostEqual(result['mean_total_spin_squared'], 1.)
        self.assertAlmostEqual(result['singlet_weight'], .5)
        self.assertAlmostEqual(result['total_spin_probabilities'][1.], .5)

    def test_singlet_triplet_and_mixed_state(self):
        model = build_fixed_number_model(2, 2, [(0, 1)])
        operators = spin_operators(model)
        a, b = ket(model, (1, 0, 0, 1)), ket(model, (0, 1, 1, 0))
        singlet, triplet = (a-b)/math.sqrt(2), (a+b)/math.sqrt(2)
        self.assertAlmostEqual(closure_diagnostics(singlet, operators)['singlet_weight'], 1.)
        self.assertAlmostEqual(closure_diagnostics(triplet, operators)['mean_total_spin_squared'], 2.)
        rho = .25*np.outer(singlet, singlet.conj()) + .75*np.outer(triplet, triplet.conj())
        result = closure_diagnostics(rho, operators)
        self.assertAlmostEqual(result['singlet_weight'], .25)
        self.assertAlmostEqual(result['mean_total_spin_squared'], 1.5)
        self.assertAlmostEqual(result['norm_or_trace'], 1.)

    def test_traced_face_can_have_zero_mean_spin_and_no_singlet_weight(self):
        # Tracing one spin-1/2 out of a two-face singlet gives I/2.
        model = build_fixed_number_model(1, 1, [])
        result = closure_diagnostics(np.eye(2)/2, spin_operators(model))
        np.testing.assert_allclose(list(result['mean_total_spin_vector'].values()), 0., atol=1e-14)
        self.assertAlmostEqual(result['mean_total_spin_squared'], .75)
        self.assertEqual(result['singlet_weight'], 0.)

    def test_full_hamiltonian_and_fl_state_match_singlet_model(self):
        full = build_fixed_number_model(4, 4, itertools.combinations(range(4), 2))
        singlet = build_fixed_k(2)
        embedding = np.zeros((len(full['occupations']), singlet['basis'].shape[1]), complex)
        for row, occupation in enumerate(singlet['occupations_m0']):
            embedding[full['index'][occupation]] = singlet['basis'][row]
        h = assemble_hamiltonian(full, 1., 5.)
        expected = -sum(singlet['bonds'].values()) + 5*singlet['onsite']
        np.testing.assert_allclose(embedding.conj().T @ h @ embedding, expected, atol=1e-12)
        np.testing.assert_allclose(h @ embedding, embedding @ expected, atol=1e-12)
        _, state = fixed_area_state(2)
        vector = np.array([state.get(tuple(row), 0j) for row in full['occupations']])
        result = closure_diagnostics(vector, spin_operators(full))
        self.assertAlmostEqual(result['singlet_weight'], 1.)
        self.assertLess(abs(result['mean_total_spin_squared']), 1e-12)

    def test_su2_algebra_and_spin_conservation_under_hopping(self):
        model = build_fixed_number_model(3, 3, [(0, 1), (1, 2)])
        operators = spin_operators(model)
        plus, minus, z = [operators[name] for name in ('plus', 'minus', 'z')]
        np.testing.assert_allclose((plus@minus-minus@plus-2*z).toarray(), 0., atol=1e-13)
        h = assemble_hamiltonian(model, 1.2, 2.3)
        for name in ('x', 'y', 'z', 'squared'):
            op = operators[name]
            np.testing.assert_allclose((h@op-op@h).toarray(), 0., atol=1e-12)
        initial = (ket(model, (2, 0, 0, 1, 0, 0)) + 1j*ket(model, (1, 0, 0, 1, 1, 0)))/math.sqrt(2)
        before = spin_sector_probabilities(initial, operators)
        evolved = expm_multiply(-.7j*h, initial)
        self.assertAlmostEqual(float(np.vdot(evolved, evolved).real), 1.)
        after = spin_sector_probabilities(evolved, operators)
        np.testing.assert_allclose(list(before.values()), list(after.values()), atol=1e-12)

    def test_invalid_states_graphs_and_dense_block_limit_fail_explicitly(self):
        for edges in ([(0, 0)], [(0, 2)], [(0, 1), (1, 0)]):
            with self.assertRaises(ValueError):
                build_fixed_number_model(2, 2, edges)
        model = build_fixed_number_model(2, 2, [(0, 1)])
        operators = spin_operators(model)
        vector = ket(model, (1, 0, 0, 1))
        with self.assertRaises(ValueError):
            spin_sector_probabilities(vector, operators, max_block_dimension=1)
        with self.assertRaises(ValueError):
            closure_diagnostics(2*vector, operators)
        invalid = np.eye(len(vector))/len(vector)
        invalid[0, 0], invalid[1, 1] = -.1, .1+2/len(vector)
        with self.assertRaises(ValueError):
            closure_diagnostics(invalid, operators)
        with self.assertRaises(ValueError):
            total_spin_operators(model['occupations'][:-1], model['index'], 2)

    def test_occupation_lookup_does_not_wrap_at_256(self):
        occupations, index = fixed_number_basis(1, 256)
        self.assertEqual(len(index), len(occupations))
        self.assertNotEqual(occupation_index(index, (256, 0)), occupation_index(index, (0, 256)))


if __name__ == '__main__':
    unittest.main()

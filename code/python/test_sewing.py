import unittest
import numpy as np
from sympy.physics.wigner import wigner_6j
from lqg_scattering.sewing import triangle_tensor, singlet_metric, contract_network, trivalent_graph_edges
from sewing_probes import TET_FACES, PRISM_FACES


class SewingTests(unittest.TestCase):
    def test_triangle_is_spin_one_singlet(self):
        tensor, spins = triangle_tensor()
        self.assertEqual(spins, (2, 2, 2))
        z = np.diag([-1., 0., 1.])
        plus = np.zeros((3, 3))
        plus[1, 0] = plus[2, 1] = np.sqrt(2)
        for op in (z, plus, plus.T):
            total = sum(np.moveaxis(np.tensordot(op, tensor, axes=(1, axis)), 0, axis)
                        for axis in range(3))
            self.assertLess(np.linalg.norm(total), 1e-12)
        _, unequal = triangle_tensor((2, 1, 1))
        self.assertEqual(unequal, (3, 3, 2))

    def test_invariant_pair_normalization_and_orientation(self):
        for n in (1, 2, 3):
            metric = singlet_metric(n)
            np.testing.assert_allclose(metric.T, (-1)**n*metric)
            self.assertAlmostEqual(np.linalg.norm(metric), 1.)

    def test_tetrahedron_agrees_with_wigner_six_j(self):
        tensor, _ = triangle_tensor()
        result, legs = contract_network([tensor]*4, trivalent_graph_edges(TET_FACES))
        self.assertEqual(legs, ())
        self.assertAlmostEqual(abs(float(result)), abs(float(wigner_6j(1,1,1,1,1,1)))/3**3)

    def test_patch_gluing_matches_direct_prism(self):
        tensor, _ = triangle_tensor()
        patch, _ = contract_network([tensor]*3, trivalent_graph_edges(TET_FACES[1:]))
        sewn, _ = contract_network([patch]*2, tuple(((0,i),(1,i)) for i in range(3)))
        direct, _ = contract_network([tensor]*6, trivalent_graph_edges(PRISM_FACES))
        self.assertAlmostEqual(float(sewn), float(direct), places=14)

    def test_link_rotation_retains_nonconstant_network_function(self):
        tensor, _ = triangle_tensor()
        edges = trivalent_graph_edges(TET_FACES)
        identity, _ = contract_network([tensor]*4, edges)
        transports = [np.eye(3, dtype=complex) for _ in edges]
        transports[0] = np.diag(np.exp(-1j*.7*np.array([-1.,0.,1.])))
        rotated, _ = contract_network([tensor]*4, edges, transports)
        self.assertGreater(abs(rotated-identity), 1e-5)

    def test_reject_double_sewing_and_mismatched_spins(self):
        with self.assertRaises(ValueError):
            contract_network([np.zeros((2,)),np.zeros((3,))], [((0,0),(1,0))])
        with self.assertRaises(ValueError):
            contract_network([np.zeros((2,)),np.zeros((2,))], [((0,0),(1,0))]*2)


if __name__ == '__main__':
    unittest.main()

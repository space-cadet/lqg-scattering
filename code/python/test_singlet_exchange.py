"""Independent oscillator and analytic controls for the T9a exchange model."""
import unittest
import numpy as np
from scipy.linalg import expm
from lqg_scattering.singlet_exchange import (
    PAIRS, build_exchange_space, exchange_hamiltonian, fl_product, readout)
from lqg_scattering.intertwiners import fixed_area_state


class ExchangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.one = build_exchange_space(1)
        cls.two = build_exchange_space(2)

    def test_one_unit_exact_rabi(self):
        h, current, _ = exchange_hamiltonian(self.one, coupling=.7+.2j)
        seed = fl_product(self.one, 1)
        for t in (0., .1, .8, 1.7):
            state = expm(-1j*t*h.toarray()) @ seed
            expected = np.cos(2*abs(.7+.2j)*t)**2
            self.assertAlmostEqual(readout(self.one, state)['area_left'], expected, places=12)
        self.assertLess(np.max(abs(h.toarray()-h.toarray().conj().T)), 1e-13)
        a = np.diag(self.one['area_left'])
        np.testing.assert_allclose(current.toarray(), 1j*(h.toarray()@a-a@h.toarray()), atol=1e-13)

    def test_oscillator_exchange_without_projection(self):
        space = self.two
        seed = fl_product(space, 1)
        g = .3+.4j
        h, _, _ = exchange_hamiltonian(space, coupling=g)
        # Rebuild the joint occupation ket directly from FL dictionaries.
        _, local = fixed_area_state(1)
        raw = {(l, r): al*ar for l, al in local.items() for r, ar in local.items()}
        result = {}
        for (left, right), amplitude in raw.items():
            for i, j in PAIRS:
                for swap, coefficient in ((False, g), (True, g.conjugate())):
                    receiver, donor = (right, left) if swap else (left, right)
                    for da, db, ds in ((2*i, 2*j+1, 1), (2*j, 2*i+1, -1)):
                        if donor[da] == 0 or donor[db] == 0:
                            continue
                        d = list(donor)
                        annihilation = ds*np.sqrt(d[da]*d[db])
                        d[da] -= 1; d[db] -= 1
                        for ca, cb, cs in ((2*i, 2*j+1, 1), (2*j, 2*i+1, -1)):
                            c = list(receiver)
                            creation = cs*np.sqrt((c[ca]+1)*(c[cb]+1))
                            c[ca] += 1; c[cb] += 1
                            key = (tuple(d), tuple(c)) if swap else (tuple(c), tuple(d))
                            result[key] = result.get(key, 0j)+coefficient*amplitude*annihilation*creation
        for k, section in enumerate(space['sectors']):
            lm, rm = space['local'][k], space['local'][2-k]
            joint = np.array([[result.get((tuple(l), tuple(r)), 0j)
                               for r in rm['occupations_m0']] for l in lm['occupations_m0']])
            projected = lm['basis'].conj().T @ joint @ rm['basis'].conj()
            np.testing.assert_allclose((h @ seed)[section], projected.ravel(), atol=1e-12)
            np.testing.assert_allclose(joint, lm['basis'] @ projected @ rm['basis'].T, atol=1e-12)

    def test_conservation_current_entropy_and_no_exchange(self):
        s = self.two
        h, current, forward = exchange_hamiltonian(s, coupling=.6, epsilon_left=.2, repulsion_left=1.)
        seed = fl_product(s, 1)
        initial = readout(s, seed, current, forward)
        self.assertAlmostEqual(initial['current_left'], 0., places=13)
        self.assertAlmostEqual(initial['entropy_nats'], 0., places=12)
        t, step = .35, 1e-5
        state = expm(-1j*t*h.toarray()) @ seed
        plus = expm(-1j*(t+step)*h.toarray()) @ seed
        minus = expm(-1j*(t-step)*h.toarray()) @ seed
        derivative = (readout(s, plus)['area_left']-readout(s, minus)['area_left'])/(2*step)
        self.assertAlmostEqual(derivative, readout(s, state, current)['current_left'], places=8)
        self.assertLess(max(s['residuals'].values()), 1e-12)
        h0, _, _ = exchange_hamiltonian(s, coupling=0., repulsion_left=2.)
        self.assertAlmostEqual(abs(np.vdot(seed, expm(-1j*h0.toarray()) @ seed)), 1., places=12)
        self.assertEqual(build_exchange_space(0)['dimension'], 1)

    def test_invalid_inputs(self):
        for invalid in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                build_exchange_space(invalid)
        with self.assertRaises(ValueError):
            exchange_hamiltonian(self.one, coupling=np.nan)
        with self.assertRaises(ValueError):
            fl_product(self.one, 2)


if __name__ == '__main__':
    unittest.main()

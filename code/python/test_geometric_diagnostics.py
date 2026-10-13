"""Analytic controls for the conditional quantum-angle readouts."""
import unittest
import numpy as np
from lqg_scattering.geometric_diagnostics import condition,moments,summarize,angular_operators
from lqg_scattering.hamiltonian import build_fixed_k


class GeometricDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=build_fixed_k(2)

    def test_two_singlet_pairs(self):
        model=self.model
        idx=next(i for i,row in enumerate(model['labels'])
                 if tuple(row[f'n{j}'] for j in range(4))==(1,1,1,1)
                 and row['twice_k_pair']==0)
        ket=np.eye(len(model['labels']))[:,idx]
        rho=np.outer(ket,ket)
        numbers=model['site_spins']
        dots=model['spin_dots'];q=1j*(dots[0,1]@dots[1,2]-dots[1,2]@dots[0,1])
        result=summarize(rho,numbers,dots,sum(model['volume_by_triple'].values()),q)
        # Product of two spin-half singlets: within-pair C=-1 sharply,
        # cross-pair mean zero and <C^2>=1/3.
        np.testing.assert_allclose(result['conditional_angle_means'],[-1,0,0,0,0,-1],atol=1e-13)
        np.testing.assert_allclose(np.diag(result['conditional_angle_covariance']),[0,1/3,1/3,1/3,1/3,0],atol=1e-13)

    def test_projection_keeps_coherence(self):
        ket=np.array([1,1j,2],complex)/np.sqrt(6)
        rho=np.outer(ket,ket.conj());p,conditioned=condition(rho,[True,True,False])
        self.assertAlmostEqual(p,1/3)
        self.assertAlmostEqual(abs(conditioned[0,1]),.5)
        self.assertIsNone(condition(rho,[False,False,False])[1])
        self.assertIsNone(condition(rho,[True,True,False],min_probability=.4)[1])

    def test_sector_normalization_is_not_ratio_of_means(self):
        numbers=np.array([[1,1],[2,2]])
        dots={(0,1):np.diag([-.75,-2.])}
        _,ops=angular_operators(numbers,dots)
        m,_=moments(np.eye(2)/2,ops)
        self.assertAlmostEqual(m[0],-1.)

    def test_symmetrized_covariance_for_noncommuting_operators(self):
        x=np.array([[0,1],[1,0]],complex);y=np.array([[0,-1j],[1j,0]])
        _,cov=moments(np.diag([1.,0.]),[x,y])
        np.testing.assert_allclose(cov,np.eye(2),atol=1e-14)


if __name__=='__main__': unittest.main()

"""Exact analytic singlet/non-singlet channel-activation benchmarks."""
import unittest
import numpy as np
from scipy.sparse import diags
from lqg_scattering.hamiltonian import build_fixed_number_model
from lqg_scattering.fixed_k import uN_generator
from lqg_scattering.total_spin import total_spin_operators
from t11_face_connectivity import pair_seed,open_seed,singlet_embedding

class FaceConnectivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=build_fixed_number_model(6,6,[(i,(i+1)%6) for i in range(6)])
        cls.occ=cls.model['occupations'];cls.index=cls.model['index']
        cls.spin=total_spin_operators(cls.occ,cls.index,6)
        cls.counts=cls.occ[:,::2]+cls.occ[:,1::2];cls.active=np.sum(cls.counts>0,axis=1)
        cls.closed=pair_seed(6,[(0,3),(0,3),(1,2)],cls.index)
        cls.open=open_seed([2,1,1,2,0,0],cls.index,True)
        cls.casimir=diags(np.sum(cls.counts*(cls.counts+2),axis=1)/4)
        cls.h=cls.casimir-sum(cls.model['bonds'].values())

    def test_pair_polynomial_and_exact_support(self):
        # (a0†b3†-b0†a3†)^2 (a1†b2†-b1†a2†), normalized Fock factors.
        expected=np.zeros(len(self.occ),complex)
        for r in range(3):
            for q in range(2):
                state=[2-r,r,1-q,q,q,1-q,r,2-r,0,0,0,0]
                expected[self.index[tuple(state)]]=(-1)**(r+q)/np.sqrt(6)
        np.testing.assert_allclose(self.closed,expected,atol=1e-15)
        self.assertAlmostEqual(np.sum(abs(self.closed[self.active==4])**2),1.)
        self.assertLess(np.linalg.norm(self.spin['squared']@self.closed),1e-14)

    def test_explicit_directed_chain(self):
        z=np.zeros((6,6));z[5,0]=1;e50=uN_generator(self.occ,self.index,z,6)
        z=np.zeros((6,6));z[4,3]=1;e43=uN_generator(self.occ,self.index,z,6)
        for psi,j in [(self.closed,0),(self.open,3)]:
            target5=e50@psi/np.sqrt(2);target6=e43@target5/np.sqrt(2)
            self.assertAlmostEqual(np.linalg.norm(target5),1.)
            self.assertAlmostEqual(np.linalg.norm(target6),1.)
            self.assertAlmostEqual(np.vdot(target5,self.h@psi).real,-np.sqrt(2))
            self.assertAlmostEqual(np.vdot(target6,self.h@target5).real,-np.sqrt(2))
            self.assertLess(np.linalg.norm(self.spin['squared']@target6-j*(j+1)*target6),1e-14)
            self.assertLess(np.linalg.norm(target5[self.active!=5]),1e-14)
            self.assertLess(np.linalg.norm(target6[self.active!=6]),1e-14)

    def test_actual_second_power_and_controls(self):
        for psi in [self.closed,self.open]:
            hp=self.h@psi
            self.assertAlmostEqual(np.linalg.norm(hp[self.active==5]),2.)
            self.assertEqual(np.linalg.norm(hp[self.active==6]),0.)
            self.assertAlmostEqual(np.linalg.norm((self.h@hp)[self.active==6]),4.)
            self.assertEqual(np.linalg.norm((self.casimir@psi)[self.active==5]),0.)

    def test_nonclosure_despite_zero_spin_mean(self):
        for axis in ['x','y','z']:self.assertAlmostEqual(np.vdot(self.open,self.spin[axis]@self.open).real,0.)
        self.assertAlmostEqual(np.vdot(self.open,self.spin['squared']@self.open).real,12.)
        self.assertLess(abs(np.vdot(self.closed,self.h@self.open)),1e-14)

    def test_minimum_number_control(self):
        model=build_fixed_number_model(6,4,[])
        n=model['occupations'][:,::2]+model['occupations'][:,1::2]
        self.assertLessEqual(np.max(np.sum(n>0,axis=1)),4)
        b,labels=singlet_embedding(model['occupations'],model['index'],6,2)
        self.assertEqual(b.shape[1],105)
        self.assertTrue(all(label['active']<=4 for label in labels))

if __name__=='__main__': unittest.main()

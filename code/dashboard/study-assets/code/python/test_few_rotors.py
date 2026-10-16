"""Small general-graph rotor invariants and exact pair bounds."""
import unittest
import numpy as np
from lqg_scattering.classical_rotors import evolve_graph
from t11_few_rotors import energies,pair_bound

class FewRotors(unittest.TestCase):
    def test_free_rotor_inertia(self):
        q=np.array([[1.,0,0],[0,1.,0]]);j=np.array([[0.,0,2.],[0,0,0.]])
        t,a,b,_=evolve_graph(q,j,[],0.,inertia=2.,dt=.01,duration=1,sample_interval=.1)
        np.testing.assert_allclose(a[-1,0],[np.cos(1),np.sin(1),0],atol=1e-13)
        np.testing.assert_allclose(b,np.broadcast_to(j,b.shape),atol=1e-13)

    def test_planar_pair_barrier(self):
        for ratio in [1.,10.,100.]:
            q=np.tile([1.,0,0],(2,1));j=np.zeros_like(q);j[0,2]=np.sqrt(2*ratio)
            t,a,b,_=evolve_graph(q,j,[(0,1)],dt=.0005,duration=20,sample_interval=.01)
            kinetic,_,energy=energies(a,b,[(0,1)],1.)
            self.assertLess(abs(kinetic[:,1].max()/ratio-pair_bound(ratio)),.0001)
            self.assertLess(np.max(abs(energy/ratio-1)),2e-6)

    def test_zero_total_J_pair_equal_kinetic(self):
        q=np.tile([1.,0,0],(2,1));j=np.array([[0.,0,2.],[0,0,-2.]])
        _,a,b,_=evolve_graph(q,j,[(0,1)],duration=20,dt=.001,sample_interval=.02)
        np.testing.assert_allclose(np.sum(b[:,0]**2,axis=1),np.sum(b[:,1]**2,axis=1),atol=1e-12)

    def test_duplicate_edges_rejected(self):
        q=np.tile([1.,0,0],(2,1));j=np.zeros_like(q)
        with self.assertRaises(ValueError):evolve_graph(q,j,[(0,1),(1,0)])

if __name__=='__main__':unittest.main()

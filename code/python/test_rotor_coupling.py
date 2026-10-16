"""Physical-unit readouts and explicit-coupling solver cross-checks."""
import unittest
import numpy as np
from lqg_scattering.classical_rotors import initial_state,evolve_graph,evolve_transfer

class Coupling(unittest.TestCase):
    def test_matches_independent_graph_readouts(self):
        q,j=initial_state(8,30,1701);edges=[(i,(i+1)%8) for i in range(8)]
        t,d,qf,jf,dt=evolve_transfer(q,j,coupling=3,inertia=2,dt=.001,duration=2,sample_interval=.1)
        tt,qq,jj,_=evolve_graph(q,j,edges,coupling=3,inertia=2,dt=.001,duration=2,sample_interval=.1)
        kin=np.sum(jj*jj,axis=2)/4
        local=kin.copy()
        for i,k in edges:
            bond=3*(1-np.sum(qq[:,i]*qq[:,k],axis=1));local[:,i]+=bond/2;local[:,k]+=bond/2
        np.testing.assert_allclose(d[:,8:16],local,atol=2e-11)
        np.testing.assert_allclose(d[:,16:],kin,atol=2e-11)
        np.testing.assert_allclose(d[:,4],kin[:,2:].sum(axis=1),atol=2e-11)
        np.testing.assert_allclose(qf,qq[-1],atol=2e-11)

    def test_coupling_inertia_scaling(self):
        q,j=initial_state(8,100,1702);g=5.;inertia=3.;scale=np.sqrt(inertia/g)
        _,d,q1,j1,_=evolve_transfer(q,j,coupling=g,inertia=inertia,dt=.0005*scale,duration=2*scale,sample_interval=.1*scale)
        _,b,q2,j2,_=evolve_transfer(q,j/np.sqrt(inertia*g),dt=.0005,duration=2,sample_interval=.1)
        np.testing.assert_allclose(d[:,0]/g,b[:,0],atol=2e-7)
        np.testing.assert_allclose(q1,q2,atol=2e-7)
        np.testing.assert_allclose(j1/np.sqrt(inertia*g),j2,atol=2e-7)

if __name__=='__main__':unittest.main()

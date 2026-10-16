"""Independent ODE, reversibility, refinement and constrained-ensemble checks."""
import unittest
import numpy as np
from scipy.integrate import solve_ivp
from lqg_scattering.classical_rotors import initial_state,evolve,sample_microcanonical

class Rotors(unittest.TestCase):
    def test_independent_ode_and_order(self):
        q,j=initial_state(8,10,9001);n=len(q)
        def rhs(t,y):
            q,j=y[:3*n].reshape(n,3),y[3*n:].reshape(n,3)
            return np.r_[np.cross(j,q).ravel(),np.cross(q,np.roll(q,1,axis=0)+np.roll(q,-1,axis=0)).ravel()]
        ref=solve_ivp(rhs,[0,2],np.r_[q.ravel(),j.ravel()],method='DOP853',rtol=1e-12,atol=1e-13).y[:,-1]
        errors=[]
        for dt in [.01,.005,.0025,.00125]:
            _,data,a,b,_=evolve(q,j,dt,2)
            errors.append(np.max(abs(np.r_[a.ravel(),b.ravel()]-ref)))
            self.assertLess(data[:,5:8].max(),2e-12)
        self.assertLess(errors[-1],2e-5)
        self.assertTrue(all(3.7<a/b<4.3 for a,b in zip(errors,errors[1:])),errors)

    def test_time_reversal(self):
        q,j=initial_state(8,100,9002)
        _,_,a,b,_=evolve(q,j,.005,10)
        _,_,aa,bb,_=evolve(a,-b,.005,10)
        self.assertLess(np.max(abs(aa-q)),2e-11)
        self.assertLess(np.max(abs(bb+j)),2e-11)

    def test_stationary_state(self):
        q=np.tile([0.,0.,1.],(8,1));j=np.zeros_like(q)
        _,_,a,b,_=evolve(q,j,.01,1)
        np.testing.assert_array_equal(a,q);np.testing.assert_array_equal(b,j)

    def test_microcanonical_constraints(self):
        q,j=initial_state(8,10,9003)
        _,d,_,_,_=evolve(q,j,.01,1)
        samples,accept=sample_microcanonical(q,d[0,0],9004,burn=200,samples=500,thin=2)
        self.assertGreater(accept,0);self.assertLess(accept,1)
        self.assertLess(np.max(abs(samples[:,0]-d[0,0])),2e-12)
        self.assertLess(samples[:,5:8].max(),2e-12)
        self.assertLess(np.max(abs(samples[:,8:].sum(axis=1)-samples[:,0])),2e-12)
        self.assertGreaterEqual(samples[:,8:].min(),0)
        # Exchange symmetry requires hot-pair mean 2/N; independent momentum
        # refreshes give a useful broad statistical check, not a mixing proof.
        self.assertLess(abs(samples[:,2].mean()-.25),.06)

if __name__=='__main__':unittest.main()

"""Independent small-system checks for fixed-momentum planar rotors."""
import unittest
from itertools import product
import numpy as np
from scipy.linalg import expm
from lqg_scattering.planar_rotors import momentum_basis,hamiltonian,momentum_state,evolve_readouts,classical_ensemble

class PlanarRotors(unittest.TestCase):
    def test_sector_and_hermiticity(self):
        b=momentum_basis(4,2)
        self.assertTrue(np.all(b.sum(axis=1)==0))
        self.assertEqual(len(b),sum(sum(s)==0 for s in product(range(-2,3),repeat=4)))
        h=hamiltonian(b,[(0,1),(1,2),(2,3),(3,0)])
        np.testing.assert_allclose(h.toarray(),h.toarray().T)

    def test_independent_angle_grid_projection(self):
        # Fourier quadrature of cos interactions, independent of shift assembly.
        b=momentum_basis(2,2,total=1); angles=np.arange(13)*2*np.pi/13
        q=np.array(list(product(angles,repeat=2)))
        fourier=np.exp(1j*q@b.T)/np.sqrt(len(q))
        potential=fourier.conj().T@((1-np.cos(q[:,0]-q[:,1]))[:,None]*fourier)
        reference=potential+np.diag(.7**2*np.sum(b*b,axis=1)/2)
        np.testing.assert_allclose(hamiltonian(b,[(0,1)],epsilon=.7).toarray(),reference,atol=2e-15)

    def test_dense_propagation_and_entropy(self):
        b=momentum_basis(3,2); h=hamiltonian(b,[(0,1),(1,2),(2,0)])
        psi=momentum_state(b,[1,-1,0]); times=np.linspace(0,1,5)
        rows=evolve_readouts(h,b,psi,times)
        end=expm(-1j*h.toarray())@psi
        np.testing.assert_allclose(rows[-1]['kinetic'],abs(end)**2@(b*b/2),atol=1e-13)
        # Independent partial trace using full tensor-product embedding.
        tensor=np.zeros((5,5,5),complex)
        for state,a in zip(b,end): tensor[tuple(state+2)]=a
        mat=tensor.reshape(5,-1); eigen=np.linalg.eigvalsh(mat@mat.conj().T)
        positive=eigen[eigen>1e-14]
        self.assertAlmostEqual(rows[-1]['entropy'][0],-sum(positive*np.log(positive)),places=12)
        self.assertGreater(rows[-1]['kinetic'][2],0)

    def test_free_and_zero_momentum_pair(self):
        b=momentum_basis(2,4); psi=momentum_state(b,[2,-2]); times=np.linspace(0,2,9)
        for coupling in [0.,1.]:
            rows=evolve_readouts(hamiltonian(b,[(0,1)],coupling=coupling),b,psi,times)
            for row in rows:
                self.assertAlmostEqual(*row['kinetic'],places=12)
                if coupling==0: self.assertAlmostEqual(row['return_probability'],1.,places=12)

    def test_classical_against_independent_ode(self):
        from scipy.integrate import solve_ivp
        edges=[(0,1),(1,2),(2,3),(3,0)]
        angles=np.random.default_rng(17).uniform(-np.pi,np.pi,(2,4))
        p=np.tile([2.,-2.,0.,0.],(2,1)); times=np.linspace(0,1,6)
        rows=classical_ensemble(angles,p,edges,times,dt=.0005)
        kin=[]
        for q0,p0 in zip(angles,p):
            def rhs(t,y):
                q=y[:4]; force=np.zeros(4)
                for i,j in edges:
                    force[i]-=np.sin(q[i]-q[j]); force[j]+=np.sin(q[i]-q[j])
                return np.r_[y[4:],force]
            sol=solve_ivp(rhs,[0,1],np.r_[q0,p0],method='DOP853',rtol=1e-12,atol=1e-13,t_eval=times)
            kin.append(sol.y[4:].T**2/2)
        np.testing.assert_allclose([r['kinetic'] for r in rows],np.mean(kin,axis=0),atol=3e-7)

    def test_classical_symmetry_and_free(self):
        theta=np.zeros((2,3)); p=np.tile([2.,-2.,0.],(2,1)); times=np.linspace(0,2,9)
        for edges in [[],[(0,1),(1,2),(2,0)]]:
            rows=classical_ensemble(theta,p,edges,times)
            self.assertEqual(rows[-1]['kinetic'][2],0.)
            self.assertLess(rows[-1]['max_total_momentum_error'],1e-12)

if __name__=='__main__': unittest.main()

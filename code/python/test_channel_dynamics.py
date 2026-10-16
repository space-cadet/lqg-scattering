"""Sparse channel construction and quantum geometry against independent controls."""
import unittest
import numpy as np
from scipy.sparse import diags
from scipy.linalg import expm
from lqg_scattering.channel_dynamics import build_basis,build_hopping,initial_state,build_geometry,readouts,geometry_readout
from lqg_scattering.hamiltonian import build_fixed_number_model
from t11_face_connectivity import singlet_embedding
from lqg_scattering.singlets import root_abs

class ChannelDynamics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=build_basis(5,2)
        cls.hop,cls.leak=build_hopping(cls.model,[(i,(i+1)%5) for i in range(5)],.5)
        cls.ops,cls.pairs,cls.checks=build_geometry(cls.model)

    def test_full_space_projection(self):
        full=build_fixed_number_model(5,4,[(i,(i+1)%5) for i in range(5)])
        b,labels=singlet_embedding(full['occupations'],full['index'],5,2)
        expected=.5*(b.conj().T@sum(full['bonds'].values())@b).toarray()
        np.testing.assert_allclose(self.hop.toarray(),expected,atol=1e-14)
        self.assertLess(max(self.model['validation'].values()),1e-13)
        self.assertLess(self.leak,1e-13)

    def test_local_energy_partition(self):
        h,leak,local=build_hopping(self.model,[(i,(i+1)%5) for i in range(5)],.5,local=True)
        np.testing.assert_allclose(sum(local).toarray(),h.toarray(),atol=1e-14)

    def test_geometry_and_closure(self):
        self.assertLess(max(self.checks.values()),1e-12)
        v=self.ops['volume'].toarray();self.assertGreaterEqual(np.linalg.eigvalsh(v).min(),-1e-13)
        np.testing.assert_allclose(v,v.conj().T,atol=1e-14)
        # Three or fewer active legs in a closed singlet have zero triple volume.
        mask=np.sum(self.model['numbers']>0,axis=1)<=3
        np.testing.assert_allclose(v[:,mask],0,atol=1e-13)

    def test_four_spin_half_rs_volume(self):
        from lqg_scattering.singlets import GAMMA
        mask=np.all(self.model['numbers']==[1,1,1,1,0],axis=1)
        small=self.ops['volume'][mask][:,mask].toarray()
        np.testing.assert_allclose(small,np.eye(2)*(2*3**.25*GAMMA**1.5),atol=1e-13)

    def test_singlet_entropy_against_partial_trace(self):
        seed,_,_=initial_state(self.model,sharp=False)
        state=expm(1j*self.hop.toarray()*.7)@seed
        rows=readouts(state[None,:],self.model,seed,-self.hop)
        mag=self.model['embedding']@state
        for site in [0,4]:
            # Independent full local-Fock partial trace, retaining all n sectors.
            groups={};local={}
            for occ,a in zip(self.model['occupations'],mag):
                left=tuple(occ[2*site:2*site+2]);rest=tuple(np.r_[occ[:2*site],occ[2*site+2:]])
                local.setdefault(left,len(local));groups.setdefault(rest,{})[left]=a
            rho=np.zeros((len(local),len(local)),complex)
            for amplitudes in groups.values():
                v=np.zeros(len(local),complex)
                for key,a in amplitudes.items():v[local[key]]=a
                rho+=np.outer(v,v.conj())
            eigen=np.linalg.eigvalsh(rho);eigen=eigen[eigen>1e-14]
            self.assertAlmostEqual(rows['entropy'][0,site],-sum(eigen*np.log(eigen)),places=12)

    def test_sharp_projection_and_no_hopping(self):
        model=build_basis(4,4);psi,_,p=initial_state(model,sharp=True)
        self.assertGreater(p,0);n=model['numbers'];support=abs(psi)>1e-12
        self.assertTrue(np.all(n[support]==2))
        diagonal=np.sum(n*(n+2),axis=1)/4
        final=psi*np.exp(-1j*diagonal*2)
        self.assertAlmostEqual(abs(np.vdot(psi,final))**2,1.)

if __name__=='__main__':unittest.main()

"""Independent saved-array audits, including direct endpoint Hamiltonians."""
import json
import numpy as np
from t11_classical_rotors import OUT


def main():
    residuals={};count=0
    def check(name,x,tol):
        nonlocal count
        value=float(np.max(abs(x)));residuals[name]=max(residuals.get(name,0.),value);count+=np.size(x)
        assert value<=tol,(name,value,tol)
    archives=sorted(p for p in OUT.glob('N*_S*.npz') if not p.stem.endswith('_refined'))
    assert len(archives)==72
    for path in archives:
        ar=np.load(path);d=ar['readouts'];n=d.shape[1]-8;e=d[0,0]
        check('local_energy_sum',d[:,8:].sum(axis=1)-d[:,0],2e-10)
        check('negative_local_energy',np.minimum(d[:,8:],0),2e-12)
        check('concentration_formula',d[:,3]-np.sum((d[:,8:]/d[:,0,None])**2,axis=1),2e-12)
        check('hot_pair_formula',d[:,2]-d[:,8:10].sum(axis=1)/d[:,0],2e-12)
        for prefix,idx in [('initial',0),('final',-1)]:
            q=ar[prefix+'_q'];j=ar[prefix+'_J']
            check('orientation_norm',np.sum(q*q,axis=1)-1,1e-10)
            check('tangency',np.sum(q*j,axis=1),1e-10)
            check('total_J',j.sum(axis=0),1e-9)
            kinetic=np.sum(j*j,axis=1)/2
            bond=1-np.sum(q*np.roll(q,-1,axis=0),axis=1)
            local=kinetic+(bond+np.roll(bond,1))/2
            check('endpoint_energy',local.sum()-d[idx,0],2e-10)
            check('endpoint_local_energies',local-d[idx,8:],2e-10)
        mc=ar['microcanonical_readouts']
        check('microcanonical_energy',mc[:,:,0]/e-1,1e-12)
        check('microcanonical_local_sum',mc[:,:,8:].sum(axis=2)-mc[:,:,0],2e-10)
        check('microcanonical_constraints',mc[:,:,5:8],1e-10)
    result=dict(archives=len(archives),scalar_comparisons=int(count),maximum_residuals=residuals)
    (OUT/'independent-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()

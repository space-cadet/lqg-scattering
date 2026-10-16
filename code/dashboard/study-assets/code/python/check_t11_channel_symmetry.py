"""Check the receiver/original permutation selection behind absent all-eight weight.

Added after inspecting the primary runs; diagnostic, not a predefined scan.
"""
from itertools import permutations
from pathlib import Path
import json
import numpy as np
from lqg_scattering.channel_dynamics import build_basis,initial_state
ROOT=Path(__file__).resolve().parents[2]

def symmetrize(v,sites,occ,index):
    isvector=v.ndim==1
    if isvector:v=v[:,None]
    out=np.zeros_like(v);support=np.flatnonzero(np.any(abs(v)>1e-14,axis=1))
    orders=list(permutations(sites))
    for perm in orders:
        for row in support:
            target=occ[row].copy()
            for dest,source in zip(sites,perm):target[2*dest:2*dest+2]=occ[row,2*source:2*source+2]
            out[index[tuple(target)]]+=v[row]/len(orders)
    return out[:,0] if isvector else out


def main():
    model=build_basis(8,4);b=model['embedding'];occ=model['occupations'];index=model['index']
    inputs={};checks={}
    for name,phi in [('regular',90),('deformed',30)]:
        psi,_,_=initial_state(model,phi,True);mag=b@psi
        old=symmetrize(mag,list(range(4)),occ,index)
        receiver=symmetrize(mag,list(range(4,8)),occ,index)
        inputs[name]=dict(original_channel_symmetric_weight=float(np.vdot(old,old).real),receiver_symmetric_residual=float(np.linalg.norm(receiver-mag)))
    mask=np.all(model['numbers']==1,axis=1);target=b[:,mask].toarray()
    received=symmetrize(target,list(range(4,8)),occ,index)
    both=symmetrize(received,list(range(4)),occ,index)
    checks['all_eight_receiver_symmetric_implies_original_symmetric']=float(np.max(abs(received-both)))
    projected=b[:,mask].conj().T@received
    checks['receiver_symmetric_all_eight_rank']=int(np.linalg.matrix_rank(projected,tol=1e-10))
    assert inputs['regular']['original_channel_symmetric_weight']<1e-25
    assert max(v['receiver_symmetric_residual'] for v in inputs.values())<2e-10
    assert checks['all_eight_receiver_symmetric_implies_original_symmetric']<2e-10
    assert checks['receiver_symmetric_all_eight_rank']==1
    result=dict(post_run_diagnostic=True,inputs=inputs,checks=checks,
        interpretation='Complete-graph H commutes with independent permutations of original and receiver groups. Initial receivers are symmetric. Within the all-eight singlet target, receiver symmetry requires original-group symmetry. The regular sharp source has zero weight in the latter; the deformed source does not.')
    path=ROOT/'results/t11-geometric-redistribution/symmetry-control.json';path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()

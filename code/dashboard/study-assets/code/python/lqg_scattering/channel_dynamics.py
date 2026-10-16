"""Sparse singlet-channel dynamics with small local-count geometry blocks.

Global bases/matrices stay sparse. Dense spectral functions are restricted to
small magnetic or singlet blocks with fixed local spins; no full density matrix.
"""
from functools import lru_cache
from itertools import combinations
import math
import numpy as np
from scipy.sparse import coo_matrix,csr_matrix,diags
from .labels import compositions,fixed_face_dimension
from .singlets import occupation_basis,singlet_paths,cg,root_abs,GAMMA
from .hamiltonian import hopping_matrix
from .coherent_states import su2_ops
from .positivity import dot_operator
from .singlets import action_matrix
from .intertwiners import fixed_area_state
from .tetrahedra import closed_equal_area_normals
from .spinors import spinors_from_normals


@lru_cache(maxsize=None)
def cached_cg(*args):return cg(*args)


def coupled_block(spins,paths,canonical):
    order=sorted(range(len(spins)),key=lambda i:(spins[i],i))
    inverse=[order.index(i) for i in range(len(spins))]
    occ=[tuple(v for i in inverse for v in o[2*i:2*i+2]) for o in canonical]
    b=np.zeros((len(occ),len(paths)),complex)
    for row,o in enumerate(occ):
        magnetic=[o[2*i]-o[2*i+1] for i in range(len(spins))]
        for col,path in enumerate(paths):
            a=1.;m=magnetic[0]
            for i in range(1,len(spins)):
                a*=cached_cg(path[i-1],spins[i],path[i],m,magnetic[i],m+magnetic[i])
                m+=magnetic[i]
                if not a:break
            b[row,col]=a
    return occ,b,inverse


def build_basis(l,k):
    occ=np.array([tuple(v for pair in zip(a,b) for v in pair) for a in compositions(k,l) for b in compositions(k,l)],int)
    index={tuple(o):r for r,o in enumerate(occ)}
    rr=[];cc=[];vv=[];blocks=[];numbers=[];start=0;gram=0.
    for spins in compositions(2*k,l):
        paths=singlet_paths(spins)
        if not paths:continue
        canonical=occupation_basis(tuple(sorted(spins)))
        local,b,inverse=coupled_block(spins,paths,canonical)
        rows=np.array([index[o] for o in local]);r,c=np.nonzero(b)
        rr.extend(rows[r]);cc.extend(start+c);vv.extend(b[r,c])
        gram=max(gram,float(np.max(abs(b.conj().T@b-np.eye(len(paths))))))
        blocks.append((start,start+len(paths),spins,b,inverse))
        numbers.extend([spins]*len(paths));start+=len(paths)
    embedding=coo_matrix((vv,(rr,cc)),shape=(len(occ),start)).tocsr()
    assert start==fixed_face_dimension(l,k)
    # J+ maps M=0 to M=1. Independent ladder application checks exact closure.
    target={};r=[];c=[];v=[]
    for col,o in enumerate(occ):
        for site in range(l):
            a,bb=o[2*site:2*site+2]
            if bb:
                changed=o.copy();changed[2*site]+=1;changed[2*site+1]-=1;key=tuple(changed)
                row=target.setdefault(key,len(target));r.append(row);c.append(col);v.append(math.sqrt((a+1)*bb))
    raising=coo_matrix((v,(r,c)),shape=(len(target),len(occ))).tocsr()
    leak=raising@embedding
    closure=float(np.max(abs(leak.data),initial=0))
    return dict(L=l,K=k,occupations=occ,index=index,embedding=embedding,blocks=blocks,
                numbers=np.array(numbers),validation=dict(gram=gram,closure_raising=closure))


def build_hopping(model,edges,weight,local=False):
    b=model['embedding'];d=b.shape[1];h=csr_matrix((d,d),dtype=complex);leakage=0.
    local_hop=[csr_matrix((d,d),dtype=complex) for _ in range(model['L'])] if local else None
    for e in edges:
        mag=hopping_matrix(model['occupations'],model['index'],e)
        projected=(b.conj().T@mag@b).tocsr()
        diff=mag@b-b@projected
        leakage=max(leakage,float(np.max(abs(diff.data),initial=0)))
        h+=weight*projected
        if local:
            for site in e:local_hop[site]+=.5*weight*projected
    return (h,leakage,local_hop) if local else (h,leakage)


def initial_state(model,phi=90,sharp=True):
    l=model['L'];k=model['K'];z=np.zeros((l,2),complex)
    z[:4]=spinors_from_normals(closed_equal_area_normals(1/math.sqrt(3),math.radians(phi)))
    # Build only the occupied four-channel FL seed; pad to avoid a huge FockSpace helper.
    _,state=fixed_area_state(k,z[:4])
    mag=np.zeros(len(model['occupations']),complex)
    for o,a in state.items():mag[model['index'][o+(0,)*(2*(l-4))]]=a
    psi=np.asarray(model['embedding'].conj().T@mag).ravel()
    if sharp:
        mask=np.all(model['numbers'][:,:4]==2,axis=1)&np.all(model['numbers'][:,4:]==0,axis=1)
        psi*=mask
    probability=float(np.vdot(psi,psi).real)
    if probability<1e-14:raise ValueError('preparation projection has negligible support')
    psi/=math.sqrt(probability)
    return psi,z,probability


@lru_cache(maxsize=None)
def canonical_geometry(spins):
    """Small M=0 magnetic operators for a sorted local-spin pattern."""
    occ=occupation_basis(spins);pairs=list(combinations(range(len(spins)),2))
    dots={p:action_matrix(occ,dot_operator(su2_ops(p[0]),su2_ops(p[1]))).tocsr() for p in pairs}
    volume=np.zeros((len(occ),len(occ)),complex)
    for i,j,k in combinations(range(len(spins)),3):
        if not spins[i]*spins[j]*spins[k]:continue
        q=(1j*(dots[i,j]@dots[j,k]-dots[j,k]@dots[i,j])).toarray()
        volume+=GAMMA**1.5*root_abs(q)[0]
    return dots,volume


def build_geometry(model):
    l=model['L'];d=len(model['numbers']);pairs=list(combinations(range(l),2))
    entries={name:[[],[],[]] for name in ['volume','kernel',*[str(p) for p in pairs]]}
    checks=dict(volume_negative=0.,kernel_projector=0.,closure_dot_identity=0.)
    for start,stop,spins,b,inverse in model['blocks']:
        dots,vm=canonical_geometry(tuple(sorted(spins)))
        volume=b.conj().T@vm@b;values,vectors=np.linalg.eigh((volume+volume.conj().T)/2)
        tol=2e-12*max(1.,float(np.max(abs(values),initial=0)))
        kernel=vectors[:,values<tol]@vectors[:,values<tol].conj().T
        checks['volume_negative']=max(checks['volume_negative'],float(max(0,-values.min())))
        checks['kernel_projector']=max(checks['kernel_projector'],float(np.max(abs(kernel@kernel-kernel))))
        small={'volume':volume,'kernel':kernel};dot_sum=np.zeros_like(volume)
        for p in pairs:
            i,j=p;dot=b.conj().T@(dots[tuple(sorted((inverse[i],inverse[j])))]@b)
            dot_sum+=dot
            denom=math.sqrt(spins[i]*(spins[i]+2)*spins[j]*(spins[j]+2))/4
            small[str(p)]=dot/denom if denom else np.zeros_like(dot)
        checks['closure_dot_identity']=max(checks['closure_dot_identity'],float(np.max(abs(dot_sum+np.eye(stop-start)*sum(s*(s+2)/4 for s in spins)/2))))
        for name,matrix in small.items():
            r,c=np.nonzero(abs(matrix)>1e-14);rr,cc,vv=entries[name]
            rr.extend(start+r);cc.extend(start+c);vv.extend(matrix[r,c])
    ops={name:coo_matrix((v,(r,c)),shape=(d,d)).tocsr() for name,(r,c,v) in entries.items()}
    return ops,pairs,checks


def readouts(states,model,seed,h):
    numbers=model['numbers'];prob=abs(states)**2;nb=2*model['K'];active=np.sum(numbers>0,axis=1)
    casimir=numbers*(numbers+2)/4;initial_casimir=float(abs(seed)**2@casimir.sum(axis=1))
    area=prob@(numbers/2);local_energy=prob@casimir
    pactive=np.column_stack([prob@(active==n) for n in range(model['L']+1)])
    entropy=np.zeros((len(states),model['L']))
    for site in range(model['L']):
        for n in range(nb+1):
            p=prob@(numbers[:,site]==n);mask=p>0
            entropy[mask,site]-=p[mask]*np.log(p[mask]/(n+1))
    hstates=(h@states.T).T
    energy=np.einsum('ij,ij->i',states.conj(),hstates).real
    return dict(area=area,casimir=local_energy,active_probability=pactive,
                expected_active=pactive@np.arange(model['L']+1),
                receiver_area_fraction=area[:,4:].sum(axis=1)/model['K'],
                receiver_casimir_fraction=local_energy[:,4:].sum(axis=1)/initial_casimir,
                concentration=prob@np.sum(numbers*numbers,axis=1)/nb**2,
                entropy=entropy,return_probability=abs(states@seed.conj())**2,
                norm_error=abs(prob.sum(axis=1)-1),energy_error=abs(energy-energy[0]),energy=energy)


def geometry_readout(psi,model,operators,pairs):
    prob=abs(psi)**2;n=model['numbers'];vpsi=operators['volume']@psi;mean=float(np.vdot(psi,vpsi).real)
    greater=np.sum(n>0,axis=1)>=5;p=float(prob[greater].sum())
    selected=psi*greater
    result=dict(volume_mean=mean,volume_sd=math.sqrt(max(0,float(np.vdot(vpsi,vpsi).real)-mean*mean)),
                zero_volume_probability=float(np.vdot(psi,operators['kernel']@psi).real),
                probability_at_least5=p,conditional_volume_at_least5=float(np.vdot(selected,operators['volume']@selected).real/p) if p>1e-12 else None,pairs=[])
    for pair in pairs:
        i,j=pair;present=(n[:,i]>0)&(n[:,j]>0);p=float(prob[present].sum());a=operators[str(pair)]@psi
        first=float(np.vdot(psi,a).real/p) if p>1e-12 else None
        sd=math.sqrt(max(0,float(np.vdot(a,a).real/p)-first*first)) if p>1e-12 else None
        result['pairs'].append(dict(i=i,j=j,presence_probability=p,conditional_angle_mean=first,conditional_angle_sd=sd))
    return result

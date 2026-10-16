"""Static connectivity audit: exact active-channel projectors, with/without closure."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix, diags, save_npz
from scipy.sparse.csgraph import connected_components
from lqg_scattering.labels import compositions, fixed_face_dimension
from lqg_scattering.fixed_k import uN_generator
from lqg_scattering.singlets import occupation_basis, singlet_paths, sequential_basis
from lqg_scattering.hamiltonian import build_fixed_number_model, assemble_hamiltonian
from lqg_scattering.total_spin import total_spin_operators

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/t11-face-connectivity'
TOL=2e-10

def maximum(a):
    return float(np.max(abs(a.data))) if hasattr(a,'toarray') and a.nnz else (0. if hasattr(a,'toarray') else float(np.max(abs(a),initial=0)))


def singlet_embedding(occupations,index,l,k):
    """Recouple each local-count sector, retaining definite active-channel labels."""
    rows=[];cols=[];vals=[];labels=[]
    for spins in compositions(2*k,l):
        paths=singlet_paths(spins)
        if not paths: continue
        occ,b,_=sequential_basis(spins,paths,occupation_basis(tuple(sorted(spins))))
        r,c=np.nonzero(b)
        start=len(labels)
        rows.extend(index[occ[i]] for i in r);cols.extend(start+c);vals.extend(b[r,c])
        labels.extend(dict(counts=list(spins),path=list(path),active=sum(n>0 for n in spins)) for path in paths)
    b=coo_matrix((vals,(rows,cols)),shape=(len(occupations),len(labels))).tocsr()
    assert len(labels)==fixed_face_dimension(l,k)
    return b,labels


def pair_seed(l,pairs,index):
    """Direct oscillator creation, with normalized Fock occupation amplitudes."""
    state={(0,)*(2*l):1.}
    for i,j in pairs:
        update={}
        for occ,amp in state.items():
            for x,y,sign in [(2*i,2*j+1,1),(2*i+1,2*j,-1)]:
                target=list(occ); factor=math.sqrt((target[x]+1)*(target[y]+1))
                target[x]+=1;target[y]+=1;key=tuple(target)
                update[key]=update.get(key,0)+sign*amp*factor
        state=update
    psi=np.zeros(len(index),complex)
    for o,a in state.items():psi[index[o]]=a
    return psi/np.linalg.norm(psi)


def open_seed(counts,index,magnetic_zero=False):
    psi=np.zeros(len(index),complex)
    if not magnetic_zero:
        occ=tuple(x for n in counts for x in (n,0));psi[index[occ]]=1
    else:
        half=sum(counts)//2
        for aa in product(*(range(n+1) for n in counts)):
            if sum(aa)!=half:continue
            occ=tuple(x for a,n in zip(aa,counts) for x in (a,n-a))
            psi[index[occ]]=math.sqrt(math.prod(math.comb(n,a) for n,a in zip(counts,aa))/math.comb(sum(counts),half))
    return psi


def block_statistics(h,active):
    out={}
    for source,target in [(4,5),(4,6),(5,6)]:
        block=h[active==target][:,active==source]
        out[f'{source}_to_{target}']=dict(shape=list(block.shape),nonzero_entries=int(np.sum(abs(block.data)>1e-12)),
            frobenius_norm=float(np.linalg.norm(block.data)))
    component_counts={}
    for tol in [1e-10,1e-12]:
        adjacency=h.copy();adjacency.setdiag(0);adjacency.data=(abs(adjacency.data)>tol).astype(float);adjacency.eliminate_zeros()
        count,labels=connected_components(adjacency,directed=False)
        sizes=Counter(np.bincount(labels).tolist())
        component_counts[str(tol)]=dict(count=int(count),size_histogram={str(s):v for s,v in sorted(sizes.items())})
    out['basis_graph_components']=component_counts
    return out


def witness(h,psi,occ,spin,expected_j):
    counts=occ[:,::2]+occ[:,1::2];active=np.sum(counts>0,axis=1)
    first=h@psi;v5=first*(active==5)
    second=h@first;v6=second*(active==6)
    n5=np.linalg.norm(v5);n6=np.linalg.norm(v6)
    targets={};checks={}
    for name,v in [('source',psi),('target5',v5),('target6',v6)]:
        norm=np.linalg.norm(v)
        if not norm:continue
        v=v/norm
        checks[name]=dict(norm_error=float(abs(np.vdot(v,v).real-1)),
            spin_squared=float(np.vdot(v,spin['squared']@v).real),
            spin_eigen_residual=float(np.linalg.norm(spin['squared']@v-expected_j*(expected_j+1)*v)),
            mean_spin=[float(np.vdot(v,spin[axis]@v).real) for axis in ['x','y','z']],
            closure_generator_norms={axis:float(np.linalg.norm(spin[axis]@v)) for axis in ['x','y','z']})
        nz=np.flatnonzero(abs(v)>1e-12)
        targets[name]=[dict(occupation=occ[i].tolist(),amplitude_real=float(v[i].real),amplitude_imag=float(v[i].imag)) for i in nz]
    return dict(norm_P5_H_source=float(n5),norm_P6_H2_source=float(n6),
        direct_P6_H_source=float(np.linalg.norm(first*(active==6))),
        matrix_element_target6_H_target5=float(np.vdot(v6/n6,h@(v5/n5)).real) if n5 and n6 else None,
        checks=checks,states=targets)


def run_case(l,k,with_witness=False):
    graphs=dict(ring=[(i,(i+1)%l) for i in range(l)],complete=list(combinations(range(l),2)),
                disconnected_receivers=list(combinations(range(4),2)))
    model=build_fixed_number_model(l,2*k,graphs['complete']);occ=model['occupations'];index=model['index']
    n=occ[:,::2]+occ[:,1::2];active=np.sum(n>0,axis=1)
    spin=total_spin_operators(occ,index,l)
    b,labels=singlet_embedding(occ,index,l,k);closed_active=np.array([label['active'] for label in labels])
    validation=dict(gram=maximum(b.conj().T@b-diags(np.ones(b.shape[1]))),
                    singlet_dimension_error=abs(b.shape[1]-fixed_face_dimension(l,k)),
                    closure_x=maximum(spin['x']@b),closure_y=maximum(spin['y']@b),closure_z=maximum(spin['z']@b))
    result=dict(L=l,K=k,full_dimension=len(occ),singlet_dimension=len(labels),
                full_active_counts={str(a):int(np.sum(active==a)) for a in range(l+1)},
                singlet_active_counts={str(a):int(np.sum(closed_active==a)) for a in range(l+1)},graphs={},validation=validation)
    if with_witness:
        counts=[2,1,1,2]+[0]*(l-4)
        seeds=dict(closed=pair_seed(l,[(0,3),(0,3),(1,2)],index),
                   open_highest_weight=open_seed(counts,index),open_M0=open_seed(counts,index,True))
    for name,edges in graphs.items():
        hopping=sum((model['bonds'][tuple(sorted(e))] for e in edges),csr_matrix((len(occ),len(occ)),dtype=complex))
        casimir=diags(np.sum(n*(n+2),axis=1)/4,format='csr')
        h=(casimir-hopping).tocsr();hc=(b.conj().T@h@b).tocsr()
        # Clean roundoff only for graph/rank counting; use raw matrices for witnesses.
        graph=dict(full=block_statistics(h,active),closed=block_statistics(hc,closed_active))
        block=hc[closed_active==5][:,closed_active==4].toarray()
        singular=np.linalg.svd(block,compute_uv=False)
        rank=int(np.sum(singular>1e-10))
        graph['closed']['4_to_5'].update(rank=rank,source_nullity=block.shape[1]-rank,
            rank_at_1e12=int(np.sum(singular>1e-12)))
        two_step=(hc[closed_active==6]@hc[:,closed_active==4]).toarray()
        singular2=np.linalg.svd(two_step,compute_uv=False)
        graph['closed']['4_to_6_second_power']=dict(shape=list(two_step.shape),
            frobenius_norm=float(np.linalg.norm(two_step)),rank=int(np.sum(singular2>1e-10)),rank_at_1e12=int(np.sum(singular2>1e-12)))

        # Embed the sparse singlet Hamiltonian without making a dense full matrix.
        validation[name+'_projection_leakage']=maximum(h@b-b@hc)
        validation[name+'_hermiticity']=maximum(h-h.conj().T)
        for axis in ['x','y','z','squared']:
            validation[name+'_commutator_'+axis]=maximum(h@spin[axis]-spin[axis]@h)
        onsite_model=dict(onsite=model['onsite'],bonds={e:model['bonds'][e] for e in model['bonds'] if e in {tuple(sorted(e)) for e in edges}})
        old=assemble_hamiltonian(onsite_model,1.,.5)+diags(np.full(len(occ),3*(2*k)/4))
        validation[name+'_onsite_identity']=maximum(h-old)
        graph['onsite_4_to_5']=float(np.linalg.norm(casimir[active==5][:,active==4].data))
        if with_witness and name in ['ring','complete']:
            z=np.zeros((l,l));z[5,0]=1
            e50=uN_generator(occ,index,z,l)
            z=np.zeros((l,l));z[4,3]=1
            e43=uN_generator(occ,index,z,l)
            graph['directed_chain']={}
            for seed,psi in seeds.items():
                target5=e50@psi; norm5=np.linalg.norm(target5);target5/=norm5
                target6=e43@target5;norm6=np.linalg.norm(target6);target6/=norm6
                graph['directed_chain'][seed]=dict(
                    source_counts=[2,1,1,2,0,0],target5_counts=[1,1,1,2,0,1],target6_counts=[1,1,1,1,1,1],
                    first_hop_norm=float(norm5),second_hop_norm=float(norm6),
                    H_target5_source=float(np.vdot(target5,h@psi).real),
                    H_target6_target5=float(np.vdot(target6,h@target5).real),
                    H2_target6_source=float(np.vdot(target6,h@(h@psi)).real),
                    target5=[dict(occupation=occ[i].tolist(),amplitude_real=float(target5[i].real),amplitude_imag=float(target5[i].imag)) for i in np.flatnonzero(abs(target5)>1e-12)],
                    target6=[dict(occupation=occ[i].tolist(),amplitude_real=float(target6[i].real),amplitude_imag=float(target6[i].imag)) for i in np.flatnonzero(abs(target6)>1e-12)])
                j=0 if seed=='closed' else 3
                for label,v in [('target5',target5),('target6',target6)]:
                    validation[name+'_'+seed+'_direct_'+label+'_spin']=float(np.linalg.norm(spin['squared']@v-j*(j+1)*v))
            validation[name+'_independent_directed_builder']=maximum(e50+e50.conj().T-model['bonds'][(0,5)])

        if with_witness:
            graph['witnesses']={s:witness(h,psi,occ,spin,0 if s=='closed' else 3) for s,psi in seeds.items()}
            for seed,w in graph['witnesses'].items():
                for target,c in w['checks'].items():
                    validation[name+'_'+seed+'_'+target+'_spin_residual']=c['spin_eigen_residual']
            save_npz(OUT/f'L{l}-K{k}-{name}-singlet-H.npz',hc)
        result['graphs'][name]=graph
    # Explicit no-hopping control for every seed.
    if with_witness:
        diag=diags(np.sum(n*(n+2),axis=1)/4)
        result['no_hopping_witnesses']={s:witness(diag,psi,occ,spin,0 if s=='closed' else 3) for s,psi in seeds.items()}
        (OUT/f'L{l}-K{k}-singlet-labels.json').write_text(json.dumps(labels,indent=2)+'\n')
        save_npz(OUT/f'L{l}-K{k}-singlet-embedding.npz',b)
        np.savez_compressed(OUT/f'L{l}-K{k}-full-occupations.npz',occupations=occ)
    assert max(validation.values())<TOL,validation
    return result


def main():
    OUT.mkdir(exist_ok=True,parents=True)
    results=[]
    for l,k in [(6,3),(5,3),(6,2)]:
        result=run_case(l,k,with_witness=(l,k)==(6,3));results.append(result)
        (OUT/f'L{l}-K{k}.json').write_text(json.dumps(result,indent=2)+'\n')
        print(l,k,result['full_dimension'],result['singlet_dimension'],max(result['validation'].values()),flush=True)
    sources=[Path(__file__),OUT/'protocol.md',*[(ROOT/'code/python/lqg_scattering'/f'{name}.py') for name in ['hamiltonian','singlets','fixed_k','total_spin','labels']]]
    (OUT/'summary.json').write_text(json.dumps(dict(cases=[f"L{r['L']}-K{r['K']}.json" for r in results],
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')

if __name__=='__main__':main()

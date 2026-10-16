"""Finite channel-count equilibration pilot; no geometry reconstruction."""
import csv
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import brentq
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import expm_multiply
from lqg_scattering.labels import compositions, fixed_face_dimension
from lqg_scattering.singlets import occupation_basis, singlet_paths, sequential_basis, closure_residual
from lqg_scattering.hamiltonian import hopping_matrix
from lqg_scattering.intertwiners import fixed_area_state, regular_tetrahedron_spinors

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'results/t11-equilibration'
TOL = 2e-9


def build(l, k):
    occ = [tuple(v for pair in zip(a,b) for v in pair)
           for a in compositions(k,l) for b in compositions(k,l)]
    index = {o:i for i,o in enumerate(occ)}
    rows, cols, vals, start = [], [], [], 0
    closure = 0.
    for spins in compositions(2*k,l):
        paths = singlet_paths(spins)
        if not paths:
            continue
        canonical = occupation_basis(tuple(sorted(spins)))
        block_occ, b, _ = sequential_basis(spins, paths, canonical)
        closure = max(closure, closure_residual(block_occ,b))
        r,c = np.nonzero(b)
        rows.extend(index[block_occ[i]] for i in r)
        cols.extend(start+c); vals.extend(b[r,c]); start += len(paths)
    assert start == fixed_face_dimension(l,k)
    basis = coo_matrix((vals,(rows,cols)),shape=(len(occ),start)).tocsr()
    gram = np.max(abs((basis.conj().T@basis).toarray()-np.eye(start)))
    n = np.asarray(occ)[:,::2]+np.asarray(occ)[:,1::2]
    hop = sum((hopping_matrix(occ,index,e) for e in itertools.combinations(range(l),2)),
              coo_matrix((len(occ),len(occ))).tocsr())/(l-1)
    onsite = diags(.5*np.sum(n*(n-1),axis=1))
    hopping = (basis.conj().T@hop@basis).toarray()
    repulsion = (basis.conj().T@onsite@basis).toarray()
    leakage = np.max(abs(hop@basis-basis@hopping))
    assert max(gram,closure,leakage) < TOL
    # Occupation-distribution readouts, all bounded in [0,1].
    active = np.sum(n>0,axis=1)
    readouts = np.column_stack([np.sum(n*n,axis=1)/(2*k)**2,
        np.sum(n[:,4:],axis=1)/(2*k), *[(active==m).astype(float) for m in range(l+1)]])
    return occ,basis,hop,onsite,hopping,repulsion,readouts,dict(gram=float(gram),closure=float(closure),leakage=float(leakage))


def groups(e):
    return np.split(np.arange(len(e)),np.flatnonzero(np.diff(e)>1e-9)+1)


def csv_write(name, rows):
    with (OUT/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=dict(task='T11',sizes=[[l,2] for l in range(4,8)]+[[4,3],[5,3],[6,3]],
        U=[0.,1.,5.],hopping='complete graph, t_ij=1/(L-1); fixed row-sum hopping scale',
        preparations=['regular','phase_shifted'],initial='normalized fixed-area FL with four nonzero spinors; NOT four sharply occupied faces',
        time_grid='0..200 inclusive, dt=.1; statistics on [20,100] and [20,200]',
        reference='exact energy-projector dephasing; coherence retained within degeneracies',
        canonical='energy-matched full fixed-K singlet ensemble, including negative beta if needed; permutation sectors NOT resolved',
        near_equilibrium='max(Q concentration absolute error, extra-area fraction absolute error, active-count total variation) <= .05 relative to dephased reference',
        threshold_sensitivity=[.02,.05,.1],limitations=['small area','finite time','full canonical benchmark does not match all permutation symmetries','occupation count cannot exceed 2K','no geometric claim','no entanglement calculation'],
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        tolerance=TOL)
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    summaries=[]; trajectories=[]; validation={}; references=[]
    times=np.linspace(0,200,2001)
    for l,k in protocol['sizes']:
        occ,b,hop,onsite,h0,hu,obs,checks=build(l,k)
        for u in protocol['U']:
            h=-h0+u*hu
            e,w=eigh(h)
            checks[f'eigen_U{u}']=float(np.max(abs(h@w-w*e)))
            for phase in protocol['preparations']:
                z=np.zeros((l,2),complex);z[:4]=regular_tetrahedron_spinors()
                if phase=='phase_shifted': z[:4]*=np.exp(1j*np.arange(4)*np.pi/2)[:,None]
                _,state=fixed_area_state(k,z)
                mag=np.array([state.get(o,0j) for o in occ]);psi=np.asarray(b.conj().T@mag).ravel()
                checks[f'input_{phase}']=float(np.max(abs(b@psi-mag)))
                a=w.conj().T@psi; energy=float(np.real(np.vdot(psi,h@psi)))
                dephased=np.zeros(len(obs))
                for g in groups(e):
                    v=b@(w[:,g]@a[g]);dephased+=abs(v)**2
                target=dephased@obs
                def weights(beta):
                    log=-beta*e;log-=log.max();p=np.exp(log);return p/p.sum()
                bound=1.
                while (weights(-bound)@e-energy)*(weights(bound)@e-energy)>0 and bound<1e8: bound*=2
                beta=brentq(lambda beta:weights(beta)@e-energy,-bound,bound)
                p=weights(beta)
                canonical=(abs(b@w)**2@p)@obs
                for i,(d,c) in enumerate(zip(target,canonical)):
                    references.append(dict(L=l,K=k,U=u,phase=phase,observable=i,dephased=float(d),canonical=float(c),beta=beta))
                amps=w@(a[:,None]*np.exp(-1j*e[:,None]*times))
                values=(abs(b@amps)**2).T@obs
                distance=np.maximum.reduce([abs(values[:,0]-target[0]),abs(values[:,1]-target[1]),.5*np.sum(abs(values[:,2:]-target[2:]),axis=1)])
                returns=abs(psi.conj()@amps)**2
                checks[f'norm_U{u}_{phase}']=float(np.max(abs(np.sum(abs(amps)**2,axis=0)-1)))
                checks[f'energy_U{u}_{phase}']=float(np.max(abs(np.sum(abs(w.conj().T@amps)**2*e[:,None],axis=0)-energy)))
                # Independent full magnetic-space propagation checks projection and evolution.
                for time in [.37,7.3]:
                    direct=expm_multiply((-hop+u*onsite)*(-1j*time),mag)
                    exact=b@(w@(a*np.exp(-1j*e*time)))
                    checks[f'propagation_U{u}_{phase}_{time}']=float(np.max(abs(direct-exact)))
                for end in [100,200]:
                    mask=(times>=20)&(times<=end)
                    row=dict(L=l,K=k,U=u,phase=phase,dimension=len(e),window_end=end,energy=energy,beta=beta,
                        mean_distance=float(distance[mask].mean()),rms_distance=float(np.sqrt(np.mean(distance[mask]**2))),
                        mean_concentration=float(values[mask,0].mean()),dephased_concentration=float(target[0]),
                        mean_extra_area_fraction=float(values[mask,1].mean()),dephased_extra_area_fraction=float(target[1]),
                        canonical_active_count_TV=float(.5*np.sum(abs(target[2:]-canonical[2:]))),
                        max_return_after20=float(returns[mask].max()))
                    for threshold in [.02,.05,.1]:row[f'residence_{threshold}']=float(np.mean(distance[mask]<=threshold))
                    summaries.append(row)
                for j,time in enumerate(times):
                    trajectories.append(dict(L=l,K=k,U=u,phase=phase,time=float(time),concentration=float(values[j,0]),
                        extra_area_fraction=float(values[j,1]),distance=float(distance[j]),return_probability=float(returns[j]),
                        **{f'p_active_{m}':float(values[j,m+2]) if m<=l else 0. for m in range(8)}))
        assert max(checks.values())<TOL,checks
        validation[f'L{l}_K{k}']=checks
        csv_write('summary.csv',summaries);csv_write('dynamics.csv',trajectories);csv_write('references.csv',references)
        (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
        print(f'Completed L={l}, K={k}, dimension={len(e)}; maximum residual {max(checks.values()):.3g}',flush=True)
    paths=[Path(__file__),*sorted((ROOT/'code/python/lqg_scattering').glob('*.py'))]
    (OUT/'provenance.json').write_text(json.dumps(dict(numpy=np.__version__,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2)+'\n')


if __name__=='__main__': main()

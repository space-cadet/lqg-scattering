"""Independent magnetic-space and explicit sliced-trace checks."""
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from scipy.sparse import coo_matrix
from lqg_scattering.singlets import independent_local_q,closure_residual

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/t11-geometric-interpretation'


def read(path):
    with path.open() as f:return list(csv.DictReader(f))


def independent_dot(occ,i,j):
    """Explicit magnetic ladder elements; no shared pair-dot constructor."""
    index={tuple(o):r for r,o in enumerate(occ)};rows=[];cols=[];data=[]
    for col,state in enumerate(occ):
        a,b=state[2*i:2*i+2];c,d=state[2*j:2*j+2]
        rows.append(col);cols.append(col);data.append((a-b)*(c-d)/4)
        for step in (1,-1):
            amplitude=math.sqrt((a+1)*b*c*(d+1) if step==1 else a*(b+1)*(c+1)*d)/2
            if amplitude:
                changed=state.copy();changed[2*i]+=step;changed[2*i+1]-=step
                changed[2*j]-=step;changed[2*j+1]+=step
                rows.append(index[tuple(changed)]);cols.append(col);data.append(amplitude)
    return coo_matrix((data,(rows,cols)),shape=(len(occ),len(occ))).tocsr()


def main():
    ar=np.load(ROOT/'results/hamiltonian-studies/operators_k4_complete.npz')
    data=np.load(OUT/'states_and_operators.npz')
    b=ar['singlet_basis'];occ=ar['occupations_m0'];numbers=data['numbers'];active=np.all(numbers>0,axis=1)
    errors={}
    for i,j in [(i,j) for i in range(4) for j in range(i+1,4)]:
        magnetic=independent_dot(occ,i,j)
        errors[f'D{i}{j}_independent_magnetic']=float(np.max(abs(b.conj().T@(magnetic@b)-data[f'D{i}{j}'])))
    errors['q012_independent_epsilon']=0.
    errors['positive_root_reconstruction']=0.
    errors['closure']=closure_residual([tuple(o) for o in occ],b)
    mag_numbers=occ[:,::2]+occ[:,1::2]
    for assignment in sorted(set(map(tuple,numbers))):
        cols=np.flatnonzero(np.all(numbers==assignment,axis=1))
        rows=np.flatnonzero(np.all(mag_numbers==assignment,axis=1))
        local_occ=[tuple(o) for o in occ[rows]]
        local_b=b[np.ix_(rows,cols)]
        direct=independent_local_q(local_occ,assignment,(0,1,2))
        errors['q012_independent_epsilon']=max(errors['q012_independent_epsilon'],
            float(np.max(abs(local_b.conj().T@(direct@local_b)-data['q012'][np.ix_(cols,cols)]))))
        projected=local_b.conj().T@(direct@local_b)
        values,vectors=np.linalg.eigh(projected)
        cutoff=64*np.finfo(float).eps*max(1.,float(np.max(abs(values))))
        roots=(vectors*np.sqrt(np.where(abs(values)<=cutoff,0,abs(values))))@vectors.conj().T
        # Four-valent closure gives four equal positive roots; reconstruct
        # the saved RS operator from independently contracted epsilon q.
        gamma=.2375
        errors['positive_root_reconstruction']=max(errors['positive_root_reconstruction'],
            float(np.max(abs(4*gamma**1.5*roots-data['volume'][np.ix_(cols,cols)]))))
    details=json.loads((OUT/'state_details.json').read_text())
    errors['conditional_sliced_trace']=0.;errors['angular_covariance']=0.
    errors['FL_equal_area_means']=0.;errors['degenerate_mixture_rotation']=0.
    for label,record in details.items():
        ket=data[label] if label.startswith('FL_') else None
        rho=np.outer(ket,ket.conj()) if ket is not None else data[label+'_rho']
        p=np.real(np.diag(rho)[active].sum());sub=rho[np.ix_(active,active)]/p
        angles=[]
        for index,(i,j) in enumerate([(i,j) for i in range(4) for j in range(i+1,4)]):
            spins=numbers[active]/2
            denom=np.sqrt(spins[:,i]*(spins[:,i]+1)*spins[:,j]*(spins[:,j]+1))
            op=data[f'D{i}{j}'][np.ix_(active,active)]/denom[None,:]
            angles.append(op)
            expectation=float(np.real(np.trace(sub@op)))
            errors['conditional_sliced_trace']=max(errors['conditional_sliced_trace'],
                abs(expectation-record['conditional_angle_means'][index]))
        for i,left in enumerate(angles):
            for j,right in enumerate(angles):
                covariance=float(np.real(np.trace(sub@left@right)))-record['conditional_angle_means'][i]*record['conditional_angle_means'][j]
                errors['angular_covariance']=max(errors['angular_covariance'],abs(covariance-record['conditional_angle_covariance'][i][j]))
        if ket is not None:
            errors['FL_equal_area_means']=max(errors['FL_equal_area_means'],max(abs(np.array(record['area_means'])-1)))
    errors['equal_area_overlaps']=0.
    equal_mask=np.all(numbers==2,axis=1)
    for row in read(OUT/'reference_overlaps.csv'):
        if row['equal_spin_conditioned_overlap']=='':continue
        label=row['state'];ref=data[row['reference']][equal_mask]
        ref=ref/np.linalg.norm(ref)
        rho=(np.outer(data[label],data[label].conj()) if label.startswith('FL_') else data[label+'_rho'])
        sub=rho[np.ix_(equal_mask,equal_mask)];sub=sub/np.trace(sub)
        errors['equal_area_overlaps']=max(errors['equal_area_overlaps'],
            abs(float(np.real(np.vdot(ref,sub@ref)))-float(row['equal_spin_conditioned_overlap'])))
    new=read(OUT/'thermal_geometry.csv');old=read(ROOT/'results/hamiltonian-studies/k4_thermal_volume_scan.csv')
    errors['saved_thermal_volume']=0.;errors['thermal_expm_angles']=0.
    for row in new:
        reference=next(r for r in old if r['graph']==row['graph'] and r['case']=='U20' and float(r['beta'])==float(row['beta']))
        errors['saved_thermal_volume']=max(errors['saved_thermal_volume'],abs(float(row['volume_mean'])-float(reference['mean_volume'])))
    for graph in ('complete','ring'):
        h=data[graph+'_H'];e=data[graph+'_energies'];w=data[graph+'_vectors']
        indices=np.flatnonzero(abs(e-e[0])<2e-10)
        rng=np.random.default_rng(1104)
        unitary=np.linalg.qr(rng.normal(size=(len(indices),len(indices)))+1j*rng.normal(size=(len(indices),len(indices))))[0]
        rotated=w[:,indices]@unitary
        errors['degenerate_mixture_rotation']=max(errors['degenerate_mixture_rotation'],
            float(np.max(abs(rotated@rotated.conj().T/len(indices)-data[graph+'_level0_rho']))))
        # Also rotate the first excited group, testing the complete doublet.
        first=np.flatnonzero(abs(e-e[len(indices)])<2e-10)
        unitary=np.linalg.qr(rng.normal(size=(len(first),len(first)))+1j*rng.normal(size=(len(first),len(first))))[0]
        rotated=w[:,first]@unitary
        errors['degenerate_mixture_rotation']=max(errors['degenerate_mixture_rotation'],
            float(np.max(abs(rotated@rotated.conj().T/len(first)-data[graph+'_level1_rho']))))
        for beta in (.1,1.,100.):
            target=min((r for r in new if r['graph']==graph and np.isfinite(float(r['beta']))),key=lambda r:abs(float(r['beta'])-beta))
            beta=float(target['beta'])
            rho=expm(-beta*(h-e[0]*np.eye(len(h))));rho/=np.trace(rho)
            p=np.real(np.diag(rho)[active].sum());sub=rho[np.ix_(active,active)]/p
            errors['thermal_expm_angles']=max(errors['thermal_expm_angles'],
                abs(float(np.real(np.trace(rho@data['volume'])))-float(target['volume_mean'])))
            spins=numbers[active]/2
            for i,j in [(i,j) for i in range(4) for j in range(i+1,4)]:
                denom=np.sqrt(spins[:,i]*(spins[:,i]+1)*spins[:,j]*(spins[:,j]+1))
                op=data[f'D{i}{j}'][np.ix_(active,active)]/denom[None,:]
                errors['thermal_expm_angles']=max(errors['thermal_expm_angles'],
                    abs(float(np.real(np.trace(sub@op)))-float(target[f'C{i}{j}_mean'])))
    assert max(errors.values())<2e-10,errors
    report={'residuals':errors,'threshold':2e-10,
        'independence':'explicit magnetic ladder dots, epsilon triples, sliced traces, matrix-exponential Gibbs states; shared singlet basis; no new Rust run'}
    (OUT/'independent_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    source_paths=[Path(__file__),ROOT/'code/python/t11_geometric_interpretation.py',
        ROOT/'code/python/test_geometric_diagnostics.py',ROOT/'code/python/lqg_scattering/geometric_diagnostics.py',
        ROOT/'code/python/plot_t11_geometric_interpretation.py',
        ROOT/'notes/t11-geometric-interpretation.md',
        *sorted((ROOT/'code/python/lqg_scattering').glob('*.py'))]
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths if p.exists()}
    (OUT/'source_hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='sha256.json'}
    (OUT/'sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(errors,indent=2))


if __name__=='__main__': main()

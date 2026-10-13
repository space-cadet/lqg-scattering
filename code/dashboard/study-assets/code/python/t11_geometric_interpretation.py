"""Frozen K4 FL-reference versus low-energy tetrahedral diagnostics."""
import csv
import hashlib
import itertools
import json
import math
import platform
import subprocess
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import eigh
from lqg_scattering.geometric_diagnostics import (mean,condition,moments,
    angular_operators,summarize)
from lqg_scattering.intertwiners import fixed_area_state
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.tetrahedra import (closed_equal_area_normals,
    classical_volume_from_faces,GEOMETRY_MATCHING_FACTORS)
from lqg_scattering.singlets import ABS_TOL,ZERO_FACTOR,GAMMA
from lqg_scattering.thermal import grouped_values,thermal_weights

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/t11-geometric-interpretation'
PAIRS=tuple(itertools.combinations(range(4),2))


def save_csv(name,rows):
    with (OUT/name).open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def reference(phi,archive):
    normals=closed_equal_area_normals(1/math.sqrt(3),math.radians(phi))
    _,state=fixed_area_state(4,spinors=spinors_from_normals(normals))
    magnetic=np.array([state.get(tuple(o),0j) for o in archive['occupations_m0']])
    ket=archive['singlet_basis'].conj().T@magnetic
    residual=float(np.max(abs(archive['singlet_basis']@ket-magnetic)))
    assert residual<ABS_TOL and abs(np.vdot(ket,ket)-1)<ABS_TOL
    return ket,normals,residual


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=dict(K=4,L=4,t=1,U=20,g=0,graphs=['complete','ring'],
        reference_phi_degrees=[90,60,30,10,0],reference_x=1/math.sqrt(3),
        reference_family='existing normalized FL; equal input area fractions; fluctuating local spins',
        flat_boundary='phi=0 is a degenerate-input control, not a nondegenerate tetrahedron',
        level_groups=3,beta_grid='0,601 geomspace(1e-3,1e3),infinity',
        angular_readout='four-face conditioned operator, normalized per area assignment',
        overlap_conditioning='full state, four active faces, and j_i=1 sector; undefined below probability threshold',
        probability_threshold=1e-14,acceptance_tolerance=ABS_TOL,root_zero_factor=ZERO_FACTOR,
        gamma=GAMMA,hbar=1,geometric_rs_factor=GEOMETRY_MATCHING_FACTORS['rs'],
        classical_reference='gamma*K/4 times input normals; separate from quantum angular means',
        physical_calibration=False,git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__)
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    archive=np.load(ROOT/'results/hamiltonian-studies/operators_k4_complete.npz')
    numbers=archive['site_boson_numbers'];volume=archive['volume']
    dots={p:archive[f'spin_dot_{p[0]}_{p[1]}'] for p in PAIRS}
    q=1j*(dots[0,1]@dots[1,2]-dots[1,2]@dots[0,1])
    values,vectors=eigh(volume)
    zero=abs(values)<=ZERO_FACTOR*max(1.,float(np.max(abs(values))))
    pzero=vectors[:,zero]@vectors[:,zero].conj().T
    volume_groups=grouped_values(values)
    active=np.all(numbers>0,axis=1)
    _,angles=angular_operators(numbers,dots)
    angles=[op*active[None,:] for op in angles]
    assignments=sorted(set(map(tuple,numbers)))
    refs={}; states={}; reference_data=[];validation={}
    for phi in protocol['reference_phi_degrees']:
        ket,normals,residual=reference(phi,archive)
        label=f'FL_phi{phi}'
        refs[label]=ket;states[label]=np.outer(ket,ket.conj())
        reference_data.append(dict(state=label,phi_degrees=phi,input_normal_gram=(normals@normals.T).tolist(),
            classical_input_volume=classical_volume_from_faces(GAMMA*normals),
            flat_boundary=phi==0))
        validation[label+'_projection']=residual
    thermals=[]; level_tables=[]
    arrays={'numbers':numbers,'volume':volume,'q012':q,**{f'D{i}{j}':dots[i,j] for i,j in PAIRS}}
    for name,ket in refs.items(): arrays[name]=ket
    for graph in protocol['graphs']:
        ar=np.load(ROOT/f'results/hamiltonian-studies/operators_k4_{graph}.npz')
        assert np.max(abs(ar['singlet_basis']-archive['singlet_basis']))<ABS_TOL
        edges=list(PAIRS) if graph=='complete' else [(0,1),(1,2),(2,3),(0,3)]
        h=20*ar['onsite_penalty']-sum(ar[f'hopping_{i}_{j}'] for i,j in edges)
        e,w=eigh(h);groups=grouped_values(e)
        validation[graph+'_eigen_residual']=float(np.max(abs(h@w-w*e)))
        arrays[graph+'_H']=h;arrays[graph+'_energies']=e;arrays[graph+'_vectors']=w
        for group_index,group in enumerate(groups[:3]):
            selected=w[:,group['indices']]
            label=f'{graph}_level{group_index}'
            states[label]=selected@selected.conj().T/len(group['indices'])
            arrays[label+'_rho']=states[label]
            level_tables.append(dict(state=label,graph=graph,group=group_index,
                energy=group['value'],energy_above_ground=group['value']-e[0],degeneracy=len(group['indices'])))
        def diagonal(op): return np.real(np.sum(w.conj()*(op@w),axis=0))
        vm=diagonal(volume);v2=diagonal(volume@volume);p4=(abs(w)**2).T@active
        angle_m=np.array([diagonal(op) for op in angles]);angle2=np.array([diagonal(op@op) for op in angles])
        v4=diagonal(volume*active[None,:]);z0=diagonal(pzero)
        for beta in [0.,*np.geomspace(1e-3,1e3,601),math.inf]:
            weights,_=thermal_weights(e,beta);prob=float(weights@p4)
            conditional_m=angle_m@weights/prob
            conditional_sd=np.sqrt(np.maximum(0,angle2@weights/prob-conditional_m**2))
            populations=[float(weights[group['indices']].sum()) for group in groups[:3]]
            row=dict(graph=graph,beta=beta,volume_mean=float(weights@vm),
                volume_sd=math.sqrt(max(0,float(weights@v2)-(weights@vm)**2)),
                four_face_probability=prob,conditional_volume_mean=float(weights@v4/prob),
                probability_zero_volume=float(weights@z0),
                conditional_angle_rms_sd=float(np.sqrt(np.mean(conditional_sd**2))),
                level0_probability=populations[0],level1_probability=populations[1],
                level2_probability=populations[2],other_levels_probability=1-sum(populations))
            for pair,m,sd in zip(PAIRS,conditional_m,conditional_sd):
                row[f'C{pair[0]}{pair[1]}_mean']=float(m);row[f'C{pair[0]}{pair[1]}_sd']=float(sd)
            thermals.append(row)
    summaries=[];pair_rows=[];sector_rows=[];distribution=[];overlaps=[];details={}
    for label,rho in states.items():
        d=summarize(rho,numbers,dots,volume,q);details[label]=d
        prob,cond=condition(rho,active)
        m=np.array(d['conditional_angle_means']);cov=np.array(d['conditional_angle_covariance'])
        summaries.append(dict(state=label,four_face_probability=prob,
            mean_active_faces=sum(int(n)*p for n,p in d['active_face_probabilities'].items()),
            volume_mean=d['volume_mean'],volume_sd=math.sqrt(d['volume_variance']),
            geometric_volume_mean=GEOMETRY_MATCHING_FACTORS['rs']*d['volume_mean'],
            conditional_volume_mean=d['conditional_volume_mean'],
            probability_zero_volume=mean(rho,pzero),signed_q_mean=d['signed_q_mean'],
            q_rms=math.sqrt(max(0,d['q_second_moment'])),
            conditional_angle_rms_sd=float(np.sqrt(np.mean(np.maximum(0,np.diag(cov))))),
            conditional_angle_max_sd=float(np.sqrt(max(0,np.diag(cov).max())))))
        for index,pair in enumerate(PAIRS):
            pair_rows.append(dict(state=label,i=pair[0],j=pair[1],dot_mean=d['pair_dot_means'][index],
                four_face_C_mean=float(m[index]),four_face_C_sd=math.sqrt(max(0,cov[index,index]))))
        for assignment in assignments:
            mask=np.all(numbers==assignment,axis=1);probability,sector=condition(rho,mask)
            if probability<=1e-14: continue
            row=dict(state=label,twice_spins=' '.join(map(str,assignment)),probability=probability,
                active_faces=sum(n>0 for n in assignment),volume_mean=mean(sector,volume),
                probability_zero_volume=mean(sector,pzero),signed_q_mean=mean(sector,q),
                q_rms=math.sqrt(max(0,mean(sector,q@q))))
            if all(assignment): sm,sc=moments(sector,angles)
            for idx,pair in enumerate(PAIRS):
                row[f'C{pair[0]}{pair[1]}_mean']=float(sm[idx]) if all(assignment) else ''
                row[f'C{pair[0]}{pair[1]}_sd']=math.sqrt(max(0,sc[idx,idx])) if all(assignment) else ''
            sector_rows.append(row)
        for group in volume_groups:
            selected=vectors[:,group['indices']]
            probability=float(np.real(np.trace(selected.conj().T@rho@selected)))
            distribution.append(dict(state=label,volume=max(0,group['value']),multiplicity=len(group['indices']),
                probability=probability,conditional_probability=float(np.real(np.trace(selected.conj().T@cond@selected)))))
        for ref,ket in refs.items():
            refprob,refcond=condition(np.outer(ket,ket.conj()),active)
            equal_mask=np.all(numbers==2,axis=1)
            equal_probability,equal_state=condition(rho,equal_mask)
            ref_equal_probability,ref_equal_state=condition(np.outer(ket,ket.conj()),equal_mask)
            overlaps.append(dict(state=label,reference=ref,overlap=mean(rho,np.outer(ket,ket.conj())),
                conditioned_overlap=mean(cond,refcond),reference_four_face_probability=refprob,
                equal_spin_probability=equal_probability,reference_equal_spin_probability=ref_equal_probability,
                equal_spin_conditioned_overlap=(mean(equal_state,ref_equal_state)
                    if equal_state is not None and ref_equal_state is not None else '')))
        validation[label+'_trace']=float(abs(np.trace(rho)-1))
        validation[label+'_positivity']=float(max(0,-np.linalg.eigvalsh(rho).min()))
        validation[label+'_sector_sum']=abs(sum(r['probability'] for r in sector_rows if r['state']==label)-1)
        assert all(np.linalg.eigvalsh(cov)>-ABS_TOL)
    assert max(validation.values())<ABS_TOL,validation
    for filename,rows in [('state_summary.csv',summaries),('pair_correlations.csv',pair_rows),
        ('area_sectors.csv',sector_rows),('volume_distributions.csv',distribution),
        ('reference_overlaps.csv',overlaps),('thermal_geometry.csv',thermals),('energy_groups.csv',level_tables)]:
        save_csv(filename,rows)
    (OUT/'state_details.json').write_text(json.dumps(details,indent=2)+'\n')
    (OUT/'reference_inputs.json').write_text(json.dumps(reference_data,indent=2)+'\n')
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    np.savez_compressed(OUT/'states_and_operators.npz',**arrays)
    source_paths=[Path(__file__),ROOT/'code/python/lqg_scattering/geometric_diagnostics.py',
        ROOT/'notes/t11-geometric-interpretation.md',ROOT/'results/hamiltonian-studies/operators_k4_complete.npz',
        ROOT/'results/hamiltonian-studies/operators_k4_ring.npz']
    (OUT/'provenance.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in source_paths},indent=2)+'\n')
    print('Calculated',len(states),'states;',len(thermals),'thermal rows; max residual',max(validation.values()))
    for row in summaries: print(row)


if __name__=='__main__': main()

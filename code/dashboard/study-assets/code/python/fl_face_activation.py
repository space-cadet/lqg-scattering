"""Large-area free-hopping control for an FL tetrahedron and empty channels."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
from lqg_scattering.intertwiners import (regular_tetrahedron_spinors,
    evolve_fl_spinors, fl_face_statistics)
from lqg_scattering.labels import fixed_face_dimension
from lqg_scattering.spinors import face_vectors_from_spinors

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/fl-face-activation'
AREAS=[2,20,100,1000,10000]
TIMES=np.unique(np.r_[np.linspace(0,2,161),
    [v for center in [0,1,2] for delta in np.geomspace(1e-5,.1,16)
     for v in [center-delta,center+delta] if 0<=v<=2]])


def inputs(channels, phase_case):
    z=np.zeros((channels,2),complex)
    z[:4]=regular_tetrahedron_spinors()/np.sqrt(2)
    if phase_case=='phase_shifted':
        z[:4]*=np.exp(1j*np.arange(4)*np.pi/2)[:,None]
    h=-(np.ones((channels,channels))-np.eye(channels))
    return z,h


def table(name,rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=dict(date='2026-10-16',task='T11',channels=[5,6],areas=AREAS,
        input='regular FL tetrahedron in first four channels; extra spinors zero',
        phase_cases=['baseline','phase_shifted'],hamiltonian='H=-sum_i<j(Eij+Eji), hopping=1, U=0',
        time='hbar=1; two exact complete-graph periods 2pi/L; uniform grid plus refined recurrence neighborhoods',
        time_points=len(TIMES),
        purpose='face activation, energy sharing and recurrence control; no thermalization claim',
        independent_check='small-K occupation-space sparse exponential evolution',tolerance=2e-10)
    protocol['normal_direction_merge_tolerance']=1e-8
    protocol['vacuum_label_norm_tolerance']=1e-10
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    arrays={}
    for l in [5,6]:
        for phase in ['baseline','phase_shifted']:
            z,h=inputs(l,phase)
            arrays[f'spinors_L{l}_{phase}']=z
            arrays[f'hopping_L{l}']=h
    np.savez_compressed(OUT/'inputs.npz',**arrays)
    rows,summaries=[],[]
    for l in [5,6]:
        for phase in ['baseline','phase_shifted']:
            z,h=inputs(l,phase)
            period=2*np.pi/l
            for k in AREAS:
                trajectory=[]
                for tau in TIMES:
                    t=tau*period
                    stats=fl_face_statistics(k,evolve_fl_spinors(z,h,t))
                    zz=stats['spinors']
                    energy_by_face=np.real(np.sum(h*(k*zz.conj()@zz.T),axis=1))
                    means=stats['mean_face_area']
                    face_vectors=face_vectors_from_spinors(zz)
                    lengths=np.linalg.norm(face_vectors,axis=1)
                    normals=face_vectors[lengths>1e-10]/lengths[lengths>1e-10,None]
                    distinct=[]
                    for normal in normals:
                        if all(np.linalg.norm(normal-old)>1e-8 for old in distinct):
                            distinct.append(normal)
                    row=dict(channels=l,K=k,phase_case=phase,time=t,period_fraction=tau,
                        expected_active_faces=stats['expected_active_faces'],
                        new_channel_mean_area=float(means[4:].sum()),
                        area_concentration=stats['area_concentration'],
                        energy=float(energy_by_face.sum()),
                        local_energy_rms_deviation=float(np.std(energy_by_face)),
                        total_area_residual=float(abs(means.sum()-k)))
                    row['classical_closure_residual']=float(np.linalg.norm(face_vectors.sum(axis=0)))
                    row['distinct_normal_directions']=len(distinct)
                    row['normal_span_rank']=int(np.linalg.matrix_rank(face_vectors,tol=1e-10))
                    for i in range(6):
                        row[f'face_{i}_area']=float(means[i]) if i<l else None
                        row[f'face_{i}_active_probability']=float(stats['active_probability'][i]) if i<l else None
                        row[f'face_{i}_energy']=float(energy_by_face[i]) if i<l else None
                    trajectory.append(row);rows.append(row)
                summaries.append(dict(channels=l,K=k,phase_case=phase,
                    singlet_dimension='d='+str(fixed_face_dimension(l,k)),
                    initial_energy=trajectory[0]['energy'],
                    initial_active_faces=trajectory[0]['expected_active_faces'],
                    maximum_sampled_active_faces=max(r['expected_active_faces'] for r in trajectory),
                    maximum_sampled_new_area=max(r['new_channel_mean_area'] for r in trajectory),
                    maximum_sampled_new_area_fraction=max(r['new_channel_mean_area'] for r in trajectory)/k,
                    recurrence_new_area_fraction=next(r['new_channel_mean_area']/k for r in trajectory if r['period_fraction']==1.),
                    maximum_distinct_normal_directions=max(r['distinct_normal_directions'] for r in trajectory),
                    minimum_normal_span_rank=min(r['normal_span_rank'] for r in trajectory),
                    maximum_classical_closure_residual=max(r['classical_closure_residual'] for r in trajectory),
                    maximum_energy_residual=max(abs(r['energy']-trajectory[0]['energy']) for r in trajectory),
                    maximum_area_residual=max(r['total_area_residual'] for r in trajectory)))
    table('dynamics.csv',rows);table('summary.csv',summaries)
    paths=[Path(__file__),ROOT/'code/python/lqg_scattering/intertwiners.py',
           ROOT/'code/python/lqg_scattering/spinors.py',ROOT/'code/python/lqg_scattering/tetrahedra.py']
    (OUT/'provenance.json').write_text(json.dumps(dict(
        numpy=np.__version__,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        artifacts={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['dynamics.csv','summary.csv','protocol.json','inputs.npz']}),indent=2)+'\n')
    print(f'Calculated {len(summaries)} controls / {len(rows)} samples using exact U(L) action')
    for r in summaries:
        if r['K']==10000: print(r)


if __name__=='__main__':main()

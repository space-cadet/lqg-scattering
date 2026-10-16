"""Reproducible classical rotor-count and initial energy concentration study."""
import csv
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
import numpy as np
from lqg_scattering.classical_rotors import initial_state,evolve,sample_microcanonical

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/t11-classical-rotors'
NAMES=['energy','kinetic_fraction','hot_pair_fraction','concentration','spread_second_moment','total_J_norm','orientation_norm_error','tangency_error']


def write_csv(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def split_rhat(x):
    # Two independent chains split into four, for scalar rotation-invariant readouts.
    a=x.reshape(2,2,-1).reshape(4,-1);m=a.shape[1]
    within=np.mean(np.var(a,axis=1,ddof=1));between=m*np.var(a.mean(axis=1),ddof=1)
    return float(np.sqrt(((m-1)*within/m+between/m)/within)) if within>0 else 1.


def block_se(x):
    a=x.reshape(2,20,-1).mean(axis=2).ravel()
    return float(a.std(ddof=1)/np.sqrt(len(a)))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol=dict(task='T11',model='3D linear rotors, H=sum J_i^2/2 + sum_ring(1-q_i.q_j); I=lambda=1',
        rotor_counts=[8,16,32,64],ratios=[1.,10.,100.],scalings=['fixed_packet','fixed_density'],seeds=[1701,1702,1703],
        packet_energy='ratio for fixed_packet; ratio*N/8 for fixed_density. Actual total energy also includes small initial potential.',
        initialization='q_i=normalize(e_z+0.05*N(0,1)); only J0=-J1=sqrt(packet_energy)*normalize(q0 cross q1)',
        constraints='unit orientations; q_i.J_i=0; total J=0; energy conserved. Total area is NOT constrained.',
        duration=2000.,sample_interval=.5,step='dt<=.01/sqrt(max(1,packet_energy/10)), rounded to divide sample interval',
        seeds_policy='same orientation seed across ratios and scalings; N8 scaling cases are identical controls',
        integrator='Strang kick-drift-kick; exact Rodrigues free rotations; no renormalization during evolution',
        windows=[[200.,1000.],[200.,2000.]],
        microcanonical=dict(chains=2,burn_sweeps=4000,samples_per_chain=4000,thin_sweeps=4,
            q_weight='det B^(-1/2)*(E-V)^(N-5/2), B=sum(I-q_i q_i^T)',
            momentum='independent tangent Gaussian, projection to total J=0, radial scaling to kinetic energy E-V',
            convergence='split Rhat<=1.05 for kinetic fraction, hot fraction and concentration; block errors also reported',
            warning='Rhat is a diagnostic, not a proof of mixing; references with larger Rhat are flagged'),
        local_energy='J_i^2/2 + half of each adjacent bond potential; sums to conserved H',
        distance='max absolute discrepancy of hot-pair fraction, kinetic fraction and normalized participation 1/(N*sum(e_i/E)^2) from microcanonical means',
        residence_thresholds=[.02,.05,.1],energy_drift_limit=5e-4,
        scope='classical preliminary finite-time study; no quantum, fixed-area or geometry claim',
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip())
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    summaries=[];refs=[];checks=[];started=time.monotonic()
    for n in protocol['rotor_counts']:
      for ratio in protocol['ratios']:
       for scaling in protocol['scalings']:
        for seed in protocol['seeds']:
         label=f'N{n}_R{int(ratio)}_{scaling}_S{seed}'
         packet=ratio*(n/8 if scaling=='fixed_density' else 1)
         q,j=initial_state(n,packet,seed)
         times,data,qf,jf,dt=evolve(q,j,.01/np.sqrt(max(1,packet/10)),protocol['duration'])
         drift=float(np.max(abs(data[:,0]/data[0,0]-1)))
         if drift>protocol['energy_drift_limit']:
             times,data,qf,jf,dt=evolve(q,j,dt/2,protocol['duration']);drift=float(np.max(abs(data[:,0]/data[0,0]-1)))
         assert drift<=protocol['energy_drift_limit'],(label,drift)
         assert data[:,5:8].max()<1e-8,(label,data[:,5:8].max())
         energy=data[0,0]
         chains=[];acceptances=[]
         for chain in range(2):
             # Distinct low-potential configurations; independent MC random streams.
             mq,_=initial_state(n,packet,seed+100000*(chain+1))
             if np.sum(1-np.sum(mq*np.roll(mq,-1,axis=0),axis=1))>=energy:mq=q.copy()
             samples,accept=sample_microcanonical(mq,energy,seed+10000+chain,burn=4000,samples=4000,thin=4)
             chains.append(samples);acceptances.append(accept)
         mc=np.array(chains)
         assert np.max(abs(mc[:,:,0]-energy))/energy<1e-10
         assert mc[:,:,5:8].max()<1e-8
         obs=np.column_stack([data[:,2],data[:,1],1/(n*data[:,3])])
         mobs=np.stack([mc[:,:,2],mc[:,:,1],1/(n*mc[:,:,3])],axis=2)
         target=mobs.mean(axis=(0,1));rhat=[split_rhat(mobs[:,:,c]) for c in range(3)]
         distance=np.max(abs(obs-target),axis=1)
         ref=dict(run=label,N=n,ratio=ratio,scaling=scaling,seed=seed,energy=energy,
             max_rhat=max(rhat),reference_pass=bool(max(rhat)<=1.05),acceptance_chain0=acceptances[0],acceptance_chain1=acceptances[1],
             hot_pair_mean=float(target[0]),hot_pair_exact_mean=2/n,
             hot_pair_SE=block_se(mobs[:,:,0]),kinetic_mean=float(target[1]),kinetic_SE=block_se(mobs[:,:,1]),
             participation_mean=float(target[2]),participation_SE=block_se(mobs[:,:,2]),
             hot_rhat=rhat[0],kinetic_rhat=rhat[1],participation_rhat=rhat[2])
         refs.append(ref)
         check=dict(run=label,dt=dt,relative_energy_drift=drift,max_total_J=float(data[:,5].max()),
             max_orientation_error=float(data[:,6].max()),max_tangency_error=float(data[:,7].max()),
             mc_relative_energy_error=float(np.max(abs(mc[:,:,0]-energy))/energy),mc_max_constraint_error=float(mc[:,:,5:8].max()))
         checks.append(check)
         for end in [1000.,2000.]:
             mask=(times>=200)&(times<=end)
             hot=data[mask,2]
             row=dict(run=label,N=n,ratio=ratio,scaling=scaling,seed=seed,packet_energy=packet,total_energy=energy,
                 energy_per_rotor=energy/n,dt=dt,window_start=200,window_end=end,reference_pass=ref['reference_pass'],
                 mean_hot_fraction=float(hot.mean()),equilibrium_hot_fraction=2/n,hot_fraction_std=float(hot.std()),
                 mean_kinetic_fraction=float(data[mask,1].mean()),reference_kinetic_fraction=float(target[1]),
                 mean_participation_fraction=float(obs[mask,2].mean()),reference_participation_fraction=float(target[2]),
                 mean_distance=float(distance[mask].mean()),maximum_hot_return=float(hot.max()),
                 mean_spread_second_moment=float(data[mask,4].mean()))
             for eps in [.02,.05,.1]:row[f'residence_{eps}']=float(np.mean(distance[mask]<=eps))
             summaries.append(row)
         np.savez_compressed(OUT/f'{label}.npz',times=times,readouts=data,distance=distance,
             initial_q=q,initial_J=j,final_q=qf,final_J=jf,microcanonical_readouts=mc,
             observable_reference=target,dt=dt)
         write_csv(OUT/'summary.csv',summaries);write_csv(OUT/'equilibrium.csv',refs);write_csv(OUT/'validation.csv',checks)
         print(f'{label}: dt={dt:.5g}, dE/E={drift:.2g}, hot={summaries[-1]["mean_hot_fraction"]:.3f} vs {2/n:.3f}, Rhat={max(rhat):.3f}, elapsed={time.monotonic()-started:.0f}s',flush=True)
    sources=[Path(__file__),ROOT/'code/classical/rotors.cpp',ROOT/'code/python/lqg_scattering/classical_rotors.py',ROOT/'code/python/test_classical_rotors.py']
    (OUT/'provenance.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=np.__version__,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')

if __name__=='__main__':main()

"""Execute the predeclared four-planar-rotor pilot and cutoff/classical controls."""
import json
import hashlib
from pathlib import Path
import numpy as np
from lqg_scattering.planar_rotors import momentum_basis,hamiltonian,momentum_state,evolve_readouts,classical_ensemble

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/t11-quantum-planar-rotors'
EDGES=[(0,1),(1,2),(2,3),(3,0)]

def main():
    times=np.linspace(0,20,101); summaries=[]
    angles=np.random.default_rng(20261016).uniform(-np.pi,np.pi,(2048,4))
    for m in [2,4]:
        previous=None; comparisons=[]
        for cutoff in [8,10,12,14,16]:
            path=OUT/f'quantum-m{m}-c{cutoff}.json'
            b=momentum_basis(4,cutoff); h=hamiltonian(b,EDGES)
            rows=evolve_readouts(h,b,momentum_state(b,[m,-m,0,0]),times)
            path.write_text(json.dumps(dict(m=m,cutoff=cutoff,dimension=len(b),rows=rows),indent=2)+'\n')
            print('quantum',m,cutoff,len(b),flush=True)
            if previous is not None:
                comparison=dict(cutoff=cutoff,previous_cutoff=cutoff-2)
                for field in ['kinetic','entropy','return_probability']:
                    comparison[field]=float(np.max(abs(np.array([r[field] for r in rows])-np.array([r[field] for r in previous]))))
                comparison['boundary_probability']=max(r['boundary_probability'] for r in rows)
                comparisons.append(comparison)
                if all(comparison[f]<1e-5 for f in ['kinetic','entropy','return_probability']) and comparison['boundary_probability']<1e-7:
                    break
            previous=rows
        else:
            raise RuntimeError(f'cutoff convergence failed m={m}: {comparisons[-1]}')
        p=np.tile([m,-m,0,0],(len(angles),1))
        coarse=classical_ensemble(angles,p,EDGES,times,dt=.005)
        step=.0025; classical_checks=[]
        for attempt in range(6):
            fine=classical_ensemble(angles,p,EDGES,times,dt=step)
            refinement=float(np.max(abs(np.array([r['kinetic'] for r in coarse])-np.array([r['kinetic'] for r in fine]))))
            classical_checks.append(dict(dt=step,max_kinetic_difference=refinement))
            if refinement<1e-3: break
            if attempt<5: coarse=fine; step/=2
        else: raise RuntimeError(f'classical refinement failed: {classical_checks}')
        (OUT/f'classical-m{m}.json').write_text(json.dumps(dict(seed=20261016,samples=len(angles),rows=fine,coarse_rows=coarse,max_kinetic_refinement=refinement,accepted_dt=step,refinement_checks=classical_checks),indent=2)+'\n')
        cold=np.array([sum(r['kinetic'][2:])/m**2 for r in rows])
        classical_cold=np.array([sum(r['kinetic'][2:])/m**2 for r in fine])
        summaries.append(dict(m=m,packet_energy=m*m,mean_total_energy=m*m+4,accepted_cutoff=cutoff,dimension=len(b),cutoff_checks=comparisons,
                              max_norm_error=max(r['norm_error'] for r in rows),max_energy_error=max(r['energy_error'] for r in rows),
                              classical_max_energy_error=max(r['max_energy_error'] for r in fine),classical_max_momentum_error=max(r['max_total_momentum_error'] for r in fine),
                              classical_refinement=refinement,quantum_late_cold_fraction=float(cold[times>=10].mean()),classical_late_cold_fraction=float(classical_cold[times>=10].mean())))
        print('completed',summaries[-1],flush=True)
    sources=[Path(__file__),ROOT/'code/python/lqg_scattering/planar_rotors.py',OUT/'protocol.md']
    (OUT/'summary.json').write_text(json.dumps(dict(cases=summaries,source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')

if __name__=='__main__': main()

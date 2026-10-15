"""Check FL hopping action and binomial faces with sparse occupation dynamics."""
from pathlib import Path
import json
import csv
import hashlib
import numpy as np
from scipy.sparse.linalg import expm_multiply
from lqg_scattering.intertwiners import fixed_area_state,evolve_fl_spinors,fl_face_statistics
from lqg_scattering.hamiltonian import build_fixed_number_model,assemble_hamiltonian
from fl_face_activation import inputs

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/fl-face-activation'


def main():
    checks=[]
    def check(name,a,b,tol=2e-10):
        error=float(np.max(abs(np.asarray(a)-np.asarray(b))))
        assert error<tol,(name,error,tol)
        checks.append(dict(name=name,residual=error,tolerance=tol))
    for l in [5,6]:
        edges=[(i,j) for i in range(l) for j in range(i+1,l)]
        for k in [1,2]:
            model=build_fixed_number_model(l,2*k,edges)
            hfull=assemble_hamiltonian(model,1.,0.)
            for phase in ['baseline','phase_shifted']:
                z,h=inputs(l,phase)
                _,initial=fixed_area_state(k,spinors=z)
                seed=np.zeros(len(model['occupations']),complex)
                for n,amp in initial.items():seed[model['index'][n]]=amp
                for tau in [0.,.1,.25,.5,1.]:
                    t=2*np.pi/l*tau
                    direct=expm_multiply(-1j*t*hfull,seed)
                    evolved_z=evolve_fl_spinors(z,h,t)
                    _,predicted=fixed_area_state(k,spinors=evolved_z)
                    ket=np.zeros_like(seed)
                    for n,amp in predicted.items():ket[model['index'][n]]=amp
                    overlap=np.vdot(ket,direct)
                    check(f'ket-L{l}-K{k}-{phase}-{tau}',np.linalg.norm(direct-ket*overlap/abs(overlap)),0.)
                    stats=fl_face_statistics(k,evolved_z)
                    p=abs(direct)**2
                    ns=model['occupations'][:,::2]+model['occupations'][:,1::2]
                    check(f'means-L{l}-K{k}-{phase}-{tau}',p@ns/2,stats['mean_face_area'])
                    check(f'active-L{l}-K{k}-{phase}-{tau}',p@(ns>0),stats['active_probability'])
                    check(f'variance-L{l}-K{k}-{phase}-{tau}',p@(ns**2)/4-(p@ns/2)**2,stats['face_area_variance'])
                    energy=float(np.vdot(direct,hfull@direct).real)
                    zz=stats['spinors']
                    analytic=float(np.sum(h*(k*zz.conj()@zz.T)).real)
                    check(f'energy-L{l}-K{k}-{phase}-{tau}',energy,analytic)
                    local=np.zeros(l)
                    for (i,j),operator in model['bonds'].items():
                        value=-.5*np.vdot(direct,operator@direct).real
                        local[i]+=value;local[j]+=value
                    check(f'local-energy-L{l}-K{k}-{phase}-{tau}',local,
                          np.real(np.sum(h*(k*zz.conj()@zz.T),axis=1)))
    for n,row in enumerate(csv.DictReader((OUT/'summary.csv').open())):
        check(f'recurrence-{n}',float(row['recurrence_new_area_fraction']),0.)
        check(f'energy-conservation-{n}',float(row['maximum_energy_residual']),0.,2e-7)
        check(f'area-conservation-{n}',float(row['maximum_area_residual']),0.,2e-7)
        check(f'classical-closure-{n}',float(row['maximum_classical_closure_residual']),0.)
        check(f'normal-span-{n}',int(row['minimum_normal_span_rank']),3)
        check(f'maximum-distinct-directions-{n}',int(row['maximum_distinct_normal_directions']),5)
    report=dict(status='passed',comparisons=len(checks),
        independence='direct sparse full-occupation exponential and independently constructed FL kets, K=1,2; large-area recurrence and conservation checks',
        maximum_residual=max(c['residual'] for c in checks),
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__),ROOT/'code/python/lqg_scattering/hamiltonian.py']},
        maximum_residual_over_tolerance=max(c['residual']/c['tolerance'] for c in checks),checks=checks)
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:v for k,v in report.items() if k!='checks'})


if __name__=='__main__':main()

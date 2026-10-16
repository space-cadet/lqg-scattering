"""Exact closed geometric-channel evolution; retain observables, not state histories."""
import csv
import gc
import hashlib
import json
from itertools import combinations
from pathlib import Path
import time
import numpy as np
import scipy
from scipy.sparse import diags
from scipy.sparse.linalg import expm_multiply
from lqg_scattering.channel_dynamics import (build_basis,build_hopping,initial_state,build_geometry,readouts,geometry_readout)
from lqg_scattering.hamiltonian import hopping_matrix
from lqg_scattering.intertwiners import evolve_fl_spinors,fl_face_statistics

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/t11-geometric-redistribution'
TOL=2e-9

def csv_write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    OUT.mkdir(parents=True,exist_ok=True);times=np.linspace(0,20,101)
    summary=[];validation={};inputs={};geometry=[];all_rows=[];performance=[]
    for l in [4,6,8]:
        tick=time.perf_counter();model=build_basis(l,4);ops,pairs,checks=build_geometry(model)
        checks.update(model['validation']);b=model['embedding'];numbers=model['numbers'];dim=len(numbers)
        diagonal=np.sum(numbers*(numbers+2),axis=1)/4
        seeds={name:initial_state(model,phi,sharp) for name,phi,sharp in [('regular_sharp',90,True),('deformed_sharp',30,True),('regular_FL',90,False)]}
        for name,(seed,z,p) in seeds.items():
            nz=np.flatnonzero(abs(seed)>1e-14)
            inputs[f'L{l}_{name}']=dict(projection_probability=p,spinors_real=z.real.tolist(),spinors_imag=z.imag.tolist(),
                                       coefficients=[dict(index=int(i),real=float(seed[i].real),imag=float(seed[i].imag),counts=numbers[i].tolist()) for i in nz])
            if name.endswith('sharp'):
                free=seed*np.exp(-1j*diagonal*7.3)
                checks[name+'_no_hopping_return']=float(abs(abs(np.vdot(seed,free))**2-1))
        performance.append(dict(L=l,stage='basis_and_geometry',seconds=time.perf_counter()-tick,magnetic_dimension=len(model['occupations']),singlet_dimension=dim))
        print('built',l,len(model['occupations']),dim,performance[-1]['seconds'],flush=True)
        for graph,edges,weight in [('ring',[(i,(i+1)%l) for i in range(l)],.5),('complete',list(combinations(range(l),2)),1/(l-1))]:
            tick=time.perf_counter();hop,leak,local_hop=build_hopping(model,edges,weight,local=True);checks[graph+'_projection_leakage']=leak
            checks[graph+'_hermiticity']=float(np.max(abs((hop-hop.conj().T).data),initial=0))
            one=np.zeros((l,l))
            for i,j in edges:one[i,j]=one[j,i]=-weight
            for alpha in [0.,1.,5.]:
                h=(alpha*diags(diagonal)-hop).tocsr()
                for name,(seed,z,p) in seeds.items():
                    run=f'L{l}_{graph}_a{alpha:g}_{name}';start=time.perf_counter()
                    states=expm_multiply(-1j*h,seed,start=0,stop=20,num=101,traceA=-1j*h.diagonal().sum())
                    obs=readouts(states,model,seed,h)
                    local_energies=alpha*obs['casimir']
                    for site,operator in enumerate(local_hop):
                        local_energies[:,site]-=np.einsum('ij,ij->i',states.conj(),(operator@states.T).T).real
                    checks[run+'_local_energy_sum']=float(np.max(abs(local_energies.sum(axis=1)-obs['energy'])))
                    checks[run+'_norm']=float(obs['norm_error'].max());checks[run+'_energy']=float(obs['energy_error'].max())
                    if alpha==0 and name=='regular_FL':
                        for j in [0,10,25,50,100]:
                            analytic=fl_face_statistics(4,evolve_fl_spinors(z,one,times[j]))
                            checks[run+f'_analytic_area_{j}']=float(np.max(abs(obs['area'][j]-analytic['mean_face_area'])))
                            checks[run+f'_analytic_active_{j}']=abs(float(obs['expected_active'][j])-analytic['expected_active_faces'])
                            checks[run+f'_analytic_concentration_{j}']=abs(float(obs['concentration'][j])-analytic['area_concentration'])
                    # Independent magnetic-space propagation for selected interacting controls.
                    if l==6 and alpha==1 and name=='regular_sharp':
                        for j in [1,10]:
                            maghop=sum((weight*hopping_matrix(model['occupations'],model['index'],e) for e in edges))
                            magnum=model['occupations'][:,::2]+model['occupations'][:,1::2]
                            mh=diags(np.sum(magnum*(magnum+2),axis=1)/4)-maghop
                            reference=expm_multiply(-1j*times[j]*mh,b@seed,traceA=-1j*times[j]*mh.diagonal().sum())
                            checks[run+f'_magnetic_propagation_{j}']=float(np.max(abs(reference-b@states[j])))
                            del maghop,mh,reference
                    for j in [0,10,25,50,100]:
                        geometry.append(dict(run=run,L=l,graph=graph,alpha=alpha,preparation=name,time=float(times[j]),
                                             **geometry_readout(states[j],model,ops,pairs)))
                    for j,t in enumerate(times):
                        row=dict(run=run,L=l,K=4,graph=graph,alpha=alpha,preparation=name,time=float(t))
                        for field in ['expected_active','receiver_area_fraction','receiver_casimir_fraction','concentration','return_probability','norm_error','energy_error','energy']:
                            row[field]=float(obs[field][j])
                        for site in range(8):
                            for field in ['area','casimir','entropy']:
                                row[f'{field}_{site}']=float(obs[field][j,site]) if site<l else ''
                        for site in range(8):row[f'local_energy_{site}']=float(local_energies[j,site]) if site<l else ''
                        row['receiver_local_energy']=float(local_energies[j,4:].sum())
                        for n in range(9):row[f'p_active_{n}']=float(obs['active_probability'][j,n]) if n<=l else 0.
                        all_rows.append(row)
                    late=times>=10
                    row=dict(run=run,L=l,K=4,graph=graph,alpha=alpha,preparation=name,dimension=dim,
                             projection_probability=p,initial_casimir=float(obs['casimir'][0].sum()),energy=float(obs['energy'][0]),
                             late_mean_active=float(obs['expected_active'][late].mean()),
                             late_receiver_area_fraction=float(obs['receiver_area_fraction'][late].mean()),
                             late_receiver_casimir_fraction=float(obs['receiver_casimir_fraction'][late].mean()),
                             late_receiver_local_energy=float(local_energies[late,4:].sum(axis=1).mean()),
                             late_probability_at_least5=float(obs['active_probability'][late,5:].sum(axis=1).mean()),
                             late_probability_all_channels=float(obs['active_probability'][late,l].mean()),
                             maximum_probability_all_channels=float(obs['active_probability'][:,l].max()),
                             maximum_norm_error=float(obs['norm_error'].max()),maximum_energy_error=float(obs['energy_error'].max()),seconds=time.perf_counter()-start)
                    summary.append(row);performance.append(dict(L=l,stage=run,seconds=row['seconds']))
                    print('completed',run,'seconds',round(row['seconds'],2),'extra_area',round(row['late_receiver_area_fraction'],4),'p5plus',round(row['late_probability_at_least5'],4),flush=True)
                    del states,obs,local_energies
            performance.append(dict(L=l,stage=graph+'_all_runs',seconds=time.perf_counter()-tick))
            del hop,h,local_hop
        assert max(checks.values())<2e-8,(l,sorted(checks.items(),key=lambda r:r[1])[-5:])
        validation[f'L{l}']=checks
        csv_write(OUT/'summary.csv',summary);csv_write(OUT/'dynamics.csv',all_rows)
        (OUT/'geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
        (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
        (OUT/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
        (OUT/'performance.json').write_text(json.dumps(performance,indent=2)+'\n')
        del model,ops,b,seeds;gc.collect()
    sources=[Path(__file__),OUT/'protocol.md',ROOT/'code/python/lqg_scattering/channel_dynamics.py']
    (OUT/'provenance.json').write_text(json.dumps(dict(numpy=np.__version__,scipy=scipy.__version__,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}),indent=2)+'\n')

if __name__=='__main__':main()

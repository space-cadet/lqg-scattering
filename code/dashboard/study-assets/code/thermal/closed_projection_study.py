"""Examine double-singlet projection of T9's selected J=1 two-FL state.

Shared recoupling-volume routines are in lqg_scattering.thermal_projection.
Run from the repo root with PYTHONPATH=code/python. Separate artifacts preserve
all earlier unprojected calculations.
"""
from pathlib import Path
import csv
import hashlib
import json
import platform
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import compare_j1_spin_methods as model
from lqg_scattering.singlets import load_block, ZERO_FACTOR
from lqg_scattering.thermal_projection import (sector_trace_data,evaluate_traces,
    coefficient_weights,VOLUME_NORM_COEFFICIENT,singlet_volume_diagonals)

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results'/'thermal-closed-projection'
FIG=ROOT/'figures'/'thermal-closed-projection'
AREA_MAX=50
TOL=2e-10


def verify_catalogue(traces):
    errors=[]
    for area in range(2,13):
        reference=np.zeros((5,6))
        with (ROOT/'results'/'closed-basis-volume'/f'states_k{area}.csv').open() as f:
            for row in csv.DictReader(f):
                a=2*(float(row['j1'])+float(row['j2'])); k=float(row['k_pair'])
                F=(a/2-k)*(a/2+k+1)
                mono=np.array([F*F,a*a,1,F*a,F,a])
                # Kernel probability is checked against matrices separately.
                obs=np.array([1,float(row['rs_mean']),float(row['rs_second_moment']),0,
                              float(row['all_four_faces_active']=='True')])
                reference+=np.outer(obs,mono)
        for component in [0,1,2,4]:
            residual=float(np.max(abs(reference[component]-traces[area,component])))
            scale=max(1,float(np.max(abs(reference[component]))))
            assert residual < TOL*scale,(area,component,residual,scale)
            errors.append(dict(area=area,component=component,absolute_error=residual,relative_error=residual/scale))
    return errors


def verify_kernel():
    errors=[]
    for area in [2,3,4]:
        metadata=json.loads((ROOT/'results/closed-basis-volume'/f'metadata_k{area}.json').read_text())
        with np.load(ROOT/'results/closed-basis-volume'/f'operators_k{area}.npz',allow_pickle=False) as archive:
            for number,block in enumerate(metadata['blocks']):
                _,_,_,kernel=singlet_volume_diagonals(block['twice_spins'])
                values,vectors=np.linalg.eigh(load_block(archive,number,'q012'))
                mask=abs(values)<=ZERO_FACTOR*max(1,float(np.max(abs(values))))
                direct=np.sum(abs(vectors[:,mask])**2,axis=1)
                error=float(np.max(abs(kernel-direct)))
                assert error<TOL
                errors.append(error)
    return dict(areas=[2,3,4],block_count=len(errors),max_absolute_difference=max(errors))


def verify_projection():
    errors=[]
    for q in [0,2,4]:
        basis,generators,projectors=model.sector_operators(q)
        V=projectors[0]; P=V@V.conj().T
        for b in [.5,1,4]:
            C=model.coefficient_polynomial(q,b)
            D=P@C@P.conj()  # right basis is conjugate, hence P_R^T=P
            single=float(np.linalg.norm(P@C)**2)
            double=float(np.linalg.norm(D)**2)
            mass=float(model.magnetic_probabilities(q,b)[0])
            residual=sum(np.linalg.norm(g@D)**2+np.linalg.norm(D@g)**2 for g in generators)
            leakage=float(np.linalg.norm(P@C@(np.eye(len(P))-P))**2)
            assert max(abs(single-double),abs(double-mass),residual,leakage)<TOL
            errors.append(dict(q=q,beta=b,single_probability=single,double_probability=double,
                               marginal_probability=mass,closure_squared_residual=float(residual),
                               cross_spin_leakage=leakage))
    return errors


def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    protocol=dict(date='2026-10-13',initial_J=1,faces=4,
        state='normalized (P_L,0 tensor P_R,0) U_beta (F12 FL tensor conjugate F12 FL)',
        input='F12 dagger vacuum / sqrt(2) in each copy',temperature_range=[.05,2],
        occupation_probability_cutoff=160,volume_area_cutoff=AREA_MAX,
        raw_volume='RS project units, gamma=0.2375, hbar=1, four triples',
        volume_tail_bound='||V_RS|| <= 4 gamma^(3/2) sqrt(2/9) A^(3/2)',
        projection='separate ordinary singlet support on both copies',tolerance=TOL,
        verification='direct double projection in q=0,2,4; catalogue traces K=2..12; recoupling probabilities')
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    start=time.time(); traces=[]; sectors=[]
    for area in range(AREA_MAX+1):
        trace,dimension,blocks=sector_trace_data(area)
        traces.append(trace); sectors.append(dict(area=area,dimension=dimension,canonical_blocks=blocks))
        if area%10==0: print(f'Volume traces through area {area}; {time.time()-start:.1f}s',flush=True)
    traces=np.array(traces)
    np.savez_compressed(OUT/'singlet_sector_traces.npz',traces=traces,areas=np.arange(AREA_MAX+1))
    catalogue_checks=verify_catalogue(traces)
    projection_checks=verify_projection()
    kernel_checks=verify_kernel()
    betas=np.unique(np.concatenate((1/np.geomspace(.05,2,81),[.5,1,2,4,8,20])))
    rows=[]; sector_rows=[]; max_mass_difference=0.0
    q=np.arange(0,model.QMAX+1,2); A=q/2
    for b in betas:
        probability=np.array([model.magnetic_probabilities(int(n),float(b))[0] for n in q])
        success=float(probability.sum())
        expectation=evaluate_traces(traces,float(b))
        difference=float(np.max(abs(expectation[:,0]-probability[:AREA_MAX+1])))
        max_mass_difference=max(max_mass_difference,difference)
        assert difference<TOL
        if b in [.5,1,2,4,8,20]:
            other=np.array([model.recoupling_probabilities(int(n),float(b))[0] for n in q])
            assert np.max(abs(other-probability))<model.ABS_TOL
        tail=probability[AREA_MAX+1:]; tail_A=A[AREA_MAX+1:]
        external_probability=model.tail_bound(float(b))
        volume_tail=(float(np.dot(tail,VOLUME_NORM_COEFFICIENT*tail_A**1.5))
                     +VOLUME_NORM_COEFFICIENT*model.tail_bound(float(b),2))/success
        second_tail=(float(np.dot(tail,VOLUME_NORM_COEFFICIENT**2*tail_A**3))
                     +VOLUME_NORM_COEFFICIENT**2/8*model.tail_bound(float(b),3))/success
        mean=float(np.dot(A,probability)/success)
        variance=float(np.dot(A*A,probability)/success-mean*mean)
        vol=float(expectation[:,1].sum()/success)
        vol2=float(expectation[:,2].sum()/success)
        kernel=float(expectation[:,3].sum()/success)
        active=float(expectation[:,4].sum()/success)
        missing=float(tail.sum())+external_probability
        assert variance>=-TOL and vol2-vol*vol>=-TOL
        rows.append(dict(temperature_kBT_over_hbar_omega=float(1/b),beta_hbar_omega=float(b),
            projection_success_probability=success,conditional_mean_area=mean,
            conditional_area_sd=float(np.sqrt(max(0,variance))),
            conditional_rs_volume_lower=vol,conditional_rs_volume_upper=vol+volume_tail,
            conditional_rs_second_lower=vol2,conditional_rs_second_upper=vol2+second_tail,
            conditional_rs_volume_sd=float(np.sqrt(max(0,vol2-vol*vol))),
            conditional_kernel_probability_lower=kernel,conditional_kernel_probability_upper=kernel+missing/success,
            conditional_four_active_faces_lower=active,conditional_four_active_faces_upper=active+missing/success,
            full_closed_probability_tail_bound=external_probability,
            conditional_volume_tail_bound=volume_tail,conditional_volume_second_tail_bound=second_tail,
            normalization_probability_error_bound=external_probability/success))
        if b in [.5,1,2,4,8,20]:
            for n,p in zip(q,probability):
                sector_rows.append(dict(beta_hbar_omega=float(b),area=int(n//2),
                                        probability=float(p/success)))
    rows.sort(key=lambda r:r['temperature_kBT_over_hbar_omega'])
    for filename,content in [('temperature_summary.csv',rows),('area_distribution.csv',sector_rows)]:
        with (OUT/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(content[0]),lineterminator='\n'); w.writeheader(); w.writerows(content)
    source_paths=[Path(__file__),Path(model.__file__),ROOT/'code/python/lqg_scattering/thermal_projection.py']
    report=dict(catalogue_checks=catalogue_checks,direct_projection_checks=projection_checks,
        archived_kernel_controls=kernel_checks,
        max_sector_mass_difference=max_mass_difference,
        max_volume_tail_bound=max(r['conditional_volume_tail_bound'] for r in rows),
        max_second_moment_tail_bound=max(r['conditional_volume_second_tail_bound'] for r in rows),
        max_normalization_probability_error_bound=max(r['normalization_probability_error_bound'] for r in rows),
        sectors=sectors,python=platform.python_version(),numpy=np.__version__,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths})
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    plt.rcParams.update({'font.size':10,'axes.labelsize':10,'axes.titlesize':11,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,3,figsize=(10.5,3.5),layout='constrained')
    temp=[r['temperature_kBT_over_hbar_omega'] for r in rows]
    for ax,key,label,title in zip(axes,['projection_success_probability','conditional_mean_area','conditional_rs_volume_lower'],
        ['Probability of separate closure',r'Mean total linear area $\langle A\rangle$','Positive RS volume (project units)'],
        ['(a) Retained fraction','(b) Area after projection','(c) Volume after projection']):
        ax.plot(temp,[r[key] for r in rows],color='#0072B2',lw=2)
        ax.set_xlabel(r'Temperature $k_BT/(\hbar\omega)$'); ax.set_ylabel(label); ax.set_title(title); ax.grid(alpha=.25)
    axes[0].set_ylim(0,1.02)
    fig.savefig(FIG/'closed_projection_temperature.pdf',bbox_inches='tight')
    fig.savefig(FIG/'closed_projection_temperature.png',dpi=300,bbox_inches='tight'); plt.close(fig)
    for b in [8,4,2,1,.5]:
        r=min(rows,key=lambda r:abs(r['beta_hbar_omega']-b))
        print('T*={:.3g}: success={:.7g}, area={:.7g}, V={:.7g}, kernel={:.7g}, fourfaces={:.7g}'.format(
            1/b,r['projection_success_probability'],r['conditional_mean_area'],r['conditional_rs_volume_lower'],
            r['conditional_kernel_probability_lower'],r['conditional_four_active_faces_lower']),flush=True)
    print('PASS:',len(rows),'temperatures; max volume tail',report['max_volume_tail_bound'],flush=True)


if __name__=='__main__': main()

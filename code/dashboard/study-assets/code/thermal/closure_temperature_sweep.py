"""Temperature dependence of ordinary per-copy closure for the selected J=1 T9 state.

Reuses the established magnetic and recoupling calculations. No singlet
postselection or cutoff renormalization. Outputs are separate from prior runs.
"""
from pathlib import Path
import csv
import hashlib
import json
import platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import compare_j1_spin_methods as model

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results' / 'thermal-closure-temperature'
FIG = ROOT / 'figures' / 'thermal-closure-temperature'
TOL = 2e-10


def evaluate(b):
    norm = mean_q = q2 = defect = singlet = 0.0
    minimum = 0.0
    for q in range(model.QMAX + 1):
        p = model.magnetic_probabilities(q, b)
        minimum = min(minimum, float(p.min()))
        spin = np.arange(q % 2, q + 1, 2) / 2
        mass = float(p.sum())
        norm += mass
        mean_q += q * mass
        q2 += q*q * mass
        defect += float(np.dot(spin*(spin+1), p))
        if q % 2 == 0:
            singlet += float(p[0])
    tails = [model.tail_bound(b, k) for k in range(3)]
    expected_q = 2 + 12 / np.expm1(b)
    assert minimum >= -TOL
    assert abs(norm-1) < TOL + tails[0]
    assert abs(mean_q-expected_q) < TOL*max(1, expected_q) + tails[1]
    denominator = q2/4 + mean_q/2  # <A(A+1)>, A=q/2
    relative = defect / denominator
    assert 0 <= singlet <= 1 + TOL and 0 <= relative <= 1 + TOL
    return dict(temperature_kBT_over_hbar_omega=1/b, beta_hbar_omega=b,
                retained_probability=norm, singlet_probability=singlet,
                closure_defect_casimir=defect, closure_defect_rms=np.sqrt(defect),
                mean_linear_area=mean_q/2, mean_area_casimir=denominator,
                relative_defect_squared=relative, relative_defect_rms=np.sqrt(relative),
                omitted_probability_bound=tails[0], omitted_defect_bound=tails[2]/4+tails[1]/2,
                minimum_probability=minimum)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    protocol = dict(state='U_beta(|J=1,F12>_L tensor |conjugate J=1,F12>_R)',
                    faces=4, input='normalized F12 dagger vacuum / sqrt(2) in each copy',
                    observable='ordinary per-copy G=sum_i J_i; G^2=S(S+1)',
                    units='angular momentum in hbar units; T*=kBT/(hbar omega)',
                    q_max=model.QMAX, temperature_range=[0.05, 2.0],
                    curve_points=121, tolerance=TOL, normalization='no cutoff renormalization',
                    relative_measure='<G^2>/<A(A+1)>, A=q/2',
                    check_betas=[0.5,1.0,2.0,4.0,8.0,20.0],
                    transformed_and_combined_closure='exactly zero by conjugation/dual-copy invariance')
    (OUT/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    betas = np.unique(np.concatenate((1/np.geomspace(.05,2,121), [.5,1,2,4,8,20])))
    rows = sorted((evaluate(float(b)) for b in betas), key=lambda r:r['temperature_kBT_over_hbar_omega'])
    validations = []
    for b in protocol['check_betas']:
        maximum = defect = singlet = 0.0
        for q in range(model.QMAX+1):
            rec = model.recoupling_probabilities(q,b)
            mag = model.magnetic_probabilities(q,b)
            maximum = max(maximum,float(np.max(abs(rec-mag))))
            s = np.arange(q % 2,q+1,2)/2
            defect += float(np.dot(s*(s+1),rec))
            if q % 2 == 0:
                singlet += float(rec[0])
        row = min(rows,key=lambda r:abs(r['beta_hbar_omega']-b))
        assert maximum < model.ABS_TOL
        assert abs(defect-row['closure_defect_casimir']) < TOL*max(1,defect)
        assert abs(singlet-row['singlet_probability']) < TOL
        validations.append(dict(beta=b,max_method_probability_difference=maximum,
                                defect_difference=abs(defect-row['closure_defect_casimir'])))
    old = json.loads((ROOT/'results/thermal-j1-spin/j1_spin_method_summary.json').read_text())
    parity = 0.0
    for reference in old['temperature_results']:
        row = min(rows,key=lambda r:abs(r['beta_hbar_omega']-reference['beta_hbar_omega']))
        parity = max(parity,abs(row['closure_defect_casimir']-reference['mean_per_copy_closure_casimir_retained']),
                     abs(row['singlet_probability']-reference['singlet_probability_retained']))
    assert parity < TOL
    assert all(a['closure_defect_casimir'] < b['closure_defect_casimir'] for a,b in zip(rows,rows[1:]))
    assert all(a['singlet_probability'] > b['singlet_probability'] for a,b in zip(rows,rows[1:]))
    relative_increases = all(a['relative_defect_squared'] < b['relative_defect_squared'] for a,b in zip(rows,rows[1:]))
    with (OUT/'closure_temperature.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    verification=dict(method_checks=validations,saved_result_max_difference=parity,
                      monotonic_defect_increase=True,monotonic_singlet_decrease=True,
                      monotonic_relative_defect_increase=relative_increases,
                      maximum_relative_defect=max(rows,key=lambda r:r['relative_defect_squared']),
                      max_normalization_error=max(abs(r['retained_probability']-1) for r in rows),
                      max_omitted_probability_bound=max(r['omitted_probability_bound'] for r in rows),
                      max_omitted_defect_bound=max(r['omitted_defect_bound'] for r in rows),
                      python=platform.python_version(),numpy=np.__version__,
                      source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in [Path(__file__),Path(model.__file__)]})
    (OUT/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
    plt.rcParams.update({'font.size':10,'axes.labelsize':10,'axes.titlesize':11,'pdf.fonttype':42})
    fig, axes=plt.subplots(1,3,figsize=(10.5,3.5),layout='constrained')
    temp=np.array([r['temperature_kBT_over_hbar_omega'] for r in rows])
    series=[('closure_defect_rms',r'RMS residual flux $\sqrt{\langle G^2\rangle}$','(a) Closure defect'),
            ('singlet_probability',r'Exact closure probability $P(S=0)$','(b) Closed fraction'),
            ('relative_defect_rms',r'$\sqrt{\langle G^2\rangle/\langle A(A+1)\rangle}$','(c) Relative defect')]
    for ax,(key,label,title) in zip(axes,series):
        ax.plot(temp,[r[key] for r in rows],color='#0072B2',lw=2)
        ax.set_xlabel(r'Temperature $k_BT/(\hbar\omega)$')
        ax.set_ylabel(label); ax.set_title(title); ax.grid(alpha=.25)
        if key=='closure_defect_rms': ax.set_yscale('log')
        else: ax.set_ylim(0,1.02)
    fig.savefig(FIG/'closure_temperature.pdf',bbox_inches='tight')
    fig.savefig(FIG/'closure_temperature.png',dpi=300,bbox_inches='tight')
    plt.close(fig)
    for b in [20,8,4,2,1,.5]:
        row=min(rows,key=lambda r:abs(r['beta_hbar_omega']-b))
        print('T*={:.3g}: D={:.9g}, RMS={:.7g}, Pclosed={:.7g}, relative_RMS={:.7g}'.format(
            1/b,row['closure_defect_casimir'],row['closure_defect_rms'],row['singlet_probability'],row['relative_defect_rms']))
    print('PASS:',len(rows),'temperatures; six recoupling controls; parity=',parity)


if __name__=='__main__': main()

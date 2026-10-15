"""Independent oscillator/SVD and saved-geometry checks of T9 entropy data."""
from pathlib import Path
import csv
import json
import hashlib
import numpy as np
from scipy.special import xlogy
import compare_j1_spin_methods as oscillator
from lqg_scattering.thermal_entanglement import labels, raw_spectrum, summarize
from lqg_scattering.thermal_projection import evaluate_traces

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'results/thermal-closed-entanglement'
TOL = 2e-10


def main():
    checks = []
    def check(name, actual, expected, tol=TOL):
        error = float(np.max(np.abs(np.asarray(actual)-np.asarray(expected))))
        assert error <= tol, (name,error,tol)
        checks.append(dict(name=name, absolute_residual=error, tolerance=tol))
    traces = np.load(ROOT/'results/thermal-closed-projection/singlet_sector_traces.npz')['traces']
    for b in [.2,.5,1.,2.,4.,20.]:
        ix = labels(50)
        c,a,d = raw_spectrum(b,ix)
        probability = np.bincount(ix[:,0],weights=d*a)
        check(f'trace-probability-b{b}',probability,evaluate_traces(traces,b)[:,0])
    for k in range(51):
        ix = labels(k); ix=ix[ix[:,0]==k]
        check(f'dimension-K{k}',np.sum((k-ix[:,1]-ix[:,2]+1)**2),
              (k+1)*(k+2)**2*(k+3)//12,0.)
    cold=summarize(40.,12)[0]
    check('cold-entropy',cold['entropy_nats'],0.)
    check('cold-mean-area',cold['mean_area'],1.)
    check('cold-purity',cold['purity'],1.)
    # No coefficient-polynomial construction here: exponentiate each oscillator
    # pair's squeeze generator, assemble occupation amplitudes and project with
    # separately diagonalized SU(2) Casimirs before an SVD.
    direct_blocks = {}
    for b in [.5,1.,2.,4.]:
        for cutoff in [40,64]:
            tables = oscillator.mode_squeezes(b,cutoff)
            for q in [0,2,4]:
                basis, generators, projectors = oscillator.sector_operators(q)
                v = projectors[0]
                full = oscillator.coefficient_from_modes(q,tables)
                block = v.conj().T @ full @ v
                singular = np.linalg.svd(block,compute_uv=False)
                ix=labels(q//2); ix=ix[ix[:,0]==q//2]
                c,a,d=raw_spectrum(b,ix)
                expected=np.repeat(a,d)
                check(f'oscillator-spectrum-b{b}-q{q}-cut{cutoff}',
                      np.sort(singular**2),np.sort(expected))
                norm=np.sum(singular**2)
                p=singular**2/norm
                e=expected/expected.sum()
                check(f'conditional-entropy-b{b}-q{q}-cut{cutoff}',
                      -np.sum(xlogy(p,p)),-np.sum(xlogy(e,e)))
                direct_blocks[b,q,cutoff]=(basis,v,block)
    # Independent F creator matrices between occupation spaces test the new
    # phase-sensitive joint-creation correlator sector by sector.
    for b in [.5,1.,2.,4.]:
        for q in [0,2]:
            basis,v,c0=direct_blocks[b,q,64]
            basis1,v1,c1=direct_blocks[b,q+2,64]
            index={tuple(n):i for i,n in enumerate(basis1)}
            f=np.zeros((len(basis1),len(basis)))
            for col,n in enumerate(basis):
                for i,j,sign in [(0,3,1),(1,2,-1)]:
                    dest=n.copy();dest[i]+=1;dest[j]+=1
                    f[index[tuple(dest)],col]+=sign*np.sqrt((n[i]+1)*(n[j]+1))
            projected=v1.conj().T @ f @ v
            direct=np.trace(c1.conj().T @ projected @ c0 @ projected.T).real
            ix=labels(q//2);ix=ix[ix[:,0]==q//2]
            amp,_,d=raw_spectrum(b,ix)
            dest=ix.copy();dest[:,0]+=1;dest[:,1]+=1
            amp1=raw_spectrum(b,dest)[0]
            k,r,l=ix.T
            expected=np.sum(d*amp*amp1*(r+1)*(k-l+2))
            check(f'joint-creation-b{b}-q{q}',direct,expected)
    rows=list(csv.DictReader((OUT/'temperature_summary.csv').open()))
    for n,row in enumerate(rows):
        b=float(row['beta_hbar_omega']); cutoff=int(row['area_cutoff'])
        saved={k:float(v) for k,v in row.items()}
        result,sectors,_=summarize(b,cutoff+12)
        check(f'entropy-decomposition-{n}',saved['entropy_nats'],
              saved['area_entropy_nats']+saved['within_area_entropy_nats'])
        check(f'conditional-sector-average-{n}',result['within_area_entropy_nats'],
              sum(s['weighted_entropy_nats'] for s in sectors))
        check(f'cutoff-entropy-{n}',saved['entropy_nats'],result['entropy_nats'],
              saved['entropy_truncation_bound_nats']+2e-12)
        check(f'cutoff-coherence-{n}',saved['joint_F12_creation_real'],result['joint_F12_creation_real'],
              saved['joint_F12_creation_tail_error_bound']+2e-11)
        assert saved['renyi2_nats'] <= saved['entropy_nats']+2e-12
        assert saved['entropy_nats'] >= 0 and 0 < saved['purity'] <= 1+2e-12
        # Repeat numerical derivatives at half the original step.
        t=1/b;h=t*5e-5
        lo=summarize(1/(t-h),cutoff)[0];hi=summarize(1/(t+h),cutoff)[0]
        for key in ['entropy','mean_area']:
            field='entropy_nats' if key=='entropy' else 'mean_area'
            check(f'derivative-{key}-{n}',saved[f'd_{key}_d_temperature'],
                  (hi[field]-lo[field])/(2*h),2e-6)
    # Previously saved geometric means use magnetic counting, a distinct route.
    previous=ROOT/'results/thermal-closed-projection/temperature_summary.csv'
    for n,row in enumerate(csv.DictReader(previous.open())):
        b=float(row['beta_hbar_omega']);cutoff=max(12,int(36/b)+16)
        result=summarize(b,cutoff)[0]
        check(f'previous-area-{n}',result['mean_area'],float(row['conditional_mean_area']))
        check(f'previous-area-variance-{n}',result['area_variance'],float(row['conditional_area_sd'])**2)
    primary=[c for c in checks if not c['name'].startswith('derivative-')]
    report=dict(status='passed', comparisons=len(checks), spectrum_and_geometry_tolerance=TOL,
        max_absolute_residual=max(c['absolute_residual'] for c in checks),
        max_nonderivative_absolute_residual=max(c['absolute_residual'] for c in primary),
        max_residual_over_its_tolerance=max(c['absolute_residual']/c['tolerance'] for c in checks if c['tolerance']>0),
        derivative_step_agreement_tolerance=2e-6,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__), ROOT/'code/thermal/compare_j1_spin_methods.py']},
        independence='per-mode oscillator exponentials and Casimir projection/SVD, plus saved magnetic-counting geometry; cutoff/derivative checks share the analytic spectrum',
        checks=checks)
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:v for k,v in report.items() if k!='checks'})


if __name__=='__main__': main()

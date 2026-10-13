"""Independent limits, saved-pilot parity, and Gibbs scan checks."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.special import logsumexp

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'results/t11-size-comparison'


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def main():
    rows=read(OUT/'summary.csv')
    saved=read(ROOT/'results/hamiltonian-studies/spectra.csv')
    errors={'saved_pilot':0.,'free_orbital':0.,'no_hopping':0.,
            'gibbs_logsumexp':0.,'covariance_derivative':0.}
    for row in rows:
        l,k=int(row['L']),int(row['K'])
        graph,case=row['graph'],row['case']
        if l==4:
            reference=next(r for r in saved if int(r['K'])==k and r['graph']==graph and r['case']==case)
            for new,old in [('ground_energy','ground_energy'),('gap','gap'),
                            ('ground_volume','ground_mean_volume'),
                            ('ground_zero_probability','ground_probability_zero_volume')]:
                errors['saved_pilot']=max(errors['saved_pilot'],abs(float(row[new])-float(reference[old])))
        adjacency=np.ones((l,l))-np.eye(l) if graph=='complete' else np.zeros((l,l))
        if graph=='ring':
            for i in range(l):
                adjacency[i,(i+1)%l]=adjacency[(i+1)%l,i]=1
        if case=='free':
            orbital=np.linalg.eigvalsh(-adjacency)
            # Spin-singlet bosons carry spatial Young symmetry (K,K).
            # The lowest two orbital energies each occur K times.
            errors['free_orbital']=max(errors['free_orbital'],abs(float(row['ground_energy'])-k*sum(orbital[:2])))
        if case=='no_hopping':
            # At this integer density, the convex onsite cost is minimized
            # by two bosons at every site; the spin-one sites admit singlets.
            errors['no_hopping']=max(errors['no_hopping'],abs(float(row['ground_energy'])-l))
        archive=np.load(OUT/f'L{l}_K{k}_{graph}_{case}.npz')
        e=archive['energies'];v=archive['volume_by_energy_state'];e=e-e.min()
        for beta in (.01,.1,1.,10.):
            def mean(b):
                weights=np.exp(-b*e-logsumexp(-b*e))
                return float(weights@v)
            weights=np.exp(-beta*e-logsumexp(-beta*e))
            stable=np.exp(-beta*e);stable/=stable.sum()
            errors['gibbs_logsumexp']=max(errors['gibbs_logsumexp'],abs(mean(beta)-float(stable@v)))
            step=1e-5*max(1,beta)
            derivative=(mean(beta+step)-mean(beta-step))/(2*step)
            covariance=float(weights@((e-weights@e)*v))
            errors['covariance_derivative']=max(errors['covariance_derivative'],abs(derivative+covariance))
    assert max(errors[n] for n in errors if n!='covariance_derivative')<2e-9,errors
    assert errors['covariance_derivative']<2e-6,errors
    source_paths=[Path(__file__),ROOT/'code/python/t11_size_comparison.py',
                  ROOT/'code/python/plot_t11_size_comparison.py',
                  *sorted((ROOT/'code/python/lqg_scattering').glob('*.py'))]
    report={'checks':errors,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
            'independence_scope':'operator construction uses shared CG/root code; epsilon-q and orbital/no-hop limits are independent controls; no independent Rust larger-system run'}
    (OUT/'independent_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='sha256.json'}
    (OUT/'sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    print(json.dumps(errors,indent=2))


if __name__=='__main__':
    main()

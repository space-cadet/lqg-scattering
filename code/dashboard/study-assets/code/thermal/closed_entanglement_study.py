"""T9 closed-reference entropy study; no stochastic sampling or fitted physics."""
from pathlib import Path
import csv
import hashlib
import json
import platform
import time
import numpy as np
import scipy
from lqg_scattering.thermal_entanglement import summarize, tail_bounds

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'results/thermal-closed-entanglement'


def table(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    protocol = dict(date='2026-10-16', task='T9',
        state='normalized double-singlet projection of squeezed F12 reference in conjugate copies',
        input_area_per_copy=1, faces=4, temperature='T*=kBT/(hbar omega)',
        range=[.05, 5.], core_previously_validated_range=[.05,2.],
        entropy_units='S/kB in nats', tolerance=1e-9,
        cutoff='adaptive; positive-polynomial envelope bounds infinite entropy and area tails',
        claims='bipartite pure-state entropy in the fixed ordinary L/R tensor factorization; no Gibbs or heat-capacity identification',
        seeds='none: deterministic exact-sector sums')
    (OUT/'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    rows, sectors = [], []
    selected = [.25,.5,1.,2.,3.,5.]
    temperatures = np.unique(np.r_[np.geomspace(.05,5.,81),selected])
    start = time.time()
    for t in temperatures:
        cutoff = max(12, int(20*t))
        while True:
            tail = tail_bounds(1/t, cutoff)
            if tail and tail['entropy'] < 1e-13 and tail['moment2'] < 1e-12:
                break
            cutoff += max(4,int(4*t))
        row, area_rows, spectrum = summarize(1/t, cutoff)
        assert row['entropy_truncation_bound_nats'] < 1e-9
        rows.append(row); sectors.extend(area_rows)
        if t in selected:
            labels, amplitude, eigenvalues, degeneracy = spectrum
            np.savez_compressed(OUT/f'spectrum_T{t:g}.npz', labels=labels,
                amplitude=amplitude, eigenvalue=eigenvalues, multiplicity=degeneracy)
    # Derivatives of explicit state family, evaluated by central differences.
    for row in rows:
        t = row['temperature']; h = 1e-4*t
        lo = summarize(1/(t-h), row['area_cutoff'])[0]
        hi = summarize(1/(t+h), row['area_cutoff'])[0]
        row['d_entropy_d_temperature'] = (hi['entropy_nats']-lo['entropy_nats'])/(2*h)
        row['d_mean_area_d_temperature'] = (hi['mean_area']-lo['mean_area'])/(2*h)
    table(OUT/'temperature_summary.csv', rows)
    table(OUT/'area_sectors.csv', sectors)
    source_paths = [Path(__file__), ROOT/'code/python/lqg_scattering/thermal_entanglement.py',
                    ROOT/'code/python/lqg_scattering/thermal_projection.py']
    provenance = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, elapsed_seconds=time.time()-start,
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        artifact_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir())
            if p.suffix in ('.csv','.npz','.json') and p.name not in ('provenance.json','verification.json')})
    (OUT/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
    print(f'Calculated {len(rows)} temperatures; maximum entropy truncation bound '+
          f'{max(r["entropy_truncation_bound_nats"] for r in rows):.3g} nats; {time.time()-start:.1f}s')
    for r in rows:
        if r['temperature'] in selected:
            print({k:r[k] for k in ('temperature','entropy_nats','area_entropy_nats','within_area_entropy_nats','mean_area','area_cutoff')})


if __name__ == '__main__': main()

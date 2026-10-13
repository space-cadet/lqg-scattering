"""Focused density-matched L=4,K=4 versus L=5,K=5 RS-volume study.

Run with OPENBLAS_NUM_THREADS=1 and PYTHONPATH=code/python. No existing
pilot artefacts are overwritten. Protocol is saved before calculations.
"""
import csv
import hashlib
import itertools as it
import json
import platform
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import eigh
from scipy.sparse import coo_matrix, diags
from lqg_scattering.labels import compositions, fixed_face_dimension
from lqg_scattering.hamiltonian import hopping_matrix
from lqg_scattering.singlets import (occupation_basis, singlet_paths,
    sequential_basis, magnetic_singlet_count, closure_residual, root_abs,
    independent_local_q, action_matrix, GAMMA, ZERO_FACTOR)
from lqg_scattering.coherent_states import su2_ops
from lqg_scattering.positivity import dot_operator

OUT = Path(__file__).resolve().parents[2] / 'results/t11-size-comparison'
TOL = 2e-10


def maximum(a):
    return float(np.max(abs(a))) if np.size(a) else 0.


@lru_cache(None)
def pattern(spins):
    occ = occupation_basis(spins)
    paths = singlet_paths(spins)
    assert len(paths) == magnetic_singlet_count(spins)
    _, b, _ = sequential_basis(spins, paths, occ)
    checks = {'gram': maximum(b.conj().T @ b - np.eye(len(paths))),
              'closure': closure_residual(occ, b), 'epsilon_q': 0.}
    dots = {p: action_matrix(occ, dot_operator(su2_ops(p[0]), su2_ops(p[1])))
            for p in it.combinations(range(len(spins)), 2)}
    small = {p: b.conj().T @ (d @ b) for p, d in dots.items()}
    roots = {}
    for i, j, k in it.combinations(range(len(spins)), 3):
        q = 1j * (small[i,j] @ small[j,k] - small[j,k] @ small[i,j])
        direct = b.conj().T @ (independent_local_q(occ, spins, (i,j,k)) @ b)
        checks['epsilon_q'] = max(checks['epsilon_q'], maximum(q-direct))
        roots[i,j,k] = GAMMA**1.5 * root_abs(q)[0]
    assert max(checks.values()) < TOL, checks
    return occ, b, roots, checks


def build(l, k):
    occ = [tuple(x for pair in zip(a,b) for x in pair)
           for a in compositions(k,l) for b in compositions(k,l)]
    index = {o:i for i,o in enumerate(occ)}
    dim = fixed_face_dimension(l,k)
    rows, cols, vals = [], [], []
    blocks, start, checks = [], 0, {}
    for spins in compositions(2*k,l):
        paths = singlet_paths(spins)
        if not paths:
            continue
        sorted_spins = tuple(sorted(spins))
        canonical_occ, _, roots, residuals = pattern(sorted_spins)
        block_occ, b, inverse = sequential_basis(spins, paths, canonical_occ)
        # Use a freshly projected block: its coupling order differs from the
        # canonical order, so matrices must be transformed, not relabelled.
        transformed_roots = {}
        canonical_b = pattern(sorted_spins)[1]
        transform = canonical_b.conj().T @ b
        for triple in it.combinations(range(l),3):
            canonical_triple = tuple(sorted(inverse[i] for i in triple))
            transformed_roots[triple] = transform.conj().T @ roots[canonical_triple] @ transform
        nzr, nzc = np.nonzero(abs(b)>0)
        rows.extend(index[block_occ[r]] for r in nzr)
        cols.extend(start+nzc)
        vals.extend(b[nzr,nzc])
        stop = start+len(paths)
        blocks.append((start,stop,transformed_roots))
        for name, value in residuals.items():
            checks[name] = max(checks.get(name,0.),value)
        start = stop
    assert start == dim
    basis = coo_matrix((vals,(rows,cols)),shape=(len(occ),dim)).tocsr()
    checks['global_gram'] = maximum((basis.conj().T@basis).toarray()-np.eye(dim))
    numbers = np.asarray(occ)[:,::2]+np.asarray(occ)[:,1::2]
    onsite_diag = .5*np.sum(numbers*(numbers-1),axis=1)
    onsite = (basis.conj().T@diags(onsite_diag)@basis).toarray()
    bonds = {}
    for edge in it.combinations(range(l),2):
        mag = hopping_matrix(occ,index,edge)
        projected = (basis.conj().T@mag@basis).toarray()
        # The scalar hopping must preserve the entire singlet space.
        leakage = mag@basis-basis@projected
        checks['hopping_leakage'] = max(checks.get('hopping_leakage',0.), maximum(leakage))
        bonds[edge] = projected
    assert max(checks.values()) < TOL, checks
    print(f'built L={l} K={k} dim={dim} checks={checks}',flush=True)
    return onsite,bonds,blocks,checks


def save_csv(name, rows):
    with (OUT/name).open('w') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def run(l,k):
    onsite,bonds,blocks,checks = build(l,k)
    dim = len(onsite)
    summary, scans, levels = [],[],[]
    for graph in ('complete','ring'):
        edges = tuple(bonds) if graph=='complete' else tuple(sorted({tuple(sorted((i,(i+1)%l))) for i in range(l)}))
        triples = [tri for tri in it.combinations(range(l),3)
                   if sum(p in edges for p in it.combinations(tri,2))>=2]
        v = np.zeros((dim,dim),complex)
        for start,stop,roots in blocks:
            v[start:stop,start:stop] = sum(roots[tri] for tri in triples)
        checks[f'{graph}_onsite_commutator'] = maximum(onsite@v-v@onsite)
        vv,z = eigh(v)
        zero = abs(vv)<=ZERO_FACTOR*max(1.,maximum(vv))
        assert vv.min()>-TOL
        for case,t,u in [('no_hopping',0.,1.),('free',1.,0.),('U20',1.,20.)]:
            h = u*onsite-t*sum(bonds[e] for e in edges)
            e,w = eigh(h)
            residual = maximum(h@w-w*e)
            assert residual<TOL
            means = np.real(np.sum(w.conj()*(v@w),axis=0))
            pzero = np.sum(abs(z[:,zero].conj().T@w)**2,axis=0)
            ground = abs(e-e[0])<TOL
            gap = float(e[~ground][0]-e[0])
            curve = []
            for beta in [0.,*np.geomspace(1e-3,1e4,701),float('inf')]:
                weights = ground/ground.sum() if np.isinf(beta) else np.exp(-beta*(e-e[0]))
                weights = weights/weights.sum()
                mean = float(weights@means)
                covariance = float(weights@((e-weights@e)*means))
                curve.append(dict(L=l,K=k,graph=graph,case=case,beta=beta,
                    mean_volume=mean,volume_per_triple=mean/len(triples),
                    probability_zero_volume=float(weights@pzero),covariance=covariance))
            peak = max(curve,key=lambda row:row['mean_volume'])
            summary.append(dict(L=l,K=k,graph=graph,case=case,dimension=dim,
                triples=len(triples),ground_energy=float(e[0]),gap=gap,
                ground_degeneracy=int(ground.sum()),ground_volume=float(means[ground].mean()),
                ground_zero_probability=float(pzero[ground].mean()),
                infinite_temperature_volume=float(means.mean()),
                peak_volume=peak['mean_volume'],peak_beta=peak['beta'],
                eigen_residual=residual))
            for a,b in it.groupby(range(dim),key=lambda n:round(float(e[n]),8)):
                indices=list(b)
                levels.append(dict(L=l,K=k,graph=graph,case=case,energy=float(e[indices].mean()),
                    degeneracy=len(indices),mean_volume=float(means[indices].mean())))
            scans.extend(curve)
            np.savez_compressed(OUT/f'L{l}_K{k}_{graph}_{case}.npz',energies=e,
                                volume_by_energy_state=means,zero_probability_by_energy_state=pzero)
            print(summary[-1],flush=True)
    assert max(checks.values())<TOL
    return summary,scans,levels,checks


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    protocol = dict(question='Does the L4 K4 U20 nonmonotonic response persist at L5 K5?',
        sizes=[[4,4],[5,5]],density='2K/L=2; K=sum j_i, not sum sqrt(j_i(j_i+1))',
        graphs=['complete','periodic ring'],hopping='unit per edge; no degree rescaling',
        controls=[dict(t=0,U=1),dict(t=1,U=0),dict(t=1,U=20)],g=0,
        volume='gamma^(3/2) sum connected-induced-triple sqrt(abs(q)); gamma=0.2375; hbar=1',
        reported_normalizations=['total','per selected triple'],physical_calibration=False,
        beta='inverse energy, kB=1; beta*t for t=1 and beta*U for t=0,U=1',
        grid='0,701 log-spaced 1e-3..1e4,infinity; uniform ground-space mixture',
        tolerance=TOL,root_zero_factor=ZERO_FACTOR,
        controls_validation=['CG versus magnetic multiplicity','raising/lowering closure',
            'direct epsilon q versus dot commutator','singlet hopping leakage',
            'eigenpair residuals','onsite-volume commutator','L4 saved archive parity'],
        limitations=['odd ring changes topology','complete degree grows',
            'volume operator changes with graph','finite crossover is not a phase transition'],
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__)
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    summaries,scans,levels,validation=[],[],[],{}
    for l,k in protocol['sizes']:
        a,b,c,d=run(l,k)
        summaries.extend(a); scans.extend(b); levels.extend(c); validation[str(l)]=d
        save_csv('summary.csv',summaries);save_csv('thermal_scan.csv',scans);save_csv('energy_levels.csv',levels)
        (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
        pattern.cache_clear()
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name!='sha256.json'}
    (OUT/'sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')


if __name__=='__main__':
    main()

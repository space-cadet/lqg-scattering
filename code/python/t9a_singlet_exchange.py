"""Reproducible first two-polyhedron FL exchange pilot; no reservoir claim."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.linalg import eigh
from lqg_scattering.singlet_exchange import (
    build_exchange_space, exchange_hamiltonian, fl_product, readout)
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.tetrahedra import closed_equal_area_normals

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'results/t9a-singlet-exchange'


def table(name, rows):
    with (OUT/name).open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    space = build_exchange_space(4)
    regular = spinors_from_normals(closed_equal_area_normals(1/np.sqrt(3), np.pi/2))
    deformed = spinors_from_normals(closed_equal_area_normals(1/np.sqrt(3), np.pi/6))
    preparations = [('equal_regular', 2, regular), ('unequal_regular', 3, regular),
                    ('equal_deformed_right', 2, deformed)]
    seeds = {name: fl_product(space, k, regular, right) for name, k, right in preparations}
    np.savez_compressed(OUT/'inputs.npz', spinors_left=regular, spinors_right_regular=regular,
                        spinors_right_deformed=deformed, area_left=space['area_left'], **seeds)
    cases = [('no_exchange', 0., 0., 0.), ('resonant', .1, 0., 0.),
             ('repulsive', .1, 1., 0.), ('detuned', .1, 0., 2.)]
    times = np.linspace(0., 20., 101)
    dynamics, grounds, thermal, spectra, checks = [], [], [], [], dict(space['residuals'])
    for name, g, u, detuning in cases:
        h, current, forward = exchange_hamiltonian(space, coupling=g, epsilon_left=detuning,
                                                  repulsion_left=u, repulsion_right=u)
        dense = h.toarray()
        values, vectors = eigh(dense)
        checks[name+'_eigen_residual'] = float(np.max(abs(dense @ vectors-vectors*values)))
        checks[name+'_hermiticity'] = float(np.max(abs(dense-dense.conj().T)))
        checks[name+'_current_commutator'] = float(np.max(abs(current.toarray()-
            1j*(dense*space['area_left'][None, :]-space['area_left'][:, None]*dense))))
        np.savez_compressed(OUT/(name+'_operators.npz'), h_data=h.data, h_indices=h.indices,
                            h_indptr=h.indptr, h_shape=h.shape, energies=values)
        spectra.extend(dict(case=name, index=i, energy=float(e)) for i, e in enumerate(values))
        tolerance = 1e-10*max(1., float(np.max(abs(values))))
        mask = values-values[0] <= tolerance
        ground_vectors = vectors[:, mask]
        ground_readouts = [readout(space, v, current, forward) for v in ground_vectors.T]
        # Uniform ground-space mixture: no arbitrary eigenvector geometry.
        ground = {key: float(np.mean([r[key] for r in ground_readouts]))
                  for key in ground_readouts[0] if key not in ('entropy_nats', 'area_variance')}
        ground['area_variance'] = float(np.mean([r['area_variance']+r['area_left']**2
                                                for r in ground_readouts])-ground['area_left']**2)
        grounds.append(dict(case=name, energy=float(values[0]), degeneracy=int(mask.sum()), **ground))
        diag_area = np.sum(abs(vectors)**2*space['area_left'][:, None], axis=0)
        diag_vol = {side: np.sum(vectors.conj()*(op @ vectors), axis=0).real
                    for side, op in space['volumes'].items()}
        for beta in (0., .5, 2., 10., 100.):
            weights = np.exp(-beta*(values-values[0])); weights /= weights.sum()
            thermal.append(dict(case=name, beta=beta, energy=float(weights @ values),
                                area_left=float(weights @ diag_area),
                                volume_L=float(weights @ diag_vol['L']), volume_R=float(weights @ diag_vol['R']),
                                entropy_nats=float(-np.sum(weights[weights>0]*np.log(weights[weights>0])))))
        for prep, seed in seeds.items():
            coefficients = vectors.conj().T @ seed
            states = vectors @ (coefficients[:, None]*np.exp(-1j*values[:, None]*times))
            energy0 = float(np.vdot(seed, h @ seed).real)
            worst_norm = worst_energy = 0.
            for t, state in zip(times, states.T):
                row = readout(space, state, current, forward)
                energy = float(np.vdot(state, h @ state).real)
                worst_norm = max(worst_norm, abs(row['norm']-1))
                worst_energy = max(worst_energy, abs(energy-energy0))
                dynamics.append(dict(case=name, preparation=prep, time=float(t), energy=energy,
                                     return_probability=float(abs(np.vdot(seed, state))**2), **row))
            checks[name+'_'+prep+'_norm'] = worst_norm
            checks[name+'_'+prep+'_energy'] = worst_energy
        print(name, 'complete', flush=True)
    table('dynamics.csv', dynamics); table('ground_states.csv', grounds)
    table('thermal.csv', thermal); table('spectra.csv', spectra)
    assert max(checks.values()) < 2e-10, checks
    sources = ['code/python/lqg_scattering/singlet_exchange.py', 'code/python/t9a_singlet_exchange.py',
               'code/python/test_singlet_exchange.py', 'code/python/lqg_scattering/hamiltonian.py',
               'code/python/lqg_scattering/intertwiners.py', 'code/python/lqg_scattering/singlets.py']
    summary = dict(total_area=4, dimension=space['dimension'], local_dimensions=space['dimensions'],
                   hbar=1, time_points=101, time_interval=[0, 20], coupling_convention='six identical corresponding-pair coefficients; no division by six',
                   cases=[dict(name=n, g=g, U=u, detuning=d) for n,g,u,d in cases],
                   preparations=[dict(name=n, K_left=k, K_right=4-k) for n,k,_ in preparations],
                   residuals=checks, max_residual=max(checks.values()),
                   source_sha256={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
                   numpy_version=np.__version__)
    (OUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print('PASS: dimension', space['dimension'], 'maximum residual', max(checks.values()))


if __name__ == '__main__':
    main()

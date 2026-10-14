"""Verify saved trajectories with sparse expm_multiply, without diagonalization."""
import csv
import json
from pathlib import Path
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply
from lqg_scattering.singlet_exchange import build_exchange_space, exchange_hamiltonian, readout

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'results/t9a-singlet-exchange'


def main():
    summary = json.loads((OUT/'summary.json').read_text())
    space = build_exchange_space(summary['total_area'])
    inputs = np.load(OUT/'inputs.npz', allow_pickle=False)
    rows = list(csv.DictReader((OUT/'dynamics.csv').open()))
    errors = []
    for case in summary['cases']:
        name = case['name']
        archive = np.load(OUT/(name+'_operators.npz'), allow_pickle=False)
        saved = csr_matrix((archive['h_data'], archive['h_indices'], archive['h_indptr']), shape=tuple(archive['h_shape']))
        h, current, forward = exchange_hamiltonian(space, coupling=case['g'],
            epsilon_left=case['detuning'], repulsion_left=case['U'], repulsion_right=case['U'])
        difference = saved-h
        errors.append(float(np.max(abs(difference.data))) if difference.nnz else 0.)
        for prep in summary['preparations']:
            name_p = prep['name']
            seed = inputs[name_p]
            for t in (0., .2, 7.4, 20.):
                state = expm_multiply(-1j*t*saved, seed)
                observed = readout(space, state, current, forward)
                observed['energy'] = float(np.vdot(state, saved @ state).real)
                observed['return_probability'] = float(abs(np.vdot(seed, state))**2)
                row = next(r for r in rows if r['case']==name and r['preparation']==name_p and abs(float(r['time'])-t)<1e-12)
                errors.extend(abs(value-float(row[key])) for key, value in observed.items())
    thermal = list(csv.DictReader((OUT/'thermal.csv').open()))
    for row in thermal:
        if float(row['beta']) == 0.:
            errors.append(abs(float(row['area_left'])-2))
            errors.append(abs(float(row['entropy_nats'])-np.log(space['dimension'])))
            errors.append(abs(float(row['volume_L'])-space['volumes']['L'].diagonal().real.mean()))
    result = dict(method='sparse expm_multiply versus saved dense energy-basis trajectories; analytic beta=0 traces',
                  checks=len(errors), max_residual=max(errors), tolerance=2e-10,
                  scope='48 sampled states; shared singlet basis/readouts; independent oscillator and analytic tests are in test_singlet_exchange.py')
    assert result['max_residual'] < result['tolerance'], result
    (OUT/'independent_verification.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS', result['checks'], 'checks; maximum residual', result['max_residual'])


if __name__ == '__main__':
    main()

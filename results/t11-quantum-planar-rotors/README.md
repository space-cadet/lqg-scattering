# Four quantum planar rotors at exactly zero total momentum

First pilot, October 16, 2026. See the [pedagogical account](../../notes/quantum-planar-rotor-energy-transfer.md) and [pre-run protocol](protocol.md).

Four-site ring, I=lambda=hbar=1; initial momentum eigenstates |m,-m,0,0>, m=2,4; time 0..20 in increments of 0.2. Mean total energies are 8 and 20; energy is not sharp. Independent uniform initial classical angles match the initial momentum-eigenstate Wigner measure. This differs from the nearly aligned classical rotor studies.

| Initial packet energy | Quantum mean cold-pair ratio | Classical mean cold-pair ratio |
|---:|---:|---:|
| 4 | 59.20% | 48.52% |
| 16 | 6.71% | 5.32% |

These are equal-weight means over the saved times $10\leq\tau\leq20$, including both endpoints.

## Validation

Both cutoffs 8 and 10 were run. The accepted cutoff is 10 (6,181 sector states). No cutoff 12 run was needed because the declared stopping criteria passed.

- m=2: cutoff kinetic difference 1.22e-13, entropy difference 1.06e-13, return difference 1.48e-14; maximum boundary probability 1.64e-20. Quantum norm error 4.63e-14, energy error 3.57e-13. Classical accepted dt 0.00015625, successive-step kinetic difference 0.000224, maximum per-trajectory energy error 2.24e-07 and total momentum error 4.04e-13.
- m=4: cutoff kinetic difference 4.36e-09, entropy difference 3.92e-09, return difference 5.07e-10; maximum boundary probability 1.91e-15. Quantum norm error 1.78e-14, energy error 3.48e-13. Classical accepted dt 0.00062500, successive-step kinetic difference 0.000392, maximum per-trajectory energy error 8.35e-06 and total momentum error 3.67e-13.

The initial classical dt=.005/.0025 comparison failed the 1e-3 kinetic criterion. Steps were reduced until the same criterion passed; every refinement is saved in the classical JSON files. These refinements were numerical controls, not new selected physical cases. Ensemble pointwise standard errors are saved; time samples are correlated. The plotted cold-pair uncertainty uses the sum of marginal standard errors as a conservative bound, without assuming independent rotor energies.

All 62 regression tests passed. Six new tests cover sector dimension/Hermiticity; independent Fourier-quadrature matrix elements (including an odd pair momentum sector); dense versus sparse propagation and explicit partial trace; free evolution and equal kinetic energies for a zero-momentum pair; independent classical DOP853 trajectories; and the symmetric triangle. Production checks compare every saved kinetic mean, entropy and return at successive cutoffs, and track norm, energy, momentum and boundary residuals. This is local numerical validation, not an external physics review.

## Files and reproduction

- quantum-m*-c*.json: all quantum readouts at both tested cutoffs, including local kinetic energies, signed momentum means, single-site entropy, return, boundary population and conservation errors.
- classical-m*.json: accepted and preceding step controls, sampling standard errors, conservation diagnostics and refinement history (2048 samples, seed 20261016).
- summary.json: comparisons, time-window averages and source SHA256 hashes.
- protocol.md: preparation, units, acceptance criteria and limitations specified before evolution.

From the repository root:

```sh
OPENBLAS_NUM_THREADS=1 python3 code/python/t11_quantum_planar_rotors.py
python3 -m unittest discover -s code/python -p 'test_*.py'
python3 code/python/plot_t11_quantum_planar_rotors.py
```

Numerics require NumPy and SciPy; plotting additionally requires Matplotlib. The original run used NumPy 2.4.1 and SciPy 1.17.0. Figures are vector PDF and 300-dpi PNG under figures/t11-quantum-planar-rotors. The plotting script was run with a temporary environment providing Matplotlib.

## Claim limits

This establishes energy transfer and single-rotor entanglement for two specified four-planar-rotor preparations at epsilon=1. It does not establish equilibration, many-body scaling, a semiclassical limit, tunneling, or three-dimensional singlet/polyhedral dynamics. The mean cold-pair kinetic ratio is normalized by initial packet kinetic energy, not conserved total energy, and need not lie below one in general. No dashboard publication, commit or push is part of this pilot.

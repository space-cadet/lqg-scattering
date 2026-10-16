# Classical rotor equilibration: numerical record

The [illustrated physical account](../../notes/classical-rotor-equilibration.md) gives the Hamiltonian, exact split-flow integrator, constrained microcanonical measure, measured outcomes and claim limits.

The study covers 72 production runs (63 unique initial dynamical problems), 144 microcanonical chains, and ten full-duration half-step controls. It finds equilibrium-like spreading for moderate packets and persistent high-energy concentration through time 2000. The latter is a finite-time finding, not a claim of permanent localization.

## Reproduce

From the repository root, with a scientific Python environment containing NumPy and SciPy, and a host C++17 compiler:

```sh
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/t11_classical_rotors.py > /tmp/t11-classical-rotors.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/analyze_t11_classical_rotors.py > /tmp/classical-rotor-analysis.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/verify_t11_classical_rotors.py > /tmp/classical-rotor-independent.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 -m unittest discover -s code/python -p 'test_*.py' > /tmp/classical-all-tests.log 2>&1
```

The plotting script `code/python/plot_t11_classical_rotors.py` also requires Matplotlib. It exports vector PDF and 300-dpi PNG under `figures/t11-classical-rotors/`. The Python library compiles the small C++ stepping/sampling kernel into a content-addressed temporary library using clang++; there is no committed binary or dependency change.

## Files

- `protocol.json`: production protocol and seeds, written before calculations.
- `analysis-protocol.json`: equilibrium-fluctuation calibration and refinement selection, written before that analysis.
- `summary.csv`: two late-time windows, concentration, spreading, fluctuations, energy retention and fixed-tolerance residence.
- `equilibrium.csv`: two-chain references, block errors, acceptance rates and split-Rhat diagnostics.
- `equilibrium-analysis.csv`: equilibrium-calibrated residence and empirical distribution distances.
- `grouped-summary.csv`: means and ranges across three orientation seeds.
- `validation.csv`: production conservation and equilibrium constraint checks.
- `step-refinement.csv`: ten full-duration comparisons at half the time step.
- `independent-validation.json`: direct endpoint Hamiltonian and saved-array audits.
- `verification.json`: regression, figure and resource evidence.
- `provenance.json`, `sha256.json`: source/runtime provenance and artifact hashes.
- `N*_R*_*_S*.npz`: reproducible initial/final configurations, sampled trajectories and equilibrium samples. `_refined.npz` files hold half-step trajectories. These large per-run archives are generated locally and ignored by Git.

## Array conventions

Orientations and angular momenta have shape `(N,3)`. `times` has 4,001 entries. `readouts` columns are energy, kinetic fraction, original-pair energy fraction, concentration, spatial energy second moment, total angular momentum norm, orientation norm error, tangency error, followed by the N local energies. `microcanonical_readouts` has shape `(2,4000,N+8)`. `distance` is the maximum deviation from the equilibrium means of the hot-pair fraction, kinetic fraction and normalized participation; it is not a phase-space or quantum-state distance.

I=lambda=1. Sites are zero-indexed on a periodic ring. Ratios 1, 10, 100 specify the initial packet kinetic energy at N=8. Fixed-packet runs hold this energy fixed; fixed-density runs multiply it by N/8. Initial potential energy is additional and recorded in the actual total energy. N=8 scaling controls are duplicates, not independent statistical samples.

The primary quantitative caveats are three initial orientation seeds, a special opposite-momentum pair preparation, a finite interval, and residual long-time sampling/step sensitivity in chaotic cases. See the physical account before interpreting individual metrics. Full per-run archives remain local and ignored by Git; compact summaries, protocols, validation reports, and curated figures are versioned.

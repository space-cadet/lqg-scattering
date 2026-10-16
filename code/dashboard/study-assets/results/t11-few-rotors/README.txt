# Few-rotor energy-transfer benchmark

See [the mathematical explanation and illustrated results](../../notes/few-rotor-energy-transfer.md).

The study includes 14 planar-pair runs, 63 generic three-dimensional runs, six half-step controls, an exactly symmetric triangle control, and a coupling/time scaling check. There is no quantum calculation or thermalization claim.

## Reproduction

Run from the repository root with NumPy, SciPy and clang++ available:

```sh
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 code/python/t11_few_rotors.py > /tmp/t11-few-rotors.log 2>&1
OPENBLAS_NUM_THREADS=1 PYTHONPATH=code/python python3 -m unittest discover -s code/python -p 'test_*.py' > /tmp/few-rotor-all-tests.log 2>&1
```

`plot_t11_few_rotors.py` additionally requires Matplotlib and exports vector PDF and 300-dpi PNG. Sources extend the existing general rotor library; previous ring methods and saved results are preserved. The numerical kernel is compiled to a temporary, content-addressed library; no binary is committed.

## Artifacts

- `protocol.json`: settings and analytic benchmark frozen before runs.
- `pair-summary.csv`: exact and sampled transfer maxima, coupling, energy and rotation/libration classification.
- `few-summary.csv`: separate kinetic and local-total-energy transfer metrics, three seeds, three graphs, seven couplings.
- `pair_*.npz`: scaled time, full configurations and angular momenta, kinetic energies, relative angle and momentum. These large run archives are generated locally and ignored by Git.
- `triangle_*.npz`, `four_open_*.npz`, `four_ring_*.npz`: scaled time, per-rotor kinetic and local energies, total energy and initial/final configurations; these archives are also local-only.
- `validation.json`: independent scalar-ODE comparisons, conserved quantities, half-step controls, symmetric-triangle and scaling checks.
- `provenance.json`, `sha256.json`: source and artifact identities.
- `verification.json`: test outcome and numerical evidence.

All runs use I=1 and scaled time tau=t*sqrt(lambda), ending at tau=200. Three-dimensional initial kinetic packet energy is 100; it excludes the additional initial potential energy. Cold kinetic-energy fractions are normalized by that initial kinetic packet, not by total energy. Local energy includes half of each adjacent bond's potential energy.

The exact planar transfer formula applies only to an aligned pair with one initially resting rotor. The generic three-dimensional scans are controls, not a complete parameter-space map. Full per-run archives remain local and ignored by Git; compact summaries, protocols and validation reports are versioned, and selected summaries and figures appear in the dashboard package.

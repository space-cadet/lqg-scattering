# T9a: two closed FL polyhedra exchanging singlet pairs

Calculated October 14, 2026. [Study specification](../../notes/t9a-singlet-exchange.md); [task](../../memory-bank/tasks/T9a.md).

## Scope and inputs

Exact separately closed four-face spaces at combined linear area $K=4$, including both vacuum endpoints and empty faces. Local dimensions are 1, 6, 20, 50, 105; the joint direct sum has 1,210 states. Area is half the Schwinger-boson number. There is no occupation truncation within this declared combined-area space.

All six identical ordered face-pair channels have coefficient $g$. This is an explicitly chosen exchange Hamiltonian, not a derived interaction or a sewn/glued geometry. Local energies are $\epsilon_X A_X+U_X A_X(A_X-1)/2$, with $\hbar=1$. Repulsion acts on the whole polyhedron's area rather than on face-site occupations.

| Setting | Pair coupling $g$ | $U_L=U_R$ | $\epsilon_L$ | $\epsilon_R$ |
|---|---:|---:|---:|---:|
| No exchange | 0 | 0 | 0 | 0 |
| Resonant | 0.1 | 0 | 0 | 0 |
| Repulsive | 0.1 | 1 | 0 | 0 |
| Detuned | 0.1 | 0 | 2 | 0 |

Three ordinary product FL inputs: regular tetrahedra at areas $(2,2)$ and $(3,1)$, and a regular/deformed pair at $(2,2)$. The right seed is not conjugated. Inputs use the existing closed equal-face family with $x=1/\sqrt3$, bend angles $90^\circ$ and $30^\circ$, and the repository's documented normal-to-spinor convention. Actual complex spinors and normalized joint seeds are saved. These small-area preparations need not be sharply classical.

Each of the twelve trajectories uses 101 points at $t=0,0.2,\ldots,20$. Canonical controls have $\beta=0,0.5,2,10,100$ on fixed combined area; inverse temperature is in the chosen model energy units.

## First findings

- Resonant unequal regular inputs exchange substantial area: the sampled left mean ranges from approximately 1.0083 to 3.0000. With detuning it ranges from 2.5120 to 3.2200 over the same interval. These are sampled ranges, not analytic extrema.
- Equal regular inputs retain mean left area 2 while the resonant area variance reaches approximately 2.722. Equal means therefore do not imply absence of transfer: the distribution broadens and the copies become entangled.
- Repulsion reduces the maximum sampled equal-input variance to approximately 1.050. The three interacting settings change both correlations and volume during evolution.
- All three interacting ground spaces have degeneracy 105. Their geometry is reported using the uniform ground-space mixture, not an arbitrarily selected eigenvector. Resonant and repulsive ground means have left area 2; the detuned ground mean has left area approximately 0.0967.
- Dynamics remain those of a finite isolated pair. The canonical controls do not establish relaxation or equivalence to the selected squeezed-and-projected thermal family.

![Area exchange, fluctuations, entropy and volume](../../figures/t9a-singlet-exchange/exchange-overview.png)

The figure compares all three interacting settings. Panel (a): unequal regular mean area. Panel (b): equal regular area variance. Panel (c): unequal regular bipartite entropy. Panel (d): deformed-right positive RS volume in repository units. [Vector PDF](../../figures/t9a-singlet-exchange/exchange-overview.pdf). No physical volume prefactor or energy calibration is claimed.

## Saved artifacts

- `inputs.npz`: complex spinor labels, seed vectors, joint left-area diagonal.
- `*_operators.npz`: sparse Hamiltonian arrays and full energy spectra; reconstruct with SciPy CSR and stored shape, using `allow_pickle=False`.
- `dynamics.csv`: 1,212 rows with return probability, conserved energy/norm, both mean areas, left variance and complete area probabilities, current, weighted pair coherence, pure bipartite entropy in nats, both positive RS volumes, eight face-area means and twelve flux-dot means.
- `ground_states.csv`: ground energy, degeneracy and uniform-ground-mixture readouts. No pure-state entanglement entropy is assigned to these mixed states. Variance is computed from the mixture's first and second moments.
- `thermal.csv`: 20 fixed-combined-area canonical means and full joint Gibbs entropy; this entropy differs from the pure trajectory's bipartite entropy.
- `spectra.csv`: all 4,840 energy values.
- `summary.json`: dimensions, parameters, source hashes and internal residuals.
- `independent_verification.json`: 1,792 comparisons; maximum residual $9.06\times10^{-13}$ against tolerance $2\times10^{-10}$.
- `provenance.json`: runtime versions, dependency/driver hashes and artifact hashes.

## Verification

All 46 Python regression tests passed, including four new tests. New controls cover the exact one-unit law $\langle A_L(t)\rangle=\cos^2(2|g|t)$, independent joint-occupation transfer, current commutator/sign and finite-difference derivative, vacuum endpoints, no-exchange evolution, normalization and initial product entropy. The oscillator comparison also verifies that the transferred state has no component outside the separately closed basis.

The pilot checks local closure/orthogonality, creator leakage, Hermiticity, eigensystem residuals, current commutators, and all trajectory norm/energy residuals. Maximum internal residual is $4.53\times10^{-14}$.

An independent sparse `expm_multiply` verifier checks 48 sampled states against the saved dense-eigenbasis trajectories, comparing all readouts, energy and return probability. It also checks the analytic infinite-temperature area, entropy and volume traces. The verifier shares local singlet bases and readout operators; its independence concerns propagation. Separate analytic and raw oscillator controls cover those operator constructions.

The figure was exported as vector PDF and 300-dpi PNG. Backing arrays were checked for finiteness and expected sample counts; the standalone PNG was visually inspected for readable labels, clipping and legend placement.

## Reproduce

From the repository root, using the project's scientific Python environment:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=code/python python code/python/t9a_singlet_exchange.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=code/python python code/python/verify_t9a_singlet_exchange.py
PYTHONPATH=code/python python -m unittest discover -s code/python -p 'test_*.py'
PYTHONPATH=code/python python code/python/plot_t9a_singlet_exchange.py
```

The local run used `/Users/deepak/miniconda3/envs/qc-diff/bin/python`. Redirect verbose outputs to a temporary log when running. The pilot writes its own results directory; figure generation reads saved CSVs and does not rerun the physics.

## Open work

Larger areas, broader shape/channel choices, physically specified phase-coherent inputs, reservoir dynamics, recurrence/relaxation tests, and full reduced-state comparison with the selected T9 thermal construction remain open. No thermodynamic phase, unique ground shape, or reservoir thermalization follows from this pilot.

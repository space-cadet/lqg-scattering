# T11 large-area FL face-activation control

Calculated October 16, 2026. [Pedagogical note and interaction proposal](../../notes/face-energy-equipartition.md).

## Question and scope

Can an FL tetrahedron populate additional face channels while remaining closed
at fixed area? Exact coherent-state evolution under the existing free hopping
Hamiltonian answers a controlled part of that question. Available channels
L=5,6; K=2,20,100,1000,10000; two specified face-phase choices. Initial means
are K/4 on four regular-tetrahedral labels, with vacuum extra channels. U=0,
unit complete-graph hopping and hbar=1. These are pure-state trajectories.

At K=10000, five-channel new-area peak fractions are 0.2906394529 and
0.0946802735 for the two phase choices. Six-channel combined fractions are
0.4036659069 and 0.1315003799. The two extra six-channel normals coincide:
six occupied channels yield only five distinct classical directions. The
five-channel baseline has unequal mean areas and exact periodic returns;
local energies also recur. No equipartition or relaxation is established.
Initial phase changes alter the conserved energy as well as the trajectory.

## Method and evidence

The quadratic U(L) action preserves the fixed-area FL family, so an L-by-2
spinor matrix replaces an infeasible large-K Hilbert-space diagonalization.
Reported exact singlet dimensions are counting information, not built matrix
sizes. Area and active probabilities use each face's exact binomial marginal;
joint face occupations are not treated as independent.

- `protocol.json`: Hamiltonian, phases, areas, time grid and tolerance, saved
  before computation. Time samples refine the neighbourhood of exact returns.
- `inputs.npz`: actual complex spinors for both phase choices and both channel
  counts, plus the hopping matrices. Load with `allow_pickle=False`.
- `dynamics.csv`: per-face areas, nonempty probabilities and energies; total
  energy, concentration, active counts and geometric normal diagnostics.
- `summary.csv`: 20 controls; sampled peaks, returns and conservation residuals.
  Exact dimensions have a d= prefix so browser numeric parsing cannot round
  large integers.
- `verification.json`: 360 comparisons against direct sparse occupation-space
  exponentials and independently rebuilt FL kets at K=1,2; recurrence and
  conservation checks over all large-area controls. Maximum residual 1.9e-11.
- `provenance.json`: code and artifact hashes. The existing 46 Python tests
  pass after the shared library extension.
- [Figure](../../figures/fl-face-activation/face_activation_control.pdf): vector
  PDF and 300-dpi PNG, exported from saved arrays and visually inspected.

The face-vector checks concern classical input labels of coherent intertwiners.
No new metric reconstruction, quantum positive-volume calculation, interacting
evolution, thermal ensemble or variable-valence refinement is included.

## Reproduce

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=code/python python code/python/fl_face_activation.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=code/python python code/python/verify_fl_face_activation.py
PYTHONPATH=code/python python code/python/plot_fl_face_activation.py
```

Reusable FL propagation and exact face statistics extend
`lqg_scattering/intertwiners.py`; Bloch face vectors extend `spinors.py`.
The verifier uses the existing sparse Hamiltonian builder. No parallel
implementation of a Fock space, FL state, or hopping matrix was introduced.

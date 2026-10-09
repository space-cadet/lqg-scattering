# LQG scattering Python library

`lqg_scattering` contains the reusable numerical routines used by the research
scripts in this directory. Python 3.10 or newer, NumPy, SciPy, and SymPy are
required. Plotting dependencies are optional.

Install from the repository root:

```bash
python -m pip install -e code/python
# Include plotting dependencies when needed:
python -m pip install -e 'code/python[visualization]'
```

| Module | Responsibility |
|---|---|
| `coherent_states`, `schwinger`, `fixed_k`, `intertwiners` | Fock spaces, operators, coherent and fixed-area states |
| `labels`, `singlets` | Spin-sector counting and four-face or sequential singlet recoupling |
| `grassmannian`, `spinors`, `tetrahedra`, `minkowski`, `correspondence` | Kinematic maps and geometric reconstruction |
| `positivity`, `observables`, `fl_volume`, `volume_blocks` | Flux readouts, positive RS/AL volumes, and independent matrix checks |
| `hamiltonian` | Full fixed-number hopping/repulsion on an undirected graph, plus the four-site singlet/volume builder |
| `total_spin` | Total SU(2) operators, closure diagnostics, singlet weight, and spin-sector probabilities |
| `preparations` | Fixed-number FL tetrahedron and face-product coherent kets |
| `thermal` | Gibbs weights, degenerate-subspace averages, site reduced entropy, and Schmidt-form TFD readouts |
| `analysis` | Shared power-law fit and local logarithmic slopes |
| `conventions` | Shared project units and conventions |

For example, build the tested four-site fixed-area sector without running a
study or writing files:

```python
import numpy as np
from lqg_scattering.hamiltonian import build_fixed_k, connected_triples
from lqg_scattering.thermal import thermal_weights

model = build_fixed_k(2)
ring = ((0, 1), (1, 2), (2, 3), (0, 3))
hopping = sum(model["bonds"][edge] for edge in ring)
hamiltonian = -hopping + 5 * model["onsite"]
volume = sum(model["volume_by_triple"][triple]
             for triple in connected_triples(ring))
energies, vectors = np.linalg.eigh(hamiltonian)
weights, log_partition = thermal_weights(energies, beta=1.0)
volume_by_state = np.real(np.diag(vectors.conj().T @ volume @ vectors))
mean_volume = weights @ volume_by_state
```

`K` denotes total linear area and the boson number is `2K` in this builder.
It retains the tested four-site scope; it is not a larger-lattice solver.
Volumes use project units, with physical normalization unresolved. The site
entropy of a degenerate Gibbs mixture is not an entanglement measure.

## Full-space numerics and closure

Use `build_fixed_number_model` for open or closed configurations without a
singlet projection. `n_bosons` is the exact total boson count, including odd
values. Graph edges are unique undirected pairs; the hopping coefficient is
the scalar `t` passed to `assemble_hamiltonian`.

```python
from lqg_scattering.hamiltonian import build_fixed_number_model, assemble_hamiltonian
from lqg_scattering.total_spin import total_spin_operators, closure_diagnostics

ring = ((0, 1), (1, 2), (2, 3), (0, 3))
model = build_fixed_number_model(4, 1, edges=ring)
hamiltonian = assemble_hamiltonian(model, t=1.0, U=5.0)
spin = total_spin_operators(model["occupations"], model["index"], n_sites=4)
state = np.zeros(model["metadata"]["dimension"], dtype=complex)
state[model["index"][(1, 0, 0, 0, 0, 0, 0, 0)]] = 1.0
diagnostics = closure_diagnostics(state, spin)
```

This single-face example has total spin $J=1/2$, mean squared total spin
$3/4$, and zero singlet weight. `closure_diagnostics` also accepts normalized
dense density matrices. `spin_sector_probabilities` returns a dictionary
mapping $J$ to $P(J)$; zero mean spin alone does not establish closure.

Spin probabilities use exact local-occupation/magnetic blocks with a default
maximum dense block dimension of 512. An oversized block raises an error;
it is not truncated. Dense density-matrix positivity checks also require an
eigenvalue calculation. Fixed-number dimensions still grow combinatorially.
The full builder supplies hopping and repulsion only; it does not assign a
geometric volume to open states. The explicit probe preparations and their
complete/ring evolution example are in `closure_probes.py`.

Study drivers retain their sampling, analysis tables, plots, provenance, and
repository-specific output paths. They are not included in the wheel. The
wheel includes compatibility imports for `coherent_states`, `correspondence`,
`grassmannian`, `minkowski`, `positivity`, and `sparse_schwinger`.

Run the tests from the repository root:

```bash
python -m unittest discover -s code/python -p 'test_*.py'
```

Same-number singlet dissociation thresholds are evaluated by `binding_energy.py`.
Run `python code/python/binding_energy.py` from the repository root; it saves
`results/binding-energy/summary.json`. See `notes/binding-energy.md` for the
state definitions, separation convention, and finite-graph interpretation.

`sewing_probes.py` evaluates the constructive F-pair triangle, tetrahedral,
and joined exterior-boundary networks using `lqg_scattering.sewing`.
See `notes/constructive-sewing-probe.md`; these tensor contractions do not
assign a Hamiltonian or reuse the face-site binding energies.

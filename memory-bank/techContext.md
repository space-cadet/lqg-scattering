# Tech Context

*Last Updated: 2026-10-10 03:26:38 IST*

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Rust implementation | Rust (`sprs`, `rayon`, `nalgebra`) | Sparse numerical engine |
| Python reference | Python 3 (NumPy, SciPy) | State construction, n=4 validation, scans, and figure generation |
| Dashboard | HTML, JavaScript, static JSON/SVG | Research result viewer |
| Memory Bank tools | Node.js, `sql.js`, Express | Markdown parsers, searchable database, and viewer |
| Version control | Git + GitHub | Source management |
| Memory Bank | mb-core v6.12 | Project knowledge base |

## Source Layout

Project source code is grouped under `code/`:

```
code/
├── dashboard/                 # Dashboard page, browser code, static inputs/assets
├── memory-bank/database/      # Node.js parser and viewer source
├── papers/                    # LaTeX manuscripts and their build assets
├── python/                    # Python research calculations
│   ├── dashboard_assets/      # Python dashboard data and figure builders
│   └── project_paths.py       # Stable repository paths for Python scripts
├── rust/                      # Rust crate, sources, and examples
├── thermal/                   # Thermal coefficient figure and dependencies
├── tools/                     # Shell run recipes
└── project-paths.js           # Stable repository paths for Node.js scripts
```

Research notes and session history are in `notes/` and `memory-bank/`. Figures
and derived presentation assets are in `figures/`; calculation results remain
at the output paths recorded in their task notes.

## Python Reference Implementation

Reusable research code now lives in `code/python/lqg_scattering/`. Its modules
cover conventions and labels; Schwinger and singlet bases; intertwiners and
fixed-area states; coherent states; spinors, tetrahedra, Grassmannian and
Minkowski geometry; correspondence maps; observables; and positive volume.
Top-level files such as `coherent_states.py`, `positivity.py`,
`grassmannian.py`, `minkowski.py`, and `correspondence.py` are compatibility
facades that re-export package implementations. Study entry points remain in
`code/python/`, retaining sampling/output. Shared Hamiltonian and
variable-face cores are extracted into package APIs, alongside thermal and
fitting helpers. `hamiltonian.py` supplies arbitrary-site full fixed-number
models; `total_spin.py` handles pure/density closure and spin probabilities.
`preparations.py` supplies explicit coherent products and the FL seed.
`sewing.py` separately supplies edge-leg tensors and invariant contractions,
including optional link transports; it has no assigned Hamiltonian.

The pinned calculation environment is described by
`code/python/requirements.txt` (NumPy 1.24.3, SciPy 1.15.3, SymPy 1.14.0).
Plot and dashboard-image dependencies are in
`code/python/requirements-visualization.txt` (Matplotlib 3.10.8 and Pillow
12.1.0). The package metadata declares NumPy, SciPy, and SymPy as runtime dependencies;
visualization dependencies are optional. Wheel, sdist, wheel-from-sdist,
external installation, and numerical smoke checks passed. Root-level research
commands and installation guidance are in `code/README.md`.

The T11 Python-versus-TS comparison is recorded in
`results/python-vs-ts/README.md`. It is a warm local K=2 matched benchmark, not
a general language ranking: the saved TS end-to-end pipeline was about 529
times slower than Python for that workload, while sparse application was a
separate case. K=3 has no saved matched artifact and K=4 TS was stopped. The
user selected Python plus Rust for this research code; the benchmark does not
establish performance for other tasks or system sizes.

Python entry-point scripts should be run from the repository root; see
`code/README.md` for examples.

## Rust Crate

The Cargo manifest is `code/rust/Cargo.toml`. Rust sources are in
`code/rust/src/`, and example programs are in `code/rust/examples/`. The
repository-root recipe for the T5e sweep is `code/tools/run_t5e.sh`.

## Shared calculation conventions

The Python and Rust routines construct LQG Fock and coherent states, with
independent local-spin checks for selected sectors. The scoped Python package
extraction is complete and validated against saved results. Full-number
models use tuple occupation keys and are distinct from projected singlet
models. Sewn edge-leg spin networks are a third state-space description;
fully contracted identity-link values are evaluations, not state norms or
Hamiltonian energies. The
JavaScript Memory Bank database and dashboard present project information;
neither supplies state construction routines.

## Constraints

- Fock-space dimensions grow combinatorially with the number of modes and bosons.
- Positive-volume spectral calculations currently limit active dense blocks to dimension 512.
- Numerical claims remain bounded by the specific states, ranges, controls, and checks recorded in their task notes.

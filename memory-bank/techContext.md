# Tech Context

*Last Updated: 2026-10-08 10:28 IST*

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

| File | Purpose |
|------|---------|
| `code/python/coherent_states.py` | U(N) coherent-state construction |
| `code/python/positivity.py` | Positive Grassmannian-cell tests and volume expectations |
| `code/python/fl_volume_validation.py` | FL volume validation and independent local-spin comparison |
| `code/python/t7_geometry_thermal.py` | Earlier small-sector thermal-intertwiner pilot |
| `code/thermal/plot_vacuum_coefficients.py` | Exact squeezed-vacuum coefficient and sector-probability figure |

Python entry-point scripts should be run from the repository root; see
`code/README.md` for examples.

## Rust Crate

The Cargo manifest is `code/rust/Cargo.toml`. Rust sources are in
`code/rust/src/`, and example programs are in `code/rust/examples/`. The
repository-root recipe for the T5e sweep is `code/tools/run_t5e.sh`.

## Shared calculation conventions

The Python and Rust routines construct LQG Fock and coherent states, with
independent local-spin checks for selected sectors. The JavaScript Memory Bank
database and dashboard present project information; neither supplies state
construction routines.

## Constraints

- Fock-space dimensions grow combinatorially with the number of modes and bosons.
- Positive-volume spectral calculations currently limit active dense blocks to dimension 512.
- Numerical claims remain bounded by the specific states, ranges, controls, and checks recorded in their task notes.

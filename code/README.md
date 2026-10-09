# Project code

Project source code is organized beneath this directory.

| Area | Location | Purpose |
|---|---|---|
| Python research calculations | `python/` | Shared Schwinger operators and state, volume, positivity, T5/T7/T11 studies |
| Rust research engine | `rust/` | Fock states, operators, volume, experiments, and examples |
| Dashboard application | `dashboard/` | HTML, JavaScript, data, and generated dashboard figures |
| Memory Bank tooling | `memory-bank/database/` | Node.js parsers, database schema, and viewer |
| Paper sources | `papers/` | LaTeX manuscripts, bibliography sources, and figure assets |
| Thermal coefficient figure | `thermal/` | Plot code; uses the shared Python visualization dependencies |
| Shell run tools | `tools/` | Repeatable command-line research workflows |
| Shared path definitions | `project-paths.js`, `python/project_paths.py` | Stable paths after source relocation |

Research notes, figures, and calculation outputs are organized in `notes/`, `figures/`, and `results/`. Each tool's README or task record gives the relevant command. Run research scripts from the repository root unless a task says otherwise.

## Python module responsibilities

- `python/lqg_scattering/` is the reusable Python library. Its modules own coherent states, exact and capped Schwinger bases, Grassmannian maps, spinors and tetrahedron geometry, fixed-area FL intertwiners, flux statistics, singlet recoupling, and RS/AL volumes. `hamiltonian.py` owns the exact four-site operator builder; `volume_blocks.py` owns variable-face RS blocks and independent matrix checks; `thermal.py` owns Gibbs weights and reduced-state/TFD readouts; `analysis.py` owns the shared power-law fit.
- Top-level files such as `coherent_states.py`, `positivity.py`, `grassmannian.py`, and `correspondence.py` are compatibility facades. New code imports their implementations from `lqg_scattering`.
- T5, T7, and T11 files are study drivers. Shared calculation helpers now live in the package; each driver retains its sampling choices, analysis, and result format.
- `python/sparse_schwinger.py` re-exports the package engine for existing scripts. `python/fl_volume_validation.py`, `python/fl_volume_labels.py`, and `python/closed_basis_volume.py` keep their command-line study entry points and use package implementations.

Install the package in editable mode after installing the pinned research dependencies:

```bash
python3 -m pip install -r code/python/requirements.txt
python3 -m pip install -e code/python
```

The package metadata is in `python/pyproject.toml`. NumPy, SciPy, and SymPy are runtime dependencies; plotting libraries are in the optional `visualization` extra. The built wheel contains the package and compatibility facades, while study drivers and repository-specific paths remain in the checkout. The Hamiltonian builder retains the tested four-site scope.

Independent tensor, oscillator, and commutator constructions are retained when they check one another numerically; those are separate validation routes, not duplicate production modules. Selected Python and Rust kernels also remain separate so the small-sector parity checks and larger sparse runs can be compared directly.

## Python environment

Install the numerical stack for quantum calculations with:

```bash
python3 -m pip install -r code/python/requirements.txt
```

Plotting and dashboard-image scripts also need the optional visualization
dependencies:

```bash
python3 -m pip install -r code/python/requirements-visualization.txt
```

The requirements files are the single source of version pins. The older
thermal requirements path forwards to the shared visualization list.

## Thermal sector plot

- [Research note](../notes/thermal-area-sectors.md)
- [Figure and data](../figures/thermal-area-sectors/)
- [Plot script](thermal/plot_vacuum_coefficients.py)
- [Python dependencies](python/requirements-visualization.txt)

Run the figure generator from the repository root after installing the visualization dependencies:

```bash
MPLCONFIGDIR=/tmp/lqg-mpl-config python code/thermal/plot_vacuum_coefficients.py
```

The output directory is resolved from the script's repository location.

## Python research calculations

The modules in `python/` contain the project's research calculations and
shared operator code. Install their requirements above, then run entry-point
scripts from the repository root, for example:

```bash
python3 code/python/fl_volume_validation.py
python3 code/python/t7_geometry_thermal.py
conda run -n qc-diff python code/python/hamiltonian_studies.py
```

Run the library and sparse Schwinger checks from the repository root with:

```bash
python3 -m unittest discover -s code/python -p 'test_*.py'
```

Data inputs and results use the paths documented by each task; running from
the repository root keeps relative command-line arguments stable. Default
result outputs are written under `results/`.

The four-site Hamiltonian and volume pilot is tracked in
[`memory-bank/tasks/T11.md`](../memory-bank/tasks/T11.md), with its methods and
results in [`notes/hamiltonian-studies.md`](../notes/hamiltonian-studies.md).

## Rust research engine

The crate is in `code/rust/`. For a normal build, run
`cargo build --manifest-path code/rust/Cargo.toml --release` from the
repository root. Example programs are in `code/rust/examples/`.

The T5e sweep and fit recipe is `bash code/tools/run_t5e.sh`.

## Dashboard

The dashboard page and its JavaScript, JSON inputs, and SVG assets are in
`code/dashboard/`. Serve that directory as a static site. Its Python data and
thumbnail builders are in `code/python/dashboard_assets/`.

Rebuild the saved-study catalogue and packaged plots/downloads with
`conda run -n qc-diff python code/python/dashboard_assets/build_research_catalogue.py`.
See [dashboard instructions](dashboard/README.md) for the data and artifact layout.

## Memory Bank tools

The parser, schema, and viewer package is in
`code/memory-bank/database/`. From the repository root:

```bash
pnpm --dir code/memory-bank/database install
pnpm --dir code/memory-bank/database start
```

The Memory Bank source is in `memory-bank/`; runtime database files are
stored in `memory-bank/database/`.

## Paper sources

LaTeX source and its build assets are in `code/papers/`. Compiled PDFs remain
in `paper/` as research outputs.

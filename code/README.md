# Project code

Project source code is organized beneath this directory.

| Area | Location | Purpose |
|---|---|---|
| Python research calculations | `python/` | State, volume, positivity, T5 and T7 calculations |
| Rust research engine | `rust/` | Fock states, operators, volume, experiments, and examples |
| Dashboard application | `dashboard/` | HTML, JavaScript, data, and generated dashboard figures |
| Memory Bank tooling | `memory-bank/database/` | Node.js parsers, database schema, and viewer |
| Paper sources | `papers/` | LaTeX manuscripts, bibliography sources, and figure assets |
| Thermal coefficient figure | `thermal/` | Plot code and Python dependency list |
| Shell run tools | `tools/` | Repeatable command-line research workflows |
| Shared path definitions | `project-paths.js`, `python/project_paths.py` | Stable paths after source relocation |

Research notes, figures, and calculation outputs are organized in `notes/`, `figures/`, and `results/`. Each tool's README or task record gives the relevant command. Run research scripts from the repository root unless a task says otherwise.

## Thermal sector plot

- [Research note](../notes/thermal-area-sectors.md)
- [Figure and data](../figures/thermal-area-sectors/)
- [Plot script](thermal/plot_vacuum_coefficients.py)
- [Python dependencies](thermal/requirements.txt)

Run the figure generator from the repository root with an environment containing NumPy, SciPy, and Matplotlib:

```bash
MPLCONFIGDIR=/tmp/lqg-mpl-config python code/thermal/plot_vacuum_coefficients.py
```

The output directory is resolved from the script's repository location.

## Python research calculations

The modules in `python/` form the project's research calculation library.
Run entry-point scripts from the repository root, for example:

```bash
python3 code/python/fl_volume_validation.py
python3 code/python/t7_geometry_thermal.py
```

Data inputs and results use the paths documented by each task; running from
the repository root keeps relative command-line arguments stable. Default
result outputs are written under `results/`.

## Rust research engine

The crate is in `code/rust/`. For a normal build, run
`cargo build --manifest-path code/rust/Cargo.toml --release` from the
repository root. Example programs are in `code/rust/examples/`.

The T5e sweep and fit recipe is `bash code/tools/run_t5e.sh`.

## Dashboard

The dashboard page and its JavaScript, JSON inputs, and SVG assets are in
`code/dashboard/`. Serve that directory as a static site. Its Python data and
thumbnail builders are in `code/python/dashboard_assets/`.

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

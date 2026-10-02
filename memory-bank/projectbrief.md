# Project Brief

*Last Updated: 2026-10-01 20:31 IST*

## Project Overview
LQG-Scattering is a numerical physics project that interfaces Loop Quantum Gravity (LQG) spin networks with scattering amplitudes via Grassmannian geometry. The follow-up code computes signed triple-grasp means and a square-root-of-mean proxy on U(N) coherent states. Its relation to a positive quantum volume operator and classical volume is open.

The EPJC paper (lqg-amplituhedron) is published. Current work is follow-up numerical computation that was not feasible at publication time.

## Research Goals and Current Phase

### Completed foundation
- Build the Python reference for the n=4 correspondence and volume calculation.
- Build the Rust implementation and record scans through n=8; revalidate their coherent-state convergence and complex-plane magnitudes.
- Preserve the published EPJC paper as the frozen baseline.

### Current research program
- Establish where the signed triple-grasp mean vanishes and calculate a specified positive volume-operator expectation separately.
- Determine whether chirality is a vertex-wide property or depends on each edge triple.
- Test whether the computed quantum volume has a classical polyhedron interpretation and a controlled large-area limit.
- Extend the real-momentum work to thermal and doubled (TFD) states, with explicit limits on what the tested constructions establish.
- Reconnect the geometric results to scattering kinematics and amplituhedron regions.
- Maintain a follow-up manuscript whose claims track validated results and open caveats.

## Core Features
- Fock space construction for Schwinger bosons (Python + Rust)
- U(N) Perelomov coherent states
- Triple-grasp commutator and signed-mean proxy; positive-volume calculation open
- Grassmannian embedding (Plücker coordinates)
- Positive Grassmannian cell identification
- n=4..8 benchmark suite

## Project Structure
```
lqg-scattering/
├── paper/
│   ├── lqg-amplituhedron.tex      # EPJC published paper (DO NOT MODIFY)
│   ├── lqg-amplituhedron.pdf      # Published PDF
│   └── lqg-amplituhedron.bib
├── rust/
│   ├── Cargo.toml
│   └── src/
│       ├── main.rs                # Binary entry + benchmark scan
│       ├── lib.rs                 # Module re-exports
│       ├── fock.rs                # Fock space basis (Schwinger bosons)
│       ├── ops.rs                 # Sparse u(N) operators
│       ├── coherent.rs            # U(N) Perelomov coherent states
│       ├── volume.rs              # Triple-grasp commutator and signed-mean proxy
│       └── grassmannian.rs        # Grassmannian embedding
├── coherent_states.py             # Python reference (n=4)
├── positivity.py                  # Python positivity checks
├── manifold.py                    # Python geometric utilities
├── rotation.py                    # Python rotation operators
└── memory-bank/                   # Project knowledge base
```

## Key Components
- **Fock space**: Schwinger boson formalism, U(N) decomposition, basis enumeration
- **Coherent states**: Perelomov U(N) coherent states for intertwiners
- **Triple grasp**: sparse commutator and signed-mean proxy; positive-volume interpretation open
- **Grassmannian**: Plücker embedding, positive cell identification

## Current Status (2026-10-01)
- Published paper and the Python/Rust implementation phases are recorded complete.
- Corrected Rust/Python n=4 comparison and converged n=4..8 scans are recorded. Independent SciPy checks cover n=4,5,7,8; n=6 remains unchecked independently. An independent positive-plane $n=4$ state has $\langle q\rangle\approx0$ but $\langle q^2\rangle=0.375981$.
- The follow-up manuscript is a developed draft, not yet recorded as reviewed or circulated.
- T5 has a mix of completed experiments and open investigations; the T5a magnetization sweep has been rerun with converged states for one plane.
- T7a..T7e have reported results for their tested constructions; follow-up work is needed for a temperature-dependent coherent-sector law.
- Current focus: reconcile manuscript claims and task records, repair or qualify provisional results, then conduct an independent claim review before circulation.

## Task Tracking
See `tasks.md` for current T4, T5, and T7 states. The T3 implementation and corrected T3d/T3e numerical runs are recorded; independent n=6 verification remains open. See `implementation-details/red-team-audit.md`.

## Memory Bank Organization
- `/memory-bank/`: Core documentation files
- `/memory-bank/implementation-details/`: Technical deep-dives
- `/memory-bank/tasks/`: Individual task files (T1.md, T2.md, etc.)
- `/memory-bank/sessions/`: Session logs
- `/memory-bank/templates/`: File templates
- `/memory-bank/archive/`: Archived documentation

## Implementation Guidelines
- ALL numerical claims must pass the red-team protocol before being reported
- Simulation scripts must be checkpointable and resumable
- Sparse matrices are mandatory for Fock spaces above n=4
- Rust implementation must match Python at n=4 to f64 machine precision

## External Dependencies
- Rust: sprs (sparse matrices), rayon (parallelism), nalgebra (dense linear algebra)
- Python: NumPy, SciPy (reference implementation only)
- ORX (OpenResearch): Agent-driven development and benchmarking

## Notes
The EPJC paper (lqg-amplituhedron) is the published baseline. Current work extends it with numerical results for n≥5 that were computationally infeasible at publication time. The paper directory is frozen; all new work goes in rust/ and follow-up manuscript drafts.

# Project Brief

*Last Updated: 2026-09-19 16:30 IST*

## Project Overview
LQG-Scattering is a numerical physics project that interfaces Loop Quantum Gravity (LQG) spin networks with scattering amplitudes via Grassmannian geometry. The project computes the quantum volume of U(N) coherent states embedded in the positive Grassmannian, connecting LQG geometry to the amplituhedron program.

The EPJC paper (lqg-amplituhedron) is published. Current work is follow-up numerical computation that was not feasible at publication time.

## Goals
- Primary: Compute quantum volume for n≥5 vertices via Rust implementation (Python too slow for n≥5)
- Secondary: Verify Rust implementation against Python at n=4 (machine precision)
- Tertiary: Draft follow-up manuscript with numerical results for n=4..8

## Core Features
- Fock space construction for Schwinger bosons (Python + Rust)
- U(N) Perelomov coherent states
- Volume operator via Bianchi-Haggard-Thiemann formula
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
│       ├── volume.rs              # Volume operator (BHT)
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
- **Volume operator**: BHT triple-grasp formula, sparse matrix construction
- **Grassmannian**: Plücker embedding, positive cell identification

## Current Status
- Overall Progress: ~60% (Python complete, Rust Phase C in progress)
- Active Tasks: 1 (T3c)
- Current Focus: Rust volume operator implementation and n=4 verification

## Task Tracking
Tasks are tracked in `tasks.md` with the following priority structure:
- **High Priority**: T3c (Rust volume operator), T3d (n=4 verification)
- **Medium Priority**: T3e (n≥5 benchmarks), T4 (follow-up manuscript)
- **Low Priority**: Polish and documentation

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

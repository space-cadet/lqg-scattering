# Rust Port Architecture

## Overview

The Rust port reimplements the LQG-Grassmannian pipeline for n≥5 vertices, where Python becomes computationally infeasible due to Fock space dimension growth.

## Crate Structure

```
rust/
├── Cargo.toml          # sprs, rayon, nalgebra dependencies
└── src/
    ├── main.rs         # Binary entry, benchmark scan loop
    ├── lib.rs          # Module re-exports
    ├── fock.rs         # Fock space basis (Schwinger bosons)
    ├── ops.rs          # Sparse u(N) operators
    ├── coherent.rs     # U(N) Perelomov coherent states
    ├── volume.rs       # Volume operator (BHT)
    └── grassmannian.rs # Plücker embedding, positivity tests
```

## Design Decisions

### Sparse-First (sprs)
All operators use `sprs::CsMat` (compressed sparse column). Dense matrices are used only for small test cases. This is essential because:
- Fock dimension for n=8, J=1 is ~286
- Volume operator is a large sparse matrix
- Dense storage would exhaust memory for n≥6

### Parallelism (rayon)
Basis state enumeration and matrix construction use `rayon` for data-parallel iteration. Target: near-linear speedup on multi-core.

### Module Separation
Each physics concept is isolated in its own module:
- `fock.rs`: Basis generation only
- `ops.rs`: Operator construction only
- `coherent.rs`: Coherent state preparation only
- `volume.rs`: Volume operator assembly only
- `grassmannian.rs`: Geometric embedding only

This allows independent testing and verification of each component.

## Verification Strategy

The n=4 case is the ground truth. Rust must reproduce Python results to f64 machine precision. See `verification-protocol.md` for details.

## Benchmarking

`main.rs` includes a `scan()` function that runs the full pipeline for n=4..8 and reports timing, memory usage, and volume eigenvalues. Results are recorded in `performance-benchmarks.md`.

## Future Extensions

- GPU acceleration via `wgpu` or `cust` for n>8
- Distributed computing for very large Fock spaces
- Integration with symbolic algebra for analytical cross-checks

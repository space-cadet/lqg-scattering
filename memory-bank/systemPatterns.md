# System Patterns

*Last Updated: 2026-09-19 16:30 IST*

## Design Patterns and Conventions

### Numerical Computing
- **Sparse matrices are mandatory** for Fock spaces above n=4 — dense matrices exhaust memory
- **Checkpointable and resumable** — any computation >10 minutes must write incremental results and support `--resume`
- **Red-team protocol** — all numerical claims must pass 5-gate validation before being reported or committed
- **Cross-implementation verification** — Rust results must match Python at n=4 to f64 machine precision

### Code Organization
- **Published paper is frozen** — `paper/lqg-amplituhedron.tex` must not be modified
- **Rust is the production implementation** — Python is reference/benchmark only
- **Sparse-first design** — all operators use sprs::CsMat, dense only for small test matrices
- **Parallel by default** — rayon for basis state iteration and matrix construction

### Naming Conventions
- `[TEST]` prefix for runs with <500K sweeps to distinguish from production
- Task IDs: T{number} for major tasks, T{number}{letter} for subtasks (T3a, T3b, etc.)
- Rust modules: snake_case matching physics concept (fock.rs, coherent.rs, volume.rs)

### Testing Strategy
- Unit tests in each Rust module (`#[cfg(test)]`)
- n=4 is the critical benchmark — must match Python exactly
- Integration test: `cargo test --release` runs all tests including cross-validation

### Version Control
- All work committed to git before ORX session ends
- ORX worktree is the canonical development location
- GitHub: https://github.com/space-cadet/lqg-scattering

## Anti-Patterns to Avoid
- Dense matrices for large Fock spaces (memory explosion)
- Modifying the published paper
- Reporting numerical results without red-team validation
- Python for n≥5 computations (too slow)

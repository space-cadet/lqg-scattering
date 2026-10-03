# Verification Protocol

## Overview

The $n=4$ case is the cross-implementation reference, but matching Rust and
Python is insufficient when both use the same truncated coherent state. The
2026-10-01 red-team audit found such a shared truncation. The corrected n=4 state and signed mean now match an independent SciPy exponential. A positive volume-operator calculation and an independent n=6 scan check remain open.

## Procedure

### Step 1: Run Python Reference
```bash
cd lqg-scattering
python3 positivity.py
```
Record: triple-grasp matrix properties, coherent state overlaps, Grassmannian
Plücker coordinates, and the signed-mean proxy. Separately compute a specified
positive volume-operator expectation if claiming quantum volume.

### Step 2: Run Rust Implementation
```bash
cd rust
cargo run --release --bin lqg_grassmannian -- verify4
```
Record: the canonical $n=4$ positive and complex-plane values. Then use
`cargo run --release --bin lqg_grassmannian -- scan` for the higher-$n$ benchmark after the
canonical comparison passes.

### Step 3: Compare

| Quantity | Tolerance | Criterion |
|----------|-----------|-----------|
| Signed $\langle q\rangle$ on the complex plane | rtol $=10^{-11}$ | Match corrected Python and independent exponential |
| Area means and uncertainties | rtol $=10^{-11}$ | Match at the same state |
| Normalized coherent-state vectors | norm difference $<10^{-11}$ | Compare after mapping the occupation bases |
| Plücker coordinates | rtol = 1e-12 | Exact match (f64) |
| Positive real-plane $\langle q\rangle$ | absolute $<10^{-12}$ | Check real-state symmetry |
| Complex-plane state | relative norm $<10^{-11}$ | Match `scipy.sparse.linalg.expm_multiply` |
| Positive-plane $\langle q^2\rangle$ | absolute $<10^{-10}$ | Keep distinct from $\langle q\rangle$ |

### Step 4: Investigate Discrepancies

Any mismatch indicates a bug in:
1. Fock space basis enumeration (fock.rs)
2. Operator construction (ops.rs)
3. Coherent state normalization (coherent.rs)
4. Volume operator assembly (volume.rs)
5. Grassmannian embedding (grassmannian.rs)

## Cross-Implementation Checklist

- [ ] Same Fock space dimension
- [ ] Occupation bases mapped consistently
- [ ] Same operator matrix elements
- [ ] Same signed-mean and area observables on a converged state
- [ ] Same coherent state parameters
- [ ] Same Plücker coordinates
- [ ] Zero signed mean on real planes confirmed, including a mixed-sign-minor control
- [ ] State convergence and independent exponential confirmed
- [ ] Positive volume-operator definition and expectation checked separately

## Sign-off

Verification is complete only when all checklist items pass on the final
state-construction code. Record seeds, references, tolerances, and results in
`performance-benchmarks.md` before promoting T3e magnitudes.

## Related documentation

- [Shared volume numerical preliminaries](./volume-numerical-preliminaries.md)
- [Volume operator](./volume-operator.md)
- [T5 volume-positivity studies](./volume-positivity-studies.md)
- [T5c calculation specification](./T5c-flux-covariance-volume-comparison.md)
- [Fock-space construction](./fock-space-construction.md)
- [Grassmannian embedding](./grassmannian-embedding.md)
- [Rust port architecture](./rust-port-architecture.md)
- [Performance benchmarks](./performance-benchmarks.md)
- [Red-team audit](./red-team-audit.md)

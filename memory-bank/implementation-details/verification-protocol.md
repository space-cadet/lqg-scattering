# Verification Protocol

## Overview

The n=4 case is the ground truth for verifying the Rust implementation. Python has been analytically verified; Rust must reproduce identical results.

## Procedure

### Step 1: Run Python Reference
```bash
cd lqg-scattering
python3 positivity.py
```
Record: volume eigenvalues for n=4, coherent state overlaps, Grassmannian Plücker coordinates.

### Step 2: Run Rust Implementation
```bash
cd rust
cargo run --release -- scan
```
Record: identical quantities from Rust.

### Step 3: Compare

| Quantity | Tolerance | Criterion |
|----------|-----------|-----------|
| Volume eigenvalues | rtol = 1e-12 | Exact match (f64) |
| Coherent state norms | rtol = 1e-12 | Exact match (f64) |
| Plücker coordinates | rtol = 1e-12 | Exact match (f64) |
| Positive cell volume | exact zero | Must be exactly 0.0 |

### Step 4: Investigate Discrepancies

Any mismatch indicates a bug in:
1. Fock space basis enumeration (fock.rs)
2. Operator construction (ops.rs)
3. Coherent state normalization (coherent.rs)
4. Volume operator assembly (volume.rs)
5. Grassmannian embedding (grassmannian.rs)

## Cross-Implementation Checklist

- [ ] Same Fock space dimension
- [ ] Same basis state ordering
- [ ] Same operator matrix elements
- [ ] Same volume eigenvalues
- [ ] Same coherent state parameters
- [ ] Same Plücker coordinates
- [ ] Zero volume on positive cell confirmed

## Sign-off

Verification is complete when all checklist items pass. Record results in `performance-benchmarks.md` and proceed to T3e (n≥5 benchmarks).

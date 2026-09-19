# Volume Operator Implementation

## Overview

The volume operator for LQG intertwiners is implemented via the Bianchi-Haggard-Thiemann (BHT) formula, which expresses the volume as a sum over triple-grasp operators acting on the intertwiner space.

## BHT Formula

For a 4-valent intertwiner with spins j1,j2,j3,j4, the volume matrix elements are:

V_{j12,j12'} = (8πγ)^{3/2} / √2 * |q_{j12,j12'}|^{1/2}

where q is the triple-grasp operator matrix.

## Implementation Strategy

### Python Reference (n=4)
- Direct matrix construction using NumPy
- Explicit Fock space basis enumeration
- Verified against analytical results

### Rust Port (n≥5)
- Sparse matrix representation using `sprs` crate
- Parallel matrix construction using `rayon`
- Target: handle Fock dimensions up to ~10^6 for n=8

## Key Files

| File | Purpose |
|------|---------|
| `rust/src/fock.rs` | Fock space basis generation |
| `rust/src/ops.rs` | Angular momentum operators (sparse) |
| `rust/src/volume.rs` | Volume operator construction |
| `rust/src/grassmannian.rs` | Grassmannian embedding |
| `rust/src/coherent.rs` | U(N) coherent states |

## Verification

The n=4 case is the critical benchmark. Python and Rust implementations must agree to machine precision (f64, rtol=1e-12).

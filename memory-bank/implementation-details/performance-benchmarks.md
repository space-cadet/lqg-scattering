# Performance Benchmarks

*Last Updated: 2026-09-19 16:30 IST*

## Overview

Timing and memory usage for the Rust LQG-Grassmannian pipeline. Benchmarks are run via `cargo run --release -- scan`.

## Current Results

| n | Volume Computed | Zero on Positive Cell | Time | Memory | Status |
|---|-----------------|----------------------|------|--------|--------|
| 4 | — | — | — | — | 🔄 In progress (T3c) |
| 5 | — | — | — | — | ⏳ Pending T3d |
| 6 | — | — | — | — | ⏳ Pending T3d |
| 7 | — | — | — | — | ⏳ Pending T3d |
| 8 | — | — | — | — | ⏳ Pending T3d |

## Target Performance

| n | Target Time | Max Memory |
|---|-------------|------------|
| 4 | < 1 second | < 10 MB |
| 5 | < 5 seconds | < 50 MB |
| 6 | < 30 seconds | < 200 MB |
| 7 | < 2 minutes | < 500 MB |
| 8 | < 5 minutes | < 1 GB |

## Scaling Analysis

Fock space dimension: dim = C(2J + n - 1, n - 1)

For J=1:
- n=4: dim = 10
- n=5: dim = 35
- n=6: dim = 84
- n=7: dim = 165
- n=8: dim = 286

Volume operator matrix size: dim × dim

Expected scaling: O(dim³) for dense diagonalization, O(nnz × dim) for sparse operations.

## Zero-Volume Confirmation

| n | Volume on Positive Cell | Status |
|---|------------------------|--------|
| 4 | 0.0 | ✅ Confirmed (Python) |
| 5 | — | ⏳ Pending |
| 6 | — | ⏳ Pending |
| 7 | — | ⏳ Pending |
| 8 | — | ⏳ Pending |

## Notes

Benchmarks will be populated by ORX agent as T3c, T3d, and T3e complete. Results feed into the follow-up manuscript (T4).

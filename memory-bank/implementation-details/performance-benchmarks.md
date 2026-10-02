# Performance Benchmarks

*Last Updated: 2026-10-01 20:31 IST*

## Overview

Timing and memory usage for the Rust LQG-Grassmannian pipeline. Benchmarks are run via `cargo run --release -- scan`.
The current values come from the 2026-10-01 converged Rust release scan. Its 20 release tests passed. The historical 15-term scan values were superseded. The listed $V$ is the signed-mean proxy
$V_{\rm proxy}=(\gamma\hbar)^{3/2}\sqrt{|\langle q\rangle|}$, not the
expectation of a positive volume operator.

## Results

| n | K | dim | V/g^1.5 (positive) | V/g^1.5 (complex) | Time | Status |
|---|---|-----|-------------------|-------------------|------|--------|
| 4 | 6 | 3,003 | 2.214953e-9 | 2.876955e-2 | 12–14ms | Rust/SciPy checked |
| 5 | 8 | 43758 | 3.286511e-9 | 3.391578e-2 | 303–325ms | Rust/SciPy checked |
| 6 | 9 | 293930 | 8.811059e-10 | 1.315281e-3 | 3.27–3.91s | Independent check open |
| 7 | 6 | 38760 | 3.661094e-10 | 1.186078e-2 | 330–383ms | Rust/SciPy checked |
| 8 | 6 | 74613 | 1.304153e-9 | 1.056697e-2 | 792–858ms | Rust/SciPy checked |

## Target Performance

| n | Target Time | Max Memory | Achieved |
|---|-------------|------------|----------|
| 4 | < 1 second | < 10 MB | ✅ 12ms |
| 5 | < 5 seconds | < 50 MB | ✅ 264ms |
| 6 | < 30 seconds | < 200 MB | ✅ 2.96s |
| 7 | < 2 minutes | < 500 MB | ✅ 299ms |
| 8 | < 5 minutes | < 1 GB | ✅ 724ms |

## Scaling Analysis

For $2n$ oscillator modes and total occupation at most $K$, the basis
dimension is $\binom{2n+K}{K}$. The $n=4$, $K=6$ basis therefore has 3,003
states; the old table's `10` was a small illustrative sector, not the
`verify4` basis.

Triple-grasp matrix size: dim × dim

Expected scaling depends on the sparse matrix fill pattern and the chosen
state construction; the recorded Rust runs were sub-minute at these settings.

## Real-plane signed-mean check

| n | Current proxy on real plane | Status |
|---|------------------------|--------|
| 4 | 2.21e-9 (≈ 0) | Signed mean only |
| 5 | 3.29e-9 (≈ 0) | Signed mean only |
| 6 | 8.81e-10 (≈ 0) | Signed mean only |
| 7 | 3.66e-10 (≈ 0) | Signed mean only |
| 8 | 1.30e-9 (≈ 0) | Signed mean only |

The listed proxy values are about $10^{-9}$ because the square root amplifies
rounding in $\langle q\rangle$; they are not machine-precision errors in the
proxy itself. The real-plane cancellation of $\langle q\rangle$ is analytic.
It does not imply $q|\psi\rangle=0$: an independent positive-plane $n=4$,
$K=6$ calculation gives $\langle q^2\rangle=0.375981$. The positive-volume
expectation was not calculated in these benchmarks.

## Notes

Initial benchmarks were recorded on 2026-09-19. The corrected values above were rerun on 2026-10-01. Times are single-run observations; memory targets were not remeasured.

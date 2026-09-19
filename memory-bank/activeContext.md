# Active Context

*Last Updated: 2026-09-19 16:30 IST*

## Current Focus
**Primary Task:** T3c
**Secondary Tasks:** T3d, T3e

## Active Tasks
- T3c: Rust volume operator — ORX agent actively debugging
- T3d: n=4 verification — pending T3c completion
- T3e: n≥5 benchmarks — pending T3d completion

## Implementation Focus
`rust/src/volume.rs` — the Bianchi-Haggard-Thiemann volume operator construction. Integration point between `fock.rs` (basis), `ops.rs` (operators), and `grassmannian.rs` (embedding).

## Task-Specific Context

### T3c: Volume Operator (Rust)
ORX agent (session chat_66108501) is implementing the BHT volume operator. Binary rebuilt at 16:08 IST. The volume operator is the most numerically sensitive component — it involves triple products of angular momentum operators acting on the intertwiner space. Sparse matrix representation is essential.

Key physics: V = sqrt(|det(E)|) where E are flux operators. The BHT formula expresses this as a sum over triple-grasp terms. For n=4, the volume matrix is small enough to verify against Python by hand.

### T3d: Verify Rust vs Python at n=4
The n=4 case is the ground truth. Python reference implementation (`positivity.py`) has been verified analytically. Rust must reproduce the same eigenvalues to f64 machine precision. Any discrepancy indicates a bug in either the Rust operator construction or the Fock space basis enumeration.

### T3e: Benchmarks n=5,6,7,8
After n=4 verification, run the full benchmark suite. Target: < 1 minute per n value. Record timing, memory usage, and confirm zero-volume on positive cell for all n. Results go into `performance-benchmarks.md` and the follow-up manuscript.

## Current Decisions
- ORX agent has been instructed to update `manuscript.md` as numerical results arrive (not just at the end)
- The EPJC paper is frozen; all new results go in the follow-up manuscript draft
- Rust is the production implementation; Python is reference only

## Next Actions By Task
- T3c: Wait for ORX agent to complete volume operator debug, verify n=4 match
- T3d: Run `cargo run --release -- scan` and compare with Python output
- T3e: Run full benchmark suite, record results, confirm zero-volume for all n
- T4: Begin drafting follow-up manuscript with available results

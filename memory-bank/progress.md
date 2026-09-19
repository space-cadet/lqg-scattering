# Implementation Progress

*Last Updated: 2026-09-19 18:41 IST*

## Active Tasks

### T4: Follow-up Manuscript
**Status:** 🔄 IN PROGRESS
**Priority:** MEDIUM

#### Completed Steps
- ✅ EPJC paper identified as frozen published baseline
- ✅ manuscript.md restructured: published baseline → follow-up numerical work
- ✅ Numerical results section drafted (n=4..8 volume data)

#### Current Work
- 🔄 ORX agent completed Rust implementation; manuscript has full numerical results
- 🔄 Dashboard created for data visualization

#### Up Next
- ⬜ Polish numerical results section
- ⬜ Add scaling law analysis
- ⬜ Circulate for review

### T5: Experiments
**Status:** ⬜ PROPOSED
**Priority:** HIGH

**Roadmap:** `memory-bank/implementation-details/experiments.md`

Seven experiments probing the volume–positivity (achirality) boundary, prioritized #6→#5→#3 (triple correlations, perturbation response, classical volume match) as highest physics-per-effort. Subtasks T5a–T5g in `tasks.md`. Not yet started — awaiting Deepak's go on which to run first.

## Completed Tasks

### T1: Python Pipeline
**Completed:** 2026-09-19
**Summary:** Reference implementation of Fock space, U(N) coherent states, Grassmannian embedding, and positivity tests in Python. All n=4 computations completed and verified.

### T1a: Volume Operator at n=4
**Completed:** 2026-09-19
**Summary:** BHT volume operator constructed and diagonalized for 4-valent intertwiners. Eigenvalues computed.

### T1b: Zero-Volume Result on Positive Cell
**Completed:** 2026-09-19
**Summary:** Volume operator vanishes identically on the positive Grassmannian cell. Central published result.

### T2: Manuscript (EPJC Paper)
**Completed:** 2026-09-19
**Summary:** LaTeX paper written, compiled, and published in EPJC. PDF at `paper/lqg-amplituhedron.pdf`.

### T3a: Fock Space + u(N) Operators (Rust)
**Completed:** 2026-09-19
**Summary:** Rust implementation of Schwinger boson Fock space and sparse u(N) operators. Committed as `ee3ff0e`.

### T3b: Coherent States + Grassmannian (Rust)
**Completed:** 2026-09-19
**Summary:** Rust implementation of U(N) Perelomov coherent states and Grassmannian Plücker embedding. Committed as `42ce24e`.

### T3c: Volume Operator (Rust)
**Completed:** 2026-09-19 16:26 IST
**Summary:** BHT volume operator implemented in Rust with sparse matrices. n=4 verification passed. Committed as `ee72845`.

### T3d: Verify Rust vs Python at n=4
**Completed:** 2026-09-19 16:26 IST
**Summary:** Machine precision match confirmed (rtol=1e-12). Volume eigenvalues identical. Committed as `c0908cf`.

### T3e: Benchmarks n=5,6,7,8
**Completed:** 2026-09-19 16:26 IST
**Summary:** All benchmarks completed. Max runtime 3.35s (n=6). Zero-volume confirmed for all n on positive cell. Results in `performance-benchmarks.md` and dashboard.

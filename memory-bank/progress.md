# Implementation Progress

*Last Updated: 2026-10-02 13:37:45 IST*

## Active Tasks

### T4: Follow-up Manuscript
**Status:** 🔄 IN PROGRESS
**Priority:** MEDIUM

#### Completed Steps
- ✅ EPJC paper identified as frozen published baseline
- ✅ manuscript.md restructured: published baseline → follow-up numerical work
- ✅ Numerical results section drafted (n=4..8 volume data)

#### Current Work
- 🔄 The manuscript contains results through T7e and separates signed-mean proxies from positive volume. RS/AL operators are now implemented for small active sectors; coherent-state volume results and claim review remain open.
- ✅ Independent red-team audit recorded in `implementation-details/red-team-audit.md`.

#### Up Next
- ✅ Reconciled the conclusion with T5e and qualified the T5a magnetization sweep.
- ✅ Corrected converged signed-mean scans completed. RS/AL positive volume routines implemented and checked on simple states; coherent-state volume reruns and large-block methods remain open.
- ⬜ Record independent red-team review per claim.
- ⬜ Circulate the corrected draft for review.

### T5: Experiments
**Status:** 🔄 IN PROGRESS (T5a base analysis recorded; magnetization sweep converged for one plane; T5a′ kinematic local-triple analysis recorded; T5b converged rerun complete for its tested family; T5e converged scoped study recorded; T5c, T5d, T5f, T5g open)
**Priority:** HIGH

**Roadmap:** `memory-bank/implementation-details/experiments.md`

Seven experiments probing signed triple-grasp response and its possible
relation to volume. The positive cell is not the full zero locus; see the
red-team audit. Subtasks T5a–T5g are in `tasks.md`.

**T5a evidence and caveat:** the n=6,7 base triple-correlation runs record sign-agreement 0.50–0.70 and small cross-seed correlations, consistent with per-triple chirality; n=8 remains resource-limited. The n=5 magnetization sweep was rerun with convergence assertions (39–41 terms) and four sectors matched independent SciPy exponentiation to at most 3.6e-16 in triple means. Its fixed-plane sign pattern remains one-plane evidence. T5a′ reports no increase in sign coherence for kinematic-polyhedron-local triples, with 8 planes per n=5 channel and weak per-plane sign-test power. See `t5a_mag_notes.md`, `t5a_prime_notes.md`, and `implementation-details/experiments.md`.

### T7: Thermal and TFD Program
**Status:** 🔄 IN PROGRESS (T7a–T7e results recorded for tested constructions; broader temperature-dependent coherent-sector question open)

- T7a reports zero mean signed triple grasp and nonzero $q^2$ fluctuations;
  the high-temperature end is cutoff-limited for the capped basis.
- T7b–T7c report a valid Gibbs purification and the tested identity `⟨q_L q_R⟩ = −Tr(ρ q²)`; the low-temperature Gibbs-TFD tends to the Fock vacuum, not a Perelomov state.
- T7d reports an exponential `e^{-3β}` onset in the tested Gibbs-TFD, not a power law.
- T7e reports a quadratic change with complexification in a fixed-`K` construction, with temperature flatness there. This does not establish a general combined `V(ε,T)` law.
- Notes and source data: `t7a_notes.md` through `t7e_notes.md` and corresponding result JSON files; manuscript status and scope need a final review.

## Historical Implementation and Runs

### T1: Python Pipeline
**Completed:** 2026-09-19
**Summary:** Reference implementation of Fock space, U(N) coherent states, Grassmannian embedding, and positivity tests in Python. All n=4 computations completed and verified.

### T1a: Volume Operator at n=4
**Completed:** 2026-09-19
**Summary:** Historical results were signed triple-grasp means and their proxy, not positive volume expectations. Exact small-sector RS and AL expectations are implemented. A preliminary EPJC Eq. (38) FL regular-tetrahedron evaluation is positive under both prescriptions; a roughly $1.8\times10^{-10}$ direct-method discrepancy, physical prefactors, and broader checks remain open.

### T1b: Signed-mean result on real planes
**Completed:** 2026-09-19
**Summary:** Real-plane states have zero signed triple-grasp mean, including
planes outside the positive cell. The positive volume-operator expectation
remains uncalculated; the historical zero-volume interpretation is withdrawn.

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
**Summary:** Sparse triple-grasp matrix and signed-mean proxy are retained. RS and AL positive vertex expectations are now implemented in project normalization for active sectors up to dimension 512.
The historical n=4 verification shared an unconverged Taylor state; the corrected Rust/Python and SciPy checks now agree. Committed as `ee72845`.

### T3d: Verify Rust vs Python at n=4
**Historical run:** 2026-09-19 16:26 IST
**Summary:** Historical Rust/Python match shared a 15-term Taylor truncation.
Corrected Rust/Python and independent SciPy checks agree on $\langle q\rangle=-0.000827687168$ for the canonical complex plane.

### T3e: Benchmarks n=5,6,7,8
**Historical run:** 2026-09-19 16:26 IST
**Summary:** Corrected converged Rust scans were completed for $n=5$–$8$. Independent SciPy checks $n=5,7,8$; $n=6$ remains open. The real-plane signed-mean cancellation
does not establish zero positive quantum volume.

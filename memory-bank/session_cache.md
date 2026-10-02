# Session Cache

*Last Updated: 2026-10-02 10:07 IST*

## Overview
- Active Tasks: T1a/T3c RS/AL volume validation; T4 manuscript; T5 volume program; T7 thermal/TFD program
- Paused Tasks: 0
- Current checkout: `main` at `d0f1e97`; local research and Memory Bank changes from the 2026-10-01 session remain uncommitted.

## Task Registry
- T4: Follow-up manuscript — 🔄 IN PROGRESS; correct claims, document review status, then circulate.
- T5: Volume–positivity experiments — 🔄 IN PROGRESS; T5a magnetization sweep converged for one plane; T5c/T5d/T5f/T5g open.
- T7: Thermal/TFD experiments — 🔄 IN PROGRESS; T7a–T7e recorded complete for tested setups; general temperature-dependent coherent-sector response remains open.
- T1–T3e: Python/Rust implementation and corrected converged scan recorded; n=6 independent state check remains open.

## Current Work

### T4: Follow-up Manuscript
**Status:** 🔄 IN PROGRESS

`manuscript.md` contains results through T7e and now distinguishes the signed-mean proxy from positive quantum volume. An independent audit found shared Taylor truncation and a real off-cell zero counterexample. Claim-level sign-off and circulation remain open. The published EPJC paper remains frozen.

### Positive volume operators
**Status:** 🔄 IN PROGRESS

Python and Rust now implement exact RS and AL positive expectations by dense spectral decomposition of populated fixed-spin blocks (maximum dimension 512). A paired spin-1/2 singlet gives $V_{RS}=0.304653190236$ and $V_{AL}=0.152326595118$ in repository normalization despite $\langle q_{012}\rangle=0$; independent tensor-product matrices agree. The outstanding project-state rerun targets the Freidel–Speziale coherent state used in the EPJC paper; its construction and volume evaluation remain open, along with physical prefactors and larger-block algorithms.

### T5: Volume–Positivity Program
**Status:** 🔄 IN PROGRESS

- T5a base triple correlations at n=6,7 are recorded; n=8 remains unresolved.
- T5a magnetization sweep was rerun with convergence assertions (39–41 terms); four sectors matched independent SciPy exponentiation to at most 3.6e-16 in triple means. The result remains one-plane evidence.
- T5a′ local kinematic-polyhedron test is recorded, with limited n=5 sample count and its own engine/convergence caveats.
- T5b has a corrected converged 13-point rerun at n=4,5; four n=4 and three n=5 points agree with independent SciPy exponentiation. The near-half proxy exponent is supported for this family. T5e has converged results for its tested range.
- T5c quantum/classical volume comparison, T5d distance/cocycle scaling, T5f scattering-region mapping, and T5g higher-n profiling remain open.

### T7: Thermal and TFD Program
**Status:** 🔄 IN PROGRESS

- T7a–T7e have recorded results for the tested constructions.
- Gibbs TFD approaches the Fock vacuum at low temperature; it does not approach a Perelomov state.
- T7e finds an approximately quadratic epsilon response and beta-flatness for the tested fixed-K construction; a general combined temperature/complexification law remains open.
- Small-beta Gibbs results are cutoff-limited; consult `t7a_notes.md` for the stated validity range.

## Completed Foundation
- Python pipeline and published EPJC paper.
- Rust Fock/coherent/volume pipeline.
- Corrected Rust/Python n=4 comparison and converged scans through n=8; independent SciPy checks cover n=4,5,7,8.

## Session History
- 2026-10-02: U(N) coherent-state discussion and cloud setup recorded; see `sessions/2026-10-02-morning.md` and `sessions/2026-10-02-morning-transcript.md`. Follow-up: work through Freidel–Livine Section D, Eqs. 47–51. Cloud Rust suite has one numerical regression failure; no research source was modified in that session.
- 2026-10-01: Project status and manuscript claims reconciled; red-team review gaps and research sequence assessed. See `sessions/2026-10-01-evening.md`.
- 2026-09-20: T7a/T7b thermal and Gibbs-TFD numerical work recorded; see `sessions/2026-09-20-T7a-thermal-state.md` and T7 notes.
- 2026-09-19: Rust phases and T5 experiment program integrated on `main`; see `memory-bank/tasks.md` and `memory-bank/progress.md`.

## Cloud Session Notes
- The cloud session documented that its `mem-scan` command was unavailable; this checkout has the global `mem-scan` skill available, but no project-specific five-gate red-team skill was found.
- Cloud checks recorded Rust 1.99/Cargo, NumPy/SciPy, release binaries, n=4 CLI and T5e smoke checks, and arXiv HTTP 200. Its Rust suite had one numerical regression failure (`experiment::tests::n4_sign_matches_python`; 18 other tests passed). Treat that as cloud-host evidence until rerun locally.

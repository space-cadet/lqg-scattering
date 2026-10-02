# Session Cache

*Last Updated: 2026-10-03 00:27:43 IST*

## Overview
- Active Tasks: T1a FL positive-volume shape numerics; T3c Rust reproduction; T4 manuscript; T5 volume program; T7 thermal/TFD program
- Paused Tasks: 0
- Checkout is `main` at `9b7f588`; uncommitted local files include the FL $J=2$ shape scan and dashboard edits. The website copy with shape thumbnails on both panels is deployed at `f0b6fdd` (workflow `37033479554`).

## Task Registry
- T1a: FL positive RS/AL area and shape numerics — 🔄 IN PROGRESS; $J=2$ equal-area grid minima are regular among 440 ordered samples; boundaries and unequal-area shape domains remain open.
- T3c: Rust positive-volume implementation — 🔄 IN PROGRESS; FL example source awaits working Cargo toolchain.
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

Python and Rust now implement exact RS and AL positive expectations by dense spectral decomposition of populated fixed-spin blocks (maximum dimension 512). A paired spin-1/2 singlet gives $V_{RS}=0.304653190236$ and $V_{AL}=0.152326595118$ in repository normalization despite $\langle q_{012}\rangle=0$; independent tensor-product matrices agree. The EPJC Eq. (38) FL regular-tetrahedron calculation gives positive RS/AL volumes, and a saved independent local-spin tensor-product calculation now matches the project routines below $7\times10^{-18}$. The source of the older unsaved $1.8\times10^{-10}$ discrepancy remains unknown. At $J=2$, both sampled RS/AL minima in a 440-point ordered equal-face-area grid occur at the regular tetrahedron; this is not a global-minimum proof, and exact degenerate limits were excluded. The positive-label enumerator finds one strict assignment with two recoupling channels, not a continuous shape count. See `fl_volume_shape_scan_log.md` for comparison data and scope limits. The final shape dashboard has 11 thumbnails per operator panel (22 total) and is live at website commit `f0b6fdd` (workflow `37033479554`). Next: study degenerate limits and volume spread across $J$, then extend shape sampling to unequal allowed assignments. Rust example execution, physical prefactors, and larger-block algorithms remain open.

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
- 2026-10-03: Recorded the $J=2$ equal-face FL shape scan, its finite-grid limitation, the fixed-$J$ label result, exploratory classical-volume comparison, and boundary/assignment follow-ups. The final shape dashboard with representative thumbnails on both RS and AL panels is live. See `sessions/2026-10-03-night.md` and `fl_volume_shape_scan_log.md`.
- 2026-10-02: Cloud setup and U(N) discussion recorded under T1a/T3c. The latest follow-up adds a reproducible FL Eq. (38) Python direct-tensor check and a Rust example; the independent Python methods agree, while the Rust run awaits toolchain recovery. See `sessions/2026-10-02-morning.md`.
- 2026-10-02: Extended the Python FL tetrahedron calculation through $J=1\ldots5$, added an RS/AL volume-versus-area dashboard plot, and published its website copy to `codex/lqg-scattering-dashboard` at `824b2b8`. Local browser verification passed with the CDN fallback; GitHub Actions dispatch and live-site verification remain pending API/browser access. See `sessions/2026-10-02-morning.md`.
- 2026-10-02: Used host access to dispatch and complete website workflow `36990851937` for `824b2b8`; live Projects, project, dashboard, JSON, and SVG requests returned HTTP 200. The Projects page hides the Scattering in LQG card inside its initially collapsed “Quantum physics and research” section; expanding it reveals the card. Live browser loaded the dashboard and plot. See `sessions/2026-10-02-morning.md`.
- 2026-10-01: Project status and manuscript claims reconciled; red-team review gaps and research sequence assessed. See `sessions/2026-10-01-evening.md`.
- 2026-09-20: T7a/T7b thermal and Gibbs-TFD numerical work recorded; see `sessions/2026-09-20-T7a-thermal-state.md` and T7 notes.
- 2026-09-19: Rust phases and T5 experiment program integrated on `main`; see `memory-bank/tasks.md` and `memory-bank/progress.md`.

## Cloud Session Notes
- The cloud session's `mem-scan` command was not registered in its skill/tool catalog. The later read-only memory-bank scan followed `integrated-rules-v6.12.md`; no project-specific five-gate red-team procedure was found.
- Cloud checks recorded Rust 1.99/Cargo, NumPy/SciPy, release binaries, n=4 CLI and T5e smoke checks, and arXiv HTTP 200. Its Rust suite had one numerical regression failure (`experiment::tests::n4_sign_matches_python`; 18 other tests passed). Treat that as cloud-host evidence until rerun locally.
- 2026-10-02 follow-up: pushed the session record as `d0f1e97`, then pulled `9602c98`. A read-only memory-bank audit used the integrated rules. This update reconciled checkout metadata and added October 2 edit chunks; task-registry schema drift and the rules filename/title mismatch remain. T1a/T3c remain open; the FL/F† discussion made no implementation change. Continue with Appendix D Eqs. 47–51 when requested.
- 2026-10-02 documentation follow-up: committed and pushed individual task records, session transcript/write-up, technical notes, and edit chunks as `1f84fd2`; the checkout is clean and matches `origin/main`.

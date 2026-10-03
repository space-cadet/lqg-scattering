# Session Cache

*Last Updated: 2026-10-03 18:53:30 IST*

## Overview
- Active Tasks: T1a FL positive-volume shape numerics; T3c Rust reproduction; T4 manuscript; T5 volume program; T7 thermal/TFD program
- Paused Tasks: 0
- Checkout is `main` at `e0d1ed7`; local modifications include the shared zero-mode cutoff, refreshed FL area/shape data, T1b results, and T5c shape-recovery artifacts. The latest dashboard visual update is deployed at website commit `9c6670c` (workflow `37125090987`); refreshed numerical data remain distinct from that presentation update.

## Task Registry
- T1a: FL positive RS/AL area and shape numerics — 🔄 IN PROGRESS; the 440-point $J=2$ scan and $J=1\ldots5$ area sweep were refreshed with a shared numerical zero-mode cutoff; boundary and unequal-area behavior remain open.
- T1b: Real-plane positive-volume follow-up — ✅ COMPLETE for two tested $N=4$, $K=6$ states; both RS and AL expectations are nonzero and independently checked.
- T3c: Rust positive-volume implementation — 🔄 IN PROGRESS; FL example matches Python using the direct Rust 1.92 toolchain; physical prefactors and blocks above 512 remain open.
- T4: Follow-up manuscript — 🔄 IN PROGRESS; correct claims, document review status, then circulate.
- T5: Volume–positivity numerical studies — 🔄 IN PROGRESS; T5a magnetization sweep converged for one plane; T5c/T5d/T5f/T5g open. T5c now has a selected-shape covariance scan for 14 shapes at $J=1\ldots6$ and reusable deployed shape previews; its state-to-geometry interpretation and comparison criteria remain open.
- T7: Thermal/TFD experiments — 🔄 IN PROGRESS; T7a–T7e recorded complete for tested setups; general temperature-dependent coherent-sector response remains open.
- T1–T3e: Python/Rust implementation and corrected converged scan recorded; n=6 independent state check remains open.

## Current Work

### T4: Follow-up Manuscript
**Status:** 🔄 IN PROGRESS

`manuscript.md` contains results through T7e and now distinguishes the signed-mean proxy from positive quantum volume. An independent audit found shared Taylor truncation and a real off-cell zero counterexample. Claim-level sign-off and circulation remain open. The published EPJC paper remains frozen.

### Positive volume operators
**Status:** 🔄 IN PROGRESS

Python and Rust implement RS and AL positive expectations by dense spectral decomposition of populated fixed-spin blocks (maximum dimension 512), with eigenvalues within $64\epsilon_{\rm mach}\max(1,\rho(|Q|))$ set to zero to remove numerical exact-kernel artifacts. A paired spin-1/2 singlet gives $V_{RS}=0.304653190236$ and $V_{AL}=0.152326595118$ in repository normalization despite $\langle q_{012}\rangle=0$; independent tensor-product matrices agree. The EPJC Eq. (38) FL regular-tetrahedron example now matches across Python, Rust, and the saved local-spin calculation after this cutoff. T1b also shows nonzero positive RS/AL expectations on tested real planes inside and outside the positive cell. At $J=2$, both sampled minima in 440 equal-face-area samples remain at the regular tetrahedron; this is not a global-minimum proof, and exact degenerate limits were excluded. The latest shape-preview presentation is deployed at website commit `9c6670c`; refreshed numerical data are tracked separately. Next: study degenerate limits and volume spread across $J$, extend shape sampling to unequal assignments, select physical prefactors, and handle larger blocks.

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
- 2026-10-03: Renamed the T5 overview to volume-positivity numerical studies, added shared volume preliminaries and a detailed T5c specification, and linked related implementation notes and the shape-scan run log. T5c remains open; the pilot does not recover the bent input shape.
- 2026-10-03: Completed the T1b real-plane positive-volume check, stabilized Python/Rust spectral zero modes, refreshed the FL area and shape numerics, and ran the Rust FL example successfully with the installed toolchain. See `sessions/2026-10-03-morning.md`.
- 2026-10-03: Recorded the $J=2$ equal-face FL shape scan, its finite-grid limitation, the fixed-$J$ label result, exploratory classical-volume comparison, and boundary/assignment follow-ups. The final shape dashboard with representative thumbnails on both RS and AL panels is live. See `sessions/2026-10-03-night.md` and `fl_volume_shape_scan_log.md`.
- 2026-10-03: Added reusable T5c input/covariance previews and refreshed the T1a shape SVG; website commit `9c6670c` deployed successfully. T5c remains open. See `sessions/2026-10-03-night.md` and the T5c specification.
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

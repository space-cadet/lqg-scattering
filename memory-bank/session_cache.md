# Session Cache

*Last Updated: 2026-10-05 15:00:41 IST*

## Overview
- Active Tasks: T5c FL classical/quantum volume comparison; T1a positive-volume numerics; T3c Rust volume implementation; T4 manuscript; T5 program; T7 thermal/TFD; T8 amplituhedron
- Paused Tasks: 0
- Documentation commit `33e332f` is pushed to `origin/main`; the new T5c scripts, results, Memory Bank follow-up, and weighted input-volume plots/data remain local changes after it. The new plot/data extension is not deployed. Separately, dashboard math typesetting was deployed from website commit `15f698f` (workflow `37286586717`) and checked live; the earlier plot-artwork update is `9c6670c`. Two pre-existing untracked Python cache directories remain under `__pycache__/` and `dashboard/__pycache__/`.

## Task Registry
- T1a: FL positive RS/AL area and shape numerics — 🔄 IN PROGRESS; the 440-point $J=2$ scan and $J=1\ldots5$ area sweep were refreshed with a shared numerical zero-mode cutoff; boundary and unequal-area behavior remain open.
- T1b: Real-plane positive-volume follow-up — ✅ COMPLETE for two tested $N=4$, $K=6$ states; both RS and AL expectations are nonzero and independently checked.
- T3c: Rust positive-volume implementation — 🔄 IN PROGRESS; FL example matches Python using the direct Rust 1.92 toolchain; physical prefactors and blocks above 512 remain open.
- T4: Follow-up manuscript — 🔄 IN PROGRESS; correct claims, document review status, then circulate.
- T5: Volume–positivity numerical studies — 🔄 IN PROGRESS; T5a magnetization sweep converged for one plane; T5c/T5d/T5g open. Former T5f positive-cell/scattering-region mapping is now T8b. T5c owns the positive-volume comparison against the input FL tetrahedron; first weighted pilots and variance records now exist, while broad area/shape coverage and limit orders remain open. Its equal-area normalized covariance relation follows the known FL formula and is a consistency check.
- T5c pilot update: weighted regular and unequal-skew input geometries reach $J=7$; the unequal-area grid covers $J=2,4$ plus selected $J=6$ points; a flat path covers $J=2,4,6,7$. Weighted closure and mean areas pass, but finite-$J$ unequal correlations do not exactly recover the input normals. At the exact flat boundary, calibrated positive volume remains finite in the sampled range; limit orders remain open. RS/AL calibrated curves coincide under the tested four-valent closure/sign convention and are not independent checks.
- T7: Thermal/TFD experiments — 🔄 IN PROGRESS; T7a–T7e recorded complete for tested setups; general temperature-dependent coherent-sector response remains open. The thermal-intertwiners draft is copied to `paper/thermal-intertwiners/`; its proposed thermal ket is not implemented.
- T8: Amplituhedron Program — 🔄 IN PROGRESS; T8a cluster algebra/chart relevance and T8b positive-cell/scattering-region mapping (former T5f) are open. See `tasks/T8.md`.
- T1–T3e: Python/Rust implementation and corrected converged scan recorded; n=6 independent state check remains open.

## Current Work

### T4: Follow-up Manuscript
**Status:** 🔄 IN PROGRESS

`manuscript.md` contains results through T7e and now distinguishes the signed-mean proxy from positive quantum volume. An independent audit found shared Taylor truncation and a real off-cell zero counterexample. Claim-level sign-off and circulation remain open. The published EPJC paper remains frozen.

### Positive volume operators
**Status:** 🔄 IN PROGRESS

Python and Rust implement RS and AL positive expectations by dense spectral decomposition of populated fixed-spin blocks (maximum dimension 512), with eigenvalues within $64\epsilon_{\rm mach}\max(1,\rho(|Q|))$ set to zero to remove numerical exact-kernel artifacts. A paired spin-1/2 singlet gives $V_{RS}=0.304653190236$ and $V_{AL}=0.152326595118$ in repository normalization despite $\langle q_{012}\rangle=0$; independent tensor-product matrices agree. The EPJC Eq. (38) FL regular-tetrahedron example now matches across Python, Rust, and the saved local-spin calculation after this cutoff. T1b also shows nonzero positive RS/AL expectations on tested real planes inside and outside the positive cell. At $J=2$, both sampled minima in 440 equal-face-area samples remain at the regular tetrahedron; this is not a global-minimum proof. The new T5c scan adds weighted input geometries and an exact flat-boundary finite-$J$ scan; neither iterated limit is established. For gauge-invariant four-valent inputs, calibrated RS/AL agreement follows from closure and is not independent evidence. The latest shape-preview presentation is deployed at website commit `9c6670c`; numerical scripts/results are local after documentation commit `33e332f`. Next: broaden unequal shape and $J$ coverage, study both limit orders, select physical prefactors, and handle larger blocks.

### T5: Volume–Positivity Program
**Status:** 🔄 IN PROGRESS

- T5a base triple correlations at n=6,7 are recorded; n=8 remains unresolved.
- T5a magnetization sweep was rerun with convergence assertions (39–41 terms); four sectors matched independent SciPy exponentiation to at most 3.6e-16 in triple means. The result remains one-plane evidence.
- T5a′ local kinematic-polyhedron test is recorded, with limited n=5 sample count and its own engine/convergence caveats.
- T5b has a corrected converged 13-point rerun at n=4,5; four n=4 and three n=5 points agree with independent SciPy exponentiation. The near-half proxy exponent is supported for this family. T5e has converged results for its tested range.
- T5c quantum/classical volume comparison, T5d distance/cocycle scaling, and T5g higher-n profiling remain open. Positive-cell/scattering-region mapping is tracked under T8b.

### T8: Amplituhedron Program
**Status:** 🔄 IN PROGRESS

- T8a: Cluster algebra and coordinate-chart relevance; exploratory, with no new physical interpretation asserted.
- T8b: Positive-cell/scattering-region mapping, transferred from T5f; open and to be scoped against the published T2 baseline.

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
- 2026-10-04: Created T8 for the Amplituhedron Program; T8a tracks the cluster-algebra/chart question and former T5f is subsumed as T8b. T6 remains assigned to Minkowski polyhedron reconstruction.
- 2026-10-05: Clarified T5c as the direct FL classical/positive-quantum volume comparison, recorded weighted unequal-area inputs and degenerate-limit criteria, and saved the initial physics transcript through the task-ownership review. See `sessions/2026-10-05-morning.md` and `sessions/2026-10-05-morning-transcript.md`.
- 2026-10-05: Ran the first weighted input-geometry T5c scans and audited vector means, volume normalization, and the four-valent RS/AL relation. The FL single-face vector means vanish by gauge invariance; shape comparison uses flux correlations. The nine-shape area grid, J=7 starter scans, and exact flat-boundary values are exploratory and do not establish either iterated limit. See the updated T5c specification and morning session note.
- 2026-10-05: Appended the follow-on physics discussion through the weighted-volume audit to the transcript. Dashboard MathJax changes were live-verified after deployment at website commit `15f698f`; the weighted input-volume plot/data extension remains local and undeployed. Mobile layout was not examined, per user direction. See `sessions/2026-10-05-morning-transcript.md` and `sessions/2026-10-05-morning.md`.
- 2026-10-04: Recorded the cluster algebra dialogue and updated the attached discussion note with the fixed-marked-surface flip correspondence, its Pachner-move scope, and the exploratory connection to the project's $\operatorname{Gr}(2,N)$ Plücker charts. No cluster-algebra task or implementation was started. See `sessions/2026-10-04-cluster-algebras-transcript.md` and the attached `cluster-algebras-discussion.md`.
- 2026-10-04: Copied the thermal-intertwiners paper sources/assets and recorded the physical dialogue plus the visible chat through the tetrahedron construction. The F-pair sewing exploration remains conceptual and has no assigned task ID. See `implementation-details/constructive-geometric-sewing-dialogue.md` and `sessions/2026-10-04-geometric-construction-transcript.md`.
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

# Active Context

*Last Updated: 2026-10-08 23:21:44 IST*

## Current Focus
Session-close handoff: [sessions/2026-10-08-physics-handoff.md](sessions/2026-10-08-physics-handoff.md); exact [physics-only transcript](sessions/2026-10-08-physics-transcript.md). Latest discussion distinguishes area $J$, resultant spin $S$, and magnetic number $M$, derives a nonzero-spin reference-state extension, and clarifies group action versus averaging. The extension remains unimplemented and numerically unchecked.

**Primary Task:** T9 — analyze the selected two-copy squeezed FL state. The coefficient framework and exact $J=0$ vacuum case are documented. The four-face $J_{\mathrm{in}}=1$ marginal $P(q,S)$ has been calculated by two methods and plotted; full two-copy reduced-state blocks and geometric observables are next.
**Supporting Tasks:** T1a Python volume numerics; T3c Rust volume implementation; T6 kinematic Minkowski geometry; T4 manuscript audit; T8 amplituhedron program.

## Active Tasks
- T4: Manuscript claim audit and review preparation — IN PROGRESS; independent audit recorded.
- T1a: The regular FL tetrahedron sweep covers $J=1\ldots5$. At $J=2$, both RS and AL have their minima at the regular tetrahedron among 440 ordered equal-face-area samples; this is not a global-minimum proof. Initial weighted-area input-volume pilots cover one unequal geometry through $J=7$, a nine-shape grid at $J=2,4$, and selected $J=6$ points. Broader unequal-area coverage and degenerate limits remain open.
- T3c: The Rust FL Eq. (38) example now builds and matches the Python $J=2$ result after the shared zero-mode cutoff. Physical prefactors and a method for blocks above 512 remain open; the Cargo shim itself is still broken.
- T5: Volume–positivity numerical-studies program — IN PROGRESS; T5c/T5d/T5g open; the former T5f amplituhedron mapping is now T8b. Initial T5c pilots compare the input classical tetrahedron with weighted FL positive volume: regular/unequal-skew through $J=7$, a nine-shape unequal-area grid at $J=2,4$, selected $J=6$ points, and a flat path through $J=7$. Area means and weighted closure pass; finite-$J$ unequal correlations do not exactly reproduce input angles. Calibrated RS/AL agreement follows from closure and is not independent evidence. Broader shape and iterated-limit conclusions remain open. See `implementation-details/T5c-flux-covariance-volume-comparison.md` and shared `implementation-details/volume-numerical-preliminaries.md`.
- T8: Amplituhedron Program — IN PROGRESS; T8a cluster algebra/chart relevance and T8b positive-cell/scattering-region mapping (transferred from T5f) are open. See `tasks/T8.md`.
- T9: Thermal/TFD state construction and physical study — IN PROGRESS; owns all ongoing TFD construction and analysis, with exactly five completed child-study records T7a–T7e. The four-face $J_{\mathrm{in}}=1$ $P(q,S)$ calculation and method comparison are complete through $q=160$ at five temperatures; full reduced-state blocks, entropy, and geometry remain open.

## Project State
- Published EPJC paper is the frozen baseline.
- All source code, including LaTeX manuscript sources and build assets, is grouped under `code/`; compiled PDFs remain under `paper/`.
- The project root retains the README and living manuscript. Calculation JSON files are organized under `results/`; experiment records, task specifications, and the published-paper overview are under `notes/`. Dashboard files now sit directly in `code/dashboard/`.
- The task inventory has dedicated records for all 29 current registry IDs plus the transferred historical T5f and T7 records. Completed tasks are archived; active tasks remain under `tasks/`. Statuses and task relationships were reconciled against the current Memory Bank and full Git history.
- T1b's positive-volume follow-up is complete for two $N=4$, $K=6$ real-plane states inside and outside the positive cell; both RS and AL expectations are nonzero and independently cross-checked.
- Python and Rust implementations exist. The old n=4 comparison shared a truncated Taylor state. Corrected Rust scans now cover n=4..8; SciPy independently checks n=4,5,7,8.
- `manuscript.md` contains results through T7e but needs corrected conclusions, caveats, independent review, and circulation.
- At the start of the 2026-10-06 task-record audit, `main` and `origin/main` both pointed to `0a254849a5e12734ee32d9d8af74bd4309d17648`. Existing local numerical, dashboard, and Memory Bank work remains in the working tree; this audit preserved it while reconstructing task records from the full 79-commit history. Separately, the dashboard's math typesetting update was deployed from website commit `15f698f` (workflow `37286586717`) and verified live in the study and fixed-area sections. Chart SVG labels remain compact text; mobile view was not examined, per the user's direction. The earlier plot-artwork update is website commit `9c6670c`. Two pre-existing untracked Python cache directories remain under `__pycache__/` and `code/dashboard/__pycache__/`.
- T7 was archived as the former umbrella; T9 now owns all thermal/TFD work. The selected target is $U_\beta(|J,z\rangle_L\otimes|\overline{J,z}\rangle_R)$ with transformed geometric observables. The $SU(1,1)$ factorization and coefficient-level partial-trace construction are documented. The four-face $J_{\mathrm{in}}=1$ $P(q,S)$ marginal has two agreeing implementations through $q=160$ and temperature plots; allowed sectors have positive finite-temperature weight, so plotted cutoffs reflect display/numerical limits. Full two-copy reduced-state blocks, entropy, and geometric correlations remain to be calculated. See `tasks/T9.md`, `notes/thermal-area-sectors.md`, and the October 8 session records.
- The constructive F-pair sewing discussion is recorded in [the dialogue note](implementation-details/constructive-geometric-sewing-dialogue.md) and [the session transcript](sessions/2026-10-04-geometric-construction-transcript.md). Triangle and tetrahedron sewing remain conceptual; metric shape and volume have not been validated, and no task ID was assigned.

## Current Decisions
- The corrected T5a magnetization sweep converged in 39–41 terms and four sectors matched SciPy exponentiation. Retain its one-plane scope.
- Keep T5a′ local-triple findings separate from the corrected magnetization sweep and retain their limited sample-size caveats.
- T5e does not establish the expected classical $K^{3/2}$ volume growth through $K=24$; do not summarize it as a checked classical limit.
- Gibbs TFD tends to the Fock vacuum, not a Perelomov state. The T7e result is limited to the tested fixed-$K$ construction and does not establish a general $V(\epsilon,T)$ law.
- Distinguish the signed-mean proxy from positive volume expectations. RS sums positive triple roots; AL takes the positive root after an embedding-signed triple sum. Both are now implemented in project normalization for active blocks up to dimension 512.
- Set eigenvalues within $64\epsilon_{\rm mach}\max(1,\rho(|Q|))$ to zero in both Python and Rust positive-volume routines; this prevents solver-dependent positive contributions from exact kernel modes.
- Do not mark numerical claims red-team reviewed without a documented protocol and per-claim evidence.
- Under T9, study the user's selected two-copy squeezed FL state with transformed observables. Keep full doubled-space observables distinct from left-reduced-state expectations. A fixed positive total-area Hamiltonian on unrestricted Fock space cannot generate this family at all temperatures: the Gibbs limit is vacuum while the squeezed family returns its nonzero-$J$ input state.

## Next Actions
1. Expand the weighted FL shape grid beyond the first area partition and track the face-normal and vertex-sphere cross-ratios alongside Euclidean metric data; treat normals as input labels and correlations as the quantum shape diagnostic.
2. Extend selected shape and unequal-area volume comparisons to larger $J$; quantify convergence and the remaining shape dependence under the fixed geometric factors.
3. Extend the flat-boundary path far enough in $J$ and smaller $\varphi$ to assess each iterated limit; keep absolute discrepancies near zero classical volume.
4. Fix and document the graph embedding and AL signs, keep project units separate from physical prefactors, and address active blocks above dimension 512 when required.
5. Extend the corrected T5a and T5b results across plane controls
  and run T5d with real off-cell controls.
6. Complete T5c/T6 polyhedron reconstruction and controlled comparisons.
7. Under T9, extend the validated $J_{\mathrm{in}}=1$ calculation to the selected two-copy state, combining coherent contributions within each final occupation sector.
8. Form the sector matrices $C_qC_q^\dagger$ and evaluate their spectrum and entropy with explicit convergence controls.
9. Calculate two-sided and transformed geometric observables; compare with only explicitly specified ensemble Hamiltonians.
10. Review corrected numerical artifacts before circulating the manuscript.

## Latest volume session

Completed the single-copy four-face closed-basis catalogue and positive RS/AL data through $K=12$ (10,549 states), with matrices, figures and independent checks. The extension stopped at the user request; no $K=13$ result is accepted. New notation: $K$ total linear area, $J$ resultant angular momentum. [T10](tasks/T10.md) is deferred to a later session for all active face counts at fixed $K$; implementation not started. T9 thermal reduced-state/geometry work remains open. See [summary](sessions/2026-10-08-volume-studies.md) and [physics transcript](sessions/2026-10-08-volume-physics-transcript.md).

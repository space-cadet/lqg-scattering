# Active Context

*Last Updated: 2026-10-06 12:55:19 IST*

## Current Focus
**Primary Task:** T9 — construct thermal/TFD state families and study their physical geometry. The four-face pilot compares the draft squeeze and singlet-projected candidate; physical state/observable selection remains open.
**Supporting Tasks:** T1a Python volume numerics; T3c Rust volume implementation; T6 kinematic Minkowski geometry; T4 manuscript audit; T8 amplituhedron program.

## Active Tasks
- T4: Manuscript claim audit and review preparation — IN PROGRESS; independent audit recorded.
- T1a: The regular FL tetrahedron sweep covers $J=1\ldots5$. At $J=2$, both RS and AL have their minima at the regular tetrahedron among 440 ordered equal-face-area samples; this is not a global-minimum proof. Initial weighted-area input-volume pilots cover one unequal geometry through $J=7$, a nine-shape grid at $J=2,4$, and selected $J=6$ points. Broader unequal-area coverage and degenerate limits remain open.
- T3c: The Rust FL Eq. (38) example now builds and matches the Python $J=2$ result after the shared zero-mode cutoff. Physical prefactors and a method for blocks above 512 remain open; the Cargo shim itself is still broken.
- T5: Volume–positivity numerical-studies program — IN PROGRESS; T5c/T5d/T5g open; the former T5f amplituhedron mapping is now T8b. Initial T5c pilots compare the input classical tetrahedron with weighted FL positive volume: regular/unequal-skew through $J=7$, a nine-shape unequal-area grid at $J=2,4$, selected $J=6$ points, and a flat path through $J=7$. Area means and weighted closure pass; finite-$J$ unequal correlations do not exactly reproduce input angles. Calibrated RS/AL agreement follows from closure and is not independent evidence. Broader shape and iterated-limit conclusions remain open. See `implementation-details/T5c-flux-covariance-volume-comparison.md` and shared `implementation-details/volume-numerical-preliminaries.md`.
- T8: Amplituhedron Program — IN PROGRESS; T8a cluster algebra/chart relevance and T8b positive-cell/scattering-region mapping (transferred from T5f) are open. See `tasks/T8.md`.
- T9: Thermal/TFD state construction and physical study — IN PROGRESS; owns all ongoing TFD construction and analysis, with exactly five completed child-study records T7a–T7e.

## Project State
- Published EPJC paper is the frozen baseline.
- The task inventory has dedicated records for all 29 current registry IDs plus the transferred historical T5f and T7 records. Completed tasks are archived; active tasks remain under `tasks/`. Statuses and task relationships were reconciled against the current Memory Bank and full Git history.
- T1b's positive-volume follow-up is complete for two $N=4$, $K=6$ real-plane states inside and outside the positive cell; both RS and AL expectations are nonzero and independently cross-checked.
- Python and Rust implementations exist. The old n=4 comparison shared a truncated Taylor state. Corrected Rust scans now cover n=4..8; SciPy independently checks n=4,5,7,8.
- `manuscript.md` contains results through T7e but needs corrected conclusions, caveats, independent review, and circulation.
- At the start of the 2026-10-06 task-record audit, `main` and `origin/main` both pointed to `0a254849a5e12734ee32d9d8af74bd4309d17648`. Existing local numerical, dashboard, and Memory Bank work remains in the working tree; this audit preserved it while reconstructing task records from the full 79-commit history. Separately, the dashboard's math typesetting update was deployed from website commit `15f698f` (workflow `37286586717`) and verified live in the study and fixed-area sections. Chart SVG labels remain compact text; mobile view was not examined, per the user's direction. The earlier plot-artwork update is website commit `9c6670c`. Two pre-existing untracked Python cache directories remain under `__pycache__/` and `dashboard/__pycache__/`.
- T7 was archived as the former umbrella; T9 now owns all thermal/TFD work. The draft thermal ket has an exact small-sector implementation. Combined dual closure passes, ordinary per-copy closure fails, and separately labelled singlet postselection restores closure. Physical ensemble/observable selection remains open. See `tasks/T9.md` and `implementation-details/T7-mathematical-background-and-calculations.md`.
- The constructive F-pair sewing discussion is recorded in [the dialogue note](implementation-details/constructive-geometric-sewing-dialogue.md) and [the session transcript](sessions/2026-10-04-geometric-construction-transcript.md). Triangle and tetrahedron sewing remain conceptual; metric shape and volume have not been validated, and no task ID was assigned.

## Current Decisions
- The corrected T5a magnetization sweep converged in 39–41 terms and four sectors matched SciPy exponentiation. Retain its one-plane scope.
- Keep T5a′ local-triple findings separate from the corrected magnetization sweep and retain their limited sample-size caveats.
- T5e does not establish the expected classical $K^{3/2}$ volume growth through $K=24$; do not summarize it as a checked classical limit.
- Gibbs TFD tends to the Fock vacuum, not a Perelomov state. The T7e result is limited to the tested fixed-$K$ construction and does not establish a general $V(\epsilon,T)$ law.
- Distinguish the signed-mean proxy from positive volume expectations. RS sums positive triple roots; AL takes the positive root after an embedding-signed triple sum. Both are now implemented in project normalization for active blocks up to dimension 512.
- Set eigenvalues within $64\epsilon_{\rm mach}\max(1,\rho(|Q|))$ to zero in both Python and Rust positive-volume routines; this prevents solver-dependent positive contributions from exact kernel modes.
- Do not mark numerical claims red-team reviewed without a documented protocol and per-claim evidence.

## Next Actions
1. Expand the weighted FL shape grid beyond the first area partition and track the face-normal and vertex-sphere cross-ratios alongside Euclidean metric data; treat normals as input labels and correlations as the quantum shape diagnostic.
2. Extend selected shape and unequal-area volume comparisons to larger $J$; quantify convergence and the remaining shape dependence under the fixed geometric factors.
3. Extend the flat-boundary path far enough in $J$ and smaller $\varphi$ to assess each iterated limit; keep absolute discrepancies near zero classical volume.
4. Fix and document the graph embedding and AL signs, keep project units separate from physical prefactors, and address active blocks above dimension 512 when required.
5. Extend the corrected T5a and T5b results across plane controls
  and run T5d with real off-cell controls.
6. Complete T5c/T6 polyhedron reconstruction and controlled comparisons.
7. Under T9, select and specify the physical thermal map, support, area ensemble and right-copy convention.
8. Under T9, extend geometric and two-sided observable comparisons for the selected state families, with cutoff evidence.
8. Review corrected numerical artifacts before circulating the manuscript.

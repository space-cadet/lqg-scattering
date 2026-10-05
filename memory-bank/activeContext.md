# Active Context

*Last Updated: 2026-10-05 10:49:54 IST*

## Current Focus
**Primary Task:** T5c — compare positive RS/AL expectations from FL tetrahedron states with the classical volume of the same input geometry, including weighted areas and degenerate limits.
**Supporting Tasks:** T1a Python volume numerics; T3c Rust volume implementation; T6 kinematic Minkowski geometry; T4 manuscript audit; T7 thermal/TFD work; T8 amplituhedron program.

## Active Tasks
- T4: Manuscript claim audit and review preparation — IN PROGRESS; independent audit recorded.
- T1a: The regular FL tetrahedron sweep covers $J=1\ldots5$. At $J=2$, both RS and AL have their minima at the regular tetrahedron among 440 ordered equal-face-area samples; this is not a global-minimum proof. The current spinor helper uses unit spinors. Weighted spinors can extend the existing FL family to unequal area ratios; those positive-volume calculations and exact boundary behavior remain open.
- T3c: The Rust FL Eq. (38) example now builds and matches the Python $J=2$ result after the shared zero-mode cutoff. Physical prefactors and a method for blocks above 512 remain open; the Cargo shim itself is still broken.
- T5: Volume–positivity numerical-studies program — IN PROGRESS; T5c/T5d/T5g open; the former T5f amplituhedron mapping is now T8b. T5c owns the direct classical/quantum tetrahedron-volume comparison. Existing volume spectra cover five interior equal-area shapes at $J=1,2,3$; covariance results cover 14 equal-area shapes through $J=6$. Weighted areas, fixed cross-shape normalization, positive-volume boundary limits, and volume variance remain open. See `implementation-details/T5c-flux-covariance-volume-comparison.md` and shared `implementation-details/volume-numerical-preliminaries.md`.
- T7: Thermal/TFD program — reported T7a–T7e runs complete for their tested setups; broader coherent-sector thermal question remains open.
- T8: Amplituhedron Program — IN PROGRESS; T8a cluster algebra/chart relevance and T8b positive-cell/scattering-region mapping (transferred from T5f) are open. See `tasks/T8.md`.

## Project State
- Published EPJC paper is the frozen baseline.
- T1b's positive-volume follow-up is complete for two $N=4$, $K=6$ real-plane states inside and outside the positive cell; both RS and AL expectations are nonzero and independently cross-checked.
- Python and Rust implementations exist. The old n=4 comparison shared a truncated Taylor state. Corrected Rust scans now cover n=4..8; SciPy independently checks n=4,5,7,8.
- `manuscript.md` contains results through T7e but needs corrected conclusions, caveats, independent review, and circulation.
- At the 2026-10-05 scan baseline, the checkout was on `main` at `5a597ed`; two pre-existing untracked Python cache directories remain under `__pycache__/` and `dashboard/__pycache__/`. The latest visual dashboard update is separately deployed at `9c6670c`.
- The thermal-intertwiners paper source and assets are copied into `paper/thermal-intertwiners/`; this does not implement or validate its proposed thermal ket.
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
1. Construct weighted FL spinors from closed unequal-area tetrahedron data and verify the area fractions and closure before evaluating positive volumes.
2. Compare RS/AL expectations divided by $J^{3/2}$ with the classical volume of the input tetrahedron, using one fixed normalization per operator and recording variance where feasible.
3. Study controlled degenerate paths and both limit orders; keep absolute discrepancies near zero classical volume.
4. Fix the graph embedding and AL signs, state project units separately from physical prefactors, and address active blocks above dimension 512 when required.
5. Extend the corrected T5a and T5b results across plane controls
  and run T5d with real off-cell controls.
6. Complete T5c/T6 polyhedron reconstruction and controlled comparisons.
7. Resolve the TFD right-operator convention before extending T7.
8. Review corrected numerical artifacts before circulating the manuscript.

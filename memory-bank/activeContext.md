# Active Context

*Last Updated: 2026-10-04 19:51:53 IST*

## Current Focus
**Primary Task:** T1a — extend the positive FL volume numerics from the regular-tetrahedron area sweep to shape and boundary behavior.
**Secondary Tasks:** T3c Rust reproduction; T4 manuscript audit; T5 volume experiments; T7 thermal/TFD work; T8 amplituhedron program.

## Active Tasks
- T4: Manuscript claim audit and review preparation — IN PROGRESS; independent audit recorded.
- T1a: The regular FL tetrahedron sweep covers $J=1\ldots5$. At $J=2$, both RS and AL have their minima at the regular tetrahedron among 440 ordered equal-face-area samples; this is not a global-minimum proof. The latest shape-figure presentation is live at website commit `9c6670c` (workflow `37125090987`) and reuses saved tetrahedron thumbnails. Physical prefactors, exact boundary behavior, unequal-area shapes, and a general proof remain open.
- T3c: The Rust FL Eq. (38) example now builds and matches the Python $J=2$ result after the shared zero-mode cutoff. Physical prefactors and a method for blocks above 512 remain open; the Cargo shim itself is still broken.
- T5: Volume–positivity numerical-studies program — IN PROGRESS; T5c/T5d/T5g open; the former T5f amplituhedron mapping is now T8b. T5a magnetization sweep converged and independently checked for four sectors of one plane. T5c's selected-shape covariance scan covers 14 shapes at $J=1\ldots6$; the dashboard's precomputed shape previews are deployed, while the state-to-geometry interpretation and remaining comparisons are open. See `implementation-details/T5c-flux-covariance-volume-comparison.md` and shared `implementation-details/volume-numerical-preliminaries.md`.
- T7: Thermal/TFD program — reported T7a–T7e runs complete for their tested setups; broader coherent-sector thermal question remains open.
- T8: Amplituhedron Program — IN PROGRESS; T8a cluster algebra/chart relevance and T8b positive-cell/scattering-region mapping (transferred from T5f) are open. See `tasks/T8.md`.

## Project State
- Published EPJC paper is the frozen baseline.
- T1b's positive-volume follow-up is complete for two $N=4$, $K=6$ real-plane states inside and outside the positive cell; both RS and AL expectations are nonzero and independently cross-checked.
- Python and Rust implementations exist. The old n=4 comparison shared a truncated Taylor state. Corrected Rust scans now cover n=4..8; SciPy independently checks n=4,5,7,8.
- `manuscript.md` contains results through T7e but needs corrected conclusions, caveats, independent review, and circulation.
- At this session's scan baseline, the checkout was on `main` at `c64de52` with no tracked modifications; pre-existing untracked content was under `__pycache__/`, `dashboard/__pycache__/`, and `figures/`. The latest visual dashboard update is separately deployed at `9c6670c`.
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
1. Probe the equal-area family near $x=0$, $x=1$, and $\varphi=180^\circ$ as limits, then compare classical volume, RS/AL expectations, and volume spread across increasing $J$.
2. Extend positive spin-label enumeration to larger fixed $J$, then parameterize or sample the continuous closed shapes for each allowed unequal face-area assignment. Check the qhe-bhe Thurston/Minkowski work for useful geometric constraints without treating it as a proof for the quantum operators.
3. Select physical prefactors and AL embeddings for the intended convention, and replace dense diagonalization before evaluating active blocks above dimension 512. The Rust FL Eq. (38) example now runs through the installed Rust 1.92 toolchain.
4. Extend the corrected T5a and T5b results across plane controls
  and run T5d with real off-cell controls.
5. Complete T5c/T6 polyhedron reconstruction and controlled comparisons.
6. Resolve the TFD right-operator convention before extending T7.
7. Review corrected numerical artifacts before circulating the manuscript.

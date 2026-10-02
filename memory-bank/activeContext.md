# Active Context

*Last Updated: 2026-10-03 00:27:43 IST*

## Current Focus
**Primary Task:** T1a — extend the positive FL volume numerics from the regular-tetrahedron area sweep to shape and boundary behavior.
**Secondary Tasks:** T3c Rust reproduction; T4 manuscript audit; T5 volume experiments; T7 thermal/TFD work.

## Active Tasks
- T4: Manuscript claim audit and review preparation — IN PROGRESS; independent audit recorded.
- T1a: The regular FL tetrahedron sweep covers $J=1\ldots5$. At $J=2$, both RS and AL have their minima at the regular tetrahedron among 440 ordered equal-face-area samples; this is not a global-minimum proof. The shape dashboard, including thumbnails on both panels, is live from website commit `f0b6fdd` (workflow `37033479554`). Physical prefactors, exact boundary behavior, unequal-area shapes, and a general proof remain open.
- T3c: Rust FL example source exists but has not been compiled or run because the local Cargo symlink points to a missing `rustup-init`.
- T5: Volume–positivity research program — IN PROGRESS; T5c/T5d/T5f/T5g open; T5a magnetization sweep converged and independently checked for four sectors of one plane.
- T7: Thermal/TFD program — reported T7a–T7e runs complete for their tested setups; broader coherent-sector thermal question remains open.

## Project State
- Published EPJC paper is the frozen baseline.
- Python and Rust implementations exist. The old n=4 comparison shared a truncated Taylor state. Corrected Rust scans now cover n=4..8; SciPy independently checks n=4,5,7,8.
- `manuscript.md` contains results through T7e but needs corrected conclusions, caveats, independent review, and circulation.
- The checkout is on `main` at `9b7f588`; the current working tree contains uncommitted FL shape-scan source/data/figures and dashboard edits. The website copy is separately deployed at `f0b6fdd`. A clean-checkout reproduction of the shape scan is not recorded.

## Current Decisions
- The corrected T5a magnetization sweep converged in 39–41 terms and four sectors matched SciPy exponentiation. Retain its one-plane scope.
- Keep T5a′ local-triple findings separate from the corrected magnetization sweep and retain their limited sample-size caveats.
- T5e does not establish the expected classical $K^{3/2}$ volume growth through $K=24$; do not summarize it as a checked classical limit.
- Gibbs TFD tends to the Fock vacuum, not a Perelomov state. The T7e result is limited to the tested fixed-$K$ construction and does not establish a general $V(\epsilon,T)$ law.
- Distinguish the signed-mean proxy from positive volume expectations. RS sums positive triple roots; AL takes the positive root after an embedding-signed triple sum. Both are now implemented in project normalization for active blocks up to dimension 512.
- Do not mark numerical claims red-team reviewed without a documented protocol and per-claim evidence.

## Next Actions
1. Probe the equal-area family near $x=0$, $x=1$, and $\varphi=180^\circ$ as limits, then compare classical volume, RS/AL expectations, and volume spread across increasing $J$.
2. Extend positive spin-label enumeration to larger fixed $J$, then parameterize or sample the continuous closed shapes for each allowed unequal face-area assignment. Check the qhe-bhe Thurston/Minkowski work for useful geometric constraints without treating it as a proof for the quantum operators.
3. Run the Rust FL Eq. (38) example after restoring a working Cargo toolchain; select physical prefactors and AL embeddings, and replace dense diagonalization before large blocks.
4. Extend the corrected T5a and T5b results across plane controls
  and run T5d with real off-cell controls.
5. Complete T5c/T6 polyhedron reconstruction and controlled comparisons.
6. Resolve the TFD right-operator convention before extending T7.
7. Review corrected numerical artifacts before circulating the manuscript.

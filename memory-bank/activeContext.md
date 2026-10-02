# Active Context

*Last Updated: 2026-10-02 13:49:49 IST*

## Current Focus
**Primary Task:** T4 — bring the follow-up manuscript and its claims into agreement with the experiment records.
**Secondary Tasks:** T5 red-team repair; T7 scope and status reconciliation.

## Active Tasks
- T4: Manuscript claim audit and review preparation — IN PROGRESS; independent audit recorded.
- T1a: Preliminary Python evaluation of the EPJC Eq. (38) FL fixed-area state on a regular tetrahedron is positive under RS and AL; the direct tensor-product cross-check differs by about $1.8\times10^{-10}$. T3c Rust validation, discrepancy resolution, physical prefactors, and large-block methods remain open.
- T5: Volume–positivity research program — IN PROGRESS; T5c/T5d/T5f/T5g open; T5a magnetization sweep converged and independently checked for four sectors of one plane.
- T7: Thermal/TFD program — reported T7a–T7e runs complete for their tested setups; broader coherent-sector thermal question remains open.

## Project State
- Published EPJC paper is the frozen baseline.
- Python and Rust implementations exist. The old n=4 comparison shared a truncated Taylor state. Corrected Rust scans now cover n=4..8; SciPy independently checks n=4,5,7,8.
- `manuscript.md` contains results through T7e but needs corrected conclusions, caveats, independent review, and circulation.
- The cloud checkout was synchronized with `origin/main`; this local follow-up records the preliminary Python FL volume calculation in Memory Bank only. No research source code was changed.

## Current Decisions
- The corrected T5a magnetization sweep converged in 39–41 terms and four sectors matched SciPy exponentiation. Retain its one-plane scope.
- Keep T5a′ local-triple findings separate from the corrected magnetization sweep and retain their limited sample-size caveats.
- T5e does not establish the expected classical $K^{3/2}$ volume growth through $K=24$; do not summarize it as a checked classical limit.
- Gibbs TFD tends to the Fock vacuum, not a Perelomov state. The T7e result is limited to the tested fixed-$K$ construction and does not establish a general $V(\epsilon,T)$ law.
- Distinguish the signed-mean proxy from positive volume expectations. RS sums positive triple roots; AL takes the positive root after an embedding-signed triple sum. Both are now implemented in project normalization for active blocks up to dimension 512.
- Do not mark numerical claims red-team reviewed without a documented protocol and per-claim evidence.

## Next Actions
1. Resolve the direct-tensor discrepancy in the preliminary Python EPJC Eq. (38) FL tetrahedron case; validate the FL case in Rust, then select physical prefactors and AL embeddings and replace dense diagonalization before large blocks.
2. Extend the corrected T5a and T5b results across plane controls
   and run T5d with real off-cell controls.
3. Complete T5c/T6 polyhedron reconstruction and controlled comparisons.
4. Resolve the TFD right-operator convention before extending T7.
5. Review corrected numerical artifacts before circulating the manuscript.

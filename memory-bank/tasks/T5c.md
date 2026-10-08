---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T5c
*Created: 2026-09-19*
*Last Updated: 2026-10-06 09:47:11 IST*

## Task Information
**Title:** FL classical/quantum tetrahedron-volume comparison
**Status:** 🔄 IN PROGRESS
**Priority:** HIGH
**Created:** 2026-09-19
**Started:** 2026-10-03
**Completed:** —
**Dependencies:** T5, T3c

## Description
Compare positive RS/AL expectations of weighted Freidel–Livine tetrahedron states with the classical volume of those same input face data, using fixed geometric factors.

## Acceptance Criteria
- [ ] Verify weighted-spinor closure, requested area means, and classical input volume.
- [ ] Expand unequal-area and shape coverage and compare normalized positive volume, discrepancy, and variance where feasible.
- [ ] Study controlled degenerate paths with both limit orders; keep covariance reconstruction as a separate diagnostic.

## Progress Tracking
- 2026-10-03: T5c pilots and selected-shape diagnostics were recorded.
- 2026-10-05: Scope and fixed geometric conversion were clarified; weighted scans cover regular and unequal-skew families through J=7, a nine-shape grid at J=2,4 plus selected J=6, and a flat path at J=2,4,6,7.
- 2026-10-06: Exploratory J=8–10 and Rust J=10 checks were recorded; the Rust J=11 flat attempt was stopped after over four minutes without a result.

## Related Files
- `memory-bank/implementation-details/T5c-flux-covariance-volume-comparison.md`
- `memory-bank/implementation-details/volume-numerical-preliminaries.md`
- `code/python/t5c_input_geometry_scan.py`
- `code/python/t5c_weighted_shape_scan.py`
- `code/python/t5c_degenerate_limits_scan.py`
- `results/t5c_degenerate_limits_highJ_results.json`

## Issues and Blockers
- Neither iterated limit is established. Physical regularization factors and dense-block methods above dimension 512 remain open. At J=10 the Rust calibrated RS cross-check differs from Python by about 4.4e-10; AL agrees.

## Notes
For the tested four-valent closure/sign convention, geometry-matched RS and AL curves coincide by closure and are not independent evidence.

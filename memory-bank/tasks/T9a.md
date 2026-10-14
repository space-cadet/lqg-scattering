# Task: T9a
*Created: 2026-10-14 14:35:25 IST*
*Last Updated: 2026-10-14 16:13:37 IST*

## Task Information
**Title:** Closure-preserving singlet exchange and thermal equilibration
**Status:** 🔄 IN PROGRESS
**Priority:** HIGH
**Created:** 2026-10-14
**Started:** 2026-10-14
**Completed:** —
**Parent:** T9
**Dependencies:** T9, T11, T1a

## Description
Study two separately closed polyhedra exchanging singlet pairs, beginning with pure fixed-area FL preparations and the coupled ground states. Continue to a geometric reservoir, equilibrium, and comparison with the selected squeezed-and-projected T9 family. A prepared pure FL state is not identified with the Hamiltonian's zero-temperature ground state.

## Acceptance Criteria
- [x] Build complete finite combined-area spaces including vacuum endpoints; validate singlet-transfer matrix elements and separate closure.
- [x] Specify regular-tetrahedron spinors, face correspondence, phase convention, and controlled area/shape variations.
- [x] Implement and run the first FL exchange pilot with area current, distributions, face correlations, positive RS volume, entropy, and return probability.
- [x] Calculate coupled ground-space mixtures and fixed-combined-area canonical ensembles; preserve degeneracy and distinguish equilibrium from relaxation.
- [x] Verify analytic one-unit oscillations, direct oscillator transfer, current sign, conservation, and independent propagation.
- [ ] Extend combined-area and shape coverage and study physically relevant phase coherence across area sectors.
- [ ] Specify and implement a geometric reservoir; test relaxation, recurrence, initial-state dependence, and equilibrium comparisons.
- [ ] Compare reduced spectra and geometry with the existing T9 thermal family without assuming their equivalence.

## Implementation Details
See [the study specification](../../notes/t9a-singlet-exchange.md). First pilot: combined area $K=4$, 1,210 states, local dimensions 1, 6, 20, 50, 105; six equal corresponding-pair couplings. Four settings and three preparations give twelve trajectories, each with 101 time points. Repulsion acts on each polyhedron's total area, distinct from T11 face-site repulsion. Exact diagonalization supplies dynamics and degenerate ground-space mixtures; finite-temperature ensembles are within fixed combined area. Reservoir and grand-canonical limits are future stages.

## Related Files
- `code/python/lqg_scattering/singlet_exchange.py`: reusable operators, FL inputs, and readouts.
- `code/python/t9a_singlet_exchange.py`: pilot driver.
- `code/python/test_singlet_exchange.py`: analytic and direct-oscillator tests.
- `code/python/verify_t9a_singlet_exchange.py`: sparse propagation verifier.
- `results/t9a-singlet-exchange/`: saved numerical results and provenance.
- [Session](../sessions/2026-10-14-t9a-singlet-exchange.md).

## Progress Tracking
- 2026-10-14 14:35:25 IST: User explicitly authorized a new T9 child, documentation reconciliation, and implementation, superseding the prior five-child restriction. Implemented the finite-area pilot; internal maximum residual 4.53e-14. Independent verification and regression evidence are recorded in the result report/session.

## Issues and Blockers
No implementation blocker. The finite two-polyhedron pilot does not establish reservoir thermalization, a unique ground-state shape, a thermodynamic phase, or physical energy/volume calibration.

Verification closeout: all 46 Python regression tests passed. Independent sparse propagation and infinite-temperature traces gave 1,792 comparisons with maximum residual $9.06\times10^{-13}$. Vector PDF and 300-dpi PNG overview exported and visually inspected. See [the result report](../../results/t9a-singlet-exchange/README.md).

## Research-note extraction — 2026-10-14

The heating, projected geometry, equilibrium discussion and current exchange results are consolidated in [the new illustrated note](../../notes/thermal-geometry-and-singlet-exchange.md). The remaining thermal area-sector note has a [reorganization assessment](../../notes/thermal-area-sectors-reorganization.md); its main-text/appendix rewrite is now complete, preserving all eight figures and the historical derivations. No scientific implementation changed in this documentation step.

- 2026-10-14 16:13:37 IST: Completed the authorized thermal-area note rewrite: six physical sections, seven appendices, all eight figures and legacy anchors preserved. Documentation validation passed; no scientific code or numerical result changed.

---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T7a
*Created: 2026-09-20*
*Last Updated: 2026-10-06 11:29:29 IST*

## Task Information
**Title:** Single-copy thermal state
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-20
**Started:** 2026-09-20
**Completed:** 2026-09-20
**Dependencies:** T9, T3c
**Current Parent:** T9 (original identifier retained; formerly under T7)

## Description
Compute areas, signed grasp, and grasp fluctuations in the Gibbs state on the n=4,5 capped Fock spaces.

## Acceptance Criteria
- [x] Compute thermal area expectations across the beta sweep.
- [x] Verify $\mathrm{Tr}(\rho_\beta q)=0$.
- [x] Compute nonzero $\mathrm{Tr}(\rho_\beta q^2)$ and report cutoff limits.

## Progress Tracking
- 2026-09-20: Completed in the T7a run; the thermal mean signed grasp vanishes while $q^2$ fluctuations are nonzero.

## Related Files
- `t7a_thermal.py`
- `t7a_results.json`
- `t7a_notes.md`
- `memory-bank/implementation-details/thermofield-double-volume.md`

## Issues and Blockers
- Capped-basis results are quantitative for $\beta\gtrsim1$ and qualitative at $\beta\leq0.5$.

## Notes
The Gibbs state tends to the Fock vacuum at large beta, not to a Perelomov state.

- 2026-10-06 12:55:19 IST: Parent ownership consolidated under T9; completed status, original scope, and task ID retained.

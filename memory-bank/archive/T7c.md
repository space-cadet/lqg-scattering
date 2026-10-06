---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T7c
*Created: 2026-09-20*
*Last Updated: 2026-10-06 11:29:29 IST*

## Task Information
**Title:** Two-sided chirality correlator
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-20
**Started:** 2026-09-20
**Completed:** 2026-09-20
**Dependencies:** T9, T7a, T7b
**Current Parent:** T9 (original identifier retained; formerly under T7)

## Description
Evaluate the Gibbs-TFD correlator $\langle q_Lq_R\rangle$ and compare it with single-copy $q^2$ fluctuations and entropy.

## Acceptance Criteria
- [x] Evaluate the correlator across the tested beta sweep.
- [x] State the right-copy operator convention explicitly.
- [x] Compare the correlator to $\mathrm{Tr}(\rho_\beta q^2)$ and record when the identity fails.

## Progress Tracking
- 2026-09-20: With the same occupation-basis matrix $q$ on both copies, the tested Gibbs TFD obeyed $\langle q_Lq_R\rangle=-\mathrm{Tr}(\rho_\beta q^2)$.
- 2026-09-20: Conjugating the right operator reverses the sign; the identity fails for the Perelomov-weighted TFD.

## Related Files
- `t7b_tfd.py`
- `t7b_results.json`
- `t7b_notes.md`
- `memory-bank/implementation-details/thermofield-double-volume.md`

## Issues and Blockers
- The sign is convention-dependent and must not be stated without the right-copy convention.

## Notes
This is a result for the tested Gibbs-TFD construction, not a universal TFD identity.

- 2026-10-06 12:55:19 IST: Parent ownership consolidated under T9; completed status, original scope, and task ID retained.

---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T7e
*Created: 2026-09-20*
*Last Updated: 2026-10-06 12:55:19 IST*

## Task Information
**Title:** Complexified momenta in the TFD
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-20
**Started:** 2026-09-20
**Completed:** 2026-09-21
**Dependencies:** T9, T7b, T7c
**Current Parent:** T9 (original identifier retained; formerly under T7)

## Description
Test the T5b complex plane perturbation in a fixed-K Perelomov-weighted TFD and examine the two-sided correlator response.

## Acceptance Criteria
- [x] Use the declared T5b perturbation and converged state construction.
- [x] Measure epsilon response and beta dependence for n=4,5.
- [x] Separate the fixed-K result from a general temperature-dependent coherent-sector law.

## Progress Tracking
- 2026-09-21: The fixed-K correlator change was approximately quadratic in epsilon and beta-flat.
- 2026-09-21: Explicit conjugation checks showed no effect on this q-like correlator.

## Related Files
- `t7e_complex_tfd.py`
- `results/t7e_results.json`
- `notes/experiments/t7e_notes.md`
- `memory-bank/implementation-details/thermofield-double-volume.md`

## Issues and Blockers
- A general multi-K $V(\epsilon,T)$ law remains open; the result applies only to the fixed-K construction.

## Notes
This study is separate from the Gibbs TFD results in T7b–T7d.

- 2026-10-06 12:55:19 IST: Parent ownership consolidated under T9; completed status, original scope, and task ID retained.

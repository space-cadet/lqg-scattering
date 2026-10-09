---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T5b
*Created: 2026-09-19*
*Last Updated: 2026-10-06 11:29:29 IST*

## Task Information
**Title:** Perturbation response of the signed-mean proxy
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-19
**Started:** 2026-09-19
**Completed:** 2026-10-01
**Dependencies:** T5, T3c

## Description
Measure the signed-mean proxy response for a fixed imaginary perturbation of a positive real plane and fit its onset exponent.

## Acceptance Criteria
- [x] Sweep $\epsilon=10^{-6}\ldots1$ for n=4,5 with the declared vertex reference.
- [x] Require convergence and independently check representative points.
- [x] Label $\sqrt{|\langle q\rangle|}$ as a signed-mean proxy, not a positive-volume expectation.

## Progress Tracking
- 2026-09-19: The 13-point sweep gave $\alpha\approx0.5$ for n=4,5.
- 2026-10-01: Corrected rerun included convergence assertions; four n=4 and three n=5 points agreed with independent SciPy.

## Related Files
- `t5b_perturbation.py`
- `results/t5b_results.json`
- `memory-bank/implementation-details/volume-positivity-studies.md`

## Issues and Blockers
- The exponent describes this plane perturbation and reference family only; broader plane controls remain open.

## Notes
The tested response is a smooth, non-analytic onset. It does not establish a universal exponent.

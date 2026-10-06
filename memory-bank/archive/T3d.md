---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T3d
*Created: 2026-09-19*
*Last Updated: 2026-10-06 09:47:11 IST*

## Task Information
**Title:** Rust versus Python verification at n=4
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-19
**Started:** 2026-09-19
**Completed:** 2026-10-01
**Dependencies:** T3c

## Description
Cross-validate the Rust and Python n=4 implementations with a converged state and an independent exponential reference.

## Acceptance Criteria
- [x] Compare the Rust state and signed grasp with corrected Python and an independent SciPy exponential.
- [x] Check the Grassmannian embedding and operator conventions.
- [x] Document why the earlier shared short Taylor truncation was not independent validation.

## Progress Tracking
- 2026-09-19: Historical n=4 verification was recorded.
- 2026-10-01: Converged Rust and corrected Python values were checked against independent SciPy; the earlier 15-term comparison was identified as jointly truncated.

## Related Files
- `rust/src/main.rs`
- `coherent_states.py`
- `positivity.py`
- `memory-bank/implementation-details/performance-benchmarks.md`

## Issues and Blockers
- No outstanding T3d item is listed; the independent n=6 check belongs to T3e.

## Notes
Archived for the validated n=4 comparison. Preserve the historical caveat: the first machine-precision agreement compared states with the same unconverged Taylor truncation.

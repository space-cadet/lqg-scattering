---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T5e
*Created: 2026-09-19*
*Last Updated: 2026-10-06 09:47:11 IST*

## Task Information
**Title:** Large-K semiclassics
**Status:** ✅ COMPLETED
**Priority:** MEDIUM
**Created:** 2026-09-19
**Started:** 2026-09-19
**Completed:** 2026-09-20
**Dependencies:** T5, T3c

## Description
Test large-$K$ scaling for fixed-shape and vertex-scaled state families using converged Rust on-the-fly evolution.

## Acceptance Criteria
- [x] Run and checkpoint both specified families over the recorded K range.
- [x] Assert Taylor convergence and independently compare selected stored/on-the-fly points.
- [x] State whether the tested runs support $V\sim K^{3/2}$ without generalizing beyond the families.

## Progress Tracking
- 2026-09-19–20: Converged results reached K=24; vertex-scaled data behaved as $V\sim(K-4)^{1/2}$ and the uniform M=0 family had signed grasp approximately zero.
- 2026-09-20: The claimed $K^{3/2}$ law was not supported for these tested families.

## Related Files
- `rust/src/bin/t5e.rs`
- `t5e_fit.py`
- `notes/experiments/t5e_notes.md`
- `results/t5e_results.json`
- `memory-bank/implementation-details/volume-positivity-studies.md`

## Issues and Blockers
- The original K=20–50 target was not reached; the result is complete only for the converged recorded range through K=24.

## Notes
The first short Taylor cap shifted results and was superseded by the converged cap and assertions.

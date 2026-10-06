---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T1b
*Created: 2026-09-19*
*Last Updated: 2026-10-06 09:47:11 IST*

## Task Information
**Title:** Signed-mean cancellation and positive-volume check on real planes
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-19
**Started:** 2026-09-19
**Completed:** 2026-10-03
**Dependencies:** T1, T1a

## Description
Establish the real-plane cancellation of the signed triple grasp and determine whether it implies vanishing of positive volume, including a real plane outside the positive cell.

## Acceptance Criteria
- [x] Prove and numerically verify $\langle q_{012}
angle=0$ for real-plane states.
- [x] Evaluate positive RS and AL volume on one strictly positive and one off-cell real-plane state.
- [x] Cross-check the tested values with independent local-spin tensor-product blocks.

## Progress Tracking
- 2026-09-19: Original signed-mean result entered the task registry.
- 2026-10-03: Positive RS/AL values were independently checked for two $N=4$, $K=6$ real-plane states; both were nonzero.

## Related Files
- `positivity.py`
- `real_plane_volume.py`
- `t1b_real_plane_volume_results.json`
- `memory-bank/implementation-details/volume-numerical-preliminaries.md`

## Issues and Blockers
- Evidence covers two states and does not establish the result for every real plane or embedding.

## Notes
The supported conclusion is that zero signed mean does not imply zero positive volume. The tested AL values use signs $(+,-,+,-)$.

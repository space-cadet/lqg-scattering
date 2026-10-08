---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T5a′
*Created: 2026-09-19*
*Last Updated: 2026-10-06 09:47:11 IST*

## Task Information
**Title:** Kinematic-polyhedron local chirality
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-19
**Started:** 2026-09-19
**Completed:** 2026-09-19
**Dependencies:** T5a, T6

## Description
Restrict the triple-chirality analysis to facet triples meeting at a vertex of a kinematic Minkowski polyhedron, with adjacency determined before inspecting grasp signs.

## Acceptance Criteria
- [x] Construct conserved kinematics and all-incoming closed face data.
- [x] Freeze geometric adjacency before evaluating $q_{ijk}$.
- [x] Report every tested channel and compare local with all-triple sign agreement.

## Progress Tracking
- 2026-09-19: Completed in commit c443d9a across ten n=5 incoming-pair channels; local and all-triple agreement tracked each other.
- 2026-09-19: The n=4 s/t/u controls were exactly 0.500 and degenerate; the test is informative for local subsetting only at n≥5.

## Related Files
- `minkowski.py`
- `t5a_prime.py`
- `notes/experiments/t5a_prime_notes.md`
- `results/t5a_prime_results.json`
- `memory-bank/implementation-details/T6-minkowski-polyhedron.md`

## Issues and Blockers
- Independent expm exposed an unconverged shared 15-term reference in an earlier check; retain the recorded explicit validation and do not use that shared-truncation comparison as independent evidence.

## Notes
The local subset did not reveal hidden handedness. This is the kinematic pilot under T6, not the full quantum-state geometry correspondence.

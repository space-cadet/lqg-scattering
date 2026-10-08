---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T3e
*Created: 2026-09-19*
*Last Updated: 2026-10-06 09:47:11 IST*

## Task Information
**Title:** Independent n=6 benchmark check
**Status:** 🔄 IN PROGRESS
**Priority:** HIGH
**Created:** 2026-09-19
**Started:** 2026-09-19
**Completed:** —
**Dependencies:** T3c, T3d

## Description
Complete the higher-valence Rust benchmark record and obtain an independent state/exponential check for the n=6 point.

## Acceptance Criteria
- [x] Retain the converged Rust benchmark results for n=5–8.
- [ ] Independently check n=6 using a method that does not share the same state-construction truncation.
- [ ] Record runtime, memory, and the precise observable scope.

## Progress Tracking
- 2026-09-19: Rust n=5–8 benchmark scans were completed.
- 2026-10-01: Corrected converged signed-mean scans were recorded; SciPy checks cover n=5,7,8, leaving n=6 open.

## Related Files
- `code/rust/src/main.rs`
- `memory-bank/implementation-details/performance-benchmarks.md`

## Issues and Blockers
- Independent n=6 check is still open; the original timing targets were met in the recorded run.

## Notes
The benchmark results concern the signed-mean proxy unless a separate positive-volume operator is explicitly named.

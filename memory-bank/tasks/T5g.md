---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T5g
*Created: 2026-09-19*
*Last Updated: 2026-10-06 09:47:11 IST*

## Task Information
**Title:** Higher-valence performance frontier
**Status:** 🔄 IN PROGRESS
**Priority:** MEDIUM
**Created:** 2026-09-19
**Started:** —
**Completed:** —
**Dependencies:** T3c

## Description
Profile the Rust on-the-fly volume calculation at n=10–12 with triple-local references to determine whether state evolution or operator matvecs dominate.

## Acceptance Criteria
- [ ] Select runs that unlock an identified physics calculation.
- [ ] Record dimension, memory, runtime, and dominant kernel.
- [ ] Keep long scans checkpointable.

## Progress Tracking
- 2026-09-19: Registered as an engineering study, not a physics result.
- 2026-10-06: No dedicated T5g profiling run is recorded.

## Related Files
- `memory-bank/implementation-details/performance-benchmarks.md`
- `code/rust/src/onthefly.rs`

## Issues and Blockers
- No current T5g profile or performance limit has been established.

## Notes
Prioritize profiling only where it enables T5a–T5e or another defined physics question.

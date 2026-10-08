---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T7d
*Created: 2026-09-20*
*Last Updated: 2026-10-06 11:29:29 IST*

## Task Information
**Title:** Thermal scaling laws
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-20
**Started:** 2026-09-20
**Completed:** 2026-09-20
**Dependencies:** T9, T7a, T7c
**Current Parent:** T9 (original identifier retained; formerly under T7)

## Description
Test the temperature dependence of the Gibbs-TFD two-sided correlator and compare it with the T5b perturbation response.

## Acceptance Criteria
- [x] Fit the tested beta/temperature response and report fit quality.
- [x] Check the low-temperature occupied-sector onset.
- [x] Separate a tested Boltzmann onset from any general power law.

## Progress Tracking
- 2026-09-20: No reliable power law was found in the tested sweep.
- 2026-09-20: The low-temperature correlator showed an approximately $e^{-3\beta}$ onset; capped-basis results are quantitative for $\beta\ge1$.

## Related Files
- `results/t7b_results.json`
- `notes/experiments/t7b_notes.md`
- `memory-bank/implementation-details/thermofield-double-volume.md`

## Issues and Blockers
- High-temperature values at $\beta\le0.5$ are qualitative because the finite occupation cutoff matters.

## Notes
This subtask is complete for the recorded Gibbs ensemble only.

- 2026-10-06 12:55:19 IST: Parent ownership consolidated under T9; completed status, original scope, and task ID retained.

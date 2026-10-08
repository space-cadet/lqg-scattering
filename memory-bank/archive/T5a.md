---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T5a
*Created: 2026-09-19*
*Last Updated: 2026-10-06 11:29:29 IST*

## Task Information
**Title:** Triple-volume correlations at n≥5
**Status:** ✅ COMPLETED
**Priority:** HIGH
**Created:** 2026-09-19
**Started:** 2026-09-19
**Completed:** 2026-10-01
**Dependencies:** T5, T3c

## Description
Test whether a higher-valence vertex exhibits one shared handedness or whether signed triple-grasp behavior is primarily per-triple.

## Acceptance Criteria
- [x] Evaluate all $\binom{n}{3}$ triple means for the specified n=5–8 state families.
- [x] Compare sign and magnitude correlations and magnetization controls.
- [x] Retain sample-size, convergence, and independent-check limits in the conclusion.

## Progress Tracking
- 2026-09-19: Base n=6,7 runs found sign agreement 0.50–0.70, consistent with per-triple chirality.
- 2026-10-01: Corrected one-plane n=5 magnetization sweep converged in 39–41 Taylor terms; four sectors matched SciPy within $3.6\times10^{-16}$.

## Related Files
- `t5a_mag_sweep.py`
- `results/t5a_mag_results.json`
- `notes/experiments/t5a_mag_notes.md`
- `notes/experiments/t5a_prime_notes.md`
- `memory-bank/implementation-details/volume-positivity-studies.md`

## Issues and Blockers
- The evidence is limited to the recorded planes and samples; it does not establish a universal handedness theorem.

## Notes
The magnetization hypothesis was not supported in the tested sweep. The earlier short-Taylor M-sweep was superseded by the converged rerun.

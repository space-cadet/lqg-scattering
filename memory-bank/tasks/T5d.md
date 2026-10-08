---
source_branch: main
source_commit: 0a254849a5e12734ee32d9d8af74bd4309d17648
---

# Task: T5d
*Created: 2026-09-19*
*Last Updated: 2026-10-06 09:47:11 IST*

## Task Information
**Title:** Cocycle phase and distance-to-cell response
**Status:** 🔄 IN PROGRESS
**Priority:** HIGH
**Created:** 2026-09-19
**Started:** 2026-10-06
**Completed:** —
**Dependencies:** T5, T3c

## Description
Determine how the signed triple grasp responds to leaving the gauge-real locus, using a gauge-invariant Plücker phase and, after definition, a positivity-defect measure.

## Acceptance Criteria
- [ ] Define the phase variable from a Plücker cross-ratio and test gauge invariance.
- [ ] Include positive-real and mixed-sign real controls, plus complex paths at fixed reference and K.
- [ ] Compare the signed grasp to the phase and defect; do not interpret it as positive volume.

## Progress Tracking
- 2026-09-19: T5d registered for cocycle and distance-to-cell scaling.
- 2026-10-06: Rust n=4, K=7 pilot uses $P=M_{01}M_{23}/(M_{02}M_{13})$ and $d_\phi=|\mathrm{Im}P|/|P|$. Both real controls vanish; the sampled small-phase branch is approximately linear and turns over at larger perturbation.

## Related Files
- `code/rust/src/bin/t5d.rs`
- `results/t5d_phase_scan_results.json`
- `memory-bank/implementation-details/volume-positivity-studies.md`

## Issues and Blockers
- The pilot is one seed and one reference family; no general onset exponent or independent distance-to-cell law is established.

## Notes
The real mixed-sign control shows that negative real minors alone are not a distance to the gauge-real zero locus.

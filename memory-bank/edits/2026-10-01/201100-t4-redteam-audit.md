---
source_branch: main
source_commit: cfaf6866c92c8c4d1bda35473bd67bb4bdeb885a
---

#### 20:11:00 IST - T4: Red-team audit of volume claims
- Added `memory-bank/implementation-details/red-team-audit.md` - Recorded independent $n=4$ recomputation, observable distinction, real off-cell control, and claim dispositions.
- Modified `rust/src/coherent.rs` - Made Taylor convergence fail loudly; corrected nonterminating-series comment.
- Modified `rust/src/onthefly.rs` - Made the on-the-fly wrapper reject a saturated Taylor cap.
- Modified `coherent_states.py` - Replaced the shared short Taylor cap with a convergence-checked exponential.
- Modified `positivity.py` - Labeled the signed-mean proxy and added a real plane outside the positive cell as a control.
- Modified `t7a_thermal.py` - Distinguished the thermal signed mean from positive volume.
- Modified `t7b_tfd.py` - Documented the right-operator convention of the two-sided correlator.
- Modified `t5b_perturbation.py` - Repaired the historical sweep's short Taylor cap and added a convergence failure.
- Modified `t5b_results.json` - Saved the converged n=4/5 rerun and state-engine provenance.
- Modified `t5a_mag_sweep.py` - Repaired the provisional sweep's short Taylor cap and added a convergence failure.
- Modified `t5a_mag_results.json` - Saved the converged ten-state sweep with iteration counts and state-engine provenance.
- Modified `t5a_mag_notes.md` - Replaced the provisional verdict with fixed-plane findings and independent-state checks.
- Modified `t5a_prime_notes.md` - Removed the stale parent-sweep rerun-pending note.
- Modified `t7a_notes.md` - Clarified that the thermal zero concerns the signed mean.
- Modified `t7b_notes.md` - Stated the right-operator convention governing the correlator sign.
- Modified `t7e_notes.md` - Scoped the near-half proxy exponent to the tested family.
- Modified `rust/src/volume.rs` - Labeled the signed-mean proxy and corrected the zero-mean interpretation.
- Modified `rust/src/main.rs` - Scoped the scan assertions to the tested real and complex planes.
- Modified `rust/src/experiment.rs` - Replaced the truncated n=4 test value with the independently converged value.
- Modified `manuscript.md` - Narrowed the central claim and marked historical baseline numbers for revalidation.
- Modified `dashboard/data.json` - Marked baseline verification open and corrected the paper year and theory summary.
- Modified `dashboard/index.html` - Labeled historical proxy values in the visible dashboard.
- Modified `memory-bank/implementation-details/performance-benchmarks.md` - Kept timings as historical records with convergence caveat.
- Modified `memory-bank/implementation-details/verification-protocol.md` - Added independent exponential, real off-cell, and positive-volume checks.
- Modified `memory-bank/implementation-details/experiments.md` - Reordered research around observable definition and converged reruns.
- Modified `memory-bank/implementation-details/thermofield-double-volume.md` - Distinguished signed mean and stated the right-operator convention.
- Modified `memory-bank/tasks.md` - Reopened T3d/T3e validation and narrowed T1b/T5b claims.
- Modified `memory-bank/projectbrief.md` - Updated project interpretation and current status.
- Modified `memory-bank/productContext.md` - Corrected the EPJC baseline and reframed the research question.
- Modified `memory-bank/implementation-details/grassmannian-embedding.md` - Replaced the unsupported zero-volume claim with the signed-mean result.
- Modified `memory-bank/activeContext.md` - Recorded audit findings and next actions.
- Modified `memory-bank/session_cache.md` - Recorded current validation status.
- Modified `memory-bank/progress.md` - Separated historical implementation from numerical revalidation.
- Modified `memory-bank/sessions/2026-10-01-evening.md` - Appended red-team findings and limitations.
- Modified `memory-bank/changelog.md` - Summarized red-team correction.

#### Host Rust continuation
- Ran the 20-test Rust release suite and the corrected n=4 and n=5..8 scans with the host Rust toolchain.
- Independently checked the corrected n=5,7,8 complex-plane proxies with fixed-$K$ SciPy exponentiation; n=6 remains open.
- Updated manuscript, dashboard, benchmarks, audit, task state and session records with the current numerical results.

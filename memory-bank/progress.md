# Implementation Progress

*Last Updated: 2026-10-09 11:16:39 IST*

## Active Tasks

### T1a: Positive FL Volume Across Tetrahedron Shapes
**Status:** 🔄 IN PROGRESS
**Priority:** HIGH

The regular FL tetrahedron area sweep covers $J=1\ldots5$; direct tensor-product expectations now agree within $1.67\times10^{-16}$ after a shared numerical zero-mode cutoff. At $J=2$, a refreshed 440-point ordered equal-face-area scan finds the regular tetrahedron as the sampled minimum for both RS and AL expectations. Two direct tensor-product shape checks agree to floating-point precision, and the displayed shape guide remains on both dashboard panels. This grid does not establish a global minimum. Initial T5c weighted inputs now verify unequal area means and closure; broader unequal-area sampling and the flat-boundary limit remain open. The project-normalized $J=2$ expectations do not simply follow reconstructed classical volume at the selected comparison points.

**Next:** study equal-area shape and boundary behavior under T1a. T5c now owns the FL classical/quantum volume comparison, with weighted spinors for unequal area ratios and the input tetrahedron as the primary classical reference. Keep sampled minima distinct from a global-minimum claim.

### T5c: FL Classical/Quantum Volume Comparison
**Status:** 🔄 IN PROGRESS
**Priority:** HIGH

The original positive-volume results cover a regular-area sweep and five
interior equal-area shapes at $J=1,2,3$. The new weighted input pilot covers
regular and unequal-skew tetrahedra through $J=7$, a nine-shape unequal-area
grid at $J=2,4$, four selected grid shapes at $J=6$, and a fixed-area flat
path at $J=2,4,6,7$. With fixed geometric factors, the regular and
unequal-skew mean ratios reach $0.953$ and $0.904$ at $J=7$. Weighted closure
and scalar area means pass; unequal normalized pair correlations still
differ from the input normals, reaching $0.0584$ error at $J=7$. At the
exact flat boundary the normalized positive mean remains nonzero in the
tested range, but neither iterated limit is established. The calibrated RS
and AL curves coincide by four-valent closure under the selected signs, so
they are not independent evidence. AL graph signs and physical prefactors
remain open. See `implementation-details/T5c-flux-covariance-volume-comparison.md`.

### T8: Amplituhedron Program
**Status:** 🔄 IN PROGRESS
**Priority:** MEDIUM

T8a tracks whether cluster algebra structures help organize the project's
Plücker-coordinate charts or positivity checks. T8b subsumes the former T5f
positive-cell/scattering-region mapping. Both remain exploratory; no new
physical interpretation or implementation is asserted. See `tasks/T8.md`.

### T4: Follow-up Manuscript
**Status:** 🔄 IN PROGRESS
**Priority:** MEDIUM

#### Completed Steps
- ✅ EPJC paper identified as frozen published baseline
- ✅ manuscript.md restructured: published baseline → follow-up numerical work
- ✅ Numerical results section drafted (n=4..8 volume data)

#### Current Work
- 🔄 The manuscript contains results through T7e and separates signed-mean proxies from positive volume. RS/AL operators are now implemented for small active sectors; coherent-state volume results and claim review remain open.
- ✅ Independent red-team audit recorded in `implementation-details/red-team-audit.md`.

#### Up Next
- ✅ Reconciled the conclusion with T5e and qualified the T5a magnetization sweep.
- ✅ Corrected converged signed-mean scans completed. RS/AL positive volume routines implemented and checked on simple states; coherent-state volume reruns and large-block methods remain open.
- ⬜ Record independent red-team review per claim.
- ⬜ Circulate the corrected draft for review.

### T5: Volume–Positivity Numerical Studies
**Status:** 🔄 IN PROGRESS (T5a base analysis recorded; magnetization sweep converged for one plane; T5a′ kinematic local-triple analysis recorded; T5b converged rerun complete for its tested family; T5e converged scoped study recorded; T5c, T5d, T5g open; former T5f transferred to T8b)
**Priority:** HIGH

**Roadmap:** `memory-bank/implementation-details/volume-positivity-studies.md`

Seven numerical studies probing signed triple-grasp response and its possible
relation to volume. The positive cell is not the full zero locus; see the
red-team audit. Subtasks T5a–T5g are in `tasks.md`. T5c's
state-specific definitions and exploratory covariance pilot are in
`implementation-details/T5c-flux-covariance-volume-comparison.md`;
common notation is in `implementation-details/volume-numerical-preliminaries.md`.

**T5a evidence and caveat:** the n=6,7 base triple-correlation runs record sign-agreement 0.50–0.70 and small cross-seed correlations, consistent with per-triple chirality; n=8 remains resource-limited. The n=5 magnetization sweep was rerun with convergence assertions (39–41 terms) and four sectors matched independent SciPy exponentiation to at most 3.6e-16 in triple means. Its fixed-plane sign pattern remains one-plane evidence. T5a′ reports no increase in sign coherence for kinematic-polyhedron-local triples, with 8 planes per n=5 channel and weak per-plane sign-test power. See `notes/experiments/t5a_mag_notes.md`, `notes/experiments/t5a_prime_notes.md`, and `implementation-details/volume-positivity-studies.md`.

### T9: Thermal/TFD State Construction and Physical Study
**Status:** 🔄 IN PROGRESS; exactly five completed child-study records, with new state-family and geometry work ongoing at parent level.

T9 owns the entire thermal/TFD program. The former T7 umbrella was transferred and archived; T7a–T7e retain their IDs and completed evidence as T9 child studies. The new manuscript squeeze is implemented for small FL sectors. Combined dual-copy closure passes, ordinary closure on each copy fails, and a separately labelled double-singlet projection restores ordinary closure; its Gibbs interpretation remains unresolved. The initial pilot compares regular and unequal-skew four-face FL labels at $J=1,2$ over $\beta=3,4,5,8$, with pair cutoff 4 and cutoff-2 comparisons. The data are comparative evidence, not a reconstruction of classical geometry. See `tasks/T9.md`, `archive/T7.md`, the mathematical-background note, and the saved T7-named numerical artifacts.

T9 follow-up: the selected state is $U_\beta(|J,\mathbf z\rangle_L\otimes|\overline{J,\mathbf z}\rangle_R)$, with transformed geometric observables. For four faces and $J_{\mathrm{in}}=1$, $P(q,S)$ is implemented by explicit spin coupling and magnetic-component counting with finite differences. The methods agree across 32,805 entries ($q=0\ldots160$; $\beta\hbar\omega=0.5,1,2,4,8$) to maximum absolute discrepancy $2.67\times10^{-16}$. Independent oscillator coefficient and direct Casimir-projector checks cover $q\le4$. Plots show broader occupation and spin distributions at higher temperature. The apparent high-$q$ cutoff is a display/numerical limit: an analytic positive bound establishes nonzero probability at every kinematically allowed $(q,S)$ for finite temperature. Full two-copy reduced-state blocks, entropy, and geometric correlations remain open. For fixed positive $H_A=\lambda N_L/2$ on unrestricted Fock space, the Gibbs low-temperature limit is vacuum while the squeezed family returns its nonzero-$J$ input; that Hamiltonian is excluded as its Gibbs generator over all temperatures. The earlier one-sided pilot remains separate evidence for the draft's original state. See `notes/thermal-area-sectors.md` and `tasks/T9.md`. Calculation and note update by GPT 6.1 Sol.

## Historical Implementation and Runs

### T1: Python Pipeline
**Completed:** 2026-09-19
**Summary:** Reference implementation of Fock space, U(N) coherent states, Grassmannian embedding, and positivity tests in Python. All n=4 computations completed and verified.

### T1a: Volume Operator at n=4
**Initial implementation completed:** 2026-09-19
**Summary:** Historical results were signed triple-grasp means and their proxy, not positive volume expectations. Exact small-sector RS and AL expectations are implemented. The EPJC Eq. (38) FL regular-tetrahedron fixed-area sweep for $J=1\ldots5$ is positive under both prescriptions; with the shared numerical zero-mode cutoff, direct-tensor expectations agree within $1.67\times10^{-16}$ and triple-grasp matrices within $2.8\times10^{-15}$. The later $J=2$ shape scan and its limits are recorded in the active T1a section and `implementation-details/volume-operator.md`.

### T1b: Signed-mean result on real planes
**Completed:** 2026-10-03 (positive-volume follow-up; signed-mean result recorded 2026-09-19)
**Summary:** Real-plane states have zero signed triple-grasp mean, including
planes outside the positive cell. At $N=4$, $K=6$, tested strictly positive
and off-cell Perelomov states have nonzero positive RS and AL expectations.
The AL values use regular-tetrahedron tangent signs; see `code/python/real_plane_volume.py`
and `results/t1b_real_plane_volume_results.json`.

### T2: Manuscript (EPJC Paper)
**Completed:** 2026-09-19
**Summary:** LaTeX paper written, compiled, and published in EPJC. PDF at `paper/lqg-amplituhedron.pdf`.

### T3a: Fock Space + u(N) Operators (Rust)
**Completed:** 2026-09-19
**Summary:** Rust implementation of Schwinger boson Fock space and sparse u(N) operators. Committed as `ee3ff0e`.

### T3b: Coherent States + Grassmannian (Rust)
**Completed:** 2026-09-19
**Summary:** Rust implementation of U(N) Perelomov coherent states and Grassmannian Plücker embedding. Committed as `42ce24e`.

### T3c: Volume Operator (Rust)
**Completed:** 2026-09-19 16:26 IST
**Summary:** Sparse triple-grasp matrix and signed-mean proxy are retained. RS and AL positive vertex expectations use project normalization and dense active-sector evaluation up to dimension 512. The Rust FL Eq. (38) example now matches the Python $J=2$ values after both engines apply the shared numerical zero-mode cutoff. Physical prefactors and a larger-block method remain open. The historical n=4 signed-mean verification shared an unconverged Taylor state; the corrected Rust/Python and SciPy checks now agree. Committed as `ee72845`.

### T3d: Verify Rust vs Python at n=4
**Historical run:** 2026-09-19 16:26 IST
**Summary:** Historical Rust/Python match shared a 15-term Taylor truncation.
Corrected Rust/Python and independent SciPy checks agree on $\langle q\rangle=-0.000827687168$ for the canonical complex plane.

### T3e: Benchmarks n=5,6,7,8
**Historical run:** 2026-09-19 16:26 IST
**Summary:** Corrected converged Rust scans were completed for $n=5$–$8$. Independent SciPy checks $n=5,7,8$; $n=6$ remains open. The real-plane signed-mean cancellation
does not establish zero positive quantum volume.

## 2026-10-08 23:21:44 IST: Closed-basis volume baseline

T1a completed all four-labelled-face singlet basis data at $K=2,\ldots,12$ (10,549 states), with positive RS/AL expectations, fluctuations, spectra and compressed matrices. Independent triple checks and reload verification passed within declared tolerances. The user stopped extension during $K=13$ verification; no $K=13$ output is accepted. T10 is deferred for the variable-face catalogue; no such spectra or new thermal volumes were computed. See [session summary](sessions/2026-10-08-volume-studies.md).

## Variable-face RS baseline and volume note — 2026-10-09 11:10:50 IST

T10's completed catalogue covers all labelled positive-face singlets at $K=2,3,4$, with closed dimensions 2, 36, and 347 and positive-volume dimensions 2, 32, and 329. Independent counts, triple matrices, exact spin-half controls, saved operators, readable catalogues and figure exports are recorded in [volume studies](../notes/volume-studies.md). The saved verifier checked 112 blocks and 385 eigenstates. Physical normalization and higher-valence AL orientation data remain unresolved. No Hamiltonian energy, thermal-volume, or graph-changing result is claimed.

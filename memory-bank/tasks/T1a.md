---
source_branch: work
source_commit: 9602c9811278635eb4b3e3e601badd28e7964862
---

# T1a: Positive-volume construction and validation in Python
*Created: 2026-10-02 12:15:21 IST*
*Last Updated: 2026-10-03 00:27:43 IST*

**Description**: Implement and validate positive Rovelli–Smolin and Ashtekar–Lewandowski volume expectations in the Python reference implementation at n=4.
**Status**: 🔄 IN PROGRESS
**Priority**: HIGH
**Started**: 2026-09-19
**Last Active**: 2026-10-03 00:27:43 IST
**Dependencies**: T1

## Completion Criteria
- ✅ Implement positive RS and AL expectations using exact active-sector spectral decomposition.
- ✅ Check paired spin-1/2 singlet and collinear controls against an independent tensor-product calculation.
- ✅ Preliminary Python evaluation of the EPJC Eq. (38) FL fixed-area coherent state on a regular tetrahedron gives positive RS and AL volumes.
- ✅ Rebuild an independent local-spin tensor-product calculation for the regular tetrahedron; both positive volumes now match the sector routines to floating-point precision. The source of the earlier inline discrepancy is not recoverable because its calculation was not saved.
- ✅ At $J=2$, scan 440 ordered equal-face-area shapes; both sampled RS and AL minima occur at the regular tetrahedron. This is a finite-grid result, not a global-minimum proof.
- ✅ At $J=2$, strict-positive face-spin enumeration yields one assignment $(1/2,1/2,1/2,1/2)$ and its two recoupling channels. This counts discrete labels, not continuous shapes.
- 🔄 Extend validation and select physical regularization prefactors.
- 🔄 Replace dense diagonalization before evaluating active blocks above dimension 512.

## Related Files
- `positivity.py`
- `coherent_states.py`
- `fl_volume_validation.py`
- `fl_volume_shape_scan.py`
- `fl_volume_labels.py`
- `fl_volume_shape_scan_log.md`
- `dashboard/fl-volume-shape-j2.json`
- `dashboard/figures/fl-volume-shape-j2.svg`
- `memory-bank/implementation-details/fock-space-construction.md`
- `memory-bank/implementation-details/volume-operator.md`

## Progress
1. ✅ Positive RS and AL calculations and simple-state controls are recorded in the repository.
2. ✅ The EPJC Eq. (38) target is the FL fixed-area coherent state; one regular-tetrahedron case has positive RS and AL expectations.
3. ✅ Reproduced the Eq. (38) state and matched independently assembled tensor-product blocks to the project routines (maximum operator-matrix difference 0; volume differences below $7\times10^{-18}$). The prior inline discrepancy does not reproduce; its origin remains unknown.
4. ✅ Swept the regular-tetrahedron fixed-area label $J=1\ldots5$ and added the RS/AL positive-volume plot to the dashboard. Triple-grasp matrices agree with the direct tensor calculation within $2.8\times10^{-15}$; positive-volume expectations differ by at most $2.91\times10^{-10}$ over the sweep.
5. ✅ Scanned 440 ordered equal-face-area shapes at $J=2$. The sampled RS and AL minima are at $x=1/\sqrt{3}$, $\varphi=90^\circ$; closure, cross-ratio, two tensor-product points, and phase/rotation invariance were checked. The grid excludes exact degenerate boundaries and does not establish a global minimum.
6. ✅ Enumerated strict positive face-spin assignments at $J=2$: only $(1/2,1/2,1/2,1/2)$ occurs, with two recoupling channels. This is not an enumeration of continuous shapes.
7. ✅ Added shape thumbnails to both dashboard panels and deployed the final asset at website commit `f0b6fdd` (workflow `37033479554`). The live HTML and cache-busted SVG returned HTTP 200; the SVG contains 11 thumbnails per panel, 22 total.
8. 🔄 Extend the scan to boundary limits, larger $J$, and unequal positive face assignments; track volume spread/variance and keep sampled minima distinct from a proof. Select physical prefactors and address larger blocks.

## Context
The EPJC Eq. (38) fixed-area coherent state is the FL state. In the regular-tetrahedron case ($N=4$, $J=2$, $K=4$), project routines give $V_{RS}=0.05077553260216399$ and $V_{AL}=0.025387766749131433$. A reproducible independent construction from local spin-$j$ tensor-product matrices gives $V_{RS}=0.050775532602163984$ and $V_{AL}=0.02538776674913143$; the largest triple-matrix difference is zero at the reported precision. The earlier inline direct values differed by about $1.8\times10^{-10}$, but that unsaved calculation’s cause remains unknown. Reproduce with fl_volume_validation.py. Rust evaluation source is in rust/examples/fl_volume.rs; execution remains unverified because this checkout’s Cargo symlink points to a missing rustup-init. The spinorial phase-space framework is due to Freidel–Speziale (FS); it is not a distinct target family for this EPJC equation.

The sweep values and chart are in `fl_volume_area_results.json` and `dashboard/data.json`; the SVG is `dashboard/figures/fl-volume-area.svg`. Website copy is on `space-cadet/website` branch `codex/lqg-scattering-dashboard` at `824b2b8`. Host-access workflow run `36990851937` succeeded; live Projects, project, dashboard, JSON, and SVG routes returned HTTP 200. The live card is inside the collapsed “Quantum physics and research” group, so expand that section to see it. The browser loaded all eight run records and rendered the static area plot. Physical prefactors and broader validation remain open. Keep the signed-mean proxy distinct from expectation values of positive volume operators.

The $J=2$ equal-face-area scan and its limits are recorded in `fl_volume_shape_scan_log.md` and `implementation-details/volume-operator.md`. The regular shape is the minimum only among 440 ordered grid samples. The $J=2$ positive-label enumerator reports one strict assignment with two recoupling channels; it does not enumerate the continuum of shapes. The shape plot is in both RS and AL panels, with representative thumbnails, and its final website deployment is commit `f0b6fdd` (workflow `37033479554`). Classical-volume comparisons at selected points differ from the quantum expectations; exact degenerate limits and fluctuation analysis remain open. Consult the qhe-bhe Thurston/Minkowski material for possible geometric parameterization, without treating it as a proof about the quantum operator.

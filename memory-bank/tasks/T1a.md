---
source_branch: work
source_commit: 9602c9811278635eb4b3e3e601badd28e7964862
---

# T1a: Positive-volume construction and validation in Python
*Created: 2026-10-02 12:15:21 IST*
*Last Updated: 2026-10-08 10:26:00 IST*

**Description**: Implement and validate positive Rovelli–Smolin and Ashtekar–Lewandowski volume expectations in the Python reference implementation at n=4.
**Status**: 🔄 IN PROGRESS
**Priority**: HIGH
**Started**: 2026-09-19
**Last Active**: 2026-10-08 10:27:24 IST
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
- `code/python/positivity.py`
- `code/python/coherent_states.py`
- `code/python/fl_volume_validation.py`
- `code/python/fl_volume_shape_scan.py`
- `code/python/fl_volume_labels.py`
- `notes/experiments/fl_volume_shape_scan_log.md`
- `code/dashboard/fl-volume-shape-j2.json`
- `code/dashboard/figures/fl-volume-shape-j2.svg`
- `memory-bank/implementation-details/fock-space-construction.md`
- `memory-bank/implementation-details/volume-operator.md`
- [Shared volume numerical preliminaries](../implementation-details/volume-numerical-preliminaries.md)
- [T5c state-to-geometry comparison](../implementation-details/T5c-flux-covariance-volume-comparison.md) (related comparison; T5c remains separate)

## Progress
1. ✅ Positive RS and AL calculations and simple-state controls are recorded in the repository.
2. ✅ The EPJC Eq. (38) target is the FL fixed-area coherent state; one regular-tetrahedron case has positive RS and AL expectations.
3. ✅ Reproduced the Eq. (38) state and matched independently assembled tensor-product blocks to the project routines (maximum operator-matrix difference 0; volume differences below $7\times10^{-18}$). The prior inline discrepancy does not reproduce; its origin remains unknown.
4. ✅ Swept the regular-tetrahedron fixed-area label $J=1\ldots5$ and added the RS/AL positive-volume plot to the dashboard. A scale-aware numerical zero-mode cutoff makes direct tensor-product expectations agree within $1.67\times10^{-16}$ over the sweep; triple-grasp matrices agree within $2.8\times10^{-15}$.
5. ✅ Scanned 440 ordered equal-face-area shapes at $J=2$. The sampled RS and AL minima are at $x=1/\sqrt{3}$, $\varphi=90^\circ$; closure, cross-ratio, two tensor-product points, and phase/rotation invariance were checked. The grid excludes exact degenerate boundaries and does not establish a global minimum.
6. ✅ Enumerated strict positive face-spin assignments at $J=2$: only $(1/2,1/2,1/2,1/2)$ occurs, with two recoupling channels. This is not an enumeration of continuous shapes.
7. ✅ Added 11 representative shape thumbnails to each dashboard panel; the initial live version was deployed at website commit `f0b6fdd` (workflow `37033479554`).
8. ✅ Reused pre-generated input-shape thumbnails in the saved 440-point figure and deployed the updated figure with the T5c per-point previews at website commit `9c6670c190e813470975f18037c1ed4a6ecea8bc` (workflow `37125090987`).
9. 🔄 Extend the scan to boundary limits, larger $J$, and unequal positive face assignments; track volume spread/variance and keep sampled minima distinct from a proof. Select physical prefactors and address larger blocks.
10. 🔄 Initial weighted FL volume pilots now cover a regular and an unequal-skew tetrahedron through $J=7$, plus a nine-shape unequal-area grid at $J=2,4$. The weighted spinors reproduce the requested closure and mean face spins. Broader unequal-area sampling and higher-$J$ comparisons remain open; this is distinct from enumerating fixed face-spin assignments. See the T5c scan records.

## Context
The EPJC Eq. (38) fixed-area coherent state is the FL state. With a $64\epsilon_{\rm mach}\max(1,\rho(|Q|))$ cutoff for numerical zero eigenvalues, the regular-tetrahedron case ($N=4$, $J=2$, $K=4$) gives $V_{RS}=0.05077553170606511$ and $V_{AL}=0.02538776585303255$. An independent local spin-$j$ tensor-product construction agrees within $7\times10^{-18}$; the largest triple-matrix difference is zero at the reported precision. The Rust FL example now runs from the installed Rust 1.92 toolchain and matches the Python values at the displayed precision. The old unsaved inline result remains unrecoverable. Reproduce with `code/python/fl_volume_validation.py` and `code/rust/examples/fl_volume.rs`. The spinorial phase-space framework is due to Freidel–Speziale (FS); it is not a distinct target family for this EPJC equation.

The sweep values and chart are in `results/fl_volume_area_results.json` and `code/dashboard/data.json`; the SVG is `code/dashboard/figures/fl-volume-area.svg`. Website copy is on `space-cadet/website` branch `codex/lqg-scattering-dashboard` at `824b2b8`. Host-access workflow run `36990851937` succeeded; live Projects, project, dashboard, JSON, and SVG routes returned HTTP 200. The live card is inside the collapsed “Quantum physics and research” group, so expand that section to see it. The browser loaded all eight run records and rendered the static area plot. Physical prefactors and broader validation remain open. Keep the signed-mean proxy distinct from expectation values of positive volume operators.

The $J=2$ equal-face-area scan and its limits are recorded in `notes/experiments/fl_volume_shape_scan_log.md` and `implementation-details/volume-operator.md`. The regular shape is the minimum only among 440 ordered grid samples. The $J=2$ positive-label enumerator reports one strict assignment with two recoupling channels; it does not enumerate the continuum of shapes. The dashboard's latest visual update, including the refreshed T1a shape figure, is deployed at commit `9c6670c` (workflow `37125090987`); earlier numerical data refreshes remain separate from this presentation update. Classical-volume comparisons at selected points differ from the quantum expectations; exact degenerate limits and fluctuation analysis remain open. Consult the qhe-bhe Thurston/Minkowski material for possible geometric parameterization, without treating it as a proof about the quantum operator.

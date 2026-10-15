---
source_branch: main
source_commit: 8dbd02a5be7752a4620a2586b656234801a169de
---

# T9 entanglement and the next face-growth question

*Recorded: 2026-10-16 03:47:18 IST*

The user authorized numerical investigations at the assistant's discretion,
requested all work in the numerics dashboard with pedagogical explanations,
and emphasized existing code organization and avoiding duplication. They then
specified the next physical question: can a large-area tetrahedron evolve
toward a polyhedron with more, smaller faces, and what is needed to test energy
equipartition? This session completes the closed-reference entropy study and
records a feasibility assessment for that next question.

## Implemented study

The exact reference is the normalized double-singlet projection of the
conjugate-paired F12 area-one input after the two-copy squeeze. It starts with
two occupied faces. The selected unprojected family and general regular or
deformed four-face FL inputs remain separate work.

Shared coefficient parameters and singlet eigenvalues extend
`code/python/lqg_scattering/thermal_projection.py`.
`thermal_entanglement.py` handles labels, spectrum sums and infinite tails.
Calculation, independent verification and plotting drivers live in
`code/thermal/`; outputs, figures and narrative follow existing directories.
The library index is updated. The earlier independent oscillator code is
reused for verification rather than duplicating squeeze implementations.

86 temperatures cover T*=0.05..5, adaptive per-copy area cutoffs 12..140.
Outputs include entropy and explicit tail intervals, area-distribution and
within-area components, purity/Rényi-2, moments, coherent joint F12 creation
and numerical temperature derivatives. Six grouped Schmidt spectra preserve
signed amplitudes and multiplicities. Maximum entropy truncation estimate is
6.4e-12 nats; floating-point rounding is not interval-certified.

At T*=1 and 2, S/kB=4.2499614704 and 7.2455421267; within-area contributions
are 2.3116703474 and 4.5340173366. Joint-creation means are 9.9453994512 and
36.3705318491. Transfer coherence is exactly zero by equal-area support.
Joint creation probes inter-area coherence that the single-copy density matrix
cannot distinguish from a dephased joint state. No entropy derivative is
identified with heat capacity.

## Evidence

All 802 comparisons pass: independent per-mode matrix exponentials and Casimir
projection/SVD for small sectors, direct oscillator creator matrices, saved
magnetic-counting geometric moments, enlarged cutoffs and halved derivative
steps. Max non-derivative residual is 1.74e-11; max derivative discrepancy is
6.25e-8 against 2e-6 tolerance. Existing 46 regression tests pass after the
shared coefficient refactor. Two vector-PDF/300-dpi-PNG figures were visually
inspected. Full records are in `results/thermal-closed-entanglement/`.

The dashboard's established catalogue/exporter adds the entropy study and
previously absent closure, projection and T9a exchange records: 25 catalogue
studies, 34 selectable datasets, 44 figures. NS30 backfills October 14 exchange;
NS31 records this entropy study. It adds direct note-reader access per dataset
and keeps uncertainty columns available in details while presenting a compact
entropy table. Local schema/link/hash and all numerical source-parity checks
pass. Browser notes render 53 math expressions without errors and load both
figures; all four shared tabs are reachable. Publication acceptance is recorded
below when verified.

## Next physical investigation

`notes/face-energy-equipartition.md` records a proposed T11 continuation with
T9 support. Existing E_ij hopping preserves closure and area and can populate
vacuum extra channels. A free quadratic U(N) Hamiltonian preserves FL coherent
states, permitting a prospective large-K spinor evolution control without a
large many-body matrix. Small-K occupation-space verification is the first
implementation step. Interacting equilibration requires specified face-energy
conventions, recurrence/initial-state/size controls and scalable operator
actions. Actual valence changes require additional Hilbert-space and refinement
rules. No new simulation or task ID is claimed for this proposal.

The incomplete SQLite/history backfill remains unchanged; the canonical edit
chunk records this session without regenerating the historical view.

## User's proposed neighbouring-face interaction

The user suggested F/J interactions or pairwise Hubbard terms. Added the
exact identity F_ij-dagger F_ij = n_i n_j/2 - 2 J_i dot J_j to the face-growth
note, with its oscillator derivation. Both diagonal F interactions and spin
exchange preserve each n_i; E hopping or off-diagonal F_ij-dagger F_kl changes
occupations. On a fixed-area singlet space the uniform all-pair diagonal F
sum is K(K+1), while the all-pair spin sum is minus half the sum of local
Casimirs. These avoid redundant proposed interactions. The note records a
candidate family and a minimal staged comparison; no added Hamiltonian was
simulated or adopted as a derived physical law.

## Publication status

Local dashboard generation, 512 packaged link checks, 250 hash checks and
source parity for 2,365 numerical rows / 33,386 numeric values pass. The
overview contributes 42 additional rows, giving 2,407 rows checked by schema.
The new entropy dataset exposes its pedagogical note directly; bounds remain
available in row details. All four browser tab visibility assertions pass.
The entropy note renders 53 math expressions, no math errors, and both images;
the face-growth note also renders without math/console errors. The initial
standalone local favicon request returned 404; subsequent application
interactions reported no console errors. See the UI-test record and screenshot.

An isolated website checkout was prepared at
`/private/tmp/website-lqg-thermal-20261016` from current origin/main. It changes
only `projects/scattering-in-lqg/numerics/`, preserving unrelated website work.
Automatic approval review rejected the commit/push publication command because
explicit authorization for exporting research artifacts to the shared main
branch was required. No commit or push ran in that rejected command. The local
package is prepared; an explicit publication question was sent to the user.
Public deployment remains pending until approval and live verification.


## Local completion: face activation control and dashboard

Completed 20 free-hopping FL controls (five/six channels, K=2..10000, two phase
choices), with exact binomial face marginals and 360 independent comparisons
(maximum residual 1.82e-11). Initially empty channels activate; unequal areas and
local energies recur. No thermalization or interacting equipartition is established.
Six occupied channels can share one normal direction, so channel count is not
a geometric face count. Inputs, provenance, plots and pedagogical explanation
are saved under results/fl-face-activation and notes/face-energy-equipartition.md.

The shared dashboard now contains 35 datasets and 26 catalogue studies. Schema,
532 packaged links, 263 hashes and parity of 2385 numerical rows/33646 numeric
values pass. Browser: face study has 20 rows, one figure and 33 rendered math
expressions without KaTeX or console errors. Entropy verification remains 802
comparisons, and all 46 existing regression tests passed after shared library
changes.

Automatic approval review rejected website upload/shared-main publication. The
user explicitly answered "Keep the update local". No website commit or push ran;
code/dashboard is authoritative. Interacting F/J/Hubbard proposals are documented
but have not been simulated in this continuation.

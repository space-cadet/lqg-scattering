---
source_branch: main
source_commit: 9a2fedd660a70cba8906a41bd6e46b6438264535
---

# T9a singlet exchange — 2026-10-14

*Created: 2026-10-14 14:35:25 IST*

The user explicitly requested a new T9 subtask, documentation reconciliation, and implementation. This overrides the former five-child restriction. T9a is the sixth child; historical T7a–T7e remain intact.

The discussion selected pure fixed-area FL preparations as geometric inputs, alongside a distinct coupled ground-state calculation. Regular tetrahedra are the baseline; controlled unequal areas and one closed shape deformation separate the effects. Face correspondence and spinor phases are specified in [the study plan](../../notes/t9a-singlet-exchange.md).

Implemented exact singlet creation across local area sectors, six corresponding-pair transfer channels, polyhedron-area energies/repulsion, FL products, area/current/coherence/entropy, positive RS volumes, face areas and flux-dot readouts. The combined $K=4$ space has 1,210 states; four Hamiltonian settings and three inputs give twelve trajectories. Ground states use uniform degenerate-space mixtures; finite-temperature controls are canonical on fixed combined area. No reservoir dynamics, sewing, or thermal-family equivalence was implemented.

Internal maximum residual: 4.53e-14. Analytic one-unit oscillations, direct oscillator transfer, current derivative and vacuum/no-exchange controls pass. The sparse-propagation verifier and full regression results are recorded in the result report. Equal-area means remain equal despite distribution broadening and entanglement; unequal-area resonant input transfers substantial area. Interacting ground spaces have degeneracy 105, so no unique geometry is inferred.

Reconciled the stale T11 geometric implementation note and remaining-program statement against the existing October 11 candidate/evolution report. Linked ownership through T9, T11, research notes, registry, context and cache. The generated history view is preserved because its database/chunk backfill remains incomplete, as recorded in the earlier October 14 session.

Continue with larger-area/shape/channel controls, initial states coherent across area sectors, and then reservoir relaxation and comparison with the selected T9 family. No commit, publication, or deployment was requested.

Verification closeout: all 46 Python regression tests passed. Independent sparse propagation and infinite-temperature traces gave 1,792 comparisons with maximum residual $9.06\times10^{-13}$. Vector PDF and 300-dpi PNG overview exported and visually inspected. See [the result report](../../results/t9a-singlet-exchange/README.md).

## Research-note extraction and editorial assessment — 2026-10-14 16:05:06 IST

The user requested moving the heating/closure and equilibrium/exchange sections, together with this session and the previous session's work, into a fresh illustrated document. Created `notes/thermal-geometry-and-singlet-exchange.md`, preserving the prior physical prose, equations, tables and three heating figures, and adding the implemented exchange Hamiltonian, FL preparations, ground/canonical comparisons, results, fourth figure, and manuscript/session provenance. The three manuscript heating figures are the same existing assets, not duplicated exports.

The remaining `notes/thermal-area-sectors.md` shrank from 1,470 to 1,066 lines. Legacy section anchors contain short redirects; current task, note-index and research-record links point directly to the extracted note. The remaining derivations/figures are preserved. A malformed coefficient denominator was repaired from the preceding ordered expansion, and three verified obsolete pending statements were corrected. Historical proposals are preserved pending the full rewrite.

Created `notes/thermal-area-sectors-reorganization.md`: eight central physical insights, a six-section proposed main argument, appendix destinations for derivations and numerical methods, and concrete notation/status/organization repairs. This is an assessment; the full rewrite of the remaining note has not been performed. No new numerical calculation, code change, figure export, manuscript edit or deployment occurred in this documentation step.

Validation: new-document links/anchors, four figure/PDF pairs, retained source-section coverage, and Markdown diff hygiene were checked. Generated edit history remains untouched because the previously recorded database/history backfill is incomplete.

## Remaining thermal-note rewrite — 2026-10-14 16:13:37 IST

Following explicit user authorization, rewrote `notes/thermal-area-sectors.md` around six physical sections: selected squeezed FL state; area/shape and one-copy observables; conservation and closure; exact vacuum Gibbs example; excited-reference occupation/spin results; interpretation and current questions. The main narrative is 262 lines. Seven appendices preserve occupation coefficients/partial trace, angular-momentum conventions and spin counting, both excited-reference methods, convergence/Gibbs diagnostics, the complete single-copy volume baseline, the exploratory nonzero-spin family, and discussion provenance.

All eight original image embeds and their vector PDF links remain: four thermal figures in the main text and four volume figures in Appendix E. All 56 original explicit anchors remain, with unique IDs. Main notation uses $K_{m in},q,A,S,M,	au$ with an explicit mapping to the historical $J,t$ formulas and unchanged saved arrays. Replaced the obsolete proposal list with a current scope/status table; retained originating history through the session links. The separately extracted heating/equilibrium/exchange note remains unchanged.

Updated note index, assessment completion status and T9/T9a records. Local links/anchors, image/PDF assets, math delimiters, control characters and diff whitespace all pass. This is documentation-only: no physics rerun, numerical array change, code change, figure regeneration or manuscript modification. Generated edit history remains preserved under the previously documented incomplete-backfill constraint.

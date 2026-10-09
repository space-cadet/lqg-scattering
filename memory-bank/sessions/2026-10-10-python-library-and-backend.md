---
source_branch: main
source_commit: 379d59288f01cf75ad360de3e667760f56552204
---

# Session summary: Python library structure and backend evaluation

*Created: 2026-10-10 01:14:19 IST*
*Last Updated: 2026-10-10 01:14:19 IST*

This is the continuation and closeout record for the October 9 lattice-Hamiltonian work. The detailed research, numerical, and deployment history is in the [October 9 session summary](2026-10-09-lattice-hamiltonian-session-summary.md); canonical worktree records are in the [T10 closeout](../edits/2026-10-09/111639-t10-catalogue-closeout.md), [T11 pilot](../edits/2026-10-09/114252-t11-hamiltonian-pilot.md), [thermal scan](../edits/2026-10-09/205604-t11-k4-thermal-crossover.md), and [dashboard update](../edits/2026-10-09/215828-t11-dashboard-deployment.md).

## Research results carried forward

- T10 is complete for its stated positive-face $K=2,3,4$ closed-volume RS catalogue. Physical normalization and higher-valence AL orientation data remain outside that completion claim.
- T11's four-site singlet Hamiltonian pilot covers $K=2,3,4$ on complete and ring graphs, with the recorded hopping/interaction controls, thermal observables, connected-triple positive RS volume, and Hamiltonian-volume commutator. The dense $K=4$ scan found a nonmonotonic volume response and a low-temperature finite-size crossover; it does not establish a phase transition.
- The static dashboard catalogue contains 18 saved studies, including T11's 30 cases, and its website copy was live-verified. These results and the deployment evidence remain detailed in the October 9 T11 records.

## Python-versus-TypeScript evaluation

The user decided to continue with Python plus Rust for the research code. The saved comparison is a warm, local, matched $K=2$ benchmark of the T11 singlet workload. Its TS adapter uses `ts-quantum` state-vector, sparse/matrix-operator, Clebsch–Gordan, and eigensystem objects, while LQG-specific occupation enumeration, Schwinger assembly, coupled-basis projection, and T11 orchestration live in the adapter.

For this one saved workload, TS/Python timing ratios were 1.49 for construction, 261 for positive-root evaluation, 529 for the complete pipeline, and 882 for full eigendecomposition. Repeated sparse application was a distinct workload and showed a smaller, still slower TS ratio. Python references cover $K=2,3,4$; only $K=2$ has a saved matched TS artifact. A previous in-memory $K=3$ comparison has no saved output, and the $K=4$ TS run was stopped. These measurements are not a general language ranking. The benchmark, commands, environment, and limits are in [`results/python-vs-ts/README.md`](../../results/python-vs-ts/README.md).

The benchmark exposed a `MatrixOperator.compose` metadata issue for products of noncommuting Hermitian operators. The adapter marked intermediate products as general; this benchmark did not modify `ts-quantum` itself.

## Python library extraction status

Reusable modules now live under `code/python/lqg_scattering/`: conventions, labels, Schwinger and singlet bases, intertwiners, fixed-area and coherent states, spinors, tetrahedra, Grassmannian and Minkowski geometry, correspondence, observables, and volume routines. Root modules for coherent states, positivity, Grassmannian geometry, Minkowski reconstruction, and correspondence now re-export the package implementations for compatibility. Study scripts remain separate entry points.

Extraction is incomplete. The Hamiltonian calculation core remains in `hamiltonian_studies.py`; variable-face volume helpers remain in `variable_n_volume.py`; duplicated thermal or fitting helpers may still merit review. The new package metadata and pinned dependency files have not received a final wheel/build check after the last module move.

Earlier in the work period, 10 extraction tests passed, import smoke checks covered 36 root modules and 15 package modules, and selected T11, FL, and thermal checks passed. Those are historical checks before the extraction stop point. At the user's direction, final testing and build verification are deferred to the next session; no test suite or build was run for this Memory Bank closeout.

## Next work and open research questions

Resume by reviewing ownership of helpers still in the Hamiltonian and variable-face drivers, and identify whether any thermal/fitting routines are genuinely shared before moving them. Finish extraction, then perform one planned validation pass, including package installation/build checks.

Separate physics follow-ups remain open: inspect earlier calculations for quantities evaluated outside singlet subspaces, and evaluate the Hamiltonian on Schwinger-boson configurations representing a closed tetrahedron, a single face, and a three-face tetrahedron with one face missing. Neither the benchmark nor the library extraction answers these questions. T11's larger-system work, optional spin exchange, and physical volume normalization also remain open.

## Subsequent continuation — 2026-10-10 03:26:38 IST

The later session completed the scoped extraction and packaging validation,
then added full-number closure probes, a corrected same-number dissociation
comparison, and small-spin constructive sewing. The earlier incomplete
status above records the original stop point. See [the new handoff](2026-10-10-binding-and-constructive-sewing-summary.md)
and [physics transcript](2026-10-10-binding-and-constructive-sewing-transcript.md).

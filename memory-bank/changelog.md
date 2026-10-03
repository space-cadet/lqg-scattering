# Changelog

## 2026-10-03
- Renamed the T5 roadmap to volume-positivity numerical studies, created shared mathematical preliminaries and a detailed T5c implementation specification, and linked the related implementation notes, task records, manuscript, and shape-scan log. The covariance pilot is explicitly marked exploratory; T5c remains open.
- Evaluated positive RS/AL volumes for strictly positive and off-cell real-plane states under T1b; added a reproducible driver and result JSON.
- Applied a shared scale-aware zero-mode cutoff to Python and Rust spectral volume expectations, reran the $J=1\ldots5$ FL sweep and 440-point $J=2$ shape scan, and matched the Rust FL example to Python.
- Recorded the $J=2$ FL equal-face-area scan of 440 ordered samples. Both sampled RS and AL minima occur at the regular tetrahedron; the Memory Bank states clearly that this is a finite-grid observation, not a global-minimum proof.
- Added the shape-scan method, numerical ranges, two independent tensor-product checks, selected classical-volume comparisons, and open boundary/fluctuation questions to `fl_volume_shape_scan_log.md` and the volume-operator notes.
- Updated the website dashboard so representative tetrahedron thumbnails appear beside both RS and AL panels. Final website commit `f0b6fdd` was deployed by workflow `37033479554`; the live HTML and cache-busted SVG returned HTTP 200.
- Recorded the $J=2$ strict positive face-spin assignment result (one assignment, two recoupling channels) and planned boundary scaling and shape sampling across unequal allowed assignments.
- Added reusable T5c input and covariance tetrahedron previews, reused saved input thumbnails in the T1a shape figure, and deployed the visual update at website commit `9c6670c` (workflow `37125090987`). T5c remains open; the preview does not validate the state-to-geometry map.

## 2026-10-01
- Added exact small-sector Rovelli–Smolin and Ashtekar–Lewandowski positive vertex-volume expectations in Python and Rust, with singlet and collinear controls independently checked. Physical normalization and large-sector evaluation remain open.
- Used the host Rust toolchain to pass 20 release tests and rerun converged `verify4` and n=5..8 `scan`; corrected manuscript, dashboard and benchmark values. Independent SciPy checks agree at n=4,5,7,8; n=6 remains open.
- Continued the red-team audit: distinguished zero signed mean from positive
  quantum volume; found a real off-cell zero and shared Taylor truncation in
  the historical baseline comparison.
- Reclassified T3d/T3e complex-plane values as needing converged reruns,
  corrected the manuscript/dashboard/roadmap, and made Rust state
  construction fail when its Taylor cap is reached.
- Reran T5b with converged Python states, saved corrected n=4/5 result
  values, and independently checked four n=4 points with SciPy.
- Reran T5a magnetization states to convergence; its fixed-plane sign
  pattern persisted and four sectors matched independent SciPy states.
- Updated project goals and current T4, T5, and T7 status to match the recorded experiments.
- Corrected the manuscript's T5a caveat, classical-limit summary, and TFD scope.
- Updated the TFD specification and experiment roadmap with completed results and remaining work.

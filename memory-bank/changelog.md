# Changelog

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

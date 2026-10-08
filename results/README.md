# Calculation results

This directory holds saved JSON outputs from the project's numerical runs.
Run records retain their task prefixes so they can be matched to the relevant
experiment notes and Memory Bank records.

- **T1:** [FL area sweep](fl_volume_area_results.json),
  [real-plane volume check](t1b_real_plane_volume_results.json), and
  [volume prescription check](volume_prescription_results.json).
- **T5:** [magnetization](t5a_mag_results.json),
  [local chirality](t5a_prime_results.json), [perturbation](t5b_results.json),
  [covariance pilot](t5c_covariance_probe_results.json),
  [input geometry](t5c_input_geometry_results.json),
  [shape recovery](t5c_shape_recovery_results.json),
  [unequal-area scan](t5c_weighted_shape_results.json),
  [selected $J=6$ points](t5c_weighted_shape_j6_results.json),
  [flat-boundary scan](t5c_degenerate_limits_results.json),
  [higher-$J$ boundary scan](t5c_degenerate_limits_highJ_results.json),
  [phase scan](t5d_phase_scan_results.json), and
  [large-$K$ fit](t5e_results.json).
- **T7 child studies:** [single-copy thermal state](t7a_results.json),
  [TFD](t7b_results.json), and
  [small-sector geometry audit](t7_geometry_thermal_results.json),
  [complexified TFD](t7e_results.json).

The Python and Rust drivers write their default outputs here. T5e raw sweep
inputs also belong here; `code/tools/run_t5e.sh` creates them before fitting.

Use the relevant task record in `memory-bank/tasks/` or experiment note in
`notes/experiments/` to find the calculation method, interpretation, and
limitations for each file.

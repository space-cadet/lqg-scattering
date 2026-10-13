# T11: geometric diagnostics and persistence

*Created: 2026-10-11 10:27:17 IST*

## Implemented support

`code/python/lqg_scattering/geometric_diagnostics.py` supplies face-spin moments, assignment/active-face probabilities, pair-dot and assignment-normalized angular operators, symmetrized covariance, volume distributions, signed-grasp moments and coherent projector conditioning. Drivers retain preparation, sampling, plotting and output. Conditioning is $P\rho P/\operatorname{Tr}(P\rho)$, with selection probabilities retained. Degenerate energy groups use uniform mixtures.

Five FL references use existing normalized $(F_z^\dagger)^4|0\rangle$ preparation, closure and the recorded spinors. They are distinct from energy eigenstates and Gibbs states. The equal-spin assignment has three shared-$k$ singlets. All 105 full-space dimensions and the 51 four-active-face dimensions are retained in their appropriate readouts.

## Artifacts and verification

- `results/t11-size-comparison/`: protocol, summary/thermal/energy CSVs, operators, validation, independent checks, provenance/hashes, report and PDF/PNG. Drivers: `t11_size_comparison.py`, `verify_t11_size_comparison.py`, `plot_t11_size_comparison.py`.
- `results/t11-geometric-interpretation/`: state summaries/details, reference inputs, pair/area/volume/overlap CSVs, thermal reconstruction, provenance/hashes, operator/control checks, report and PDF/PNG. Drivers: `t11_geometric_interpretation.py`, `verify_t11_geometric_interpretation.py`, `plot_t11_geometric_interpretation.py`; analytic tests: `test_geometric_diagnostics.py`.
- Previous suite progression: 38 then 42 tests. Largest geometric independent residual $5.14\times10^{-12}$, tolerance $2\times10^{-10}$. Shared singlet basis remains part of the independent-control scope; no new Rust run.

## Pending physics

Prepared-$K=4$ evolution is not implemented. Positive-volume and signed-triple couplings are discussed, not added. Use $g_V$ for the new volume proposal to distinguish it from historical spin-exchange $g$. Existing data remains $g=0$. For interpretation and original wording see [Hamiltonian dialogs](../../notes/hamiltonian-studies.md) and [closeout](../sessions/2026-10-11-t11-geometry-closeout.md).

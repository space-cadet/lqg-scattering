# Channel-count equilibration pilot

Adding channels does not by itself produce equilibration in the tested uniform complete graph. Onsite repulsion suppresses the free oscillations and increases residence near the exact long-time reference for many settings. The dependence on channel count is interaction- and preparation-dependent. This is a finite, small-area dynamical result, not evidence of thermalization in a large system.

## Frozen protocol

T11 owns this single-polyhedron dynamics study. Geometry reconstruction is excluded. The saved protocol precedes each run; no random sampling or seed is used. Units have hbar=1.

$$H=-\frac{1}{L-1}\sum_{i<j}(E_{ij}+E_{ji})+\frac U2\sum_i n_i(n_i-1).$$

The hopping row sum stays fixed when channels are added. Thus this differs from the previous unit-per-edge free control. The pilot covers K=2 with L=4,5,6,7 and K=3 with L=4,5,6, each at U=0,1,5. Two normalized regular FL inputs differ by spinor phases exp(i pi i/2) on the first four labels. Extra spinors are zero. An FL input has fluctuating occupations: four nonzero input labels do not mean four sharply occupied faces. Phase choices generally have different conserved energies, so their difference is not a same-energy test of persistent memory.

## Reference and distance

The primary reference is the exact dephased state rho_bar=sum_E P_E rho(0) P_E. Coherences within degenerate eigenspaces are retained; this reference automatically respects all conserved quantities. It is an infinite-time average, not an assumption that observables approach it.

The bounded readouts are concentration Q=sum_i n_i^2/(2K)^2, total area fraction in channels i>=4, and the complete probability distribution of occupied-channel count. The distance is the maximum of the two absolute scalar deviations and the total-variation distance of the occupied-count distribution from their dephased references. This is a distance between selected readouts, not a full quantum-state distance. Residence is the sampled fraction with distance <=0.05. Thresholds 0.02 and 0.1 are also saved.

Times are 0..200 at spacing 0.1. Statistics use [20,100] and [20,200]; t=20 is an explicitly chosen exclusion interval, not a measured relaxation time. Reported residence fractions are finite-grid estimates. No asymptotic residence or equilibration time is inferred.

An energy-matched canonical ensemble in the full fixed-K singlet space is saved separately, allowing negative beta for the bounded spectrum. Permutation-sector weights are not matched. Consequently canonical disagreement cannot distinguish failed thermalization from omitted conserved constraints.

## Results

Regular input, K=3, window [20,200]; percentage of samples within distance 0.05 of the exact long-time reference:

| Channels | U=0 | U=1 | U=5 |
|---|---:|---:|---:|
| 4 | 19.0% | 66.8% | 76.1% |
| 5 | 0.0% | 50.3% | 76.7% |
| 6 | 0.0% | 50.1% | 90.3% |

For U=5, the same fractions in [20,100] are 76.2%, 70.5%, and 84.1%. The increasing late-window residence at six channels is promising, but the dependence on observation window must remain visible. At threshold 0.02 the [20,200] fractions are only 36.7%, 20.9%, and 31.3%; the quantitative conclusion depends on the stated tolerance. At U=1 the default-threshold fractions decrease with channel count.

For the phase-shifted K=3 input, U=5 gives 91.6%, 99.1%, and 87.6% residence: the monotonic channel trend does not survive this preparation change. Because energy changes too, these are preparation/energy controls, not matched-energy comparisons.

The maximum post-t=20 return probability for the regular K=3,U=5 state drops from 0.753 to 0.433 to 0.198 across L=4,5,6. The free controls return almost exactly. A reduced return probability and near-reference readouts are separate observations; neither establishes a canonical state.

At K=3,U=5, the active-count total-variation difference between the dephased and energy-matched full canonical references grows from 0.018 to 0.106 to 0.154. These benchmarks are not interchangeable, and the canonical symmetry caveat above is material.

At K=2 there are only four bosons, so more than four channels can never be occupied simultaneously. K=3 permits up to six. The K=2 sweep is a channel-availability/dilution control; it cannot establish simultaneous activation beyond four. The pilot has not settled behavior at large initial face areas.

## Verification and reproducibility

All 42 runs passed Gram, singlet closure, hopping leakage, initial-state projection, eigensystem, norm, and energy checks. Every run was independently propagated in the larger magnetic occupation space at t=0.37 and 7.3 using sparse exponential action. The maximum recorded internal/propagation residual is 9.41e-14 against tolerance 2e-9.

Independent verification additionally compares free readouts with analytic U(L) spinor evolution and FL marginal formulas, and checks saved active-count probability normalization, nonnegativity and occupation bounds. It passed 252,840 comparisons, including 714 analytic comparisons; maximum residual 1.88e-13. All 46 existing regression tests passed.

Run from the repository root with the scientific Python interpreter and OPENBLAS_NUM_THREADS=1, PYTHONPATH=code/python: first code/python/t11_equilibration.py, then code/python/verify_t11_equilibration.py. The full-resolution time series stays local and is ignored by Git; compact summaries and selected figures are included in the published dashboard package.

Files: protocol.json; summary.csv (both windows, fluctuations in readout distance, returns and threshold sensitivity); references.csv; validation.json; independent-validation.json; provenance.json; sha256.json. The full-resolution `dynamics.csv` (84,042 samples) is generated locally and ignored by Git because of its size. Observable indices in references.csv are 0=concentration, 1=extra-area fraction, 2+m=probability of m occupied channels.

## Next calculation

Test whether the result survives weaker graph symmetry and same-energy preparations before increasing initial area. A comparison between the complete graph and a specified less-symmetric hopping graph should retain the hopping normalization, fixed-area input and readouts. Longer windows and finer time sampling are needed for quantitative residence convergence. A symmetry-resolved thermal comparison and entanglement growth remain unperformed.

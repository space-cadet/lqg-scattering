# Exact geometric-channel area redistribution

54 sparse exact-singlet trajectories, October 16, 2026. See the [pedagogical account](../../notes/geometric-area-redistribution.md) and [protocol](protocol.md).

## Model and preparations

K=4 (Nb=8), L=4,6,8; rings and complete graphs with equal hopping row sum one. H=alpha sum Ji² - sum_edges w(Eij+Eji), alpha=0,1,5. Ring w=1/2, complete w=1/(L-1). hbar=1. Times 0..20 inclusive, 101 samples. Closure and linear area are exact; sum sqrt(ji(ji+1)) is not the conserved area.

Regular and phi=30-degree deformed FL labels use x=1/sqrt(3). The main preparations condition on local counts (2,2,2,2,0,...), giving exactly four occupied spin-one channels. Conditioning probabilities are 0.06944444444 and 0.08083767361. A third, unconditioned regular FL preparation is a separate fluctuating-occupation control, not an exact-four-active state.

## Eight-channel regular sharp results

| Graph | Casimir coupling $\alpha$ | Area in receivers | Probability of at least five occupied channels |
|---|---:|---:|---:|
| Ring | 0 | 53.0% | 56.8% |
| Ring | 1 | 50.6% | 68.1% |
| Ring | 5 | 25.3% | 30.9% |
| Complete | 0 | 12.4% | 42.0% |
| Complete | 1 | 34.6% | 67.6% |
| Complete | 5 | 12.7% | 20.6% |

Equal-weight means over saved times 10..20. Receiver area is divided by conserved K. These summaries describe finite evolution, not equilibrium. Ring alpha=1 puts about half the area into the initially empty four channels, with about 68% probability for at least five active channels. Alpha=5 reduces transfer over this window. Complete-graph behavior is different and is not monotonically related to the ring or coupling.

All-eight occupation is rare: ring alpha=1 has maximum probability about 0.00341 and late mean about 0.00137 for the regular sharp state. Complete-graph regular sharp all-eight probability is numerical zero for all three couplings. Deformed sharp and unconditioned FL preparations have nonzero all-eight weight on that same graph. This is a state-specific symmetry restriction, not numerical failure or universal inability to reach eight channels.

The post-run symmetry check was added after inspecting these outputs. It shows that the regular sharp source has no original-group symmetric component, while initially empty receivers are symmetric. In the all-eight singlet subspace, receiver permutation symmetry implies original-group symmetry. Complete H commutes with each group's permutations, forbidding all-eight weight for that source. This diagnostic was not a predeclared scan criterion; it does not alter or select the primary cases.

Symmetry check: regular original-group symmetric weight 1.06e-32; deformed weight 0.348993; target implication residual 2.95e-17. See symmetry-control.json.

## Geometric readouts

At t=0,2,5,10,20 save all conditional pair-angle means/SDs with pair-presence probabilities; positive RS volume mean/SD and kernel probability; and volume conditioned on >=5 occupied channels. Angle normalization is inside each local-spin block, followed by conditioning on pair presence. No division of mean flux dots by mean spins. Singlet mean fluxes vanish and are not used as classical normals.

RS uses all unordered triples independently of the interaction graph, gamma=0.2375 in project units. This differs from earlier T11 connected-induced-triple graph conventions. No four-valent geometric calibration is applied at higher valence. All sampled >=5 components with probability above the conditioning tolerance have positive conditional mean volume; the minimum saved value is approximately 0.69472 in project units. Distinct normals, a unique reconstructed polyhedron and semiclassical sharpness remain unverified.

Single-channel entropy uses -sum_n p(n) log[p(n)/(n+1)], including spin multiplicity from exact SU(2) invariance. Initially occupied sharp spin-one channels have entropy log(3), empty channels zero. No dense density matrices are constructed. Local total energy uses equal half-bond allocation and sums to H; receiver Casimir and receiver local total energy are separate saved quantities.

## Validation

All 73 regression tests pass. Production operator and trajectory checks have maximum residual 6.43e-12. An independent saved-observable audit checks 91,476 quantities, including all 606 free-FL frames against analytic spinor evolution; its maximum residual is 6.43e-12. Selected interacting states also agree with magnetic-space propagation. Small-system tests independently check the full-space Hamiltonian projection, a known four-spin-half RS volume, local energy partition, and single-channel entropy by an explicit partial trace.

The geometric operator is block diagonal in definite local occupation. Matrix-function roots use the repository's zero-mode prescription. The small-system tests verify a known RS eigenvalue for four spin-half faces, vanishing closed <=3-active volume, positivity and the flux-dot closure identity. The saved audit verifies probability bounds and conditional consistency; it is not an external scientific review.

## Sparse implementation and retained data

The global Hamiltonian, basis embedding and geometry operators are sparse; expm_multiply avoids a dense propagator. Dense spectral work is limited to local-spin blocks. The L=8 basis has 13,860 singlets embedded in 108,900 M=0 occupations, avoiding the 490,314-state full Fock basis. Cached Clebsch-Gordan coefficients accelerate construction. One run's state history is transient and released; no trajectory vectors or large intermediate operators are retained.

- L=4: basis and geometry construction 0.14 seconds, magnetic dimension 1225, singlet dimension 105.
- L=6: basis and geometry construction 0.55 seconds, magnetic dimension 15876, singlet dimension 1764.
- L=8: basis and geometry construction 4.22 seconds, magnetic dimension 108900, singlet dimension 13860.

Timings are local warm-process measurements, not general benchmarks. Final numerical outputs are about 5.6 MB, with less than 1 MB of PDF/PNG figures. No file approaches the user's 200-500 MB temporary-data threshold.

- summary.csv: 54 run/window summaries.
- dynamics.csv: 5,454 time rows with local area, Casimir, entropy, full local energy, occupied-count probabilities, returns and conservation checks.
- geometry.json: 270 geometric samples and all pair diagnostics.
- inputs.json: spinor labels, initial sparse singlet coefficients/counts and projection weights. Basis ordering is reproducible from channel_dynamics.build_basis.
- validation.json, independent-validation.json, symmetry-control.json: primary, analytic/saved-data and post-run selection-rule checks.
- performance.json, provenance.json, postprocessing-provenance.json: timings and source SHA256 hashes.

Reproduce from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 code/python/t11_geometric_redistribution.py
python3 code/python/verify_t11_geometric_redistribution.py
OPENBLAS_NUM_THREADS=1 python3 code/python/check_t11_channel_symmetry.py
python3 -m unittest discover -s code/python -p 'test_*.py'
python3 code/python/plot_t11_geometric_redistribution.py
```

Dependencies: existing NumPy/SciPy/SymPy; plotting additionally uses Matplotlib. Vector PDF and 300-dpi PNG figures are in figures/t11-geometric-redistribution. No dashboard changes, commit or publication are included.

## Remaining questions

Larger K, longer times and an explicitly justified equilibrium comparison remain open. Activated nonzero-spin channels with positive RS volume are quantum geometric evidence, but not verification of distinct semiclassical face normals or of a unique higher-faced classical polyhedron. Closure-preserving dynamics does not turn a nonclosed state into a singlet. No thermodynamic or permanent-localization conclusion is made.

# Numerical studies: chronological research record

*Last updated: 2026-10-16*

This is the central record of numerical studies in this repository. Each entry records the question, calculated coverage, findings, and source artifacts. Dates follow calculation records, session records, and Git history. Date ranges group related calculations; corrections and extensions appear at their own dates. The identifiers NS01–NS40 are local index labels for this document. Project task IDs are included for cross-reference.

[Research map](quantum-geometry-research.md) · [Project notes](README.md).

## Index

| Entry | Calculation date | Study | Project reference |
|---|---|---|---|
| [NS01](#ns01) | 2026-09-19 | Python state, geometry, and positivity pipeline | T1, T6 |
| [NS02](#ns02) | 2026-09-19 | Rust implementation and four-to-eight-face calculations | T3a–T3e |
| [NS03](#ns03) | 2026-09-19 | Triple chirality across complex planes | T5a |
| [NS04](#ns04) | 2026-09-19 | Kinematic-polyhedron local chirality | T5a′ |
| [NS05](#ns05) | 2026-09-19–20 | Large-area signed-flux families | T5e |
| [NS06](#ns06) | 2026-09-20 | Single-copy oscillator thermal states | T7a |
| [NS07](#ns07) | 2026-09-20 | Gibbs purification, two-sided correlations, thermal scaling | T7b–T7d |
| [NS08](#ns08) | 2026-09-21 | Complexified coherent purification | T7e |
| [NS09](#ns09) | 2026-10-01 | Converged magnetization sweep | T5a |
| [NS10](#ns10) | 2026-10-01 | Converged imaginary-perturbation response | T5b |
| [NS11](#ns11) | 2026-10-01–03 | Positive RS/AL volume controls and implementation checks | T1a, T3c |
| [NS12](#ns12) | 2026-10-01–03 | FL regular-area sweep and equal-area shape scan | T1a |
| [NS13](#ns13) | 2026-10-03 | Positive volume on real planes | T1b |
| [NS14](#ns14) | 2026-10-03–06 | Flux-covariance geometry and shape recovery | T5c, T6 |
| [NS15](#ns15) | 2026-10-05 | Weighted FL input geometry and unequal-area volumes | T5c |
| [NS16](#ns16) | 2026-10-05–06 | Flat-boundary and higher-area volume probes | T5c |
| [NS17](#ns17) | 2026-10-06 | Gauge-invariant phase-response pilot | T5d |
| [NS18](#ns18) | 2026-10-06 | Small-sector squeezed-FL geometry audit | T9 |
| [NS19](#ns19) | 2026-10-08 | Squeezed-vacuum occupation and spin distributions | T9 |
| [NS20](#ns20) | 2026-10-08 | Excited-input joint occupation and spin distribution | T9 |
| [NS21](#ns21) | 2026-10-08 | Complete four-face closed-basis volume catalogue | T1a |
| [NS22](#ns22) | 2026-10-08–09 | Variable-face positive-volume catalogue | T10 |
| [NS23](#ns23) | 2026-10-09 | Four-site Hamiltonian spectra and thermal volumes | T11a |
| [NS24](#ns24) | 2026-10-09–10 | Open-state evolution and same-number detachment energies | T11a |
| [NS25](#ns25) | 2026-10-09–10 | Triangle, tetrahedron, and joined-boundary sewing | Constructive sewing |
| [NS26](#ns26) | 2026-10-10 | Four/five-site comparison and prepared-FL diagnostics | T11a |
| [NS27](#ns27) | 2026-10-11 | Geometric interactions and prepared-FL evolution | T11a |
| [NS28](#ns28) | 2026-10-13 | Temperature dependence of ordinary per-copy closure | T9 |
| [NS29](#ns29) | 2026-10-13 | Separately closed projection and thermal geometric growth | T9 |
| [NS30](#ns30) | 2026-10-14 | Finite-area singlet exchange and canonical controls | T9a |
| [NS31](#ns31) | 2026-10-16 | Closed-reference entanglement and coherent singlet creation | T9 |
| [NS32](#ns32) | 2026-10-16 | Large-area FL face activation and free-hopping recurrence | T11b |
| [NS33](#ns33) | 2026-10-16 | Small-area face-channel equilibration pilot | T11b |
| [NS34](#ns34) | 2026-10-16 | Classical rotor energy spreading and equilibrium comparison | T11c |
| [NS35](#ns35) | 2026-10-16 | Few-rotor energy transfer and the planar threshold | T11c |
| [NS36](#ns36) | 2026-10-16 | Rotor coupling crossover and delayed release | T11c |
| [NS37](#ns37) | 2026-10-16 | Four quantum planar rotors at zero total momentum | T11c |
| [NS38](#ns38) | 2026-10-16 | Closed/nonclosed four-to-five-to-six channel connectivity | T11d |
| [NS39](#ns39) | 2026-10-16 | Sparse geometric redistribution across four, six and eight channels | T11d |
| [NS40](#ns40) | 2026-10-16 | Complete-graph permutation selection for all-eight occupation | T11d |

## Notation

Each face/site carries two Schwinger modes. Its spin is $j_i=(n_{a,i}+n_{b,i})/2$. Newer studies write total linear area as $K=\sum_i j_i$; older FL studies use $J$ for the same area label. $L$ counts available sites and $N$ counts occupied faces. Closure selects total spin zero.

The signed triple flux is $q_{ijk}=\mathbf J_i\cdot(\mathbf J_j\times\mathbf J_k)$. Early studies calculate its mean and the proxy $\gamma^{3/2}\sqrt{|\langle q\rangle|}$. Positive-volume studies instead evaluate spectral operator roots: RS sums $\sqrt{|q_{ijk}|}$, while AL applies the root to an orientation-signed triple sum. The observable used is specified in each entry.

## 2026-09-19–21: state construction, chirality, and oscillator thermal studies

<a id="ns01"></a>
### NS01 — Python state, geometry, and positivity pipeline

**Question:** How can the LQG–Grassmannian correspondence be calculated explicitly?

**Calculation:** Built Schwinger Fock bases, sparse spin and $U(N)$ operators, Perelomov coherent states, Plücker coordinates, positivity tests, and geometry/kinematics conversion routines. Initial numerical calculations used four faces. Minkowski routines reconstruct polyhedra from closing face data.

**Findings:** Real-plane states have vanishing signed triple means. The pipeline supplies explicit state vectors and geometric coordinates for subsequent experiments.

**Sources:** [Python code](../code/python/), [shared package](../code/python/lqg_scattering/), [T1 record](../memory-bank/archive/T1.md), [T6 record](../memory-bank/tasks/T6.md).

<a id="ns02"></a>
### NS02 — Rust implementation and four-to-eight-face calculations

**Question:** How far can the coherent-state and signed-flux calculations be extended?

**Calculation:** Implemented Rust Fock-space enumeration, sparse $U(N)$ actions, coherent states, Grassmannian coordinates, and triple-flux evaluation. Calculated four-face comparisons and five-to-eight-face runs. Subsequent convergence repairs and SciPy comparisons supply the corrected values.

**Findings:** The corrected canonical complex four-face state gives $\langle q\rangle=-0.000827687168$. Independent SciPy checks cover selected $n=4,5,7,8$ cases. The Rust on-the-fly engine supports larger occupation spaces without storing every operator.

**Sources:** [Rust code](../code/rust/), [numerical dashboard run records](../code/dashboard/data.json), [T3e record](../memory-bank/tasks/T3e.md), [local-chirality validation notes](experiments/t5a_prime_notes.md).

<a id="ns03"></a>
### NS03 — Triple chirality across complex planes

**Question:** Do the signed triple means align into a common vertex handedness?

**Calculation:** Compared triple means across complex-plane seeds at six and seven faces, recording sign agreement and cross-seed correlations.

**Findings:** Recorded sign agreement lies around 0.50–0.70, with small cross-seed correlations. Different triples carry different orientation signals.

**Sources:** [T5a record](../memory-bank/archive/T5a.md), [study overview](../memory-bank/implementation-details/volume-positivity-studies.md), [dashboard run records](../code/dashboard/data.json).

<a id="ns04"></a>
### NS04 — Kinematic-polyhedron local chirality

**Question:** Does choosing adjacent triples reveal coherent handedness?

**Calculation:** Generated conserved two-to-two and two-to-three kinematics, constructed the associated spinor planes and face geometry, then compared local and all-triple sign agreement. Four-face runs cover three channels; five-face runs cover ten incoming-pair channels with eight planes per channel.

**Findings:** Channel-averaged five-face agreement is approximately 0.589 for all triples and 0.594 for local triples. Four-face channels give 0.500. Selecting adjacent triples leaves the orientation mixture essentially unchanged. Independent exponentiation in this study exposed the earlier short-Taylor state construction.

**Artifacts:** [Driver](../code/python/t5a_prime.py), [results](../results/t5a_prime_results.json), [experiment notes](experiments/t5a_prime_notes.md).

<a id="ns05"></a>
### NS05 — Large-area signed-flux families

**Question:** How does the signed-mean proxy grow when occupations increase?

**Calculation:** Used converged Rust on-the-fly states for a vertex-loaded family through $K=22$ and balanced families through $K=24$. Saved iteration counts, fits, and cross-engine controls.

**Findings:** Vertex loading gives signed flux linear in the loading parameter and proxy growth proportional to $(K-4)^{1/2}$. Balanced-family signed means remain near numerical zero. The fitted response differs from the proposed $K^{3/2}$ growth.

**Artifacts:** [Results](../results/t5e_results.json), [fit code](../code/python/t5e_fit.py), [experiment notes](experiments/t5e_notes.md).

<a id="ns06"></a>
### NS06 — Single-copy oscillator thermal states

**Question:** How do area and triple-flux fluctuations change with temperature?

**Calculation:** Evaluated capped oscillator Gibbs ensembles for four and five faces over seven inverse temperatures, alongside Perelomov-weighted and pure-state comparisons. Measured face areas, entropy, $\langle q\rangle$, and $\langle q^2\rangle$.

**Findings:** Signed means vanish while flux fluctuations remain nonzero. Gibbs area, entropy, and fluctuations decrease toward the vacuum during cooling. Fixed-number coherent comparisons are temperature-independent because their occupation energy is constant across the state support.

**Artifacts:** [Driver](../code/python/t7a_thermal.py), [results](../results/t7a_results.json), [experiment notes](experiments/t7a_notes.md).

<a id="ns07"></a>
### NS07 — Gibbs purification, two-sided correlations, and thermal scaling

**Question:** Does a two-copy purification reproduce the Gibbs ensemble, and what do its cross-copy correlations measure?

**Calculation:** Constructed four- and five-face thermofield doubles in Schmidt form. Compared the left marginal, entropy, areas, and fluctuations with NS06. Evaluated two-sided chirality correlations and their temperature dependence.

**Findings:** The left marginal reproduces the Gibbs state and entanglement entropy matches thermal entropy. The low-temperature state approaches the vacuum product. With the same occupation-basis $q$ matrix on both copies, $\langle q_Lq_R\rangle=-\operatorname{Tr}(\rho_\beta q^2)$. The low-temperature signal behaves approximately as $e^{-3\beta}$.

**Artifacts:** [Driver](../code/python/t7b_tfd.py), [results](../results/t7b_results.json), [experiment notes](experiments/t7b_notes.md).

<a id="ns08"></a>
### NS08 — Complexified coherent purification

**Question:** How does complexifying the coherent input affect a two-copy correlator?

**Calculation:** Swept imaginary perturbations from $10^{-6}$ to 1 for four and five faces, preserving coherent amplitudes in a fixed-number purification. Checked conjugation and measured signed means, fluctuations, and cross-copy correlations.

**Findings:** The signed mean grows approximately linearly in perturbation strength. Changes in the two-copy correlator grow approximately quadratically. The fixed-number construction remains temperature-independent; conjugating the input amplitudes leaves the tested correlator unchanged.

**Artifacts:** [Driver](../code/python/t7e_complex_tfd.py), [results](../results/t7e_results.json), [experiment notes](experiments/t7e_notes.md).

## 2026-10-01–03: converged reruns and positive quantum volume

<a id="ns09"></a>
### NS09 — Converged magnetization sweep

**Question:** Does boson-species imbalance align the signs of triple fluxes?

**Calculation:** Reran the five-face, $K=8$ fixed-plane sweep over magnetizations $M=-4,\ldots,4$, including spread and concentrated $M=0$ references. States converged in 39–41 Taylor terms; four sectors were checked with independent SciPy exponentiation.

**Findings:** Nonpolarized sectors have sign agreement 0.50–0.60. Fully polarized endpoints have vanishing triple flux. Magnetization changes the magnitudes and relative strength of individual triples while the signs remain mixed. Independent triple-mean differences are at most $3.6\times10^{-16}$.

**Artifacts:** [Driver](../code/python/t5a_mag_sweep.py), [results](../results/t5a_mag_results.json), [experiment notes](experiments/t5a_mag_notes.md).

<a id="ns10"></a>
### NS10 — Converged imaginary-perturbation response

**Question:** How does the signed-mean proxy turn on away from a real plane?

**Calculation:** Corrected the four- and five-face perturbation sweep with convergence assertions and independent SciPy spot checks, covering $\epsilon=10^{-6},\ldots,1$.

**Findings:** The signed mean has approximately linear onset; the proxy $\sqrt{|\langle q\rangle|}$ has exponent near one half. The corrected results supersede the initial September 19 sweep.

**Artifacts:** [Driver](../code/python/t5b_perturbation.py), [results](../results/t5b_results.json), [T5b record](../memory-bank/archive/T5b.md).

<a id="ns11"></a>
### NS11 — Positive RS/AL volume controls and implementation checks

**Question:** How do signed cancellation and positive volume compare on explicit quantum states?

**Calculation:** Implemented spectral RS/AL roots in Python and Rust, with a shared scale-aware zero-mode cutoff. Built independent local-spin tensor operators for paired spin-half singlets and collinear product controls.

**Findings:** The paired singlet has positive RS/AL volume despite zero signed mean; the collinear control gives zero. Python and Rust reproduce the fixed-area FL $J=2$ values after applying the shared cutoff.

**Artifacts:** [Control driver](../code/python/volume_prescription_demo.py), [results](../results/volume_prescription_results.json), [tensor validation](../code/python/fl_volume_validation.py), [operator definitions](../memory-bank/implementation-details/volume-operator.md).

<a id="ns12"></a>
### NS12 — FL regular-area sweep and equal-area shape scan

**Question:** How does positive volume depend on total area and tetrahedral shape?

**Calculation:** Evaluated the regular FL tetrahedron at $J=1,\ldots,5$, followed by 440 ordered equal-area shape samples at $J=2$. Calculated RS/AL means and checked selected shapes with direct tensor operators.

**Findings:** The regular tetrahedron is the minimum in the sampled shape grid for both prescriptions. Direct-tensor area-sweep expectations agree within $1.67\times10^{-16}$. Shape is tracked using face normals, bending coordinates, and spinor cross-ratios.

**Artifacts:** [Area driver](../code/python/fl_volume_validation.py), [area results](../results/fl_volume_area_results.json), [shape driver](../code/python/fl_volume_shape_scan.py), [shape data](../code/dashboard/fl-volume-shape-j2.json), [scan log](experiments/fl_volume_shape_scan_log.md).

<a id="ns13"></a>
### NS13 — Positive volume on real planes

**Question:** What positive volume do real-plane states carry inside and outside the positive cell?

**Calculation:** Evaluated two four-face, $K=6$ Perelomov states using RS and AL, with independent operator checks.

**Findings:** Both states have zero signed mean and nonzero positive volume. The calculation separates real-plane signed cancellation from the positive-volume spectrum.

**Artifacts:** [Driver](../code/python/real_plane_volume.py), [results](../results/t1b_real_plane_volume_results.json).

## 2026-10-03–06: classical geometry comparisons and squeezed-state pilots

<a id="ns14"></a>
### NS14 — Flux-covariance geometry and shape recovery

**Question:** How closely do quantum flux correlations recover the tetrahedral input?

**Calculation:** Formed flux Gram matrices, normalized pair correlations, and candidate classical face data. The first six-record pilot compared two shapes at $J=1,2,3$. Extended scans cover five interior shapes and three boundary-approach families through $J=6$, with positive-volume comparisons at $J=1,2,3$.

**Findings:** Regular-shape normalized correlations reproduce the input Gram matrix. Other shapes show area-dependent corrections, with the recorded interpolation matching the FL correlation relation. Reconstructed covariance geometry, input classical volume, signed proxy, and positive volume are saved as separate readouts.

**Artifacts:** [Pilot](../results/t5c_covariance_probe_results.json), [shape-recovery driver](../code/python/t5c_shape_recovery_scan.py), [shape-recovery results](../results/t5c_shape_recovery_results.json), [comparison write-up](../memory-bank/implementation-details/T5c-flux-covariance-volume-comparison.md).

<a id="ns15"></a>
### NS15 — Weighted FL input geometry and unequal-area volumes

**Question:** How does positive quantum volume compare with the classical tetrahedron used to prepare the state?

**Calculation:** Started from explicit vertices and face-area vectors, constructed weighted spinors, and evaluated regular and unequal-skew inputs through $J=7$. Added a nine-shape unequal-area grid at $J=2,4$ and four selected points at $J=6$. Saved mean areas, angular correlations, volume fluctuations, cross-ratios, and classical targets.

**Findings:** At $J=7$, geometry-matched quantum/classical volume ratios are 0.953 for the regular input and 0.904 for the unequal-skew input. Grid ratios span 0.325–0.529 at $J=2$, 0.726–1.020 at $J=4$, and 0.881–1.034 for the selected $J=6$ points. Mean face areas reproduce the weighted inputs. The unequal-skew normalized correlation error is 0.0584 at $J=7$.

**Artifacts:** [Input driver](../code/python/t5c_input_geometry_scan.py), [input results](../results/t5c_input_geometry_results.json), [grid driver](../code/python/t5c_weighted_shape_scan.py), [grid results](../results/t5c_weighted_shape_results.json), [selected J=6 results](../results/t5c_weighted_shape_j6_results.json).

<a id="ns16"></a>
### NS16 — Flat-boundary and higher-area volume probes

**Question:** What happens to positive volume as the classical tetrahedron becomes flat?

**Calculation:** Held the equal-area diagonal coordinate fixed and reduced the bending angle to zero. Initial samples cover $J=2,4,6,7$; later Python points reach $J=10$, with Rust flat, near-flat, and regular controls at $J=10$.

**Findings:** The exact flat input has positive mean quantum volume. Its geometry-matched mean divided by $J^{3/2}$ is approximately 0.00247, 0.00461, 0.00418, and 0.00398 at $J=2,4,6,7$, then decreases slowly in the higher-area samples. At the $J=10$ flat point, Python/Rust AL agrees within $4\times10^{-17}$; the RS difference is approximately $4.4\times10^{-10}$. The recorded Rust $J=11$ attempt produced no result.

**Artifacts:** [Driver](../code/python/t5c_degenerate_limits_scan.py), [initial results](../results/t5c_degenerate_limits_results.json), [higher-area results](../results/t5c_degenerate_limits_highJ_results.json), [Rust scan](../code/rust/examples/fl_volume_scan.rs).

<a id="ns17"></a>
### NS17 — Gauge-invariant phase-response pilot

**Question:** How does signed triple flux respond to a phase defect in the Plücker coordinates?

**Calculation:** Evaluated ten four-face, $K=7$ points using the Rust on-the-fly engine. Tracked the phase of a Plücker cross-ratio and its defect $|\sin\arg P|$.

**Findings:** Both real controls give zero signed grasp. The sampled small-phase branch is approximately linear, with fitted slope $-0.08978$, then turns over at larger perturbations.

**Artifacts:** [Results and method](../results/t5d_phase_scan_results.json), [study record](../memory-bank/tasks/T5d.md).

<a id="ns18"></a>
### NS18 — Small-sector squeezed-FL geometry audit

**Question:** What closure and geometry does the draft two-copy squeeze produce?

**Calculation:** Evaluated regular and unequal-skew four-face inputs at $J=1,2$ for $\beta=3,4,5,8$, with pair cutoff four and cutoff-two comparisons. Calculated closure, area/correlation diagnostics, positive volumes, and entropy before and after explicit double-singlet projection.

**Findings:** Combined dual-copy closure passes. Ordinary closure on each copy fails for the draft squeezed state and is restored by double-singlet projection. The saved readouts compare the resulting preparations and their geometry.

**Artifacts:** [Driver](../code/python/t7_geometry_thermal.py), [results](../results/t7_geometry_thermal_results.json), [session record](../memory-bank/sessions/2026-10-06-t7-physical-thermal-audit.md).

## 2026-10-08–09: thermal distributions, complete catalogues, and Hamiltonians

<a id="ns19"></a>
### NS19 — Squeezed-vacuum occupation and spin distributions

**Question:** How does the two-copy squeezed vacuum populate area and spin sectors?

**Calculation:** Evaluated four-face occupation coefficients and distributions at four temperatures, plus ordinary per-copy resultant-spin distributions conditioned on occupation.

**Findings:** Increasing temperature broadens occupation support. Sector multiplicities shape the distribution across total occupation and resultant spin. The coefficient plots retain numerical arrays and reproducible plotting code.

**Artifacts:** [Occupation plot code](../code/thermal/plot_vacuum_coefficients.py), [spin plot code](../code/thermal/plot_vacuum_spin.py), [figures and arrays](../figures/thermal-area-sectors/), [thermal write-up](thermal-area-sectors.md).

<a id="ns20"></a>
### NS20 — Excited-input joint occupation and spin distribution

**Question:** How does a nonzero-area FL input change the squeezed state's sector distribution?

**Calculation:** Calculated $P(q,S)$ for four faces and $J_{\mathrm{in}}=1$ through $q=160$ at $\beta\hbar\omega=0.5,1,2,4,8$. Compared explicit spin coupling with magnetic-component counting. Independent oscillator coefficients and Casimir-projector controls cover $q\le4$.

**Findings:** The two methods agree across 32,805 entries with maximum absolute difference $2.67\times10^{-16}$. Higher temperature broadens both occupation and spin distributions. Every kinematically allowed sector has positive finite-temperature weight.

**Artifacts:** [Method comparison](../code/thermal/compare_j1_spin_methods.py), [plot code](../code/thermal/plot_j1_spin.py), [results](../results/thermal-j1-spin/), [session record](../memory-bank/sessions/2026-10-08-j1-spin-distribution.md).

<a id="ns21"></a>
### NS21 — Complete four-face closed-basis volume catalogue

**Question:** What are all volume outcomes in fixed-area four-face singlet spaces?

**Calculation:** Enumerated four labelled faces with zero-spin faces allowed for $K=2,\ldots,12$: 10,549 basis states. Saved positive RS/AL spectra, basis means and fluctuations, and compressed operators.

**Findings:** The catalogue resolves positive-volume and zero-volume sectors across the complete calculated spaces. Saved matrices support reconstruction of the means, fluctuations, and spectra. The completed catalogue ends at $K=12$.

**Artifacts:** [Driver](../code/python/closed_basis_volume.py), [catalogue and storage description](../results/closed-basis-volume/README.md), [results](../results/closed-basis-volume/), [figures](../figures/closed-basis-volume/).

<a id="ns22"></a>
### NS22 — Variable-face positive-volume catalogue

**Question:** How does the closed-state and volume spectrum change with active face number?

**Calculation:** Enumerated all labelled positive-spin assignments and singlet coupling channels for $K=2,3,4$, with $4\le N\le2K$. Calculated RS spectra in nine area/face sectors. Independent verification covers 112 blocks and 385 eigenstates.

**Findings:** Total closed dimensions are 2, 36, and 347; positive-volume dimensions are 2, 32, and 329. Saved counts, eigenstates, operators, distributions, and figures make active-face dependence explicit.

**Artifacts:** [Driver](../code/python/variable_n_volume.py), [verifier](../code/python/verify_variable_n_volume.py), [catalogue](../results/variable-n-volume/README.md), [volume write-up](volume-studies.md).

<a id="ns23"></a>
### NS23 — Four-site Hamiltonian spectra and thermal volumes

**Question:** Which closed states are selected by hopping, repulsion, and temperature?

**Calculation:** Diagonalized the two-species hopping-plus-on-site-repulsion Hamiltonian for four sites and $K=2,3,4$, with singlet dimensions 20, 50, and 105. Complete and ring graphs use no-hopping, free-hopping, and $U/t=1,5,20$ controls: 30 cases. Calculated spectra, correlations, one-site entropy, Gibbs thermodynamics, active-face probabilities, volume distributions, and commutators. A dense $K=4$ follow-up resolves the low-temperature response.

**Findings:** On-site repulsion commutes with volume; the hopping edge–triple sum reconstructs $[H,V]$ within $7.2\times10^{-15}$. At $U/t=20$, the complete-graph ground volume is 0.03349, its first gap is 0.00923, and the first excited doublet has volume 0.60110. Cooling changes the relative populations of these groups and produces a pronounced low-temperature volume drop. Several controls show nonmonotonic thermal volume.

**Artifacts:** [Driver](../code/python/hamiltonian_studies.py), [output guide](../results/hamiltonian-studies/README.md), [results and figures](../results/hamiltonian-studies/), [study note](hamiltonian-studies.md).

## 2026-10-09–11: evolution, binding, sewing, and geometric interactions

<a id="ns24"></a>
### NS24 — Open-state evolution and same-number detachment energies

**Question:** How do open preparations evolve, and what energy does separating one face cost?

**Calculation:** Evolved a closed FL seed, a single coherent face, and a missing-face product under complete/ring hopping at $t=1,U=5$. Separately compared intact and dissociated four-boson singlet ground states, deleting hopping to the isolated face while retaining its degrees of freedom. Detachment outputs also cover $U/t=0,1,5,20$.

**Findings:** Total-spin sector weights stay fixed while hopping redistributes occupation and populates the initially empty site. At $U/t=5$, the three-plus-one detachment costs are 0.769253300 for the complete graph and 0.795078777 for the ring. The main separated channel couples two spin-half subsystems to a singlet. FL seed energies and uncertainties are also saved.

**Artifacts:** [Evolution driver](../code/python/closure_probes.py), [evolution results](../results/state-space-probes/summary.json), [evolution note](state-space-probes.md), [detachment driver](../code/python/binding_energy.py), [detachment results](../results/binding-energy/summary.json), [detachment note](binding-energy.md).

<a id="ns25"></a>
### NS25 — Triangle, tetrahedron, and joined-boundary sewing

**Question:** Can local invariant tensors be explicitly sewn into one and two-polyhedron boundary networks?

**Calculation:** Built spin-one triangle tensors using pair-creation operators. Contracted four triangles into a tetrahedral network, then joined two open three-triangle patches along the three edges of their common face. Retained link transports and checked direct versus patch contractions.

**Findings:** The identity-link tetrahedral evaluation is $1/162$, matching the normalized Wigner-six-j calculation. Each open patch has 27 components. Sewing normalized patches gives $1/(3\sqrt3)$; direct exterior-boundary contraction gives 0.000197993919475 and agrees with sewing raw patches. The joined exterior graph has six face nodes and nine edges.

**Artifacts:** [Driver](../code/python/sewing_probes.py), [results and tensors](../results/sewing-probes/), [construction note](constructive-sewing-probe.md).

<a id="ns26"></a>
### NS26 — Four/five-site comparison and prepared-FL diagnostics

**Question:** Does the four-site thermal suppression persist at five sites, and which geometric correlations explain it?

**Calculation:** Compared $(L,K)=(4,4)$ and $(5,5)$ at mean occupation $2K/L=2$, with dimensions 105 and 1,176. Complete/ring graphs use strong-repulsion, free, and no-hopping controls. Separately constructed five $K=4$ FL references at bending angles $90,60,30,10,0$ degrees and compared them with low-energy groups, measuring areas, angular covariance, volume distributions, and overlaps.

**Findings:** Intermediate-temperature nonmonotonicity appears at both sizes. The five-site complete graph has a substantial-volume six-dimensional ground space and gap 12.6434; the pronounced four-site low-temperature suppression disappears. The four-site ground retains nearly unit four-face probability but has zero-volume probability 0.93154. Within the dominant equal-spin assignment, ground and excited groups share mean pair angles $-1/3$, while volume and angular fluctuations distinguish them.

**Artifacts:** [Size driver](../code/python/t11_size_comparison.py), [size report](../results/t11-size-comparison/README.md), [geometry driver](../code/python/t11_geometric_interpretation.py), [geometry report](../results/t11-geometric-interpretation/README.md), [geometry figures](../results/t11-geometric-interpretation/).

<a id="ns27"></a>
### NS27 — Geometric interactions and prepared-FL evolution

**Question:** How do positive-volume and oriented-flux interactions change energy preferences and the evolution of prepared tetrahedral states?

**Calculation:** First tested $H_0+g_VV_{\mathrm{RS}}$ at $U/t=20$ and three couplings, then expanded to 62 settings for positive-volume and signed-flux interactions at $U/t=0,1,5,20$, including ring controls. Evolved five $K=4$ FL references under the baseline and both signs of each interaction at $U/t=5,20$: 50 trajectories. Saved spectra, thermal curves, area/angle/volume readouts, signed grasp, return probability, and time-scale schedules.

**Findings:** At $U/t=20$, ground volume is 0.033487 for the baseline, 0.601241 for the volume-rewarding coupling, and 0.031332 for the volume penalty. Either sign of the signed-flux interaction gives approximately 0.601235 while reversing the preferred orientation. The regular FL preparation has ground-space overlap 0.112216 under the volume-rewarding coupling. The evolution uses exact energy-basis phases. Independent verification passed 1,510 checks with largest residual $1.07\times10^{-12}$.

**Artifacts:** [Initial volume-coupling report](../results/t11-volume-coupling/README.md), [candidate/evolution driver](../code/python/t11_candidate_hamiltonians.py), [independent verifier](../code/python/verify_t11_candidate_hamiltonians.py), [full study report](../results/t11-candidate-hamiltonians/README.md), [results and figures](../results/t11-candidate-hamiltonians/).

## 2026-10-13: closure and the growth of closed thermal geometry

<a id="ns28"></a>
### NS28 — Temperature dependence of ordinary per-copy closure

The study asks how heating changes the magnitude of the residual total face flux in the selected four-face, initial-area-one two-copy state. Across 125 temperatures, increasing $T_*=k_BT/(\hbar\omega)$ raises the ordinary RMS closure defect and reduces the single-copy singlet fraction. The full state continues to obey combined dual-copy closure. The distinction is developed with definitions, a figure and a table in [the thermal-area note](thermal-geometry-and-singlet-exchange.md#section-16-02).

[Calculation and verification](../results/thermal-closure-temperature/README.md), [driver](../code/thermal/closure_temperature_sweep.py), and [figure](../figures/thermal-closure-temperature/closure_temperature.pdf).

<a id="ns29"></a>
### NS29 — Separately closed projection and thermal geometric growth

Double-singlet projection enforces ordinary closure in each copy while allowing area and volume to change. Because the copies have correlated resultant spins, the retained probability equals the earlier marginal singlet fraction rather than its square. The 85-temperature calculation shows increasing projected mean area, area fluctuations, and positive RS volume; four-active-face and nonzero-volume probabilities increase as well. Exact finite singlet sums give the high-temperature law $\langle A\rangle\sim(57/14)T_*$. The scientific narrative, three figures and compact tables are in [the thermal-area note](thermal-geometry-and-singlet-exchange.md#section-16).

[Study and verification](../results/thermal-closed-projection/README.md), [projection driver](../code/thermal/closed_projection_study.py), [shared library](../code/python/lqg_scattering/thermal_projection.py), [fit and analytic derivation](../code/thermal/fit_closed_temperature.py), and [distribution figure](../figures/thermal-closed-projection/closed_projection_distributions.pdf).

<a id="ns30"></a>

### NS30 — Finite-area singlet exchange and canonical controls

Calculated October 14 under T9a; entered into this central index October 16.
The complete fixed-combined-area K=4 space has 1,210 states. Four Hamiltonians
and three FL inputs give twelve trajectories, with area current, entanglement,
coherence and positive-volume readouts. Twenty canonical controls retain joint
Gibbs entropy separately from trajectory entanglement. Prior verification
records 46 regression tests and 1,792 independent comparisons. The finite pair
does not establish reservoir relaxation or equivalence to the T9 squeeze.

[Report](../results/t9a-singlet-exchange/README.md),
[specification](t9a-singlet-exchange.md), and
[illustrated narrative](thermal-geometry-and-singlet-exchange.md).

<a id="ns31"></a>

### NS31 — Closed-reference entanglement and coherent singlet creation

Calculated October 16 under T9. Direct Schmidt eigenvalues and multiplicities
for the separately projected F12 area-one reference yield entropy, Rényi-2
entropy, purity and area-sector decomposition across 86 temperatures,
T*=0.05..5. Within-area contributions exceed shared-area entropy at T*=1,2,5.
A joint singlet-creation expectation detects coherence between adjacent area
sectors; the singlet-transfer mean vanishes by equal-area support. Adaptive
cutoffs 12..140 control the infinite entropy tail below 6.4e-12 nats. The 802
comparisons include independent oscillator/Casimir/SVD controls, creator
matrices, saved geometry, and convergence checks. This reference begins with
two active faces; general four-face FL inputs remain open.

[Pedagogical note](thermal-entanglement.md),
[report and artifacts](../results/thermal-closed-entanglement/README.md),
[driver](../code/thermal/closed_entanglement_study.py),
[independent verifier](../code/thermal/verify_closed_entanglement.py), and
[figure](../figures/thermal-closed-entanglement/entanglement_overview.pdf).

<a id="ns32"></a>

### NS32 — Large-area FL face activation and free-hopping recurrence

Calculated October 16 under T11, following the user's question about energy
sharing and growth beyond a large tetrahedron. Exact U(L) FL evolution embeds
four regular tetrahedral labels in five/six channels with vacuum extras.
Twenty controls span K=2,20,100,1000,10000 and two phase choices, using existing
complete-graph free hopping with U=0. An extra channel receives up to 29.06%
of total area in the five-channel baseline; face areas and local energies
remain unequal and recur. The symmetric six-channel run has six occupied
channels but at most five distinct classical normal directions. All 360
independent sparse-evolution, face-statistics and conservation comparisons
pass. This is a coherent activation control, not an interacting equilibration
or arbitrary-valence refinement result.

[Pedagogical results and proposed F/J interactions](face-energy-equipartition.md),
[report](../results/fl-face-activation/README.md),
[driver](../code/python/fl_face_activation.py),
[verifier](../code/python/verify_fl_face_activation.py), and
[figure](../figures/fl-face-activation/face_activation_control.pdf).

<a id="ns33"></a>

### NS33 — Small-area face-channel equilibration pilot

The finite-area quantum pilot compares four to seven available channels at
$K=2,3$, three repulsion strengths, and two regular FL phase choices. The
42 trajectories are summarized over windows ending at $t=100$ and $200$.
For the regular $K=3$ input and distance tolerance $0.05$, late-window
residence rises from 19.0% to 76.1% as $U$ changes from zero to five at four
channels; at five and six channels the corresponding $U=5$ values are 76.7%
and 90.3%. The trend changes for the phase-shifted preparation, so this is not
a channel-count law or a matched-energy comparison. All 252,840 independent
comparisons passed; the larger 46-test regression suite also passed. No
large-area quantum equilibration result follows from this pilot.

[Local report](../results/t11-equilibration/README.md),
[saved summary](../results/t11-equilibration/summary.csv), and the combined
[T11 equilibration and rotor note](classical-rotor-equilibration.md).

<a id="ns34"></a>

### NS34 — Classical rotor energy spreading and equilibrium comparison

The classical ring study follows $N=8,16,32,64$ rotors from a neighboring
equal-and-opposite hot pair, using three orientation seeds and both fixed
packet-energy and fixed-density preparations. The published table groups the
three seeds rather than listing trajectories. At packet energy 10, the late
hot-pair fraction follows the microcanonical mean $2/N$ and residence in the
sampled 90% equilibrium region ranges from 87.2% to 90.4%. At packet energy
100, the pair retains 98.7–99.0% of local energy through $t=2000$ and has no
sampled residence in that region. The distinction is finite-time: it neither
establishes permanent localization nor proves eventual equilibration.

[Full physical account](classical-rotor-equilibration.md),
[local result report](../results/t11-classical-rotors/README.md), and
[grouped summary](../results/t11-classical-rotors/grouped-summary.csv).

<a id="ns35"></a>

### NS35 — Few-rotor energy transfer and the planar threshold

For an aligned planar pair with one initially resting rotor, the relative
motion is a pendulum. Complete exchange is possible below $T_0=4\lambda$;
above it the exact maximum receiver fraction is
$[(1-\sqrt{1-4\lambda/T_0})/2]^2$. The saved scan includes 14 pair cases,
with numerical maxima checked against the exact bound and a scalar-ODE
reference. Separate three-dimensional zero-total-angular-momentum controls
cover a triangle, open four-rotor chain, and four-rotor ring at seven coupling
values and three seeds. These finite-time controls demonstrate transfer in
the tested preparations; they do not establish equilibration or a transition.

[Pedagogical note](few-rotor-energy-transfer.md),
[local result report](../results/t11-few-rotors/README.md), and
[key figure](../figures/t11-few-rotors/few-rotor-transfer.pdf).

<a id="ns36"></a>

### NS36 — Rotor coupling crossover and delayed release

The primary zero-angular-momentum ring scan covers four sizes, 14 initial
packet-energy-to-coupling ratios, and three orientation seeds through scaled
time $\tau=2000$. The 29 additional histories check direct physical couplings,
step refinement, and longer windows. The sampled half-response brackets lie
between $12<r_c<16$ and $16<r_c<18$, depending on ring size; they are grid
brackets, not fitted critical points. For $N=8,r=18$, the mean transferred
fraction grows from below 1% through $\tau=2000$ to about 30% over
$[200,10000]$. The late release is qualitatively reproduced across seeds and
a smaller step, while its timing remains sensitive. The crossover depends on
the observation window and does not prove permanent localization or universal
equilibration.

[Full coupling note](rotor-coupling-crossover.md),
[local result report](../results/t11-rotor-coupling/README.md),
[grouped scan](../results/t11-rotor-coupling/grouped-scan.csv), and
[key figure](../figures/t11-rotor-coupling/coupling-crossover.pdf).

<a id="ns37"></a>

### NS37 — Four quantum planar rotors at zero total momentum

A four-rotor ring starts in $|m,-m,0,0\rangle$ with $m=2,4$ and
$I=\lambda=\hbar=1$. The initial packet kinetic energies are 4 and 16;
mean total energies include another four units of interaction energy. The
matched classical comparison uses 2,048 uniform-angle samples with the same
momenta. Over saved times $10\leq t\leq20$, the quantum cold-pair kinetic
ratios are 59.20% and 6.71%, versus classical 48.52% and 5.32%. Local entropy,
returns and conservation readouts accompany the transfer curves. Cutoffs
8 and 10 agree; classical steps were refined until the declared criterion
passed. The suite then had 62 tests.

[Physical account](quantum-planar-rotor-energy-transfer.md),
[result report](../results/t11-quantum-planar-rotors/README.md),
[summary](../results/t11-quantum-planar-rotors/summary.json),
[driver](../code/python/t11_quantum_planar_rotors.py), and
[figure](../figures/t11-quantum-planar-rotors/energy-transfer.pdf).

<a id="ns38"></a>

### NS38 — Closed/nonclosed four-to-five-to-six connectivity

The Casimir-plus-hopping Hamiltonian is tested in the full six-channel,
six-boson space (12,376 states) and its singlet subspace (490 states). A
normalized singlet with counts $(2,1,1,2,0,0)$ connects to
$(1,1,1,2,0,1)$ and then $(1,1,1,1,1,1)$, with each directed matrix element
$-\sqrt2\,t$. The same chain occurs in total-spin-three states, including an
$M=0$ state whose mean spin is zero. The ring's actual second-power
six-channel amplitude has norm $4t^2$. Singlet $P_5HP_4$ has rank 90 and
$P_6H^2P_4$ rank five on both ring and complete graphs. Five-channel and
minimum-boson controls, no hopping and disconnected receivers were checked.
The 99 independent dictionary-algebra checks have maximum residual
$1.99\times10^{-15}$; the suite then had 67 tests.

[Derivation](face-activation-connectivity.md),
[result report](../results/t11-face-connectivity/README.md),
[primary record](../results/t11-face-connectivity/L6-K3.json), and
[driver](../code/python/t11_face_connectivity.py).

<a id="ns39"></a>

### NS39 — Sparse closed-state geometric redistribution

At $K=4$, compare four, six and eight channels on normalized rings and
complete graphs, with Casimir couplings $\alpha=0,1,5$. Two preparations
condition regular/deformed FL states onto exactly four spin-one channels;
a third retains unconditioned regular FL occupation fluctuations. The
54 trajectories contain 5,454 time rows. For the regular sharp eight-channel
input at $\alpha=1$, late receiver-area fractions are 50.6% (ring) and
34.6% (complete), while probabilities for at least five occupied channels
are 68.1% and 67.6%. Positive RS volume, pair angles and entropies are saved
at selected times; the volume uses all vertex triples independently of the
interaction graph. Sparse construction uses 108,900 magnetic states and
13,860 singlets at the largest size. All 73 tests and 91,476 independent
saved-data/analytic checks pass, maximum residual $6.43\times10^{-12}$.
Compact numerical outputs occupy about 5.6 MB; wavefunction histories are
not retained.

[Pedagogical account](geometric-area-redistribution.md),
[result report](../results/t11-geometric-redistribution/README.md),
[run summaries](../results/t11-geometric-redistribution/summary.csv),
[driver](../code/python/t11_geometric_redistribution.py),
[area figure](../figures/t11-geometric-redistribution/area-transfer.pdf), and
[geometry figure](../figures/t11-geometric-redistribution/geometry-and-activation.pdf).

<a id="ns40"></a>

### NS40 — A permutation selection rule for all-eight occupation

A post-run diagnostic explains why the regular sharp preparation on the
symmetric complete graph has all-eight probability below
$2\times10^{-30}$, while the deformed preparation does not. Empty receivers
are initially permutation symmetric. Within the all-eight singlet target,
receiver symmetry requires original-group symmetry; the corresponding target
subspace has rank one. The regular sharp source has symmetric weight
$1.06\times10^{-32}$, versus 0.348993 for the deformed source. The checked
target-projector identity has residual $2.95\times10^{-17}$. Complete-graph
permutation invariance preserves the restriction, while the ring permits
all-eight activation. This check followed inspection of NS39; it is not an
additional trajectory scan.

[Explanation](geometric-area-redistribution.md),
[saved symmetry check](../results/t11-geometric-redistribution/symmetry-control.json),
and [diagnostic program](../code/python/check_t11_channel_symmetry.py).

## Numerical infrastructure and browsing

The [Python–TypeScript benchmark](../results/python-vs-ts/README.md), recorded in the October 9–10 backend work, independently constructs the matched $K=2$ T11 model and compares matrix construction, roots, eigensystems, sparse actions, and thermal readouts. Its saved numerical parity and timings accompany the Python-plus-Rust research stack.

Shared state, volume, geometry, Hamiltonian, sewing, and thermal routines live in [the Python package](../code/python/lqg_scattering/). Study drivers select parameters and write artifacts. Package extraction retained saved-result parity and passed build, installation, and test checks.

The [InfoDash numerical dashboard](../code/dashboard/index.html) is the single interface for the overview, study records, figures, tasks, and case-level datasets. Its [study catalogue](../code/dashboard/studies.json) and selectable numerical datasets are generated from saved artifacts by [the catalogue builder](../code/python/dashboard_assets/build_research_catalogue.py), which uses [the numerical-data exporter](../code/python/dashboard_assets/export_numerical_data.py). This document supplies the chronological narrative; the dashboard provides the interactive numerical records and downloads.

## Maintaining this record

Append each new calculation in chronological order and add its index row. Record the calculation date, question, coverage, findings, driver, outputs, and figure/report links. Give corrected reruns their own dated entry and link the calculation they replace. Keep the existing entry identifiers stable when adding older recovered studies.

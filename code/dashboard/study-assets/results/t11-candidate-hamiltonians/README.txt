# T11: candidate Hamiltonians on tetrahedral singlets

*Recorded: 2026-10-11 13:15 IST*

This study compares two explicit geometric additions to the four-site Hamiltonian, then evolves all five prepared Feller–Livine (FL) references. It uses the existing $K=4$, total-spin-zero space, which has dimension 105.

## Hamiltonians and parameter choices

The baseline is

$$
H_0=-t\sum_{\langle i,j\rangle}(E_{ij}+E_{ji})
+U\sum_i\binom{n_i}{2}
=-t\sum_{\langle i,j\rangle}(E_{ij}+E_{ji})
+\frac{U}{2}\sum_i n_i(n_i-1).
$$

The second term is on-site repulsion. The complete graph is used as the tetrahedral face-adjacency model. The ring is a sparse-hopping control and is not interpreted as a tetrahedron.

The two tested candidates are

$$
H_V=H_0+g_V V_{\rm RS},
\qquad
H_\chi=H_0+\lambda_\chi Q_\chi.
$$

Here $V_{\rm RS}$ is the existing positive RS operator, summed over the four connected triples. The signed term uses

$$
q_{ijk}=i[D_{ij},D_{jk}]
=\mathbf J_i\cdot(\mathbf J_j\times\mathbf J_k),
\qquad
Q_\chi=q_{012}-q_{013}+q_{023}-q_{123},
$$

with the orientation signs $(+,-,+,-)$. They obey

$$
q_{012}=-q_{013}=q_{023}=-q_{123},
\qquad
Q_\chi=4q_{012}.
$$

With the existing positive-root cutoff and $\gamma=0.2375$, the operators also satisfy

$$
V_{\rm RS}=2\gamma^{3/2}\sqrt{|Q_\chi|}.
$$

The numerical operator residual for this functional relation is below $10^{-15}$. Thus these two candidates are related on this closed four-face space: $V_{\rm RS}$ depends on the magnitude of the oriented grasp, while $Q_\chi$ also distinguishes its sign. The signed term is orientation-sensitive and odd under time reversal. The calculation tests it as a candidate model; it does not establish that a physical Hamiltonian should contain it.

Couplings are reported as dimensionless parameters

$$
\alpha_V=\frac{g_V\Delta V_{\rm RS}}{t},
\qquad
\alpha_\chi=\frac{\lambda_\chi\Delta Q_\chi}{t},
$$

where $\Delta V_{\rm RS}=0.609306380473$ project units and $\Delta Q_\chi=13.856406460551$. We set $t=1$. Complete-graph runs use $U/t=0,1,5,20$ and $\alpha=-2,-1,-0.5,0,0.5,1,2$ for both candidates. The ring control uses $U/t=5,20$ and $\alpha_V=-1,0,1$. These are 62 candidate-parameter settings; the four complete-graph $\alpha=0$ pairs are duplicate $H_0$ matrices.

All five prepared FL references use equal input face areas, $x=1/\sqrt3$, and $\varphi=90^\circ,60^\circ,30^\circ,10^\circ,0^\circ$. The endpoints are labelled regular and flat-boundary control. Static reference readouts include all five preparations for each setting.

## Static and thermal readouts

For each setting, the files include the full 105-level spectrum; ground energy, degeneracy, first distinct gap and uniform degenerate-state readouts; the first three distinct energy groups; and probabilities for each prepared FL reference in those groups. State and thermal readouts include face-area means and covariances, assignment and active-face probabilities, all six pair dots, four-face-conditioned angular means and symmetrized covariances, positive-volume mean and variance, the zero-volume probability and outcome distribution, and signed-grasp means and rms values.

Thermal quantities use $\beta t=0$, 601 logarithmic values from $10^{-3}$ to $10^3$, and the exact uniform ground-subspace mixture at $\beta=\infty$. Volume values remain in project RS units; no physical volume calibration is implied.

For the complete graph at $U/t=20$, the zero-temperature comparison is:

| Candidate | $\alpha$ | Ground energy | First gap | Ground $\langle V_{\rm RS}\rangle$ | $P(V_{\rm RS}=0)$ | Ground $\langle Q_\chi\rangle$ |
|---|---:|---:|---:|---:|---:|---:|
| $H_0$ | 0 | 78.474435 | 0.009226 | 0.033487 | 0.931544 | 0 |
| $H_V$ | -1 | 77.497011 | 0.920552 | 0.601241 | 0.000193 | 0 |
| $H_V$ | +1 | 78.527599 | 0.942482 | 0.031332 | 0.935951 | 0 |
| $H_\chi$ | -1 | 77.996471 | 0.477630 | 0.601235 | 0.000197 | +6.752495 |
| $H_\chi$ | +1 | 77.996471 | 0.477630 | 0.601235 | 0.000197 | -6.752495 |

At $\beta t=10$, the corresponding thermal mean volumes are $0.400087$ for $H_0$, $0.601213$ for $H_V$ with $\alpha=-1$, $0.031424$ for $H_V$ with $\alpha=+1$, and $0.596491$ for either sign of $H_\chi$. The signed coupling therefore selects high $|Q_\chi|$ and high volume for either sign; changing its sign reverses the preferred oriented grasp. Its $\alpha$ and $-\alpha$ spectra agree to numerical precision because complex conjugation maps $H_\chi(\alpha)$ to $H_\chi(-\alpha)$.

The regular reference's ground-space overlap at $U/t=20$ is $0.112216$ for $H_V,\alpha=-1$, $0.000870$ for $H_V,\alpha=+1$, zero for $H_\chi,\alpha=-1$, and $0.1123$ for $H_\chi,\alpha=+1$. The flat-boundary overlaps are $0.080898$, $0.063541$, $0.0404$, and $0.0404$, respectively. These are projections onto ground eigenspaces, not exclusive shape probabilities.

The plotted ground-energy figure is explicitly a Hamiltonian result: it shows $(E_0(\alpha)-E_0(0))/t$ for each candidate coupling and each $U/t$ on the complete graph. It is not a plot of the RS-volume eigenvalues or of thermal volume. `energy_levels.csv` contains every level for each evaluated Hamiltonian, and `model_summary.csv` contains each ground energy and its gap.

The ring changes the thermal response. At $U/t=20$ and $\beta t=10$, the ring mean volumes for $\alpha_V=-1,0,+1$ are $0.539372$, $0.291685$, and $0.110923$, versus $0.601213$, $0.400087$, and $0.031424$ on the complete graph. This supports using the ring only as a hopping-topology control.

## FL-state dynamics

We propagated all five $K=4$ FL references ($\varphi=90^\circ,60^\circ,30^\circ,10^\circ,0^\circ$) under the complete-graph baseline, $H_V$ at $\alpha_V=\pm1$, and $H_\chi$ at $\alpha_\chi=\pm1$, for $U/t=5,20$: 50 trajectories in total. Propagation uses exact finite-dimensional energy-basis phases. The time series records return probability, volume mean/variance/kernel weight, active-face and area statistics, angular means/covariances, and signed-grasp readouts. Norm, energy, total-area and singlet-closure residuals are retained.

The energy support makes a uniform time grid impractical. Resolved beats are those whose normalized observable coefficient is at least $10^{-8}$; gaps below $10^{-10}\max(1,\text{bandwidth})$ are treated as numerically unresolved. The saved series has 20 samples per fastest resolved beat over the first ten fastest periods, followed by 900 exact logarithmic-time samples through ten periods of the slowest resolved beat. A uniform grid over that full interval would require from 4,413,058 to 2,005,038,331 samples per trajectory. The required count and exact sampled horizon are recorded in the dynamics schedule; the long-time values are exact samples, not a uniformly resolved trace of every fast oscillation.

## Files and reproduction

- [Model summary](model_summary.csv), [full spectra](energy_levels.csv).
- [State geometry](state_geometry.csv), [volume outcomes](state_volume_distributions.csv), [area assignments](state_area_assignments.csv), and [FL energy populations](fl_energy_populations.csv).
- [Thermal scan](thermal_scan.csv), [thermal volume outcomes](thermal_volume_outcomes.csv), and [selected thermal area assignments](thermal_area_assignments_selected.csv).
- [FL evolution samples for all five seeds](dynamics_scan.csv) and [time-scale accounting](dynamics_schedule.csv).
- [Validation](validation.json), [independent verification](verification.json), [protocol](protocol.json), and [source/input hashes](provenance.json).
- Figures: [Hamiltonian ground-energy shifts](candidate_ground_energy_shifts.pdf), [ground-state volume and chirality response](candidate_ground_state_response.pdf), [thermal response](candidate_thermal_response_u20.pdf), [ring control](ring_topology_control.pdf), and [early FL dynamics](prepared_FL_early_dynamics_u20.pdf). Each PDF has a 300-dpi PNG preview alongside it.

Reproduce the static/thermal calculation and evolution with

~~~sh
PYTHONPATH=code/python python code/python/t11_candidate_hamiltonians.py
~~~

Run independent checks with

~~~sh
PYTHONPATH=code/python python code/python/verify_t11_candidate_hamiltonians.py
~~~

Regenerate figures with

~~~sh
PYTHONPATH=code/python python code/python/plot_t11_candidate_hamiltonians.py
~~~

The scripts were run with the repository's Python research environment.

The independent verifier performed 1,510 checks, including NumPy spectra, matrix-exponential Gibbs traces, saved-baseline parity, direct spin-one grasp spectra, site-permutation/orientation covariance, volume-distribution normalization and early-time matrix-exponential evolution. The largest residual was $1.07\times10^{-12}$, below the $2\times10^{-10}$ tolerance.

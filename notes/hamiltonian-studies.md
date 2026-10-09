# Four-site Hamiltonian and volume pilot

*Created: 2026-10-09 11:35:15 IST*
*Last Updated: 2026-10-09 20:53:49 IST*

This note records the first numerical milestone of the proposed lattice-Hamiltonian program. It covers four available sites, fixed $K=2,3,4$, total SU(2) spin zero, and $g=0$. It is a finite-sector study, not a thermodynamic-limit or phase-transition result.

## Model and scope

The fixed-area subspace has total boson number $2K$ and includes empty sites. The exact singlet dimensions are 20, 50, and 105 for $K=2,3,4$. The driver compares:

- the complete graph on four sites, with six hopping bonds;
- the periodic four-site ring, with four hopping bonds.

The Hamiltonian is

$$
H=-t\sum_{\langle i,j\rangle}(E_{ij}+E_{ji})
+\frac U2\sum_i n_i(n_i-1),\qquad
E_{ij}=a_i^\dagger a_j+b_i^\dagger b_j,
$$

with $g=0$. The controls are no hopping $(t,U)=(0,1)$ and $t=1$ with $U/t=0,1,5,20$.

The volume is the project-normalized positive RS sum

$$
V=(\gamma\hbar)^{3/2}\sum_{\tau\in\mathcal T_G}\sqrt{|q_\tau|},
\qquad q_{ijk}=i[\mathbf J_i\cdot\mathbf J_j,\mathbf J_j\cdot\mathbf J_k],
$$

using $\gamma=0.2375$ and $\hbar=1$. A triple is included when its induced three-site subgraph is connected; mutual adjacency is not required. For both the four-site ring and the complete graph, all four three-site subsets are connected. Therefore this pilot uses the same four volume terms on each graph, and the graph comparison changes the hopping Hamiltonian only. Physical volume calibration remains open.

The singlet basis couples $((j_0,j_1)k,(j_2,j_3)k)$ to total spin zero, with Condon–Shortley phases. The magnetic $M=0$ occupation basis is used to project the spin-independent hopping terms into the exact singlet space. Volume terms are built in each local-spin block from their positive spectral roots.

The raw ground-energy curves for the two graphs nearly overlap. The difference plot resolves the graph effect: $E_0(\mathrm{complete})-E_0(\mathrm{ring})$ is zero to numerical precision for $K=2$ and $U/t=0$, while for $K=3$ it is $-0.05754,-0.09437,-0.05379$ at $U/t=1,5,20$; for $K=4$ it is $-0.08014,-0.05347,-0.00408$.

## Calculated outputs

For each $K$, graph, and control, the driver records the full energy spectrum, ground energy and gap, ground-subspace volume moments, volume-zero probability, active-site count, pairwise occupation and spin correlations, and the site-0 reduced-state entropy and purity in the zero-temperature Gibbs state. It also forms the fixed-$K$ Gibbs state for $\beta=0,0.1,0.25,0.5,1,2,4,8,16$ and the zero-temperature limit. Thermal outputs include energy, entropy, heat capacity, volume moments, volume-measurement probabilities, and $P(N)$ with conditional volume at each active-site count. The reported site entropy is for the equal mixture of degenerate ground states where applicable; it is not reported as an entanglement measure.

| $K$ | Singlet dimension | No-hop ground energy | Free-hopping ground energy | $U/t=20$ complete / ring ground energy |
|---:|---:|---:|---:|---:|
| 2 | 20 | 0 | -4 | -0.585732 / -0.585732 |
| 3 | 50 | 2 | -6 | 35.740181 / 35.793968 |
| 4 | 105 | 4 | -8 | 78.474435 / 78.478518 |

In the no-hopping control, the two graph spectra agree and the ground space has all four sites occupied. In the free control, the lowest energy is $-2K$ on both graphs, although their gaps and volume distributions differ. At $U/t=20$, the $K=4$ complete-graph ground state has a small gap of about $0.00923$ and mean volume about $0.03349$; the ring gives about $0.35987$ and $0.28317$. These are observations in a 105-dimensional sector, not evidence for a phase transition.

At $\beta=0$, the mean volume matches the saved four-face equal-weight RS baseline: $0.030465319024$, $0.093434906442$, and $0.175563653024$ for $K=2,3,4$. The volume-outcome and active-site probabilities each normalize to one within floating-point error.

The infinite-temperature active-site distribution also matches the exact kinematic count

$$
P_\infty(N\mid K,L)=\frac{\binom{L}{N}D_K(N)}{d_L(K)}.
$$

Here $D_K(N)$ counts closed singlets with all $N$ labelled active sites carrying positive spin, and $d_L(K)$ counts the complete closed space with $L$ available sites, including empty ones.

For $L=4$, the probabilities at $N=2,3,4$ are $(0.30,0.60,0.10)$ for $K=2$, $(0.12,0.56,0.32)$ for $K=3$, and $(0.057143,0.457143,0.485714)$ for $K=4$. The $N=1$ probability is zero in all three sectors.

The pair correlations also satisfy the singlet closure identity $\langle\mathbf J_i^2\rangle+\sum_{j\ne i}\langle\mathbf J_i\cdot\mathbf J_j\rangle=0$ to a maximum residual of $8.9\times10^{-16}$ across the saved ground-state mixtures.

## Follow-up: the $K=4$ thermal volume crossover

The initial $U/t=5$ figure ended at $\beta/t=16$ and omitted the zero-temperature limit. The follow-up samples $K=4$ at $\beta=0$, 601 logarithmically spaced values from $10^{-3}$ to $10^3$, and $\beta\to\infty$. It covers no hopping and all four $t=1$ interaction controls, and records $\langle V\rangle$, $P(V=0)$, mean active-site count, energy, and the energy–volume covariance. A second table groups degenerate energy eigenspaces and records their mean volume and zero-volume probability.

The nonmonotonic response is not exclusive to hopping: the no-hopping control also rises from the infinite-temperature mean $0.175564$ to a maximum near $0.446392$ at $\beta/t\approx1.78$, then approaches its ground-state mean $0.406204$. With hopping, the maximum shifts to lower $\beta$ as $U/t$ grows. For $U/t=5$, it is about $0.4419$ near $\beta/t=0.4$ for both graphs; the zero-temperature means are $0.184330$ (complete graph) and $0.336318$ (ring). For $U/t=20$, the maximum is about $0.4461$ near $\beta/t=0.089$; the zero-temperature means are $0.033487$ and $0.283172$, respectively.

The energy-resolved data identify a low-temperature crossover rather than a monotone approach to the ground state. At $U/t=5$, the complete graph has a first excited doublet only $0.124901$ above its ground state, with mean volume $0.559168$, compared with ground-state mean $0.184330$. The ring's first excited level is $0.666929$ above its ground state and has mean volume $0.561417$. At $U/t=20$, the complete graph's first excited doublet lies just $0.0092257$ above a ground state with mean volume $0.033487$; the doublet mean is $0.601103$. Its zero-volume probability rises to $0.931544$ in the ground state. The corresponding ring gap is $0.359870$, with ground-state mean volume $0.283172$ and zero-volume probability $0.521863$. The small complete-graph gap explains why the finite-$\beta$ curve is still well above its ground-state limit at $\beta/t=16$.

This temperature dependence follows the exact finite-system identity

$$
\frac{d\langle V\rangle_\beta}{d\beta}
=-\operatorname{Cov}_\beta(E,V_{nn}),
\qquad V_{nn}=\langle n|V|n\rangle,
$$

so the curve rises or falls as the Gibbs weights shift among energy eigenspaces with different volume expectations. The low-lying groups in these cases remain concentrated near four active sites, so the ground-state drop is not explained by a transition to a mostly empty-site sector. These are finite four-site crossovers, not phase-transition evidence.

## Hamiltonian–volume commutator

The projected onsite term commutes with each volume term to a maximum residual of $2.3\times10^{-16}$, consistent with $[n_i,q_{jkl}]=0$. The numerical decomposition of $[H,V]$ into triple terms and edge–triple terms has maximum residuals $3.6\times10^{-15}$ and $7.2\times10^{-15}$.

For $t=1$, the Frobenius norms of $[H,V]$ are independent of $U$, as expected because $[H_U,V]=0$:

| $K$ | Complete graph | Four-site ring |
|---:|---:|---:|
| 2 | 2.110699 | 1.723379 |
| 3 | 6.031197 | 4.924452 |
| 4 | 13.015778 | 10.627338 |

Within these closed four-site sectors, the four positive triple-root matrices agree to at most $8.4\times10^{-17}$. Their commutators therefore add without a reduction in Frobenius norm; this is specific to this four-valent singlet support and does not establish a cancellation rule for larger graphs.

## Reproduction and files

Run from the repository root:

```bash
conda run -n qc-diff python code/python/hamiltonian_studies.py
```

The saved run used the `qc-diff` Conda environment (Python 3.10.19, NumPy 1.24.3, SciPy 1.15.3, SymPy 1.14.0, and Matplotlib 3.10.8). The driver writes five figures in both PDF and PNG formats: ground energy versus repulsion, graph energy differences, the $U/t=5$ thermal-volume curve, a dense $K=4$ thermal scan, and the low-energy volume spectrum.

- [Driver](../code/python/hamiltonian_studies.py)
- [JSON summary](../results/hamiltonian-studies/summary.json)
- [Energy levels and controls](../results/hamiltonian-studies/energy_levels.csv)
- [Ground-state summary](../results/hamiltonian-studies/spectra.csv)
- [Thermodynamics](../results/hamiltonian-studies/thermodynamics.csv)
- [Active-site probabilities](../results/hamiltonian-studies/active_site_probabilities.csv)
- [Infinite-temperature active-site counts](../results/hamiltonian-studies/kinematic_active_site_counts.csv)
- [Ground-state correlations](../results/hamiltonian-studies/ground_state_correlations.csv)
- [Ground-state one-site reduced state](../results/hamiltonian-studies/ground_state_reduced_state.csv)
- [Volume distributions](../results/hamiltonian-studies/volume_distributions.csv)
- [Edge–triple commutator terms](../results/hamiltonian-studies/commutator_edge_triple_terms.csv)
- [Dense $K=4$ thermal scan](../results/hamiltonian-studies/k4_thermal_volume_scan.csv)
- [Energy-resolved $K=4$ volume](../results/hamiltonian-studies/k4_energy_resolved_volume.csv)
- Operator and basis archives: `results/hamiltonian-studies/operators_k{2,3,4}_{complete,ring}.npz`.
- Figures: `results/hamiltonian-studies/ground_energy_vs_repulsion.{pdf,png}`, `ground_energy_graph_difference.{pdf,png}`, and `thermal_volume_u5.{pdf,png}`.
- Detailed figures: `results/hamiltonian-studies/k4_thermal_volume_scan.{pdf,png}` and `results/hamiltonian-studies/k4_low_energy_volume_spectrum.{pdf,png}`.

The broader program remains open: larger site counts and areas, optional spin exchange, quenches and entanglement, fluctuating-area ensembles, and the energy-basis TFD comparison have not been implemented. Strict one-boson-per-site dynamics also require a spin Hamiltonian or a derived effective interaction because ordinary hopping leaves that subspace.

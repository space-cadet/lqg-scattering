# Singlet exchange between closed FL polyhedra

[Research map](quantum-geometry-research.md) · Related: [thermal geometry and singlet exchange](thermal-geometry-and-singlet-exchange.md), [constructive sewing probe](constructive-sewing-probe.md).

*Created: 2026-10-14 14:35:25 IST*

For the consolidated physical narrative and all related heating/exchange figures, see [Heating closed quantum geometry](thermal-geometry-and-singlet-exchange.md). This document remains the detailed implementation specification.

## Physical question and task ownership

T9a is a child of T9. T11 provides previously tested singlet bases, geometry operators, and exact evolution methods. The question is how two closed quantum polyhedra exchange area, and whether extension to a geometric reservoir can yield equilibrium related to the existing thermal-intertwiner construction.

We start with prepared FL states because their labels specify recognizable classical input geometries. We also calculate the coupled ground space, which need not resemble those inputs. Thermal equilibrium and reservoir relaxation are separate subsequent questions.

## Hamiltonian and exact support

Each copy has four ordered faces. Work on

$$
\mathcal H_K=\bigoplus_{k=0}^K\mathcal H^{\rm singlet}_{4,k}\otimes\mathcal H^{\rm singlet}_{4,K-k}.
$$

Vacuum endpoints and zero-area faces are included. With $\hbar=1$,

$$
H=\epsilon_LA_L+\epsilon_RA_R+\frac{U_L}2A_L(A_L-1)+\frac{U_R}2A_R(A_R-1)
+\sum_{i<j}\left(g_{ij}F_{ij,L}^\dagger F_{ij,R}+\overline{g}_{ij}F_{ij,R}^\dagger F_{ij,L}\right).
$$

The first implementation couples identical ordered face pairs on both copies. Equal coefficients on all six pairs define the symmetric baseline; there is no division by six. Pair creators use $F_{ij}^\dagger=a_i^\dagger b_j^\dagger-a_j^\dagger b_i^\dagger$. Creation raises area by one, and transfer preserves both closure constraints and $A_L+A_R$. The current into the left copy is

$$
I_L=i[H,A_L]=i(B^\dagger-B),\qquad B=\sum_{i<j}g_{ij}F_{ij,L}^\dagger F_{ij,R}.
$$

Thus $\langle I_L\rangle=2\operatorname{Im}\langle B\rangle$ and $I_R=-I_L$. The area repulsion here is a polyhedron-level term, not T11's face-site occupation repulsion. Fixed combined area makes the implemented space finite. Extending to unrestricted area would require a separate boundedness/partition-function analysis. These copies exchange quanta; no face sewing or spatial gluing is imposed.

## Choosing classical labels

Choose outward normals and positive face-area proportions satisfying $\sum_i a_i\mathbf n_i=0$. Spinors obey $z_i^\dagger z_i=2a_i$ and $z_i^\dagger\boldsymbol\sigma z_i=2a_i\mathbf n_i$. The fixed FL label $K_X$ sets total quantum linear area; normalized spinor norms set proportions.

The pilot uses equal unit-norm face spinors on each copy. Their norm sum is four; uniform rescaling to norm sum two leaves the normalized fixed-area ket unchanged. The reusable normal-to-spinor convention is $z=(\cos(\theta/2),e^{i\varphi}\sin(\theta/2))$. The actual complex arrays are retained in the local `inputs.npz` record; the dashboard release carries the compact summary tables. Common rotations are gauge choices and are not physical orientation controls. Face-dependent spinor phases and their relation to the channel couplings must be specified when varied; a common spinor phase only changes the overall phase of a fixed-area FL state.

Use the existing closed equal-area family at $x=1/\sqrt3$: $\phi=90^\circ$ is regular, and $\phi=30^\circ$ supplies a nondegenerate deformation. Initial states are ordinary products $|K_L,z_L\rangle\otimes|K_R,z_R\rangle$. The right input is not automatically conjugated: that convention belongs to the distinct selected T9 squeeze construction.

The three preparations are regular/regular at $(2,2)$; regular/regular at $(3,1)$; and regular/deformed at $(2,2)$. At these small areas the labels are preparation data, not a claim that the state is sharply concentrated on a classical tetrahedron.

## Stages and first pilot

1. Exact exchange and prepared-FL dynamics: implemented at combined $K=4$, including a no-exchange control. Follow mean areas, area probabilities/variance, current, weighted pair coherence, entropy, return probability, four face-area means and six flux-dot means per copy, and positive RS volumes.
2. Ground states and equilibrium: implemented for the first Hamiltonian settings. Report the uniform mixture over the full degenerate ground space. Canonical ensembles use the same finite combined-area support; they do not demonstrate dynamical equilibration.
3. Extend the controls: larger areas, broader shape/channel coverage, combined detuning and repulsion, and states coherent across individual-area sectors. This remains open.
4. Reservoir and equilibrium: couple one polyhedron to several closed subsystems; assess recurrence, relaxation and initial-state dependence. In an appropriate weak-coupling large-reservoir limit, compare with $e^{-\beta(H_L-\mu A_L)}/Z$. Do not assume this limit for the two-copy pilot.
5. Compare with the selected thermal family: spectra, area distributions, entropy, volume and correlations. The existing fixed single-copy Gibbs obstruction remains applicable to that prepared reference.

The first four settings are $(g,U,\epsilon_L-\epsilon_R)=(0,0,0),(0.1,0,0),(0.1,1,0),(0.1,0,2)$, with $U_L=U_R=U$ and $\epsilon_R=0$. Times are 101 equally spaced points over $[0,20]$ in the chosen energy units. Thermal data use $\beta=0,0.5,2,10,100$. Positive volume retains repository normalization; energy scales are model parameters.

## Verification and interpretation

The one-unit analytic control has $\langle A_L(t)\rangle=\cos^2(2|g|t)$ for a left-area-one FL seed, equal area energies, and all six equal transfer channels. A separate joint-occupation calculation checks transfer without assuming the projected operator. Creator leakage, basis closure, Hermiticity, current commutators, trajectory norm/energy, and independent sparse exponential propagation are checked.

Pilot results and numerical evidence are in [the report](../results/t9a-singlet-exchange/README.md). The equal-area mean can stay fixed while the area distribution broadens and entanglement grows; mean area alone cannot establish absence of exchange. Highly degenerate ground spaces do not select a unique tetrahedron. No reservoir simulation or thermalization claim follows from these finite-system results.

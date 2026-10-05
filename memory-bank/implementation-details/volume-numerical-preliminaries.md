# Shared Preliminaries for Volume Numerics
*Last Updated: 2026-10-05 10:49:54 IST*

This page defines notation and conventions reused by the volume calculation
notes. Task-specific inputs, algorithms, and results belong in the linked
task specifications and evidence records.

## Indices, oscillators, and spin

- $i,j,k$ label legs (or faces) at a vertex; $N$ is the number of legs.
- Each leg $i$ has Schwinger bosons $a_i,b_i$ and occupations
  $n_{a_i},n_{b_i}$.
- The angular momentum operators are

  $$
  J_i^x=\frac{a_i^\dagger b_i+b_i^\dagger a_i}{2},\qquad
  J_i^y=\frac{a_i^\dagger b_i-b_i^\dagger a_i}{2i},\qquad
  J_i^z=\frac{a_i^\dagger a_i-b_i^\dagger b_i}{2}.
  $$

- A fixed-occupation leg has spin
  $j_i=(n_{a_i}+n_{b_i})/2$, with
  $\vec J_i^{\,2}=j_i(j_i+1)$ in the dimensionless operator convention.
- $K_{\mathrm{Fock}}=\sum_i(n_{a_i}+n_{b_i})$ is the total boson number.
  It is not the same symbol as the FL area label $J$ below.
- Older T5 scan notes often write bare $K$ for this total boson number.
  For the FL fixed-area state in this note, $K_{\mathrm{Fock}}=2J$.

## The FL fixed-area state used in the T5c pilot

The pilot uses the Freidel–Livine (FL) fixed-area intertwiner from Eq. (38)
of [Freidel and Livine, arXiv:1005.2090](https://arxiv.org/abs/1005.2090),
not a distinct Freidel–Speziale (FS) state. For spinors
$z_i\in\mathbb C^2$, not necessarily normalized individually, define

$$
F_{ij}^\dagger=a_i^\dagger b_j^\dagger-a_j^\dagger b_i^\dagger,
\qquad
F_z^\dagger=\sum_{i<j}[z_j|z_i\rangle F_{ij}^\dagger,
$$

where the code convention is $[z_j|z_i\rangle=z_{j,0}z_{i,1}-z_{j,1}z_{i,0}$.
The normalized state is

$$
|J,z\rangle=\frac{(F_z^\dagger)^J|0\rangle}
{\|(F_z^\dagger)^J|0\rangle\|}.
$$

When a generic state symbol is useful, write
$|\psi_{J,z}\rangle\equiv|J,z\rangle$.
$J$ is the nonnegative integer power of the pair creator and the total
dimensionless area label in this construction. Each pair creator adds two
bosons, so $K_{\mathrm{Fock}}=2J$. Individual $j_i$ can vary across
occupation components; $J$ is not the spin on every leg.

For closed coherent labels, require

$$
\sum_i |z_i\rangle\langle z_i|=A(z)\mathbbm 1,
\qquad A(z)=\frac12\sum_i\langle z_i|z_i\rangle.
$$

Given closed classical face data with area fractions $a_i>0$,
$\sum_i a_i=1$, unit spinors $\chi_i$ with Bloch vectors $n_i$, and
$\sum_i a_i n_i=0$, choose $z_i=\sqrt{2a_i}\,\chi_i$. These labels obey
the closure identity with $A(z)=1$. The FL expectation of the individual
face spin is $\langle j_i\rangle=J a_i$ ([Freidel–Livine, Eq. (63)](https://arxiv.org/html/1005.2090#S3.SS5));
individual $j_i$ still fluctuate.
Thus unequal area ratios can be represented by weighting the spinors in the
existing FL family. A common rescaling of all $z_i$ cancels when the Fock
state is normalized.

The current n=4 volume drivers pass individually unit-normalized spinors,
so their sampled classical labels have equal face-area ratios. The Python
state constructor accepts weighted spinors, but the unequal-area mapping and
volume comparison have not yet been numerically checked. In this discussion
$J a_i n_i$ are the classical face vectors associated with the labels; they
are not one-point flux expectations. The FL state is SU(2)-invariant, so
$\langle J_i^a\rangle=0$ for each leg and component $a$, while two-point
correlations such as $\langle\vec J_i\cdot\vec J_j\rangle$ can be nonzero.
Do not infer a classical normal from the one-point flux of this state.

The FL fixed-area states form a Perelomov U($N$) coherent-state family. This
pilot constructs Eq. (38) directly with the singlet-pair creator. The generic
exponential-state API in [coherent_states.py](../../coherent_states.py) is a
different implementation/parameterization used by other calculations.
FL identifies the fixed-area family above; FS names the spinorial phase-space
framework. An FL numerical result does not validate an FS construction.

## Spinors and normals

For a normalized spinor $z=(z_0,z_1)^T$, its unit Bloch vector is

$$
n(z)=z^\dagger\vec\sigma z,
$$

where $\vec\sigma$ are the Pauli matrices. A convenient representative for
a unit vector with polar angles $(\theta,\alpha)$ is

$$
z(\theta,\alpha)=
\begin{pmatrix}\cos(\theta/2)\\e^{i\alpha}\sin(\theta/2)\end{pmatrix}.
$$

The spinor phase convention is part of the state construction; the Bloch
vector records only the corresponding ray direction.

## Flux correlations and closure

For a state $|\psi\rangle$, define the real symmetric flux-correlation
matrix

$$
G_{ij}=\sum_{a=x,y,z}\langle\psi|J_i^aJ_j^a|\psi\rangle
=\langle\psi|\vec J_i\cdot\vec J_j|\psi\rangle.
$$

On the diagonal use the local Casimir,
$G_{ii}=\langle j_i(j_i+1)\rangle$. For an SU(2)-invariant state this is
the trace over spatial components of its two-point covariance; it is not a
matrix of one-point fluxes. Gauge invariance gives

$$
\sum_i\vec J_i|\psi\rangle=0,\qquad G\mathbf 1=0.
$$

$G$ is positive semidefinite. A tetrahedron reconstructed by factoring
$G=XX^T$ requires rank three, the closure null vector, and nondegeneracy.
These conditions must be checked for each state. They do not establish that
the factor rows are the unique or physically correct classical face vectors
for every quantum state.

The row norm $\sqrt{G_{ii}}$ is an RMS flux length in dimensionless spin
units. It is not $|\langle\vec J_i\rangle|$ and is not automatically the
classical face area.

## Classical tetrahedron from closed face-area vectors

For four closed, rank-three oriented area vectors $F_i$, choose three that
meet at one vertex and arrange their orientation so
$\det(F_1,F_2,F_3)<0$. A coordinate reflection may be used because it leaves
their Gram matrix unchanged. Define

$$
D=\sqrt{-8\det(F_1,F_2,F_3)},\qquad
e_1=\frac{4(F_2\times F_3)}{D},\quad
e_2=\frac{4(F_3\times F_1)}{D},\quad
e_3=\frac{4(F_1\times F_2)}{D}.
$$

The tetrahedron vertices can be taken as $0,e_1,e_2,e_3$; its volume is
$|\det(e_1,e_2,e_3)|/6$. Recompute the four outward area vectors and check
their Gram matrix against the input. This dual construction applies to
classical area vectors; using quantum flux correlations as those vectors is
an additional state-to-geometry hypothesis.

## Triple grasp and volume quantities

For three distinct legs define

$$
A_{ij}=\vec J_i\cdot\vec J_j,\qquad
\hat q_{ijk}=i[A_{ij},A_{jk}]
=\epsilon_{abc}J_i^aJ_j^bJ_k^c.
$$

Write $q_{ijk}=\langle\psi|\hat q_{ijk}|\psi\rangle$ for its signed
expectation. The transformed signed-mean proxy is

$$
V_{\mathrm{proxy}}=(\gamma\hbar)^{3/2}\sqrt{|q_{ijk}|}.
$$

This is not the expectation of a positive volume operator. In the project
code, the positive vertex prescriptions are

$$
\hat V_{\mathrm{RS}}=c_{\mathrm{RS}}\sum_{I<J<K}\sqrt{|\hat q_{IJK}|},
\qquad
\hat V_{\mathrm{AL}}=c_{\mathrm{AL}}
\sqrt{\left|\sum_{I<J<K}\varepsilon_{IJK}\hat q_{IJK}\right|}.
$$

In these sums $I,J,K$ are leg indices, not the FL area label $J$ or
$K_{\mathrm{Fock}}$. The embedding sign $\varepsilon_{IJK}$ is distinct
from the Levi-Civita symbol $\epsilon_{abc}$ in the triple grasp.
The calculated quantities are $\langle\hat V_{\mathrm{RS}}\rangle$ and
$\langle\hat V_{\mathrm{AL}}\rangle$. The AL signs describe an embedded
oriented graph and must be supplied; spinors or face normals alone do not
fix them. The signed-mean proxy, $\langle\hat q^2\rangle$, and positive
RS/AL expectations are distinct observables.

Unless a calculation says otherwise, the project prefactor is
$(\gamma\hbar)^{3/2}$ with $\gamma=0.2375$ and $\hbar=1$. Outputs using
this convention are project-normalized values. The standard physical
regularization constants and $8\pi\ell_P^2$ factors have not been selected.

The Python and Rust positive-volume routines use dense Hermitian
diagonalization on populated blocks and discard eigenvalues satisfying

$$
|\lambda|\le64\epsilon_{\mathrm{mach}}\max(1,\rho(|Q|)).
$$

They refuse an active fixed-spin block larger than 512. This is a numerical
implementation convention, not a physical regularization.

## Documentation map

- [Volume-positivity numerical studies](./volume-positivity-studies.md):
  T5 program, recorded scope, and open study questions.
- [T5c flux-covariance reconstruction and comparison](./T5c-flux-covariance-volume-comparison.md):
  state family, shape labels, geometry algorithm, observables, pilot, and
  completion evidence.
- [Volume operator](./volume-operator.md): implemented RS/AL prescriptions,
  checks, and current limitations.
- [T6 Minkowski reconstruction](./T6-minkowski-polyhedron.md): kinematic
  and state-derived polyhedron reconstruction.
- [Fock-space construction](./fock-space-construction.md): oscillator basis
  and singlet-pair construction.
- [Grassmannian embedding](./grassmannian-embedding.md): plane coordinates,
  Plücker data, and signed-mean results.
- [Rust port architecture](./rust-port-architecture.md): implementation
  modules and cross-language structure.
- [Verification protocol](./verification-protocol.md): independent checks
  and acceptance evidence.
- [Red-team audit](./red-team-audit.md): claim limits and numerical pitfalls.
- [Performance benchmarks](./performance-benchmarks.md): tested ranges and
  costs.
- [Thermofield-double volume](./thermofield-double-volume.md): T7 states and
  volume observables at finite temperature.
- [Open ideas](./open-ideas-park.md): related speculative directions.

The task registry is in [tasks.md](../tasks.md). Numerical protocols and
generated data are referenced by each task specification. Run logs preserve
provenance and results and should not be used as definitions of the
mathematical model.

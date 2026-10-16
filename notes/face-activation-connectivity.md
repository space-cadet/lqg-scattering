# Can a closed four-face state connect to five or six faces?

[Research map](quantum-geometry-research.md) · Related: [quantum planar rotor energy transfer](quantum-planar-rotor-energy-transfer.md), [geometric area redistribution](geometric-area-redistribution.md).

*Hamiltonian connectivity before time evolution, October 16, 2026.*

Before asking how quickly area spreads, we should check that the proposed
Hamiltonian allows the required transitions at all. Does it connect states
with area on four channels to states with area on five or six, and does
imposing geometric closure prevent those connections?

The answer is yes: both the full fixed-number space and its exactly closed
singlet subspace contain explicit four-to-five-to-six transitions. The
calculation below establishes the required operator connections. The
subsequent [dynamical study](geometric-area-redistribution.md) measures how
strongly these channels become populated.

## What changes and what stays fixed

Each channel has two Schwinger modes, with

$$
n_i=a_i^\dagger a_i+b_i^\dagger b_i,\qquad
j_i=\frac{n_i}{2},\qquad
\mathbf J_i^2=\frac{n_i(n_i+2)}4.
$$

We set $\hbar=1$. A channel is active when $n_i>0$. The fixed linear area is
$K=\sum_i j_i=N_b/2$. This is the repository's linear-area convention;
$\sum_i\sqrt{j_i(j_i+1)}$ is a different area observable and is not generally
conserved by the hopping term.

We test

$$
H=\alpha\sum_i\mathbf J_i^2
-t\sum_{\langle ij\rangle}(E_{ij}+E_{ji}),\qquad
E_{ij}=a_i^\dagger a_j+b_i^\dagger b_j.
$$

The Casimir term is diagonal in the local occupations. It cannot activate
an empty channel. The hopping term can: $E_{ij}$ takes one boson from $j$
and puts it in $i$. Total occupation, and hence $K$, stays fixed.

The Hamiltonian commutes with every component of total angular momentum.
Consequently an exact singlet remains closed, and a state in a nonzero-total-spin
sector stays nonclosed. Merely having zero mean angular momentum is not closure.

The proposed Casimir term also connects to the earlier implementation:

$$
\alpha\sum_i\mathbf J_i^2
=\frac{\alpha}{4}\sum_i n_i(n_i-1)
+\frac{3\alpha}{4}N_b.
$$

At fixed $N_b$, the existing onsite-repulsion builder therefore represents
this Hamiltonian with $U=\alpha/2$, up to the displayed constant.

## Why one extra face is allowed

Suppose channel $i$ is empty and its neighbor $j$ has definite occupation
$n_j$. On any normalized state with these definite occupations,

$$
\|E_{ij}|\psi\rangle\|^2
=\langle\psi|E_{ji}E_{ij}|\psi\rangle=n_j.
$$

The empty destination makes this identity independent of the magnetic
coupling of the occupied channels. If $n_j\geq2$, the donor remains occupied,
and the number of active channels increases by one. For $n_j=1$, the donor
empties, so the active count is unchanged. Since $E_{ij}$ commutes with total
angular momentum, the same reasoning applies inside the singlet subspace.

An allowed edge from a multiply occupied donor to an empty receiver is thus
a sufficient condition for a direct activation from a definite occupation
pattern. The diagonal Casimir coefficient does not change this matrix element.

## An explicit closed four-to-five-to-six chain

Use six channels on the ring $1-2-3-4-5-6-1$. Take $K=3$, or six bosons,
with initial local occupations

$$
(n_1,n_2,n_3,n_4,n_5,n_6)=(2,1,1,2,0,0).
$$

There are four active channels, including two donors that can each give away
one boson. Define

$$
F_{ij}^\dagger=a_i^\dagger b_j^\dagger-b_i^\dagger a_j^\dagger,\qquad
|\psi_4\rangle=\frac{(F_{14}^\dagger)^2F_{23}^\dagger}{\sqrt{24}}|0\rangle.
$$

Each pair creator is an SU(2) scalar, so this normalized state is exactly
closed. Its occupation pattern is sharp. It is a convenient witness, not a
claim of a sharply semiclassical tetrahedron.

Now form normalized states

$$
|\psi_5\rangle=\frac{E_{61}}{\sqrt2}|\psi_4\rangle,\qquad
|\psi_6\rangle=\frac{E_{54}}{\sqrt2}|\psi_5\rangle.
$$

Their occupation patterns and Hamiltonian matrix elements are

| Transition | Local occupations after the hop | Matrix element |
|---|---|---:|
| $\psi_4\to\psi_5$ | $(1,1,1,2,0,1)$ | $\langle\psi_5|H|\psi_4\rangle=-\sqrt2\,t$ |
| $\psi_5\to\psi_6$ | $(1,1,1,1,1,1)$ | $\langle\psi_6|H|\psi_5\rangle=-\sqrt2\,t$ |

All three states are singlets. These are explicit nonzero transitions,
not conclusions drawn solely from the number of states in each sector.

A single hop cannot take four active channels directly to six. The ring
calculation nevertheless gives

$$
P_6H|\psi_4\rangle=0,\qquad
\|P_6H^2|\psi_4\rangle\|=4t^2,
$$

where $P_6$ selects exactly six active channels. Thus the actual second power
of the Hamiltonian has a nonzero six-channel component, including all
interference between the possible intermediate states.

## The same test without closure

Choose the same initial occupation pattern with every boson in an $a$ mode.
It has total spin $J=3$. Both normalized directed hops above again have
matrix element $-\sqrt2\,t$, and the ring has the same nonzero second-power
norm $4t^2$. Redistribution therefore does not require singlet closure.

We also lower that state to total magnetic number $M=0$ while keeping $J=3$.
Its mean spin vector vanishes, but $\langle\mathbf J_{\rm tot}^2\rangle=12$.
It has the same ring activation amplitudes. This provides an explicit
nonclosed comparison that cannot be mistaken for closure merely because its
mean angular momentum is zero.

## Checking the whole finite space

The primary calculation uses the complete six-channel, six-boson Fock space
of dimension 12,376 and its singlet subspace of dimension 490. Every singlet
basis vector has definite local occupations and sequential coupling labels.
At $K=3$, the closed subspaces with four, five and six active channels have
dimensions 240, 90 and 5, respectively.

For both the ring and complete graph, the direct block $P_5HP_4$ is nonzero
and has rank 90. The direct block $P_6HP_4$ vanishes. The second-power block
$P_6H^2P_4$ is tested separately in the saved results. The coupled-basis
Hamiltonian graph has one connected component in the singlet space for both
graphs, at either numerical counting threshold.

This does not say every four-channel superposition immediately activates a
fifth channel. The direct block has a 150-dimensional source kernel. Its
vectors have no first-order five-channel amplitude; that alone does not make
them permanently confined. More generally, paths between basis vectors do
not remove the need to check interference for a particular prepared state.

A five-channel $K=3$ calculation independently confirms direct four-to-five
connections. At $K=2$, only four bosons are available, so five active channels
are impossible in either the full or closed space. Turning off hopping, or
removing all links from the initially occupied channels to the two empty
receivers, makes both witness activation amplitudes zero. The disconnected
control is source-specific: a global active-count block includes other
initial placements and need not vanish.

## What this establishes for the geometric question

Closure does not obstruct the proposed redistribution: the Hamiltonian
connects exact four-channel singlets to exact five- and six-channel singlets.
It also allows these transitions without closure and preserves total spin
throughout. The six-channel example uses the minimum even boson number that
can populate more than four channels.

An active channel has nonzero spin. The subsequent
[geometric redistribution calculation](geometric-area-redistribution.md)
follows its occupation probability and positive volume. Its
[face-direction proposal](geometric-area-redistribution.md#recovering-face-directions)
explains how to determine whether activated channels have distinct normals.

The [result report](../results/t11-face-connectivity/README.md) contains the
numerical checks and reproduction commands. The [pre-run specification](../results/t11-face-connectivity/protocol.md)
fixes the scope; saved witness coefficients permit independent reconstruction.

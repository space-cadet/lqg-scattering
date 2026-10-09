# Explicit F-pair sewing: triangle, tetrahedron, two joined tetrahedra

This implements the construction recorded in `memory-bank/implementation-details/constructive-geometric-sewing-dialogue.md`. It does not update the Memory Bank or assign an energy to the sewn networks.

## Triangle seed

Each triangle has its own three edge oscillator pairs. The state is

$$|T\rangle=\mathcal N F^\dagger_{12}F^\dagger_{23}F^\dagger_{31}|0\rangle.$$

Each edge has two bosons and spin one. The normalized magnetic tensor has shape $3\times3\times3$, only six nonzero entries, and is annihilated by total spin. More general powers $(p,q,r)$ give edge twice-spins $(p+r,p+q,q+r)$, so repeated pair insertions are supported.

The oriented normalized invariant contraction is

$$C^{(j)}_{mn}=\frac{(-1)^{j-m}}{\sqrt{2j+1}}\delta_{m,-n}.$$

Only equal-spin copies are sewn. This contracts their indices; it does not add their occupation numbers. Reversing an edge changes this convention by $(-1)^{2j}$.

## One tetrahedron

Use triangles $ABC,ABD,ACD,BCD$, retaining separate copies of each edge before sewing. Contract the copies of $AB,AC,AD,BC,BD,CD$. The dual face graph is $K_4$.

At spin one on every edge, the fully contracted identity-link evaluation is $1/162$. This agrees in magnitude with the Wigner six-j symbol $\{1,1,1;1,1,1\}=1/6$, divided by $3^3$ from the six normalized sewing bras. Signs depend on ordering conventions. The evaluation is neither a state norm nor an energy.

A nontrivial closed spin-network function retains the six group/link variables. The implementation accepts spin-$j$ transport matrices and contracts each edge with $C^{(j)}D^{(j)}(g)$. Setting all transports to identity gives the number above; rotating one link changes the result. These evaluations do not compute a Haar norm or define a Hamiltonian.

## Two tetrahedra joined on ABC

To construct the exterior boundary, remove triangle $ABC$ from each tetrahedral boundary. The first patch contains $ABD,ACD,BCD$ and has open edge legs $AB,AC,BC$; the second contains $ABE,ACE,BCE$ and has corresponding open legs. Match and sew these three pairs.

This yields six exterior face nodes and nine sewn edges, the triangular-prism face graph. The new adjacencies are $ABD$--$ABE$, $ACD$--$ACE$, and $BCD$--$BCE$. They arise from the three edges of the shared face, not from a single extra face-site hopping edge.

Each open patch has just 27 magnetic components at spin one. Its raw norm is 0.032075014955; after normalization it is a singlet ket on the three exposed edge spaces. Two separate normalized patches have 729 boundary tensor entries and unit norm. Sewing their normalized boundaries gives the scalar $1/(3\sqrt3)=0.192450089730$. Direct contraction of the six exterior triangles gives 0.000197993919475 and agrees with sewing the raw patch tensors.

This is an exterior-boundary construction. It omits the common interior face from the output, rather than retaining all data of a two-cell bulk complex. A bulk construction must retain cell labels and specify the shared-face data and map separately. At identity transports the patch tensor contains very little information; it does not by itself establish tetrahedral shape or volume.

## Cost and next numerical step

Local triangle tensors require $(2j+1)^3$ entries in the equal-spin case, rather than a full unrestricted oscillator basis. Tensor contraction avoids expanding the product of all face states. Cost grows with intermediate tensor ranks, edge spins, and spin-label superpositions; networks with loops and large separators become harder. This spin-one pilot is inexpensive.

For a binding-energy comparison, specify whether the degrees of freedom are the exterior boundary or the retained two-cell bulk, then define the Hamiltonian and conserved quantities on that space. The earlier four-face-site Bose-Hubbard energies do not automatically apply to these edge-leg networks. Sewing itself is a contraction map, not fixed-number unitary evolution of the earlier eight-mode system.

## Reproduction

Run `python code/python/sewing_probes.py` in the numerical environment. Results are saved in `results/sewing-probes/summary.json` and the triangle/open-patch tensors in `results/sewing-probes/tensors.npz`.

Tests check triangle closure, normalized invariant pairing, the independent Wigner six-j value, direct-prism versus two-patch contraction, retained link-variable dependence, and invalid sewings.

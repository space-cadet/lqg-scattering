# Hamiltonian connectivity before geometric dynamics

Pre-run specification, October 16, 2026. Task T11.

At fixed boson number Nb=2K, use H=alpha sum_i J_i^2 - t sum_edges(Eij+Eji),
with hbar=1. Local counts are ni=ai+bi and Ji^2=ni(ni+2)/4. Set alpha=t=1
for the operator audit. The diagonal Casimir cannot connect distinct count
sectors. All occupation-changing matrix elements come from hopping.

Primary case: L=6, K=3 (six bosons). Compare the ring and complete graph,
and a disconnected control containing only edges among channels 0..3.
Initial exact local counts are (2,1,1,2,0,0). The explicitly closed source is
normalized (F03^dagger)^2 F12^dagger|0>. The nonclosed sources are all-a
occupation and its normalized total-spin lowering to M=0; both have J=3.
Zero mean spin is not singlet closure.

For the complete full fixed-number basis and an independently constructed
recoupled singlet basis, measure direct P5 H P4 and P6 H P4 blocks. For the
three concrete sources evaluate P5 H psi and P6 H^2 psi. Normalize their
nonzero projections to give explicit orthogonal target states and matrix
elements. Also evaluate <target6|H|normalized P5 H psi> and closure/spin
residuals of every witness. Exact H^2 amplitudes, not merely paths in a basis
graph, prevent an inference that ignores interference. No time evolution.

Count connected components of the nonzero Hamiltonian graph at thresholds
1e-10 and 1e-12. Basis graph connectivity does not imply every initial
superposition reaches every sector. Inspect ranks of singlet P5 H P4 blocks
and record dark combinations where present; do not claim universal activation.
Full-space graph components retain Na and Nb separately; SU(2) spin conservation
must be checked independently and not inferred just from these components.

Negative controls: t=0; initial support disconnected from receiving sites;
and K=2 on six available channels (Nb=4 cannot occupy five channels).
Also check L=5,K=3 for direct four-to-five connectivity. Tolerance 2e-10
for Hermiticity, orthonormality, fixed-number consistency, exact full-space
spin commutators, projection leakage and closure residuals. Compare Casimir
Hamiltonian to existing onsite builder using U=alpha/2 and the constant
3 alpha Nb/4. Report raw counts, amplitudes, basis labels, source hashes and
limitations. Face activation here means nonzero occupation, not verified
nondegenerate geometric faces, semiclassical tetrahedra or equilibration.

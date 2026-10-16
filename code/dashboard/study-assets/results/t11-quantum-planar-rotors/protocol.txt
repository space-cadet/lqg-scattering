# Four quantum planar rotors: first energy-transfer benchmark

Specified before production evolution, October 16, 2026.

We study a four-site ring with edges 01,12,23,30 and
$H=\frac{\epsilon^2}{2}\sum_i m_i^2+\sum_{\langle ij\rangle}[1-\cos(\theta_i-\theta_j)]$,
with $i\epsilon\partial_\tau\psi=H\psi$. Here $I=\lambda=1$ and
$\epsilon=\hbar/\sqrt{I\lambda}=1$. This pilot does not take a classical limit.

The initial states are exactly $|m,-m,0,0\rangle$, for $m=2,4$.
Their packet kinetic energies are 4 and 16; the mean potential energy is 4.
All four angles are initially uniform, with independent relative angles.
The first pair has nonzero signed momenta, the second has exactly zero
kinetic energy. Total momentum is exactly zero, not merely zero on average.
This differs from the earlier nearly aligned classical packet preparation.

Use sparse Galerkin projection onto $|m_i|\leq c$ and $\sum_i m_i=0$.
Run cutoffs 8,10,12, extending if needed. Propagate to $\tau=20$ at 0.2
intervals. Compare time-dependent local kinetic means, single-rotor entropy
(natural logarithms), return probability, energy conservation, and boundary
probability. Target successive-cutoff agreement: kinetic means below 1e-5
absolute, entropies and returns below 1e-5, with boundary probability below
1e-7 at the largest accepted cutoff. Extend the cutoff if those fail.
These are computational acceptance criteria, not thermalization criteria.

Classical comparison: 2048 independent uniform angle samples, seed 20261016,
with exact momenta $(m,-m,0,0)$ in every sample. The initial quantum state has
a positive momentum-eigenstate Wigner measure with precisely these classical
marginals; matching it does not imply quantum/classical agreement at later
times. Report sampling standard errors. Use velocity Verlet with dt<=0.005
and repeat with half step using identical samples. Require kinetic ensemble
means to change by less than 1e-3 absolute under step refinement. Check total
momentum and energy per trajectory. Classical momenta can become continuous;
quantum momenta remain integer multiples of epsilon.

Report cold-pair kinetic energy divided by initial packet kinetic energy,
individual kinetic means, and single-site entanglement entropy. A cold site
can acquire energy despite zero mean momentum. Finite four-site transfer,
recurrence, or entanglement is not evidence of thermalization, a thermodynamic
limit, three-dimensional singlet dynamics, or polyhedral geometry. No
quantum/classical-limit claim or tunneling attribution follows from this pilot.

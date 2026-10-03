# Thermofield Double Construction for the Volume-Positivity Program

**Status:** 🔄 IN PROGRESS — T7a–T7e results are recorded for their tested constructions; broader temperature-dependent coherent-sector response remains open.
**Priority:** HIGH (opens a new branch of the program — thermal states on real momenta)
**Created:** 2026-09-20
**Status updated:** 2026-10-01

## Background and motivation

The red-team audit found a narrower starting point: real-plane Perelomov
states have **zero signed triple-grasp mean**, including real planes outside
the positive cell. A tested positive-plane state has nonzero
<tg-math>\langle q^2\rangle</tg-math>, so zero positive quantum volume has
not been established. Selected complex perturbations turn on the signed mean.

Deepak's proposal (2026-09-20): instead of complexifying momenta,
**double the system** via the thermofield double (TFD) construction.
Thermal states are mixed states of real momenta; purifying them yields
a single pure state on a doubled Hilbert space in which all one-sided
expectation values are real and thermal. Volume may then emerge from
the thermal ensemble rather than from complexification.

Aspirational long-term context (not the focus of this task): the TFD is
the canonical two-sided black-hole (wormhole) state in AdS/CFT. If the
TFD of the spin-network vertex carries a genuine interior volume
encoded in L–R correlations, that is a candidate concrete LQG wormhole
state. Worth keeping in view, premature to center.

## Why the TFD is attractive here — three concrete reasons

1. **Computational freeness.** The natural thermal Hamiltonian
   <tg-math>\hat{H} = \sum_i \omega_i (a_i^\dagger a_i + b_i^\dagger b_i)</tg-math>
   is occupation-diagonal. The Euclidean factor <tg-math>e^{-\beta\hat{H}/2}</tg-math>
   rescales Fock amplitudes directly — no Taylor series, no convergence
   parameter, no truncation bug, exact at any K. Temperature is a
   computationally free lever.
2. **Thermal analogue of T5b.** T5b found V ~ eps^{0.5} off-cell. Thermal
   excitation is a different continuous deformation (populating higher
   Fock sectors coherently rather than deforming the plane). Comparing
   the thermal exponent to 0.5 tests whether the sqrt onset is a
   universal feature of "leaving the pure coherent state" or specific to
   complexification.
3. **Two-sided observables.** The doubled state gives access to L–R
   chirality correlators <tg-math>\langle q_L q_R\rangle</tg-math> and
   their relation to the entanglement entropy across the doubling —
   observables invisible in any single-copy experiment.

## Construction

Doubled Schwinger system: edges i = 0..n-1, each with L and R copies of
(a_i, b_i). Hamiltonian (choose omega_i = 1 by default; unequal
frequencies are a later refinement):

<tg-math-block>
\hat{H} = \sum_i \omega_i \left[ (a_{iL}^\dagger a_{iL} + b_{iL}^\dagger b_{iL}) + (a_{iR}^\dagger a_{iR} + b_{iR}^\dagger b_{iR}) \right]
</tg-math-block>

TFD state at inverse temperature beta, built from the (real) moment-curve
plane and the T5 reference convention:

<tg-math-block>
|\mathrm{TFD}(\beta)\rangle = \frac{1}{\sqrt{Z}} \sum_n e^{-\beta E_n / 2}\, |n\rangle_L \otimes |n\rangle_R^*
</tg-math-block>

where |n> runs over the fixed-K (or capped-K) occupation basis of the L
system built from the Perelomov state on the real plane, and * denotes
amplitude conjugation on the R copy.

Implementation note: since H is occupation-diagonal, the exponential is
applied per Fock component: amplitude c_n -> c_n e^{-beta E_n / 2},
followed by joint normalization. The R copy's conjugation makes the
combined state the canonical purification; one-sided expectations of any
real-observable operator equal the thermal mixed-state value.

## Subtasks

Ordered: the single-copy step comes first and is load-bearing, not just
pedagogy -- it yields a small theorem that motivates the doubling.

- **T7a -- Single-copy thermal state (recorded complete for the tested n=4,5 capped systems).** Build rho_beta = e^{-beta H}/Z on
  ONE Schwinger system at the real moment-curve plane (n = 4, 5, K = N+3
  to match T5b). Compute and report:
  (i) thermal areas Tr(rho_beta A_i) -- nonzero, giving the thermal area
  spectrum;
  (ii) mean signed triple grasp Tr(rho_beta q) -- expected to be zero, since
  rho_beta is diagonal in the Fock basis and <n|q|n> = 0 for every real
  Fock state (the same real-amplitude cancellation as T5b).
  Verify this numerically; an occupation-diagonal ensemble has zero signed
  mean, which does not imply zero positive volume;
  (iii) fluctuations Tr(rho_beta q^2) -- nonzero despite that cancellation.
- **T7b -- TFD construction (recorded complete for the Gibbs TFD tested).**
  Verify that the reduced density matrix of L equals rho_beta and that the
  L|R entanglement entropy matches the Gibbs entropy. Correction to the
  original prediction: as beta -> infinity, the Gibbs TFD approaches the
  Fock-vacuum product, not a Perelomov state. The Gibbs weights do not retain
  the coherent plane. A Perelomov-weighted TFD has a beta-independent,
  dephased marginal and is not the Gibbs purification.
- **T7c -- Two-sided chirality correlator (recorded complete for the Gibbs TFD tested).** With the same occupation-basis matrix for $q$ on both copies, the tested Gibbs TFD obeys <q_L q_R>(beta) = -Tr(rho_beta q^2) across the recorded beta sweep. This sign is convention dependent: representing the right operator by the conjugated matrix reverses it. The identity does not hold for the Perelomov-weighted TFD, whose Schmidt weights are nonuniform within energy sectors.
- **T7d -- Thermal scaling laws (recorded complete for the Gibbs TFD tested).**
  The beta sweep shows no reliable power law. At low temperature the
  correlator follows an approximately e^(-3 beta) onset, consistent with
  the leading occupied sector needed by q. Capped-basis results are
  quantitative for beta >= 1 and qualitative for beta <= 0.5.
- **T7e -- Complexified momenta in the TFD (recorded complete for a fixed-K
  construction).** The tested Perelomov-phase state gives an approximately
  quadratic epsilon response in the two-sided correlator and is beta-flat,
  because beta rescales a single fixed-energy sector uniformly. This answers
  the question for that construction only; it does not establish a general
  V(epsilon,T) law. A broader test requires a defined multi-K coherent
  reference or a physically justified non-uniform-frequency ensemble.

## Parameters and conventions

- gamma = 0.2375, hbar = 1 (unchanged from T5 series).
- Volume: V = (gamma*hbar)^{3/2} sqrt(|q|), q = -2 Im<A01 psi|A12 psi>,
  triple (0,1,2), vertex_reference convention (one a-boson per edge +
  one b-boson on each edge of the measured triple).
- Plane: real moment-curve plane for T7a–T7d Gibbs calculations; T7e applies
  the T5b imaginary perturbation to the coherent fixed-K reference.
- Engine: numpy/scipy is sufficient at n = 4, 5, K ~ 8 for T7a–T7c;
  the no-Taylor property removes the K ceiling that constrained T5e.
  Rust port only if T7d or larger n needs it.

## Caveats

1. The T5e lesson applies: every Perelomov number must carry a
   convergence flag. The TFD rescaling is exact, but the underlying
   Perelomov state feeding it must be built with the converged Taylor
   (8K+50 cap + assert) or the expm route.
2. Finite-K cutoff: the thermal ensemble is over a capped Fock space,
   not the infinite tower. At small beta (high T) the cutoff bites;
   report beta-vs-Kmax validity bounds per run.
3. Reference-state dependence: thermal averages depend on the reference
   (the coherent label Z). All comparisons to T5b must hold the
   reference convention fixed.

## Related documentation

- [Shared volume numerical preliminaries](./volume-numerical-preliminaries.md)
- [T5 volume-positivity studies](./volume-positivity-studies.md)
- [Volume operator](./volume-operator.md)
- [Fock-space construction](./fock-space-construction.md)
- [Verification protocol](./verification-protocol.md)
- [Red-team audit](./red-team-audit.md)
- [Performance benchmarks](./performance-benchmarks.md)

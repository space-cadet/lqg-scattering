# Thermofield Double Construction for the Volume-Positivity Program

**Status:** ⬜ PROPOSED
**Priority:** HIGH (opens a new branch of the program — thermal states on real momenta)
**Created:** 2026-09-20

## Background and motivation

The volume-positivity program has hit a consistent wall: the Perelomov
coherent state has **zero volume on the positive (real) Grassmannian
cell** (T1b, T5b). Volume turns on only by complexifying the plane
(moving off-cell), which breaks the reality of the scattering momenta.

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

- **T7a -- Single-copy thermal state.** Build rho_beta = e^{-beta H}/Z on
  ONE Schwinger system at the real moment-curve plane (n = 4, 5, K = N+3
  to match T5b). Compute and report:
  (i) thermal areas Tr(rho_beta A_i) -- nonzero, giving the thermal area
  spectrum;
  (ii) mean volume Tr(rho_beta q) -- expected to be EXACTLY ZERO, since
  rho_beta is diagonal in the Fock basis and <n|q|n> = 0 for every real
  Fock state (same argument as T5b's "real amplitudes -> V = 0").
  Verify this numerically; state it as a result, not an aside: no ensemble
  diagonal in the occupation basis carries volume;
  (iii) volume fluctuations Tr(rho_beta q^2) -- nonzero; this is where the
  thermal state's volume information actually lives.
- **T7b -- TFD construction.** Purify rho_beta into |TFD(beta)> on the
  doubled system. Verify: (i) reduced density matrix of L equals rho_beta
  (trace over R); (ii) at beta -> infinity the state reduces to the pure
  Perelomov state on L; (iii) entanglement entropy S(beta) across L|R --
  should match the thermal entropy of rho_beta, S = beta(<H> - F).
- **T7c -- Two-sided chirality correlator.** Measure <q_L q_R>(beta) on the
  TFD. This is now motivated by T7a: the mean volume vanished on one copy,
  so the volume signal, if present, must live in correlations. Compare
  <q_L q_R> against Tr(rho_beta q^2) (they should be related through the
  purification) and against S(beta).
- **T7d -- Thermal scaling laws.** Sweep beta (e.g. beta = 0.1 .. 10) and
  fit the correlator: <q_L q_R> ~ T^alpha. Compare with T5b's V ~ eps^0.5
  universality. Deviations are interesting either way; report honestly
  including noise-dominated regimes.
- **T7e -- Complexified momenta in the TFD (open, careful).** NOT
  subsumed by the above. Open question: what happens when the plane
  defining the doubled state is itself complexified (C + i*dC), so that
  the "thermal ensemble" lives on off-cell kinematics? Does
  complexification commute with purification, does the thermal ensemble
  wash out the off-cell volume, or does it reshape the V(eps) law into
  V(eps, T)? Runs separately from T7d; treat as a distinct experiment
  with its own protocol, not a parameter tweak.

## Parameters and conventions

- gamma = 0.2375, hbar = 1 (unchanged from T5 series).
- Volume: V = (gamma*hbar)^{3/2} sqrt(|q|), q = -2 Im<A01 psi|A12 psi>,
  triple (0,1,2), vertex_reference convention (one a-boson per edge +
  one b-boson on each edge of the measured triple).
- Plane: real moment-curve plane, seeds per existing convention; a fixed
  small imaginary row dC is NOT applied in T7a–T7c (that is T7d's job).
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

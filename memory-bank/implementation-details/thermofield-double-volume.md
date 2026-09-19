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

- **T7a — TFD construction.** Build |TFD(beta)> on the doubled Schwinger
  system for n = 4, 5 at fixed K (start K = N+3 to match T5b). Verify:
  (i) at beta -> infinity the state reduces to the pure Perelomov state
  on L tensor the vacuum structure on R; (ii) one-sided thermal
  expectation of the area operator reproduces a Boltzmann-weighted
  average over the capped-K ensemble; (iii) the reduced density matrix
  of L is thermal, tr_rho_L^2 < 1 at finite beta.
- **T7b — Thermal volume law.** Measure V(beta) on the L copy over a
  beta sweep (e.g. beta = 0.1 .. 10, i.e. T = 10 .. 0.1). Fit
  V ~ T^alpha. Hypothesis (probe, not established): alpha ~ 0.5, the
  same universality class as T5b's V ~ sqrt(eps). Deviations are
  interesting either way: alpha < 0.5 suggests thermal smearing kills
  volume faster than off-cell deformation; alpha > 0.5 would be
  surprising. Report honestly including noise-dominated regimes.
- **T7c — Two-sided chirality correlator.** Measure
  <tg-math>\langle q_L q_R\rangle(\beta)</tg-math> and compare against the
  one-sided <tg-math>\langle q_L\rangle</tg-math> and the L–R entanglement
  entropy S(beta). Questions: does the two-sided correlator vanish at
  high T (maximal mixing) and grow as T -> 0? Is its magnitude bounded
  by the thermal entropy budget?
- **T7d — Complexified momenta in the TFD (open, careful).** NOT
  subsumed by the above. Open question: what happens when the plane
  defining the doubled state is itself complexified (C + i*dC), so that
  the "thermal ensemble" lives on off-cell kinematics? Does
  complexification commute with purification, does the thermal ensemble
  wash out the off-cell volume, or does it reshape the V(eps) law into
  V(eps, T)? Runs separately from T7b; treat as a distinct experiment
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

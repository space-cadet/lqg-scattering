# Session handoff: channel count, classical rotor equilibration and quantum continuation

*Recorded: 2026-10-16 11:43:41 IST*

## Scope and conversation record

This session began with mem-load and the last session's face-activation/equilibration question. It ended with the decision to continue the quantum rotor example in a new session. The [Markdown transcript](2026-10-16-equilibration-and-rotors-transcript.md) contains all 58 retained user/assistant prose messages through the user's save request, including progress messages. Its [JSON companion](2026-10-16-equilibration-and-rotors-transcript.json) preserves the original text and timestamps. Tool calls, tool outputs, setup instructions and expanded skill definitions are excluded.

The user emphasized that channel count, rather than increasing area at a fixed channel count, is the central system-size comparison. Geometry reconstruction was explicitly deferred: study equilibration first. Later the user supplied the rotor interpretation, with kinetic energy proportional to $\mathbf J_i^2$, and requested classical calculations before quantum evolution.

## Initial quantum FL channel pilot and resource assessment

The first implementation used exact singlet-sector hopping plus onsite repulsion, with normalized complete-graph hopping $t_{ij}=1/(L-1)$. Fixed-area FL states occupy four nonzero input spinor labels, with additional zero spinors. Their occupations fluctuate; they are not states with four sharply occupied faces.

The pilot has 42 trajectories: $K=2$, $L=4,5,6,7$ and $K=3$, $L=4,5,6$; $U=0,1,5$; two phase choices. It measures concentration, additional-channel area, occupied-count distributions, returns and residence near an exact dephased reference. Degenerate energy-projector coherences are retained. An energy-matched canonical benchmark is saved, but it does not match permutation-sector weights and cannot by itself test thermalization.

Results depend on interaction strength and preparation; more channels do not consistently improve residence. The user correctly questioned the relevance of $K=3$ to a large initial tetrahedron. At $K=2$, more than four channels cannot be occupied simultaneously. This pilot is numerical preparation, not an answer to the large-area problem.

Files: `code/python/t11_equilibration.py`, `verify_t11_equilibration.py`, `results/t11-equilibration/`. Independent free-FL/probability checks: 252,840 comparisons, including 714 analytic comparisons; maximum residual $1.88\times10^{-13}$. Existing regression suite then had 46 tests.

The exact singlet dimension is

$$
d_{L,K}=\frac{1}{K+1}\binom{K+L-1}{K}\binom{K+L-2}{K}.
$$

For $K=10$, dimensions at $L=4,5,6$ are 1,716; 26,026; 273,273. One dense complex matrix at the last size requires approximately 1.2 TB. This motivated discussing sparse and coherent-state/semiclassical methods. The transcript contains the FL variational energy and equations; no interacting large-area FL variational evolution was implemented.

## Physical clarification and prior literature

The user's central picture is initially concentrated energy spreading through an interacting system, with long residence near equilibrium compatible with eventual recurrence. Prior-session precedents were revisited: FPUT mode-energy redistribution and delayed equipartition; Trotzky's Bose-gas density-wave relaxation; Kaufman's entanglement/local thermal behavior; Newton's cradle as a near-integrable counterexample; and Rigol's ETH framework. Site-localized rotor energy differs from FPUT's usual initially excited normal modes.

A coupling made only from $\mathbf J_i\cdot\mathbf J_j$ preserves each local Casimir $\mathbf J_i^2$. Orientation-dependent interactions are required for the proposed rotor kinetic energies to change. For zero total angular momentum, two equal-inertia rotors necessarily have equal kinetic energies, so the energetic-pair/cold-rest preparation needs at least three rotors.

## Classical ring study

The adopted model is

$$
H=\sum_i\frac{\mathbf J_i^2}{2I}
+\lambda\sum_i(1-\mathbf q_i\cdot\mathbf q_{i+1}),
\quad |\mathbf q_i|=1,\quad \mathbf q_i\cdot\mathbf J_i=0.
$$

It is a model of classical linear rotors, not fixed-area intertwiner dynamics. Total angular momentum is zero; total area $\sum_i|\mathbf J_i|$ is not constrained. All completed rotor production studies have $I=1$. The initial ring scan also fixes $\lambda=1$.

The initial orientations are small generic three-dimensional perturbations of alignment, using seeds 1701–1703. Only two neighboring rotors initially move; they carry equal-and-opposite tangent momenta. Both fixed packet energy and approximately fixed energy density were compared for $N=8,16,32,64$ at energy parameters 1, 10, 100. Actual total energy includes the initial potential background.

There are 72 production histories, of which 63 are unique because the two scalings coincide at $N=8$, and ten full-duration half-step controls. Two independent microcanonical chains per production case enforce energy and zero total angular momentum. Their orientation weight is $[E-V]^{N-5/2}/\sqrt{\det B}$ with $B=\sum_i(I-\mathbf q_i\mathbf q_i^{\mathsf T})$. Split-Rhat is at most 1.0033 for the readouts used.

Moderate fixed packets spread, with selected late-time observables and distributions close to microcanonical references. High packets retain about 99% of local total energy in the original pair through $t=2000$. That is finite-time trapping, not permanent localization. The illustrations, definitions and qualifications are in [the classical account](../../notes/classical-rotor-equilibration.md). Saved outputs: `results/t11-classical-rotors/`; two figure pairs under `figures/t11-classical-rotors/`. This stage passed 50 regression tests and 12,399,912 independent scalar audits.

## Few-rotor mechanism and coupling

The user asked whether a large chain was necessary to understand parameter dependence. We reduced two aligned planar rotors with one initially moving and the other at rest to a free collective rotation plus a pendulum:

$$
H=\frac{P^2}{4I}+\frac{p^2}{I}+\lambda(1-\cos\phi),
\qquad P=p_1+p_2,\quad p=(p_1-p_2)/2.
$$

The relative energy is $T_0/2$ and the barrier is $2\lambda$. For $T_0<4\lambda$, full velocity exchange is possible. For $T_0>4\lambda$,

$$
\frac{T_{2,\max}}{T_0}
=\left[\frac{1-\sqrt{1-4\lambda/T_0}}2\right]^2.
$$

At high ratio the maximum fraction scales as $(\lambda/T_0)^2$. At ratios 10 and 100 it is 1.27017% and 0.0102051%. The exact boundary requires the stated planar preparation; it is not a general three-dimensional or many-body cutoff.

We ran 14 pair histories, 63 generic three-dimensional controls on a triangle, four-site open chain and four-site ring, six half-step controls, plus symmetry/scaling checks. Generic controls have zero total angular momentum and fixed initial packet kinetic energy 100 while coupling varies from 0.1 to 100. Stronger coupling permits substantial cold-rotor kinetic energy, with a nonmonotonic response in the stronger-coupling regime.

An exactly symmetric planar triangle with opposite moving momenta and an initially resting third rotor leaves the third rotor stationary by torque cancellation. It is an invariant special preparation, not evidence against generic transfer.

See [the mechanism note](../../notes/few-rotor-energy-transfer.md), `results/t11-few-rotors/`, and `figures/t11-few-rotors/`. This stage passed 54 tests.

## Larger-ring coupling crossover and delayed release

At the user's request, we scanned 14 ratios $r=E_{\rm packet}/\lambda$ on $N=8,16,32,64$ with three seeds: 168 primary histories. Explicit coupling, half-step, long-time and fixed-physical-time controls add 29 histories, giving 197 histories and 409 saved window summaries. The transfer metric is cold kinetic energy divided by initial packet kinetic energy, not local energy with a potential share.

At matched scaled time $\tau=t\sqrt{\lambda/I}$, the classical equations depend on $r$. Thus any operational packet-energy crossover scales as $E_c=\lambda r_c(N,\tau,\mathrm{preparation},\mathrm{criterion})$. At fixed physical time, the scaled observation time changes with coupling, so a time-dependent coefficient must be retained.

The main transfer drop is near ratios 14–20, with threshold and size dependence. The secondary half-response brackets over three seeds are 16–18 for $N=8$, 14–16 for $N=16,32$, and 12–16 for $N=64$. This secondary summary was added after inspection and is identified as such. The predefined significant/suppressed criteria are at least 10% / at most 1% mean transfer; full threshold sensitivity is saved.

At fixed packet energy 100 in the 64-rotor ring, mean cold kinetic fractions over the same physical interval $t=200$–approximately 2000 are 0.196%, 3.03%, and 49.6% at $\lambda=1,5,10$ for seed1701.

The decisive longer-time finding is $N=8,r=18$: all three seeds transfer below 1% through $\tau=2000$, but the longer mean through 10,000 is 29–32%; a half-step repetition gives 30.6%. Some apparent cutoffs therefore become delayed release. The timing is not converged precisely. A larger $N=64,r=16$ example also releases more energy later, with substantial sensitivity of its quantitative timing.

Maximum relative energy drift is $7.05\times10^{-5}$. All 56 regression tests pass. Independent audits cover 33,916,477 scalar quantities. Sources, protocols and results are under `code/python/*t11_rotor*`, the reusable rotor library, `code/classical/rotors.cpp`, and `results/t11-rotor-coupling/`. See [the coupling note](../../notes/rotor-coupling-crossover.md) and its figure pair.

## Quantum continuation: discussion only

The user explicitly deferred quantum rotor work to the next session. No quantum rotor solver or tunneling result was implemented. This does not negate the earlier, separate small-K quantum FL pilot.

The proposed mechanical quantization uses $\mathcal H_i=L^2(S^2)$, local kinetic energies $\hbar^2j_i(j_i+1)/(2I)$ and the same orientation interaction. The local angular-momentum labels must be allowed to change; a fixed-spin Heisenberg model would freeze the proposed kinetic energies. For these linear rotors, $j$ is integer.

The first proposed benchmark is the quantum planar pair, with

$$
\hat H_{\rm rel}=-\frac{\hbar^2}{I}\partial_\phi^2+\lambda(1-\cos\phi).
$$

The relative wavefunction's periodic or antiperiodic boundary condition depends on the conserved total-angular-momentum sector; this must be specified before implementation. The associated rotation-state splitting can produce a transfer time of order $\pi\hbar/\Delta E$ when a two-state description applies. It is a proposed calculation, not a result inferred from the classical scan.

The independent dimensionless quantum parameter is $\epsilon=\hbar/\sqrt{I\lambda}$ alongside $r$. Classical comparison requires matched initial distributions: a sharp angular-momentum state has delocalized orientation and is not the same preparation as a localized classical rotor. After the pair benchmark, use three/four three-dimensional rotors in the total-angular-momentum-zero sector; study kinetic-energy distributions, transfer and entanglement, with cutoff and semiclassical convergence checks.

## Documentation check and working state

The user requested a transcript and an assessment of existing homes for a pedagogical write-up in their style, with all relevant figures and tables. [The note assessment](../../notes/equilibration-session-note-map.md) inventories the three illustrated rotor notes, the earlier face-energy note and thermal/exchange note. Existing rotor notes contain four figures and five tables; resource, small-K/FL-variational and quantum-continuation material still needs integration into the recommended narrative.

The transcript and this handoff were saved; the existing scientific notes were not rewritten during the assessment. No new simulation ran for the transcript request. No main Memory Bank cache, task registry or global memory was updated. No commit, push, deployment or dashboard publication occurred. Earlier untracked work and `.playwright-mcp/` remain preserved. Continue from the quantum formulation, not by restarting the classical study.

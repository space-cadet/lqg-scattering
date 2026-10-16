# Coupling strength and the apparent energy-transfer cutoff

[Research map](quantum-geometry-research.md) · Related: [few rotor energy transfer](few-rotor-energy-transfer.md), [quantum planar rotor energy transfer](quantum-planar-rotor-energy-transfer.md).

*Larger classical rotor rings, October 16, 2026.*

The large-ring tests confirm strong coupling dependence, but they also show why the word cutoff needs a time qualifier. The main transfer drop occurs in a fairly narrow range of initial packet energy relative to coupling. Some states that look trapped through scaled time 2,000 release substantial energy by 10,000. The calculation measures a finite-time crossover, not a permanent localization threshold.

![Coupling crossover and delayed transfer](../figures/t11-rotor-coupling/coupling-crossover.png)

*Left: mean kinetic energy acquired by initially resting rotors, over scaled times 200–2,000. Bands span three orientation seeds. Middle: explicitly changing coupling at fixed initial packet kinetic energy 100; curves use the equivalent dimensionless scans, while circles are direct integrations at the physical coupling. Right: longer trajectories reveal delayed release. The gray vertical line marks the end of the initial scan.*

## The system and comparison

We retain the three-dimensional linear-rotor ring

$$
H=\sum_i\frac{\mathbf J_i^2}{2I}
+\lambda\sum_i(1-\mathbf q_i\cdot\mathbf q_{i+1}),
\quad |\mathbf q_i|=1,\quad \mathbf q_i\cdot\mathbf J_i=0.
$$

All runs have $I=1$ and zero total angular momentum. Rotors 0 and 1 carry equal-and-opposite tangent momenta initially; all other rotors have zero kinetic energy. Orientations use the same three small three-dimensional perturbations as the previous study, seeds 1701–1703. The degree remains two for every ring size, so increasing $N$ does not increase an individual rotor's number of couplings.

The main scan covers $N=8,16,32,64$ and 14 ratios

$$
r=E_{\rm packet}/\lambda
\in\{2,4,6,8,10,12,14,16,18,20,25,30,50,100\},
$$

with three seeds: 168 primary trajectories. Each ends at scaled time $\tau=2000$. Explicit physical-coupling checks, half-step refinements, longer runs and equal-physical-duration controls bring the total to 197 trajectories. Initial potential energy is additional to the packet kinetic energy and is recorded separately.

We measure transfer using kinetic energy outside the original pair:

$$
F_{\rm cold}(\tau)
=\frac{\sum_{i\geq2}\mathbf J_i(\tau)^2/(2I)}{E_{\rm packet}}.
$$

This avoids counting a share of bond potential energy as activation of an initially resting rotor. Even in equilibrium, this fraction need not approach one: energy remains in the original rotors and in the interaction potential. The study concerns energy transfer, not a new equilibrium-ensemble calculation.

## What coupling scaling can and cannot tell us

Define

$$
\tau=t\sqrt{\lambda/I},\qquad
\boldsymbol\ell_i=\frac{\mathbf J_i}{\sqrt{I\lambda}}.
$$

Then

$$
\frac H\lambda=\sum_i\frac{\boldsymbol\ell_i^2}{2}
+\sum_i(1-\mathbf q_i\cdot\mathbf q_{i+1}).
$$

At fixed graph, orientations and dimensionless initial momenta, the equations therefore depend on $r$, not on $\lambda$ independently. At a matched scaled observation time, an operational crossover has the form

$$
\boxed{E_{\rm packet,c}=\lambda\,r_c(N,\tau,\text{preparation},\text{criterion}).}
$$

The linear coupling factor follows from exact rescaling. The numerical work determines the coefficient, its size and seed dependence, and whether a finite-time apparent cutoff survives longer evolution. It would be misleading to fit an independent scaling exponent to redundant rescalings of the same equations.

At a fixed physical time $t$, coupling also changes how much scaled evolution has elapsed:

$$
E_{\rm packet,c}(\lambda,t)
=\lambda\,r_c\!\left(N,t\sqrt{\lambda/I},\ldots\right).
$$

Consequently a finite-physical-time apparent cutoff need not look purely linear if delayed transfer moves the crossover as the observation time grows.

## The measured crossover

The primary protocol calls mean transfer of at least 10% significant and mean transfer of at most 1% suppressed. These are explicit diagnostic thresholds, not a phase-transition definition. Sensitivities at 0.5%, 1%, 2%, 5% and 10% are saved.

To describe the main drop separately from the small transfer tail, a secondary analysis locates where transfer falls to half its low-ratio response. For each size and seed, the baseline is the mean response at $r=2,4,6,8,10$. This summary was introduced after inspecting the initial scan and is marked as such in the analysis protocol. No interpolation between energy-grid points is used.

At $\tau\in[200,2000]$:

| Rotors | Half-response crossover bracket, envelope over seeds | First persistently below 1% transfer, range over seeds |
|---:|---:|---:|
| 8 | $16<r_c<18$ | $r=18$ |
| 16 | $14<r_c<16$ | $r=18$–20 |
| 32 | $14<r_c<16$ | $r=25$ |
| 64 | $12<r_c<16$ | $r=30$–50 |

Here a bracket means the lower sampled ratio remains above half response and the upper sampled ratio is below it; it is not an uncertainty interval from a statistical fit. The last column uses the sampled ratios only and requires every tested larger ratio to remain below the threshold for that seed.

For example, the $N=32$ half-response bracket corresponds to packet energies between approximately $14\lambda$ and $16\lambda$ in this observation window. The strictly suppressed tail extends to higher ratios as more rotors are available to acquire small amounts of kinetic energy. A single cutoff number would hide that distinction.

The exact two-rotor boundary $T_0=4\lambda$ does not apply to this ring preparation. That benchmark had one moving rotor, nonzero total angular momentum and a conserved relative pendulum energy. This scan starts with a compensating energetic pair and has additional degrees of freedom through which pairwise relative energy can change.

## Directly changing lambda at fixed packet energy

We explicitly integrated $\lambda=5,10$ with $E_{\rm packet}=100$ at every ring size, complementing the $\lambda=1$, $r=100$ controls. Early-time scaled transfer histories match the equivalent $\lambda=1$ histories to better than $9.0\times10^{-16}$. Late-time individual histories are sensitive to accumulated numerical perturbations, so their means are compared separately rather than requiring pointwise agreement over the full interval.

We also ran $N=8,64$ at a common physical duration approximately 2,000. Using the same physical late window $t\in[200,2000]$, the mean transferred kinetic fractions for seed 1701 are:

| Rotors | $\lambda=1$ | $\lambda=5$ | $\lambda=10$ |
|---:|---:|---:|---:|
| 8 | 0.0257% | 0.632% | 37.8% |
| 64 | 0.196% | 3.03% | 49.6% |

The physical end times differ from 2,000 by less than 0.061 because outputs lie on a fixed scaled-time grid. These controls support the qualitative conclusion under a common physical clock as well: increasing coupling can turn weak transfer into substantial transfer for the same initial momenta. They are single-seed controls, not a full map of physical-time cutoff coefficients.

## A short-time cutoff can become delayed transfer

The $N=8$, $r=18$ case is particularly informative. At $\lambda=1$, its mean cold kinetic fraction through scaled time 2,000 is below 1% for all three seeds. Extending the same initial conditions to $\tau=10000$ gives mean fractions over $[200,10000]$ of 31.6%, 29.0% and 30.1%. A half-step repetition gives 30.6% for seed 1701.

For seed 1701, the mean fraction in successive illustrative blocks is about 0.74% over $[0,2000)$, 15.1% over $[2000,4000)$, and 45.7% over $[4000,6000)$. These are the same deterministic preparation with no added driving or noise. The onset time is not asserted to be numerically converged, but the existence of substantial delayed transfer within the tested longer interval survives both the other seeds and the smaller step.

The larger ring shows delayed behavior too. At $N=64,r=16$, the mean fraction increases from 10.6% over $[200,2000]$ to 24.4% over $[200,10000]$ for seed 1701; the smaller-step longer run gives 15.4%. Both transfer substantially, but their quantitative timing remains sensitive. At $N=64,r=20$, the longer-run mean is still only 3.4%.

The main new physical finding is therefore a competition of timescales: rapid relative rotation suppresses short-time transfer, while additional degrees of freedom can eventually permit leakage and release. These simulations do not yet determine a distribution of escape times or prove that every high-energy packet ultimately equilibrates.

## Numerical verification and limits

The integrator is the existing exact kick/rotation splitting, extended to record per-rotor kinetic energies and explicit physical $\lambda$ and $I$. An independent general-graph solver cross-checks its physical-unit readouts. Total angular momentum, tangency, orientation lengths, energy and local-energy accounting are checked.

The maximum production/follow-up relative energy drift is $7.05\times10^{-5}$. Independent saved-array audits check 33,916,477 scalar quantities. Their maximum local-energy sum error is $1.43\times10^{-13}$, and direct endpoint energies agree within $8.53\times10^{-14}$. All 56 regression tests pass.

Six short-window half-step controls and two longer half-step controls are included. The short-window transfer means change by as much as 3.23 percentage points near the crossover. One $N=64,r=16$ control crosses the arbitrary 10% threshold when the step is halved. This reinforces reporting a band and threshold sensitivity rather than a precise critical value. Long-time transfer timing is less well determined than conservation errors alone would suggest.

The full scan uses three related orientation seeds and one special equal-and-opposite hot-pair preparation. It does not characterize all initial conditions or graph topologies. The apparent cutoff remains dependent on observation time and transfer criterion. No phase transition, permanent localization, quantum result, or polyhedral geometry is claimed. Finer output sampling for residence metrics, more initial packets and escape-time statistics remain future work.

The [numerical record](../results/t11-rotor-coupling/README.md) contains the protocols, trajectories, brackets, physical-time comparison and validation. Results remain local; the dashboard and Memory Bank were not changed.

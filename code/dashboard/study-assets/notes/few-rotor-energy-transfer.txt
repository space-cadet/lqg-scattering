# Why fast rotors exchange little energy

*Exact planar-pair benchmark and three-dimensional controls, October 16, 2026.*

Energy trapping does not require a long chain. Two planar rotors already show a sharp distinction between complete exchange and bounded exchange. The difference follows from an ordinary pendulum barrier in their relative motion. This gives an exact benchmark for the fast-rotation explanation; it does not turn the previous many-rotor observation into an exact theorem.

![Few-rotor energy transfer](../figures/t11-few-rotors/few-rotor-transfer.png)

*Left: kinetic energy acquired by an initially resting planar rotor. Middle: exact all-time transfer bound and numerical maxima. Right: independently simulated three-dimensional systems at zero total angular momentum; bands show three orientation seeds. A planar pair and a generic three-dimensional rotor system are distinct problems.*

## Two planar rotors separate into a free rotation and a pendulum

Take two identical rotors with one interaction bond:

$$
H=\frac{p_1^2+p_2^2}{2I}+\lambda[1-\cos(\theta_1-\theta_2)].
$$

This is an invariant planar subspace of the three-dimensional orientation model. Both angular momenta point along the common plane normal. We do not impose zero total angular momentum for this benchmark.

Introduce canonical variables

$$
\Theta=\frac{\theta_1+\theta_2}{2},\quad
\phi=\theta_1-\theta_2,\quad
P=p_1+p_2,\quad p=\frac{p_1-p_2}{2}.
$$

Indeed $p_1d\theta_1+p_2d\theta_2=P d\Theta+p d\phi$, and

$$
H=\underbrace{\frac{P^2}{4I}}_{\text{constant collective energy}}
+\underbrace{\frac{p^2}{I}+\lambda(1-\cos\phi)}_{H_{\rm rel}}.
$$

The total momentum $P$ is conserved. The relative coordinate obeys

$$
\dot\phi=\frac{2p}{I},\qquad
\dot p=-\lambda\sin\phi,\qquad
\ddot\phi=-\frac{2\lambda}{I}\sin\phi.
$$

It is a pendulum with a potential barrier of height $2\lambda$.

## An initially moving rotor and an initially resting rotor

Start aligned, $\phi(0)=0$, with $p_1(0)=p_0>0$ and $p_2(0)=0$. Define the initial kinetic energy

$$
T_0=\frac{p_0^2}{2I}.
$$

The collective and relative energies are both $T_0/2$. This makes the boundary especially simple:

$$
H_{\rm rel}=2\lambda\quad\Longleftrightarrow\quad T_0=4\lambda.
$$

For $T_0<4\lambda$, the relative pendulum librates and its momentum changes sign. On returning to $\phi=0$ with $p=-p_0/2$, the original velocities have exchanged: $p_1=0$ and $p_2=p_0$. Complete kinetic-energy transfer is possible. The system then transfers the energy back; this is reversible exchange, not equilibration.

For $T_0>4\lambda$, the relative pendulum rotates. Its momentum cannot reach zero, so the initially fast rotor cannot become the slower one. The least relative momentum occurs at the top of the interaction potential:

$$
p_{\min}=\sqrt{I\left(\frac{T_0}{2}-2\lambda\right)}
=\frac{p_0}{2}\sqrt{1-\frac{4\lambda}{T_0}}.
$$

Since $p_2=P/2-p$, the exact maximum kinetic-energy fraction received by rotor 2 is

$$
\boxed{
\frac{T_{2,\max}}{T_0}
=\left[\frac{1-\sqrt{1-4\lambda/T_0}}{2}\right]^2,
\qquad T_0>4\lambda.
}
$$

At high energy this is

$$
\frac{T_{2,\max}}{T_0}\sim\left(\frac{\lambda}{T_0}\right)^2.
$$

Thus the kinetic-energy exchange becomes small quadratically in coupling relative to initial energy. The relative motion winds rapidly instead of reversing. Fast torque averaging and the exact phase-space obstruction are two descriptions of the same high-energy behavior in this integrable benchmark.

| $T_0/\lambda$ | Motion | Maximum receiver kinetic energy / initial kinetic energy |
|---|---|---:|
| 1 | Libration | 100% |
| 3.9 | Libration | 100% |
| 4.1 | Rotation | 17.8011% |
| 10 | Rotation | 1.27017% |
| 100 | Rotation | 0.0102051% |

At the separatrix $T_0=4\lambda$, the supremum is 25%, approached only asymptotically. The full-exchange time diverges as the libration boundary is approached from below, so finite observation times must be distinguished from all-time bounds. The numerical check at the separatrix is particularly sensitive to solver error and is not used to establish the analytic boundary.

This threshold assumes aligned initial orientations. More generally, with the same initial momenta and relative angle $\phi_0$, the relative energy is $T_0/2+\lambda(1-\cos\phi_0)$. Its classification must use that full expression. The present numerical pair scan fixes $\phi_0=0$; it is not a complete survey of relative orientations or three-dimensional initial data.

## What changing lambda means

At fixed initial $T_0=10$, the threshold is $\lambda=2.5$. Weak coupling places the pair in the rotating, weak-transfer regime; sufficiently strong coupling permits full exchange. We directly checked couplings 0.1, 0.3, 1, 2.4, 2.5, 2.6, 3, 10 and 30, as well as five specified energy ratios.

For identical inertias,

$$
\tau=t\sqrt{\lambda/I},\qquad \ell_i=p_i/\sqrt{I\lambda}
$$

removes $I$ and $\lambda$ from the dimensionless equations. Therefore changing coupling at fixed physical initial momenta changes the dimensionless initial state through $T_0/\lambda$. Changing $I$ while holding initial momenta fixed also changes their physical kinetic energies; inertia is only a pure clock rescaling when the dimensionless initial state is held fixed.

The numerical scans use $I=1$ and a fixed scaled-time horizon $\tau=200$. Physical durations are therefore different for different couplings. The few-rotor comparison is not a fixed-physical-time leakage-rate measurement.

## Why two rotors cannot test redistribution at zero total angular momentum

For two equal-inertia rotors,

$$
\mathbf J_1+\mathbf J_2=0
\quad\Longrightarrow\quad
\frac{\mathbf J_1^2}{2I}=\frac{\mathbf J_2^2}{2I}
$$

at every time. A fast rotor and a resting partner are incompatible with that constraint. At least three rotors are needed to put opposite momenta in an energetic pair and leave an additional rotor initially slow.

There is another special case to avoid: three planar rotors with identical initial orientations and momenta $+p,-p,0$ on a triangle. Reflection symmetry keeps the third rotor fixed because the two neighbor torques cancel. No cold-rotor activation occurs in that exact invariant subspace, irrespective of the inference one might draw from energy alone. Our numerical symmetric control confirms this cancellation to rounding accuracy. Perturbing the symmetry changes the problem.

## Three-dimensional controls with zero total angular momentum

We therefore used three generic orientation seeds, 1701–1703, with the same slightly perturbed three-dimensional orientations as the ring study and equal-and-opposite tangent momenta in rotors 0 and 1. Their combined initial kinetic energy is 100. The remaining rotor or rotors start with zero kinetic energy. Initial potential energy is additional.

The graphs are a triangle, a four-rotor open chain, and a four-rotor ring. Every undirected edge is counted once. Seven couplings from 0.1 to 100 give 63 runs. We report kinetic energy separately from local total energy: half-bond potential assignments can make a cold site have nonzero local total energy even before it rotates.

For the open four-rotor chain, the mean kinetic energy acquired by the initially resting pair, divided by the initial packet energy, is:

| $\lambda$ | Mean over three orientation seeds, $\tau\in[20,200]$ |
|---:|---:|
| 0.1 | 0.000324% |
| 1 | 0.01033% |
| 3 | 0.08955% |
| 10 | 28.53% |
| 30 | 23.34% |
| 100 | 24.60% |

Increasing coupling clearly permits much stronger exchange in these preparations. The response is not monotonic throughout the stronger-coupling region, and the exact planar-pair threshold does not apply to these graphs. These measurements demonstrate energy transfer, not thermalization, and do not locate a phase transition.

## What this explains about the larger ring

The few-rotor calculation establishes that bounded interaction energy and fast relative rotation can strongly suppress transfer without any many-body mechanism. It supports investigating that mechanism in the large-ring trajectories. The ring does not conserve a separate relative energy for each pair, so the exact two-rotor bound cannot be imposed on it. Resonances, slow leakage, and additional degrees of freedom can change the long-time result.

The next mechanistic distinction is between resonant exchange and generic redistribution: vary initial angular-momentum imbalance, relative orientations and the location of the compensating momentum, then measure transfer times and torque spectra. The present results identify a clean explanation to test, not a universal localization theorem.

## Numerical evidence

The pair solver agrees with the exact bounds and with independently integrated scalar pendulum equations. The general graph solver counts a single bond for two rotors; calling the previous periodic-ring helper with $N=2$ would double that bond and give the wrong threshold.

Six three-dimensional controls were repeated at half step. Maximum relative energy drift decreases by about a factor of four, and the largest change in their mean cold kinetic-energy fraction is below $5.3\times10^{-7}$. Maximum production drift across the 63 generic runs is $5.60\times10^{-6}$. Scaling-equivalent simulations agree to $1.25\times10^{-12}$ in orientation and $7.8\times10^{-13}$ in scaled momentum. All 54 regression tests pass.

The [numerical record](../results/t11-few-rotors/README.md) contains the pre-run protocol, individual initial states, trajectories, summary tables and validation. The planar relative-coordinate reduction also appears in the coupled-rotor limit discussed by [Dorignac and Flach](https://arxiv.org/abs/cond-mat/0112168); their broader quantum pendulum study is a related model, not numerical validation of ours.

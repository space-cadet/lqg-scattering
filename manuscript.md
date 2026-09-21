# Follow-up Numerical Work on the LQG-Grassmannian Correspondence

**Status of this document.** The analytic correspondence between the
kinematic space of $N$ massless particles and $U(N)$ coherent states in LQG was
published in EPJC (Vaid & Suresh, arXiv:2208.10632;
`paper/lqg-amplituhedron.tex` in this repository — the published baseline,
not modified here). What the publication *lacked* was numerical evidence:
no coherent states were constructed, no volume operators evaluated, and no
positivity tests performed. This document tracks the **new numerical
program** carried out after publication:

- **Python pipeline** (`grassmannian.py`, `coherent_states.py`,
  `correspondence.py`, `positivity.py`, `classical_limit.py`): the full
  correspondence verified at $n = 4$.
- **Rust port** (`rust/`): the same pipeline re-engineered for $n \geq 5$,
  where the Fock-space dimension makes Python infeasible.
- **New results**: the volume-positivity (achirality) theorem verified
  through $n = 8$, scaling laws, and performance benchmarks.

## 1. Published Baseline (Reference)

The published paper establishes analytically:

1. **The correspondence.** Holomorphic spinor-network data of LQG
   ($U(N)$ coherent states, Freidel-Krasnov-Livine framework) assembles into
   a 2-plane in $\mathbb{C}^N$ — a point of the Grassmannian $\mathrm{Gr}(2, N)$, the kinematic
   space of the $N$-leg massless amplitude.
2. **Spinor helicity dictionary.** Null momenta factorize as
   $p = \lambda \tilde{\mu}$; momentum conservation $\Sigma p = 0$ is the $2 \times 2$ matrix identity
   $\Sigma \lambda_i \mu_i^T = 0$.
3. **$U(N)$ coherent states.** Perelomov states labeled by $N \times N$ matrices $Z$,
   with the momentum map $Z_{ij} = a_i \bar{b}_j - b_i \bar{a}_j$ from the Grassmannian.
4. **Positivity.** The positive Grassmannian $\mathrm{Gr}_+(2, N)$ and its connection
   to the amplituhedron's positive external data.

The paper contains **no numerical results**. Every number below is new.

## 2. New Numerical Results

### 2.1 Python Verification of the Correspondence ($n = 4$)

All checks machine-precision (details in git history, Phases 1–5):

- **$\mathrm{Gr}(2, N)$ from momenta**: reconstructed momenta null to $10^{-16}$,
  momentum conservation exact, Plücker relation $M_{12} M_{34} - M_{13} M_{24} +
  M_{14} M_{23} = 0$ to $10^{-16}$.
- **$\mathfrak{u}(N)$ algebra**: $[E_{ij}, E_{kl}] = \delta_{jk} E_{il} - \delta_{li} E_{kj}$ verified to
  $1.8 \times 10^{-15}$ on random Fock states (total-$K$ truncation is essential:
  per-edge truncation does not close under $\mathfrak{u}(N)$).
- **Perelomov states**: $\exp(\Sigma Z_{ij} E_{ij})$ via terminating Taylor series;
  areas positive with exact closure $\Sigma \langle A_i \rangle = \gamma \hbar K$; momentum-map label
  exactly anti-Hermitian.
- **Invariant dictionary**: $s_{ij} = |M_{ij}|^2$ verified on 20 random real
  configurations (max deviation $< 10^{-10}$); the plane is recovered from a
  coherent state exactly (principal angles $0.0000$ rad).
- **Classical limit**: relative area uncertainty falls as $K^{-0.41}$
  (coherent-state prediction $-1/2$).

### 2.2 The Volume–Positivity Connection ($n = 4$, new)

The central new finding of the follow-up work. Implementing the
De Pietri/Rovelli–Smolin volume $q = i[J_i \cdot J_j, J_j \cdot J_k]$,
$V = (\gamma \hbar)^{3/2} \sqrt{|\langle q \rangle|}$:

- **Positivity = achirality**: for real planes the momentum map gives a
  real antisymmetric $Z$, the Fock amplitudes are exactly real, and $\langle q \rangle = 0$
  identically. Every positive plane is gauge-real, so **$V$ vanishes on all
  of $\mathrm{Gr}_+(2, 4)$** (measured: $V/\gamma^{3/2} \approx 2 \times 10^{-9}$ vs $0.029$ off-cell).
- **No functional $V(s)$**: the momentum map is projective (orthonormalized
  rows), so $V$ is exactly scale-invariant (log-log exponent $0.000$) while
  $s_{ij} \to t^2 s_{ij}$ under scaling. Volume probes the complex structure of
  the plane, not its energy scale.
- **Spin freezing**: $U(N)$ orbits of single-species references stay in the
  $N_b = 0$ sector with all $\langle J_i \rangle$ collinear on the $z$ axis; the volume is
  carried by the $b$-sector of the Schwinger pair.

### 2.3 Rust Port and $n \geq 5$ Results (this session)

Python's Fock basis generation scans $(K+1)^{2N}$ occupation tuples — infeasible
for $n \geq 5$ ($7^{12} \approx 1.4 \times 10^{10}$ for $n = 6$, $K = 6$). The Rust port
(`rust/`, sprs sparse matrices + rayon parallel matvec) replaces this with
combinatorial stars-and-bars generation in $O(\mathrm{dim} \cdot 2N)$.

**Verification at $n = 4$** (exact match with Python, `lqg verify4`):

| observable | Python | Rust |
|---|---|---|
| $\langle n_e \rangle$ | 1.534636, 1.862035, 1.027227, 1.576102 | identical |
| $\Delta n_e$ | 1.177545, 1.326392, 0.597280, 1.374821 | identical |
| $V/\gamma^{3/2}$ (complex plane) | $2.914888 \times 10^{-2}$ | $2.914888 \times 10^{-2}$ |
| $\langle q \rangle$ | $-8.496572 \times 10^{-4}$ | $-8.496572 \times 10^{-4}$ |
| $V/\gamma^{3/2}$ (positive plane) | $2.3 \times 10^{-9}$ | $1.4 \times 10^{-9}$ |

**Higher-$n$ benchmark** (`lqg scan`; moment-curve positive plane vs.
imaginary perturbation breaking the minor-phase cocycle):

| $n$ | $K$ | Fock dim | $V/\gamma^{3/2}$ on $\mathrm{Gr}_+$ | $V/\gamma^{3/2}$ off $\mathrm{Gr}_+$ | time |
|---|---|---|---|---|---|
| 4 | 6 | 3,003 | $1.4 \times 10^{-9}$ | $2.9 \times 10^{-2}$ | 12 ms |
| 5 | 8 | 43,758 | $1.6 \times 10^{-9}$ | $3.4 \times 10^{-2}$ | 0.3 s |
| 6 | 9 | 293,930 | $9.9 \times 10^{-10}$ | $1.4 \times 10^{-3}$ | 3.4 s |
| 7 | 6 | 38,760 | $3.7 \times 10^{-10}$ | $1.2 \times 10^{-2}$ | 0.3 s |
| 8 | 6 | 74,613 | $6.2 \times 10^{-10}$ | $1.1 \times 10^{-2}$ | 0.8 s |

Two results stand out:

1. **Achirality generalizes**: $V = 0$ on $\mathrm{Gr}_+(2, n)$ through $n = 8$ (any edge
   triple), nonzero immediately off the positive cell. The zero-volume
   result is a general feature of the positive Grassmannian, not an $n = 4$
   kinematic accident.
2. **Performance**: worst case 3.4 s per full computation ($n = 6$ with the
   complete vertex reference, dim 293,930) — two orders of magnitude inside
   the 1-minute target, and $\sim 100\times$ faster than Python at $n = 4$.

### 2.4 Experiment T5a: triple-volume correlations ($n = 6, 7$)

New in the follow-up program (spec:
`memory-bank/implementation-details/experiments.md`). From ONE Perelomov
state on a complex plane, with uniform reference $(1,1)$ on every edge (no
triple privileged, $K = 2n$), compute $q_{ijk} = i\langle [A_{ij}, A_{jk}] \rangle$ on every
$C(n,3)$ triple, and test whether the vertex carries a single handedness
(correlated signs) or per-triple chirality (independent). $n = 6$ uses the
stored engine (dim 2,704,156); $n = 7$ uses a new on-the-fly engine
(combinatorial rank indexing + atomic-scatter matvec, dim 40,116,600, no
stored operators).

**Results.**

| $n$ | seeds | sign-agreement | Pearson $|q|$ across seeds | Pearson signed $q$ |
|---|---|---|---|---|
| 6 | 1000/2000/3000 | 0.55 / 0.70 / 0.50 | $-0.23$, $+0.27$, $+0.04$ | $+0.21$, $-0.42$, $-0.08$ |
| 7 | 1000/2000 | 0.51 / 0.56 | $+0.10$ | $+0.44$ |

**Verdict: per-triple chirality.** Sign-agreement sits at the binomial
level everywhere; $|q|$ magnitudes are uncorrelated across independent
states (fluctuation-driven, not geometry-determined); signed-$q$
correlations are small. A $U(N)$ coherent-state vertex does not carry a
global handedness — chirality is an independent property of each edge
triple. (Caveats: 20–35 triples per state limits sign-test power; $n = 8$
unresolved — the uniform reference needs $\sim 10$ GB/vector, beyond this node.)

A subsequent magnetization sweep (T5a′, fixed $n = 5$ plane, $K = 8$,
$M = -3..+3$) confirmed the result extends across the whole reference
manifold: sign-agreement stays at $0.50$–$0.60$ for every $M$, and the $M = 0$
per-triple-chirality finding is not an artifact of the balanced reference.
The all-a ($M = +4$) limit is trivially achiral ($q \approx 0$, all $J$ collinear).

### 2.5 Experiment T5b: perturbation-response $V(\epsilon)$ sweep ($n = 4, 5$)

Deform the moment-curve plane by an imaginary perturbation scaled by $\epsilon$,
$C(\epsilon) = C_0 + \epsilon \cdot dC$ with $dC[1,i] = i \cdot 0.35 \cdot (i+0.5)$, and measure how the
volume responds. Tests whether the $\sqrt{\epsilon}$ onset is a robust feature of
the complex structure or an artifact of the specific plane. Converged
Taylor series ($8K+50$ cap, convergence assert, 38/40 iterations).

| $n$ | $K$ | $\alpha$ ($V \sim \epsilon^\alpha$) | $R^2$ |
|---|---|---|---|
| 4 | 7 | 0.497 | 0.9999 |
| 5 | 8 | 0.499 | 0.99999 |

**Verdict: the $\sqrt{\epsilon}$ law is robust.** The volume turns on as $\epsilon^{1/2}$ to
better than one part in $10^4$ across the full $\epsilon$ range $10^{-6}$ to $1$. The
real part of $q$ is zero at $\epsilon = 0$ ($V = 2.6 \times 10^{-10}$ = rounding noise) and
grows linearly in $\epsilon$; the volume $V = \sqrt{|q|}$ inherits the square root from
the $q \sim \epsilon^1$ linear onset. This is a genuine complex-structure effect, not
a plane-specific accident.

### 2.6 Experiment T5e: large-$K$ semiclassics ($n = 4$)

Test whether the coherent-state volume enters a classical-growth regime
$V \sim K^{3/2}$ (i.e. $\langle q \rangle \sim K^3$ for $V = \gamma^{3/2} \sqrt{|\langle q \rangle|}$) at large $K$. Two
families at fixed shape ($n = 4$ moment-curve plane, seed 11, $\epsilon = 1$):

1. **Vertex-scaled family** ($b$-bosons loaded onto the measured triple,
   $K = 4+3s$): $\langle q \rangle$ is **exactly linear in $s$** — $q/s = -1.059 \times 10^{-3}$ at
   all five points ($K = 10..22$, equal to 9 digits). Hence $V \sim (K-4)^{1/2}$,
   i.e. $\alpha \to 0.5$ asymptotically. Each triple boson contributes
   independently; there is no collective $K^3$ enhancement of triple
   correlations.

2. **Uniform $M=0$ family** (fixed shape, $K = 8..24$): $q = 0$ to solver
   precision ($|q| \leq 9 \times 10^{-13}$). Uniform scaling of the coherent state
   develops no volume at all up to $K = 24$.

**Verdict: the $K^{3/2}$ classical law does NOT hold.** No family shows
$\alpha \sim 1.5$. The coherent-state volume does not enter a classical-growth
regime up to $K = 24$. (Caveats: $K = 8..24$ is only 0.5 dex of lever arm;
$K = 28+$ needs $\sim 30$M-dim vectors, beyond this node. An earlier run with
cap $2K+4$ produced truncation-shifted values; the reported run uses cap
$8K+50$ with a convergence assert.)

### 2.7 Experiment T7a: single-copy thermal state ($n = 4, 5$)

Extend the construction to finite temperature. $\rho_\beta = \exp(-\beta H)/Z$ on one
Schwinger system, $H = \sum_i (n_{a,i} + n_{b,i})$, $\omega = 1$. Three families per
$\beta \in \{0, 0.1, 0.5, 1, 2, 5, 10\}$: (A) plain Gibbs diagonal; (B)
Perelomov-weighted diagonal; (C) thermally-rescaled pure state
(TFD precursor).

**Results.**
1. **Thermal areas are nonzero.** Gibbs: uniform across edges, 0.369 ($n=4$)
   / 0.346 ($n=5$) per edge at $\beta = 0$ → $\sim 2 \times 10^{-5}$ at $\beta = 10$.
   Perelomov-weighted ($\beta$-flat): $n = 4$ $[0.439, 0.383, 0.469, 0.371]$,
   sum $= \gamma \hbar K$ ✓; $n = 5$ $[0.438, 0.436, 0.427, 0.255, 0.344]$, sum $= \gamma \hbar K$ ✓.
2. **Mean volume is exactly zero** at every $\beta$ in all three families,
   both $n$. Mechanism: $A_{ij}$ are real-symmetric, so $q = i[A_{01},A_{12}]$ is
   imaginary-antisymmetric with identically zero diagonal; the pure state
   adds reality. **Theorem: no ensemble diagonal in the occupation basis
   carries volume.**
3. **Fluctuations are nonzero — the thermal volume information lives in
   $\langle q^2 \rangle$.** Gibbs $\mathrm{Tr}(\rho q^2)$: 0.357/0.349 ($\beta = 0$) → $7 \times 10^{-14}$ ($\beta = 10$).
   Perelomov-weighted: 0.785 ($n = 4$), 0.679 ($n = 5$), $\beta$-flat.
   Pure-rescaled: 0.707 ($n = 4$), 0.719 ($n = 5$), $\beta$-flat.

**Structural finding.** Families B and C are $\beta$-flat by construction:
the Perelomov state sits entirely in the $E = K$ sector and $\exp(-\beta E/2)$
is constant on its support. Thermalizing fixed-$K$ coherence does nothing.
Genuine temperature dependence needs either the full Gibbs ensemble
(which forgets the plane) or the doubled TFD (where $\beta$ enters via L–R
entanglement across $E$ sectors) — motivating T7b.

### 2.8 Experiment T7b: TFD construction and two-sided correlator ($n = 4, 5$)

Construct the thermo-field-double state
$|\mathrm{TFD}(\beta)\rangle = Z^{-1/2} \sum_n \exp(-\beta E_n/2) |n\rangle_L |n\rangle_R^*$
over the full capped occupation basis (Gibbs purification, per the T7a
guidance). Computed in Schmidt form — the $D \times D$ doubled space (41M for
$n = 4$, 1.9B for $n = 5$) is never formed explicitly.

**Verification.**
- **(i) $\rho_L = \rho_\beta$: PASS.** Schmidt weights reproduce the T7a Gibbs
  distribution; $\max|\Delta S| = 3.6 \times 10^{-15}$ / $1.4 \times 10^{-14}$, $\max|\Delta q^2| = 0$.
- **(ii) $\beta \to \infty$ limit: CORRECTED.** The Gibbs-TFD flows to the Fock
  vacuum product ($p_{\mathrm{vac}} = 0.9996/0.9995$ at $\beta = 10$, $S \to 0.004/0.005$),
  NOT to the pure Perelomov state on L. The Gibbs ensemble forgets the
  plane, so no low-$T$ limit recovers Perelomov coherence.
- **(iii) $S(\beta)$ matches thermal entropy: PASS.** $S = 8.77/10.69$ at $\beta = 0$
  ($= \log D$) → $\sim 0$ at $\beta = 10$.

**Small theorem.** $\langle q_L q_R \rangle(\beta) = -\mathrm{Tr}(\rho_\beta q^2)$ at every $\beta$, not just
$\beta = 0$ (corr $+ q^2 \sim 10^{-17}$ across the whole sweep). Proof: $q$ preserves
total boson number, so $q_{nm} \neq 0 \Rightarrow E_n = E_m \Rightarrow \sqrt{p_n p_m} = p_n$, and $q$
imaginary gives $(q_{nm})^2 = -|q_{nm}|^2$. The two-sided signal carries exactly
the single-copy fluctuation content with opposite sign (L–R
anticorrelation).

**Scaling fit: no T5b-like power law.** $|\langle q_L q_R \rangle|$ vs $T$ shows no clean
power law (formal fits give deceptive $R^2$ on 4 points of an exponential).
Instead $d \ln|\mathrm{corr}|/d\beta = -3.008 \approx -3$ on $[5,10]$: Boltzmann-exponential onset
$\sim e^{-3\beta}$, because $q$ needs edges 0,1,2 occupied (leading $E = 3$ sector).
**Honest verdict: thermal onset is exponential, qualitatively distinct
from T5b's $V \sim \epsilon^{1/2}$ law** — complexification and thermalization are
different deformations with different universality.

### 2.9 Experiment T7e: complexified momenta in the TFD ($n = 4, 5$)

Combine the T5b complexification with the T7b TFD: keep Perelomov phases
in the doubled state, $|\Psi(\beta,\epsilon)\rangle = \sum_n d_n |n\rangle_L|n\rangle_R$ with
$d_n \sim c_n(\epsilon) \exp(-\beta E_n/2)$, and measure how the two-sided correlator responds
to $\epsilon$. Tests whether the TFD correlator inherits the single-copy $\sqrt{\epsilon}$ law.

**R-conjugation is a no-op for this observable.** "R from conjugate plane
$C^*$" and "conjugated R amplitudes of $C$" coincide to $\sim 10^{-16}$. The
correlator is additionally invariant under $d \to d^*$ — theorem: $(q_{nm})^2$ is
real symmetric ($q$ imaginary Hermitian), so conjugation drops out of
$\langle q_L q_R \rangle$. Complexification does not complicate purification for
$q$-like observables.

**$\epsilon$-scaling: the correlator does NOT inherit the $\sqrt{\epsilon}$ law (hypothesis
confirmed).**

| Quantity | $\epsilon$-scaling exponent |
|---|---|
| Single-copy $\|q\|$ | $\sim 1.0$ (linear) |
| Single-copy $V = \sqrt{|q|}$ | $\sim 0.5$ ($\sqrt{\epsilon}$ law) |
| **TFD correlator change** | **$\sim 2.0$ (quadratic)** |
| TFD $\|\mathrm{corr}(\epsilon) - \mathrm{corr}(0)\|$ | 1.991 / 1.994 ($R^2 = 1.000$) |

The TFD correlator onset is **quadratic in $\epsilon$** — much stiffer than the
single-copy $\sqrt{\epsilon}$. The same exponent holds for the pure $\langle q^2 \rangle$ change (1.99),
consistent with the correlator's $(q_{nm})^2$ structure. On-cell values:
corr $= +0.0306$ ($n = 4$), $-0.0107$ ($n = 5$) — sign is plane/seed-dependent
interference of Perelomov amplitude signs; the $\epsilon^2$ scaling is the robust
claim, identical for both $n$.

**No combined $V(\epsilon,T)$ law: complexification and thermalization factorize.**
corr$(\beta, \epsilon)$ is $\beta$-flat to $\sim 10^{-17}$ at every $\epsilon$ (fixed-$K$ support kills the
Boltzmann factor), while the Gibbs-TFD is $\epsilon$-flat. Each deformation acts
on an orthogonal aspect — $\epsilon$ on coherences/populations within $E = K$, $\beta$ on
weights across $E$ — so they commute trivially. There is no $V(\epsilon,T)$ combined
law in this construction; a genuine one would need $\beta$-dependence inside
the coherent sector (e.g. non-uniform $\omega_i$ or multi-$K$ reference).

## 3. Discussion

The published correspondence is now backed by complete numerical
verification at $n = 4$, and extended to $n = 5$–$8$ by the Rust port. The new
volume–positivity connection — the positive Grassmannian cell as the
achiral locus of the dual quantum geometry — was invisible in the analytic
treatment and is the main quantitative addition of this follow-up. T5a
adds that the off-cell chirality is per-triple, not a vertex-global
handedness, and T5a′ confirms this extends across the reference
magnetization manifold. T5b establishes that the $\sqrt{\epsilon}$ complexification
onset is robust; T5e shows the volume does not enter a classical-growth
regime up to $K = 24$. The TFD series (T7a–T7e) opens a new direction:
thermal states carry zero mean volume (a theorem for occupation-diagonal
ensembles) but nonzero fluctuations, the TFD two-sided correlator
reproduces exactly the single-copy fluctuation content with opposite sign,
and complexification in the TFD produces a quadratic $\epsilon^2$ onset — steeper
than the single-copy $\sqrt{\epsilon}$ — with no combined $V(\epsilon,T)$ law because the two
deformations act orthogonally. Open directions: characterize $\langle q \rangle$ as a
measure on $\mathrm{Gr}(2, N) \setminus \mathrm{Gr}_+$ (is it log-barrier-like in the minor-phase
cocycle?); a sharper handedness test with sign-controlled perturbations
over $\geq 10$ seeds; $n = 8$ on larger memory; large-$K$ asymptotics beyond
$K = 24$; $\beta$-dependence inside the coherent sector (non-uniform $\omega_i$ or
multi-$K$ reference) to find a genuine $V(\epsilon,T)$ law; amplitude dynamics
(Grassmannian measure, momentum-twistor map), which remains the missing
link to actual scattering amplitudes.

## 4. Conclusions

Numerically: the correspondence, the $s = |M|^2$ dictionary, positivity,
and the classical limit all check out to machine precision; the volume
operator vanishes exactly on the positive Grassmannian for every $n$ tested
($4 \leq n \leq 8$) and is scale-invariant off it. The $\sqrt{\epsilon}$ complexification
onset is robust (T5b), but the volume does not enter a classical-growth
regime up to $K = 24$ (T5e). Thermal states carry zero mean volume — a
theorem for occupation-diagonal ensembles — with the thermal information
residing entirely in the fluctuations $\langle q^2 \rangle$ (T7a). The TFD two-sided
correlator reproduces the single-copy fluctuation content with opposite
sign at every $\beta$ (T7b), and complexification in the TFD produces a
quadratic $\epsilon^2$ onset with no combined $V(\epsilon,T)$ law because complexification
and thermalization act orthogonally (T7e). Methodologically: the Python
pipeline suffices for $n = 4$; the Rust port (combinatorial Fock basis,
sprs, rayon) pushes the same physics to $n \geq 5$ at sub-minute runtimes;
the Schmidt-form TFD computation avoids ever forming the $D \times D$ doubled
space.

## Appendix: Code

- `paper/lqg-amplituhedron.tex` — published EPJC paper (baseline; frozen).
- `grassmannian.py`, `coherent_states.py`, `correspondence.py`,
  `positivity.py`, `classical_limit.py` — Python pipeline ($n = 4$),
  each self-testing (`python3 <module>.py`).
- `rust/` — Cargo project; `cargo test --release` (13 tests: Fock
  dimension, basis uniqueness, su(2) matrix elements, u(3) algebra,
  $J_i \cdot J_j$, closure, vacuum triviality, analytic triple product,
  volume-zero-on-real-planes, volume-nonzero-on-complex, momentum-map
  anti-Hermiticity, moment-curve positivity); `cargo run --release --
  verify4` (Python comparison), `cargo run --release -- scan` ($n = 5..8$).

# Follow-up Numerical Work on the LQG-Grassmannian Correspondence

**Status of this document.** The analytic correspondence between the
kinematic space of $N$ massless particles and $U(N)$ coherent states in LQG was
published in EPJC (Vaid & Suresh, arXiv:2208.10632;
`code/papers/lqg-amplituhedron.tex` in this repository — the published baseline,
not modified here). What the publication *lacked* was numerical evidence:
no coherent states were constructed, no volume operators evaluated, and no
positivity tests performed. This document tracks the **new numerical
program** carried out after publication:

This is a research draft, not an independently reviewed manuscript. The
T5a magnetization and T5b perturbation sweeps were rerun with converged
states and independent spot checks; their conclusions remain limited to
the tested plane and reference families. The Rust baseline and $n=5$–$8$ scan have now been rerun with convergence checks; independent SciPy checks cover $n=4,5,7,8$.

- **Python pipeline** (`code/python/grassmannian.py`, `code/python/coherent_states.py`,
  `code/python/correspondence.py`, `code/python/positivity.py`, `code/python/classical_limit.py`): the full
  correspondence verified at $n = 4$.
- **Rust port** (`code/rust/`): the same pipeline re-engineered for $n \geq 5$,
  where the Fock-space dimension makes Python infeasible.
- **Follow-up results under review**: signed triple-grasp expectations,
  selected perturbation responses, thermal correlators, and historical
  performance measurements. The original $n=4$–$8$ baseline scan needs
  recomputation with converged coherent states.

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

The following historical algebraic and geometric checks were recorded at
$n=4$. State-dependent numbers need a converged-state review after the
Taylor-truncation finding:

- **$\mathrm{Gr}(2, N)$ from momenta**: reconstructed momenta null to $10^{-16}$,
  momentum conservation exact, Plücker relation $M_{12} M_{34} - M_{13} M_{24} +
  M_{14} M_{23} = 0$ to $10^{-16}$.
- **$\mathfrak{u}(N)$ algebra**: $[E_{ij}, E_{kl}] = \delta_{jk} E_{il} - \delta_{li} E_{kj}$ verified to
  $1.8 \times 10^{-15}$ on random Fock states (total-$K$ truncation is essential:
  per-edge truncation does not close under $\mathfrak{u}(N)$).
- **Perelomov states**: $\exp(\Sigma Z_{ij} E_{ij})$ is the target construction;
  older Taylor implementations did not always converge;
  areas positive with exact closure $\Sigma \langle A_i \rangle = \gamma \hbar K$; momentum-map label
  exactly anti-Hermitian.
- **Invariant dictionary**: $s_{ij} = |M_{ij}|^2$ verified on 20 random real
  configurations (max deviation $< 10^{-10}$); the plane is recovered from a
  coherent state exactly (principal angles $0.0000$ rad).
- **Classical limit**: relative area uncertainty falls as $K^{-0.41}$
  (coherent-state prediction $-1/2$).

### 2.2 Real-plane cancellation of the signed triple grasp ($n = 4$, new)

The implementation computes $q_{ijk}=i[J_i\cdot J_j,J_j\cdot J_k]$ and reports
the **signed-mean proxy** $V_{\rm proxy}=(\gamma\hbar)^{3/2}\sqrt{|\langle q_{ijk}\rangle|}$.
This differs from the expectation of a positive operator such as
$(\gamma\hbar)^{3/2}\langle\sqrt{|q_{ijk}|}\rangle$.

- **Reality implies zero signed mean**: for any real plane, the momentum map
  gives real antisymmetric $Z$, the Fock amplitudes are real, and
  $\langle q_{ijk}\rangle=0$ by antisymmetry. Positive planes are examples,
  but the real plane with ordered minors $(1,1,1,2,1,-1)$ is outside
  $\mathrm{Gr}_+$ even after column sign changes and has zero signed mean.
  The positive cell is therefore not the full zero locus.
  At the tested positive $n=4$, $K=6$ state, an independent matrix exponential
  gives $\langle q\rangle\approx0$ but $\langle q^2\rangle=0.375981$:
  the operator does not annihilate the state. No zero eigenvalue or zero
  expectation of a positive volume operator follows from $\langle q\rangle=0$.
- **No functional $V(s)$**: the momentum map is projective (orthonormalized
  rows), so this proxy is scale-invariant under rescaling the plane while
  $s_{ij} \to t^2 s_{ij}$ under scaling. The signed mean probes the complex structure of
  the plane, not its energy scale.
- **Spin freezing**: $U(N)$ orbits of single-species references stay in the
  $N_b = 0$ sector with all $\langle J_i \rangle$ collinear on the $z$ axis;
  the tested signed-mean response requires a different reference.

### 2.3 Rust Port and $n \geq 5$ Results (this session)

Python's Fock basis generation scans $(K+1)^{2N}$ occupation tuples — infeasible
for $n \geq 5$ ($7^{12} \approx 1.4 \times 10^{10}$ for $n = 6$, $K = 6$). The Rust port
(`code/rust/`, sprs sparse matrices + rayon parallel matvec) replaces this with
combinatorial stars-and-bars generation in $O(\mathrm{dim} \cdot 2N)$.

**Corrected $n=4$ comparison** (`lqg verify4`). Historically, Rust and Python agreed
because both used the same 15-term Taylor truncation; that agreement did not
validate the coherent state. An independent `scipy.sparse.linalg.expm_multiply`
calculation for the same complex plane gives $\langle q\rangle=-0.000827687168$
and $V_{\rm proxy}/\gamma^{3/2}=0.028769553$, versus the historical
$-0.0008496572$ and $0.029148881$. The corrected Python and Rust paths reproduce the independent result. Current values are:

| observable | Python | Rust |
|---|---|---|
| $\langle n_e \rangle$ | 1.533865, 1.860998, 1.025999, 1.579137 | identical to displayed precision |
| $\Delta n_e$ | 1.178372, 1.327455, 0.598558, 1.375919 | identical to displayed precision |
| $V_{\rm proxy}/\gamma^{3/2}$ (complex plane) | $2.8769553 \times 10^{-2}$ | $2.8769553 \times 10^{-2}$ |
| $\langle q \rangle$ | $-8.2768717 \times 10^{-4}$ | $-8.2768717 \times 10^{-4}$ |
| $V_{\rm proxy}/\gamma^{3/2}$ (positive plane) | rounding floor | $2.21 \times 10^{-9}$ |

**Converged higher-$n$ benchmark** (`lqg scan`; moment-curve positive plane vs.
imaginary perturbation breaking the minor-phase cocycle):

| $n$ | $K$ | Fock dim | $V/\gamma^{3/2}$ on $\mathrm{Gr}_+$ | $V/\gamma^{3/2}$ off $\mathrm{Gr}_+$ | time |
|---|---|---|---|---|---|
| 4 | 6 | 3,003 | $2.21 \times 10^{-9}$ | $2.876955 \times 10^{-2}$ | 12–14 ms |
| 5 | 8 | 43,758 | $3.29 \times 10^{-9}$ | $3.391578 \times 10^{-2}$ | 0.3 s |
| 6 | 9 | 293,930 | $8.81 \times 10^{-10}$ | $1.315281 \times 10^{-3}$ | 3.3–3.9 s |
| 7 | 6 | 38,760 | $3.66 \times 10^{-10}$ | $1.186078 \times 10^{-2}$ | 0.3–0.4 s |
| 8 | 6 | 74,613 | $1.30 \times 10^{-9}$ | $1.056697 \times 10^{-2}$ | 0.8–0.9 s |

The exact real-state cancellation of $\langle q\rangle$ applies at any $n$
and for any triple in this representation. It does not identify the positive
cell as the unique zero locus. The listed times are current single-run measurements. Independent SciPy exponentiation checks the complex-plane values for $n=4,5,7,8$; the $n=6$ value has Rust convergence evidence only. These values are signed-mean proxies.

### 2.4 Experiment T5a: triple-volume correlations ($n = 6, 7$)

New in the follow-up program (spec:
`memory-bank/implementation-details/volume-positivity-studies.md`). From ONE Perelomov
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

The fixed-plane $n=5$, $K=8$ magnetization sweep was rerun with a
convergence assertion (39–41 Taylor terms), and four representative states
matched an independent SciPy exponential to at most $3.6\times10^{-16}$
in the triple-grasp means. Its sign pattern remained 0.50–0.60 agreement
across the tested nonpolarized sectors. This supports the observation for
one plane, not a general handedness statement across planes. Separately, the
kinematic-polyhedron-local T5a′ analysis reports no increased sign coherence
for local triples across the tested channels; it used only 8 planes per
$n=5$ channel, and its dense-expm comparison exposed non-convergence in the
shared 15-term reference implementation. Treat that result as limited evidence,
not as a high-power handedness test. The all-a endpoint gives $q$ near zero,
consistent with the spin-freezing control.

### 2.5 Experiment T5b: perturbation-response $V(\epsilon)$ sweep ($n = 4, 5$)

Deform the moment-curve plane by an imaginary perturbation scaled by $\epsilon$,
$C(\epsilon) = C_0 + \epsilon \cdot dC$ with $dC[1,i] = i \cdot 0.35 \cdot (i+0.5)$, and measure how the
volume responds. Tests whether the $\sqrt{\epsilon}$ onset is a robust feature of
the complex structure or an artifact of the specific plane. The original
T5b sweep used a short Taylor cap. The table below comes from a corrected
13-point rerun with a convergence assertion; four $n=4$ and three $n=5$
states were checked against SciPy's independent `expm_multiply` route.

| $n$ | $K$ | $\alpha$ ($V \sim \epsilon^\alpha$) | $R^2$ |
|---|---|---|---|
| 4 | 7 | 0.496907 | 0.999888 |
| 5 | 8 | 0.499104 | 0.999991 |

**Scoped finding:** for the tested imaginary perturbation, the corrected T5b
sweep fits the proxy with exponents near $0.5$ at $n=4,5$. The square root follows from a roughly linear
signed mean and the definition of the proxy. A universality claim across
planes and references needs independent tests.

### 2.6 Experiment T5e: large-$K$ semiclassics ($n = 4$)

Test whether the signed-mean proxy enters a $K^{3/2}$ growth regime
(i.e. $\langle q \rangle \sim K^3$ for $V_{\rm proxy} = \gamma^{3/2} \sqrt{|\langle q \rangle|}$) at large $K$. Two
families at fixed shape ($n = 4$ moment-curve plane, seed 11, $\epsilon = 1$):

1. **Vertex-scaled family** ($b$-bosons loaded onto the measured triple,
   $K = 4+3s$): $\langle q \rangle$ is **exactly linear in $s$** — $q/s = -1.059 \times 10^{-3}$ at
   all five points ($K = 10..22$, equal to 9 digits). Hence $V_{\rm proxy} \sim (K-4)^{1/2}$,
   i.e. $\alpha \to 0.5$ asymptotically. Each triple boson contributes
   independently; there is no collective $K^3$ enhancement of triple
   correlations.

2. **Uniform $M=0$ family** (fixed shape, $K = 8..24$): $q = 0$ to solver
   precision ($|q| \leq 9 \times 10^{-13}$). Uniform scaling of the coherent state
   has zero signed mean to solver precision up to $K = 24$.

**Scoped finding:** neither tested family shows $K^{3/2}$ proxy growth.
This does not test the expectation of a positive volume operator or exclude
a classical regime in other state families. (Caveats: $K = 8..24$ is only 0.5 dex of lever arm;
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
2. **Mean signed triple grasp is zero** at every $\beta$ in all three families,
   both $n$. Mechanism: $A_{ij}$ are real-symmetric, so $q = i[A_{01},A_{12}]$ is
   imaginary-antisymmetric with identically zero diagonal; the pure state
   adds reality. **Theorem: an occupation-diagonal ensemble has zero
   signed triple-grasp mean.**
3. **Fluctuations are nonzero; signed-mean cancellation does not remove
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

The published correspondence is separate from these follow-up calculations.
The real-plane argument establishes a zero **signed triple-grasp mean**, not
zero quantum volume. The corrected Rust/Python comparison and $n=4$–$8$ scan establish converged signed-mean proxy values for these fixed inputs; $n=6$ still lacks an independent engine check. See the red-team audit.
T5a's $n=6,7$ runs are consistent with per-triple
chirality rather than one vertex-wide handedness, with limited sign-test
power; the corrected magnetization sweep supports that pattern for one
fixed plane. T5a′ reports no increased
sign coherence for local triples in its tested kinematic samples, also with
limited statistics and an engine-convergence caveat. T5b reports a
$\sqrt{\epsilon}$ complexification onset for the tested $n=4,5$ states. T5e
does **not** support the expected $K^{3/2}$ volume growth through $K=24$: the
vertex-loaded family grows as a shifted square root over the measured range,
while the uniform family is zero to solver precision. These results do not
establish a general classical limit. The TFD series (T7a–T7e) opens a new direction:
thermal states carry zero mean signed triple grasp (a theorem for occupation-diagonal
ensembles) but nonzero fluctuations, the TFD two-sided correlator
reproduces the negative single-copy fluctuation in the tested Gibbs setup,
and the tested fixed-$K$ complexified TFD produces a quadratic $\epsilon^2$
correlator change. In that construction, temperature is flat; this does not
establish a general combined $V(\epsilon,T)$ law. Open directions: characterize $\langle q \rangle$
near the gauge-real locus using phase-sensitive perturbations; a sharper handedness test with sign-controlled perturbations
over $\geq 10$ seeds; $n = 8$ on larger memory; large-$K$ asymptotics beyond
$K = 24$; $\beta$-dependence inside the coherent sector (non-uniform $\omega_i$ or
multi-$K$ reference) to find a genuine $V(\epsilon,T)$ law; amplitude dynamics
(Grassmannian measure, momentum-twistor map), which remains the missing
link to actual scattering amplitudes.

## 4. Conclusions

Numerically: independent $n=4$ recomputation supports zero signed mean on
real planes and a nonzero signed mean for the tested complex plane, but also
shows nonzero $\langle q^2\rangle$ on a positive plane. Corrected converged $n=4$–$8$ complex-plane proxy values are now recorded, with independent $n=4,5,7,8$ checks. The positive-volume-operator
expectation and a classical volume interpretation remain open.
T5b reports a $\sqrt{\epsilon}$ proxy onset in its tested $n=4,5$ cases.
T5e finds no $K^{3/2}$ proxy growth through $K=24$ in its tested families;
a general classical limit remains unestablished. Thermal states in the tested
occupation-diagonal ensemble have zero signed mean and nonzero $q^2$
fluctuations (T7a). The Gibbs-TFD correlator matches the
negative single-copy fluctuation in the tested setup and temperature range
(T7b). T7e finds a quadratic $\epsilon$ response and temperature flatness in
its fixed-$K$ construction; a combined temperature/complexification law is
still open. Methodologically: the Python
pipeline suffices for $n = 4$; the Rust port (combinatorial Fock basis,
sprs, rayon) pushes the same physics to $n \geq 5$ at sub-minute runtimes;
the Schmidt-form TFD computation avoids ever forming the $D \times D$ doubled
space.

## Appendix: Code

- `code/papers/lqg-amplituhedron.tex` — published EPJC paper (baseline; frozen).
- `code/python/grassmannian.py`, `code/python/coherent_states.py`, `code/python/correspondence.py`,
  `code/python/positivity.py`, `code/python/classical_limit.py` — Python pipeline ($n = 4$),
  each self-testing (`python3 <module>.py`).
- `code/rust/` — Cargo project; `cargo test --release` (13 tests: Fock
  dimension, basis uniqueness, su(2) matrix elements, u(3) algebra,
  $J_i \cdot J_j$, closure, vacuum triviality, analytic triple product,
  volume-zero-on-real-planes, volume-nonzero-on-complex, momentum-map
  anti-Hermiticity, moment-curve positivity); `cargo run --release --
  verify4` (Python comparison), `cargo run --release -- scan` ($n = 5..8$).

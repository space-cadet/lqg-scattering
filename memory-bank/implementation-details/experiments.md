# Experiments: Volume–Positivity Program

**Status:** 🔄 IN PROGRESS — T5a/base, T5a′, T5b, and T5e have recorded results; several follow-ups remain open.
**Last Updated:** 2026-10-01
**Parent task:** T5 (Experiments)
**Depends on:** T3c (Rust triple-grasp implementation); T3d/T3e converged reruns are recorded; the n=6 point awaits an independent state check.

**Current state:** T5a's n=6,7 base analysis is recorded. Its n=5
magnetization sweep was rerun with a convergence assertion; four sectors
matched independent SciPy exponentiation. The one-plane sign pattern is
scoped evidence, not a general handedness law. T5a′ reports no stronger chirality on tested
kinematic-polyhedron-local triples, with limited n=5 samples and a shared
reference-engine convergence caveat. T5b and T5e have recorded results for
their tested ranges. T5c (state-based classical-volume comparison), T5d
(cocycle/distance scaling), T5f (scattering-region mapping), and T5g
(higher-n profiling) remain open. See `tasks.md` and the experiment notes for
the limits of each result.

## Motivation

The red-team audit narrows the central claim: real-plane states have zero
expectation of the **signed triple grasp**. This includes positive planes and
real planes outside the positive cell. The computed square-root-of-mean
quantity is a proxy, not the expectation of a positive volume operator.

Concretely, for the De Pietri / Rovelli–Smolin commutator on a triple of edges <tg-math>(i,j,k)</tg-math>,

<tg-math-block>
q_{ijk} = i\,[A_{ij}, A_{jk}], \qquad A_{ij}\equiv J_i\cdot J_j, \qquad V_{\mathrm{proxy}}=(\gamma\hbar)^{3/2}\sqrt{|\langle q\rangle|}
</tg-math-block>

Real planes give real Fock amplitudes and <tg-math>\langle q\rangle=0</tg-math>
for any triple. Some imaginary perturbations give a smoothly increasing
signed mean. The corrected <tg-math>n=4</tg-math> complex-plane magnitude
was shifted by Taylor truncation; the positive-cell state has nonzero
<tg-math>\langle q^2\rangle</tg-math>. See `red-team-audit.md`.

Every experiment below probes this boundary. They are independent and can run in any order; the priority reflects physics-per-unit-effort, not dependency.

---

## Experiment index

| ID | Short name | One-line question | Primary code |
|----|-----------|-------------------|--------------|
| T5a | Triple-volume correlations (<tg-math>n\ge5</tg-math>) | One vertex handedness, or independent per-triple chirality? | Rust `volume.rs` (extend `scan`) |
| T5b | Signed-mean proxy response <tg-math>V_{\rm proxy}(\varepsilon)</tg-math> | What exponent appears for a specified complex perturbation? | `t5b_perturbation.py` |
| T5c | Classical volume match | Does <tg-math>\sqrt{\langle q\rangle}</tg-math> equal the reconstructed polyhedron's classical volume? | `spin_vectors` + closure/twist map |
| T5d | Phase response / gauge-real locus | Which phase changes produce nonzero <tg-math>\langle q\rangle</tg-math>? | Rust `grassmannian.rs` (phase scan) |
| T5e | Large-K semiclassics | Does <tg-math>V\sim K^{3/2}</tg-math> hold at <tg-math>K=20\text{–}50</tg-math>? | Rust (recorded range currently reaches K=24) |
| T5f | Amplituhedron kinematics | Which scattering regions does <tg-math>\mathrm{Gr}_+</tg-math> cover? | `correspondence.py` + twistor map |
| T5g | Performance frontier | Where does sparse matvec stop being the bottleneck? | Rust profiling |

---

## T5a — Triple-volume correlations at <tg-math>n\ge 5</tg-math>  *(highest priority)*

**Physics question.** At an <tg-math>n</tg-math>-valent vertex the volume operator can be built on any triple of distinct edges: <tg-math>q_{123}, q_{145}, q_{246}, \dots</tg-math> (no adjacency requirement — the commutator is defined for any three distinct edges). If <tg-math>q_{123}</tg-math> is nonzero/chiral, is <tg-math>q_{145}</tg-math> correlated in sign or magnitude?

- **Correlated** → the whole vertex carries a single chiral character ("one handedness").
- **Uncorrelated / independent** → chirality is a per-triple property, a genuine <tg-math>n\ge5</tg-math> structure **invisible at <tg-math>n=4</tg-math>** (where there is only one independent triple).

**Why novel.** <tg-math>n=4</tg-math> has a single triple up to symmetry, so this correlation structure cannot be seen there. It is the cleanest genuinely-new physics on the list.

**Implementation.** Extend the Rust `scan` mode to compute <tg-math>\langle q_{ijk}\rangle</tg-math> on **all <tg-math>\binom{n}{3}</tg-math> triples** for a fixed state (e.g. <tg-math>n=6,7,8</tg-math>), then compute the sign / magnitude correlation matrix across triples. The infrastructure (`volume_operator` on an arbitrary `triple`) already exists; this is a loop + correlation analysis, well under the existing per-<tg-math>n</tg-math> runtime budget.

**Deliverable.** Correlation matrix + verdict (single-handedness vs per-triple chirality) → manuscript §3.

---

## T5b — Perturbation response <tg-math>V(\varepsilon)</tg-math>

**Physics question.** Turn on a specified imaginary plane perturbation
<tg-math>\varepsilon</tg-math> and measure the signed-mean proxy from
<tg-math>\varepsilon\sim10^{-6}</tg-math> up to <tg-math>1</tg-math>. Fit its
exponent for that family.

- **<tg-math>\alpha<1</tg-math>** → chirality turns on *arbitrarily softly*: an arbitrarily small-handed geometry carries appreciable volume.
- **<tg-math>\alpha\ge1</tg-math>** or a threshold → chirality is more "quantized."

This directly answers: *can chirality be switched on smoothly, or is there a barrier?*

**Implementation.** The corrected `t5b_perturbation.py` completed the
13-point $n=4,5$ sweep with a convergence assertion. Independent SciPy
exponentiation checked four $n=4$ and three $n=5$ points. Extend this with
multiple plane/reference controls before claiming a general onset law.

---

## T5c — Classical volume match

**Physics question.** The manuscript flags a missing link: does <tg-math>\sqrt{\langle q\rangle}</tg-math>, computed quantum-mechanically from *correlations*, equal the *classical* volume of the polyhedron reconstructed from the same state?

**Key distinction (do not conflate).** <tg-math>\langle q\rangle</tg-math> is the expectation of the operator <tg-math>\epsilon^{abc}J_i^aJ_j^bJ_k^c</tg-math>, **not** the classical triple product <tg-math>\frac{1}{6}|n_i\cdot(n_j\times n_k)|</tg-math> of one-point functions <tg-math>\langle J_i\rangle</tg-math>. A coherent superposition can have nonzero <tg-math>\langle q\rangle</tg-math> even when all <tg-math>\langle J_i\rangle</tg-math> are collinear (e.g. frozen along <tg-math>z</tg-math>), because the operator probes <tg-math>J^xJ^y</tg-math> correlations. This experiment tests whether that quantum value nonetheless *matches* the classical volume of the reconstructed dual polyhedron.

**Implementation.**
1. From a coherent state, read off <tg-math>\langle J_i\rangle</tg-math> and the covariance matrices (`spin_vectors` gives the normals; note <tg-math>\langle J_i^x\rangle=\langle J_i^y\rangle=0</tg-math> identically by <tg-math>N_a/N_b</tg-math> conservation, so the one-point data alone is degenerate — the reconstruction must use the covariance / closure data).
2. Reconstruct the dual polyhedron via the LQG closure condition + twist-angle map (edge vectors from face normals).
3. Compute its classical volume <tg-math>V_{\text{cl}}</tg-math>.
4. Compare <tg-math>(\gamma\hbar)^{3/2}\sqrt{|\langle q\rangle|}</tg-math> against <tg-math>V_{\text{cl}}</tg-math> as <tg-math>K</tg-math> grows.

**Deliverable.** First distinguish the signed-mean proxy from a positive
volume-operator expectation. Then compare each specified observable against
the reconstructed classical volume for converged state families; a numerical
match in a finite range does not prove a general classical limit.

---

## T5d — Cocycle barrier / distance-to-cell scaling

**Physics question.** Which phase perturbations turn on the signed mean
as a plane leaves the gauge-real locus?

- **Cocycle scan.** Parameterize the phase-cocycle violation <tg-math>\varphi=\arg(M_{12}M_{34}/M_{13}M_{24})</tg-math> and measure <tg-math>\langle q\rangle(\varphi)</tg-math> at fixed shape/<tg-math>K</tg-math>, <tg-math>n=4..8</tg-math>. Test <tg-math>\langle q\rangle\sim|\varphi|</tg-math> (linear emergence) vs a barrier-like singularity as <tg-math>\varphi\to0</tg-math>.
- **Gauge-real control.** Include real planes with mixed-sign minors and
  complex planes whose signed mean cancels. A defect based on negative real
  minors cannot be treated as distance to the zero locus.

The signed mean must be characterized on specified plane and reference
families; it is not a positive measure on the complement of
<tg-math>\mathrm{Gr}_+</tg-math>.

**Implementation.** Rust. The `positive_plane_curve` generator + minor-phase perturbation machinery already exists. New code: a cocycle-phase sweep and a `d`-defect computation + log-log fit.

---

## T5e — Large-K semiclassics

**Physics question.** Does the semiclassical prediction <tg-math>V\sim K^{3/2}</tg-math> actually hold at accessible <tg-math>K</tg-math>? The <tg-math>n=4</tg-math> Python scan was non-monotonic at <tg-math>K\le8</tg-math> (too small to see the asymptote). The Rust port can push <tg-math>K=20\text{–}50</tg-math> at <tg-math>n=4\text{–}6</tg-math> cheaply.

**Secondary check — peakness vs. shape.** Coherent states should sharpen (<tg-math>\Delta A/\langle A\rangle\to0</tg-math>) as <tg-math>K</tg-math> grows. Do *all* plane shapes sharpen uniformly, or do degenerate / near-collinear planes sustain quantum spread? Stress-tests the coherent-state construction.

**Implementation.** Extend the Rust `scan` K-range. Mostly a sanity check on the side; not the headline.

---

## T5f — Amplituhedron kinematics

**Physics question.** Connect back to actual scattering. Generate planes in <tg-math>\mathrm{Gr}_+</tg-math>, extract the Mandelstam invariants <tg-math>s_{ij}=(p_i+p_j)^2</tg-math>, and check which physical scattering regions (s-, t-, u-channels for <tg-math>n=4</tg-math>) are covered. Map <tg-math>\mathrm{Gr}_{\ge0}</tg-math> cell boundaries to kinematic thresholds. Optionally: compute momentum-twistor images of positive planes and verify they land in the N<tg-math>^k</tg-math>MHV amplituhedron region for small <tg-math>k</tg-math>.

**Why lowest priority.** It is the most "amplituhedron-flavoured" and needs the most *new* machinery (momentum-twistor code) for the least immediate physics payoff. Defer until T5a–T5d land.

---

## T5g — Performance frontier

**Engineering, not physics.** Push the Rust port to <tg-math>n=10\text{–}12</tg-math> with triple-local references (Fock dim stays ~<tg-math>10^5</tg-math>) to find where sparse matvec, not dimension, becomes the bottleneck. Profile whether the Taylor exponential or `j_dot` construction dominates. Enables T5a–T5e at higher <tg-math>n</tg-math>.

---

## Recommended order

1. **Define the observable and finish independent baseline checks.** Separate $\langle q\rangle$, $\sqrt{|\langle q\rangle|}$, $\langle q^2\rangle$, and a specified positive volume operator. T3d/T3e converged reruns and independent $n=4,5,7,8$ exponentials are recorded; independently check $n=6$.
2. **Extend T5a/T5a′ and T5b.** The corrected magnetization sweep is converged
   for one plane and cross-checked in four sectors. Add independent plane
   samples, strengthen the local-triple comparison, and add multiple
   plane/reference controls before generalizing either result.
3. **Run T5d with controls.** Include positive real, mixed-sign real, and complex planes. Define a gauge-invariant phase variable before fitting any onset.
4. **Complete T5c and the full quantum T6 reconstruction.** Compare explicitly named quantum observables with a reconstructed classical polyhedron and test state-family dependence.
5. **Scope the next T7 experiment.** The existing T7e result is beta-flat for fixed-$K$ support. Proceed only with a physically justified multi-$K$ coherent reference or non-uniform-frequency Hamiltonian, and predefine cutoff and temperature convergence checks.
6. **Extend T5e if it changes the claim.** Current converged records reach $K=24$; larger-$K$ work should test the two observed families separately.
7. **Do T5f after the geometric observables are stable.** Map the positive-cell data to scattering invariants and amplituhedron regions.
8. **Use T5g as enabling work.** Profile $n=10$–$12$ only where it unlocks one of the preceding physics questions.
9. **Update and review the manuscript continuously.** Promote claims only with recorded validation evidence, limits, and provenance; circulate after the claim ledger and red-team review are complete.

T5b's original point values used a short Taylor cap. A corrected 13-point
rerun with a convergence assertion now supports the near-half proxy exponent
for the tested $n=4,5$ family; four $n=4$ and three $n=5$ points have an
independent SciPy cross-check. Generality across planes remains open.

---

## Notes

- **Numerical claims require independent evidence before promotion.** The
  referenced `skills/red-team/SKILL.md` and workspace `MEMORY.md` were not
  present in the searched checkout/skill locations; the available scoped
  protocol and findings are in `red-team-audit.md` and
  `verification-protocol.md`.
- **Code must be checkpointable/resumable** if any scan exceeds ~10 min (standing workspace rule).
- **Reference-state caveat** (applies to every experiment): an all-<tg-math>a</tg-math> reference (<tg-math>N_b=0</tg-math>) gives <tg-math>\langle q\rangle=0</tg-math> regardless of the plane. Use `vertex_reference` (or the Rust equivalent), which places <tg-math>b</tg-math>-bosons on the measured triple, for the recorded signed-mean comparisons.

---

# Experiment Specifications — Follow-up Numerical Program

## T5a: triple-volume correlations at n >= 5

**Question.** Does an n-valent vertex built from ONE U(N) coherent state on
a complex (off-cell) plane carry a single handedness, or independent
per-triple chirality?

**Protocol.**

1. Build ONE Perelomov state per (n, seed) on a complex plane
   (moment-curve positive plane + fixed imaginary perturbation that
   violates the minor-phase cocycle).
2. Reference occupations: uniform (1,1) on every edge — no triple
   privileged. K = 2n.
3. For every triple (i, j, k), 1 <= i < j < k <= n:
   q_ijk = i <[A_ij, A_jk]>,  A_ij = J_i . J_j  (Schwinger),
   computed as q_ijk = -2 Im <A_ij psi | A_jk psi>.
4. Per state: sign-agreement fraction = max(#pos, #neg) / (#nonzero),
   nonzero = |q| > 1e-9.
5. Ensemble (multiple seeds): Pearson correlation of |q| magnitudes
   across states; Pearson of signed q across states.

**Prediction (single handedness)** would show: sign-agreement -> 1,
Pearson |q| across seeds -> 1 (magnitudes geometry-determined).
**Prediction (per-triple chirality)** would show: sign-agreement ~ 0.5,
Pearson |q| across seeds ~ 0.

**Targets.** n = 6, 7, 8. n = 8 with uniform (1,1) needs Fock dim
C(32,16) = 601,080,390 (~10 GB per dense vector) — beyond an 8 GB node;
n = 8 to be run on larger memory or with an out-of-core engine.

**Engines.** n <= 6: stored sprs operators (`rust/src/ops.rs`,
pivot scheme in `rust/src/experiment.rs`). n >= 7: on-the-fly engine
(`rust/src/onthefly.rs`) — combinatorial rank indexing, atomic-scatter
parallel matvec, no stored operators.

**Driver.** `cargo run --release --bin t5a -- <n> [seed ...]`

**Status.** RUN — see "Results" below.

## Results (T5a)

### n = 6 (stored engine, uniform reference K = 12, dim 2,704,156)

| seed | runtime | pos + neg (of 20) | sign-agreement | max |q| | mean |q| |
|---|---|---|---|---|---|
| 1000 | 96 s | 11 + 9 | 0.55 | 1.77e-6 | 4.46e-7 |
| 2000 | 268 s | 6 + 14 | 0.70 | 3.15e-7 | 9.81e-8 |
| 3000 | 129 s | 10 + 10 | 0.50 | 2.26e-6 | 4.14e-7 |

### n = 7 (on-the-fly engine, uniform reference K = 14, dim 40,116,600)

| seed | runtime | pos + neg (of 35) | sign-agreement | max |q| | mean |q| |
|---|---|---|---|---|---|
| 1000 | 155 s | 17 + 18 | 0.51 | 4.71e-7 | 1.79e-7 |
| 2000 | 179 s | (of 35) | 0.56 | | |

### Ensemble Pearson correlations (across seeds)

n = 6 (20 triples each, 3 seeds):
| pair | Pearson |q| | Pearson signed q |
|---|---|---|
| 1000 vs 2000 | −0.23 | +0.21 |
| 1000 vs 3000 | +0.27 | −0.42 |
| 2000 vs 3000 | +0.04 | −0.08 |

n = 7 (35 triples, 2 seeds):
| pair | Pearson |q| | Pearson signed q |
|---|---|---|
| 1000 vs 2000 | +0.10 | +0.44 |

### Interpretation (T5a verdict)

**Per-triple chirality, no global handedness.** Across all states and
both n:

1. Sign-agreement fractions (0.50–0.70 at n = 6; 0.51–0.56 at n = 7)
   are consistent with independent random signs (binomial fluctuation at
   these sample sizes). No state exhibits the near-unanimous sign pattern
   a single-handedness vertex would produce.
2. Pearson correlations of |q| magnitudes across independent states are
   ≈ 0 (−0.23 … +0.27 at n = 6, +0.10 at n = 7): which triple is
   "loudest" is fluctuation-driven, not geometry-determined.
3. Signed-q correlations are likewise small (|r| <= 0.44), confirming
   chirality signs do not cohere across states.

Caveats: (a) each state is one sample — the sign test's power at 20–35
triples is modest; (b) the single moderately positive signed-q Pearson at
n = 7 (+0.44) is one pair and not significant; (c) n = 8 remains
unresolved (resource bound, ~10 GB/vector at the spec's uniform (1,1)
reference). To sharpen the sign test, a future run should flip the
perturbation sign per seed (deterministic sign control) or average
signed-q coherence over >= 10 seeds.

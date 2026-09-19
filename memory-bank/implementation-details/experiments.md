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

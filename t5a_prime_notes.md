# T5a′ kinematic-polyhedron local chirality — notes (run 3a0c6323)

Child of the T5a M-sweep. Question: does chirality cohere on
Minkowski-ADJACENT triples even though all-triples sign-agreement is ~0.5?

## Verdict

**No. Restricting to kinematic-polyhedron-adjacent triples does not reveal
hidden handedness.** Mean local sign-agreement (0.52–0.71, n=5) tracks mean
all-triples agreement (0.53–0.68) across all 10 incoming-pair channels,
exceeding it in 4/10, trailing in 5/10, tied in 1/10. Channel-averaged:
all ≈ 0.589, local ≈ 0.594 — dead even. n=4: exact 0.500 in all 3 channels
(s/t/u), i.e. no channel dependence either.

## Design (reversed construction)

Plane column-momenta generically do NOT close under any sign assignment
(closure is 3 continuous equations; sign flips are discrete), so the
protocol generates conserved kinematics FIRST (2->2 / 2->3 CM, exact
closure), builds the spinor plane from them, the kinematic polyhedron via
all-incoming Minkowski (A_i=E_i, n_i=eps_i p_i/E_i), and measures the
Perelomov state on C0 + FIXED dC (same row-1 pattern as the T5a sweep).
Adjacency frozen from geometry before looking at q signs; all channels
reported. M fixed to the 0-spread sector to isolate adjacency.

Two corrections found during implementation (both in this branch's code):
1. Scattering-spinor planes are generically OFF-cell (minor-phase cocycle
   is gauge- and GL(2)-invariant and nontrivial) — column-realification is
   impossible; the eps=0 calibration concept was dropped in favor of a
   fixed-dC floor + explicit-commutator red-team check (passed on both n).
2. n=4 CM 2->2 normals are planar (rank 2): no 3D polyhedron exists, and
   tetrahedron combinatorics would make local == all triples anyway. The
   n=4 arm therefore tests channel-(in)dependence of the all-triples
   verdict only. Genuine subsetting needs n >= 5.

## Engine validation (dense expm ground truth)

- n=4 Rust-test replication: mine -8.276875e-4, expm -8.276872e-4
  (10-digit match). The Rust/Python reference -8.496572e-4 is off 2.6%:
  BOTH references truncate Taylor at 15 terms (2K+4, K=6) and agree with
  each other only through shared truncation. Convergence needs ~25 terms.
- n=3 cross-check: expm gives q ~ 4e-17 (exact zero). Reason: EVERY n=3
  plane is gauge-real (3 minor phases, 3 column-phase unknowns — always
  solvable), so q = 0 identically. The Python pipeline's non-zero value
  there is truncation noise. n=3 can never show chirality.
- Consequence: the frozen parent M-sweep (cap 2K+8 = 24 terms at K=8,
  needs ~40) ran on TRUNCATED states. Per the repair rule (bug, not
  result) that node is provisional: repaired + rerun separately.

## Table (run 3a0c6323, 91.5s local)

n=4 (20 planes/channel, local == all by combinatorics):
| channel | agree_all |
| s | 0.500 | t | 0.500 | u | 0.500 |

n=5 (8 planes/channel, 6 local of 10 triples, 1 distinct local set each):
| channel | agree_all | agree_local |
| in01 0.575 0.625 | in02 0.675 0.604 | in03 0.625 0.583 |
| in04 0.638 0.708 | in12 0.587 0.521 | in13 0.562 0.646 |
| in14 0.613 0.583 | in23 0.525 0.521 | in24 0.562 0.562 |
| in34 0.575 0.562 |

## Caveats

8 planes/channel at n=5 (per-plane 6-triple sign test is weak);
per-triple q values not persisted (means only) — pooled sign test is a
follow-up. Cosmetic RuntimeWarnings (nanmean over empty n=4 local) in log.
n=6+ needs the Rust engine. Parent M-sweep rerun pending (repair branch).

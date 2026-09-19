# T5e large-K semiclassics — notes (run 26062159, commit b4aa1c0)

Fixed shape (n=4 moment-curve plane, seed 11, imag dC eps=1 — T5b
convention), triple (0,1,2), gamma=0.2375. Rust on-the-fly engine,
q = -2 Im<A01 psi|A12 psi>, V = gamma^1.5 sqrt(|q|).

## Verdict

**The K^1.5 law does NOT hold.** No family shows alpha ~ 1.5:

1. **Vertex-scaled family (b-bosons loaded onto the measured triple,
   K = 4+3s): <q> is EXACTLY linear in s** — q/s = -1.059408e-3 at
   all five points (K=10..22, equal to 9 digits) plus the K=7
   regression point. Hence V ~ (K-4)^0.5, i.e. alpha -> 0.5
   asymptotically (log-log fit over K=10..22 gives alpha=0.696,
   R2=0.998, but that number is a finite-range artifact of fitting a
   shifted square root; local slopes decline +0.77 -> +0.62 toward 0.5).
   Each triple boson contributes independently; no collective K^3
   enhancement of triple correlations.
2. **Uniform M=0 family (fixed shape, K=8..24, seeds 11 and 42):
   q = 0 to solver precision** (|q| <= 9e-13, signs fluctuate, both
   engines agree to ~1e-17 at K=8). The t5e_results.json uniform fits
   (alpha ~ +3.9) fit SOLVER NOISE, not physics — do not quote them.
   Uniform scaling of the coherent state develops NO volume at all.

Classical V ~ r^3 would need <q> ~ K^3. Observed: <q> ~ K^1 (triple
loading) or <q> ~ 0 (uniform scaling). Per the probe guide this is the
alpha < 1.5 branch: the coherent-state volume does not enter a
classical-growth regime up to K=24.

## Method / engine choices

- Single engine: Rust on-the-fly (no stored operators), validated vs
  the stored engine at K=8,12 (abs-diff ~1e-17..1e-15, both consistent
  with zero there). Real-plane (eps=0) controls give EXACTLY 0 at every
  K tested. Closure sum<n_i> = K exact. Sanity gate: K=7 vertex V =
  3.767e-3, in the t5b 1e-3..1e-2 range. Seed-42 uniform points
  confirm the zero.
- Fit: log-log slope + R2 + local slopes (t5e_fit.py, inside the run).

## Caveats (read before quoting)

1. **Truncation saga.** The first recorded run (7a8364f6) used Taylor
   cap 2K+4 and produced smooth-looking but WRONG large-K values
   (uniform alpha ~ -2, vertex alpha ~ +3.2). The audit child proved
   truncation (K=24 needed 74 iters, not 52; values shifted x6500 /
   x35). The recorded run uses cap 8K+50 with a fail-loudly convergence
   assert; per-point Taylor counts (38..79) are in t5e_results.json.
   Even K=7 needed 35+ iterations — treat ANY Perelomov number without
   a convergence flag as suspect (see 4).
2. **Uniform zero is an upper bound, not a theorem.** |q| <= ~1e-12 at
   K <= 24 given tol 1e-13 states. Whether it is exactly zero (a new
   selection rule for balanced references?) or merely tiny needs higher
   precision or an analytic argument — open follow-up.
3. **Narrow lever arm.** K=8..24 is 0.5 dex (Fock dim 1e4..1e7 at n=4);
   K=28+ needs ~30M-dim vectors, beyond this 8 GB machine.
4. **WARNING to sibling nodes.** The Rust `perelomov_otf`/`perelomov`
   cap 2K+4 truncated at ALL K (even K=7). T5a's Rust-driver magnitudes
   (uniform refs, K=12..14) predate the 8K+50 fix and are likely
   truncation-shifted; sign agreements are probably robust (T5a Python
   showed zero sign flips under truncation) but magnitudes are not.
   The n=4 legacy test value has the same caveat (already flagged by
   the T5a session for Python). Rust lib + t5e driver on branch
   t5e-large-k (commits 6ef2a65..) carry the fix; sibling branches do
   not.
5. Single plane shape family (moment curve + fixed dC), eps=1 fixed,
   n=4, triple (0,1,2) only. Vertex family changes shape with K (edge
   3 frozen at spin-1/2) — it is triple-loading, not a fixed-shape
   semiclassical limit.

## Provenance

- orx node 113dad04 (root), run 26062159 (done, 75 s, local).
  Repair history: 27c65fa6 (fit crashed on non-JSON ref format),
  7a8364f6 (valid fit of truncated states), audit child 047f5824
  (FAIL verdict that caught the truncation).
- Engine source: this branch (rust/), mirrored from lqg-scattering
  branch t5e-large-k; t5e_results.json + this file committed there too.

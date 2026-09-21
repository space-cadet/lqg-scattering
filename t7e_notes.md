# T7e notes: complexified momenta in the TFD — eps-scaling

## Construction

`C(eps) = C0 + eps*dC`, T5b `dC` convention (`dC[1,i] = 1j*0.35*(i+0.5)`),
eps = 1e-6..1.0, n = 4, 5, converged Taylor (38/40 iters, 8K+50 cap + assert).
Two-sided state keeps Perelomov phases:
`|Psi(beta,eps)> = sum_n $d_{n}$ |n>_L|n>_R`, `$d_{n}$ ~ $c_{n}$(eps) e^{-beta $E_{n}$/2}`,
`<q_L q_R> = sum $d_{n}$^* $d_{m}$ ($q_{nm}$)^2`. Full tables in t7e_results.json
(run 45efb872).

## R-conjugation verdict: explicit, then no-op for this observable

"R from conjugate plane C*" and "conjugated R amplitudes of the C state"
coincide to ~1e-16 (momentum map and Taylor both commute with conjugation;
asserted at every eps). The correlator itself is additionally invariant under
`d -> d^*`, verified numerically — theorem: `($q_{nm}$)^2` is real symmetric (q
imaginary Hermitian), so conjugation drops out of `<q_L q_R>`. Conjugation
would matter only for phase-sensitive observables. So: complexification does
not complicate purification for q-like observables; the eps-dependence below
comes from populations + coherences, not from conjugation bookkeeping.

## Eps-scaling: correlator does NOT inherit the sqrt law (hypothesis confirmed)

- T5b replication with converged Taylor: V-fit alpha = 0.495/0.499 vs T5b
  0.497/0.499; point ratios 1.008/0.999 — the old truncated Taylor was fine
  at small K, and the sqrt law is robust.
- `|q| ~ eps^1.0` (0.990/0.997): the mean chirality turns on linearly, and
  `V = sqrt(|q|)` gives the 0.5 — consistent picture.
- **TFD correlator change `|corr(eps) - corr(0)| ~ eps^2.0`** (1.991/1.994,
  local slopes 2.00/2.00/1.96, R2 = 1.000): quadratic onset, much stiffer
  than the single-copy sqrt law. Same exponent for pure `<q^2>` change
  (1.99) — the correlator tracks q-squared-like quantities, as expected from
  its `($q_{nm}$)^2` structure.
- On-cell values: corr = +0.0306 (n=4), -0.0107 (n=5) — sign is
  plane/seed-dependent interference of Perelomov amplitude signs (differs from
  the dephased PW values -0.394/-0.237 precisely because coherences survive);
  the eps^2 *scaling* is the robust claim, identical for both n.

## No combined V(eps, T) law: complexification and thermalization factorize

corr(beta, eps) is beta-flat to ~1e-17 at every eps (fixed-K support kills the
Boltzmann factor, same mechanism as T7a/T7b), while the Gibbs-TFD is eps-flat.
Each deformation acts on an orthogonal aspect — eps on coherences/populations
within E=K, beta on weights across E — so they commute trivially rather than
reshaping each other. There is no `V(eps, T)` combined law in this
construction; a genuine one would need beta-dependence inside the coherent
sector (e.g. non-uniform omega_i or multi-K reference).

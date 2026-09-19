# T7b notes: TFD construction, verification, two-sided correlator

## Construction

`|TFD(beta)> = Z^{-1/2} sum_n e^{-beta E_n/2} |n>_L |n>_R^*` over the full
capped occupation basis (Gibbs purification, per the T7a guidance — not the
Perelomov-weighted variant, which is beta-flat). The Fock basis is real so the
R-conjugation acts trivially (it would matter only off-cell, i.e. T7e).
Everything is computed in Schmidt form: the DxD doubled space (41M for n=4,
1.9B for n=5) is never formed. `<q_L q_R> = sum_{nm} sqrt(p_n p_m) (q_nm)^2`
is vectorized over the sparse nnz of q (4476 for n=4, 27208 for n=5).

## Verification (run 0abce6c3; full tables in t7b_results.json)

- **(i) rho_L == rho_beta: PASS.** Schmidt weights reproduce the T7a Gibbs
  distribution; cross-check vs t7a_results.json: max|dS| = 3.6e-15/1.4e-14,
  max|dq2| = 0, max|dAreas| = 0.
- **(ii) beta->inf limit: CORRECTED, not as spec'd.** The Gibbs-TFD flows to
  the Fock vacuum product (beta=10: p_vac = 0.9996/0.9995, S -> 0.004/0.005),
  NOT to the pure Perelomov state on L. Reason: the Gibbs ensemble forgets the
  plane (uniform omega, no Z-dependence), so no low-T limit can recover
  Perelomov coherence. The Perelomov-weighted TFD's L-marginal is
  beta-independent dephased-Perelomov — never pure either. Spec (ii) as written
  holds for neither variant; recorded here as a spec correction.
- **(iii) S(beta) matches thermal entropy: PASS** (same numbers as (i);
  S = 8.77/10.69 at beta=0 = log D, -> ~0 at beta=10).

## Small theorem (stronger than the planned beta=0 check)

`<q_L q_R>(beta) = -Tr(rho_beta q^2)` at **every** beta (corr+q2 ~ 1e-17
across the whole sweep), not just beta=0. Proof: q preserves total boson
number (each A_ij does), so `q_nm != 0 => E_n = E_m => sqrt(p_n p_m) = p_n`,
and q imaginary gives `(q_nm)^2 = -|q_nm|^2`. The two-sided signal carries
exactly the single-copy fluctuation content, with opposite sign
(L–R anticorrelation). The identity needs uniform weights within E-sectors,
so it FAILS for the Perelomov-weighted TFD (PW corr = -0.394/-0.237,
beta-flat, vs PW q2 = 0.785/0.679) — coherences `|c_n| != |c_m|` break it.

## Scaling fit (T7d protocol): no T5b-like power law

`|<q_L q_R>|` vs T: log-log local slopes drift 0.2 -> 21.7 (both n); formal
fits give alpha_all ~ 5.8 (R2 ~ 0.69), alpha_trust(beta>=1) ~ 12.0 (R2 ~ 0.93)
— the R2 is deceptive (4 points of an exponential); the drifting slopes rule
out a power law. Instead `d ln|corr|/d beta = -3.008 ≈ -3` on [5,10]:
Boltzmann-exponential onset `~e^{-3 beta}`, because q needs edges 0,1,2
occupied (leading E=3 sector). Honest verdict: thermal onset is exponential,
qualitatively distinct from T5b's `V ~ eps^0.5` sqrt law — complexification
and thermalization are different deformations with different universality
(or lack thereof). Cutoff caveat from T7a stands: beta <= 0.5 qualitative,
beta >= 1 quantitative.

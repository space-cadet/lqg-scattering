# T7e notes: complexified momenta in the TFD — $\epsilon$-scaling

## Construction

$C(\epsilon) = C_0 + \epsilon \cdot dC$, T5b $dC$ convention ($dC[1,i] = 1j \cdot 0.35 \cdot (i+0.5)$),
$\epsilon = 1\mathrm{e}{-6}..1.0$, n = 4, 5, converged Taylor (38/40 iters, $8K+50$ cap + assert).
Two-sided state keeps Perelomov phases:
$|\Psi(\beta,\epsilon)\rangle = \sum_n d_n |n\rangle_L|n\rangle_R$, $d_n \sim c_n(\epsilon) e^{-\beta E_n/2}$,
$\langle q_L q_R \rangle = \sum d_n^* d_m (q_{nm})^2$. Full tables in t7e_results.json
(run 45efb872).

## R-conjugation verdict: explicit, then no-op for this observable

"R from conjugate plane $C^*$" and "conjugated R amplitudes of the $C$ state"
coincide to $\sim 1\mathrm{e}{-16}$ (momentum map and Taylor both commute with conjugation;
asserted at every $\epsilon$). The correlator itself is additionally invariant under
$d \to d^*$, verified numerically — theorem: $(q_{nm})^2$ is real symmetric ($q$
imaginary Hermitian), so conjugation drops out of $\langle q_L q_R \rangle$. Conjugation
would matter only for phase-sensitive observables. So: complexification does
not complicate purification for $q$-like observables; the $\epsilon$-dependence below
comes from populations + coherences, not from conjugation bookkeeping.

## $\epsilon$-scaling: correlator does NOT inherit the sqrt law (hypothesis confirmed)

- T5b replication with converged Taylor: $V$-fit $\alpha = 0.495/0.499$ vs T5b
  $0.497/0.499$; point ratios $1.008/0.999$ — the old truncated Taylor was fine
  at small $K$, and the sqrt law is robust.
- $|q| \sim \epsilon^{1.0}$ (0.990/0.997): the mean chirality turns on linearly, and
  $V = \sqrt{|q|}$ gives the 0.5 — consistent picture.
- **TFD correlator change $|\mathrm{corr}(\epsilon) - \mathrm{corr}(0)| \sim \epsilon^{2.0}$** (1.991/1.994,
  local slopes 2.00/2.00/1.96, R2 = 1.000): quadratic onset, much stiffer
  than the single-copy sqrt law. Same exponent for pure $\langle q^2 \rangle$ change
  (1.99) — the correlator tracks $q$-squared-like quantities, as expected from
  its $(q_{nm})^2$ structure.
- On-cell values: corr = $+0.0306$ (n=4), $-0.0107$ (n=5) — sign is
  plane/seed-dependent interference of Perelomov amplitude signs (differs from
  the dephased PW values $-0.394/-0.237$ precisely because coherences survive);
  the $\epsilon^2$ *scaling* is the robust claim, identical for both n.

## No combined $V(\epsilon, T)$ law: complexification and thermalization factorize

corr$(\beta, \epsilon)$ is $\beta$-flat to $\sim 1\mathrm{e}{-17}$ at every $\epsilon$ (fixed-$K$ support kills the
Boltzmann factor, same mechanism as T7a/T7b), while the Gibbs-TFD is $\epsilon$-flat.
Each deformation acts on an orthogonal aspect — $\epsilon$ on coherences/populations
within $E=K$, $\beta$ on weights across $E$ — so they commute trivially rather than
reshaping each other. There is no $V(\epsilon, T)$ combined law in this
construction; a genuine one would need $\beta$-dependence inside the coherent
sector (e.g. non-uniform $\omega_i$ or multi-$K$ reference).

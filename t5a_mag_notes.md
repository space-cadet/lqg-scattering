# T5a magnetization sweep — notes (converged rerun 2026-10-01)

The saved `t5a_mag_results.json` was regenerated with a convergence
assertion. The 10 states needed 39–41 Taylor terms; the earlier 24-term
run was unconverged. Sign agreement remained 0.50–0.60 on the eight
nonpolarized sectors, with no change in the tested sign pattern. Four
representative sectors ($M=+3,0$ spread, $0$ concentrated, $-3$) were
independently exponentiated using SciPy `expm_multiply`; all saved triple
means agreed within $3.6\times10^{-16}$ absolute. This validates the
fixed-plane sweep's state construction and observed sign pattern. The
result is still one plane with ten triples per sector, so it does not
establish a universal absence of vertex-wide handedness.

Fixed plane (moment curve n=5, seed 1000 + imag perturbation on row 1),
fixed n=5, K=8. Swept reference magnetization $M=(N_a-N_b)/2$ at fixed K.

## Verdict

**No global handedness in this tested plane.** Sign-agreement stays 0.50–0.60
(5/5 or 6/4 of 10 triples) for every $M$ in $-3..+3$. The probe hypothesis
(handedness emerges only at $|M|>0$) is NOT supported — the $M=0$
per-triple-chirality result extends across the tested sectors of this plane.

## Table (rounded values from the converged rerun)

| ref | $M$ | sign-agree | $\max|q|$ | $\mathrm{mean}|q|$ | Pearson $|q|$ vs $M=0$ spread |
|---|---|---|---|---|---|
| all-a | $+4$ | — (all $q\approx 0$) | 5.4e-18 | 2.0e-18 | $-0.19$ |
| | $+3$ | 0.50 | 1.32e-02 | 4.78e-03 | $+0.01$ |
| | $+2$ | 0.60 | 2.50e-02 | 8.76e-03 | $+0.14$ |
| | $+1$ | 0.60 | 6.58e-03 | 2.82e-03 | $+0.24$ |
| spread | $0$ | 0.60 | 3.23e-02 | 7.36e-03 | $+1.00$ |
| concentrated | $0$ | 0.50 | 4.81e-02 | 2.25e-02 | $+0.76$ (signed $+0.86$) |
| | $-1$ | 0.60 | 6.58e-03 | 2.82e-03 | $+0.24$ |
| | $-2$ | 0.60 | 2.50e-02 | 8.76e-03 | $+0.14$ |
| | $-3$ | 0.50 | 1.32e-02 | 4.78e-03 | $+0.01$ |
| all-b | $-4$ | — (all $q\approx 0$) | 3.9e-18 | 1.4e-18 | $-0.26$ |

## Secondary observations

1. **Polarized endpoints freeze:** $M=\pm 4$ (all-a / all-b) give $q\approx 1\mathrm{e}{-17}$
   (numerical zero) on all triples — confirms the $N_b=0$ / $N_a=0$
   spin-freezing mechanism in this engine.
2. **$a \leftrightarrow b$ mirror symmetry:** $M=+k$ and $M=-k$ give matching $q$ to rounding;
   vectors ($J_i \cdot J_j$ is invariant under $a \leftrightarrow b$), as expected.
3. **Spatial control at $M=0$:** concentrating all $b$-bosons on one edge
   (vs spread) preserves the triple pattern (Pearson $|q|$ $+0.76$, signed
   $+0.86$) but rescales $\mathrm{mean}|q|$ $\times 3$ (7.4e-3 → 2.25e-2).
4. **Across-$M$ decoherence:** $|q|$-pattern correlation vs the $M=0$ baseline
   decays $1.0 \to 0.24 \to 0.14 \to 0.01$ with growing $|M|$ — which triple is
   loudest is $M$-sector-dependent.
5. **Magnitude is non-monotonic in $|M|$**, peaking at $M=0$ concentrated.

## Red-team check

The original explicit-commutator check used the old truncated state and
matched its $-2\mathrm{Im}$ route. The corrected state gives
$q_{123}=0.003811278991541647$ for $M=0$ spread; its saved value matches
the independent SciPy exponential's $-2\mathrm{Im}$ evaluation within
floating-point error. The commutator identity remains an operator-level
check; the convergence assertion and independent exponential now validate
the state used in the reported sweep.

## Caveats

Single fixed plane, n=5, K=8, 10 triples/state — modest sign-test power.
Multi-seed sweep and a Rust cross-check (T5a driver engine) are natural
follow-ups. Python fixed-K engine is new code (t5a_mag_sweep.py);
cross-validation against the Rust t5a binary at a shared (n, K, ref)
point is still open.

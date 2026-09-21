# T5a magnetization sweep — notes (run db7bc753)

Fixed plane (moment curve n=5, seed 1000 + imag perturbation on row 1),
fixed n=5, K=8. Swept reference magnetization $M=(N_a-N_b)/2$ at fixed K.

## Verdict

**No global handedness at any $M$.** Sign-agreement stays 0.50–0.60
(5/5 or 6/4 of 10 triples) for every $M$ in $-3..+3$. The probe hypothesis
(handedness emerges only at $|M|>0$) is NOT supported — the $M=0$
per-triple-chirality result extends across the whole sweep.

## Table (from run log db7bc753, verified against t5a_mag_results.json)

| ref | $M$ | sign-agree | $\max|q|$ | $\mathrm{mean}|q|$ | Pearson $|q|$ vs $M=0$ spread |
|---|---|---|---|---|---|
| all-a | $+4$ | — (all $q\approx 0$) | 8.7e-18 | 2.8e-18 | $-0.12$ |
| | $+3$ | 0.50 | 1.32e-02 | 4.78e-03 | $+0.01$ |
| | $+2$ | 0.60 | 2.50e-02 | 8.76e-03 | $+0.14$ |
| | $+1$ | 0.60 | 6.58e-03 | 2.82e-03 | $+0.24$ |
| spread | $0$ | 0.60 | 3.23e-02 | 7.36e-03 | $+1.00$ |
| concentrated | $0$ | 0.50 | 4.81e-02 | 2.25e-02 | $+0.76$ (signed $+0.86$) |
| | $-1$ | 0.60 | 6.58e-03 | 2.82e-03 | $+0.24$ |
| | $-2$ | 0.60 | 2.50e-02 | 8.76e-03 | $+0.14$ |
| | $-3$ | 0.50 | 1.32e-02 | 4.78e-03 | $+0.01$ |
| all-b | $-4$ | — (all $q\approx 0$) | 1.4e-17 | 2.6e-18 | $-0.24$ |

## Secondary observations

1. **Polarized endpoints freeze:** $M=\pm 4$ (all-a / all-b) give $q\approx 1\mathrm{e}{-17}$
   (numerical zero) on all triples — confirms the $N_b=0$ / $N_a=0$
   spin-freezing mechanism in this engine.
2. **$a \leftrightarrow b$ mirror symmetry exact:** $M=+k$ and $M=-k$ give byte-identical $q$
   vectors ($J_i \cdot J_j$ is invariant under $a \leftrightarrow b$), as expected.
3. **Spatial control at $M=0$:** concentrating all $b$-bosons on one edge
   (vs spread) preserves the triple pattern (Pearson $|q|$ $+0.76$, signed
   $+0.86$) but rescales $\mathrm{mean}|q|$ $\times 3$ (7.4e-3 → 2.25e-2).
4. **Across-$M$ decoherence:** $|q|$-pattern correlation vs the $M=0$ baseline
   decays $1.0 \to 0.24 \to 0.14 \to 0.01$ with growing $|M|$ — which triple is
   loudest is $M$-sector-dependent.
5. **Magnitude is non-monotonic in $|M|$**, peaking at $M=0$ concentrated.

## Red-team check

Recomputed $q_{123}$ for $M=0$ spread via the explicit commutator
$q=i[A_{12},A_{23}]$ expectation: 0.003811345194626947 (imag 2.5e-17),
matching the $-2\mathrm{Im}$ route (0.0038113451946269385) and the run log
(+3.811345e-03). $q$ is real as required. PASSED.

## Caveats

Single fixed plane, n=5, K=8, 10 triples/state — modest sign-test power.
Multi-seed sweep and a Rust cross-check (T5a driver engine) are natural
follow-ups. Python fixed-K engine is new code (t5a_mag_sweep.py);
cross-validation against the Rust t5a binary at a shared (n, K, ref)
point is still open.

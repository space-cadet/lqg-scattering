# Red-team audit of follow-up numerical claims

*2026-10-01, source branch `main`, source commit `cfaf6866c92c8c4d1bda35473bd67bb4bdeb885a`.*

This is an independent claim review, not a full program sign-off. The
published EPJC paper is unchanged. The checks below used the repository's
Python operator definitions and SciPy's `expm_multiply` as an independent
state-construction method. The corrected Rust implementation was run with the host toolchain. Its release suite passed 20 tests, and the converged `verify4` and `scan` commands completed. Independent SciPy state exponentiation checked the complex-plane results at $n=4,5,7,8$; $n=6$ has Rust convergence evidence but no independent exponential check.

## Central distinction: which volume was calculated?

The implementation forms the Hermitian signed triple grasp
$q_{ijk}=i[J_i\cdot J_j,J_j\cdot J_k]$ and reports
$V_{\rm proxy}=(\gamma\hbar)^{3/2}\sqrt{|\langle q_{ijk}\rangle|}$.
It does not calculate the expectation of a positive volume operator such as
$(\gamma\hbar)^{3/2}\langle\sqrt{|q_{ijk}|}\rangle$. The two expressions
cannot be interchanged. Even for one triple, the latter is positive when
$q_{ijk}|\psi\rangle\ne0$.

For a moment-curve positive plane at $n=4$, seed 11, $K=6$, reference
occupations `[(1,1),(1,1),(1,0),(1,0)]`, and triple `(0,1,2)`, SciPy's
matrix exponential gives $\langle q\rangle=-5.2\times10^{-18}i$ from
rounding, while $\langle q^2\rangle=\|q|\psi\rangle\|^2=0.375981088857$.
Thus the signed mean vanishes, but $q$ does not annihilate this positive-plane
state. A zero expectation of a positive volume operator is not supported.
The full vertex volume operator may also involve a prescribed combination
of triples; this audit does not identify that prescription.

## Real planes are a wider zero set than the positive cell

For a real plane, $Z$ and the coherent-state amplitudes are real in the
occupation basis. The matrices $J_i\cdot J_j$ are real symmetric, so
$q_{ijk}=i[A_{ij},A_{jk}]$ is imaginary antisymmetric. Consequently
$\langle q_{ijk}\rangle=0$ for a real state and any triple. Positivity of
the plane is sufficient for this cancellation, not necessary.

As a numerical control, use the real plane
$C=\begin{pmatrix}1&0&-2&-1\\0&1&1&1\end{pmatrix}$. Its six ordered minors
are $(1,1,1,2,1,-1)$. No combination of column sign flips makes all
minors positive, and the repository's `is_positive_plane` returns false.
The independently exponentiated state still has real amplitudes and
$\langle q\rangle=0$ to computed precision; its
$\langle q^2\rangle=0.3080495$.
Claims that the positive cell is *the* achiral locus or that the signed mean
becomes nonzero everywhere immediately outside it are false as stated.

## Shared Taylor truncation invalidates the old baseline comparison

The historical `verify4` Python and Rust paths used 15 Taylor terms for
$e^A|\mathrm{ref}\rangle$. Agreement between them tested implementation
consistency under the same truncation, not state convergence. At the
canonical complex plane, the old state differs from `expm_multiply` by
$0.0117332$ in vector norm. A converged Taylor calculation takes 34 terms
and agrees with `expm_multiply` within $1.6\times10^{-14}$ in vector norm.

| $n=4$, $K=6$ complex plane | Historical 15-term | Converged SciPy |
|---|---:|---:|
| $\langle q\rangle$ | $-0.000849657246$ | $-0.000827687168$ |
| $V_{\rm proxy}/\gamma^{3/2}$ | $0.029148881$ | $0.028769553$ |

The positive-plane old state also differs from the independent exponential
by $0.0153219$ in vector norm. Its signed mean remains zero by reality;
the square-root proxy around $10^{-9}$ reflects amplification of floating
residuals and must not be called machine precision in $V_{\rm proxy}$.
The performance table and dashboard also labeled the $n=4$, $K=6$
`verify4` basis as dimension 10; its actual total-occupation basis has
$\binom{2n+K}{K}=\binom{14}{6}=3003$ states.
The original $n=5$–$8$ complex-plane magnitudes were superseded by the converged Rust scan below. Historical timings remain records of those older runs. The Rust on-the-fly wrapper also discarded its diagnostic
convergence flag; it now fails if the cap is reached, but the older runs
did not record that flag.

The corrected core Python path (`coherent_states.py` through
`positivity.py`) was rerun at the canonical $n=4$ positive and complex
planes. It reproduces the independent complex-plane result
$\langle q\rangle=-0.000827687168$ and
$V_{\rm proxy}/\gamma^{3/2}=0.028769553$. It also rejects the real
mixed-sign-minor plane while returning zero signed mean there. The corrected Rust `verify4` gives the same complex-plane signed mean to displayed precision; T3d's numerical comparison is complete.

## Converged Rust baseline

The host Rust 1.92 release suite passed 20 tests. `verify4` returned complex-plane $\langle q\rangle=-0.0008276871677210$ and $V_{\rm proxy}/\gamma^{3/2}=0.02876955278973$. The positive-plane signed mean printed as zero, with a $2.21\times10^{-9}$ proxy floor from rounding. The full `scan` used the repository's fixed seeds, references and $10^{-12}$ Taylor increment tolerance. Times are wall-clock measurements for this run, not controlled performance comparisons.

| $n$ | $K$ | dimension | positive-plane proxy | complex-plane proxy | independent SciPy check |
|---:|---:|---:|---:|---:|---|
| 4 | 6 | 3,003 | $2.214953\times10^{-9}$ | $0.02876955278973$ | yes |
| 5 | 8 | 43,758 | $3.286511\times10^{-9}$ | $0.03391578040395$ | yes |
| 6 | 9 | 293,930 | $8.811059\times10^{-10}$ | $0.001315280547001$ | pending |
| 7 | 6 | 38,760 | $3.661094\times10^{-10}$ | $0.01186077720871$ | yes |
| 8 | 6 | 74,613 | $1.304153\times10^{-9}$ | $0.01056697265461$ | yes |

All entries are signed-mean proxies, not positive quantum-volume expectations. The independent $n=5,7,8$ checks used a fixed-$K$ basis and SciPy `expm_multiply`; their values agree with the Rust full-basis scan. The $n=6$ point should be independently checked before a strong quantitative claim.

## Other claims checked and held at their evidence level

| Claim | Audit disposition |
|---|---|
| T5b $\sqrt{\epsilon}$ onset | The original sweep used a short Taylor cap. A corrected 13-point rerun with a convergence assertion gives proxy exponents $0.496907$ ($n=4$) and $0.499104$ ($n=5$); saved values are in `t5b_results.json`. Independent SciPy exponentiation agrees at four $n=4$ points and three $n=5$ points (largest $n=5$ proxy difference $4.2\times10^{-17}$). Universality across planes remains open. |
| T5a magnetization sweep | The original 24-term run was unconverged. A corrected rerun converged in 39–41 terms; four sectors matched independent SciPy exponentiation within $3.6\times10^{-16}$ in all triple means. The 0.50–0.60 sign agreement is supported for that one plane, not established generally. |
| T5a′ local-triple sign test | Limited sample count and a shared reference truncation. Its recorded observation is not a general handedness result. |
| T5e semiclassical law | Converged recorded families reach $K=24$ and do not show a general $K^{3/2}$ proxy law. A classical-volume match is open. |
| T7 thermal/TFD | Diagonal Gibbs states have zero signed mean and can have nonzero $q^2$. The reported negative two-sided $q$ correlator uses the same matrix representation on the right copy; a conjugate right-operator convention changes the sign. Fixed-$K$ T7e is temperature-flat by construction. |

## Research sequence and sign-off conditions

1. Specify the physical volume operator, its triple/sign prescription, and
   whether each plotted quantity is $\langle q\rangle$,
   $\sqrt{|\langle q\rangle|}$, $\langle q^2\rangle$, or
   $\langle\sqrt{|q|}\rangle$. Do not infer the last from the first.
2. Independently check the corrected $n=6$ scan point, and preserve the frozen seeds, references, tolerances and code revision with the baseline artifact.
3. Extend the corrected T5a magnetization and T5b perturbation sweeps to
   independent plane/reference controls.
   Recheck T5a′'s shared reference and limited sign-test power. For T5d,
   include positive real, mixed-sign real, and complex controls and define a
   gauge-invariant phase defect around the wider real zero set.
4. Reconstruct a state-dependent polyhedron for T5c/T6 and compare each
   explicitly defined quantum observable with its classical volume across
   controlled $K$ and plane families. Extend T5e only where it tests that
   comparison.
5. Revisit the TFD right-operator convention and energy/cutoff controls
   before generalizing T7. Then connect stable geometry to scattering
   kinematics (T8b, formerly T5f); use T5g profiling only as needed.
6. Update the claim ledger and manuscript after each rerun. Circulation
   requires an independent review of the corrected numerical artifacts and
   their precise claim limits.

No repository-wide five-gate red-team checklist was found. The existing
`verification-protocol.md` covers an $n=4$ cross-implementation comparison
but does not supply a claim-by-claim sign-off. This audit records the
necessary checks and leaves unresolved claims open.

## Positive-volume implementation follow-up

The legacy Rust/Python scans audited above still report signed-mean proxies. New routines now implement both vertex structures in repository-normalized units: RS sums $\sqrt{|q_{IJK}|}$ contributions; AL takes $\sqrt{|\sum \epsilon(e_I,e_J,e_K)q_{IJK}|}$ using caller-supplied embedding signs. Exact dense diagonalization is split by conserved edge-spin and total-magnetic sectors and refuses active blocks above 512.

For the normalized paired spin-1/2 singlet on four edges, regular-tetrahedron signs $(+,-,+,-)$ give $\langle q_{012}\rangle=0$, $V_{RS}=0.304653190236$, and $V_{AL}=0.152326595118$ with the project prefactor $(\gamma\hbar)^{3/2}$. A collinear four-edge product gives zero for both. Python, Rust, and an independent tensor-product Pauli-matrix calculation agree. These are normalized implementation checks, not physical-volume claims: standard regularization prefactors, AL embeddings for the project coherent states, and large active blocks remain unresolved.

## Related documentation

- [Shared volume numerical preliminaries](./volume-numerical-preliminaries.md)
- [T5 volume-positivity studies](./volume-positivity-studies.md)
- [T5c classical-volume comparison specification](./T5c-flux-covariance-volume-comparison.md)
- [Implemented volume operators](./volume-operator.md)
- [T6 Minkowski reconstruction](./T6-minkowski-polyhedron.md)
- [Verification protocol](./verification-protocol.md)
- [Performance benchmarks](./performance-benchmarks.md)

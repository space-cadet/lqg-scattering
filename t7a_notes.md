# T7a notes: single-copy thermal state — areas, null mean volume, $q^2$ fluctuations

## Construction

$\rho_\beta = \exp(-\beta H)/Z$ on ONE Schwinger system, $H = \sum_i (n_{a,i}+n_{b,i})$
($\omega = 1$, occupation-diagonal, so the Boltzmann factor is exact — no Taylor).
Conventions held fixed from T5b: n = 4, 5; capped Fock basis (total $\leq K$,
$K = N+3$); real moment-curve plane, seeds 11/12, NO complexification;
`vertex_reference`; gamma = 0.2375; $q = i[A_{01},A_{12}]$, triple (0,1,2).
Perelomov states use the converged Taylor ($8K+50$ cap + assert; 38/40 iters).

Three families per beta in {0, 0.1, 0.5, 1, 2, 5, 10}:
(A) plain Gibbs diagonal $w \propto e^{-\beta E}$ (plane-independent control);
(B) Perelomov-weighted diagonal $w \propto |c_n|^2 e^{-\beta E}$ (plane-dependent);
(C) thermally-rescaled pure $|\psi_\beta\rangle \propto c_n e^{-\beta E/2} |n\rangle$ (TFD precursor).

## Results (run 0551787b, full tables in t7a_results.json)

1. **Thermal areas are nonzero.** Gibbs: uniform across edges ($\omega$ uniform),
   0.369 (n=4) / 0.346 (n=5) per edge at $\beta=0$ → $\sim 2\mathrm{e}{-5}$ at $\beta=10$.
   Perelomov-weighted ($\beta$-flat, = Perelomov areas): n=4
   [0.439, 0.383, 0.469, 0.371], sum = $\gamma K$ ✓; n=5
   [0.438, 0.436, 0.427, 0.255, 0.344], sum = $\gamma K$ ✓.
2. **Mean volume is EXACTLY zero** — bit-exact $+0.00\mathrm{e}{+00}$ at every $\beta$ in all
   three families, both n. Mechanism: $A_{ij}$ are real-symmetric, so
   $q = i[A_{01},A_{12}]$ is imaginary-antisymmetric with identically zero diagonal
   ($\max|\mathrm{diag}(q)| = 0.00\mathrm{e}{+00}$); the pure state adds reality
   ($\max|\mathrm{imag}(\psi)| = 0$). **Theorem: no ensemble diagonal in the occupation
   basis carries volume.** Control $V(\epsilon=0) = 2.6\mathrm{e}{-10}$ (rounding noise).
3. **Fluctuations are nonzero — this is where the thermal volume info lives.**
   Gibbs $\mathrm{Tr}(\rho q^2)$: 0.357/0.349 ($\beta=0$) → $7\mathrm{e}{-14}$ ($\beta=10$).
   Perelomov-weighted: 0.785 (n=4), 0.679 (n=5), $\beta$-flat.
   Pure-rescaled $\langle q^2 \rangle$: 0.707 (n=4), 0.719 (n=5), $\beta$-flat.

## Structural finding (load-bearing for T7b)

Families B and C are $\beta$-FLAT by construction: $A(Z) = \sum Z_{ij} E_{ij}$
preserves total boson number, so the Perelomov state sits entirely in the $E=K$
sector and $\exp(-\beta E/2)$ is constant on its support. Thermalizing fixed-$K$
coherence does nothing. Genuine temperature dependence needs the full Gibbs
ensemble (which forgets the plane) — or the doubled TFD, where $\beta$ enters via
L–R entanglement across $E$ sectors. **T7b should therefore purify the full
occupation basis (Gibbs), not the Perelomov-weighted one.**

## Cutoff validity (caveat 2)

Boundary weight $P(E=K)$: 0.53/0.56 at $\beta=0$ → $1\mathrm{e}{-27}/1\mathrm{e}{-31}$ at $\beta=10$.
$Z_{\mathrm{capped}}/Z_{\mathrm{inf}}$: $2\mathrm{e}{-5}/1\mathrm{e}{-6}$ at $\beta=0.1$ (cutoff bites) → 0.86/0.82 at $\beta=1$ →
1.000 at $\beta \geq 2$. Trust $\beta \gtrsim 1$ quantitatively; $\beta \leq 0.5$ is qualitative.
Gibbs entropy $S$: 8.77/10.69 ($\beta=0$) → $\sim 0$ ($\beta=10$); recorded for T7b
entropy-matching ($S(\beta)$ vs TFD entanglement).

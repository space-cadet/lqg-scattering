# T7 physical thermal-intertwiner audit

*Recorded: 2026-10-06 12:08:08 IST*

Full derivations and worked calculation: [mathematical background](T7-mathematical-background-and-calculations.md).

## Construction and scope

`t7_geometry_thermal.py` implements the thermal-intertwiners draft's same-mode Bogoliubov squeeze of a normalized FL singlet seed on L and the vacuum on R. Four faces, total seed spin-area $J=1,2$ ($K_0=2J$ bosons), regular and unequal-skew input tetrahedra are tested at $\beta=3,4,5,8$, $\omega=1$. These are quantum states labelled by closed tetrahedron data; they are not an enumeration of classical shapes. Finite-$J$ fluctuations and zero-area face sectors remain present.

For seed occupation $n$ and created pair occupations $r$, the exact coefficient is
$$
c_n(1-x)^{(K_0+8)/2}x^{|r|/2}\sqrt{\prod_\mu {n_\mu+r_\mu\choose r_\mu}},\qquad x=e^{-\beta}.
$$
The retained state includes total created pairs $|r|\le4$. Left and right boson numbers are $K_0+|r|$ and $|r|$; this is an area-changing construction. Reduced states, entropy, face-area means, flux Gram matrices, signed triple moments and positive RS/AL volume moments are computed. Volume uses existing repository prefactors and AL signs $(1,-1,1,-1)$; absolute physical normalization is not resolved.

## Constraint result

The draft squeeze preserves the combined constraint with the conjugate right representation, $\mathbf J_L-\mathbf J_R^T$. It does not preserve ordinary Gauss closure independently on L and R. For any singlet seed in the tested construction, the exact untruncated ordinary defect on each copy is
$$
\langle\mathbf J_L^2\rangle=\langle\mathbf J_R^2\rangle
=\frac34(K_0+8)\bar n(1+\bar n),\qquad \bar n=(e^\beta-1)^{-1}.
$$
For $J=2$, $\beta=5$, the exact defect is $0.0614670559$; the retained-state result is $0.0614667783$. Thus the ordinary face fluxes do not describe two independently closed polyhedra. Conjugated Gauss operators $U\mathbf J_LU^\dagger$ and $U\mathbf J_RU^\dagger$ do annihilate the squeezed state. If geometry is also wholly conjugated, its expectation values equal the seed's values; the observable convention is therefore part of the physical question.

## Conditional candidate

The script separately implements and normalizes $(P_{L,0}\otimes P_{R,0})U(|J,z\rangle_L|0\rangle_R)$. This is explicit singlet postselection, changes the draft state, and is not established as a Gibbs ensemble or unique thermal prescription. Both ordinary constraints vanish numerically. Odd created-pair sectors vanish under this projection.

At regular $J=2$, $\beta=5$, retained projection probability is $0.922702874$, left entropy is $0.006750920$, and RS expectation changes from seed $0.050775532$ to $0.050823437$. The unequal-skew seed gives $0.044958686$ and candidate $0.045005713$. The calculation distinguishes input geometries at $J=2$; $J=1$ seed volume vanishes for both examples.

## Verification and limits

- Squeeze coefficients agree with independent matrix exponentiation to $1.67\times10^{-16}$.
- Singlet dimensions for total bosons $0\ldots6$ are $1,0,6,0,20,0,50$, agreeing with the four-face representation formula.
- Seed volumes agree with the existing RS/AL implementation to numerical precision; this checks assembly, not independence of the shared triple operator.
- Each exact pair sector has the expected negative-binomial norm. Combined dual closure vanishes; both projected ordinary closure residuals are below $10^{-10}$.
- At $J=2$, $\beta=5$, conditional omitted-probability upper bound is $6.18\times10^{-8}$. Increasing pair cutoff from 2 to 4 changes candidate RS volume by $3.39\times10^{-8}$ and entropy by $4.12\times10^{-6}$.
- At $\beta=3$, the corresponding bound is $0.00149$; these warmer results are less converged. Probability bounds do not by themselves bound unbounded volume moments or entropy. Explicit cutoff comparisons are recorded; no high-temperature limit is claimed.
- Python completed this pilot. Larger $J$ and warmer states may require sparse singlet bases, recoupling methods, or Rust; changing language alone does not remove Hilbert-space growth.

## Steps needed next

1. Fix the intended geometric observables: ordinary fluxes on two independently closed copies, or consistently transformed fluxes.
2. For ordinary fluxes, choose and justify a singlet-preserving thermal operation or a physical-Hilbert-space Gibbs/TFD ensemble. The implemented postselection is one diagnostic candidate.
3. Specify the Hamiltonian and whether area varies. $H=2J$ is scalar in a fixed-$J$ physical sector, so its Gibbs state there has no temperature-dependent weighting within that sector.
4. Extend cutoff and area coverage only for the selected construction; compare face correlations and positive volume with the same closed input geometry.
5. T9 now owns state definitions, construction, and geometric/physical study; this note records the work transferred from the former T7 umbrella. Preserve completed T7a–T7e findings within their recorded oscillator/Gibbs scope; they do not establish the new physical thermal-polyhedron response.

Artifacts: `t7_geometry_thermal.py`, `t7_geometry_thermal_results.json`. The manuscript has not been edited.

## T9 follow-up — 2026-10-06

The user selected the two-copy construction $U_\beta(|J,z\rangle_L\otimes|\overline{J,z}\rangle_R)$, with transformed geometric observables. This resolves the earlier choice between ordinary and consistently transformed observables for the current mathematical analysis; it does not select the construction as a Gibbs state or establish a canonical energy-basis TFD. The $SU(1,1)$ factorization and occupation expansion are derived in the [mathematical-background note](T7-mathematical-background-and-calculations.md#11-t9-follow-up-squeeze-two-conjugate-fl-intertwiners). Reduced-state and geometry calculations remain open. The earlier one-sided squeeze and projected candidate above remain the results of their original pilot.

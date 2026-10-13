# Separately closed thermal intertwiners

Calculated 2026-10-13. This examines double-singlet projection of the same selected four-face $J_{\mathrm{in}}=1$ two-FL construction used in the preceding closure-temperature sweep. The input in each copy is the normalized reference $F_{12}^\dagger|0\rangle/\sqrt2$, with conjugate pairing on the right.

## Construction and answer

Let $P_{X,0}$ project onto ordinary total-spin-zero states in copy $X$. Define

$$
|\Psi_\beta^{\mathrm{closed}}\rangle
=\frac{(P_{L,0}\otimes P_{R,0})U_\beta
(|\phi\rangle_L\otimes|\overline\phi\rangle_R)}{\sqrt{p_\beta}}.
$$

Both ordinary Gauss constraints annihilate this state:

$$
(\mathbf G_L\otimes I_R)|\Psi_\beta^{\mathrm{closed}}\rangle=0,
\qquad
(I_L\otimes\mathbf G_R)|\Psi_\beta^{\mathrm{closed}}\rangle=0.
$$

This gives exact separate closure at every finite temperature while preserving temperature-dependent area, positive volume, and fluctuations. In this model $p_\beta$ is strictly positive for every finite temperature: at positive temperature the vacuum-vacuum sector alone contributes $(1-e^{-b})^8e^{-2b}>0$, with $b=\beta\hbar\omega$; at zero temperature the original closed product returns and $p=1$.

## Why the retained probability is not squared

Combined dual-copy invariance implies the sector coefficient matrices obey $\mathbf G C_q=C_q\mathbf G$. They connect only equal left/right resultant-spin sectors. Therefore selecting $S_L=0$ already selects $S_R=0$, and

$$
p_\beta=\|(P_{L,0}\otimes P_{R,0})|\Psi_\beta\rangle\|^2
=\sum_{q\ \mathrm{even}}P(q,S=0).
$$

The previous marginal singlet fraction becomes the actual double-projection probability. This equality is verified directly on the doubled coefficient matrices through $q=4$.

## Results after projection and normalization

Temperature is $T_*=k_BT/(\hbar\omega)$. Final total linear area is $A=q/2$, in spin-area units; volume uses the existing positive RS operator with four triples, $\gamma=0.2375$, $\hbar=1$, in project units.

| $T_*$ | Retained fraction | Mean area | Mean positive RS volume | Four nonzero-area faces |
|---:|---:|---:|---:|---:|
| 0.125 | 99.5316% | 1.000002 | $3.43\times10^{-8}$ | 0.0000113% |
| 0.25 | 77.7501% | 1.006029 | 0.0001025 | 0.03367% |
| 0.5 | 19.5317% | 1.302780 | 0.0064133 | 2.1122% |
| 1 | 2.64065% | 2.787747 | 0.0723452 | 18.6059% |
| 2 | 0.340367% | 6.475739 | 0.3535060 | 48.4812% |

All projected components are separately closed. Closure permits zero-area faces and zero-volume states: the $J=1$ input reference itself has only two active faces and zero volume. The reported active-face fraction distinguishes closed degenerate configurations from four-active-face support. At $T_*=1$, 14.08% of the projected state has nonzero volume; at $T_*=2$, 36.34% does. These are obtained from the positive-volume kernel projector, not from a signed mean.

The projected state retains a changing area distribution. The retained fraction decreases as heating puts more of the unprojected state into nonsinglet sectors; the normalized closed fraction expands in area and develops positive volume. Projection changes the state; it is an explicit way to impose separate closure on the original construction.

## Calculation and verification

- Evaluated 85 temperatures across $T_*=0.05\ldots2$.
- Occupation/singlet probabilities extend through $q=160$ using the established magnetic-counting method, checked against group-spin recoupling at six temperatures.
- Volume traces extend through total area $A=50$. Within each singlet block, the projected coefficient polynomial is diagonal in the $((j_1,j_2)k,(j_3,j_4)k)$ basis. All ordered face-spin assignments are included, using exact permutation multiplicities.
- The analytic tridiagonal triple-grasp representation supplies positive RS moments and kernel weights. Probability, first/second volume moment, and active-face polynomial traces agree with the independently constructed saved catalogue for every area $2\ldots12$; maximum relative difference is below $2.2\times10^{-15}$.
- Independent archived grasp spectra validate kernel weights on 148 blocks, maximum difference below $1.4\times10^{-15}$.
- Direct coefficient-matrix double projection at $q=0,2,4$ verifies probability equality, absence of cross-spin leakage, and both ordinary closure constraints; maximum squared closure residual is below $2.4\times10^{-32}$.
- A rigorous operator bound $\|V_{\mathrm{RS}}\|\le4\gamma^{3/2}\sqrt{2/9}\,A^{3/2}$ bounds omitted volume contributions. The largest conditional mean-volume tail bound is below $5.4\times10^{-12}$. Probability and moment cutoffs are bounded rather than silently renormalized.

The exported figure was visually inspected for readable, unclipped labels. Settings, source hashes and all numerical residuals are saved in [protocol.json](protocol.json) and [verification.json](verification.json).

## Organized source and artifacts

- Driver: [closed_projection_study.py](../../code/thermal/closed_projection_study.py).
- Shared library: [thermal_projection.py](../../code/python/lqg_scattering/thermal_projection.py).
- Earlier ordinary-closure driver: [closure_temperature_sweep.py](../../code/thermal/closure_temperature_sweep.py).
- Existing probability calculator: [compare_j1_spin_methods.py](../../code/thermal/compare_j1_spin_methods.py).
- [Temperature summaries](temperature_summary.csv), [conditional area distributions](area_distribution.csv), and [sector traces](singlet_sector_traces.npz).
- [Vector PDF](../../figures/thermal-closed-projection/closed_projection_temperature.pdf) and [300 dpi PNG](../../figures/thermal-closed-projection/closed_projection_temperature.png).

Reproduce in the existing research Python environment:

```sh
PYTHONPATH=code/python python code/thermal/closed_projection_study.py
```

## Temperature slopes and exact area asymptote

A follow-up fit uses 1,001 uniformly spaced temperatures over $1\le T_*\le2$, evaluating the saved singlet-sector traces directly. The fitted lines are

$$
\langle A\rangle\simeq3.7021308T_*-0.9640557,
\qquad
\langle V_{\mathrm{RS}}\rangle\simeq0.2826230T_*-0.2237750.
$$

The area line has $R^2=0.999686$ and maximum relative residual 1.78%. The volume line has $R^2=0.995148$, but maximum relative residual 18.66%; its local slope rises from 0.19610 at $T_*=1$ to 0.35126 at $T_*=2$. Thus 0.282623 is an interval-average slope rather than a temperature-independent proportionality constant. Fits include intercepts and are not fits through the origin.

For area, an exact finite-sum derivation gives

$$
\lim_{T_*\to\infty}\frac{\langle A\rangle}{T_*}
=\frac{57}{14}=4.0714285714.
$$

To obtain it, resolve a total-area-$K$ singlet into two group spins. Write $r,l\ge0$, $r+l\le K$, and twice the group spin as $K-r-l$. The multiplicity is $(K-r-l+1)^2$, the pair-annihilation eigenvalue is $f=r(K-l+1)$, and the first-pair occupation is $a=K+r-l$. The six exact probability traces are the double sums of this multiplicity times $[f^2,a^2,1,fa,f,a]$. Their polynomial degrees are $[8,6,4,7,6,5]$; their leading coefficients are $[1/240,4/45,1/12,1/60,1/72,1/12]$. These symbolic sums match every saved sector through $K=50$ exactly.

Combining their high-temperature weights gives $p_{\mathrm{closed}}\sim(7/256)b^3$ and the unnormalized first area moment $\sim(57/512)b^2$, where $b=1/T_*$. Their ratio yields $57/(14b)$. This is a derived asymptote and does not rely on truncating a high-temperature distribution at $K=50$.

[Fit and derivation script](../../code/thermal/fit_closed_temperature.py), [fit report](temperature_fit.json), and [uniform fitting grid](temperature_fit_grid.csv).

```sh
PYTHONPATH=code/python python code/thermal/fit_closed_temperature.py
```

The pedagogical account is in [the thermal-area note](../../notes/thermal-area-sectors.md#section-16). Its additional [area-distribution and geometric-support figure](../../figures/thermal-closed-projection/closed_projection_distributions.pdf) is generated from saved data by [plot_closed_temperature_writeup.py](../../code/thermal/plot_closed_temperature_writeup.py).

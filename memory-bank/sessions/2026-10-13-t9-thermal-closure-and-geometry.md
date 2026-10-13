# T9 thermal closure and growth of closed geometry — 2026-10-13

*Recorded: 2026-10-13 22:50:22 IST*

This continuation measures how temperature changes ordinary closure, then asks whether imposing separate closure removes the thermal growth of geometry.

The ordinary per-copy constraint is $\mathbf G=\sum_i\mathbf J_i$. The doubled state remains annihilated by the combined dual-copy generator $\mathbf G_L\otimes I-I\otimes\overline{\mathbf G}_R$. Imposing ordinary closure on both copies requires the singlet projector $P_{L,0}\otimes P_{R,0}$, which selects closed sectors while allowing area to fluctuate.

For the four-face $J_{\mathrm{in}}=1$ reference, the closure sweep covers 125 temperatures and the projected-geometry calculation covers 85. The per-copy RMS flux defect rises with temperature while the singlet fraction falls. After projection, the state remains exactly closed and its conditional area distribution broadens. The mean area grows from 1.000 at $T_*=0.125$ to 2.788 at $T_*=1$ and 6.476 at $T_*=2$. The corresponding mean positive RS volumes are $3.43\times10^{-8}$, 0.07235, and 0.35351. The symbolic high-temperature result is

$$
\langle A\rangle\sim\frac{57}{14}T_*.
$$

The positive-volume curve increases but is nonlinear over the studied range. At $T_*=1$ and 2, the conditional probabilities of four active faces are 18.61% and 48.48%; probabilities of nonzero RS volume are 14.08% and 36.34%. The retained projection probabilities at those temperatures are 0.02641 and 0.003404.

Checks include magnetic-counting and recoupling agreement, direct small-sector double projection, both Gauss constraints, volume traces against the saved closed-basis catalogue through area 12, and comparison with 148 archived grasp blocks. The maximum independent grasp-block discrepancy is $1.33\times10^{-15}$; the largest bound on the omitted conditional mean-volume contribution is $5.4\times10^{-12}$.

The pedagogical account, tables, and figures are in [thermal-area-sectors.md](../../notes/thermal-area-sectors.md#section-16). Reproduction sources are [the closure sweep](../../code/thermal/closure_temperature_sweep.py), [the projection study](../../code/thermal/closed_projection_study.py), [the fit](../../code/thermal/fit_closed_temperature.py), [the plots](../../code/thermal/plot_closed_temperature_writeup.py), and [the shared projection routines](../../code/python/lqg_scattering/thermal_projection.py). Full protocols and data are in the [closure report](../../results/thermal-closure-temperature/README.md) and [closed-projection report](../../results/thermal-closed-projection/README.md). T9 remains in progress; full selected-state reduced blocks and Gibbs characterization are still part of the broader program.

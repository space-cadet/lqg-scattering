# Total-spin distribution of the squeezed vacuum

Calculated 2026-10-08 by GPT 6.1 Sol. The state is the four-face, initial-$J=0$ same-mode squeezed vacuum, with no separate singlet projection. The plotted spin $S$ is the ordinary resultant spin of **one copy**; it is not the combined dual-copy spin or the transformed spin.

At fixed boson number $q$, every occupation vector has the same reduced-state weight. Consequently the conditional density matrix is $I_q/g_q$, where $g_q=\binom{q+2N-1}{2N-1}$. With $N=4$, count the states at magnetic number $M$ as

$$
D(q,M)=\binom{q/2+M+N-1}{N-1}\binom{q/2-M+N-1}{N-1}.
$$

This is zero unless the two species totals are nonnegative integers. Each spin-$S$ multiplet supplies one state at every $M=-S,\ldots,S$, so the multiplicity is $D(q,S)-D(q,S+1)$. Therefore

$$
P(S\mid q)=\frac{(2S+1)[D(q,S)-D(q,S+1)]}{g_q}.
$$

Allowed spins run from $0$ to $q/2$ for even $q$, and from $1/2$ to $q/2$ for odd $q$, in unit steps. The conditional distribution is independent of temperature for this vacuum input. Its average closure Casimir is

$$
\langle\mathbf G_L^2\rangle_q=\langle S(S+1)\rangle_q
=\frac{3q(q+2N)}{4(2N+1)},
$$

with dimensionless angular-momentum operators. The orange curve plots the square root of this quantity, not the mean spin.

The joint thermal weights use $b=\beta\hbar\omega=1$ and

$$
P(q,S)=p_qP(S\mid q),\qquad
p_q=(1-e^{-b})^{2N}g_qe^{-bq}.
$$

The plot retains $q=0,\ldots,26$; omitted probability is below $10^{-6}$, without renormalizing the displayed weights. This probability bound does not by itself bound errors in unbounded observables. The conditional moments are calculated exactly at each displayed $q$, rather than estimated from a truncated ensemble.

At $q=0$ only $S=0$ occurs; at $q=1$ only $S=1/2$ occurs. At $q=2$, $P(S=0\mid q)=1/6$ and $P(S=1\mid q)=5/6$. Nonvacuum even-$q$ sectors thus contain singlet components, although their individual occupation vectors are not singlets. The reduced state is rotationally invariant, but is not supported solely on $S=0$. A zero mean flux does not establish closure.

The counting was cross-checked against $U(N)$ Weyl dimensions for highest weights $[q/2+S,q/2-S,0,\ldots]$, and against directly constructed Schwinger total-spin Casimir eigenspectra for $q=0,1,2,3,4$. The representation relation is discussed in [Freidel–Livine, Eq. (21)](https://arxiv.org/html/0911.3553); the probability calculation here uses the selected oscillator vacuum marginal.

Reproduce with the dependencies in [requirements.txt](../../code/thermal/requirements.txt):

```bash
python code/thermal/plot_vacuum_spin.py
```

Artifacts: [PDF](thermal_vacuum_spin.pdf), [PNG](thermal_vacuum_spin.png), [CSV](thermal_vacuum_spin.csv), [checks and settings](thermal_vacuum_spin_summary.json), and [source](../../code/thermal/plot_vacuum_spin.py).

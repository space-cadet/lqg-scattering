# Temperature and the amount of closure

Calculated 2026-10-13 for T9's selected symmetric two-copy squeeze of the normalized four-face $J_{\mathrm{in}}=1$ reference $F_{12}^\dagger|0\rangle/\sqrt2$ and its conjugate. The same input and coefficient methods are used by `code/thermal/compare_j1_spin_methods.py`. This calculation measures ordinary closure in either copy, without singlet projection.

## Measures

Let $\mathbf G=\sum_i\mathbf J_i$ and $T_*=k_BT/(\hbar\omega)$. Angular momenta are in units of $\hbar$.

- Absolute closure defect: $D=\langle\mathbf G^2\rangle=\sum_{q,S}S(S+1)P(q,S)$; RMS residual is $\sqrt D$.
- Exact closed fraction: $P_0=\sum_qP(q,S=0)$.
- Relative RMS defect: $\sqrt{D/\langle A(A+1)\rangle}$, with final linear area $A=q/2$. This denominator is the maximum resultant-spin Casimir at each occupation, averaged over occupations. It is an explicitly chosen normalization, not a probability.

Both the ordinary mean vector $\langle\mathbf G\rangle$ and the combined dual-copy closure remain zero; neither means that each copy has $S=0$. Consistently transformed per-copy closure also remains exactly zero by unitary conjugation.

## Result

Heating increases the absolute ordinary closure defect and reduces the exact closed fraction throughout the 125 evaluated temperatures, $T_*=0.05\ldots2$. The relative RMS defect peaks at the sampled $T_*=0.8721$ with value $0.59014$, then decreases slightly as total area grows faster than the residual in this normalization. The lower relative value at warmer temperatures is not restoration of exact closure.

| $T_*$ | RMS residual | Exact closed fraction | Relative RMS defect |
|---:|---:|---:|---:|
| 0.125 | 0.05937 | 0.995316 | 0.04190 |
| 0.25 | 0.44672 | 0.777501 | 0.28747 |
| 0.5 | 1.37865 | 0.195317 | 0.54784 |
| 1 | 3.10919 | 0.026406 | 0.58873 |
| 2 | 6.41372 | 0.003404 | 0.56469 |

At zero temperature the construction returns the original closed FL product: $D=0$, $P_0=1$.

## Verification and reproduction

Protocol was saved before the numerical sweep. The calculation sums $P(q,S)$ through $q=160$ without renormalizing the cutoff. Magnetic counting and explicit group-spin recoupling were compared at six inverse temperatures, including a new cold control $\beta\hbar\omega=20$. Normalization and the analytic mean occupation $2+12/(e^{\beta\hbar\omega}-1)$ were checked at every temperature. Saved prior results agree within $2.85\times10^{-14}$. Maximum normalization error is $1.89\times10^{-15}$; omitted probability is bounded by $8.94\times10^{-21}$ and omitted closure Casimir by $6.01\times10^{-17}$. Source hashes and method residuals are in [verification.json](verification.json).

Run with a Python environment containing NumPy, SciPy and Matplotlib:

```sh
python code/thermal/closure_temperature_sweep.py
```

Outputs: [backing CSV](closure_temperature.csv), [protocol](protocol.json), [verification](verification.json), [vector PDF](../../figures/thermal-closure-temperature/closure_temperature.pdf), and [300 dpi PNG](../../figures/thermal-closure-temperature/closure_temperature.png). The exported figure was visually inspected for readable, unclipped labels.

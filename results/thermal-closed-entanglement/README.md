# T9 closed-reference entanglement and joint singlet coherence

Calculated October 16, 2026. The [pedagogical note](../../notes/thermal-entanglement.md)
explains the physical question, derivation, figures and interpretation.

## Scope

Four labelled faces; input F12 singlet of area one on each conjugate-paired
copy; two-copy squeeze followed by normalized separate singlet projection.
The 86-temperature sweep covers T*=0.05..5, with adaptive per-copy area cutoff
12..140. This extends the earlier geometric range beyond T*=2 using analytic
spectrum/tail bounds, without extending volume numerics. No stochastic inputs.
Entropies are S/kB in nats in the ordinary left/right tensor factorization.

At T*=1,2,5, entropy is 4.2499614704, 7.2455421267, 11.6882135279. Within-area
contributions are 2.3116703474, 4.5340173366, 8.0293555103. The joint-creation
coherence is 9.9453994512, 36.3705318491, 222.2542758889. Transfer coherence is
exactly zero by area-difference support. This reference starts with only two
active faces; it is not a regular four-face FL preparation.

## Artifacts and verification

- `protocol.json`: support, fixed settings, tolerance and claim limits, saved before calculation.
- `temperature_summary.csv`: entropy bounds, area/within-area decomposition,
  purity, Rényi-2 entropy, area moments, joint-creation coherence and temperature slopes.
- `area_sectors.csv`: area probabilities and conditional sector entropies.
- `spectrum_T*.npz`: six selected temperatures; `(K,r,l)` labels, raw signed
  amplitudes, individual eigenvalues and their integer multiplicities. Normalize
  with the retained probability through the declared cutoff; infinite-tail
  errors are recorded separately. Load with `allow_pickle=False`.
- `verification.json`: 802 comparisons. Independent per-mode oscillator
  exponentials, Casimir projection/SVD and creator matrices cover small sectors;
  saved magnetic-counting geometry covers earlier temperatures. Cutoff and
  derivative-step checks reuse the analytic spectrum. Maximum non-derivative
  residual 1.8e-11; derivative step discrepancy 6.3e-8 against 2e-6 tolerance.
- `provenance.json`: source/dependency hashes and calculation artifact hashes.
- [Figures](../../figures/thermal-closed-entanglement/): vector PDFs, 300-dpi
  PNGs and backing-array hashes. Both figures were visually inspected.

The maximum analytic entropy truncation estimate is 6.4e-12 nats. Probability,
area moments and coherence have separate infinite-tail estimates. These bounds
do not certify floating-point roundoff. The fixed-H Gibbs obstruction remains;
no entropy slope is identified as heat capacity. No general FL-state,
reservoir-thermalization or AdS/wormhole equivalence is asserted.

## Reproduce

Use the existing scientific environment, from the repository root:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=code/python python code/thermal/closed_entanglement_study.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=code/python python code/thermal/verify_closed_entanglement.py
PYTHONPATH=code/python python code/thermal/plot_closed_entanglement.py
```

The local run used `/Users/deepak/miniconda3/envs/qc-diff/bin/python`.
Redirect verbose logs to a temporary file. Dashboard generation consumes these
saved artifacts; it never reruns the physics.

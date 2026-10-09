# Closed and open Schwinger-state probes

This numerical probe compares three explicit initial states under the
four-site Hamiltonian

$$
H=-t\sum_{\langle i,j\rangle}\left(E_{ij}+E_{ji}\right)
 +\frac{U}{2}\sum_i n_i(n_i-1),
\qquad E_{ij}=a_i^\dagger a_j+b_i^\dagger b_j,
$$

at $t=1$, $U=5$, and $\hbar=1$. It compares the complete graph and the
four-site ring. The stored result is
[`summary.json`](../results/state-space-probes/summary.json); reproduce it
from the repository root with:

```bash
conda run -n qc-diff python code/python/closure_probes.py
```

The three preparations are:

1. The existing four-face Freidel–Livine regular-tetrahedron intertwiner at
   area label $2$, embedded in the four-boson sector. This is an exact total
   spin singlet.
2. A spin-coherent $j=1$ face on site 0, oriented along face 0 of the regular
   tetrahedron, with the other sites empty. This uses two bosons.
3. Three spin-coherent $j=1/2$ faces along tetrahedron normals 0, 1, and 2,
   with site 3 empty. This uses three bosons and represents the chosen
   missing-face product preparation; it is not a projection of the FL state.

The initial mean squared total spins are, respectively, $0$, $2$, and
$7/4$. The single-face state is entirely in $J=1$. The missing-face product
has $P(J=1/2)=2/3$ and $P(J=3/2)=1/3$, with zero singlet weight. Its mean
spin vector is minus one half of the omitted face normal, with magnitude
$1/2$; the separate $J^2$ readout quantifies the full spin-sector mixture.

Across both graphs, the closed seed remains in $J=0$, the single face remains
in $J=1$, and the missing-face spin-sector weights stay fixed during the
unitary evolution. Hopping redistributes face occupation in the open cases.
At $t_{\rm evol}=1$, the missing-face mean boson counts are approximately
$(0.7633,0.7633,0.7633,0.7101)$ on the complete graph and
$(0.6486,0.7792,0.6840,0.8882)$ on the ring. The initially empty fourth site
is populated in both cases. Full trajectories for all three states and
controls are saved in the JSON.

These are small-sector diagnostics, not a calibrated geometric evolution.
No volume is assigned to a non-singlet state. The missing-face initial state
is an explicitly chosen product of the three retained coherent faces; tracing
or annihilating a face in the four-face FL state would define other states.

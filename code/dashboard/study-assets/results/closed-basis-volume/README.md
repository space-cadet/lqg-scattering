# Complete four-face closed-state volume calculation

Calculated on 2026-10-08. Completed areas are $K=2,\ldots,12$, comprising 10,549 orthonormal basis states. The extension was stopped at the user's request during $K=13$ archive verification. No $K=13$ result is included.

## States and conventions

Here $K=\sum_i j_i=N_{\mathrm{bosons}}/2$ is total linear area, and $J=0$ is resultant angular momentum. Faces are labelled and zero-spin faces are allowed. A basis state couples faces $(1,2)$ and $(3,4)$ to the same intermediate spin $k$, then couples the pair to a singlet:

$$
|j_1,j_2,j_3,j_4;k\rangle
=\frac{1}{\sqrt{2k+1}}\sum_{m=-k}^{k}(-1)^{k-m}
|(j_1j_2)k,m\rangle|(j_3j_4)k,-m\rangle.
$$

Clebsch–Gordan coefficients use the Condon–Shortley convention, evaluated with exact half-integer inputs before conversion to floating point. Each CSV row is one basis state, not a face-spin assignment or an arbitrary superposition. These are recoupling states, not FL coherent states or, in general, volume eigenstates.

Raw positive RS/AL operators use $(\gamma\hbar)^{3/2}$ with $\gamma=0.2375$, $\hbar=1$, and AL signs $(+,-,+,-)$ for triples $(012,013,023,123)$ in zero-based face indexing. The fixed geometric factors are $\sqrt2/12$ for RS and $\sqrt2/6$ for AL. Absolute physical normalization remains unresolved. This is a one-copy, zero-temperature calculation.

## Results

| $K$ | Complete basis dimension | Basis states with positive volume expectation |
|---:|---:|---:|
| 2 | 20 | 2 |
| 3 | 50 | 12 |
| 4 | 105 | 39 |
| 5 | 196 | 94 |
| 6 | 336 | 190 |
| 7 | 540 | 342 |
| 8 | 825 | 567 |
| 9 | 1210 | 884 |
| 10 | 1716 | 1314 |
| 11 | 2366 | 1880 |
| 12 | 3185 | 2607 |

The positive-expectation count uses the declared $2\times10^{-10}$ absolute tolerance. It is not a count of nonzero volume eigenvalues: a basis vector can overlap both the volume kernel and its nonzero eigenspaces. At $K=2$, both four-active-face states have raw RS mean $0.304653190236$ and AL mean $0.152326595118$, with zero intrinsic spread; the other 18 states have zero volume. At $K=4$ and beyond, some recoupling states have nonzero intrinsic volume spread.

The CSVs report $\langle V\rangle$, $\langle V^2\rangle$, and $\sigma_V$ for each prescription. The full operator matrices retain information needed for arbitrary superpositions, including off-diagonal entries. Metadata includes each block's volume eigenvalues and its basis ordering.

Equal-weight fixed-area means are traces divided by the full closed-space dimension. They differ from the existing shape-selected FL curves. Restricting to four active faces defines another ensemble; the plotting script displays both. Neither is a canonical-temperature calculation.

## Compressed storage

For each area there are three files:

- `states_kK.csv`: readable state labels and volume moments.
- `metadata_kK.json`: ordered face-spin blocks, intermediate spins, spectra, checks, timing, archive size and SHA-256 hash.
- `operators_kK.npz`: losslessly compressed numerical arrays, loadable without pickle.

The NPZ stores all six scalar products $\mathbf J_i\cdot\mathbf J_j$, all four signed triple grasps, RS/AL volume matrices and their squares, and their eigensystems in the singlet basis. Blocks are flattened into packed arrays with offsets and shapes, avoiding a large global zero-filled matrix and the ZIP overhead of many tiny files. The magnetic occupation basis and its transformation to the singlet basis are also saved, with the transformation in CSR form.

Individual vector flux operators take a singlet out of the singlet space, so these archives do not misrepresent their zero singlet projections as full flux matrices. The saved full singlet blocks are the appropriate reusable matrices for the gauge-invariant volume calculation. Sparse storage of volume matrices is unnecessary at these sizes and would not generally preserve sparsity after taking spectral square roots. The largest singlet block at $K=12$ is $7\times7$; that area's complete archive is about 2.5 MB.

Load one complete block as follows, with `code/python` on the Python import path:

```python
import json
import numpy as np
from closed_basis_volume import load_block

metadata = json.load(open("results/closed-basis-volume/metadata_k4.json"))
with np.load("results/closed-basis-volume/operators_k4.npz", allow_pickle=False) as archive:
    volume = load_block(archive, 0, "v_rs")
    pair_spins = load_block(archive, 0, "twice_k") / 2
    # Block 0 uses metadata["blocks"][0]["twice_spins"] / 2 as its face spins.
```

For repeated access, first materialize the NPZ arrays in a dictionary to avoid repeatedly decompressing them. `load_block` accepts that dictionary too. State index starts at one in CSV; block index starts at zero. Occupation rows specify $(n_{a_1},n_{b_1},\ldots,n_{a_4},n_{b_4})$ and are explicitly stored rather than inferred from a sorting rule.

## Verification and provenance

Every block passes orthogonality, total raising/lowering closure, Casimir, pair-recoupling, Hermiticity, invariant-subspace, and four-valent triple-closure checks. An independently assembled sparse local-spin epsilon contraction checks the magnetic-space $q_{012}$ for every unordered face-spin pattern at every completed area. Through $K=4$, additional full dense local-spin and existing Schwinger-oscillator triple matrices agree, and spectral roots taken in the magnetic space agree with roots in the singlet space. Permutations share the canonical magnetic matrices but have separately constructed coupling bases and checks.

The declared absolute tolerance is $2\times10^{-10}$. The largest recorded residual across completed areas is below $8\times10^{-14}$. Spectral square roots use the repo's $64\epsilon_{\mathrm{mach}}\max(1,\max|\lambda|)$ zero-mode cutoff. Variance roundoff within the corresponding floating-point threshold is recorded as zero. Compressed archives pass lossless reload checks; [summary.json](summary.json) records conventions, versions, coverage, and checks. This does not establish a classical-limit or physical-normalization result.

Reproduce using [closed_basis_volume.py](../../code/python/closed_basis_volume.py), with NumPy, SciPy, and SymPy available:

```bash
python code/python/closed_basis_volume.py --k-min 2 --k-max 12
python code/python/plot_closed_basis_volume.py
```

Plots: [fixed-area ensemble means](../../figures/closed-basis-volume/fixed_area_ensemble_volume.png), [PDF](../../figures/closed-basis-volume/fixed_area_ensemble_volume.pdf), [individual states at K = 2, 3, 4](../../figures/closed-basis-volume/basis_state_volumes_k2_k4.png), [PDF](../../figures/closed-basis-volume/basis_state_volumes_k2_k4.pdf). The [plot summary](../../figures/closed-basis-volume/plot_summary.json) records source hashes and equal-weight ensemble statistics. The ensemble standard deviation uses the average second moment minus the square of the ensemble mean; it is not an average of individual-state standard deviations.

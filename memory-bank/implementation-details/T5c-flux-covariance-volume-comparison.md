# T5c: Flux-Covariance Reconstruction and Volume Comparison

**Status:** OPEN — the saved calculation is an exploratory pilot, not a
completed classical-limit analysis.
**Task:** T5c, under [the T5 numerical-studies program](./volume-positivity-studies.md).
**Shared notation:** [volume numerical preliminaries](./volume-numerical-preliminaries.md).

## Aim

For one specified quantum state family, construct a candidate classical
tetrahedron from that state's flux correlations, then compare its volume
with explicitly named quantum observables calculated from the same state.

This task does not assume that the reconstruction is already the correct
state-to-geometry map. It must check whether the correlation geometry
recovers the input shape when one is known, and whether that relationship
persists as the state label grows. A finite numerical match alone would not
establish a general classical limit.

## State family and labels

The current pilot uses the $N=4$ Freidel–Livine fixed-area state from
[Freidel and Livine, arXiv:1005.2090](https://arxiv.org/abs/1005.2090):

$$
|J,z\rangle\propto(F_z^\dagger)^J|0\rangle,\qquad
F_z^\dagger=\sum_{i<j}[z_j|z_i\rangle
\left(a_i^\dagger b_j^\dagger-a_j^\dagger b_i^\dagger\right).
$$

The spinor bracket is
$[z_j|z_i\rangle=z_{j,0}z_{i,1}-z_{j,1}z_{i,0}$. The implementation
normalizes the resulting Fock state. $J$ is the power of the pair creator;
the total boson number is $K_{\mathrm{Fock}}=2J$. Each pair adds two
bosons, and $K_{\mathrm{Fock}}$ is not an individual face spin. See the
[shared preliminaries](./volume-numerical-preliminaries.md) for the
Schwinger generators, normalization, and distinction between FL and FS.

The original full-observable pilot evaluates $J=1,2,3$ on two
equal-face-area tetrahedron shapes. A selected-shape follow-up now computes
the covariance geometry for $J=1,\ldots,6$ on five shapes, and recomputes
all four named quantum observables for $J=1,2,3$. This remains a short finite
range, not a large-$J$ limit.

The current T5c driver has no separate $\xi$ parameter: its state inputs are
$J$ and the four spinors $z_i$. If another state family is later labeled by
$\xi$, that parameter needs a definition in that family's specification;
it is not interchangeable with $x$, $\varphi$, a face spin, or
$K_{\mathrm{Fock}}$.

## Shape labels $x$ and $\varphi$

Let $x\in(0,1)$ and $\varphi\in[0,2\pi)$, and set
$u=\sqrt{1-x^2}$. The four unit face normals are

$$
\begin{aligned}
n_0&=(u,0,x), & n_1&=(-u,0,x),\\
n_2&=(u\cos\varphi,u\sin\varphi,-x), &
n_3&=(-u\cos\varphi,-u\sin\varphi,-x).
\end{aligned}
$$

They close: $\sum_i n_i=0$. The opposite-pair sums are
$n_0+n_1=(0,0,2x)$ and $n_2+n_3=(0,0,-2x)$.

- $x$ is half the length of the first pair sum,
  $x=|n_0+n_1|/2$. It sets the common component of each pair along the
  diagonal axis.
- $\varphi$ is the azimuthal bend of the second pair around that axis,
  measured from the fixed $x$-axis in the transverse plane. It changes
  relative face directions while preserving closure. It is a coordinate of
  this family, not by definition a tetrahedral dihedral angle.
- $u$ is the transverse component required by unit-normal length.

The regular tetrahedron occurs at $x=1/\sqrt{3}$ and
$\varphi=\pi/2$. The nondegenerate domain excludes $x=0$, $x=1$, and
$\sin\varphi=0$; these boundary shapes must be approached separately if
their limits are studied.

For normalized spinors whose Bloch vectors are $n_i$, the code uses these
canonical representatives:

$$
\begin{aligned}
z_0&=\left(\sqrt{\frac{1+x}{2}},\sqrt{\frac{1-x}{2}}\right),&
z_1&=\left(\sqrt{\frac{1+x}{2}},-\sqrt{\frac{1-x}{2}}\right),\\
z_2&=\left(\sqrt{\frac{1-x}{2}},e^{i\varphi}\sqrt{\frac{1+x}{2}}\right),&
z_3&=\left(\sqrt{\frac{1-x}{2}},-e^{i\varphi}\sqrt{\frac{1+x}{2}}\right).
\end{aligned}
$$

Each is unit normalized and obeys $n_i=z_i^\dagger\vec\sigma z_i$.
The spinor phase convention is fixed here to make the state construction
reproducible.

The related T1a shape scan also checks the four spinor rays using the cross ratio

$$
\lambda=\left(\frac{t^2-e^{i\varphi}}{t^2+e^{i\varphi}}\right)^2,
\qquad t^2=\frac{1-x}{1+x}.
$$

This acts as a coordinate-consistency check between the shape labels and
the spinor construction. It does not identify the Thurston four-marked-sphere
data with LQG flux geometry.

## Correlation geometry

For the normalized state, calculate the real symmetric $4\times4$ matrix

$$
G_{ij}=\langle\vec J_i\cdot\vec J_j\rangle.
$$

Use $G_{ii}=\langle j_i(j_i+1)\rangle$ for the diagonal, including all
occupation components in the state. The FL state is gauge-invariant, so its
one-point fluxes vanish. The nonzero information used here is in $G$, not
inverting those one-point means into normals.

Before reconstruction, check:

1. symmetry and positive semidefiniteness of $G$ within a stated tolerance;
2. closure, $G\mathbf 1\simeq0$;
3. exactly one closure mode and three nondegenerate spatial modes, up to
   numerical tolerance;
4. successful reconstruction of all four face-vector inner products.

If these checks pass, factor $G=XX^T$. The rows $X_i\in\mathbb R^3$ are
closed candidate face-area vectors in spin units. They are defined only up
to an orthogonal transformation. Their lengths
$\sqrt{G_{ii}}$ are RMS flux lengths, not one-point flux magnitudes.
This rank-three covariance factorization is a candidate map to classical
geometry; the required checks do not establish that it is a general
twisted-geometry reconstruction.

### Tetrahedron volume from four area vectors

The pilot selects rows 1, 2, and 3 of the factored matrix as
$F_1,F_2,F_3$. The shared [face-vector dual construction](./volume-numerical-preliminaries.md#classical-tetrahedron-from-closed-face-area-vectors)
gives the vertices and candidate volume $V_{\mathrm{cl}}^{(J)}$. The
implementation recomputes its four outward area vectors and records the
maximum absolute error in their Gram matrix against $G$. The displayed
project-unit value is
$(\gamma\hbar)^{3/2}V_{\mathrm{cl}}^{(J)}$, with $\gamma=0.2375$ and
$\hbar=1$ in the pilot.

## Quantum quantities to compare

For the same normalized state, triple $(0,1,2)$, and declared conventions,
record separately:

1. $q_{012}=\langle\hat q_{012}\rangle$, the signed triple-grasp mean;
2. $V_{\mathrm{proxy}}=(\gamma\hbar)^{3/2}\sqrt{|q_{012}|}$;
3. $\langle\hat V_{\mathrm{RS}}\rangle$, the expectation of the positive
   Rovelli–Smolin vertex operator;
4. $\langle\hat V_{\mathrm{AL}}\rangle$, the expectation of the positive
   Ashtekar–Lewandowski vertex operator, with its embedding signs stated.

The RS and AL definitions and the numerical zero-mode cutoff are in the
[shared preliminaries](./volume-numerical-preliminaries.md) and
[volume-operator note](./volume-operator.md). The pilot uses lexicographic
triple signs $(+1,-1,+1,-1)$ for AL. These signs are a fixed comparison
choice; no graph embedding has been justified for the
covariance-reconstructed tetrahedron.

Do not compare $V_{\mathrm{cl}}$ only with $V_{\mathrm{proxy}}$ and call
that a positive-volume test. A zero $q_{012}$ can coexist with nonzero
positive RS/AL expectations.

## Current pilot and what it shows

The saved pilot is [t5c_covariance_probe.py](../../t5c_covariance_probe.py);
its complete machine-readable output is
[t5c_covariance_probe_results.json](../../t5c_covariance_probe_results.json).
It tests the regular shape
$(x,\varphi)=(1/\sqrt3,\pi/2)$ and one bent shape
$(x,\varphi)=(1/2,\pi/3)$ at $J=1,2,3$. All values below are in project
units.

| Shape | $J$ | $K_{\mathrm{Fock}}$ | $V_{\mathrm{cl}}$ | $V_{\mathrm{proxy}}$ | $\langle V_{\mathrm{RS}}\rangle$ | $\langle V_{\mathrm{AL}}\rangle$ | Normalized Gram error |
|---|---:|---:|---:|---:|---:|---:|---:|
| Regular | 1 | 2 | 0.022940436 | 0 | 0 | 0 | $3.89\times10^{-16}$ |
| Regular | 2 | 4 | 0.043309609 | 0.031093536 | 0.050775532 | 0.025387766 | $3.89\times10^{-16}$ |
| Regular | 3 | 6 | 0.064885352 | 0.062187072 | 0.162213379 | 0.081106690 | $4.44\times10^{-16}$ |
| Bent | 1 | 2 | 0.022815949 | 0 | 0 | 0 | 0.3438 |
| Bent | 2 | 4 | 0.042837320 | 0.028561237 | 0.053849831 | 0.026924916 | 0.2946 |
| Bent | 3 | 6 | 0.063834292 | 0.057122473 | 0.168411229 | 0.084205615 | 0.2578 |

The normalized Gram error is the maximum absolute difference between
$G_{ij}/\sqrt{G_{ii}G_{jj}}$ and the input normal Gram matrix
$n_i\cdot n_j$. Closure and reconstructed-Gram residuals are at
floating-point scale in all six cases. The regular pilot recovers the input
normal Gram matrix to floating-point accuracy. The bent pilot does not:
its errors are about 0.26–0.34. Thus the current covariance map reproduces
the regular pilot shape but has not been shown to preserve general shape.

At $J=1$, the covariance-derived candidate has positive classical volume
while the signed proxy and tested positive quantum expectations are zero.
At $J=2,3$, the four volume values differ. These are six exploratory
comparisons with a fixed AL sign choice, not evidence for a large-$J$ law,
an optimized reconstruction, or a general classical limit.

## Selected-shape recovery follow-up (2026-10-03)

The follow-up driver is
[t5c_shape_recovery_scan.py](../../t5c_shape_recovery_scan.py), with the full
covariance matrices, spectra, reconstructed Gram residuals, and volume
comparisons in
[t5c_shape_recovery_results.json](../../t5c_shape_recovery_results.json).
It samples five interior labels from the same closed, equal-face-area family:
the regular shape, two mirror-related bends at $x=0.5$,
$\varphi=60^\circ$ and $120^\circ$, one shape at $x=0.65$,
$\varphi=60^\circ$, and a low-$x$ shape at $x=0.2$,
$\varphi=90^\circ$. It also samples three finite approaches to each of
$x\to0$, $x\to1$, and $\varphi\to0$, for 14 shapes total. The covariance
calculation covers $J=1,\ldots,6$; positive RS/AL and signed-mean comparisons
are recomputed for the five interior shapes at $J=1,2,3$.

The table reports
$E_J=\max_{ij}|G_{ij}/\sqrt{G_{ii}G_{jj}}-n_i\cdot n_j|$:

| Shape | $E_1$ | $E_2$ | $E_3$ | $E_4$ | $E_5$ | $E_6$ |
|---|---:|---:|---:|---:|---:|---:|
| Regular | $<2\times10^{-15}$ | $<2\times10^{-15}$ | $<2\times10^{-15}$ | $<2\times10^{-15}$ | $<2\times10^{-15}$ | $<2\times10^{-15}$ |
| $x=0.5$, $60^\circ$ | 0.343750 | 0.294643 | 0.257813 | 0.229167 | 0.206250 | 0.187500 |
| $x=0.5$, $120^\circ$ | 0.343750 | 0.294643 | 0.257813 | 0.229167 | 0.206250 | 0.187500 |
| $x=0.65$, $60^\circ$ | 0.283438 | 0.242946 | 0.212578 | 0.188958 | 0.170063 | 0.154602 |
| $x=0.2$, $90^\circ$ | 0.440000 | 0.377143 | 0.330000 | 0.293333 | 0.264000 | 0.240000 |

The nine boundary-approach labels have the following observed error ranges;
each range runs from the farthest to the closest sampled point to that
boundary:

| Approach | $E_1$ range | $E_3$ range | $E_6$ range |
|---|---:|---:|---:|
| $x\to0$ at $\varphi=90^\circ$ | 0.365000–0.491562 | 0.273750–0.368672 | 0.199091–0.268125 |
| $x\to1$ at $\varphi=90^\circ$ | 0.235000–0.783438 | 0.176250–0.587578 | 0.128182–0.427330 |
| $\varphi\to0$ at $x=1/\sqrt3$ | 0.438791–0.496099 | 0.329093–0.372074 | 0.239341–0.270599 |

For every one of the 14 sampled shapes, the **whole normalized Gram matrix**
follows
$H_J=H_{\mathrm{input}}+\frac{6}{J+5}(H_1-H_{\mathrm{input}})$
through $J=6$, with maximum matrix residual $4.4\times10^{-15}$. Here
$H_J=G_{ij}/\sqrt{G_{ii}G_{jj}}$ and $H_{\mathrm{input}}=n_i\cdot n_j$.
This is a finite-sample identity to numerical precision, not yet a theorem
or a general-limit result. The regular-shape errors remain at floating-point
scale, while nonregular errors decrease with $J$. Across all 84 cases, the
maximum closure residual is $2.0\times10^{-14}$ and the maximum reconstructed
face-Gram residual is $1.6\times10^{-14}$.

The $J=1,2,3$ quantum volume values on the original regular and bent cases
reproduce the saved pilot to floating-point precision. The three added
interior shapes provide more shape dependence for all four comparisons,
with the same fixed AL signs $(+1,-1,+1,-1)$. The boundary-approach cases
are covariance-only. No AL embedding has been established, and no
positive-volume spectral calculation was attempted at $J=4,5,6$. At $J=6$
the state occupies 5,208 basis components in an ambient Fock space of
dimension 125,970.

To reach this ambient dimension without scanning every possible oscillator
tuple, the Python Fock-space constructor now generates only bounded
occupations in the same lexicographic order as before. The state itself still
has the exact total boson number $K_{\mathrm{Fock}}=2J$.

## Dashboard previews and reusable thumbnails (2026-10-03)

The T5c chart exposes each selectable shape/area point through hover, click,
keyboard focus, and Shape/$J$ selectors. Its preview places the input
tetrahedron beside the covariance-reconstructed candidate. Both are scaled
for display; the candidate is aligned for visual comparison, so the preview
does not encode an absolute orientation.

`dashboard/tetrahedron_thumbnails.py` generates reusable static SVG assets:
24 input-shape thumbnails and 84 covariance candidates (14 shape labels at
$J=1,\ldots,6$). The T1a saved shape figure reuses the input thumbnails.
Parameterized tetrahedron displays should show the corresponding shape
thumbnail, and generated assets should be reused across displays. The source
assets are under `dashboard/figures/t5c-input/` and
`dashboard/figures/t5c-covariance/`.

The updated dashboard, including the refreshed T1a shape SVG, is deployed at
website commit `9c6670c190e813470975f18037c1ed4a6ecea8bc` (workflow
`37125090987`). This records the presentation and deployment; it does not
change T5c's numerical status.

## Work required for a T5c result

- Define and justify the state-to-classical-geometry map, or explicitly
  scope T5c to testing the covariance candidate above.
- Retain the pilot and selected-shape checks for closure, rank, positivity,
  and reconstructed face Gram matrix. Expand beyond the five selected
  labels, include controlled approaches to degenerate boundaries, and show
  which input shape the covariance map recovers.
- Extend positive RS/AL comparisons beyond $J=1,2,3$ where feasible, with
  resource limits recorded. The covariance-only scan already reaches $J=6$;
  distinguish those geometry results from positive-volume spectra.
- Justify the graph embedding and AL orientation signs, or report AL only
  as a convention-dependent comparison.
- Keep project normalization separate from physical regularization
  prefactors.
- Compare all four named quantities with uncertainties or convergence
  evidence before making any classical-limit claim.

## Related documentation

- [Shared volume preliminaries](./volume-numerical-preliminaries.md)
- [T5 program and study dependencies](./volume-positivity-studies.md)
- [T5/T5c task registry entry](../tasks.md#t5-volume-positivity-numerical-studies)
- [Implemented volume operators and limits](./volume-operator.md)
- [T6 Minkowski reconstruction](./T6-minkowski-polyhedron.md)
- [Fock-space and singlet-pair conventions](./fock-space-construction.md)
- [Grassmannian and coherent-state coordinates](./grassmannian-embedding.md)
- [Numerical verification protocol](./verification-protocol.md)
- [Red-team audit and claim limits](./red-team-audit.md)
- [Shape-scan run log](../../fl_volume_shape_scan_log.md)
- [Selected-shape covariance results](../../t5c_shape_recovery_results.json)
- [Selected-shape covariance driver](../../t5c_shape_recovery_scan.py)
- [T1a task record](../tasks/T1a.md) and [T3c task record](../tasks/T3c.md)

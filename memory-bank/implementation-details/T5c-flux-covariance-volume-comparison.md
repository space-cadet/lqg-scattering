# T5c: Flux-Covariance Reconstruction and Volume Comparison
*Last Updated: 2026-10-05 12:24:39 IST*

**Status:** OPEN — the saved calculation is an exploratory pilot, not a
completed classical-limit analysis.
**Task:** T5c, under [the T5 numerical-studies program](./volume-positivity-studies.md).
**Shared notation:** [volume numerical preliminaries](./volume-numerical-preliminaries.md).

## Aim

Start from a specified closed classical tetrahedron, encode its face areas
and normals in one named quantum state family, and compare its classical
volume with positive volume observables of that same state. Separately check
whether flux correlations recover the input shape as the state label grows.
Do not treat covariance reconstruction as the primary volume target or
assume it is already the correct state-to-geometry map. A finite numerical
match alone would not establish a general classical limit.

## Central numerical question

For a closed tetrahedron represented by an FL state, do the positive RS and
AL volume expectations approach the tetrahedron's classical volume as $J$
increases, using one fixed normalization per operator across all shapes?
How does the discrepancy depend on shape, unequal face-area ratios, and
approach to a degenerate tetrahedron?

Use the input face data as the primary classical reference. For area
fractions $a_i=A_i/\sum_k A_k$ and unit normals $n_i$ satisfying
$\sum_i a_i n_i=0$, construct the FL labels
$z_i=\sqrt{2a_i}\,\chi_i$, where $\chi_i$ is a unit spinor with Bloch
vector $n_i$. The associated classical input face vectors at total
spin-area label $J$ are $J a_i n_i$, and their tetrahedron volume scales as
$J^{3/2}$. They are the classical reference encoded by the spinor labels,
not the quantum means $\langle\vec J_i\rangle$: each individual vector
mean vanishes in the gauge-invariant FL intertwiner. Its area means are
$\langle j_i\rangle=Ja_i$, while its shape information is in inter-face
correlations. The covariance-reconstructed tetrahedron remains a separate
geometry diagnostic; it should not replace the input tetrahedron as the
primary volume target.

## Fixed geometric normalization

For closed tetrahedral face vectors $F_i$, let
$q=\det(F_1,F_2,F_3)$ for three faces meeting at a vertex. The Euclidean
tetrahedron volume is

$$
V_{\mathrm{cl}}=\sqrt{\frac{2}{9}|q|}.
$$

Closure gives the classical triple pattern
$q_{012}=-q_{013}=q_{023}=-q_{123}$. The corresponding classical symbols
of the raw RS sum and the AL root with lexicographic signs $(+,-,+,-)$ are
$4\sqrt{|q|}$ and $2\sqrt{|q|}$. Therefore compare to the classical volume
using the fixed factors

$$
\kappa_{\mathrm{RS}}=\frac{\sqrt{2}}{12},\qquad
\kappa_{\mathrm{AL}}=\frac{\sqrt{2}}{6}.
$$

They multiply the repository's project-normalized expectations and are held
fixed for every shape and $J$. In the tested gauge-invariant four-valent
states, the four quantum triple operators obey the same signed closure
pattern to numerical residual below $3.3\times10^{-16}$, so the two
geometry-matched RS and AL curves coincide. Their agreement is expected
from this relation and is not an independent confirmation. This is the
geometric conversion for the stated four-valent convention; it does not
select the remaining physical regularization or Planck-unit prefactors.
Other AL tangent signs require a separate conversion.

For each operator $X\in\{\mathrm{RS},\mathrm{AL}\}$ and each
nondegenerate shape, report the classical volume at unit total area and
$\langle\hat V_X\rangle/J^{3/2}$, along with a discrepancy or ratio that
uses a normalization fixed once for that operator. State the project units
and any physical conversion separately. Fix the AL orientation signs from
the declared graph embedding and keep that embedding fixed across the shape
family. Near zero classical volume, report absolute differences instead of
ratios. Record $\mathrm{Var}(\hat V_X)$ where the calculation permits it.

For a controlled degenerate limit, parameterize a nondegenerate path by
$\delta\to0$ and evaluate both orders: first $J\to\infty$ at fixed
$\delta$, then $\delta\to0$; and first $\delta\to0$ at fixed $J$, then
$J\to\infty$. Record the finite-$J$ quantum volume and its variance near
the boundary.

This is the T5c numerical extension, not a new task or a change of state
family. The weighted-spinor pilot below verifies the closure matrix and
area means for selected closed inputs; its correlation matrix also closes.
For the unequal starter, however, normalized pair correlations differ from
the input normal dot products by up to $0.0584$ at $J=7$, so full finite-$J$
shape recovery remains open.

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

The original T5c and T1a drivers build each spinor from a unit face normal,
so those saved scans cover equal face-area ratios. The new pilot verifies
that weighted inputs $z_i=\sqrt{2a_i}\,\chi_i$ encode selected unequal
closed tetrahedra with the requested area means; it does not yet cover the
full unequal-area shape space. Do not read the normals as individual
quantum vector means: those means vanish by gauge invariance, and angular
shape is tested through $\langle\vec J_i\cdot\vec J_j\rangle$.

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

## Scale-free tetrahedron shape coordinates

At fixed face-area fractions, the closed four-face tetrahedron shape has
two degrees of freedom after common rotations are removed. One convenient
pair is $d=|F_0+F_1|$ at unit total area and the bend angle between the
$F_0,F_1$ and $F_2,F_3$ pairs. `t5c_input_geometry_scan.py` records the
complex cross-ratio of the four vertices projected from the unit
circumsphere. The unequal-area driver also scans $(d,\varphi)$ and records
the cross-ratio of the face-normal spinor rays.

For a fixed Euclidean similarity shape, volume is a scale factor:
$V=R_{\mathrm{circ}}^3 V_{R=1}$, or
$V=A_{\mathrm{tot}}^{3/2}V_{A=1}$. T5c fixes $A_{\mathrm{tot}}=1$ for the
input fractions and scales the comparison by $J^{3/2}$. A vertex
cross-ratio by itself does not retain all Euclidean chord lengths, so the
input records also include the six chord lengths after setting the
circumsphere radius to one.

## Initial input-geometry results (2026-10-05)

The driver starts from explicit tetrahedron vertices, computes each
outward triangle area vector, and uses its unit direction as the face
normal. It rescales the four areas to total area one, forms
$z_i=\sqrt{2a_i}\,\chi_i$, and checks the weighted closure matrix and the
FL means $\langle j_i\rangle=Ja_i$. The classical target comes from those
same face vectors. Full cross-ratios, chord lengths, covariance matrices,
variances, and per-$J$ results are saved in
`t5c_input_geometry_results.json`.

Here $V_{\mathrm{cl,proj}}=(\gamma\hbar)^{3/2}V_{\mathrm{cl}}$ is the
unit-total-area classical target in the same project units as the quantum
operator; both sides therefore carry the same $\gamma^{3/2}$ factor.

| Input shape | Face-area fractions | Vertex cross-ratio on unit circumsphere | $\kappa_X\langle V_X\rangle_{\mathrm{proj}}/(J^{3/2}V_{\mathrm{cl,proj}})$ at $J=2,5,7$ |
|---|---|---|---|
| Regular | $(0.25,0.25,0.25,0.25)$ | $0.5000-0.8660i$ | $0.3536, 0.8788, 0.9529$ |
| Unequal skew | $(0.3155,0.1458,0.3000,0.2388)$ | $0.3378+0.7796i$ | $0.3168, 0.8073, 0.9043$ |

The RS and AL ratios coincide to numerical precision under the stated AL
signs and geometric factors. At $J=7$, the normalized geometry-matched
standard deviations are $0.00172$ for the regular case and $0.00226$ for
the unequal case, in project units divided by $J^{3/2}$. The weighted
closure-matrix residual is below $4.1\times10^{-16}$, and the largest error
in $\langle j_i\rangle=Ja_i$ is below $6.2\times10^{-14}$ through $J=7$.
For the unequal case, the covariance Gram matrix closes to $4.4\times10^{-15}$
at $J=7$, but its normalized pairwise-correlation error is still $0.0584$;
its RMS covariance area fractions also differ from the input fractions.

The nine-point unequal-area grid in `t5c_weighted_shape_scan.py` fixes
$(a_0,a_1,a_2,a_3)=(0.32,0.18,0.30,0.20)$ and samples three interior
diagonals and three bend angles. The geometry-matched volume ratio ranges
from $0.325$ to $0.529$ at $J=2$ and from $0.726$ to $1.020$ at $J=4$.
Face closure is exact by construction; the largest weighted spinor closure
error is $2.8\times10^{-16}$ and the largest mean-spin error at $J=4$ is
$3.8\times10^{-15}$. The grid shows finite-$J$ shape dependence, not a
shape-uniform limit. Four selected grid points at $J=6$ have ratios from
$0.881$ to $1.034$.

The boundary driver `t5c_degenerate_limits_scan.py` holds
$x=1/\sqrt{3}$ and takes $\varphi\to0$, where the face normals become
coplanar. At the exact boundary, the classical volume is zero while the
geometry-matched $\langle V\rangle/J^{3/2}$ values at $J=2,4,6,7$ are
$0.00247,0.00461,0.00418,0.00398$; the corresponding standard deviations
are $0.00502,0.00350,0.00282,0.00261$. At $\varphi=0.05$, the classical
project volume is $0.001338$, while the normalized quantum mean is nearly
the boundary value; its ratio to the classical volume is $1.84$ at $J=2$
and $2.98$ at $J=7$. These finite samples do not establish either
iterated limit. Full records are in `t5c_degenerate_limits_results.json`.

## Correlation geometry

For the normalized state, calculate the real symmetric $4\times4$ matrix

$$
G_{ij}=\langle\vec J_i\cdot\vec J_j\rangle.
$$

The normalized covariance pattern is the pairwise angular-correlation
matrix

$$
C_{ij}=\frac{G_{ij}}{\sqrt{G_{ii}G_{jj}}}.
$$

Compare it with the input normal Gram matrix $N_{ij}=n_i\cdot n_j$.
This removes the RMS flux lengths and tests angular shape; it is not a
volume observable and does not retain the overall scale. In the weighted
unequal starter, $\max_{ij}|C_{ij}-N_{ij}|=0.0584$ at $J=7$.

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

For every one of the 14 sampled equal-area shapes, the **whole normalized
Gram matrix** follows
$H_J=H_{\mathrm{input}}+\frac{6}{J+5}(H_1-H_{\mathrm{input}})$
through $J=6$, with maximum matrix residual $4.4\times10^{-15}$. Here
$H_{J,ij}=G_{ij}/\sqrt{G_{ii}G_{jj}}$ and
$H_{\mathrm{input},ij}=c_{ij}=n_i\cdot n_j$. This relation is already
implied by the exact equal-area FL correlation formula in
[Freidel and Livine, Eq. (72)](https://arxiv.org/html/1005.2090#S3.SS5): for
$i\ne j$,

$$
G_{ij}=\frac{J\big((2J+1)c_{ij}-3\big)}{32},\qquad
G_{ii}=\frac{J(J+5)}{16},\qquad
H_{J,ij}=\frac{(2J+1)c_{ij}-3}{2(J+5)}.
$$

Rearranging gives the affine relation above. Thus the recorded scan is a
numerical check of the known equal-area formula, which predicts an
$O(J^{-1})$ recovery of the input normal Gram matrix. It is not evidence for
a new covariance law, a volume limit, or an unequal-area result. Across all
84 cases, the maximum closure residual is $2.0\times10^{-14}$ and the
maximum reconstructed face-Gram residual is $1.6\times10^{-14}$.

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

### Weighted input-volume dashboard extension (2026-10-05)

The local dashboard now loads `dashboard/t5c-input-volume.json`, assembled
from the four scan result files by
`dashboard/build_t5c_input_volume_data.py`. The helper plots in
`dashboard/t5c-input-volume.js` add four views:

- Regular and unequal-skew mean/classical ratios and intrinsic spread ratios
  over $J=1,\ldots,7$.
- A tile grid for the nine unequal-area shapes at $J=2,4$, with four selected
  points at $J=6$; empty tiles mark uncomputed cases.
- Separate complex cross-ratio plots for the circumsphere vertices and the
  face-normal spinors. The full result bundle retains six normalized vertex
  chord lengths because a cross-ratio alone is not a Euclidean shape metric.
- Positive-volume mean, classical target, and intrinsic spread along the
  sampled flat path $\varphi=0,0.05,\pi/2$.

The page also reports weighted-spinor closure and scalar area-mean residuals.
For the tested four-valent signs, the calibrated RS and AL curves coincide by
closure and are not independent evidence. The flat-path points are discrete
samples, not a limit fit; neither order of the flat-shape and large-$J$ limits
is established. This extension was rendered and visually checked from the
local dashboard on 2026-10-05; it has not been deployed. It changes no T5c
numerical-status claim.

## Work required for a T5c result

- Use the same closed input area vectors to build weighted FL spinors and
  the classical reference tetrahedron. Verify closure, $\langle j_i\rangle$
  against the requested area fractions, and the classical volume before
  comparing quantum observables. The regular and unequal-skew starters pass;
  expand to a broader area and shape family. Retain covariance reconstruction
  as a separate geometry diagnostic.
- Compare regular and distorted equal-area shapes, then add genuinely
  unequal positive area fractions. Cover multiple nondegenerate shapes and
  record the normalized RS/AL expectations, absolute discrepancy, volume
  variance where feasible, and convergence as $J$ grows.
- Use the fixed geometric factors derived above across all shapes. Keep
  project units separate from physical regularization factors; choose and
  justify the latter before making physical-volume claims.
- Fix AL signs from a stated graph embedding, or label AL values as
  convention-dependent. The face normals alone do not determine these signs.
- Evaluate positive-volume spectra along controlled degenerate paths and
  compare the two limit orders. Do not infer positive-volume behavior from
  the signed-mean proxy or from the covariance-only boundary scan.
- Treat the known equal-area FL covariance identity as an analytic
  cross-check. Do not generalize it to weighted unequal-area labels without
  deriving or validating that case.
- Extend the new weighted positive-volume calculations beyond $J=7$ where
  feasible, report active-block limits, and add independent numerical checks
  for the new shape families.

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
- [Input-geometry weighted scan](../../t5c_input_geometry_scan.py) and [results](../../t5c_input_geometry_results.json)
- [Unequal-area shape scan](../../t5c_weighted_shape_scan.py) and [results](../../t5c_weighted_shape_results.json), with [selected $J=6$ points](../../t5c_weighted_shape_j6_results.json)
- [Flat-boundary scan](../../t5c_degenerate_limits_scan.py) and [results](../../t5c_degenerate_limits_results.json)
- [T1a task record](../tasks/T1a.md) and [T3c task record](../tasks/T3c.md)

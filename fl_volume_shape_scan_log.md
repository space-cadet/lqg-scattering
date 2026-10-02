# FL tetrahedron shape scan: experiment log

Recorded: 2026-10-02 22:01 IST (Asia/Kolkata)

Source checkout: `lqg-scattering`, branch `main`, HEAD `9b7f588`. The scan
source, results, and dashboard edits were in the working tree and not committed
to this repository at the time of this log. The website copy is on branch
`codex/lqg-scattering-dashboard`, commit `f0b6fdd`.

## Objective and scope

Record the numerical and visualization work on positive FL tetrahedron volume
at fixed total area label $J=2$, including the exploratory steps and the
evidence limits. The scan studies one continuous, equal-face-area shape family;
it does not enumerate all classical tetrahedra or all coherent-state labels.

The regular-tetrahedron volume-versus-area sweep for $J=1\ldots5$ was already
recorded in `memory-bank/implementation-details/volume-operator.md` and
`fl_volume_area_results.json`. It is referenced here rather than presented as
a new calculation from this shape scan.

## Investigation trail

1. Kept discrete spin/intertwiner labels separate from classical shapes. The
   saved `dashboard/fl-volume-allowed-labels.json` reports, at $J=2$, 19
   closure sectors (total intertwiner dimension 20), but only one sector with
   four positive faces and strict polygon inequality: $(1/2,1/2,1/2,1/2)$,
   with two recoupling channels. That is a label count, not a shape count.
2. Used the four spinor rays' cross ratio as a coordinate link to Thurston's
   four-marked-sphere moduli space. No identification was made between its
   cone-metric curvature data and LQG flux geometry, volume, or spin labels.
   Reference: [Thurston, *Shapes of polyhedra and triangulations of the sphere*](https://arxiv.org/abs/math/9801088).
3. Chose a closed, equal-area normal family parameterized by diagonal length
   $x$ and bending angle $\varphi$ so the plotted coordinates have direct
   geometric meanings and can be reconstructed as tetrahedra.

## Numerical protocol

For $u=\sqrt{1-x^2}$, the four unit face normals are

$$
\begin{aligned}
n_0&=(u,0,x), & n_1&=(-u,0,x),\\
n_2&=(u\cos\varphi,u\sin\varphi,-x), &
n_3&=(-u\cos\varphi,-u\sin\varphi,-x).
\end{aligned}
$$

Their sum is zero by construction. The scan uses 19 equally spaced $x$ values
from 0.03 through 0.97 plus $1/\sqrt{3}$, for 20 values total. It uses the
15-degree bending-angle grid from 15 to 345 degrees, omitting the degenerate
180-degree line, for 22 values. The product gives 440 ordered samples. Face
labels are not quotiented by permutations.

Each sample builds the Freidel–Livine Eq. (38) fixed-area state at $J=2$ and
evaluates positive Rovelli–Smolin (RS) and Ashtekar–Lewandowski (AL) volume
expectations in project-normalized units. The physical regularization
prefactor remains unselected. For the spinor rays, the recorded cross ratio is

$$
\lambda=\left(\frac{t^2-e^{i\varphi}}{t^2+e^{i\varphi}}\right)^2,
\qquad t^2=\frac{1-x}{1+x}.
$$

The script is `fl_volume_shape_scan.py`; the exact sampled records are in
`dashboard/fl-volume-shape-j2.json`. The initial full scan used the bundled
Python 3.12.14 runtime with NumPy 2.3.5. Running the script with its defaults
uses $J=2$, 19 base $x$ samples, and 24 angular divisions.

## Results and checks

- Closure residual maximum: 0.0. Maximum difference between the spinor
  cross-ratio calculation and its shape-coordinate formula: $8.68\times10^{-14}$.
- Sampled RS range: 0.05077553260216396 to 0.07482161446122469.
- Sampled AL range: 0.025387766749131426 to 0.037410807581783.
- Both sampled minima occur at the regular tetrahedron,
  $x=1/\sqrt{3}$, $\varphi=90^\circ$. The sampled maxima include
  $x=0.03$, $\varphi=15^\circ$; this grid result is not a proof of a global
  maximum.
- At the regular tetrahedron, the project routines give
  $V_{RS}=0.05077553260216396$ and $V_{AL}=0.025387766749131426$.
- Two direct local-spin tensor-product checks were made at
  $(x,\varphi)=(0.5,60^\circ)$ and $(1/\sqrt{3},90^\circ)$. The largest
  triple-matrix difference was zero at reported precision; RS expectation
  differences were at most $1.39\times10^{-17}$ and AL differences at most
  $6.94\times10^{-18}$.
- Rephasing the spinor columns and applying a common SU(2) rotation changed
  either volume by at most $6.94\times10^{-18}$ in the recorded invariance
  check.

The numerical command used for the full calculation was:

```text
/Users/deepak/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 fl_volume_shape_scan.py
```

Later figure-only edits loaded the saved JSON and called `make_svg`; those
edits did not recalculate the 440 volume records.

## Shape reconstruction and thumbnails

The plot originally encoded shapes only by dot position. To give those
coordinates a visual meaning, the thumbnail helper reconstructs a tetrahedron
from the closed unit face normals, treating each normal as an outward area
vector for unit face area. It orders three face vectors to give a negative
determinant, then uses

$$
D=\sqrt{-8\det(F_1,F_2,F_3)},\qquad
e_1=\frac{4(F_2\times F_3)}{D},\quad
e_2=\frac{4(F_3\times F_1)}{D},\quad
e_3=\frac{4(F_1\times F_2)}{D}.
$$

The four vertices are translated to their centroid and drawn with one fixed
orthographic camera. A manual check at the regular-tetrahedron point recovered
four unit face areas and the expected face-normal directions. The shape scan
generator contains the reconstruction in `tetrahedron_vertices` and the SVG
drawing in `tetrahedron_glyph`.

Each RS and AL panel now has six bottom thumbnails (vary $x$ at
$\varphi=90^\circ$) and five side thumbnails (vary $\varphi$ at
$x=1/\sqrt{3}$): 22 miniatures total. At degenerate axis ticks the nearest
valid sampled shape is shown. Each miniature is scaled to the same display
bounding box, so the drawings compare shape proportions, not absolute size.
These are static guides, not one tetrahedron for every heatmap dot.

An exploratory comparison reconstructed classical volume from the same
unit-face-area normals using $V_{\rm cl}=|\det(e_1,e_2,e_3)|/6$. At the
regular point $(x,\varphi)=(1/\sqrt{3},90^\circ)$ this gives
$V_{\rm cl}=0.41360216$, while the scanned RS/AL expectations are
0.05077553/0.02538777. At $(0.03,15^\circ)$, the reconstructed classical
volume is 0.05871810, but the quantum expectations are 0.07482161/0.03741081.
At $(1/\sqrt{3},165^\circ)$ they are 0.21041704 classically and
0.05867124/0.02933562 quantum mechanically. Thus these sampled points already
show that the project-normalized positive-operator expectations do not simply
track classical tetrahedron volume at $J=2$. This uses existing scan records
and the logged normal-to-edge reconstruction; it is not an independent volume
validation. The exact boundaries $x=0$, $x=1$, and $\varphi=180^\circ$ were
excluded, so no boundary-limit or fluctuation analysis has been performed.

## Figure and website trail

The figure source is `dashboard/figures/fl-volume-shape-j2.svg`; it is embedded
in the dashboard's Performance tab. The visual work proceeded as follows:

- `4bddb97` widened the SVG so the AL color-bar labels no longer clip; workflow
  `37005281266` completed successfully.
- `dd7fb65` added the first 11 shape thumbnails around the RS panel and a short
  explanation; workflow `37028432359` completed successfully.
- After the user noted the AL panel lacked thumbnails, `e9c96fa` added the
  matching guides around AL, for 22 total, and widened the figure to 1160 by
  520 SVG units; workflow `37030175574` completed successfully.
- The unversioned asset URL initially served the cached 11-thumbnail SVG,
  while a query-string version returned all 22. Commit `f0b6fdd` added that
  cache-busting version to the page's image URL. Workflow `37033479554`
  completed successfully.

The final live dashboard HTML and cache-busted SVG both returned HTTP 200. The
live SVG reported `viewBox="0 0 1160 520"` and contained all 22 miniature
tetrahedra. The local SVG was rendered with `rsvg-convert` for visual review;
the 440 numerical records were not rerun for these layout changes.

## Interpretation, caveats, and next steps

- The heatmap is a fixed-$J$ shape scan, not volume versus area. Its results
  cover equal face areas and ordered face labels only; they do not cover all
  area partitions or all of $\mathrm{Gr}(2,4)$.
- The cross ratio $\lambda$ is recorded as a coordinate for the four spinor
  rays. This is a coordinate correspondence, not evidence that Thurston's
  cone-metric geometry is the LQG flux geometry or that its lattice result
  enumerates LQG tetrahedra.
- “FL” identifies the Freidel–Livine fixed-area state in Eq. (38). The
  Freidel–Speziale (FS) name refers to the spinorial phase-space framework;
  this scan does not evaluate a separate FS state family.
- All volume values are project-normalized. The physical prefactor, graph
  embedding choices for AL beyond the recorded convention, broader independent
  checks, and behavior outside the sampled family remain open.
- A useful next enumeration is two-stage: enumerate allowed positive spin
  assignments and intertwiner channels at fixed $J$, then sample or
  parameterize the continuous tetrahedron shapes for each assignment. The
  current `fl_volume_labels.py` does only the first stage; the J=2 heatmap
  samples only the equal-area case.

The scan source and its JSON were untracked in the local `lqg-scattering`
checkout at HEAD `9b7f588` when this log was made. The website copy is deployed
and traceable to its separate branch and workflow above. A clean-checkout
reproduction from a committed LQG source revision has not yet been recorded.

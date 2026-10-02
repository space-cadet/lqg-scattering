# Volume Operator: Implemented Prescriptions and Limits

*Last Updated: 2026-10-03 00:27:43 IST*

## Current code

`positivity.volume_operator` and `rust::volume::volume_operator` construct one
triple-grasp matrix $q_{ijk}=i[J_i\cdot J_j,J_j\cdot J_k]$, evaluate
$\langle q_{ijk}\rangle$, and return

$$V_{\rm proxy}=(\gamma\hbar)^{3/2}\sqrt{|\langle q_{ijk}\rangle|}.$$

This is a signed-mean diagnostic followed by a scalar transformation. It does
not apply the positive square root of the operator to the state, and it does
not assemble a vertex operator from the edge triples. The function name and
older completion notes overstated what this code calculates. The corrected
Rust and Python scans must be described as signed triple-grasp results only.

## RS and AL vertex-volume calculations

The code now implements both prescriptions in the repository's dimensionless
triple-grasp normalization. For unordered triples $I<J<K$:

$$\hat V_{v,\mathrm{RS}}=c_{\mathrm{RS}}\sum_{I<J<K}\sqrt{|\hat q_{IJK}|},\qquad
\hat V_{v,\mathrm{AL}}=c_{\mathrm{AL}}\sqrt{\left|\sum_{I<J<K}\epsilon(e_I,e_J,e_K)\hat q_{IJK}\right|}.$$

The reported observable is $\langle\psi|\hat V_v|\psi\rangle$. The caller
supplies all AL tangent signs in lexicographic triple order. Each implementation
decomposes the populated sectors and evaluates the positive square root by
dense Hermitian spectral decomposition. It returns an error for an active
fixed-spin block larger than 512, rather than silently approximating it.
The default project prefactor is $(\gamma\hbar)^{3/2}$; use the explicit
`scale`/`prefactor` argument for a different regularization normalization.
The standard LQG regularization constants and $8\pi\ell_P^2$ factors have not
been selected or included, so these outputs are in project-normalized units.

For a finite-dimensional Hermitian $Q_v=U\,\mathrm{diag}(\lambda_a)U^\dagger$,
the required expectation is

$$\langle V_v\rangle=c\frac{\sum_a |(U^\dagger\psi)_a|^2\sqrt{|\lambda_a|}}{\langle\psi|\psi\rangle}.$$

It is generally not $c\sqrt{|\langle Q_v\rangle|}$. In particular,
$\langle q_{ijk}\rangle=0$ does not imply $q_{ijk}|\psi\rangle=0$ or zero
positive volume.

## Remaining work before large-scan or physical-volume claims

- Select and document the physical prefactors for the intended regularization.
- Supply justified graph embeddings and tangent-orientation signs for each
  AL state; the Grassmannian plane alone does not provide them.
- Confirm the coherent state lies in the Hilbert space where that operator
  and any proposed single-triple reduction apply.
- The EPJC Eq. (38) fixed-area state is the Freidel–Livine (FL) state, not a
  separate FS state family. Freidel–Speziale (FS) supplies the spinorial
  phase-space framework. The reproducible Python regular-tetrahedron check
  below matches an independently assembled local-spin tensor-product
  calculation to floating-point precision. The earlier discrepancy does not
  reproduce; its unsaved calculation’s cause remains unknown.
- Replace or extend dense block diagonalization before applying it to large
  sectors; current exact code refuses blocks above 512.
- Rerun the reported states. Keep the existing signed-mean series under its
  correct name; it is not a volume series.

## FL regular-tetrahedron check (2026-10-02)

The reproducible calculation in fl_volume_validation.py evaluates the EPJC
Eq. (38) fixed-area FL coherent state for a closed regular tetrahedron
($N=4$, $J=2$, $K=4$), using unit spinors aligned with its face normals. The
closure residual is zero at the input precision. With the project prefactor
$(\gamma\hbar)^{3/2}$, $\gamma=0.2375$, $\hbar=1$, and AL signs
$(+,-,+,-)$ for the listed triples, the results were:

- $\langle q_{012}\rangle=0.07216878364870322$ (imaginary roundoff
  $1.73\times10^{-18}$).
- Project routines: $V_{\rm RS}=0.05077553260216399$ and
  $V_{\rm AL}=0.025387766749131433$.
- Independent local-spin tensor-product evaluation: $V_{\rm RS}=0.050775532602163984$
  and $V_{\rm AL}=0.02538776674913143$. Triple-grasp matrices agree exactly at
  the reported precision; volume differences are $6.94\times10^{-18}$ (RS)
  and $3.47\times10^{-18}$ (AL).
- Reproducer: fl_volume_validation.py. The earlier unsaved direct calculation
  gave values lower by about $1.8\times10^{-10}$; its origin is unknown and the
  discrepancy does not reproduce with the saved independent construction.

Both methods give positive volume in this tested case. These are
project-normalized values, not finalized physical units. The Rust reproducer
rust/examples/fl_volume.rs is added but not compiled or run: the configured
Cargo symlink points to a missing rustup-init. This evidence does not
establish a family-wide or classical-limit claim.

## Fixed-area sweep and dashboard (2026-10-02)

`fl_volume_validation.py --sweep` evaluates the regular-tetrahedron FL
fixed-area state at $J=1,2,3,4,5$, with $A_{FL}/\ell_p^2=J$ in the paper's
labeling. Dashboard records are in `dashboard/data.json`; the standalone
vector chart is `dashboard/figures/fl-volume-area.svg`. The curve uses the
project routines' positive RS and AL expectations (project normalization,
$\gamma=0.2375$):

| $J$ | $V_{RS}$ | $V_{AL}$ |
|---:|---:|---:|
| 1 | 0 | 0 |
| 2 | 0.0507755326022 | 0.0253877667491 |
| 3 | 0.162213380300 | 0.081106690422 |
| 4 | 0.318938072750 | 0.159469036682 |
| 5 | 0.498859654825 | 0.249429827554 |

The independent direct-tensor check agrees with the triple-grasp matrices to
within $2.8\times10^{-15}$. Its positive-volume expectations differ from the
project eigensolver results by at most $2.91\times10^{-10}$ over this sweep;
the chart therefore shows the project routine values. The physical volume
prefactor remains unselected. Website copy was pushed to the isolated
`space-cadet/website` branch `codex/lqg-scattering-dashboard` at `824b2b8`.
Local browser loading and fallback behavior were checked. Live deployment was
deployed successfully with GitHub Actions run `36990851937`. Live Projects,
project, dashboard, JSON, and SVG endpoints returned HTTP 200. On the Projects
page, the “Quantum physics and research” group is collapsed by default; expand
it to reveal the card. The live browser loaded the dashboard data and static
area plot.

## FL equal-face-area shape scan at $J=2$ (2026-10-02)

`fl_volume_shape_scan.py` samples a closed equal-face-area normal family with
coordinates $x$ (diagonal length) and bending angle $\varphi$. The grid has 20
$x$ values and 22 nondegenerate angles, for 440 ordered samples. It excludes
$x=0$, $x=1$, and $\varphi=180^\circ$. Exact records, protocol, and figure/deploy
history are in `fl_volume_shape_scan_log.md` and
`dashboard/fl-volume-shape-j2.json`.

In project-normalized units, sampled RS values range from
$0.05077553260216396$ to $0.07482161446122469$, and AL values range from
$0.025387766749131426$ to $0.037410807581783$. Both minima occur at the regular
tetrahedron, $x=1/\sqrt{3}$, $\varphi=90^\circ$. The maximum closure residual is
zero; shape-coordinate and spinor cross ratios agree within
$8.68\times10^{-14}$. Direct local-spin tensor checks at two points agree with
RS within $1.39\times10^{-17}$ and AL within $6.94\times10^{-18}$. Rephasing and
common rotations leave the values unchanged within $6.94\times10^{-18}$.

This is evidence about the sampled equal-area family only. It is not a proof
that the regular tetrahedron minimizes either expectation across all shapes,
and it says nothing about the exact degenerate limits or their fluctuations.
The strict positive-face label enumeration at $J=2$ finds one assignment,
$(1/2,1/2,1/2,1/2)$, with two recoupling channels; this is a discrete label
count and does not enumerate continuous shapes.

An exploratory reconstruction of classical volume from the same unit-area
normals gives $V_{\rm cl}=0.41360216$ at the regular point,
$0.05871810$ at $(x,\varphi)=(0.03,15^\circ)$, and $0.21041704$ at
$(1/\sqrt{3},165^\circ)$. At the latter two points the quantum RS/AL values are
$0.07482161/0.03741081$ and $0.05867124/0.02933562$, respectively. This limited
comparison shows that the project-normalized $J=2$ expectations do not simply
track the reconstructed classical volume; it is not an independent classical
volume validation or a boundary-limit study.

The dashboard shape figure is `dashboard/figures/fl-volume-shape-j2.svg`; it
shows 11 representative tetrahedra in each RS and AL panel, 22 total. The
final website copy is commit `f0b6fdd`, deployed by workflow `37033479554`; its
HTML and cache-busted SVG returned HTTP 200. Planned work is to study the excluded
degenerate limits and volume spread across increasing $J$, then extend allowed
positive spin-assignment enumeration and shape sampling to unequal face areas.
The qhe-bhe Thurston/Minkowski material may help construct or constrain the
classical shape domain, but it does not by itself prove a minimum for these
quantum operators.

## Code locations

| File | Current role |
|---|---|
| `positivity.py` | Python signed-mean proxy and positive RS/AL expectations |
| `rust/src/volume.rs` | Rust signed-mean proxy and positive RS/AL expectations |
| `fl_volume_validation.py` | Eq. (38) FL tetrahedron state and independent local-spin tensor-product check |
| `rust/examples/fl_volume.rs` | Rust reproducer for the same fixed-area tetrahedron state |
| `memory-bank/implementation-details/red-team-audit.md` | Numerical audit and current evidence |

The positive routines are `rovelli_smolin_volume` and
`ashtekar_lewandowski_volume` in both implementations. The exact small-state
cross-check is recorded in `volume_prescription_results.json` and can be
reproduced with `volume_prescription_demo.py`.

References: Rovelli and Smolin, [Discreteness of Area and Volume in Quantum Gravity](https://arxiv.org/abs/gr-qc/9411005), and Lewandowski, [Volume and Quantizations](https://arxiv.org/abs/gr-qc/9602035), distinguish the RS sum of positive triple contributions from the AL orientation-weighted sum. Ashtekar and Lewandowski, [Quantum Theory of Geometry II: Volume Operators](https://arxiv.org/abs/gr-qc/9711031), construct the AL operator. Regularization prefactors depend on the selected convention.

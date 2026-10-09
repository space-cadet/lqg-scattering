# Volume Operator: Implemented Prescriptions and Limits

*Last Updated: 2026-10-10 01:14 IST*

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
dense Hermitian spectral decomposition. Eigenvalues satisfying
$|\lambda|\le64\epsilon_{\rm mach}\max(1,\rho(|Q|))$ are treated as zero to
remove roundoff contributions from exact kernel modes; Python and Rust use the
same cutoff. It returns an error for an active fixed-spin block larger than
512, rather than silently approximating it.
The default project prefactor is $(\gamma\hbar)^{3/2}$; use the explicit
`scale`/`prefactor` argument for a different regularization normalization.
The standard LQG regularization constants and $8\pi\ell_P^2$ factors have not
been selected or included, so these outputs are in project-normalized units.

For a classical tetrahedron with closed face vectors, the geometric volume
is $\sqrt{2/9}\sqrt{|q|}$. Closure gives the four classical triple symbols
the pattern $(q,-q,q,-q)$; with AL tangent signs $(+,-,+,-)$, the symbols
of the raw RS and AL expressions are $4\sqrt{|q|}$ and $2\sqrt{|q|}$.
T5c therefore compares them with the same input tetrahedron using the fixed
project-volume factors $\kappa_{\mathrm{RS}}=\sqrt{2}/12$ and
$\kappa_{\mathrm{AL}}=\sqrt{2}/6$. These align this triple-grasp convention
with the Euclidean area-vector volume; they do not supply the remaining
physical regularization prefactor. The factors and derivation are recorded
in the [T5c comparison](./T5c-flux-covariance-volume-comparison.md).

For the tested gauge-invariant four-valent states and signs, the triple
operators obey the closure pattern on the state to numerical precision.
Consequently the RS and AL expectations become the same curve after their
respective geometric factors are applied. Treat this as one comparison in
two operator conventions, not as two independent confirmations.

For a finite-dimensional Hermitian $Q_v=U\,\mathrm{diag}(\lambda_a)U^\dagger$,
the required expectation is

$$\langle V_v\rangle=c\frac{\sum_a |(U^\dagger\psi)_a|^2\sqrt{|\lambda_a|}}{\langle\psi|\psi\rangle}.$$

It is generally not $c\sqrt{|\langle Q_v\rangle|}$. In particular,
$\langle q_{ijk}\rangle=0$ does not imply $q_{ijk}|\psi\rangle=0$ or zero
positive volume.

## Remaining work before large-scan or physical-volume claims

- Select and document the remaining physical prefactors for the intended
  regularization.
- Extend the FL comparison across weighted input shapes and $J$ using the
  fixed geometric factors above; do not tune a factor separately to each
  shape.
- Record positive-volume variance and controlled degenerate paths where
  feasible. Near zero classical volume, use absolute discrepancies and state
  which order of the large-$J$ and degenerate limits is being evaluated.
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
- Use the shared numerical zero-mode cutoff when reproducing the reported
  values. Keep the signed-mean series under its correct name; it is not a
  volume series.

## FL regular-tetrahedron check (updated 2026-10-03)

The reproducible calculation in code/python/fl_volume_validation.py evaluates the EPJC
Eq. (38) fixed-area FL coherent state for a closed regular tetrahedron
($N=4$, $J=2$, $K=4$), using unit spinors aligned with its face normals. The
closure residual is zero at the input precision. With the project prefactor
$(\gamma\hbar)^{3/2}$, $\gamma=0.2375$, $\hbar=1$, and AL signs
$(+,-,+,-)$ for the listed triples, the results were:

- $\langle q_{012}\rangle=0.07216878364870322$ (imaginary roundoff
  $1.73\times10^{-18}$).
- With the numerical zero-mode cutoff above, project routines give
  $V_{\rm RS}=0.05077553170606511$ and
  $V_{\rm AL}=0.02538776585303255$.
- Independent local-spin tensor-product evaluation agrees within
  $7\times10^{-18}$. Triple-grasp matrices agree exactly at the reported
  precision.
- The Rust reproducer reports $V_{\rm RS}=0.05077553170606511$ and
  $V_{\rm AL}=0.02538776585303254$, matching Python at the displayed precision.
  Its $\langle q_{012}\rangle=0.07216878364870326$ agrees with Python.
- Before the cutoff, the raw eigensolver results differed across Python and
  Rust by about $6\times10^{-10}$ because square roots magnify roundoff in exact
  zero modes. Applying the same scale-aware cutoff removes that engine-dependent
  drift. The older unsaved inline value remains unrecoverable.

Both methods give positive volume in this tested case. These are
project-normalized values, not finalized physical units. The Rust reproducer
`code/rust/examples/fl_volume.rs` was built and run with the installed Rust 1.92
toolchain by directly invoking its binaries. The configured Cargo shim still
points to a missing rustup-init. This evidence does not establish a
family-wide or classical-limit claim.

## Fixed-area sweep and dashboard (2026-10-02)

`code/python/fl_volume_validation.py --sweep` evaluates the regular-tetrahedron FL
fixed-area state at $J=1,2,3,4,5$, with $A_{FL}/\ell_p^2=J$ in the paper's
labeling. Dashboard records are in `code/dashboard/data.json`; the standalone
vector chart is `code/dashboard/figures/fl-volume-area.svg`. The curve uses the
project routines' positive RS and AL expectations (project normalization,
$\gamma=0.2375$):

| $J$ | $V_{RS}$ | $V_{AL}$ |
|---:|---:|---:|
| 1 | 0 | 0 |
| 2 | 0.0507755317061 | 0.0253877658530 |
| 3 | 0.162213379240 | 0.0811066896201 |
| 4 | 0.318938071292 | 0.159469035646 |
| 5 | 0.498859653624 | 0.249429826812 |

The independent direct-tensor check agrees with the triple-grasp matrices to
within $2.8\times10^{-15}$. With the shared numerical zero-mode cutoff, direct
positive-volume expectations differ from the project routines by at most
$1.67\times10^{-16}$ (RS) and $5.55\times10^{-17}$ (AL) over this sweep. The
physical volume prefactor remains unselected. Website copy was pushed to the isolated
`space-cadet/website` branch `codex/lqg-scattering-dashboard` at `824b2b8`.
Local browser loading and fallback behavior were checked. Live deployment was
deployed successfully with GitHub Actions run `36990851937`. Live Projects,
project, dashboard, JSON, and SVG endpoints returned HTTP 200. On the Projects
page, the “Quantum physics and research” group is collapsed by default; expand
it to reveal the card. The live browser loaded the dashboard data and static
area plot.

## FL equal-face-area shape scan at $J=2$ (updated 2026-10-03)

`code/python/fl_volume_shape_scan.py` samples a closed equal-face-area normal family with
coordinates $x$ (diagonal length) and bending angle $\varphi$. The grid has 20
$x$ values and 22 nondegenerate angles, for 440 ordered samples. It excludes
$x=0$, $x=1$, and $\varphi=180^\circ$. Exact records, protocol, and figure/deploy
history are in `notes/experiments/fl_volume_shape_scan_log.md` and
`code/dashboard/fl-volume-shape-j2.json`.

In project-normalized units, sampled RS values range from
$0.05077553170606508$ to $0.07482161375888345$, and AL values range from
$0.025387765853032544$ to $0.03741080687944174$. Both minima occur at the regular
tetrahedron, $x=1/\sqrt{3}$, $\varphi=90^\circ$. The maximum closure residual is
zero; shape-coordinate and spinor cross ratios agree within
$8.68\times10^{-14}$. Direct local-spin tensor checks at two points agree with
RS within $1.39\times10^{-17}$ and AL within $6.94\times10^{-18}$. Rephasing and
common rotations leave the values unchanged within $6.94\times10^{-18}$. The
cutoff removes eigensolver roundoff in exact kernel modes and is applied in the
saved data and figure.

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

## Real-plane positive-volume check (2026-10-03)

`code/python/real_plane_volume.py` builds normalized $N=4$, $K=6$ Perelomov states from the
same non-collinear reference occupations for two explicit real planes: one in
the strictly positive cell and one outside it (the latter has $M_{34}=-1$).
Both states have real amplitudes and $\langle q_{012}\rangle=0$ to
floating-point precision. Their project-unit expectations are:

| Real plane | $V_{\rm RS}$ | $V_{\rm AL}$ |
|---|---:|---:|
| Strictly positive cell | 0.1205292375514575 | 0.0751162653864954 |
| Outside positive cell | 0.1205292375514575 | 0.0751162653864954 |

The AL calculation uses regular-tetrahedron orientation signs $(+,-,+,-)$.
Independent local-spin tensor-product matrices agree within
$5.6\times10^{-17}$; the largest triple-matrix difference is
$5.6\times10^{-16}$. Results are saved in
`results/t1b_real_plane_volume_results.json`. These values establish nonzero positive
volume for these two examples only; they do not establish a statement for
every real-plane state or graph embedding.

The dashboard shape figure is `code/dashboard/figures/fl-volume-shape-j2.svg`; it
shows 11 representative tetrahedra in each RS and AL panel, 22 total. The
latest visual update is website commit
`9c6670c190e813470975f18037c1ed4a6ecea8bc`, deployed by workflow `37125090987`;
it reuses pre-rendered input-shape thumbnails and adds T5c per-point previews.
Whenever a dashboard view traces tetrahedron shape parameters, include shape
thumbnails; for selectable points, show that point's saved thumbnail and reuse
the generated SVGs across views. The paired input/covariance presentation is
specified in the [T5c implementation note](./T5c-flux-covariance-volume-comparison.md).
The refreshed numerical data remain separate from this visual update. Planned
work is to study the excluded degenerate limits and volume spread across
increasing $J$, then extend allowed positive spin-assignment enumeration and
shape sampling to unequal face areas. The qhe-bhe Thurston/Minkowski material
may help construct or constrain the classical shape domain, but it does not by
itself prove a minimum for these quantum operators.

## Code locations

| File | Current role |
|---|---|
| `code/python/lqg_scattering/positivity.py` | Reusable Python signed-mean proxy and positive RS/AL expectations; root `positivity.py` is a compatibility facade |
| `code/rust/src/volume.rs` | Rust signed-mean proxy and positive RS/AL expectations |
| `code/python/fl_volume_validation.py` | Eq. (38) FL tetrahedron state and independent local-spin tensor-product check |
| `code/rust/examples/fl_volume.rs` | Rust reproducer for the same fixed-area tetrahedron state |
| `code/python/real_plane_volume.py` | T1b positive RS/AL evaluations on two real-plane states |
| `memory-bank/implementation-details/red-team-audit.md` | Numerical audit and current evidence |

The positive routines are `rovelli_smolin_volume` and
`ashtekar_lewandowski_volume` in both implementations. The exact small-state
cross-check is recorded in `results/volume_prescription_results.json` and can be
reproduced with `code/python/volume_prescription_demo.py`.

References: Rovelli and Smolin, [Discreteness of Area and Volume in Quantum Gravity](https://arxiv.org/abs/gr-qc/9411005), and Lewandowski, [Volume and Quantizations](https://arxiv.org/abs/gr-qc/9602035), distinguish the RS sum of positive triple contributions from the AL orientation-weighted sum. Ashtekar and Lewandowski, [Quantum Theory of Geometry II: Volume Operators](https://arxiv.org/abs/gr-qc/9711031), construct the AL operator. Regularization prefactors depend on the selected convention.

## Related documentation

- [Shared volume numerical preliminaries](./volume-numerical-preliminaries.md)
- [T5 volume-positivity studies](./volume-positivity-studies.md)
- [T5c covariance reconstruction and comparisons](./T5c-flux-covariance-volume-comparison.md)
- [T6 Minkowski reconstruction](./T6-minkowski-polyhedron.md)
- [Fock-space construction](./fock-space-construction.md)
- [Grassmannian embedding](./grassmannian-embedding.md)
- [Rust port architecture](./rust-port-architecture.md)
- [Verification protocol](./verification-protocol.md)
- [Red-team audit](./red-team-audit.md)
- [T1a Python validation task](../tasks/T1a.md) and [T3c Rust validation task](../tasks/T3c.md)
- [FL shape-scan evidence log](../../notes/experiments/fl_volume_shape_scan_log.md)

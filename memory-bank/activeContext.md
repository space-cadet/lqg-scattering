# Active Context

*Last Updated: 2026-10-16 13:11:31 IST*

## Current Focus
T11 now includes the October 16 channel pilot and classical rotor equilibration
studies. The rotor results distinguish moderate-packet spreading from
finite-time high-energy concentration and show delayed release at longer times;
they do not establish permanent localization. The exact planar-pair threshold
and coupling scan are recorded separately. No quantum rotor evolution has
been run. See the [physics handoff](sessions/2026-10-16-equilibration-and-rotors-summary.md)
and [rotor notes](../notes/classical-rotor-equilibration.md).

The local dashboard now includes curated channel and rotor records: 30 catalogue
studies and 39 datasets. Its checker passes with 620 links and 314 hash checks;
source parity confirms 2,512 rows and 34,766 numerical values. Full per-run
archives and the large equilibration time series remain local and are ignored
by Git; compact summaries and protocols are versioned. The curated package is
published and passed hosted checks; see the [dashboard acceptance record](ui-tests/2026-10-16-numerics-dashboard-refresh.md).
T9 and T9a continue as active, independent thermal studies; the separately closed F12
entropy work is recorded in the [thermal note](../notes/thermal-entanglement.md).

**Primary Task:** T11 — Hamiltonian, volume, face-channel and rotor dynamics.
**Supporting Tasks:** T9/T9a thermal studies; T1a Python volume numerics; T3c Rust volume implementation; T6 kinematic Minkowski geometry; T4 separate numerical follow-up manuscript audit; T8 amplituhedron program.

## Active Tasks
- T4: Manuscript claim audit and review preparation — IN PROGRESS; independent audit recorded.
- T1a: The regular FL tetrahedron sweep covers $J=1\ldots5$. At $J=2$, both RS and AL have their minima at the regular tetrahedron among 440 ordered equal-face-area samples; this is not a global-minimum proof. Initial weighted-area input-volume pilots cover one unequal geometry through $J=7$, a nine-shape grid at $J=2,4$, and selected $J=6$ points. Broader unequal-area coverage and degenerate limits remain open.
- T3c: The Rust FL Eq. (38) example now builds and matches the Python $J=2$ result after the shared zero-mode cutoff. Physical prefactors and a method for blocks above 512 remain open; the Cargo shim itself is still broken.
- T5: Volume–positivity numerical-studies program — IN PROGRESS; T5c/T5d/T5g open; the former T5f amplituhedron mapping is now T8b. Initial T5c pilots compare the input classical tetrahedron with weighted FL positive volume: regular/unequal-skew through $J=7$, a nine-shape unequal-area grid at $J=2,4$, selected $J=6$ points, and a flat path through $J=7$. Area means and weighted closure pass; finite-$J$ unequal correlations do not exactly reproduce input angles. Calibrated RS/AL agreement follows from closure and is not independent evidence. Broader shape and iterated-limit conclusions remain open. See `implementation-details/T5c-flux-covariance-volume-comparison.md` and shared `implementation-details/volume-numerical-preliminaries.md`.
- T8: Amplituhedron Program — IN PROGRESS; T8a cluster algebra/chart relevance and T8b positive-cell/scattering-region mapping (transferred from T5f) are open. See `tasks/T8.md`.
- T9: Thermal/TFD state construction and physical study — IN PROGRESS; owns all ongoing TFD construction and analysis, with exactly five completed child-study records T7a–T7e. The four-face $J_{\mathrm{in}}=1$ occupation/spin comparison is complete through $q=160$. October 13 results quantify ordinary per-copy closure and show that separate singlet projection retains closed states with increasing mean area and positive RS volume; the area asymptote is $(57/14)T_*$. The October 14 analytic eigenvalue-ratio test excludes a fixed single-copy Gibbs Hamiltonian for this separately closed reference family; the separately closed reference spectra and entropy are now calculated; unprojected and other-input characterization remain open.
- T11: Hamiltonian, volume and face/rotor dynamics — IN PROGRESS. NS32–36 record large-area free-hopping activation, the small-area channel pilot, classical rotor spreading, the exact pair benchmark and the larger-ring coupling crossover. Moderate packets approach sampled microcanonical readouts; high packets can remain concentrated through $t=2000$ and some release later. The local dashboard now packages the four new channel/rotor records, and its data checks pass. Quantum rotor evolution and distinct-normal geometry remain open. See the [numerical chronology](../notes/numerical-studies.md) and [rotor handoff](sessions/2026-10-16-equilibration-and-rotors-summary.md).
- The numerics dashboard includes 30 InfoDash datasets (2,049 rows) alongside the existing catalogue of 21 studies, 29 records, and 38 figures. Website commit `8263c95b2250bc724605a71c73f1a13e429b1b3d` deployed the integration; follow-up website commit `3c1edad` added the desktop note reader. Live review confirmed all four tabs, rendered Markdown and math, and working chronology links. See [deployment session](sessions/2026-10-12-infodash-deployment.md) and [desktop reader session](sessions/2026-10-13-infodash-desktop-note-reader.md).

## Project State
- Published EPJC paper is the frozen baseline.
- All source code, including LaTeX manuscript sources and build assets, is grouped under `code/`; compiled PDFs remain under `paper/`.
- The project root retains the README and living manuscript. Calculation JSON files are organized under `results/`; experiment records, task specifications, and the published-paper overview are under `notes/`. Dashboard files now sit directly in `code/dashboard/`.
- The task inventory has dedicated records for all 29 current registry IDs plus the transferred historical T5f and T7 records. Completed tasks are archived; active tasks remain under `tasks/`. Statuses and task relationships were reconciled against the current Memory Bank and full Git history.
- T1b's positive-volume follow-up is complete for two $N=4$, $K=6$ real-plane states inside and outside the positive cell; both RS and AL expectations are nonzero and independently cross-checked.
- Python and Rust implementations exist. The old n=4 comparison shared a truncated Taylor state. Corrected Rust scans now cover n=4..8; SciPy independently checks n=4,5,7,8.
- `manuscript.md` contains results through T7e but needs corrected conclusions, caveats, independent review, and circulation.
- At the start of the 2026-10-06 task-record audit, `main` and `origin/main` both pointed to `0a254849a5e12734ee32d9d8af74bd4309d17648`. Existing local numerical, dashboard, and Memory Bank work remains in the working tree; this audit preserved it while reconstructing task records from the full 79-commit history. Separately, the dashboard's math typesetting update was deployed from website commit `15f698f` (workflow `37286586717`) and verified live in the study and fixed-area sections. Chart SVG labels remain compact text; mobile view was not examined, per the user's direction. The earlier plot-artwork update is website commit `9c6670c`. Two pre-existing untracked Python cache directories remain under `__pycache__/` and `code/dashboard/__pycache__/`.
- T7 was archived as the former umbrella; T9 now owns all thermal/TFD work. The selected target is $U_\beta(|J,z\rangle_L\otimes|\overline{J,z}\rangle_R)$ with transformed geometric observables. The $SU(1,1)$ factorization and coefficient-level partial-trace construction are documented. The four-face $J_{\mathrm{in}}=1$ $P(q,S)$ marginal has two agreeing implementations through $q=160$. The October 13 study adds ordinary-closure temperature dependence and a separately closed geometric projection; its conditional mean area has the high-temperature coefficient $57/14$, and positive RS volume increases over the studied range. Full selected-state reduced blocks, entropy, and Gibbs characterization remain open. See `tasks/T9.md`, `notes/thermal-area-sectors.md`, and the [October 13 session](sessions/2026-10-13-t9-thermal-closure-and-geometry.md).
- The constructive F-pair sewing discussion is recorded in [the dialogue note](implementation-details/constructive-geometric-sewing-dialogue.md) and [the session transcript](sessions/2026-10-04-geometric-construction-transcript.md). Triangle, tetrahedron, and joined exterior-boundary tensor sewing are now implemented at small spin, with independent checks; metric shape and volume remain unvalidated, and no dedicated task ID is assigned.

## Current Decisions
- Under T11, the physical volume sum uses connected induced triples. For the four-site complete graph and ring, all four three-site subsets are connected, so the selected volume operators coincide; only the hopping graphs differ.
- In the tested four-site sectors, $[H_U,V]$ vanishes and $[H,V]$ comes from hopping. The four positive triple-root matrices agree within $8.4\times10^{-17}$; this is not a larger-graph result.
- The corrected T5a magnetization sweep converged in 39–41 terms and four sectors matched SciPy exponentiation. Retain its one-plane scope.
- Keep T5a′ local-triple findings separate from the corrected magnetization sweep and retain their limited sample-size caveats.
- T5e does not establish the expected classical $K^{3/2}$ volume growth through $K=24$; do not summarize it as a checked classical limit.
- Gibbs TFD tends to the Fock vacuum, not a Perelomov state. The T7e result is limited to the tested fixed-$K$ construction and does not establish a general $V(\epsilon,T)$ law.
- Distinguish the signed-mean proxy from positive volume expectations. RS sums positive triple roots; AL takes the positive root after an embedding-signed triple sum. Both are now implemented in project normalization for active blocks up to dimension 512.
- Set eigenvalues within $64\epsilon_{\rm mach}\max(1,\rho(|Q|))$ to zero in both Python and Rust positive-volume routines; this prevents solver-dependent positive contributions from exact kernel modes.
- Do not mark numerical claims red-team reviewed without a documented protocol and per-claim evidence.
- Under T9, study the user's selected two-copy squeezed FL state with transformed observables. Keep full doubled-space observables distinct from left-reduced-state expectations. A fixed positive total-area Hamiltonian on unrestricted Fock space cannot generate this family at all temperatures: the Gibbs limit is vacuum while the squeezed family returns its nonzero-$J$ input state.

## Code maintenance handoff

The reusable Python package is `code/python/lqg_scattering/`; legacy root
modules for coherent states, positivity, Grassmannian geometry, Minkowski
reconstruction, and correspondence now act as compatibility facades. Python
plus Rust remains the selected research stack. The saved Python-versus-TS
comparison is limited to a matched $K=2$ T11 workload and should not be treated
as a general performance ranking. The scoped extraction is complete, including Hamiltonian, variable-face,
thermal, and fitting cores. Numerical parity, wheel/sdist builds, external
installation, and tests passed. Standard-library consolidation is deferred.
The latest complete suite passed 38 tests.

## Next Actions
1. Expand the weighted FL shape grid beyond the first area partition and track the face-normal and vertex-sphere cross-ratios alongside Euclidean metric data; treat normals as input labels and correlations as the quantum shape diagnostic.
2. Extend selected shape and unequal-area volume comparisons to larger $J$; quantify convergence and the remaining shape dependence under the fixed geometric factors.
3. Extend the flat-boundary path far enough in $J$ and smaller $\varphi$ to assess each iterated limit; keep absolute discrepancies near zero classical volume.
4. Fix and document the graph embedding and AL signs, keep project units separate from physical prefactors, and address active blocks above dimension 512 when required.
5. Extend the corrected T5a and T5b results across plane controls
  and run T5d with real off-cell controls.
6. Complete T5c/T6 polyhedron reconstruction and controlled comparisons.
7. Under T9, extend the validated $J_{\mathrm{in}}=1$ calculation to the selected two-copy state, combining coherent contributions within each final occupation sector.
8. Form the sector matrices $C_qC_q^\dagger$ and evaluate their spectrum and entropy with explicit convergence controls.
9. Calculate two-sided and transformed geometric observables; compare with only explicitly specified ensemble Hamiltonians.
10. Review corrected numerical artifacts before circulating the manuscript.

## Latest volume session

Completed the single-copy four-face closed-basis catalogue and positive RS/AL data through $K=12$ (10,549 states), with matrices, figures and independent checks. The extension stopped at the user request; no $K=13$ result is accepted. New notation: $K$ total linear area, $J$ resultant angular momentum. [T10](tasks/T10.md) is complete for the labelled positive-face RS catalogue at $K=2,3,4$; higher-valence AL geometry and physical normalization remain open limitations. Further single-copy content is in [volume studies](../notes/volume-studies.md). T9 thermal reduced-state/geometry work remains open. See [summary](sessions/2026-10-08-volume-studies.md) and [physics transcript](sessions/2026-10-08-volume-physics-transcript.md).

## Separate volume-studies record — 2026-10-09 11:10:50 IST

The user requested a dedicated [volume note](../notes/volume-studies.md) to keep the thermal-sector write-up focused. It records the numerical catalogue, analytic counting, Feller–Livine attribution, area/closure restrictions, and the proposed lattice program. The immediate physics continuation is the single-copy Hamiltonian–volume commutator; reordering details are deferred. The connected-triple prescription and unconnected transition channels are recorded as the user's research direction; the assistant's graph-labelled formulation was not adopted. No Hamiltonian or thermal numerical calculation was added.

## Binding and sewing continuation

T11 now includes same-number singlet detachment energies for an intact
four-site system versus a three-boson fragment and isolated one-boson face.
The user's next objective is two separate tetrahedra versus two tetrahedra
sewn along a triangular face. The implemented sewing follows physical edge
copies and changes all three interface neighbor relationships. It is not the
same degree-of-freedom model as face-site Bose-Hubbard hopping.

Resume from [the current handoff](sessions/2026-10-10-binding-and-constructive-sewing-summary.md)
and [physics transcript](sessions/2026-10-10-binding-and-constructive-sewing-transcript.md).
First specify exterior-boundary versus retained two-cell bulk dynamics and
conserved resources. The suggested edge-Casimir plus loop Hamiltonian is
unaccepted and unimplemented; no sewn-network binding energy is calculated.


## T11 geometric-result closeout — 2026-10-11 10:27:17 IST

- Completed and checked four/five-site persistence, five explicitly prepared $K=4$ FL references, their geometric diagnostics, energy-group comparisons and Gibbs reconstruction. Prior suite: 42 tests; independent residual maximum $5.14\times10^{-12}$. No physics rerun in this update.
- The complete-graph collapse does not persist at five sites. At four sites the ground is kernel-dominated with broad angular fluctuations, despite near-unit four-face weight.
- Preserved both physics dialogs in the Hamiltonian write-up. On-site repulsion is the preferred term interpretation. $g_VV$ and signed-triple terms are proposals; $K=4$ FL evolution is unperformed.
- [Session record](sessions/2026-10-11-t11-geometry-closeout.md); T11 stays IN PROGRESS. The 18-study deployment references above are historical; current deployment evidence is recorded separately below when verified.


### Verified dashboard release — 2026-10-11 11:07:11 IST

Website main `cea6ae9`; deployment run `38113563387` succeeded. Live catalogue: 20 studies, 28 records, 33 figures; all 235 asset URLs passed public checks and browser verification showed the new T11 cards/plots. See [deployment evidence](sessions/2026-10-11-t11-geometry-closeout.md#dashboard-deployment-and-acceptance). Research files remain uncommitted; no new scientific calculation.


## T11 candidate-Hamiltonian and FL-evolution follow-up — 2026-10-11 13:52:01 IST

The earlier statement that the prepared-$K=4$ references had not been evolved
is historical: the later candidate study propagated all five references under
the baseline and both signs of the positive-volume and signed-grasp terms at
$U/t=5,20$. It saved 50 exact energy-basis trajectories and passed 1,510
independent checks with maximum residual $1.07\times10^{-12}$. The candidate
couplings are not physically derived, and the volume remains in project
units. See [the study report](../results/t11-candidate-hamiltonians/README.md)
and [the session closeout](sessions/2026-10-11-t11-geometry-closeout.md).

The newest deployed catalogue contains 21 studies, 29 records, and 38 figures
(website commit `f59a2ccd4e3b47edd91e1c974dd3eb4b20ed8c98`, workflow
`38124134232`). All 30 new T11 links returned HTTP 200 and four compressed
data hashes matched their packaged files.

## InfoDash dashboard deployment — 2026-10-12

Published the pinned InfoDash application and saved numerical datasets. The
production workflow succeeded, and the live route serves all 30 datasets and
all 301 referenced asset URLs. The lqg-scattering source work remains local and
uncommitted; T11 research remains in progress. See the
[deployment record](sessions/2026-10-12-infodash-deployment.md).


## T9 manuscript and equilibrium continuation — 2026-10-14

- [Session record](sessions/2026-10-14-t9-manuscript-and-equilibrium.md): records the initial 15-page build with corrected closure equations and temperature results; the final 19-page version, including equilibrium and exchange material, is documented below.
- [Thermal note](../notes/thermal-geometry-and-singlet-exchange.md#section-17): pedagogical observables/equilibrium discussion and exact vacuum/reference eigenvalue-ratio obstruction, derived from existing coefficients without a new numerical sweep.
- [Volume continuation](../notes/volume-studies.md#area-conservation-volume-dynamics-and-exchange): conserved total area allows changing volume; separate singlet exchange permits changing individual areas. Transfer and correlated-creation Hamiltonians and their many-body analogues are proposals for further study.
- T9 owns this work. T4 concerns `manuscript.md`, the separate numerical follow-up. No new task or numerical implementation was created.

## T9a singlet-exchange continuation — 2026-10-14 14:35:25 IST

New T9 child [T9a](tasks/T9a.md) owns the implemented two-polyhedron finite-area FL exchange pilot and the open reservoir/equilibrium comparison. See [session](sessions/2026-10-14-t9a-singlet-exchange.md) and [study specification](../notes/t9a-singlet-exchange.md). Prior five-child restriction is superseded by explicit user direction; T7a–T7e are preserved.

## Thermal-note extraction — 2026-10-14 16:05:06 IST

The new [heating, equilibrium and exchange note](../notes/thermal-geometry-and-singlet-exchange.md) contains the previous and current sessions' physical work with four figures. The retained [area-sector note](../notes/thermal-area-sectors.md) has a [reorganization assessment](../notes/thermal-area-sectors-reorganization.md); its full rewrite/appendix separation remains pending. Numerical/code state is unchanged by the extraction.

## Thermal-note rewrite complete — 2026-10-14 16:13:37 IST

[The remaining thermal note](../notes/thermal-area-sectors.md) now has six physical sections and seven appendices; all eight figures and legacy anchors remain. The [editorial assessment](../notes/thermal-area-sectors-reorganization.md) records completion. The main-text/appendix rewrite is no longer pending. Scientific implementation and results are unchanged.

## Final T9 manuscript integration — 2026-10-14 17:24:59 IST

The final manuscript adds the fixed-Gibbs eigenvalue-ratio test, singlet-exchange Hamiltonian and current, finite-pilot results, many-body connections, and an appendix deriving the projected-area asymptote. The delivered [19-page PDF](../paper/thermal-intertwiners/thermal-intertwiners.pdf) compiled with the new citations resolved; pages 12–17 were visually checked. This supersedes the earlier 15-page, Figures 9–11 checkpoint recorded above.

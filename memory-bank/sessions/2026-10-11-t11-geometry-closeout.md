# T11: larger-system and tetrahedral-geometry closeout

*Recorded: 2026-10-11 10:27:17 IST*

## Focus and completed results

Continued the single-copy Hamiltonian-volume study at source commit `9ef9bba`, preserving T9 and constructive sewing as separate work. The prior session summary supplied by the user is reproduced in the current-session transcript; numerical reports and CSV/JSON files remain the scientific source of truth.

- Completed density-matched four/five-site comparison: dimensions 105 and 1,176, complete/ring, unit hopping per bond, $t=1,U=20,g=0$, free/no-hop controls, 701 finite inverse temperatures $10^{-3}$ to $10^4$ plus zero/infinity. Selected triples: 4/4 at four sites, 10/5 at five sites. Saved total/per-triple volume. Nonmonotonicity persists; pronounced complete collapse does not. Complete gaps: $0.0092257t$ and $12.643382t$; five-site complete ground degeneracy six. Coordination/parity change prevents clean scaling interpretation. Six sites were not run. Prior pilot agreement within $7.2\times10^{-14}$; 38 tests and independent controls passed.
- Corrected the four-site labels/highlighted bonds in the system illustration to ring order $0-1-2-3-0$. Final asset: `figures/hamiltonian-systems/four-and-five-site-graphs.png`. This was an illustration correction, not a numerical correction.
- Constructed five equal-input-area FL states at $K=4$ along $\varphi=90,60,30,10,0$ degrees, with $x=1/\sqrt3$. The actual spinors and closure are recorded in `reference_inputs.json` and the physics dialogue. Calculated spin, angular, volume, signed-grasp and overlap diagnostics for those states and three energy groups per graph; reconstructed Gibbs diagnostics on the original 601-point grid plus endpoints.
- Explained complete-graph suppression by kernel-dominated ground-state weight and broad angular fluctuations; active-face loss is not the mechanism. Same-assignment ground/excited volumes differ despite identical mean angles. Reused T5c $\sqrt2/12$ conversion. All 42 prior-session tests and independent controls passed, largest residual $5.14\times10^{-12}<2\times10^{-10}$. No new Rust run. Output/source hashes are saved.
- Clarified 105 full-space dimensions versus 51 four-active-face dimensions and positive/zero volume counts (38/67 full, 38/13 conditioned); worked through face assignments and shared-intermediate-spin singlets.

## Current-session decisions and proposals

Complete/ring labels specify interaction Hamiltonians and Gibbs mixtures, not one prepared shape. Complete connectivity matches tetrahedral face adjacency if hopping is interpreted as adjacent-face area exchange; ring is a control. On-site repulsion is the user's preferred interpretation. Three-face bulk interaction choices were discussed: positive volume $g_VV$ and signed $\lambda q$. Neither has been implemented or assigned parameters. The newly prepared $K=4$ references have not been evolved.

## Records and dashboard

T11 remains IN PROGRESS. Reconciled the completed geometric-plan checklist and larger-system milestone without inventing a task ID. Updated registry, progress, active context, cache, implementation details and one canonical edit chunk. Preserved existing historical records.

- [Previous-session transcript](2026-10-10-t11-geometry-transcript.md)
- [Current-session transcript](2026-10-11-t11-hamiltonian-transcript.md)
- [Hamiltonian write-up with both dialogs](../../notes/hamiltonian-studies.md)
- [Size-comparison results](../../results/t11-size-comparison/README.md)
- [FL diagnostics](../../results/t11-geometric-interpretation/README.md)

Dashboard records and deployment evidence will be appended after verification. Scientific scripts/results remain uncommitted in this research checkout; deployment uses a separate website checkout.


<a id="dashboard-deployment-and-acceptance"></a>

## Dashboard deployment and acceptance — 2026-10-11 11:07:11 IST

- Published website commits `09b329d9466891a308b50d828591fb914cf1f83e` and final `cea6ae9ff49968d373a6ea439eba5557f29d6754` to `space-cadet/website` main from an isolated `/tmp/t11-website-deploy` checkout. The user's active vocabulary-preview checkout was preserved. Research-repository changes remain uncommitted.
- GitHub Actions deployment succeeded: [initial run 38113477145](https://github.com/space-cadet/website/actions/runs/38113477145), [final run 38113563387](https://github.com/space-cadet/website/actions/runs/38113563387). No PR was created.
- [Live dashboard](https://quantumofgravity.com/projects/scattering-in-lqg/numerics/?v=cea6ae9) contains 20 studies, 28 run/study records and 33 figures. T11 filtering shows three records, including the new persistence and FL-diagnostics studies.
- Verified all 235 public catalogue asset URLs successfully, live catalogue equality with packaged JSON, and byte equality for six reports/summary CSVs. Saved [HTTP verification](2026-10-11-t11-dashboard-verification.json). Local checks also covered 235 URLs, source/export hashes, Python/JavaScript syntax, and changed-file whitespace (preserving CSV CRLF). All 40 previously saved output hashes match.
- Browser verification: both new study cards visible, five-site plot and corrected graph illustration loaded, FL numerical table rendered, no observed console errors. Five-site README and summary downloaded successfully and matched the original source bytes. Saved [live screenshot](../screenshots/2026-10-11-t11-dashboard-live.png).
- Reports are served as `.txt` downloads with original source names; two historical Memory Bank downloads use `study-records/` to avoid deployment exclusions. Scientific calculations and historical figures were not rerun.

T11 remains IN PROGRESS. The proposed geometric Hamiltonian term and prepared-$K=4$ evolution remain pending.


## Candidate Hamiltonians and prepared-FL evolution — 2026-10-11 13:52:01 IST

The follow-up tested two explicit additions to the four-site $K=4$, total-spin-zero baseline: a positive RS-volume term $g_VV_{\mathrm{RS}}$ and an oriented triple-grasp term $\lambda_\chi Q_\chi$. The complete graph models tetrahedral face adjacency with equal hopping strengths; the ring is retained only as a sparse-hopping control. On this closed four-face space, $Q_\chi=4q_{012}$ and $V_{\mathrm{RS}}=2\gamma^{3/2}\sqrt{|Q_\chi|}$, with operator residual below $10^{-15}$. The two terms therefore probe related grasp information; the signed term also selects orientation. This identity does not derive a physical interaction.

The static scan covers 62 parameter settings: complete-graph runs at $U/t=0,1,5,20$ and dimensionless candidate couplings $\alpha=-2,-1,-0.5,0,0.5,1,2$, plus ring positive-volume controls at $U/t=5,20$ and $\alpha_V=-1,0,1$. Five equal-input-area FL references ($x=1/\sqrt3$, $\varphi=90^\circ,60^\circ,30^\circ,10^\circ,0^\circ$) were each evolved under the baseline, both signs of the volume term, and both signs of the signed-grasp term at $U/t=5,20$: 50 trajectories. Exact spectral phases were used. Readouts include return probability, area and active-face statistics, angular correlations, positive volume, and signed grasp; norm, energy, total area, and singlet closure were checked.

The independent verifier completed 1,510 checks with maximum residual $1.07\times10^{-12}$. For the complete graph at $U/t=20$, baseline ground mean volume is 0.033487 project units; the $\alpha_V=-1$ and $+1$ ground values are 0.601241 and 0.031332. Either sign of $H_\chi$ gives 0.601235, while reversing the coupling reverses the preferred grasp orientation. At $\beta t=10$, thermal means are 0.400087 (baseline), 0.601213 ($\alpha_V=-1$), 0.031424 ($\alpha_V=+1$), and 0.596491 for either signed-coupling sign. Full conventions, dynamics sampling, tables, and output files are in the [candidate-Hamiltonian report](../../results/t11-candidate-hamiltonians/README.md); the focused $H_V$ scan is in the [volume-coupling report](../../results/t11-volume-coupling/README.md).

The numerical dashboard was subsequently redeployed from website commit `f59a2ccd4e3b47edd91e1c974dd3eb4b20ed8c98` by workflow `38124134232`. The live catalogue contains 21 studies, 29 records, and 38 figures. All 30 newly published T11 file and figure URLs returned HTTP 200, and the four compressed data hashes match the packaged sources. Browser review showed the new candidate card, eight-row table, five figures, and October 11 date. T11 remains IN PROGRESS: the candidate parameters are not physically derived, volume remains in project units, and controlled size scaling and sewn dynamics remain open. Research-repository changes are still uncommitted; website publication is a separate website commit.

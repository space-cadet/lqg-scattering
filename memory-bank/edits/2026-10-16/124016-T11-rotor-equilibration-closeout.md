---
kind: edit_chunk
id: t11-rotor-equilibration-closeout-20261016
created_at: 2026-10-16 12:40:16 IST
task_ids: [T11]
source_branch: main
source_commit: 2dcb47d02b345b199a5fc4456e90841626031b4c
---

#### 12:40:16 IST - T11: Record equilibration and rotor studies

- Created `code/python/t11_equilibration.py` - Added the finite-area face-channel equilibration pilot.
- Created `code/python/lqg_scattering/classical_rotors.py` - Added reusable classical linear-rotor dynamics and diagnostics.
- Created `code/classical/rotors.cpp` - Added the compiled classical stepping and constrained-sampling kernel.
- Created `code/python/t11_classical_rotors.py` - Added fixed-packet and fixed-density ring production runs.
- Created `code/python/analyze_t11_classical_rotors.py` - Added grouped summaries and equilibrium-reference analysis.
- Created `code/python/verify_t11_classical_rotors.py` - Added independent rotor-history audits.
- Created `code/python/t11_few_rotors.py` - Added the exact pair benchmark and few-rotor controls.
- Created `code/python/t11_rotor_coupling_scan.py` - Added the larger-ring coupling scan.
- Created `code/python/extend_t11_rotor_coupling.py` - Added long-time, half-step and neighboring-ratio controls.
- Created `code/python/check_t11_rotor_delayed_transfer.py` - Checked release beyond the primary observation window.
- Created `code/python/check_t11_rotor_physical_time.py` - Compared direct coupling cases over matched physical-time windows.
- Created `code/python/analyze_t11_rotor_coupling.py` - Added crossover and delayed-release summaries.
- Created `code/python/verify_t11_equilibration.py` - Independently checked the small-area channel pilot.
- Created `code/python/test_classical_rotors.py` - Added focused classical-rotor regression checks.
- Created `code/python/test_few_rotors.py` - Added focused few-rotor regression checks.
- Created `code/python/test_rotor_coupling.py` - Added focused coupling-scan regression checks.
- Created `code/python/plot_t11_classical_rotors.py` - Added the classical ring figures.
- Created `code/python/plot_t11_few_rotors.py` - Added the planar-pair and few-rotor figure.
- Created `code/python/plot_t11_rotor_coupling.py` - Added the coupling and delayed-release figure.
- Created `results/t11-equilibration/` - Saved channel-pilot protocols, compact summaries and validation outputs; the full dynamics CSV remains local and git-ignored.
- Created `results/t11-classical-rotors/` - Saved ring summaries, microcanonical references and validation outputs; full per-run arrays remain local and git-ignored.
- Created `results/t11-few-rotors/` - Saved planar-pair and three-dimensional control summaries; full per-run arrays remain local and git-ignored.
- Created `results/t11-rotor-coupling/` - Saved coupling summaries, follow-up protocols and crossover analyses; full per-run arrays remain local and git-ignored.
- Created `figures/t11-classical-rotors/` - Added the rotor dynamics and size-comparison figures.
- Created `figures/t11-few-rotors/` - Added the pair-transfer and few-rotor figure.
- Created `figures/t11-rotor-coupling/` - Added the crossover and delayed-release figure.
- Created `notes/classical-rotor-equilibration.md` - Recorded the model, equilibrium test, results and quantum continuation.
- Created `notes/few-rotor-energy-transfer.md` - Derived the aligned planar-pair transfer threshold and documented controls.
- Created `notes/rotor-coupling-crossover.md` - Recorded the scaled coupling scan and delayed release.
- Created `notes/equilibration-session-note-map.md` - Mapped existing note homes and the new pedagogical narrative.
- Created `memory-bank/sessions/2026-10-16-equilibration-and-rotors-summary.md` - Preserved the physics handoff.
- Created `memory-bank/sessions/2026-10-16-equilibration-and-rotors-transcript.md` - Preserved the conversation transcript.
- Created `memory-bank/sessions/2026-10-16-equilibration-and-rotors-transcript.json` - Preserved transcript text and timestamps.
- Modified `notes/numerical-studies.md` - Added NS33–36 for the channel and rotor studies.
- Modified `notes/README.md` - Indexed the three rotor notes.
- Modified `code/python/dashboard_assets/build_research_catalogue.py` - Added curated channel and rotor catalogue entries and omitted raw histories from packaged copies.
- Modified `code/python/dashboard_assets/export_numerical_data.py` - Added corresponding numerical fields and exports.
- Modified `code/dashboard/` - Regenerated the 30-study, 39-dataset local catalogue with selected rotor/channel rows and packaged figures; excluded raw trajectory histories.
- Modified `notes/t9a-singlet-exchange.md` - Clarified that full pilot arrays stay local while the dashboard uses compact summary tables.
- Modified `notes/thermal-geometry-and-singlet-exchange.md` - Linked the curated canonical control table instead of full dashboard trajectory exports.
- Modified `memory-bank/tasks/T11.md` - Recorded the new numerical scope, findings and open quantum continuation.
- Modified `memory-bank/tasks.md` - Refreshed the registry timestamp; T11 remains in progress.
- Modified `memory-bank/activeContext.md` - Set T11 as the current research focus and recorded dashboard build status.
- Modified `memory-bank/session_cache.md` - Added the study results and closeout links.
- Created `memory-bank/sessions/2026-10-16-t11-numerics-closeout.md` - Recorded the session and local catalogue status.
- Modified `.gitignore` and result READMEs - Kept large raw trajectories on disk while excluding them from Git; retained compact summaries and protocols.
- Modified `memory-bank/ui-tests/2026-10-16-numerics-dashboard-refresh.md` and added two screenshots - Recorded hosted publication and browser acceptance for the curated package.

---
kind: edit_chunk
id: 20261009-205604-t11-k4-thermal-crossover
created_at: 2026-10-09 20:56:04 IST
task_ids: [T11]
source_branch: main
source_commit: 379d59288f01cf75ad360de3e667760f56552204
---

#### 20:56:04 IST - T11: Resolve the K=4 thermal-volume crossover
- Modified `code/python/hamiltonian_studies.py` - Added dense K=4 Gibbs scans, energy-eigenspace volume summaries, and graph-difference/crossover figures.
- Modified `results/hamiltonian-studies/` - Regenerated the 30-system outputs and added dense scan tables and five PDF/PNG figure pairs using qc-diff.
- Updated `results/hamiltonian-studies/README.md` and `notes/hamiltonian-studies.md` - Recorded the reproduction environment, low-temperature analysis, and finite-size claim limits.
- Updated `memory-bank/tasks/T11.md`, `memory-bank/tasks.md`, `memory-bank/activeContext.md`, `memory-bank/progress.md`, `memory-bank/session_cache.md`, and `memory-bank/changelog.md` - Recorded the K=4 crossover results and remaining scope.
- Updated `memory-bank/sessions/2026-10-09-lattice-hamiltonian-session-summary.md` - Appended the follow-up results while preserving prior session history.

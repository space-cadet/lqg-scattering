---
kind: edit_chunk
id: 20261010-011419-python-library-backend-status
created_at: 2026-10-10 01:14:19 IST
task_ids: []
source_branch: main
source_commit: 379d59288f01cf75ad360de3e667760f56552204
---

#### 01:14:19 IST - Cross-cutting: Record Python library and backend status
- Created `code/python/lqg_scattering/` and rewired shared imports in `code/python/` - Added reusable basis, state, geometry, observable, and volume modules while retaining selected root files as compatibility facades and leaving study-specific logic in its drivers.
- Created `code/python/pyproject.toml`, shared requirements files, and extraction checks - Added package metadata and separated pinned numerical dependencies from optional visualization dependencies; final package/build verification remains deferred.
- Created `code/benchmarks/` and `results/python-vs-ts/` - Saved Python references, the `ts-quantum` adapter benchmark, matched K=2 results, and method/limitation documentation.
- Updated `memory-bank/techContext.md` - Documented the `lqg_scattering` package, dependency split, compatibility facades, incomplete extraction, and limits of the saved Python-versus-TS benchmark.
- Updated `memory-bank/tasks/T11.md` - Recorded the K=2-only matched backend comparison without changing T11's scientific scope or status.
- Updated `memory-bank/tasks/T1a.md`, `memory-bank/tasks/T6.md`, and `memory-bank/implementation-details/` - Changed canonical implementation paths to package modules and retained the root facade roles.
- Updated `memory-bank/activeContext.md`, `memory-bank/progress.md`, `memory-bank/session_cache.md`, and `memory-bank/changelog.md` - Recorded the Python-plus-Rust decision, incomplete extraction, deferred final testing/build, corrected T10 status, and next-session handoff.
- Created `memory-bank/sessions/2026-10-10-python-library-and-backend.md` - Summarized the T10/T11 work carried forward, benchmark scope, extraction state, prior checks, and open research questions.
- Updated `memory-bank/edit_history.md` - Added the canonical edit-chunk entry while preserving earlier dated records.

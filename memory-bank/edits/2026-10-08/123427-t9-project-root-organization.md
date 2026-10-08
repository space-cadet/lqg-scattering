---
source_branch: main
source_commit: 5a6aaefac3e841d18e2a8a99e158597deeb09a26
---

#### 12:34 IST - T9: Organize project root and calculation records
- Moved saved calculation JSON files from the root into `results/` and added an index.
- Moved experiment logs into `notes/experiments/`, task prompts and the paper overview into `notes/task-specifications/`, and added a notes index.
- Updated Python/Rust output locations, the T5e run recipe, dashboard input paths, and active Memory Bank references.
- Flattened the dashboard application from `code/dashboard/dashboard/` to `code/dashboard/` so source paths and generated asset paths agree.
- Added `.DS_Store` to `.gitignore`; retained the existing local cache and browser-state directories.

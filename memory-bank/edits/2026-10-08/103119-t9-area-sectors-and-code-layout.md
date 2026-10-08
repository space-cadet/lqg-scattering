---
source_branch: main
source_commit: 5a6aaefac3e841d18e2a8a99e158597deeb09a26
---

#### 10:31:19 IST - T9/T1a/T3c: Document thermal sectors and organize project source
- Created `notes/thermal-area-sectors.md` - Explained occupation coefficients, sector multiplicity, reduced-state construction, and the distinct canonical-area weighting.
- Created `memory-bank/sessions/2026-10-08-thermal-area-coefficients-transcript.md` - Preserved the discussion through the multiplicity explanation, stopping before the write-up request.
- Created `code/thermal/plot_vacuum_coefficients.py` and `figures/thermal-area-sectors/` - Added the exact four-face squeezed-vacuum plot, data, and run summary with normalization, mean, tail, and minimal-cutoff checks.
- Moved Python, Rust, dashboard, Memory Bank tooling, shell workflows, and LaTeX sources/assets under `code/`; kept compiled paper PDFs under `paper/` and repaired path references and run guidance.
- Updated T9 context and noted that fixed positive total-area Gibbs weights on unrestricted Fock space have a vacuum low-temperature limit, unlike the selected nonzero-$J$ squeezed family.

# UI Test Session: quantum and geometric T11 dashboard records

- **Date:** 2026-10-16 IST
- **Local URL:** `http://127.0.0.1:8767/`
- **Scope:** Dashboard integration and local acceptance for NS37–NS40

## Data and package checks

- Dashboard schema and asset validation: 42 datasets, 2,648 overview and
  numerical rows, 698 links, and 364 package hash checks; PASS.
- Source parity: 2,598 numerical rows and 36,640 numeric values match saved
  source records; 344 original-source SHA-256 hashes match; PASS.
- NS37 reconstructs as two accepted cutoff-10 cases with one figure.
- NS38 has 30 curated transition and size-control rows. Its source contains no
  figure directory, so the dashboard presents its 18-point chart and table.
- NS39–NS40 has 54 summary rows, 18 chart series, 270 selected geometry
  samples, and two figures. The 5,454-row dynamics history is omitted.
- Packaging uses saved results and existing figures; no physics calculation was
  rerun.

## Browser acceptance

- Desktop at 1,280 × 900: all three study notes and the parent research guide
  render without horizontal overflow. Their KaTeX counts are 30, 44 and 35;
  each has zero math-render errors.
- Mobile at 390 × 844: the three study notes render with zero horizontal
  overflow; document width remains 390 pixels.
- The parent guide's 32 same-origin links resolve locally, including session
  records, experiment and task-specification directories, result notes, and the
  physical-illustration collection. Its dashboard link redirects to the working
  dashboard root.
- Geometry chart renders 54 points across 18 groups. Both geometry figures
  load (2,160 px and 2,130 px wide).
- Browser console: zero errors and zero warnings.
- Python syntax and scoped whitespace checks: PASS.

Screenshots: `../screenshots/2026-10-16-t11-quantum-geometry-desktop.png` and
`../screenshots/2026-10-16-t11-quantum-geometry-mobile.png`.

## Hosted acceptance

- Published from website commit `5220c5df3ffb8beec84c4cee97eee8d749bd1919`;
  [deployment workflow run](https://github.com/space-cadet/website/actions/runs/38899436681)
  completed successfully.
- The live dashboard serves all 42 datasets and the 33-study catalogue. NS37,
  NS38 and NS39–NS40 appear in the selector with 2, 30 and 54 rows,
  respectively.
- The hosted NS39–NS40 view renders its 54-point chart and both figures load at
  2,160 × 1,440 and 2,130 × 1,500 pixels.
- Live layout has no horizontal overflow at 1,280 × 900 or 390 × 844. Browser
  console: zero errors and zero warnings.

Live dashboard: <https://quantumofgravity.com/projects/scattering-in-lqg/numerics/>.

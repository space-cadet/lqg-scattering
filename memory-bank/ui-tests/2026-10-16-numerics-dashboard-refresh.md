# UI Test Session: numerics dashboard refresh

**Date:** 2026-10-16 IST
**Local URL:** http://127.0.0.1:8765/
**Tester:** Codex, playwright-ui-testing workflow

## Objective

Verify the curated catalogue, figure and note links, rotor chart grouping, and
responsive layout before publishing the existing website route.

## Checks

- Dashboard schema, asset/link/hash validation: 39 datasets, 2,559 rows,
  620 links, 314 hashes; PASS.
- Source parity: 2,512 rows and 34,766 numeric values match saved sources; PASS.
- Browser layout: 1,280 x 900 and 390 x 844; no horizontal overflow at either
  width. The rotor chart series dropdown was narrowed on mobile to keep the page
  within the viewport.
- Face activation: all 20 summary rows appeared and the 2,224-pixel key figure
  loaded.
- Late T9 figures: 2/2 entanglement figures and 2/2 closed-projection figures
  loaded. T9a exchange figure: 1/1 loaded. Exported data keeps the summary
  tables and excludes the bulk spectra, input/operator archives and trajectories.
- Rotor charts: grouped ring series separate packet preparation and energy
  scale; few-rotor series separate rotor count and control type; coupling scan
  series separate rotor count and observation/control protocol.
- The note list contains eleven items, including all three rotor reports. The
  chronology includes NS33–NS36 and records finite-time limitations.
- No raw rotor archives, trajectory files, or excluded T9 intermediate arrays
  appear in the curated face/T9/rotor result packages.
- JavaScript syntax, unique run IDs, and `git diff --check`: PASS.

The dashboard rendered without JavaScript errors. The local static server made
one request for `/favicon.ico`, which returned 404; this does not affect the
dashboard page or its assets.

Screenshots: `../screenshots/2026-10-16-numerics-update-t9a.png` and
`../screenshots/2026-10-16-numerics-update-mobile-rotor.png`.

Publication and live-route acceptance are verified after the authorized website
push.

## Hosted acceptance

- Website commit `8599947d6da3cb99f1e509bf1dc6e68065384562` published the curated
  package. Commit `37971d1308a1ae608c46424378413c73e9ea3d47` added no-cache
  dashboard data fetches so returning browsers refresh the overview and dataset
  selector. Both production deploy runs completed successfully:
  `https://github.com/space-cadet/website/actions/runs/38866682872` and
  `https://github.com/space-cadet/website/actions/runs/38867408128`.
- Opened the public route with a cache-busting query after the deploy. The
  picker listed all 39 curated datasets; the overview showed 47 runs, 12 tasks,
  and 49 figures. Face activation, the three rotor studies, and T9/T9a entries
  were selectable.
- Public face-activation page showed 20 cases and loaded its key figure
  (2,224 x 1,804); its explanatory note is linked from the dataset and overview.
- Public coupling-crossover chart showed 64 records with eight separate series
  by rotor count and observation/control protocol. The axes were packet-energy
  to coupling ratio and mean transferred-energy fraction.
- Public T9/T9a datasets contained 86, 125, 85, and 20 curated rows; all six
  referenced figures returned HTTP 200.
- At 390 x 844 and 1,280 x 900, the published chart had no horizontal
  overflow. Screenshots:
  `../screenshots/2026-10-16-numerics-update-live-rotor.png` and
  `../screenshots/2026-10-16-numerics-update-live-desktop.png`.

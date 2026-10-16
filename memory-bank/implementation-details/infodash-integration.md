# InfoDash numerical-study integration

*Created: 2026-10-12 16:32:01 IST*

The local numerical dashboard now includes `code/dashboard/infodash/`, pinned to
InfoDash `80f8a983feb8d33dbdab837fc00c21dc96f25770`. It provides an overview and
30 selectable numerical datasets containing 2,049 rows. The existing catalogue
links each of its 21 studies to the matching dataset. Additional datasets expose
FL sampling, real-plane controls, weighted/input and covariance studies,
regular-area/shape scans, binding, open-state evolution and sewing records.

## Export

`code/python/dashboard_assets/export_infodash.py` reads the saved catalogue and
source CSV/JSON outputs. Six catalogue studies supply numerical summary tables;
the remaining studies use explicitly selected saved record containers. The
candidate dataset uses the complete 62-row model summary rather than the
catalogue's eight-row excerpt. Sampling records cover all 50 prepared-FL
trajectories; full time-series files remain downloads. The excited thermal spin
dataset uses five saved temperature summaries, with the joint probability CSV
available through its artifact links.

The catalogue builder calls the exporter after packaging studies. The exporter
can also run independently with standard-library Python. Each dataset has its
own typed columns, scatter-chart defaults and series controls. Literal dotted
source keys stay in case details rather than becoming ambiguous column paths.
Full-precision numbers remain in the dataset; nonfinite values become `null`.

## Records and artifacts

Parameters and results retain the source's notation and field names. Row IDs
contain the dataset and source row identifier/index; `sourceSelector` identifies
the exact record. Original-source hashes and served-file hashes are separate.
Data and figure paths point to the existing `study-assets/` package. Additional
source artifacts are copied there byte-for-byte. NPZ archives stay downloadable.
Source selectors retain parallel-array indices for the historical perturbation
output. All 27 chronological NS entries are downloadable through the overview.

The exporter records its own revision, dirty-checkout flag, source hash and time.
These fields describe the presentation export. Calculation revisions, dates and
software are copied from saved outputs when present; export metadata does not
replace calculation metadata. Full protocol and verification reports remain
linked, with scalar verification summaries displayed on the first numerical row.
The constructive sewing dataset retains an unassigned task label.

## UI and upstream maintenance

`index.html` adds a native study selector, overview link and catalogue link.
`project-navigation.js` switches datasets with the standard `?data=` query.
The renderer, schema, shared data model and D3/Plot bundles are copied from the
pinned InfoDash commit. `UPSTREAM.json` lists the local additions. The existing
project page retains its catalogue and custom volume views.

The complete `code/dashboard/` package, including the InfoDash directory and
`study-assets/`, is published at
<https://quantumofgravity.com/projects/scattering-in-lqg/numerics/>. Website
commit `8263c95b2250bc724605a71c73f1a13e429b1b3d` deployed successfully in
[workflow 38271093411](https://github.com/space-cadet/website/actions/runs/38271093411).
The live manifest lists 30 datasets with 2,049 numerical rows. All 301 unique
URLs referenced by the packaged dashboard returned HTTP 200. The lqg-scattering
source changes remain uncommitted; no calculation was rerun for publication.
See the [deployment session](../sessions/2026-10-12-infodash-deployment.md).

## Verification

- `node code/python/dashboard_assets/check_infodash.cjs`: all 31 JSON datasets
  (overview plus 30 numerical datasets) validate; 368 links exist and 204 artifact
  hashes match their served bytes.
- `python3 code/python/dashboard_assets/check_infodash_source.py`: all 2,049
  numerical rows and 27,531 numeric values match saved source records.
- Headless Chrome: overview, all 30 datasets/row counts, T11 detail/download/chart,
  390px layout and dataset switching passed; no console errors.
- [UI evidence](../ui-tests/2026-10-12-infodash.md).

## Desktop note reader — 2026-10-13

The deployed dashboard presents documentation links in a full-width reader on
desktop and keeps the expandable inline note panels on mobile. The reader uses
the shared Markdown renderer and KaTeX auto-rendering, preserves links between
packaged notes, and supports chronology anchors such as `#ns01`. Website commit
`3c1edad` deployed the responsive reader; cache-busted app scripts use
`?v=20261013-2`. Live review confirmed all four tabs remain visible and note
content, math, and internal chronology links work. See the [session record](../sessions/2026-10-13-infodash-desktop-note-reader.md).

## Curated publication refresh — 2026-10-16

The live package now includes 30 catalogue studies and 39 selectable datasets.
The curated face-activation result keeps its 20-case summary, key figure, and
note. T9/T9a expose selected summary tables and figures. Rotor exports use
grouped summaries and representative cases with series separated by rotor
count, coupling or energy ratio, and control/observation type. Full trajectory
archives stay local. The local checker reports 620 links and 314 hashes; source
parity covers 2,512 rows and 34,766 numerical values.

Website commit `8599947d6da3cb99f1e509bf1dc6e68065384562` published the content.
Follow-up commit `37971d1308a1ae608c46424378413c73e9ea3d47` set dashboard data
fetches to bypass stale browser cache for the overview and dataset selector.
Both deploys succeeded; the live route lists 39 datasets and shows 47 runs,
12 tasks, and 49 figures. See the [hosted acceptance record](../ui-tests/2026-10-16-numerics-dashboard-refresh.md).

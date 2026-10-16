# Numerics dashboard

The [numerical-studies record](../../notes/numerical-studies.md) is the indexed,
chronological record of the calculations shown here.

Serve this directory as a static site. Its InfoDash page, datasets, figures and
downloads are packaged together, so deployment does not need the repository root.

Regenerate the catalogue after updating saved studies:

```bash
conda run -n qc-diff python code/python/dashboard_assets/build_research_catalogue.py --reuse-history
```

The builder packages saved calculations and plots existing arrays; it does not
rerun scientific calculations. Dashboard JSON converts nonfinite values to
`null` and records hashes of the original sources. Original result files remain
authoritative.

- `index.html`: the shared InfoDash numerical interface.
- `data.json`: overview of saved runs and 42 study datasets.
- `datasets.json` and `datasets/`: 42 selectable datasets, including 33
  catalogue studies and nine supplemental datasets.
- `studies.json`: study descriptions, calculation limits and source manifest.
- `study-assets/`: packaged data, operators, notes, PDFs and figures.
- `figures/dashboard-history/` at the repository root: plots from saved arrays,
  with PDFs, 300-dpi PNGs and source hashes in `plot_summary.json`.

T11 includes four/five-site comparisons, prepared-state geometry, candidate
Hamiltonians, face activation, a finite-area channel pilot, and curated classical
rotor studies. Rotor charts separate rotor count, preparation, coupling or energy
ratio, and control type. Rotor tables use grouped summaries and representative
cases; the large raw rotor histories stay in the research repository. The late
T9/T9a exports include summary tables, provenance and key figures while omitting
bulk intermediate arrays. Source and package checksums are recorded with each
dataset.

The October 16 local update adds NS37 quantum planar-rotor comparisons, NS38
closed/open channel-transition witnesses, and NS39/NS40 exact-singlet area
redistribution with its post-run permutation diagnostic. The geometric chart has
54 compact run summaries in 18 series across size, graph and preparation, plus
270 selected geometry samples. The 5,454-row dynamics history and occupation
state vectors are omitted. The four new research notes are linked in the note
reader; the package remains local and is not published by this workflow.

The website deployment excludes Markdown files, so source notes are packaged as
`.txt` and downloaded with their original `.md` names. The shared dashboard
renders them as Markdown with locally packaged Marked and KaTeX libraries.
Historical Memory Bank study downloads are packaged under `study-records/`.
The source bytes and hashes remain recorded.

## Shared InfoDash interface

Open `index.html`. The four shared tabs show Runs & Studies, Figure Archive,
Charts, and Tasks & Numerical Notes at desktop and mobile widths. The project
notes appear at the top of the last tab; open a note to read its rendered
Markdown, tables, links, images, and LaTeX, or download the original Markdown.
The study selector switches between the overview and each individual dataset,
so every numerical study uses the same interface. Dataset details include saved
values, source selectors, provenance, calculation limits, figures and downloads.

The export includes the 33 catalogue studies and nine additional datasets:
prepared-FL sampling, real-plane controls, shape recovery, weighted input,
regular-area and equal-area shape scans, binding energies, state-space probes,
and sewing. Catalogue tables supply summary rows; saved CSV/JSON files supply
the other numerical rows. The candidate-Hamiltonian dataset includes all 62
model settings, and the sampling dataset lists all 50 trajectories. Face
activation is represented by its 20-case summary. Rotor exports keep compact
grouped/representative samples and figures, with sampling choices and full local
reports linked from the dashboard.

The builder also exports the chronological numerical index and supporting notes
for the dashboard's Tasks & Numerical Notes section. `catalogueDate` records when
a study entered the catalogue; export time, source revision and dirty checkout
state remain separate provenance fields.

Check generated datasets and compare every exported value with its saved source:

```bash
node code/python/dashboard_assets/check_numerical_data.cjs
python3 code/python/dashboard_assets/check_numerical_data_source.py
```

`UPSTREAM.json` records the reusable InfoDash template revision.

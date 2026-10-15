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
- `data.json`: overview of eight historical T3 runs and 35 study datasets.
- `datasets.json` and `datasets/`: the 35 selectable detailed datasets.
- `studies.json`: study descriptions, calculation limits and source manifest.
- `study-assets/`: packaged data, operators, notes, PDFs and figures.
- `figures/dashboard-history/` at the repository root: plots from saved arrays,
  with PDFs, 300-dpi PNGs and source hashes in `plot_summary.json`.

T11 includes four/five-site comparisons, prepared-state geometry, candidate
Hamiltonians, full spectra and thermal data, plus 50 prepared-state trajectories.
Large CSV artifacts are compressed for download; source and package checksums
are recorded with each dataset.

The website deployment excludes Markdown files, so source notes are packaged as
`.txt` and downloaded with their original `.md` names. The shared dashboard
renders them as Markdown with locally packaged Marked and KaTeX libraries.
Historical Memory Bank study downloads are packaged under `study-records/`.
The source bytes and hashes remain recorded.

## Shared InfoDash interface

Open `index.html`. The four shared tabs show Runs & Studies, Figure Archive,
Charts, and Tasks & Numerical Notes at desktop and mobile widths. The eight
project notes appear at the top of the last tab; open a note to read its rendered
Markdown, tables, links, images, and LaTeX, or download the original Markdown.
The study selector switches between the overview and each individual dataset,
so every numerical study uses the same interface. Dataset details include saved
values, source selectors, provenance, calculation limits, figures and downloads.

The export includes the 26 catalogue studies and nine additional datasets:
prepared-FL sampling, real-plane controls, shape recovery, weighted input,
regular-area and equal-area shape scans, binding energies, state-space probes,
and sewing. Catalogue tables supply summary rows; saved CSV/JSON files supply
the other numerical rows. The candidate-Hamiltonian dataset includes all 62
model settings, and the sampling dataset lists all 50 trajectories.

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

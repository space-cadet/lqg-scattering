# Numerics dashboard

Serve this directory as a static site. The study catalogue, plots and downloads
are packaged inside it so deployment does not require serving the repository root.

Regenerate the catalogue after updating saved studies:

```bash
conda run -n qc-diff python code/python/dashboard_assets/build_research_catalogue.py
```

The builder reads existing numerical results and generates historical plots from
their saved arrays. It does not rerun scientific calculations. It exports strict
browser-readable JSON, replacing nonfinite numbers with `null`, while recording
SHA-256 hashes of the original sources. Original result files remain authoritative.

- `studies.json`: study descriptions, limits, summary tables and artifact manifest.
- `research-studies.js`: searchable catalogue, tables and download links.
- `study-assets/`: packaged data, operator archives, notes, PDF and PNG figures.
- `data.json`: run/study records, figure archive and task summaries.
- `figures/dashboard-history/` at the repository root: newly plotted historical
  arrays, with PDF, 300-dpi PNG and source hashes in `plot_summary.json`.

The eight historical T3 runs retain their existing performance charts. Study
records are grouped calculations, not individual-case counts; task completion
is reported separately. The dense Hamiltonian interaction scan remains proposed.

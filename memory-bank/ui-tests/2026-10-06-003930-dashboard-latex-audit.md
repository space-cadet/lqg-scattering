# Numerics dashboard LaTeX audit

- Date: 2026-10-06
- Target: `code/dashboard/index.html` served locally
- Scope: Runs, Figures, Performance, Volume Studies, Theory, run-detail panel, and interactive volume-study controls
- Status: dashboard page exercise completed; final axis-label overlay changes were not rechecked in the browser

## Plan

1. Load the dashboard and wait for data and MathJax.
2. Visit each tab and check for rendered MathJax output and browser errors.
3. Exercise a run-detail row and the volume-study preview controls.

## Results

- Loaded the Runs page and confirmed MathJax rendered the static dashboard formulas.
- Opened Figures, Performance, Volume Studies, and Theory. The figure images loaded; the volume-studies view rendered its equations and six inline charts.
- Selected a run and confirmed its detail panel rendered math in the description.
- Changed the performance chart to a line chart with alternate axes and confirmed the chart rendered.
- Changed the volume preview shape and area label; MathJax rendered the selected values and the preview thumbnails loaded.
- The first browser pass found a MathJax collision when the preview was replaced; the preview now clears its old MathJax output before replacing it, and typesetting is queued to avoid overlapping requests.
- The performance chart initially failed because its Observable Plot bundle had no D3 dependency. Adding the documented D3 dependency fixed the chart; the chart width is also clamped for narrow viewports.
- Follow-up axis-label changes now place MathJax-rendered labels around SVG plots and the performance chart. They have not been rechecked in the browser after those changes.

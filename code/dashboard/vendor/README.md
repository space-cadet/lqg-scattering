# Packaged dashboard libraries

| Library | Version | Source |
|---|---|---|
| D3 | 7.9.0 | https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js |
| Observable Plot | 0.6.17 | https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6.17/dist/plot.umd.min.js |
| Marked | 17.0.1 | https://www.npmjs.com/package/marked |
| KaTeX | 0.16.47 | https://www.npmjs.com/package/katex |

The licenses are included beside each library. D3 loads before Plot; Marked and KaTeX load before `markdown-renderer.js`. All rendering files are served locally, with no CDN request from the dashboard.

These are ordinary static assets. Updating them means replacing the versioned files, licenses, and script references in `index.html`.

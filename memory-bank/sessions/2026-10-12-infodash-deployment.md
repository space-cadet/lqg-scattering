# Session: Publish InfoDash dashboard — 2026-10-12

*Recorded: 2026-10-12 21:08:16 IST*

Published the prepared `code/dashboard/` package from lqg-scattering source
revision `9ef9bba2b34dca1624ae7bc03a16fd73eba38240` to
`space-cadet/website` at `projects/scattering-in-lqg/numerics/`.

- Website commit: `8263c95b2250bc724605a71c73f1a13e429b1b3d`.
- Production workflow: [38271093411](https://github.com/space-cadet/website/actions/runs/38271093411), completed successfully.
- Live dashboard: <https://quantumofgravity.com/projects/scattering-in-lqg/numerics/>.
- The main dashboard page links to InfoDash. All 30 dataset files and six app assets returned HTTP 200; the datasets contain 2,049 numerical rows.
- All 301 unique local dashboard asset URLs returned HTTP 200. No referenced path is excluded by the website deployment rules.

The local schema, source-parity and browser checks are recorded in the
[integration session](2026-10-12-infodash-integration.md). No scientific
calculation was rerun. The lqg-scattering source changes remain uncommitted;
T11 remains in progress.

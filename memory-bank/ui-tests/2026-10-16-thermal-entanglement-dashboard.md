# UI Test Session: thermal entanglement dashboard

**Date:** 2026-10-16 IST
**URL:** http://127.0.0.1:8766/
**Tester:** Codex, playwright-ui-testing workflow

## Objective

Verify the new entropy dataset, shared tabs, figures, and pedagogical note;
record console errors and publication acceptance separately.

## Steps

Test started. Schema, packaged links, source hashes and numerical source parity
are checked by the existing dashboard scripts before browser interaction.

1. Opened the entropy dataset: 86 numerical rows and two figures appeared.
2. Opened its Tasks & Numerical Notes tab and the direct thermal-entanglement
   article. The page rendered 53 KaTeX expressions, zero math errors, and both
   figure images loaded successfully.
3. Saved `memory-bank/screenshots/2026-10-16-thermal-entanglement-note.png`.
4. Asserted visible panels after selecting each of Runs & Studies, Figure
   Archive, Charts, and Tasks & Numerical Notes: all four passed.
5. Opened the overview and the proposed face-growth/energy-sharing note:
   correct heading, no math errors and no console errors.

The initial local page requested an absent root favicon (404). Later
application interactions had zero recorded errors or warnings. No dashboard
JavaScript error occurred. Source checks: 34 datasets, 2,407 schema rows,
512 packaged links, 250 file hashes; all 2,365 source rows / 33,386 numerical
values agree with saved sources. Bounds are available in details; the entropy
table presents nine readable columns.

Publication was blocked by automatic approval review requiring explicit
authorization for uploading research artifacts to the website main branch.
The isolated package is prepared; live browser acceptance is pending.

## Face activation continuation

Verified local face dataset: 20 rows, one figure, direct teaching note; 33 KaTeX
expressions, zero math errors and zero console errors. Visible article figure
loaded; inactive figure/lightbox image elements are hidden. Screenshot:
`../screenshots/2026-10-16-face-activation-note.png`. User chose local-only delivery.

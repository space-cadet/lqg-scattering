# Session: InfoDash desktop note reader — 2026-10-13

*Recorded: 2026-10-13 13:20:14 IST*

The dashboard documentation links now open in a full-width reader on desktop.
The expandable inline note panels remain available on mobile. The change was
published separately in `space-cadet/website` commit `3c1edad` (`fix: use
full-width desktop note reader`); cache-busted app scripts use
`?v=20261013-2`.

Live browser review confirmed all four tabs are visible: Runs & Studies, Figure
Archive, Charts, and Tasks & Numerical Notes. Selecting a document opens the
desktop reader, Markdown content and KaTeX math render, and chronology links
such as NS01 navigate to the matching note entry. The user confirmed the result
works. No numerical calculations were rerun.

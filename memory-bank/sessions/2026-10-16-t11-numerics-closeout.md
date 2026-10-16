# T11 numerical-study and dashboard closeout

*Recorded: 2026-10-16 12:40:16 IST.*

This closeout complements the physics-focused [equilibration and rotor
summary](2026-10-16-equilibration-and-rotors-summary.md). It records the T11
study indexing and the state of the local numerical-dashboard source.

## Numerical studies

The chronology now indexes NS33–36: the small-area quantum channel pilot, the
classical rotor equilibrium comparison, the exact planar-pair/few-rotor
benchmark, and the larger-ring coupling scan. The rotor results use $I=1$ and
zero-total-angular-momentum packets. They distinguish moderate-packet
microcanonical-like spreading from finite-time concentration at high packet
energy. The longer runs show release in some cases that appeared trapped at
$\tau=2000$. The precise release time is step-sensitive, so the observed
crossover is not a permanent cutoff. No quantum rotor evolution was run.

The final study suite passed 56 regression tests. Independent validation of
the coupling histories checked 33,916,477 scalar quantities, with maximum
relative energy drift $7.05\times10^{-5}$. Detailed settings, tables and
figures remain in the physics summary and the three rotor notes.

## Local catalogue package

`build_research_catalogue.py` now defines compact records for the channel and
rotor studies, selecting summary tables and figures while pruning raw trajectory
arrays from packaged result copies. `export_numerical_data.py` has corresponding
field support, and `notes/numerical-studies.md` indexes NS33–36.

The generated local package includes four new catalogue studies and datasets.
It now has 30 catalogue studies and 39 selectable datasets, with 2,512 cases.
The checker passes with 620 links and 314 hash checks; source parity confirms
2,512 rows and 34,766 numeric values. Full per-run archives and the large
equilibration time series remain local and are ignored by Git. Compact summaries
and protocols are versioned. After this local closeout, the curated package was
published and passed hosted checks; see `../ui-tests/2026-10-16-numerics-dashboard-refresh.md`.

## Working state

T11 remains in progress; the quantum rotor continuation is still open. This
record was first written against source commit
`2dcb47d02b345b199a5fc4456e90841626031b4c`; the requested repository commit
was created afterward.

The canonical edit chunk was created. The generated
`memory-bank/edit_history.md` view was left intact because the project database
is absent and rebuilding from the available chunks would omit historical
entries that the current view still contains.

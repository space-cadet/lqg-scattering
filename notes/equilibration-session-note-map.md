# Where to write up the equilibration session

*Recorded: 2026-10-16 11:43:41 IST*

The session's main physical question is now clear: how does an interacting system redistribute energy that initially resides in a few degrees of freedom, and how do coupling strength, system size and observation time affect that redistribution? The rotor calculations answer this question directly. They also give a concrete route back to the original question about energy sharing among face channels.

The existing notes already contain most of the classical account. The most useful next editorial step is to make their physical sequence easier to follow, rather than introduce another competing account of the same calculations. This assessment records where each part belongs; the existing scientific notes have been inspected, not rewritten.

## Existing homes

| Existing note | What it already contains | Recommended role |
|---|---|---|
| [Energy spreading in a classical rotor ring](classical-rotor-equilibration.md) | Mechanical model, initial packets, integration, constrained equilibrium reference, spreading/trapping, two figures and one table | Main pedagogical entry point for this session's rotor work |
| [Why fast rotors exchange little energy](few-rotor-energy-transfer.md) | Exact planar-pendulum reduction, transfer bound, coupling scan, zero-angular-momentum restrictions, generic 3D controls, one figure and two tables | Analytic explanation of the mechanism; introduce it before interpreting the ring's trapping |
| [Coupling strength and the apparent energy-transfer cutoff](rotor-coupling-crossover.md) | Larger-ring scan, dimensionless scaling, operational crossover bands, common-physical-time controls, delayed release, one figure and two tables | The main numerical continuation after the mechanism is understood |
| [Can a large tetrahedron spread its area over more faces?](face-energy-equipartition.md) | Original face/channel question, free FL control, recurrence, many-body precedents, energy definitions and candidate interactions | Bridge from the intertwiner question to the rotor example and back; retain its original free-control results |
| [Heating closed quantum geometry: equilibrium and singlet exchange](thermal-geometry-and-singlet-exchange.md) | Temperature-labelled geometry and the distinct two-polyhedron singlet-exchange model | Cross-reference the rotor lesson in its equilibrium discussion; keep its Hamiltonian and results separate |
| [Small-area interacting FL pilot](../results/t11-equilibration/README.md) | Initial exact singlet-sector channel sweep and its numerical limits | Short methodological appendix or bridge section, not the main evidence for a large tetrahedron |

The published manuscript and thermal-intertwiners manuscript should not be the first home for this exploratory rotor account. The notes permit a connected explanation now, while the quantum calculation and the map back to intertwiner dynamics remain open.

## A pedagogical sequence in your style

The introductions to `code/papers/lqg-amplituhedron.tex` and `code/papers/thermal-intertwiners/thermal-intertwiners.tex` establish the physical problem before introducing the formalism. Each construction is motivated by the next physical question, and equations carry the argument forward. The write-up should follow that pattern.

Begin with the concentrated-energy preparation and the question of redistribution. Explain why recurrence does not settle the issue, and why adding available degrees of freedom is different from increasing occupation at fixed channel count. Then introduce the rotor Hamiltonian and show how orientation-dependent torques change the individual kinetic energies while conserving total energy and angular momentum.

Before interpreting the numerical trapping, derive the two-rotor pendulum. This gives the reader an exact picture of exchange, rotation and the energy-to-coupling ratio. Explain why a zero-total-angular-momentum pair cannot contain one fast and one resting rotor, and why the small three-dimensional controls use an energetic compensating pair instead.

Then show the ring figures and equilibrium comparison. Follow them with the coupling scan and the delayed-release example: this is where the distinction between a finite-time crossover and a permanent cutoff becomes physically visible. End with the quantum Hamiltonian and the additional parameter $\epsilon=\hbar/\sqrt{I\lambda}$ as the motivation for the next calculation.

Use connected prose around the equations. Put the physical conclusion beside the plot or table that establishes it. Collect implementation details, audit counts, source hashes and routine checks in a reproducibility appendix rather than interrupting the argument repeatedly. Keep internal task IDs out of the scientific prose. State the outstanding quantum work once, clearly, without repeating proposal disclaimers throughout.

## Figures already available

All four result figures have vector PDF and 300-dpi PNG versions. Their PNGs were visually inspected during this session. Existing notes embed the figures beside the associated discussion.

| Figure | Files | Placement in the narrative |
|---|---|---|
| Classical spreading and high-energy retention | [PNG](../figures/t11-classical-rotors/rotor-dynamics.png), [PDF](../figures/t11-classical-rotors/rotor-dynamics.pdf) | First comparison of redistribution and persistent concentration; explain the 20-time-unit averaging and logarithmic local-energy maps |
| Rotor-count and preparation scaling | [PNG](../figures/t11-classical-rotors/rotor-scaling.png), [PDF](../figures/t11-classical-rotors/rotor-scaling.pdf) | After defining equilibrium-region residence; distinguish fixed packet from approximately fixed density |
| Exact pair transfer and generic 3D controls | [PNG](../figures/t11-few-rotors/few-rotor-transfer.png), [PDF](../figures/t11-few-rotors/few-rotor-transfer.pdf) | Alongside the pendulum derivation; separate the exact planar bound from the three-dimensional numerical controls |
| Coupling crossover and delayed release | [PNG](../figures/t11-rotor-coupling/coupling-crossover.png), [PDF](../figures/t11-rotor-coupling/coupling-crossover.pdf) | Culminating classical result; distinguish scaled and physical clocks and show that apparent trapping can end |

There is no quantum rotor figure yet. None should be presented as a calculated result before the next session's quantum work.

## Numerical tables already in the notes

Five scientific tables are already present:

1. The classical-ring comparison of measured original-pair energy fraction with $2/N$ and equilibrium-region residence, in `classical-rotor-equilibration.md`.
2. The exact planar-pair maximum transfer versus $T_0/\lambda$, in `few-rotor-energy-transfer.md`.
3. Cold-pair kinetic transfer versus coupling in the four-rotor open chain, in the same mechanism note.
4. Half-response crossover brackets and the persistently-below-1% tail versus ring size, in `rotor-coupling-crossover.md`.
5. Direct coupling dependence at fixed packet energy and common physical-time windows, in the same coupling note.

Retain these tables, their denominators and their observation windows. In particular, cold kinetic-energy fraction, original-pair local-total-energy fraction and probability of residence near equilibrium are different observables and should not be relabelled as one transfer quantity.

## Material that still needs integration

The transcript and handoff preserve four parts not yet integrated into the existing pedagogical narrative: the small-K pilot and its limitations; the resource scaling that motivated changing methods; the FL variational discussion; and the quantum rotor continuation. The first two numerical tables are collected below so the figures and tables needed for that integration are not lost.

The FL discussion should remain a short bridge: exact free U(L) motion preserves the FL coherent family, whereas onsite interactions require a variational approximation or a larger quantum space. It was discussed but not simulated at large area. It should not be inserted into the rotor derivation as if the two phase spaces were identical.

For the quantum continuation, record the rotor Hilbert space, the same orientation interaction, conserved total angular momentum, the distinction between sharp momentum and localized-orientation preparations, and the independent parameters $r$ and $\epsilon$. The full quantum discussion is preserved in the session transcript and handoff. No quantum rotor numerical result exists yet.

## Supplementary table: the initial small-area pilot

The following is the regular-input $K=3$ control, not evidence about a large initial tetrahedron. Entries are the percentage of sampled times in $[20,200]$ lying within the stated 0.05 readout distance of the exact dephased reference. The complete-graph hopping has row-sum normalization $t_{ij}=1/(L-1)$.

| Channels | U=0 | U=1 | U=5 |
|---:|---:|---:|---:|
| 4 | 19.0% | 66.8% | 76.1% |
| 5 | 0.0% | 50.3% | 76.7% |
| 6 | 0.0% | 50.1% | 90.3% |

These data explain the user's decision to move beyond the small-K calculation. Their phase and interaction dependence is part of the record; they do not establish a universal benefit from adding channels.

## Supplementary table: exact-state resource scaling

For the fixed-area singlet space,

$$
d_{L,K}=\frac1{K+1}\binom{K+L-1}{K}\binom{K+L-2}{K}.
$$

| Total area K | 4 channels | 5 channels | 6 channels |
|---:|---:|---:|---:|
| 3 | 50 | 175 | 490 |
| 5 | 196 | 1,176 | 5,292 |
| 10 | 1,716 | 26,026 | 273,273 |
| 20 | 19,481 | 896,126 | 26,883,780 |

At $K=10,L=6$, a single dense complex128 matrix requires approximately 1.195 TB in decimal units. Full diagonalization requires more storage than one matrix. This is a limitation of that dense exact method, not a comparable resource requirement for classical rotor evolution.

## Recommended next edit

Use `classical-rotor-equilibration.md` as the main reading path, with the two specialized rotor notes supplying the analytic and coupling sections. Add a short connection from the existing face-energy note, and preserve the thermal/exchange note as a separate model. Integrate the quantum formulation as the final motivation for the next session, then extend it with actual quantum results when available. A fresh umbrella research note is unnecessary unless you prefer a single merged narrative.

The [full transcript](../memory-bank/sessions/2026-10-16-equilibration-and-rotors-transcript.md) and [detailed handoff](../memory-bank/sessions/2026-10-16-equilibration-and-rotors-summary.md) preserve the chronology and source locations for that edit.

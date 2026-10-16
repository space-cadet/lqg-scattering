# Quantum geometry: a guide to the research notes

The central physical question is how quantum face degrees of freedom form a
closed geometry, how that geometry changes under interactions, and how area,
energy and entanglement are shared. The notes approach this question from
several directions. This page gives a reading route; the
[numerical chronology](numerical-studies.md) gives the dated calculation record.

## Begin with states and geometry

The [published-paper overview](published-paper-overview.md) introduces the
oscillator construction and its relation to scattering data. The
[state-space probes](state-space-probes.md) explain the different bases and
prepared states used in subsequent calculations.

For a geometric picture, begin with [volume studies](volume-studies.md) and
[the geometric interpretation of Hamiltonian states](t11-geometric-interpretation.md).
They connect closure, local areas, flux correlations and positive volume.
The [regular/unequal-shape calculation log](experiments/fl_volume_shape_scan_log.md)
records the associated coherent-state scans. The
[illustration collection](../figures/physical-illustrations/README.md) supplies
visual explanations of the principal models.

## Follow energy and area as they spread

The natural reading sequence is:

1. [Face activation and energy sharing](face-energy-equipartition.md): a
   tetrahedral FL input, additional empty channels, free hopping and recurrence.
2. [Classical rotor equilibration](classical-rotor-equilibration.md): concentrated
   kinetic energy spreading through interacting rotors, with an equilibrium
   comparison.
3. [Few-rotor transfer](few-rotor-energy-transfer.md): the exact planar-pair
   mechanism and the role of zero total angular momentum.
4. [Coupling crossover and delayed release](rotor-coupling-crossover.md): how
   coupling and observation time affect transfer in larger classical rings.
5. [Four quantum planar rotors](quantum-planar-rotor-energy-transfer.md): a
   zero-total-momentum energetic pair and two initially cold receivers.
6. [Hamiltonian connectivity](face-activation-connectivity.md): explicit
   four-to-five-to-six channel transitions with and without geometric closure.
7. [Geometric area redistribution](geometric-area-redistribution.md): actual
   closed-state dynamics with four, six and eight available channels, followed
   by volume, angular and entanglement readouts.

The [Hamiltonian study](hamiltonian-studies.md) supplies the underlying spectral
and operator calculations. The last section of the
[redistribution note](geometric-area-redistribution.md#recovering-face-directions)
sets out the next geometric question: when do the occupied channels support
additional distinct face normals, and how sharply is a classical shape defined?

## Temperature, closure and entanglement

[Heating closed quantum geometry](thermal-geometry-and-singlet-exchange.md)
is the physical entry point: increasing occupation, the role of closure,
projected geometry and exchange between two closed subsystems.

The construction is developed in [thermal area sectors](thermal-area-sectors.md),
including the squeezed-state coefficients and appendices. Its reduced-state
spectrum and entropy are explained in [thermal entanglement](thermal-entanglement.md).
The [two-polyhedron exchange specification](t9a-singlet-exchange.md) records the
implemented Hamiltonian, preparations, currents and reservoir extension.

## Joining and separating geometric systems

[Constructive sewing](constructive-sewing-probe.md) builds invariant triangle,
tetrahedral and joined exterior-boundary tensors. [Binding energy](binding-energy.md)
examines the Hamiltonian comparison between an intact system and a separated
configuration. Sewing a boundary and transferring quanta between independently
closed polyhedra are different constructions; the
[exchange note](t9a-singlet-exchange.md) makes the latter precise.

## Finding calculations and source records

- [Numerical studies](numerical-studies.md): stable NS identifiers, dates,
  findings, programs, result reports and figures.
- [Results directory](../results/README.md): saved data and reproduction records.
- [Numerics dashboard](../code/dashboard/index.html): interactive datasets and plots.
- [Session records](../memory-bank/sessions/): transcripts and detailed handoffs.
- [Experiment records](experiments/): protocols and historical run notes.
- [Original task specifications](task-specifications/): research prompts and scope.

For the October 16 quantum continuation, see the
[session summary](../memory-bank/sessions/2026-10-16-quantum-rotors-and-geometric-redistribution-summary.md)
and [transcript](../memory-bank/sessions/2026-10-16-quantum-rotors-and-geometric-redistribution-transcript.md).
Editorial records such as the [thermal-note reorganization](thermal-area-sectors-reorganization.md)
and [earlier session note map](equilibration-session-note-map.md) explain how
longer discussions were distributed across the notes.

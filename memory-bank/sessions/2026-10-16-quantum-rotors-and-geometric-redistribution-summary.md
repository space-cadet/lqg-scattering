# Quantum rotors and geometric redistribution: session handoff

- Created: 2026-10-16 17:24:17 IST
- Last Updated: 2026-10-16 17:45:49 IST

## Focus and source record

T11: rotor energy transfer, geometric-channel connectivity and exact closed-state
redistribution. T11 remains in progress. This record covers the whole session,
including the earlier model discussion, resource measurements, numerical work,
note organization and the two separately requested sessions.

Source session: `01a1442c-c22a-73c1-b57e-1a72d17818a8`.
The [Markdown transcript](2026-10-16-quantum-rotors-and-geometric-redistribution-transcript.md) contains 51 retained
user/assistant prose messages through the save request. Progress messages are
included; tools, setup instructions and skill expansions are excluded. The
[JSON companion](2026-10-16-quantum-rotors-and-geometric-redistribution-transcript.json) preserves original text and timestamps.
The Markdown copy normalizes math delimiters. This closeout work is recorded
here rather than recursively added to the transcript.

## Physical progression

The session resumed from the [classical rotor handoff](2026-10-16-equilibration-and-rotors-summary.md).
The user corrected the proposed two-rotor continuation: two equal-inertia
rotors at zero total angular momentum necessarily have equal local kinetic
energies. A pair cannot supply an energetic pair and a separate cold receiver.
Three rotors suffice generically, but the aligned planar triangle with momenta
$+p,-p,0$ leaves the third rotor stationary by exact torque cancellation.
Four planar rotors were chosen for the first quantum example.

After quantum transfer was demonstrated, the user redirected the geometric
extension to a prior operator question: can the proposed Hamiltonian connect
exactly four occupied channels to five or more, with and without closure?
That check was completed before the larger geometric dynamics. Available
channel count and simultaneous occupied count were kept distinct; $K=2$
cannot occupy five channels, and $K=3$ can occupy at most six.

## Quantum planar rotor result: NS37

The four-site ring starts in $|m,-m,0,0\rangle$, with $m=2,4$ and
$I=\lambda=\hbar=1$. The initial packet kinetic energies are 4 and 16;
mean total energies are 8 and 20. Momentum eigenstates have uniform angles,
so the classical comparison uses 2,048 independent uniform-angle samples
with identical initial momenta, seed 20261016. This differs from the previous
nearly aligned classical preparation.

Over saved times 10..20, the cold-pair kinetic ratios are:

| Packet energy | Quantum | Classical |
|---:|---:|---:|
| 4 | 59.20% | 48.52% |
| 16 | 6.71% | 5.32% |

Cutoffs 8 and 10 pass the declared stopping criteria. The largest quantum
energy residual is $3.57\times10^{-13}$. The initial classical step check
failed; refinement continued to accepted dt 0.00015625 and 0.000625. The
suite then had 62 tests. The single-rotor entropy is the momentum-marginal
entropy in the exact total-momentum sector.

Sources: [physical note](../../notes/quantum-planar-rotor-energy-transfer.md),
[result report](../../results/t11-quantum-planar-rotors/README.md), and
[comparison figure](../../figures/t11-quantum-planar-rotors/energy-transfer.png).
Reusable core: `code/python/lqg_scattering/planar_rotors.py`; driver,
plotter and tests use `t11_quantum_planar_rotors` / `test_planar_rotors` names.

## Geometric connectivity: NS38

The proposed operator is $H=\alpha\sum_i\mathbf J_i^2-t\sum(E_{ij}+E_{ji})$.
Since $\mathbf J_i^2=n_i(n_i+2)/4$, its diagonal term is the existing onsite
model with $U=\alpha/2$ plus constant $3\alpha N_b/4$. Hopping changes
local spins while preserving total occupation and total SU(2) spin.

At six channels and $K=3$, the full Fock dimension is 12,376 and the singlet
dimension 490. The normalized source $(F_{03}^\dagger)^2F_{12}^\dagger
|0\rangle/\sqrt{24}$ has exact counts $(2,1,1,2,0,0)$. Directed hops
$E_{50}$ and $E_{43}$ give five and six occupied channels; each normalized
Hamiltonian matrix element is $-\sqrt2t$. Closed, highest-weight $J=3$,
and $J=3,M=0$ sources all give the ring second-power norm $4t^2$ into six
channels. The last nonclosed state has zero mean spin but $J^2=12$.

Both ring and complete singlet blocks have rank 90 for $P_5HP_4$ and rank
five for $P_6H^2P_4$. Direct $P_6HP_4$ vanishes. The direct five-channel block
has source nullity 150, so connectivity is not an assertion about every
superposition's first-order amplitude. No-hopping, disconnected receivers,
five-channel and minimum-number controls pass. Independent dictionary ladder
algebra checks 99 quantities, maximum residual $1.99\times10^{-15}$;
the suite then had 67 tests.

See [derivation](../../notes/face-activation-connectivity.md) and
[report](../../results/t11-face-connectivity/README.md). Sources are
`t11_face_connectivity.py`, `verify_t11_face_connectivity.py` and
`test_face_connectivity.py`. Sparse operator/basis archives remain local
under the existing ignored NPZ rule; compact witness records are JSON.

## Resource assessment and sparse implementation

Live hardware check: Apple M2, eight cores, 8 GB RAM. Existing full-space
operator audits took 13.11 s at $L=8,K=3$ and 12.63 s at $L=6,K=4$.
The $L=10,K=3$ construction plus ring/complete sparse evolution through time
20 took 48.75 s (9,075 singlets); measured peak footprint about 3.49 GB.
These are workload-specific local measurements. Benchmark logs are temporary:
`/tmp/face-capacity-benchmark.log` and `/tmp/face-capacity-dynamics.log`.

The user asked whether sparse matrices were actually being used. Clarified:
Hamiltonians, embeddings, spin operators and exponential actions were sparse;
selected connectivity rank blocks were dense. The old larger full-Fock
construction, not a dense time propagator, was the avoidable cost.

The new `channel_dynamics.py` builds only the magnetic $M=0$ basis and projects
one bond at a time into sparse singlet matrices, caching Clebsch-Gordan values.
At $L=8,K=4$, this uses 108,900 magnetic states and 13,860 singlets, avoiding
the 490,314-state full Fock basis. Basis plus geometry construction measured
about 4.2 s. Small dense roots occur only within fixed-local-spin blocks.

## Geometric redistribution: NS39

Completed 54 trajectories at $K=4$, $L=4,6,8$, ring/complete, $\alpha=0,1,5$,
and three preparations. Hopping row sum is one: ring bond 1/2 and complete
bond $1/(L-1)$. Times are 0..20, spacing .2.

Two main states condition regular/deformed FL labels ($\varphi=90,30$
degrees, $x=1/\sqrt3$) onto counts $(2,2,2,2,0,\ldots)$, giving exactly
four spin-one channels. Projection probabilities are 0.06944444 and
0.08083767. A third unconditioned regular FL state is explicitly a separate
occupation-fluctuating control.

For the eight-channel regular sharp state, late-window means are:

| Graph | alpha | Receiver linear-area fraction | Probability active count >=5 |
|---|---:|---:|---:|
| Ring | 0 | 53.0% | 56.8% |
| Ring | 1 | 50.6% | 68.1% |
| Ring | 5 | 25.3% | 30.9% |
| Complete | 0 | 12.4% | 42.0% |
| Complete | 1 | 34.6% | 67.6% |
| Complete | 5 | 12.7% | 20.6% |

Full local-energy readouts allocate half of each hopping bond to each endpoint
and sum to conserved H. They were added as a documented bookkeeping diagnostic
before a final rerun; model cases, criteria and windows were unchanged.
Receiver Casimir-energy ratios are saved separately. At alpha=1, their late
values are 50.77% (ring) and 32.27% (complete).

At five times, save all conditional pair-angle means/SDs and pair-presence
probabilities, positive RS volume/variance/kernel weight, and volume conditioned
on >=5 active channels. Every sampled nonnegligible >=5 component has positive
conditional mean RS volume. This volume sums all vertex triples independently
of the interaction graph, in repository gamma=0.2375 units. It is not the
older connected-induced-triple graph prescription. Single-site entropy includes
spin multiplicity, $S_i=-\sum_n p_i(n)\log[p_i(n)/(n+1)]$.

All 73 tests and 91,476 saved-data/analytic comparisons pass, maximum residual
$6.43\times10^{-12}$. Free FL controls check all 606 frames against analytic
spinor evolution; selected interacting states match magnetic-space evolution.
Numerical outputs are about 5.6 MB, plus under 1 MB of figures. No state-vector
histories or large intermediate operators were retained. The user's storage
instruction is to treat upwards-of-200–500 MB datasets as disposable.

See [physical account](../../notes/geometric-area-redistribution.md),
[report](../../results/t11-geometric-redistribution/README.md),
[area figure](../../figures/t11-geometric-redistribution/area-transfer.png), and
[geometry figure](../../figures/t11-geometric-redistribution/geometry-and-activation.png).
Core: `channel_dynamics.py`; driver/plot/verify names are
`t11_geometric_redistribution`; tests: `test_channel_dynamics.py`.

## Permutation selection rule: NS40

The regular sharp state on the complete graph has all-eight occupation at
numerical zero, while deformed and unconditioned FL states have nonzero
weight there. A post-run symmetry diagnostic explains this result: receivers
begin permutation symmetric; within the all-eight singlet subspace that
requires original-group symmetry. Regular sharp symmetric weight is
$1.06\times10^{-32}$, deformed weight 0.348993. The target identity residual
is $2.95\times10^{-17}$ and the receiver-symmetric target rank is one.
Complete H preserves those permutation sectors; the ring does not impose
the same restriction. This diagnostic followed inspection of NS39 and was
not an additional trajectory scan. Source: `check_t11_channel_symmetry.py`.

## Face-normal discussion and next proposal

The user asked why classical normals could not be checked and whether the
issue was leaving FL coherent states. Clarified that geometry can be examined
relationally despite vanishing singlet mean fluxes. Occupied channels can
share a direction even under exact free FL evolution: on the uniform complete
graph initially empty spinor rows become proportional. The sharp preparations
are coherent intertwiners at fixed local spins; the interaction generally
moves them beyond that family.

The next proposed analysis, not implemented in this session, is:

1. Use exact free-FL label evolution as a known-normal control and combine
   coincident directions when counting geometric faces.
2. Examine saved conditional angular distributions against coherent references
   at the same local spins, rather than equating raw quantum means with
   classical normal cosines.
3. Regenerate a few selected snapshots, resolve dominant occupation sectors,
   and compare coherent intertwiners with candidate normals obeying
   $\sum_i j_i\mathbf n_i=0$. Test overlaps and distribution widths.
4. Increase area first for four/five channels. The present all-eight sector
   has spin 1/2 on every channel, so larger area is needed to assess narrowing
   toward a classical shape. Regenerated snapshots can be discarded.

This proposal is now part of the [geometric note](../../notes/geometric-area-redistribution.md#recovering-face-directions).

## Notes, transcript and separate sessions

The new [parent research note](../../notes/quantum-geometry-research.md) organizes
states/volume, rotor and channel redistribution, thermal/entanglement work,
and sewing/binding. [notes/README.md](../../notes/README.md) points to it.
Related-note links were added across the main notes, the three current study
notes were edited into a connected pedagogical account, and the numerical
chronology now includes NS37–NS40. The transcript preserves historical
statements; the research notes give the updated account. The user explicitly
asked to avoid unnecessary repeated disclaimers; scope distinctions are kept
where they affect the physics, with future work stated positively.

Two separate local sessions were explicitly requested:

- Illustrations: `01a14436-c904-7e11-81ea-6705231c870e`, Luna 6 Extra High,
  owns `figures/physical-illustrations/`. It was started earlier in this session;
  later illustration work is owned by that session.
- Numerics dashboard: `01a1448a-c8eb-7781-855c-093b11a9bafc`, Luna 6 Extra High,
  started during this closeout. It integrated NS37–NS40 and passed local source,
  package and browser acceptance. After the user later explicitly requested
  publication, it deployed website commit `5220c5d` in workflow `38899436681`;
  see the [dashboard acceptance record](../ui-tests/2026-10-16-quantum-geometry-dashboard.md).

## Working state

The earlier dashboard-publication Memory Bank changes were committed separately
by the user. This session preserved the existing untracked `.playwright-mcp/`
artifacts. New research code, data, figures and notes remain uncommitted;
there was no commit or push from this session. The dashboard session was
instructed to update locally without publishing. The user's later deployment
request superseded that instruction. Shared-note ownership was communicated so
it did not overwrite the research closeout.

## T11 ownership split

The umbrella now has four child records: [T11a](../tasks/T11a.md) for fixed-area
Hamiltonian/volume and prepared-FL studies; [T11b](../tasks/T11b.md) for
face-channel activation and interacting equilibration; [T11c](../archive/T11c.md)
for the completed finite-time rotor-transfer pilot; and [T11d](../tasks/T11d.md)
for closed geometric channel connectivity and shape. The [numerical chronology](../../notes/numerical-studies.md)
links NS23–NS27, NS32–NS40 to these owners, while NS25 remains separately
owned by constructive sewing. The parent T11 remains active. Relational
face-normal/coherent-intertwiner analysis is the next geometric step.

Continue with the proposed relational face-direction analysis when requested.
The current completed evidence is rotor transfer, closed/nonclosed operator
connectivity and exact closed geometric-channel redistribution, with the
selection-rule explanation and compact reproducible outputs.

# Session handoff: numerical extraction, binding energy, and constructive sewing

Recorded 2026-10-10. This summarizes the entire session. The separate [physics transcript](2026-10-10-binding-and-constructive-sewing-transcript.md) excludes non-physics messages. No commit or push was performed. Extensive earlier working-tree changes were preserved. This request creates session records only; the task registry, active context, and earlier records are not rewritten.

## User’s intended physics and next starting point

The user wants to investigate binding energies of progressively constructed quantum-geometric objects: a tetrahedron versus its three-face-plus-one-face dissociation channel, then two separate tetrahedra versus two tetrahedra sewn along one triangular face. “Three plus one” retains the fourth face; it does not mean an empty fourth site. Sewing must change the neighboring-face relationships along all three edges of the common triangle.

Their construction starts with Schwinger oscillators on physical polygon edges, joins neighboring edges with invariant F-pair creators, then sews triangle edge copies to build tetrahedra. It is documented in `implementation-details/constructive-geometric-sewing-dialogue.md` and `sessions/2026-10-04-geometric-construction-transcript.md`. Do not replace this construction with a generic eight-face-site hopping model.

The immediate open question is the Hamiltonian on this sewn state space. The last response proposed a gauge-invariant edge-Casimir plus loop-holonomy toy Hamiltonian. The user has not yet accepted it and it has not been implemented. Resume from its physical definition, conserved quantities, and the distinction between an exterior boundary and a retained two-cell bulk. Avoid choosing a binding-favoring interaction solely to manufacture binding.

## Context loaded at the start

The previous session’s T10 positive-face RS catalogue and T1a four-face closed baseline were reviewed. T11 already had exact four-site singlet Bose-Hubbard studies on complete/ring graphs, thermal-volume scans, and dashboard results. T9’s selected squeezed two-copy construction remains separate; full reduced-state geometry/entropy work is open. The old Memory Bank extraction handoff says incomplete; the code extraction was completed during this session, as detailed below.

## Python extraction and numerical infrastructure completed

Reusable code was consolidated into `code/python/lqg_scattering`, with drivers retaining sampling, plotting, and output. Modules added/extracted include `hamiltonian.py`, `volume_blocks.py`, `singlets.py`, `labels.py`, `thermal.py`, and `analysis.py`. Existing compatibility facades and driver contracts were retained. Runtime dependencies and packaging were declared in `code/python/pyproject.toml`; Python/package documentation was added.

Extraction validation: 18 tests passed; 26 pre-extraction operator arrays agreed within $10^{-13}$; all 30 Hamiltonian cases and the variable-face catalogue through K=4 were rerun. Comparisons covered 1,275 saved archive arrays and 12,151 CSV rows. Wheel, sdist, wheel-from-sdist, external installation, imports, and numerical smoke checks succeeded. Earlier logs are in `/tmp/lqg-extraction-tests.log`, `/tmp/lqg-saved-comparison.log`, and associated `/tmp/lqg-extraction-*` artifacts; temporary files may not persist.

The user discussed standardized quantum-library interfaces and an optional QuTiP bridge, but explicitly deferred consolidation. No bridge was implemented.

`hamiltonian.py` now provides `build_fixed_number_model(n_sites,n_bosons,edges)` and `assemble_hamiltonian(model,t,U)` on the full fixed-number basis, including odd-number sectors. Occupation indices use tuples, fixing collisions associated with uint8 keys at occupation 256. `total_spin.py` builds total-spin operators and closure/sector diagnostics for normalized pure states or density matrices. Sector decomposition uses local-occupation/magnetization blocks and an explicit size limit. These additions brought the suite to 28 passing tests and passed installed-package checks.

The state-space audit distinguished exact singlets from general Fock states: zero magnetization does not imply closure. Earlier T5/T7 references can be non-singlets; SU(2)-invariant evolution preserves their closure defects. An incorrect M=0 comment in `t5a_prime.py` and a shadowed `perelomov` definition in `t5a_mag_sweep.py` were identified but not repaired. Do not count them as fixes.

## Initial probes and the interpretation correction

`preparations.py` constructs coherent face products and embeds the existing FL seed in the full basis. `closure_probes.py` ran complete/ring evolution at $t=1,U=5$ for:

- Closed regular FL state at area label 2, four bosons: exact total-spin singlet.
- A single coherent j=1 face, two bosons: total spin one.
- Three coherent j=1/2 faces along regular tetrahedral normals, fourth site empty, three bosons: $P(J=1/2)=2/3$, $P(J=3/2)=1/3$, no singlet.

Spin weights remained conserved. Hopping populated the initially empty site. These results are operator probes, not the requested dissociation comparison. Saved in `results/state-space-probes/summary.json`; definitions and limitations in `notes/state-space-probes.md`.

The assistant initially interpreted Delta H as a difference of mean energies, then corrected it to energy uncertainty. Neither the FL seed, single-face seed, nor missing-face seed is an eigenstate at these parameters. Their energy uncertainties are:

| Seed | Complete | Ring |
|---|---:|---:|
| FL tetrahedron | 3.316624790 | 3.316624790 |
| Single j=1 face | 2.449489743 | 2.000000000 |
| Three faces, fourth empty | 3.316624790 | 2.708012802 |

The user clarified “Think binding energy.” This redirected the calculation to same-number intact and separated systems. Preserve this correction in future discussions; zero expectation is not a zero operator or an eigenstate criterion.

## Binding-energy calculation completed in the face-site model

`code/python/binding_energy.py` compares the intact four-site Hamiltonian

$$H=-t\sum_{(i,j)}(E_{ij}+E_{ji})+\frac U2\sum_i n_i(n_i-1)$$

with the separated Hamiltonian obtained by deleting every hopping edge incident on site 3, retaining all eight oscillator modes and onsite terms. Both have four total bosons and combined total spin zero. Complete-graph separation leaves a triangle; ring separation leaves a three-site chain.

The intact state is the lowest-energy singlet, not the FL seed. The principal separated channel has three bosons in the fragment and one on the isolated face. Both subsystem spins are one-half, coupled to a singlet. The state can remain spin-entangled although the subsystems have no connecting Hamiltonian term. The calculation also checks the two-plus-two sector; one-plus-three has no compatible combined singlet.

$$E_{\mathrm{bind}}=E_3+E_1-E_{\mathrm{tet}}.$$

At $t=1,U=5$:

| Graph | Intact singlet ground | Three-plus-one threshold | Binding energy |
|---|---:|---:|---:|
| Complete | -1.844288770 | -1.075035470 | 0.769253300 |
| Ring | -1.844288770 | -1.049209993 | 0.795078777 |

The user explicitly recognized and confirmed $E_{\mathrm{tet}}<E_1+E_3$. Full-space eigenstate residuals are below $3\times10^{-14}$. The two-plus-two thresholds are respectively 2.000000000 and 3.086755804, higher than three-plus-one. Scans also cover $U/t=0,1,20$. The free-hopping thresholds agree with an independent orbital argument; zero hopping gives zero lowest detachment cost. The suite reached 32 passing tests.

Limits: this is finite graph detachment, with no spatial separation potential or continuum. Connected-fragment occupations fluctuate, including empty sites. The ground state’s tetrahedral geometry was not established. The prepared FL seed’s mean energy lies above these separation thresholds. These energies do not yet apply to the new sewn edge-leg networks.

Files: `notes/binding-energy.md`, `results/binding-energy/summary.json`, `code/python/test_binding_energy.py`.

## Constructive face-edge sewing implemented

`code/python/lqg_scattering/sewing.py` implements normalized triangle tensors from

$$|T\rangle\propto (F^\dagger_{12})^p(F^\dagger_{23})^q(F^\dagger_{31})^r|0\rangle.$$

The edge twice-spins are $(p+r,p+q,q+r)$. The seed $(1,1,1)$ has spin one on each edge, shape 3x3x3, and six nonzero tensor entries. Total local spin annihilates it.

Separate shared-edge copies are sewn with the oriented normalized invariant bra

$$C^{(j)}_{mn}=\frac{(-1)^{j-m}}{\sqrt{2j+1}}\delta_{m,-n}.$$

Copies must carry equal spin; sewing contracts indices instead of adding occupations. Orientation matters, particularly for half-integer spins.

One tetrahedron uses triangles ABC, ABD, ACD, BCD and sews AB, AC, AD, BC, BD, CD. Fully contracted at identity links, the seed evaluates to 1/162, agreeing in magnitude with the Wigner six-j value 1/6 and the six normalized pairing factors. This number is not a norm or energy.

For the exterior of tetrahedra ABCD and ABCE joined on ABC, omit ABC from each boundary. Each remaining three-face patch has open legs AB, AC, BC. Sew these three pairs. The exterior has six faces and nine edges; its dual face graph is a triangular prism. Cross-tetrahedron neighbors are ABD--ABE, ACD--ACE, BCD--BCE. Each open patch has 27 components. Its raw norm is 0.032075014955; normalized patch-to-patch contraction is $1/(3\sqrt3)=0.192450089730$. Direct six-face contraction evaluates to 0.000197993919475 and agrees with sewing the raw patches.

Important scope: this represents the exterior boundary, not all data in a two-cell bulk. Fully sewing all magnetic indices gives a scalar evaluation. `contract_network` therefore also accepts link representation matrices, using $C^{(j)}D^{(j)}(g)$, to retain a nonconstant closed spin-network function. Haar normalization and operator dynamics on this function space were not implemented. The sewing map is not fixed-number unitary evolution of the old face-site Fock space.

Reproduction: `python code/python/sewing_probes.py`. Data: `results/sewing-probes/summary.json`, `results/sewing-probes/tensors.npz`. Explanation: `notes/constructive-sewing-probe.md`. Tests in `test_sewing.py` check local closure, orientation/normalization, Wigner six-j agreement, direct versus patch contraction, holonomy dependence, and invalid sewings. Latest full suite: **38 tests passed**, log `/tmp/lqg-sewing-tests.log`.

Tensor methods avoid expanding the unrestricted product Fock space. Larger spin labels, superpositions, and intermediate contraction ranks will increase cost. The spin-one examples were inexpensive.

## Proposed Hamiltonian: discussion only

The final answer recommended replacing individual boson hopping with coordinated loop moves that respect sewn edge matching and local closure:

$$H_\Gamma=\alpha\sum_e j_e(j_e+1)-\kappa\sum_{c\in\mathcal C_\Gamma}\frac{W_c+W_c^\dagger}{2},\qquad W_c=\operatorname{Tr}\prod_{e\in c}g_e^{\pm1}.$$

This is a toy-model proposal, not a derivation of a gravitational Hamiltonian or an accepted user decision. The edge cost is $n_e(n_e+2)/4$. Ordinary individual leg hopping can violate area matching even when globally SU(2)-invariant. Loop holonomy terms preserve gauge/matching conditions but generally change spin labels and total edge occupation. A fixed-number restriction requires projection and examination of surviving moves. Choice of loop set, coefficients, spin cutoff, common comparison space, and interface interaction remain unspecified.

At fixed spin one on all edges, each trivalent intertwiner is unique; there is essentially one spin-network basis state on each fixed graph. Nontrivial dynamics requires allowing more spin assignments or other degrees of freedom. A spin cutoff is not an exact conserved-number restriction.

Relevant primary sources consulted:

- [Feller and Livine, Quantum Surface and Intertwiner Dynamics](https://arxiv.org/abs/1703.01156): surface-locality and Bose-Hubbard toy dynamics, distinct from the present edge sewing implementation.
- [Bianchi et al., Loop expansion and the bosonic representation](https://arxiv.org/abs/1609.02219): bosonic Gauss and area-matching constraints.

## Continuation checklist

1. Resolve exterior-boundary versus retained two-cell bulk degrees of freedom for the intended binding comparison.
2. Discuss and choose the Hamiltonian with the user; the last loop proposal is unaccepted and unimplemented.
3. Specify conserved resources, representation cutoff, local constraints, and which configurations have equal energy baselines. Removing an interior boundary face is not automatically a physical energy gain.
4. Build an orthonormal, multi-spin physical basis and matrix elements for one tetrahedron before attempting two sewn cells. Verify closure, matching, Hermiticity, and independent small cases.
5. Compare separated and coupled ground energies in a common defined framework. Do not reuse the four-face Bose-Hubbard binding numbers as sewn-network results.

No new chat was automatically created. The user can start the next session by asking to load this summary and the physics transcript.

## Memory Bank closeout — 2026-10-10 03:26:38 IST

The follow-up mem-update synchronized T11, the task registry, active context,
progress, technical/state-space documentation, and the sewing note. It
appended the cache and previous session without deleting historical content.
The historical transcript is unchanged. No dedicated sewing task was created.
One canonical edit chunk records this closeout; no code tests were rerun for
this documentation update. Commit-message generation was requested; no Git
commit or staging was requested.

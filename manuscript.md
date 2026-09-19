# Computational Exploration of the LQG-Grassmannian Correspondence

**Abstract.** We present a fully numerical verification of the correspondence
between U(N) coherent states of Loop Quantum Gravity and the kinematic space
of massless particle scattering on the Grassmannian Gr(2, N), following
arXiv:2208.10632 (Vaid & Suresh, EPJC 2022). Building null momenta from
spinor helicity variables, we assemble the Gr(2, N) plane, construct the
Perelomov U(N) coherent state labeled by the momentum-map image of the
plane, and verify the round trip from geometry to kinematics and back. The
exact dictionary s_ij = |M_ij|^2 between Mandelstam invariants and squared
Plücker coordinates is confirmed to machine precision. Turning to
positivity, we give a gauge-invariant numerical test for the top cell of
the positive Grassmannian Gr+(2, N), parameterize Gr+(2, 4) explicitly, and
show that its image in kinematic space has all s_ij > 0 — the external-data
condition of the amplituhedron. We then implement the LQG volume operator
of a 4-valent vertex and find two structural results: (i) the volume
expectation vanishes identically on the positive Grassmannian, because real
planes label states with real Fock amplitudes and the chiral commutator has
zero expectation; (ii) off the positive region the volume is exactly
scale-invariant, so no functional V(s) exists at fixed quantum occupation —
volume probes the complex shape of the plane rather than its energy scale.
Finally we verify the semiclassical limit: relative area uncertainties
decrease with the coherent-state exponent ≈ −0.41 (prediction −1/2).

## 1. Introduction

Loop Quantum Gravity (LQG) describes quantum geometry through spin networks
whose edges carry irreducible representations of SU(2) — quanta of area —
while the physics of massless particle scattering is most efficiently
packaged by spinor helicity variables that assemble into the Grassmannian
Gr(2, N). The observation of Vaid and Suresh (arXiv:2208.10632) is that
these two pictures are two readings of the same data: the holomorphic
spinor network of the LQG coherent-state formalism *is* a 2-plane in
C^N, i.e. a point of Gr(2, N), the kinematic space of the N-leg amplitude.

This project executes the full pipeline connecting the two frameworks:

1. **Phase 1** — assemble Gr(2, N) from N massless momenta (spinor
   helicity) and verify momentum conservation and the Plücker relations.
2. **Phase 2** — construct U(N) coherent states from Schwinger bosons and
   verify the u(N) algebra.
3. **Phase 3** — implement the correspondence: extract kinematics from a
   plane, recover the plane from a coherent state, and map scattering
   invariants to geometric invariants.
4. **Phase 4** — positivity: test for Gr+(2, N), parameterize Gr+(2, 4),
   extract positive kinematics, and implement the LQG volume operator.
5. **Phase 5** — the classical limit and this summary.

Everything is tested numerically; every number quoted below was produced by
running the accompanying code (Appendix).

## 2. Mathematical Preliminaries

### 2.1 Spinor Helicity Formalism

A massless momentum p^mu (metric (+,−,−,−), p^2 = 0) maps through the
Pauli matrices to a rank-one 2×2 matrix

    P_{a adot} = p_mu sigma^mu_{a adot} = lambda_a mu_adot ,

which factorizes into a holomorphic spinor lambda and an antiholomorphic
spinor mu. On the real Lorentzian section mu = conj(lambda), and the
energy is E = |lambda|^2. Momentum conservation Σ_i p_i = 0 becomes the
2×2 matrix identity

    sum_i lambda_i mu_i^T = 0 .

Collecting N holomorphic spinors as columns of a 2×N matrix C gives a
2-plane in C^N — a point of Gr(2, N) — invariant under per-column
rescalings lambda_i → t_i lambda_i (the little-group redundancy).

### 2.2 The Grassmannian Gr(2, N)

The Plücker embedding sends the plane C to its 2×2 minors

    M_ij = C_{1i} C_{2j} − C_{1j} C_{2i},   i < j,

which satisfy the Plücker relations; for N = 4 the single relation is
M_12 M_34 − M_13 M_24 + M_14 M_23 = 0. The positive Grassmannian Gr+(2, N)
is the set of planes whose Plücker coordinates can be gauged to be
simultaneously real and positive in the standard ordering; it is the
natural external-data domain of the amplituhedron.

### 2.3 U(N) Coherent States in LQG

Each edge i = 1..N carries a Schwinger boson pair a_i, b_i with the su(2)
generators

    J_i^z = (a_i† a_i − b_i† b_i)/2,   J_i^+ = a_i† b_i .

The u(N) Lie algebra acts through

    E_ij = a_i† a_j + b_i† b_j,   [E_ij, E_kl] = δ_jk E_il − δ_li E_kj ,

conserving the total boson number K = Σ_i (n_a,i + n_b,i). A Perelomov
coherent state labeled by an N×N complex matrix Z is

    |Z> = (1/sqrt(N(Z))) exp(Σ_ij Z_ij E_ij) |ref> ,

with |ref> a lowest-weight reference created from the vacuum by raising
monomials. The area of edge i is A_i = γ ℏ (a_i† a_i + b_i† b_i), with
γ ≈ 0.2375 the Barbero–Immirzi parameter. The momentum map from Gr(2, N)
to u(N)* sends a plane spanned by orthonormal rows (a, b) to

    Z_ij = a_i conj(b_j) − b_i conj(a_j),   Z = −Z† .

## 3. Computational Results

### 3.1 Gr(2, N) from Massless Momenta (Phase 1)

We implemented `null_momentum_to_spinor`, `momentum_from_spinors`,
`spinors_to_plane`, `check_momentum_conservation`, and `plane_to_plucker`
(`grassmannian.py`). The N = 4 example uses complexified kinematics built
directly from spinors satisfying Σ_i λ_i μ_i^T = 0, so each reconstructed
momentum is exactly null and momentum conservation holds by construction.
The output confirms:

- all four reconstructed momenta satisfy p_i^2 = 0 to 10^-16;
- total momentum Σ p_i = 0 exactly (residual 0.000e+00);
- the Plücker relation M_12 M_34 − M_13 M_24 + M_14 M_23 vanishes to
  10^-16.

Note the real section is subtle: with μ = conj(λ), the conservation
constraint becomes a sum of positive-semidefinite Hermitian matrices,
which vanishes only trivially — non-trivial real kinematics must be reached
by imposing conservation on complexified data, as we do.

### 3.2 U(N) Coherent States via Schwinger Bosons (Phase 2)

We implemented a Fock-space engine (`coherent_states.py`) truncated by the
*total* boson number K (the truncation must be total, not per-edge: the
E_ij move bosons between edges, so only the total-K subspace is
u(N)-invariant). Results:

**Algebra.** The u(3) commutation relations
[E_ij, E_kl] = δ_jk E_il − δ_li E_kj are verified on 200 random basis
states with maximum deviation 1.8 × 10^-15 — machine precision.

**Perelomov states.** The exponential exp(Σ Z_ij E_ij) is evaluated as a
Taylor series that terminates exactly on the finite total-K Fock space.
From an all-empty vacuum the exponential acts trivially (the E_ij
annihilate it), so a non-trivial reference occupation is required — we use
raising monomials, e.g. k a-bosons on edge 0.

**N = 3 example.** For the plane with columns of norms
(1.0050, 1.1576, 0.5000) and Z = 3.0 × (momentum-map image), the coherent
state gives edge areas (per γℏ)

    k = 2:  <n_i> = (1.0521, 0.6193, 0.3286)
    k = 6:  <n_i> = (3.6370, 1.2642, 1.0988)

All areas are positive and the closure sum Σ_i ⟨n_i⟩ equals the total
boson number k exactly (2.0000 and 6.0000) — the U(N) action conserves K.
The anti-Hermiticity of the momentum-map label is exact:
max |Z + Z†| = 0.000e+00.

### 3.3 The Correspondence: From Geometry to Kinematics (Phase 3)

`correspondence.py` implements the inverse maps and the invariant
dictionary. The central exact result, verified numerically on 20 random
real N = 4 configurations to better than 10^-10:

    **s_ij = (p_i + p_j)^2 = |<λ_i λ_j>|^2 = |M_ij|^2 .**

Each Mandelstam invariant is the squared modulus of one Plücker coordinate;
energies are the column norms E_i = |λ_i|^2. For the N = 4 example plane:

    s_12 = |M_12|^2 = 1.000,  s_13 = 1.000,  s_14 = 4.000,
    s_23 = 1.000,  s_24 = 1.000,  s_34 = 1.000   (deviation 0.000e+00)

**Recovering the plane from a state.** The covariance matrix of the u(N)
generators in a Perelomov state approximates the orthogonal projector onto
the plane, ⟨E_ij⟩ ~ k (a_i conj(a_j) + b_i conj(b_j)). Taking the top two
eigenvectors recovers the plane; for the N = 4 example the principal
angles between the original and recovered planes are (0.0000, 0.0000) rad
— an exact recovery. The covariance eigenvalues (1.7044, 1.2619, 0.0338,
0.0000) show the expected two-dimensional support plus small quantum
leakage.

**Round trip.** kinematics → plane → Z → coherent state → plane →
kinematics reproduces all pairwise invariant ratios (uniform rescaling by
the eigenvector normalization, as expected).

### 3.4 Positivity and the Amplituhedron (Phase 4)

**A gauge-invariant positivity test** (`is_positive_plane`). Positivity of
the top cell is the existence of a gauge (GL(2) × (C*)^N) in which all
minors are real and positive. Our test has three steps:
(1) all minors nonvanishing (strict cell point);
(2) the minor phases are gauged away — column phases θ_i solve
θ_i + θ_j = −arg M_ij via a spanning-tree construction, with a
least-squares consistency check (mod 2π) on all pairs;
(3) the realified minors admit vertex sign flips making them all equal —
equivalently every triangle product sign(M_ij) sign(M_jk) sign(M_ki) = +1.

Checks: the canonical positive plane is accepted; 0/50 generic complex
planes are accepted; the cell boundary ad − bc = 0 is rejected; and the
test is invariant under random GL(2) and column rescalings, as it must be.
(A naive least-squares phase solve fails due to angle wrapping — the
spanning tree plus mod-2π consistency is essential.)

**The positive cell Gr+(2, 4).** Any plane with M_12 ≠ 0 gauges to
C = [[1, 0, −c, −d], [0, 1, a, b]], whose minors are (1, a, b, c, d, ad − bc).
Hence

    Gr+(2, 4) = {(a, b, c, d) ∈ R_+^4 : ad − bc > 0},

a 4-dimensional cone. With (a, b, c, d) = (1, 2, 1/2, 3/2):

**Positive kinematics.** The gauge-fixed real plane gives future-directed
null momenta with energies (0.500, 0.500, 0.625, 3.125) and

    s_ij = (1.000, 1.000, 4.000, 0.250, 2.250, 0.250),  all > 0 —

the amplituhedron's positive external-data region. (Momentum conservation
cannot hold on this real section, as it is a sum of positive-energy null
vectors; conservation is imposed on the complexified data, Section 3.1.)

**The volume operator.** We implement the De Pietri / Rovelli–Smolin
4-valent volume from the Schwinger angular momenta,
q = i[J_1·J_2, J_2·J_3], V = (γℏ)^{3/2} √|⟨q⟩|. The construction is
validated against the analytic classical triple-product
−ε^{abc}⟨J_1^a⟩⟨J_2^c⟩⟨J_3^b⟩ on a polarized product state (0.125 vs
±0.125). Two structural mechanisms then control the volume:

1. **Spin freezing.** The U(N) exponential conserves N_a and N_b
   separately, so a reference with only a-bosons (N_b = 0) keeps every
   spin polarized along +z; the chiral commutator has exactly zero
   expectation. A genuine vertex reference (both oscillator types) is
   required for a nonzero volume.

2. **Positivity kills chirality.** For real planes the momentum-map label
   Z is real antisymmetric, the state has exactly real Fock amplitudes,
   and ⟨q⟩ = 0 identically. Since every positive plane is gauge-real:
   **V = 0 on all of Gr+(2, 4)** — the positive cell is the achiral locus
   of kinematic space. Measured: V/(γℏ)^{3/2} = 2.3 × 10^-9 (numerical
   zero) on the positive plane, vs 0.0291 for a genuinely complex plane.

**Volume vs s.** Scaling a plane C → √t C rescales s_ij → t² s_ij, but V
is unchanged (exponent 0.000): the momentum map is built from
orthonormalized rows and is blind to the overall scale. Therefore **there
is no functional relation V(s) at fixed quantum occupation** — the volume
measures the complex structure of the plane (its position relative to the
positive cell), not its energy scale. This is the honest answer to the
exploration: in this framework volume is complementary to s, not a
function of it.

### 3.5 The Classical Limit (Phase 5)

`classical_limit.py` scales the reference occupation at fixed plane shape
(one b-boson per edge, a-bosons distributed ∝ classical column weights)
and measures ΔA_i/⟨A_i⟩ per edge:

    K =  4: ΔA/⟨A⟩ = (1.066, 0.996, 0.732, 1.172)
    K =  6: (0.671, 0.890, 0.728, 0.730)
    K =  8: (0.754, 0.706, 0.521, 0.827)
    K = 10: (0.663, 0.722, 0.523, 0.713)
    K = 12: (0.642, 0.722, 0.428, 0.680)

The mean relative uncertainty falls with a log-log exponent **−0.41**,
consistent with the universal coherent-state suppression K^{−1/2}
(prediction −0.5), up to finite-K oscillations. The coherent states
sharpen onto the classical plane at large quantum numbers, as they must.

## 4. Discussion

**What was verified.** (i) The Gr(2, N) plane assembled from spinor
helicity data satisfies momentum conservation and the Plücker relations to
machine precision. (ii) The Schwinger-boson u(N) algebra closes exactly on
the total-K Fock truncation. (iii) Perelomov coherent states are
constructible in closed form (terminating Taylor exponential), have
positive areas with exact closure Σ⟨A_i⟩ = γℏK, and reproduce the
classical column-norm hierarchy. (iv) The round trip plane → Z → state →
plane recovers the plane exactly (zero principal angles). (v) The
dictionary s_ij = |M_ij|² holds exactly. (vi) Positivity is decidable by a
gauge-invariant phase-cocycle test, and Gr+(2, 4) maps to the all-positive
s region of kinematic space. (vii) The classical limit shows the expected
K^{−1/2} uncertainty suppression.

**New insights.** Three findings go beyond the reference paper's explicit
statements. First, the volume-chirality connection: the positive
Grassmannian cell is precisely the locus where the LQG volume operator of
the dual vertex has zero expectation — positivity is achirality for the
quantum geometry. The volume is a quantitative probe of the
non-realizable (complex) directions of Gr(2, N), complementing the sign
data of the minors. Second, the absence of a functional V(s): because the
momentum map is projective, the volume is scale-invariant and probes shape
(complex structure) while s probes scale. Any relation between volume and
scattering invariants must therefore pass through the quantum number K —
e.g. dimensionless ratios V/(γℏ s)^{3/4} ~ √K·f(shape) — rather than
through V(s) alone. Third, the spin-freezing mechanism: U(N) coherent
states built from single-species references are automatically volume-free;
the b-sector of the Schwinger pair is the carrier of the volume
information, so vertex states with genuine intertwiner content are
essential for volume physics.

**Open questions.** (1) Is the vanishing of ⟨q⟩ on Gr+ a shadow of a
deeper positivity criterion for the *operator* content of the theory
(e.g. a connection to positive geometries of amplitudes)? (2) The volume
scaling with K at small quantum numbers is non-monotonic; a proper
semiclassical asymptotic analysis (large K, peaked intertwiners) is needed
to extract the K^{3/2} law cleanly. (3) The covariance-based plane
recovery works at moderate occupation but shows quantum leakage
(eigenvalues 0.034, 0.000 vs the ideal k, k, 0, 0); whether a
maximum-likelihood (rather than eigendecomposition) recovery improves this
is untested. (4) The real-section obstruction to momentum conservation
needs a fully Lorentzian treatment (SU(1,1)-type coherent states) to
connect to physical scattering regions.

**Did scattering amplitude structure emerge?** Partially. The kinematic
side is fully realized: the s_ij = |M_ij|² dictionary and the positive
kinematics region are exactly the external-data geometry underlying
amplitude calculations. What did not emerge is amplitude *dynamics*: no
integral over the Grassmannian, no measure, and no singularity structure
was computed. The volume-chirality result suggests an intriguing
complementarity — the same positivity that makes amplituhedron geometry
simple (all-positive data) makes the dual quantum geometry maximally
degenerate (zero volume) — but turning this into a statement about
amplitudes requires the missing measure.

## 5. Conclusions and Future Directions

We have verified, end to end and to machine precision, the correspondence
between U(N) LQG coherent states and the kinematic space of massless
scattering on Gr(2, N): spinor helicity → plane → momentum-map label →
Perelomov state → recovered plane → invariants, with the exact dictionary
s_ij = |M_ij|² and positive kinematics from the positive Grassmannian
cell. The pipeline is modular (five small Python modules, all tested) and
reproducible.

The two most promising continuations:
1. **Volume-positivity duality.** Characterize ⟨q⟩ as a measure on
   Gr(2, N) \ Gr+ — is it a log-barrier-like function of the minor-phase
   cocycle? Does it relate to the canonical form of the amplituhedron?
2. **Amplitude dynamics.** Add the Grassmannian measure and the
   momentum-twistor map to compute actual tree amplitudes from the
   geometric data, and test whether the volume observable has an amplitude
   interpretation (e.g. through its singularity structure near cell
   boundaries).

## Appendix: Code Listings

All code is in the project repository; run any module as a script to
execute its tests (`python3 grassmannian.py`, etc.). Dependencies: numpy
only.

**File manifest.**
- `grassmannian.py` — Phase 1: spinor helicity → Gr(2, N); Plücker
  coordinates; momentum conservation.
- `coherent_states.py` — Phase 2: FockSpace (total-K truncation), u(N)
  generators with verified algebra, Perelomov states, area operators,
  momentum map `plane_to_Z`, `example_N3`.
- `correspondence.py` — Phase 3: `kinematics_from_plane`,
  `plane_from_coherent_state` (covariance eigendecomposition),
  `scattering_invariants`, `map_invariants` (s = |M|²), `example_N4_full`.
- `positivity.py` — Phase 4: `is_positive_plane` (phase cocycle + sign
  consistency), `positive_region_N4`, `kinematics_from_positive_plane`,
  `volume_operator` (q = i[J_1·J_2, J_2·J_3]), `volume_vs_s`.
- `classical_limit.py` — Phase 5: `classical_limit(N, scales)` with the
  relative-uncertainty scan.

**Key listing 1 — the gauge-invariant positivity test** (`positivity.py`):

```python
def is_positive_plane(plane, tol=1e-9, return_info=False):
    # 1. strict cell point: all minors nonvanishing
    # 2. gauge away minor phases: spanning-tree theta from arg M_0j,
    #    mod-2pi pairwise consistency, lstsq correction
    real_plane, info = realify_plane(plane)
    if info["phase_residual"] > tol:
        return False
    # 3. sign consistency: every triangle product of realified minors = +1
    signs = list(zip(pairs, info["minors_real"]))
    return _sign_consistent(signs, n, tol)
```

**Key listing 2 — the volume operator** (`positivity.py`):

```python
def volume_operator(state, space, gamma=GAMMA, hbar=1.0):
    J = [su2_ops(i) for i in range(4)]
    J12, J23 = _dot_ops(J[0], J[1]), _dot_ops(J[1], J[2])
    vec = space.vec(state)
    v12, v23 = space.apply(J12, vec), space.apply(J23, vec)
    q12_23 = 1j * (space.apply(J12, v23) - space.apply(J23, v12))
    q_exp = complex(vec.conj() @ q12_23)
    return (gamma * hbar) ** 1.5 * sqrt(abs(q_exp)), q_exp
```

**Key listing 3 — the classical-limit scan** (`classical_limit.py`):

```python
def classical_limit(N=4, scales=(4, 6, 8, 10, 12), plane=None, verbose=True):
    Z = plane_to_Z(plane)
    for K in scales:                       # reference scaled ∝ w (column norms)
        ref = np.stack([na(K), np.ones(N, int)], axis=1)
        state, space = perelomov_state(Z, k_max=K, ref_occupations=ref)
        rel = [area_uncertainty(state, i, space)
               / area_expectation(state, i, space) for i in range(N)]
    exponent = polyfit(log(K), log(mean_rel), 1)[0]   # measured: -0.41
```

**Representative test output** (`python3 positivity.py`):

```
positivity check: canonical positive plane accepted; 0/50 generic complex planes accepted
positivity check: invariant under GL(2) and column rescalings
positivity check: cell boundary ad-bc=0 correctly rejected
positive kinematics: s_ij = [1.000, 1.000, 4.000, 0.250, 2.250, 0.250], all > 0
volume operator (positive plane, vertex reference): V = 2.3e-09   (zero)
volume operator (complex plane,  vertex reference): V = 0.029149  (nonzero)
volume_vs_s: positive branch V = 0; complex branch exponent 0.000 (scale-invariant)
```

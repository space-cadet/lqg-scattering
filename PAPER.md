# Coherent States and Particle Scattering in Loop Quantum Gravity

**Paper:** arXiv:2208.10632 [hep-th]
**Authors:** Deepak Vaid, Devadharshini Suresh
**Published:** EPJC (2022)
**DOI:** 10.1140/epjc/s10052-022-10701-6

---

## Core Correspondence

The kinematic space for scattering of N massless particles in flat spacetime is the Grassmannian Gr(2,N) — the space of N 2-planes in $C^N$. The U(N) coherent states of Loop Quantum Gravity, which describe semiclassical geometries at a single N-valent vertex, are labeled by elements of the *same* space: Gr(2,N).

This suggests a deep connection between:
- Scattering amplitudes in QFT (spinor helicity formalism, amplituhedron)
- Coherent states of quantum geometry in LQG

## Paper Structure

### I. Introduction
- Two challenges for any quantum gravity theory:
  - (A) Consistent semiclassical limit matching continuum QFT
  - (B) Sufficient particle species/interactions to embed the Standard Model
- LQG has proposals for (B) via preon/helon models (braid excitations of spin networks)
- But (A) — connecting to flat-space QFT scattering — remains out of reach
- This paper: the kinematic space for N-gluon scattering (Gr(2,N)) is the same object labeling U(N) coherent states in LQG

### II. Scattering Amplitudes and the Grassmannian
- **II.1 Spinor Helicity Formalism:**
  - Null momentum p^$\mu$ ↔ 2$\times$2 Hermitian matrix p_{$\alpha$$\alpha$̇}
  - det(p) = p² = 0 for massless particles $\to$ rank-1 matrix
  - p_{$\alpha$$\alpha$̇} = $\lambda$_$\alpha$ $\lambda$̃_{$\alpha$̇} (two 2-component spinors)
  - Reality: $\lambda$̃_{$\alpha$̇} = ±($\lambda$_$\alpha$)*
- **II.2 Grassmannian:**
  - Collect spinor components into two N-vectors: a⃗, b⃗ ∈ $C^N$
  - Lorentz transformations act as SL(2,C) on the pair (a⃗, b⃗)
  - The invariant object is the 2-plane in $C^N$ spanned by {a⃗, b⃗} $\to$ Gr(2,N)
  - Momentum conservation: $\Sigma$ᵢ pᵢ^$\mu$ = 0 ↔ orthogonality condition on the plane

### III. U(N) Coherent States in LQG
- **III.1 LQG Phase Space:**
  - Classical: (h_ab(x), $\pi$^cd(x)) — intrinsic metric + extrinsic curvature
  - Quantum: spin network states — graphs with SU(2) irreps on edges, intertwiners at vertices
- **III.2 Area and Volume Operators:**
  - Area eigenvalues: discrete spectrum ∝ √[j(j+1)]
  - Volume eigenvalues: also discrete, more complex
- **III.3 Schwinger Boson Representation:**
  - Each edge labeled by spin j ↔ pair of harmonic oscillators (Schwinger bosons)
  - a†, b† create spin-up/down components
  - j = ($n_{a}$ + $n_{b}$)/2, m = ($n_{a}$ - $n_{b}$)/2
- **III.4 u(N) Lie Algebra:**
  - For an N-valent vertex: N edges $\to$ N Schwinger boson pairs
  - u(N) generators: $E_{ij}$ = a†_i a_j + b†_i b_j
  - Commutation: [$E_{ij}$, $E_{kl}$] = $\delta$_jk $E_{il}$ - $\delta$_li $E_{kj}$
- **III.5 Spinorial LQG:**
  - Reformulate spin networks in terms of spinors
  - Each edge labeled by a spinor |z⟩ rather than a spin j
  - Area of edge i: $A_{i}$ = $\gamma$ $\hbar$ $\langle z_i|z_i \rangle$ ($\gamma$ = Barbero-Immirzi parameter)
- **III.6 U(N) Coherent States and the Grassmannian:**
  - Perelomov coherent states for U(N): |Z⟩ = $\exp($\Sigma$ᵢⱼ $Z_{ij}$ $E_{ij}$)$ |0⟩
  - Z is an N$\times$N complex matrix
  - Physical states: gauge-invariant under SU(2) at vertex $\to$ Z encodes a 2-plane in $C^N$
  - The 2-plane is precisely an element of Gr(2,N)!
- **III.7 Reality Condition on Momenta:**
  - The reality of the classical geometry imposes conditions on Z
  - Relates to the reality condition $\lambda$̃ = ±$\lambda$* in the scattering picture

### IV. Discussion: Quantum Gravity on the Positive Grassmannian
- **IV.1 Particle Momenta, Area and the Classical Limit:**
  - The area of edge i in the coherent state ↔ momentum of particle i in scattering
  - Classical limit: large areas ↔ high momenta
- **IV.2 Kinematical vs Dynamical Aspects:**
  - This correspondence is kinematical (about state labels), not dynamical (about interactions)
  - Dynamics would require a Hamiltonian/operator connecting different Gr(2,N) elements
- **IV.3 Computational Complexity:**
  - Scattering amplitude calculations involve summing exponentially many Feynman diagrams
  - But final results are simple (Parke-Taylor formula) — suggests hidden structure
  - Maybe quantum geometry calculations have similar simplifications
- **IV.4 A Theory of Quantum Gravity on the Grassmannian:**
  - Speculative: could the positive Grassmannian be the arena for quantum gravity?
  - Amplituhedron program: locality and unitarity are emergent, not fundamental
  - Maybe LQG coherent states on Gr(2,N) could similarly "emerge" spacetime

## Key Equations

**Parke-Taylor formula (MHV amplitude):**
```
$A_{n}$(1+, ..., i-, ..., j-, ..., n+) = $\langle i|j \rangle$⁴ / ($\langle 1|2 \rangle$$\langle 2|3 \rangle$...$\langle n-1|n \rangle$$\langle n|1 \rangle$)
```

**Spinor helicity:**
```
p_{$\alpha$$\alpha$̇} = $\lambda$_$\alpha$ $\lambda$̃_{$\alpha$̇},  det(p) = p² = 0
$\langle i|j \rangle$ = $\epsilon$^{ab} $\lambda$_{ia} $\lambda$_{jb}
```

**Grassmannian:**
```
Gr(2,N) = {2-planes in $C^N$} = GL(2,C) \ Mat(2$\times$N, C) / GL(N,C)
```

**U(N) coherent state:**
```
|Z⟩ = $\exp($\Sigma$ $Z_{ij}$ $E_{ij}$)$ |0⟩,  Z ∈ Mat(N$\times$N, C)
```

**Area expectation:**
```
$\langle $A_{i}$ \rangle$ = $\gamma$ $\hbar$ $\langle z_i|z_i \rangle$ = $\gamma$ $\hbar$ (|a_i|² + |b_i|²)
```

## Open Questions / Research Directions

1. **Dynamical map:** Can one define a natural operator on Gr(2,N) that corresponds to scattering dynamics?
2. **Positive Grassmannian:** The amplituhedron lives in the *positive* part of Gr(2,N). Is there an analogous positivity condition on LQG coherent states?
3. **Volume ↔ what?:** Area corresponds to momentum magnitude. What geometric quantity corresponds to momentum *direction* or helicity?
4. **Multi-vertex states:** This paper treats a single N-valent vertex. How does the correspondence extend to full spin networks with multiple vertices?
5. **Complexity=Volume:** The paper speculates on connections to holographic complexity conjectures. Can this be made precise?

## Potential Computational Explorations

1. **Explicit Gr(2,N) parameterization:** Given N null momenta, compute the corresponding 2-plane in $C^N$. Verify that momentum conservation ↔ orthogonality.
2. **U(N) coherent state construction:** For small N (3,4,5), explicitly construct the Perelomov coherent state and compute area/volume expectation values.
3. **Classical limit:** Show that for large quantum numbers, the coherent state expectation values approach the classical geometry.
4. **Scattering amplitude ↔ geometric observable:** Define a map from kinematic invariants $s_{ij}$ = ($p_{i}$ + $p_{j}$)² to area differences, and check if any amplitude structure emerges.
5. **Positivity conditions:** Explore when a 2-plane in $C^N$ corresponds to "positive" kinematic data (all $s_{ij}$ > 0).

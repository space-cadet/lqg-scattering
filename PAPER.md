# Coherent States and Particle Scattering in Loop Quantum Gravity

**Paper:** arXiv:2208.10632 [hep-th]
**Authors:** Deepak Vaid, Devadharshini Suresh
**Published:** EPJC (2022)
**DOI:** 10.1140/epjc/s10052-022-10701-6

---

## Core Correspondence

The kinematic space for scattering of $N$ massless particles in flat spacetime is the Grassmannian $\mathrm{Gr}(2,N)$ — the space of $N$ 2-planes in $\mathbb{C}^N$. The $U(N)$ coherent states of Loop Quantum Gravity, which describe semiclassical geometries at a single $N$-valent vertex, are labeled by elements of the *same* space: $\mathrm{Gr}(2,N)$.

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
- This paper: the kinematic space for $N$-gluon scattering ($\mathrm{Gr}(2,N)$) is the same object labeling $U(N)$ coherent states in LQG

### II. Scattering Amplitudes and the Grassmannian
- **II.1 Spinor Helicity Formalism:**
  - Null momentum $p^\mu \leftrightarrow 2 \times 2$ Hermitian matrix $p_{\alpha \dot{\alpha}}$
  - $\det(p) = p^2 = 0$ for massless particles $\to$ rank-1 matrix
  - $p_{\alpha \dot{\alpha}} = \lambda_\alpha \tilde{\lambda}_{\dot{\alpha}}$ (two 2-component spinors)
  - Reality: $\tilde{\lambda}_{\dot{\alpha}} = \pm (\lambda_\alpha)^*$
- **II.2 Grassmannian:**
  - Collect spinor components into two $N$-vectors: $\vec{a}, \vec{b} \in \mathbb{C}^N$
  - Lorentz transformations act as $SL(2,\mathbb{C})$ on the pair $(\vec{a}, \vec{b})$
  - The invariant object is the 2-plane in $\mathbb{C}^N$ spanned by $\{\vec{a}, \vec{b}\}$ $\to$ $\mathrm{Gr}(2,N)$
  - Momentum conservation: $\sum_i p_i^\mu = 0 \leftrightarrow$ orthogonality condition on the plane

### III. U(N) Coherent States in LQG
- **III.1 LQG Phase Space:**
  - Classical: $(h_{ab}(x), \pi^{cd}(x))$ — intrinsic metric + extrinsic curvature
  - Quantum: spin network states — graphs with $SU(2)$ irreps on edges, intertwiners at vertices
- **III.2 Area and Volume Operators:**
  - Area eigenvalues: discrete spectrum $\propto \sqrt{j(j+1)}$
  - Volume eigenvalues: also discrete, more complex
- **III.3 Schwinger Boson Representation:**
  - Each edge labeled by spin $j \leftrightarrow$ pair of harmonic oscillators (Schwinger bosons)
  - $a^\dagger, b^\dagger$ create spin-up/down components
  - $j = (n_a + n_b)/2$, $m = (n_a - n_b)/2$
- **III.4 $\mathfrak{u}(N)$ Lie Algebra:**
  - For an $N$-valent vertex: $N$ edges $\to$ $N$ Schwinger boson pairs
  - $\mathfrak{u}(N)$ generators: $E_{ij} = a_i^\dagger a_j + b_i^\dagger b_j$
  - Commutation: $[E_{ij}, E_{kl}] = \delta_{jk} E_{il} - \delta_{li} E_{kj}$
- **III.5 Spinorial LQG:**
  - Reformulate spin networks in terms of spinors
  - Each edge labeled by a spinor $|z\rangle$ rather than a spin $j$
  - Area of edge $i$: $A_i = \gamma \hbar \langle z_i|z_i \rangle$ ($\gamma$ = Barbero-Immirzi parameter)
- **III.6 $U(N)$ Coherent States and the Grassmannian:**
  - Perelomov coherent states for $U(N)$: $|Z\rangle = \exp(\sum_{ij} Z_{ij} E_{ij}) |0\rangle$
  - $Z$ is an $N \times N$ complex matrix
  - Physical states: gauge-invariant under $SU(2)$ at vertex $\to$ $Z$ encodes a 2-plane in $\mathbb{C}^N$
  - The 2-plane is precisely an element of $\mathrm{Gr}(2,N)$!
- **III.7 Reality Condition on Momenta:**
  - The reality of the classical geometry imposes conditions on $Z$
  - Relates to the reality condition $\tilde{\lambda} = \pm \lambda^*$ in the scattering picture

### IV. Discussion: Quantum Gravity on the Positive Grassmannian
- **IV.1 Particle Momenta, Area and the Classical Limit:**
  - The area of edge $i$ in the coherent state $\leftrightarrow$ momentum of particle $i$ in scattering
  - Classical limit: large areas $\leftrightarrow$ high momenta
- **IV.2 Kinematical vs Dynamical Aspects:**
  - This correspondence is kinematical (about state labels), not dynamical (about interactions)
  - Dynamics would require a Hamiltonian/operator connecting different $\mathrm{Gr}(2,N)$ elements
- **IV.3 Computational Complexity:**
  - Scattering amplitude calculations involve summing exponentially many Feynman diagrams
  - But final results are simple (Parke-Taylor formula) — suggests hidden structure
  - Maybe quantum geometry calculations have similar simplifications
- **IV.4 A Theory of Quantum Gravity on the Grassmannian:**
  - Speculative: could the positive Grassmannian be the arena for quantum gravity?
  - Amplituhedron program: locality and unitarity are emergent, not fundamental
  - Maybe LQG coherent states on $\mathrm{Gr}(2,N)$ could similarly "emerge" spacetime

## Key Equations

**Parke-Taylor formula (MHV amplitude):**
$$A_n(1^+, \ldots, i^-, \ldots, j^-, \ldots, n^+) = \frac{\langle i|j \rangle^4}{\langle 1|2 \rangle \langle 2|3 \rangle \cdots \langle n{-}1|n \rangle \langle n|1 \rangle}$$

**Spinor helicity:**
$$p_{\alpha \dot{\alpha}} = \lambda_\alpha \tilde{\lambda}_{\dot{\alpha}}, \quad \det(p) = p^2 = 0$$
$$\langle i|j \rangle = \epsilon^{ab} \lambda_{ia} \lambda_{jb}$$

**Grassmannian:**
$$\mathrm{Gr}(2,N) = \{2\text{-planes in } \mathbb{C}^N\} = GL(2,\mathbb{C}) \backslash \mathrm{Mat}(2 \times N, \mathbb{C}) / GL(N,\mathbb{C})$$

**$U(N)$ coherent state:**
$$|Z\rangle = \exp\left(\sum_{ij} Z_{ij} E_{ij}\right) |0\rangle, \quad Z \in \mathrm{Mat}(N \times N, \mathbb{C})$$

**Area expectation:**
$$\langle A_i \rangle = \gamma \hbar \, \langle z_i|z_i \rangle = \gamma \hbar \left(|a_i|^2 + |b_i|^2\right)$$

## Open Questions / Research Directions

1. **Dynamical map:** Can one define a natural operator on $\mathrm{Gr}(2,N)$ that corresponds to scattering dynamics?
2. **Positive Grassmannian:** The amplituhedron lives in the *positive* part of $\mathrm{Gr}(2,N)$. Is there an analogous positivity condition on LQG coherent states?
3. **Volume $\leftrightarrow$ what?:** Area corresponds to momentum magnitude. What geometric quantity corresponds to momentum *direction* or helicity?
4. **Multi-vertex states:** This paper treats a single $N$-valent vertex. How does the correspondence extend to full spin networks with multiple vertices?
5. **Complexity=Volume:** The paper speculates on connections to holographic complexity conjectures. Can this be made precise?

## Potential Computational Explorations

1. **Explicit $\mathrm{Gr}(2,N)$ parameterization:** Given $N$ null momenta, compute the corresponding 2-plane in $\mathbb{C}^N$. Verify that momentum conservation $\leftrightarrow$ orthogonality.
2. **$U(N)$ coherent state construction:** For small $N$ (3,4,5), explicitly construct the Perelomov coherent state and compute area/volume expectation values.
3. **Classical limit:** Show that for large quantum numbers, the coherent state expectation values approach the classical geometry.
4. **Scattering amplitude $\leftrightarrow$ geometric observable:** Define a map from kinematic invariants $s_{ij} = (p_i + p_j)^2$ to area differences, and check if any amplitude structure emerges.
5. **Positivity conditions:** Explore when a 2-plane in $\mathbb{C}^N$ corresponds to "positive" kinematic data (all $s_{ij} > 0$).

# Research Task: LQG-Grassmannian Correspondence — Full Pipeline

You are working on a research project exploring the correspondence between $U(N)$ coherent states in Loop Quantum Gravity and the kinematic space of massless particle scattering on the Grassmannian $\mathrm{Gr}(2,N)$. This is based on arXiv:2208.10632 (Vaid & Suresh, EPJC 2022).

## CRITICAL INSTRUCTION: Record Everything in a Manuscript

As you work through each phase below, **continuously update a manuscript file** `manuscript.md` in the project root. This is not a summary at the end — it is a living document that you update after every significant finding, computation, or derivation.

Structure the manuscript as:

```markdown
# Computational Exploration of the LQG-Grassmannian Correspondence

## Abstract
[Fill in as results emerge]

## 1. Introduction
[Background from the paper — the Gr(2,N) correspondence]

## 2. Mathematical Preliminaries
### 2.1 Spinor Helicity Formalism
### 2.2 Grassmannian Gr(2,N)
### 2.3 U(N) Coherent States in LQG

## 3. Computational Results
### 3.1 [Subsection per computation — fill in as you go]

## 4. Discussion
## 5. Conclusions and Future Directions
## Appendix: Code Listings
```

After every computation, write up:
- What you computed and why
- The mathematical setup
- The results (with numbers, tables, or figures described)
- What it means physically
- Any surprises or issues encountered

---

## The Full Pipeline

Execute these phases in order. After each phase, update `manuscript.md` with your findings before proceeding.

### Phase 1: $\mathrm{Gr}(2,N)$ from Massless Momenta ✅ (already done in previous session)

The file `grassmannian.py` already exists in the project. It implements:
- `null_momentum_to_spinor(p)`: null 4-vector $\to$ 2-component spinor
- `spinors_to_plane(lambdas)`: $N$ spinors $\to$ $2 \times N$ matrix (element of $\mathrm{Gr}(2,N)$)
- `check_momentum_conservation(plane)`: verify $\sum p_i = 0$
- `plane_to_plucker(plane)`: Plücker coordinates (minors of the $2 \times N$ matrix)
- `example_n4()`: $N=4$ example

**Your task for Phase 1:** Read `grassmannian.py`, verify it is correct, run it, and write up the mathematical foundations in `manuscript.md` (Sections 2.1, 2.2, and the first part of 3.1).

### Phase 2: $U(N)$ Coherent States via Schwinger Bosons

Implement a new module `coherent_states.py`:

1. `schwinger_state(occupations)`: Given a list of $N$ pairs $(n_a, n_b)$ representing Schwinger boson occupations on $N$ edges, construct the corresponding state in the spin-$j$ representation. Each edge $i$ has oscillators $a_i, b_i$ with $[a, a^\dagger] = [b, b^\dagger] = 1$. The state is:
   $$|\{n_a, n_b\}\rangle = \prod_i \frac{(a_i^\dagger)^{n_{a,i}} (b_i^\dagger)^{n_{b,i}}}{\sqrt{n_{a,i}! \, n_{b,i}!}} \, |0\rangle$$

2. `uN_generators(N)`: Construct the $\mathfrak{u}(N)$ Lie algebra generators $E_{ij} = a_i^\dagger a_j + b_i^\dagger b_j$ for $i,j = 1,\ldots,N$. Verify the commutation relations $[E_{ij}, E_{kl}] = \delta_{jk} E_{il} - \delta_{li} E_{kj}$ numerically for small $N$.

3. `perelomov_state(Z, max_occupation)`: Construct the Perelomov coherent state $|Z\rangle = \exp(\sum_{ij} Z_{ij} E_{ij}) |0\rangle$ for a given $N \times N$ complex matrix $Z$, truncated at a maximum total boson number. The vacuum $|0\rangle$ has all edges in the lowest weight state ($j=0$).

4. `area_expectation(state, edge)`: Compute the expectation value of the area operator $A_i = \gamma \hbar (a_i^\dagger a_i + b_i^\dagger b_i)$ for edge $i$ in a given state. $\gamma$ is the Barbero-Immirzi parameter ($\sim 0.2375$ in LQG).

5. `plane_to_Z(plane)`: Given a $2 \times N$ complex matrix representing an element of $\mathrm{Gr}(2,N)$, construct the corresponding $N \times N$ matrix $Z$ that labels the $U(N)$ coherent state. The construction: if the plane is spanned by two orthonormal vectors $(\vec{a}, \vec{b}) \in \mathbb{C}^N$, then $Z_{ij} = a_i b_j^* - b_i a_j^*$ (this is related to the momentum map from the Grassmannian to $\mathfrak{u}(N)^*$).

6. `example_N3()`: For $N=3$, construct an explicit example: pick a 2-plane in $\mathbb{C}^3$, compute $Z$, build the Perelomov state, compute area expectation values, and verify that the areas are positive and satisfy any relevant constraints.

Update `manuscript.md` Section 2.3 and add Section 3.2 with your results.

### Phase 3: The Correspondence — From Geometry to Kinematics

Implement `correspondence.py`:

1. `kinematics_from_plane(plane)`: Given a 2-plane in $\mathbb{C}^N$ (from Phase 1), extract the corresponding $N$ null momenta. This is the inverse of `spinors_to_plane`: from the $2 \times N$ matrix, read off the spinors $\lambda_i$, then reconstruct $p_i = \lambda_i \lambda_i^\dagger$.

2. `plane_from_coherent_state(state, N)`: Given a $U(N)$ coherent state, extract the corresponding 2-plane. This is subtle — for a Perelomov state $|Z\rangle$, the plane is approximately the positive eigenspace of the "covariance matrix" $(Z Z^\dagger)^{1/2}$ or similar. Explore what works.

3. `scattering_invariants(momenta)`: Compute the Mandelstam invariants $s_{ij} = (p_i + p_j)^2$ for all pairs $i,j$.

4. `geometric_invariants(plane)`: Compute geometric quantities from the 2-plane: the Plücker coordinates, the "area" of each edge (norm of the $i$-th column of the $2 \times N$ matrix), and any other natural geometric observables.

5. `map_invariants(s_ij, geometric)`: Explore the mapping between scattering invariants and geometric quantities. For $N=4$, the only independent invariant is $s = (p_1 + p_2)^2 = (p_3 + p_4)^2$. Can you express $s$ in terms of Plücker coordinates or area variables?

6. `example_N4_full()`: Complete $N=4$ example: choose kinematic data $\to$ compute plane $\to$ compute $Z$ $\to$ build coherent state $\to$ compute areas $\to$ map back to kinematics. Verify the round-trip is consistent.

Update `manuscript.md` with Section 3.3.

### Phase 4: Positivity and the Amplituhedron

Implement `positivity.py`:

1. `is_positive_plane(plane)`: Check if a 2-plane in $\mathbb{C}^N$ is "positive" in the sense of the positive Grassmannian. For $\mathrm{Gr}(2,N)$, positivity means all Plücker coordinates are real and positive (after choosing an appropriate gauge).

2. `positive_region_N4()`: For $N=4$, explicitly parameterize the positive region of $\mathrm{Gr}(2,4)$. The positive Grassmannian $\mathrm{Gr}_+(2,4)$ is a 4-dimensional cell. Find explicit coordinates.

3. `kinematics_from_positive_plane(plane)`: For a positive plane, extract kinematic data. Check if the resulting Mandelstam invariants satisfy $s_{ij} > 0$ for all $i,j$ (this is the "positive region" of kinematic space, relevant for the amplituhedron).

4. `volume_operator(state)`: Implement the LQG volume operator for a 4-valent vertex. The volume is related to the commutator of area operators: $V \propto \sqrt{|(A_1 \times A_2) \cdot (A_3 \times A_4)|}$ or similar expressions involving the $\mathfrak{u}(N)$ generators. Compute the volume expectation in a $U(4)$ coherent state.

5. `volume_vs_s(momenta, state)`: For $N=4$, explore the relation between the volume of the quantum geometry and the scattering invariant $s$. Is there a natural functional relationship?

Update `manuscript.md` with Section 3.4.

### Phase 5: Classical Limit and Summary

1. `classical_limit(N, scale)`: For large quantum numbers (large areas), verify that the coherent state expectation values approach the classical geometry. Specifically, check that the relative uncertainty $\Delta A/\langle A \rangle \to 0$ as the area scale increases.

2. Write a comprehensive Discussion section in `manuscript.md` summarizing:
   - What was verified computationally
   - What new insights emerged
   - What questions remain open
   - Whether any scattering amplitude structure emerged from geometric considerations

3. Write Conclusions and Future Directions.

---

## Important Notes

- **Physical correctness is paramount.** Every formula should be checked against the literature or derived from first principles. If you're unsure about a formula, derive it.
- **Numerical stability matters.** Use numpy's complex linear algebra. Avoid naive loops where vectorized operations work.
- **Test everything.** Every function should have a test or example that you actually run.
- **The manuscript is the deliverable.** Code is supporting material. The manuscript should be readable by a physicist familiar with LQG but not necessarily with all the details of this specific correspondence.
- **Commit after each phase.** Use git to track progress.

Begin with Phase 1: read `grassmannian.py`, verify it, and start the manuscript.

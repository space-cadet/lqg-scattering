# Research Task: Entanglement Between Two Polyhedra in the LQG-Grassmannian Framework

## Prerequisites

Read `manuscript.md`, `grassmannian.py`, `coherent_states.py`, and `correspondence.py` from the previous session. These establish the single-vertex U(N) coherent state formalism. Your task is to extend this to **two entangled polyhedra**.

---

## Physical Setup

Consider two polyhedra A and B, each represented as a single vertex in LQG:
- Polyhedron A: N_A-valent vertex with faces labeled i = 1, ..., N_A
- Polyhedron B: N_B-valent vertex with faces labeled j = 1, ..., N_B
- Some faces are **shared** (identified) between A and B — these represent the "interface" between the two polyhedra
- The shared faces carry entanglement between the two vertices

In the LQG Hilbert space, each vertex has a space of intertwiners. The joint state lives in H_A ⊗ H_B. Entanglement between faces means the joint intertwiner state is not a simple product — it encodes quantum correlations between the geometric data (areas, angles) of the shared faces.

---

## The Framework

### Phase 1: Two-Vertex Hilbert Space

1. `two_vertex_space(N_A, N_B, shared_faces)`:
   - Construct the Hilbert space for two vertices with specified shared faces
   - Each vertex i has u(N_i) generators acting on its edges
   - The shared faces are identified: edge k of vertex A = edge k of vertex B for k ∈ shared_faces
   - The joint Hilbert space is a subspace of H_A ⊗ H_B satisfying the identification constraints

2. `intertwiner_basis_two_vertex(N_A, N_B, shared_faces, max_spin)`:
   - Enumerate the basis of gauge-invariant states for the two-vertex system
   - Each basis state is labeled by spins on all edges and intertwiners at both vertices
   - The identification of shared faces imposes matching constraints

### Phase 2: Entangled Coherent States

3. `entangled_perelomov_state(Z_A, Z_B, entanglement_graph, max_occupation)`:
   - Construct a Perelomov coherent state for the **joint** system
   - Z_A labels the geometry of polyhedron A (element of Gr(2, N_A))
   - Z_B labels the geometry of polyhedron B (element of Gr(2, N_B))
   - `entanglement_graph` specifies which faces are shared/entangled
   - The state should be a superposition over the shared-face spin labels:
     ```
     |Ψ(Z_A, Z_B)⟩ = $\Sigma$_{j_shared} c(j_shared) |ψ_A(Z_A; j_shared)⟩ ⊗ |ψ_B(Z_B; j_shared)⟩
     ```
   - The coefficients c(j_shared) encode the entanglement structure

4. `geometric_entanglement(Z_A, Z_B, shared_faces)`:
   - From the coherent state data, compute the **geometric entanglement** between the two polyhedra
   - This is the entanglement inherited from the shared faces
   - Key question: how does the entanglement depend on the relative geometry (areas, shapes) of the two polyhedra?

### Phase 3: Entanglement Entropy

5. `reduced_density_matrix(state, subsystem)`:
   - Trace out one polyhedron to get the reduced density matrix of the other
   - Subsystem = "A" or "B"

6. `entanglement_entropy(rho)`:
   - Compute the von Neumann entropy S = -Tr($\rho$ log $\rho$)
   - Use eigenvalue decomposition for small systems

7. `mutual_information(state)`:
   - Compute I(A:B) = S(A) + S(B) - S(A∪B)
   - This measures total correlation between the two polyhedra

8. `entanglement_vs_geometry(Z_A, Z_B, shared_faces)`:
   - Systematically explore how entanglement entropy varies with:
     - Relative area of shared faces
     - Number of shared faces
     - Shape parameters of the polyhedra
   - Look for any universal behavior (area law? volume law?)

### Phase 4: Physical Interpretation

9. `holographic_dictionary(Z_A, Z_B)`:
   - If the two polyhedra represent adjacent regions of a spatial slice, the shared faces are the boundary between them
   - In holography, entanglement entropy of a region is proportional to the area of its boundary (RT formula)
   - Check: does S(A) ∝ (total area of shared faces)? If not, what's the correction?

10. `tensor_network_structure(state)`:
    - Represent the entangled two-vertex state as a tensor network
    - Each vertex is a tensor, shared edges are contracted indices
    - Explore the connection to MERA, PEPS, or other tensor network architectures

11. `classical_correspondence_limit(Z_A, Z_B, scale)`:
    - For large areas (semiclassical limit), does the entanglement entropy approach a geometric quantity?
    - Compare with the Bekenstein-Hawking entropy-area relation

---

## Manuscript

Continue updating `manuscript.md` (which already exists from the single-vertex work). Add new sections:

```markdown
## 6. Two-Polyhedron Entanglement
### 6.1 Setup: Two Vertices with Shared Faces
### 6.2 Entangled Coherent States
### 6.3 Entanglement Entropy Results
### 6.4 Holographic Interpretation
### 6.5 Connection to Tensor Networks
```

After each phase, write up:
- The mathematical construction
- Key numerical results
- Physical interpretation
- Comparison with known results in holography / quantum information

---

## Performance Considerations

- For large N or high spins, the Hilbert space dimension grows exponentially. Use Rust for:
  - Large matrix operations (reduced density matrix, eigenvalue decomposition)
  - Iterative computations over many parameter values
  - Any O(d³) operations where d = Hilbert space dimension

- Suggested Rust crates: `ndarray` for arrays, `nalgebra` for linear algebra, `rayon` for parallelism

- Python is fine for:
  - Prototyping and small examples
  - Visualization
  - Orchestration

---

## Important Notes

- **Physical correctness first.** Every formula should be derived or checked against literature.
- **Test each phase before proceeding.** Small N (3, 4) examples where you can verify by hand.
- **The manuscript is the primary deliverable.** Code supports the narrative.
- **Commit after each phase.** Track progress in git.
- **Flag any surprising results.** If entanglement entropy does something unexpected, highlight it.

---

## Open Questions to Explore

1. Can two polyhedra be entangled **without** shared faces (e.g., through the bulk)?
2. Is there a maximum entanglement entropy for given total area?
3. Does the entanglement structure encode the spatial distance between the polyhedra?
4. Can this model reproduce any features of the Ryu-Takayanagi formula?
5. What is the role of the Barbero-Immirzi parameter in the entanglement?

Begin with Phase 1. Read the existing code carefully before extending it.

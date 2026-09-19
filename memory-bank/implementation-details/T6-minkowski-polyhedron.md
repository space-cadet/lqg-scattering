# T6 — Minkowski Polyhedron Reconstruction for Vertex Chirality

**Status:** ⬜ PROPOSED (depends on T5a′ kinematic version; full quantum version depends on T5c)
**Priority:** HIGH (sharpens the T5a chirality verdict; tests the kinematic↔quantum correspondence)
**Created:** 2026-09-19

## Motivation

T5a (base + M-sweep) found **no global handedness**: sign-agreement over all <tg-math>\binom{n}{3}</tg-math> triples stays 0.50–0.70. But this used a **crude, all-triples average**. The physics question — *is the vertex chiral?* — should only involve **geometrically neighboring** edge-triples (those bounding a genuine 3-volume). Distant triples dilute the signal with noise.

The problem: "who are the neighbors?" needs a geometry, and the n edges are currently just labeled 0..n−1 by the moment curve (a gauge choice). **Minkowski's theorem** supplies the geometry.

## The Construction (kinematic version — feasible now)

Minkowski existence/uniqueness: facet normals <tg-math>u_i</tg-math> + areas <tg-math>A_i > 0</tg-math> satisfying closure <tg-math>\sum_i A_i u_i = 0</tg-math> determine a unique convex polytope.

**Obstruction (Muse Spark, 2026-09-19):** on the real section, momenta <tg-math>p_i = \lambda_i \lambda_i^\dagger</tg-math> are future-null (code: `grassmannian.py` rejects past-directed, `E >= 0`), so <tg-math>\sum_i p_i \neq 0</tg-math> — no closure. And <tg-math>\langle J_i\rangle = 0</tg-math> identically (N_a/N_b conservation), so the state's own fluxes are degenerate.

**Resolution (Deepak's insight, conceded by Muse Spark):** use the **all-incoming convention**. Assign <tg-math>\varepsilon_i = \pm 1</tg-math> (incoming/outgoing) and set

<tg-math-block>
A_i = E_i = |\vec p_i|, \qquad n_i = \varepsilon_i \,\vec p_i / E_i
</tg-math-block>

Then <tg-math>A_i n_i = \varepsilon_i \vec p_i</tg-math>, so <tg-math>\sum_i A_i n_i = \sum_i \varepsilon_i \vec p_i = 0</tg-math> (physical momentum conservation, all-incoming), with all <tg-math>A_i > 0</tg-math>. **Valid Minkowski input** → a genuine convex "kinematic polyhedron."

## Algorithm

1. **Fix a channel** (the in/out assignment is extra input, not determined by the plane). For n=4: three channels (s: 12→34, t: 13→24, u: 14→23). For n=5: choice of the incoming pair.
2. **Extract momenta** <tg-math>p_i</tg-math> from the plane via the existing spinor map (`grassmannian.py`).
3. **Assign signs** <tg-math>\varepsilon_i</tg-math> per the chosen channel; compute <tg-math>(A_i, n_i)</tg-math> as above.
4. **Verify closure** <tg-math>|\sum_i A_i n_i| < \text{tol}</tg-math> (guard against numerical drift).
5. **Reconstruct the polyhedron** P from <tg-math>\{(A_i, n_i)\}</tg-math> via Minkowski. (Algorithm: this is a convex feasibility / least-squares problem — see "Implementation notes" below.)
6. **Read off adjacency:** edges i, j are neighbors iff facets i, j of P share an edge (equiv., vertices i, j of the dual are connected). **Local triples** = those where facets i,j,k meet at a vertex of P.
7. **Subsetting rule frozen from geometry** (BEFORE looking at q signs — avoids circularity): restrict the chirality analysis to Minkowski-local triples.
8. **Recompute sign-agreement + net χ_V** on the local subset, across ≥50 planes at n=5,6.

## Critical Safeguards (from Muse Spark)

- **Pre-registered subsetting.** The adjacency rule must be fixed from independent geometry BEFORE evaluating q signs. With 10 triples and random signs, some subset always looks coherent; deciding "these are adjacent" after seeing which agree is circular.
- **Channel dependence is a measurement, not a weakness.** The plane doesn't know which legs are incoming. Protocol: fix channel up front, compute adjacency, evaluate coherence, then repeat for all channels and report all. If adjacent-coherence appears in one channel only → kinematic-channel structure, not vertex handedness. If in all channels → much harder to dismiss.

## Honest Caveats (label in any write-up)

- **Kinematic, not quantum.** This is the *kinematic* polyhedron (from momenta), not the *state's own* polyhedron (from quantum fluxes). The measured claim is "triple chirality coheres on kinematic-polyhedron-adjacent subsets" — a real, publishable statement. Identifying it with the quantum vertex's handedness needs the T5c bridge.
- **Temporal-orientation mixing.** The <tg-math>\varepsilon_i</tg-math> mixes energy-flow direction into the spatial normals: outgoing faces get normals anti-aligned with their momentum. Minkowski doesn't care (closure + spanning suffices), but the resulting adjacency is "energy-flow-balanced" adjacency, slightly different from a purely spatial polyhedron. One sentence in the write-up.
- **Full quantum version (T6-complete) requires T5c:** reconstruct the state's own polyhedron from covariances (closure + twist map), then check the two reconstructions agree face-by-face. That agreement would be the strongest evidence the correspondence is geometrically tight.

## Implementation Notes (algorithm for step 5)

Minkowski reconstruction from <tg-math>\{(A_i, u_i)\}</tg-math> with <tg-math>\sum_i A_i u_i = 0</tg-math>:

The support numbers <tg-math>h_i</tg-math> (distance of facet i from origin) must satisfy: the polyhedron <tg-math>P = \{x : \langle x, u_i\rangle \le h_i \ \forall i\}</tg-math> has facet i with normal <tg-math>u_i</tg-math> and area <tg-math>A_i</tg-math>. This is a **convex feasibility / inverse problem**. Practical routes:

- ** scipy.optimize **: minimize <tg-math>\sum_i (\text{area}_i(P(h)) - A_i)^2</tg-math> over support numbers <tg-math>h</tg-math>, where <tg-math>\text{area}_i(P(h))</tg-math> is computed from the convex hull (via `scipy.spatial.ConvexHull` or a small custom halfspace-intersection). Convex in the areas (Alexandrov), so local methods work.
- **Halfspace intersection:** each facet is <tg-math>\langle x, u_i\rangle = h_i</tg-math>; the polyhedron is the intersection of these halfspaces. `scipy.spatial.HalfspaceIntersection` can build it given the normals and a feasible interior point; then facet areas come from the hull.

For n=5,6 (small), either is fast. **Recommendation:** start with a scipy halfspace-intersection + least-squares on support numbers; it's simple and adequate at these sizes.

## Files

- New: `minkowski.py` (reconstruction + adjacency)
- New: `t6_kinematic_chirality.py` (the local-triple analysis)
- Reuses: `grassmannian.py` (spinors/momenta), `coherent_states.py` (Perelomov), existing T5a sweep data

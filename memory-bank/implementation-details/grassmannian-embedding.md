# Grassmannian Embedding

## Overview

U(N) coherent states for LQG intertwiners admit a natural embedding into the Grassmannian Gr(k,n), connecting LQG geometry to the amplituhedron program.

## Plücker Embedding

The Grassmannian Gr(k,n) embeds into projective space via the Plücker map:
$$X \mapsto [\det(X_{I})]_{I \in \binom{[n]}{k}}$$

where $X_I$ are the maximal minors of the $k \times n$ matrix $X$.

## Positive Grassmannian

The positive Grassmannian $Gr^+(k,n)$ consists of matrices where all maximal minors are positive. This is the region relevant to the amplituhedron.

## LQG Connection

For a U(N) coherent state $|\Psi\rangle$ with occupation numbers $\{k_i\}$, the Grassmannian embedding is constructed by:
1. Forming the $k \times n$ matrix from the coherent state parameters
2. Computing the Plücker coordinates
3. Checking positivity of all maximal minors

## Signed-mean result and open volume question

The published EPJC paper establishes a kinematic correspondence; it does
not contain the follow-up zero-volume computation. In the later code,
$\langle q_{ijk}\rangle=0$ for real-plane states because the state amplitudes
are real and $q_{ijk}$ is imaginary antisymmetric in the occupation basis.

This cancellation also holds for real planes with mixed-sign minors outside
the positive cell. A positive-plane example has nonzero $\langle q^2\rangle$,
so the expectation of a positive quantum volume operator remains open. See
`red-team-audit.md`.

## Implementation

### Python (`code/python/lqg_scattering/positivity.py`)
- Direct computation of Plücker coordinates
- Positivity checks for n=4
- Analytical real-state cancellation of the signed triple-grasp mean

The root-level `code/python/positivity.py` is a compatibility facade. Related
spinor and Grassmannian maps are implemented in
`code/python/lqg_scattering/grassmannian.py`.

### Rust (`code/rust/src/grassmannian.rs`)
- Sparse Plücker coordinate computation
- Parallel positivity verification
- Extension to n≥5

## Key Files

| File | Purpose |
|------|---------|
| `code/rust/src/grassmannian.rs` | Plücker embedding, positivity tests |
| `code/python/lqg_scattering/positivity.py` | Reusable Python implementation; root `positivity.py` is a compatibility facade |
| `paper/lqg-amplituhedron.pdf` | Published kinematic correspondence |

## Related documentation

- [Shared volume numerical preliminaries](./volume-numerical-preliminaries.md)
- [T5 volume-positivity studies](./volume-positivity-studies.md)
- [T5c FL spinors and covariance geometry](./T5c-flux-covariance-volume-comparison.md)
- [Fock-space and coherent-state construction](./fock-space-construction.md)
- [Volume operator](./volume-operator.md)
- [Red-team audit](./red-team-audit.md)
- [Verification protocol](./verification-protocol.md)
- [T6 Minkowski reconstruction](./T6-minkowski-polyhedron.md)

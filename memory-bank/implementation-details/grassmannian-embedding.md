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

## Zero-Volume Result

**Published Result (EPJC):** The volume operator vanishes identically on the positive Grassmannian cell $Gr^+(k,n)$.

**Interpretation:** The amplituhedron region corresponds to classical, zero-volume geometry. Quantum volume requires the complex extension of the positive cell.

## Implementation

### Python (`positivity.py`)
- Direct computation of Plücker coordinates
- Positivity checks for n=4
- Analytical verification of zero-volume result

### Rust (`rust/src/grassmannian.rs`)
- Sparse Plücker coordinate computation
- Parallel positivity verification
- Extension to n≥5

## Key Files

| File | Purpose |
|------|---------|
| `rust/src/grassmannian.rs` | Plücker embedding, positivity tests |
| `positivity.py` | Python reference implementation |
| `paper/lqg-amplituhedron.pdf` | Published proof of zero-volume result |

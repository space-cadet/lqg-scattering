# Fock Space Construction

## Overview

The Fock space for LQG intertwiners is constructed using the Schwinger boson formalism, which maps SU(2) representation theory to harmonic oscillator algebra.

## Schwinger Boson Formalism

Each angular momentum $j$ is represented by a pair of harmonic oscillators $(a, b)$:
- $J_+ = a^\dagger b$
- $J_- = b^\dagger a$
- $J_z = \frac{1}{2}(a^\dagger a - b^\dagger b)$

The total spin is $j = \frac{1}{2}(n_a + n_b)$ where $n_a, n_b$ are occupation numbers.

## U(N) Decomposition

For an n-valent intertwiner with total spin $J$, the Fock space decomposes under U(N) as:
$$\mathcal{H}_J = \bigoplus_{\{k_i\}} \mathcal{H}_{\{k_i\}}$$

where $\{k_i\}$ are occupation numbers satisfying $\sum_i k_i = 2J$.

## Basis Enumeration

The basis states are labeled by occupation numbers $(k_1, k_2, ..., k_n)$ with:
- Constraint: $\sum_i k_i = 2J$
- Dimension: $\binom{2J + n - 1}{n - 1}$

## Dimension Growth

| n | dim(Fock) for J=1 | Notes |
|---|-------------------|-------|
| 4 | ~10 | Python manageable |
| 5 | ~35 | Python manageable |
| 6 | ~84 | Python slow |
| 7 | ~165 | Python impractical |
| 8 | ~286 | Requires Rust |

## Implementation

### Python (`coherent_states.py`)
- Direct NumPy array construction
- Explicit loop over occupation numbers
- Suitable for n=4 only

### Rust (`rust/src/fock.rs`)
- `sprs::CsMat` sparse matrix representation
- `rayon` parallel basis enumeration
- Support for n up to 8+

## Key Operations

| Operation | Formula | Implementation |
|-----------|---------|----------------|
| J_+ \|k⟩ | $\sqrt{(k+1)(2j-k)} \|k+1⟩$ | Sparse shift matrix |
| J_- \|k⟩ | $\sqrt{k(2j-k+1)} \|k-1⟩$ | Sparse shift matrix |
| J_z \|k⟩ | $(j-k) \|k⟩$ | Diagonal matrix |

//! Fock space for N Schwinger boson edges truncated by total boson number.
//!
//! Basis states are occupation vectors (n_a1, n_b1, ..., n_aN, n_bN) with
//! sum <= K. The basis is generated combinatorially (stars and bars) in
//! O(dim * 2N), not by filtering the (K+1)^(2N) product grid — the latter
//! is what made the Python implementation infeasible for n >= 5.
//!
//! Occupations are stored as u8 (K <= 255) in a flat dim x 2N array; the
//! index is a HashMap from occupation vectors to basis indices.

use rayon::prelude::*;
use std::collections::HashMap;

pub struct FockSpace {
    pub n: usize,
    pub k: usize,
    pub dim: usize,
    /// occupations[idx * 2n + m] = boson number of mode m in basis state idx
    occ: Vec<u8>,
    index: HashMap<Box<[u8]>, u32>,
}

impl FockSpace {
    pub fn new(n: usize, k: usize) -> Self {
        assert!(k <= 255, "occupations stored as u8");
        // dim = binom(2n + k, 2n)
        let mut dim: u64 = 1;
        for i in 1..=(2 * n) as u64 {
            dim = dim * (k as u64 + i) / i;
        }
        let dim = dim as usize;
        let mut occ = vec![0u8; dim * 2 * n];
        let mut index = HashMap::with_capacity(dim);
        // stars and bars: distribute up to k quanta over 2n modes, in
        // lexicographic order so the layout matches the recursive build
        let mut state = vec![0u8; 2 * n];
        let mut idx = 0usize;
        Self::build(n, k, 0, 0, &mut state, &mut idx, &mut occ, &mut index);
        assert_eq!(idx, dim, "binomial prediction mismatch");
        FockSpace { n, k, dim, occ, index }
    }

    fn build(
        n: usize,
        k: usize,
        mode: usize,
        used: usize,
        state: &mut [u8],
        idx: &mut usize,
        occ: &mut [u8],
        index: &mut HashMap<Box<[u8]>, u32>,
    ) {
        if mode == 2 * n - 1 {
            for v in 0..=(k - used) as u8 {
                state[mode] = v;
                let i = *idx;
                occ[i * 2 * n..(i + 1) * 2 * n].copy_from_slice(state);
                index.insert(state.to_vec().into_boxed_slice(), i as u32);
                *idx += 1;
            }
            state[mode] = 0;
            return;
        }
        for v in 0..=(k - used) as u8 {
            state[mode] = v;
            Self::build(n, k, mode + 1, used + v as usize, state, idx, occ, index);
        }
        state[mode] = 0;
    }

    #[inline]
    pub fn occ(&self, idx: usize) -> &[u8] {
        &self.occ[idx * 2 * self.n..(idx + 1) * 2 * self.n]
    }

    #[inline]
    pub fn index_of(&self, occ: &[u8]) -> Option<u32> {
        self.index.get(occ).copied()
    }

    /// Total boson number of basis state idx (conserved by u(N)).
    #[inline]
    pub fn total(&self, idx: usize) -> u32 {
        self.occ(idx).iter().map(|&v| v as u32).sum()
    }

    /// Dense zero vector.
    pub fn zeros(&self) -> Vec<num_complex::Complex64> {
        vec![num_complex::Complex64::zero(); self.dim]
    }
}

use num_traits::Zero;

/// Apply an occupation-space operator to a dense vector.
///
/// `op(occ_slice, out)` must append (new_occ_slice, factor) pairs to out.
/// Implemented as a rayon-parallel loop over basis states (each output
/// row is written by exactly one task after a merge of per-thread buffers).
pub fn apply_parallel<F>(
    space: &FockSpace,
    op: &F,
    vec: &[num_complex::Complex64],
) -> Vec<num_complex::Complex64>
where
    F: Fn(&[u8], usize, &mut Vec<(usize, num_complex::Complex64)>) + Sync,
{
    let n2 = 2 * space.n;
    // parallel map over row chunks: each task produces (col, val) for its
    // own source columns; we then reduce by scattering into row-major bins
    let results: Vec<Vec<(usize, num_complex::Complex64)>> = (0..space.dim)
        .into_par_iter()
        .map(|col| {
            let mut out: Vec<(usize, num_complex::Complex64)> = Vec::new();
            let v = vec[col];
            if v != num_complex::Complex64::zero() {
                op(space.occ(col), col, &mut out);
            }
            let _ = n2;
            out
                .into_iter()
                .map(|(r, f)| (r, f * v))
                .collect()
        })
        .collect();
    let mut acc = space.zeros();
    // sequential scatter (parallel merge not worth it at these sizes)
    for buf in results {
        for (r, val) in buf {
            acc[r] += val;
        }
    }
    acc
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dimension_matches_binomial() {
        // C(2n + k, 2n)
        let cases = [(1usize, 3usize), (3, 3), (4, 6), (5, 8), (6, 6), (8, 6)];
        for (n, k) in cases {
            let space = FockSpace::new(n, k);
            let mut expect: u64 = 1;
            for i in 1..=(2 * n) as u64 {
                expect = expect * (k as u64 + i) / i;
            }
            assert_eq!(space.dim, expect as usize, "n={n} k={k}");
        }
    }

    #[test]
    fn basis_states_unique_and_bounded() {
        let space = FockSpace::new(4, 6);
        assert_eq!(space.dim, 3003);
        for i in 0..space.dim {
            assert_eq!(space.index_of(space.occ(i)), Some(i as u32));
            assert!(space.total(i) <= 6);
        }
    }
}

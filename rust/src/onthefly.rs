//! On-the-fly engine for Fock spaces too large to store sparse operators
//! (n >= 7 with uniform references). Matvecs are computed by enumerating
//! oscillator branches per basis state and scattering into the output
//! with atomic adds — O(branches) memory instead of O(nnz) storage.
//!
//! Indexing uses the combinatorial rank (our basis is built in
//! lexicographic order), so no HashMap is needed: rank lookup is O(2N)
//! integer operations against a binomial table.

use num_complex::Complex64;
use num_traits::{One, Zero};
use rayon::prelude::*;
use std::sync::atomic::{AtomicU64, Ordering};

pub struct OtfSpace {
    pub n: usize,
    pub k: usize,
    pub dim: usize,
    occ: Vec<u8>,
    /// binom[M][R] = C(M + R, M) for M = 0..2n-1, R = 0..k
    binom: Vec<Vec<u64>>,
}

impl OtfSpace {
    pub fn new(n: usize, k: usize) -> Self {
        assert!(k <= 255);
        let mut dim: u64 = 1;
        for i in 1..=(2 * n) as u64 {
            dim = dim * (k as u64 + i) / i;
        }
        let dim = dim as usize;
        let mut occ = vec![0u8; dim * 2 * n];
        let mut idx = 0usize;
        let mut state = vec![0u8; 2 * n];
        build_basis(n, k, 0, 0, &mut state, &mut idx, &mut occ);
        assert_eq!(idx, dim);
        let mut binom = vec![vec![0u64; k + 1]; 2 * n];
        for m in 0..2 * n {
            for r in 0..=k {
                binom[m][r] = comb(m as u64 + r as u64, m as u64);
            }
        }
        OtfSpace { n, k, dim, occ, binom }
    }

    /// Combinatorial rank of an occupation vector: number of basis states
    /// lexicographically before it, matching the recursive build order.
    pub fn rank(&self, occ: &[u8]) -> usize {
        let n2 = 2 * self.n;
        let mut idx = 0u64;
        let mut used = 0u32;
        for m in 0..n2 - 1 {
            let m_rem = n2 - 1 - m; // modes after m
            let budget = self.k as u32 - used;
            for u in 0..occ[m] as u32 {
                idx += self.binom[m_rem][(budget - u) as usize];
            }
            used += occ[m] as u32;
        }
        idx as usize + occ[n2 - 1] as usize
    }

    #[inline]
    pub fn occ(&self, idx: usize) -> &[u8] {
        &self.occ[idx * 2 * self.n..(idx + 1) * 2 * self.n]
    }
}

fn comb(n: u64, m: u64) -> u64 {
    if m > n {
        return 0;
    }
    let m = m.min(n - m);
    let mut r = 1u64;
    for i in 0..m {
        r = r * (n - i) / (i + 1);
    }
    r
}

fn build_basis(
    n: usize,
    k: usize,
    mode: usize,
    used: usize,
    state: &mut [u8],
    idx: &mut usize,
    occ: &mut [u8],
) {
    if mode == 2 * n - 1 {
        for v in 0..=(k - used) as u8 {
            state[mode] = v;
            let i = *idx;
            occ[i * 2 * n..(i + 1) * 2 * n].copy_from_slice(state);
            *idx += 1;
        }
        state[mode] = 0;
        return;
    }
    for v in 0..=(k - used) as u8 {
        state[mode] = v;
        build_basis(n, k, mode + 1, used + v as usize, state, idx, occ);
    }
    state[mode] = 0;
}

fn atomic_add(cell: &AtomicU64, val: f64) {
    let mut old = cell.load(Ordering::Relaxed);
    loop {
        let new = f64::from_bits(old) + val;
        match cell.compare_exchange_weak(old, new.to_bits(), Ordering::Relaxed, Ordering::Relaxed)
        {
            Ok(_) => return,
            Err(o) => old = o,
        }
    }
}

fn atomic_scatter(out_re: &[AtomicU64], out_im: &[AtomicU64], row: usize, val: Complex64) {
    atomic_add(&out_re[row], val.re);
    atomic_add(&out_im[row], val.im);
}

fn atomic_output(dim: usize) -> (Vec<AtomicU64>, Vec<AtomicU64>) {
    (
        (0..dim).map(|_| AtomicU64::new(0)).collect(),
        (0..dim).map(|_| AtomicU64::new(0)).collect(),
    )
}

fn collect(out_re: Vec<AtomicU64>, out_im: Vec<AtomicU64>) -> Vec<Complex64> {
    out_re
        .into_iter()
        .zip(out_im)
        .map(|(a, b)| Complex64::new(f64::from_bits(a.into_inner()), f64::from_bits(b.into_inner())))
        .collect()
}

/// A = sum_ij Z_ij E_ij applied on the fly.
pub fn apply_gen(sp: &OtfSpace, z: &[Complex64], v: &[Complex64]) -> Vec<Complex64> {
    let n = sp.n;
    let (out_re, out_im) = atomic_output(sp.dim);
    (0..sp.dim).into_par_iter().for_each(|col| {
        let vc = v[col];
        if vc == Complex64::zero() {
            return;
        }
        let occ = sp.occ(col);
        let mut buf = occ.to_vec();
        for j in 0..n {
            // a_j -> a_i branches for all i
            let aj = 2 * j;
            if occ[aj] > 0 {
                let lo = (occ[aj] as f64).sqrt();
                for i in 0..n {
                    let zij = z[i * n + j];
                    if zij == Complex64::zero() {
                        continue;
                    }
                    buf[aj] -= 1;
                    let f = lo * (buf[2 * i] as f64 + 1.0).sqrt();
                    buf[2 * i] += 1;
                    let r = sp.rank(&buf);
                    buf[2 * i] -= 1;
                    buf[aj] += 1;
                    atomic_scatter(&out_re, &out_im, r, vc * zij * f);
                }
            }
            // b_j -> b_i branches
            let bj = 2 * j + 1;
            if occ[bj] > 0 {
                let lo = (occ[bj] as f64).sqrt();
                for i in 0..n {
                    let zij = z[i * n + j];
                    if zij == Complex64::zero() {
                        continue;
                    }
                    buf[bj] -= 1;
                    let f = lo * (buf[2 * i + 1] as f64 + 1.0).sqrt();
                    buf[2 * i + 1] += 1;
                    let r = sp.rank(&buf);
                    buf[2 * i + 1] -= 1;
                    buf[bj] += 1;
                    atomic_scatter(&out_re, &out_im, r, vc * zij * f);
                }
            }
        }
    });
    collect(out_re, out_im)
}

/// Composite single-edge operator product, one fused pass:
/// lower_jp = true  applies J-_i J+_j (lower b_j / raise a_j, then
/// lower a_i / raise b_i); lower_jp = false applies J+_i J-_j. The two
/// are summed symmetrically by `apply_jdot`.
#[allow(clippy::too_many_arguments)]
fn apply_su2_pair(
    sp: &OtfSpace,
    v: &[Complex64],
    e_i: usize,
    e_j: usize,
    lower_jp: bool,
) -> Vec<Complex64> {
    let (out_re, out_im) = atomic_output(sp.dim);
    (0..sp.dim).into_par_iter().for_each(|col| {
        let vc = v[col];
        if vc == Complex64::zero() {
            return;
        }
        let occ = sp.occ(col);
        let (lj, li) = if lower_jp {
            // J+_j = a_j^dag b_j lowers b_j (2j+1); J-_i = b_i^dag a_i lowers a_i (2i)
            (2 * e_j + 1, 2 * e_i)
        } else {
            // J-_j = b_j^dag a_j lowers a_j (2j); J+_i = a_i^dag b_i lowers b_i (2i+1)
            (2 * e_j, 2 * e_i + 1)
        };
        if occ[lj] == 0 {
            return;
        }
        let mut buf = occ.to_vec();
        buf[lj] -= 1;
        let f1 = (occ[lj] as f64).sqrt() * (buf[lj ^ 1] as f64 + 1.0).sqrt();
        buf[lj ^ 1] += 1; // raised partner on edge j
        if buf[li] == 0 {
            return;
        }
        let f2 = (buf[li] as f64).sqrt() * (buf[li ^ 1] as f64 + 1.0).sqrt();
        buf[li] -= 1;
        buf[li ^ 1] += 1;
        let r = sp.rank(&buf);
        atomic_scatter(&out_re, &out_im, r, vc * (f1 * f2));
    });
    collect(out_re, out_im)
}

/// J_i . J_j applied on the fly.
pub fn apply_jdot(sp: &OtfSpace, i: usize, j: usize, v: &[Complex64]) -> Vec<Complex64> {
    let t1 = apply_su2_pair(sp, v, i, j, true); // J-_i J+_j
    let t2 = apply_su2_pair(sp, v, i, j, false); // J+_i J-_j
    let mut out = vec![Complex64::zero(); sp.dim];
    out.par_iter_mut().enumerate().for_each(|(c, o)| {
        let occ = sp.occ(c);
        let zi = 0.5 * (occ[2 * i] as f64 - occ[2 * i + 1] as f64);
        let zj = 0.5 * (occ[2 * j] as f64 - occ[2 * j + 1] as f64);
        *o = v[c] * (zi * zj) + 0.5 * (t1[c] + t2[c]);
    });
    out
}


/// Perelomov state exp(A)|ref> via Taylor series, on-the-fly matvecs.
pub fn perelomov_otf(
    sp: &OtfSpace,
    z: &[Complex64],
    ref_occ: &[(u8, u8)],
    tol: f64,
) -> Vec<Complex64> {
    let mut flat = vec![0u8; 2 * sp.n];
    for (i, &(a, b)) in ref_occ.iter().enumerate() {
        flat[2 * i] = a;
        flat[2 * i + 1] = b;
    }
    let r0 = sp.rank(&flat);
    let mut result = vec![Complex64::zero(); sp.dim];
    result[r0] = Complex64::one();
    let mut term = result.clone();
    for it in 1..(2 * sp.k + 4) {
        term = apply_gen(sp, z, &term);
        let f = 1.0 / it as f64;
        for x in term.iter_mut() {
            *x *= f;
        }
        let inc: f64 = term.iter().map(|x| x.norm_sqr()).sum::<f64>().sqrt();
        let res: f64 = result.iter().map(|x| x.norm_sqr()).sum::<f64>().sqrt();
        for (r, t) in result.iter_mut().zip(term.iter()) {
            *r += t;
        }
        if inc < tol * res.max(1.0) {
            break;
        }
    }
    let norm: f64 = result.iter().map(|x| x.norm_sqr()).sum::<f64>().sqrt();
    for x in result.iter_mut() {
        *x /= norm;
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::fock::FockSpace;
    use crate::grassmannian::{plane_to_z, positive_plane_curve};
    use crate::ops::{generator_matrix, matvec};

    #[test]
    fn rank_matches_hashmap_index() {
        for (n, k) in [(3usize, 3usize), (4, 4), (5, 3)] {
            let fock = FockSpace::new(n, k);
            let otf = OtfSpace::new(n, k);
            assert_eq!(fock.dim, otf.dim);
            for i in (0..fock.dim).step_by(7) {
                assert_eq!(fock.index_of(fock.occ(i)), Some(i as u32));
                assert_eq!(otf.rank(otf.occ(i)), i);
            }
        }
    }

    #[test]
    fn gen_matches_stored_matrix() {
        let n = 4;
        let k = 5;
        let fock = FockSpace::new(n, k);
        let otf = OtfSpace::new(n, k);
        let plane = positive_plane_curve(n, 3);
        let z = plane_to_z(&plane, n);
        let mut v = vec![Complex64::zero(); fock.dim];
        v[3] = Complex64::new(0.7, -0.2);
        v[100] = Complex64::new(-0.1, 0.4);
        let a = generator_matrix(&fock, &z, n);
        let expect = matvec(&a, &v);
        let got = apply_gen(&otf, &z, &v);
        for (x, y) in expect.iter().zip(&got) {
            assert!((x - y).norm() < 1e-12, "{x} vs {y}");
        }
    }

    #[test]
    fn jdot_matches_stored_matrix() {
        let n = 4;
        let k = 4;
        let fock = FockSpace::new(n, k);
        let otf = OtfSpace::new(n, k);
        let mut v = vec![Complex64::zero(); fock.dim];
        v[7] = Complex64::new(0.3, 0.1);
        v[200] = Complex64::new(0.5, -0.6);
        let expect = matvec(&crate::ops::j_dot(&fock, 1, 3), &v);
        let got = apply_jdot(&otf, 1, 3, &v);
        for (x, y) in expect.iter().zip(&got) {
            assert!((x - y).norm() < 1e-12, "{x} vs {y}");
        }
    }

    #[test]
    fn perelomov_matches_stored_engine() {
        let n = 4;
        let k = 6;
        let fock = FockSpace::new(n, k);
        let otf = OtfSpace::new(n, k);
        let mut plane = positive_plane_curve(n, 8);
        for i in 0..n {
            plane[n + i] += Complex64::new(0.0, 0.3);
        }
        let z = plane_to_z(&plane, n);
        let ref_occ = [(1u8, 1u8), (1, 1), (1, 0), (1, 0)];
        let rv = crate::coherent::reference_vector(&fock, &ref_occ);
        let v_stored = crate::coherent::perelomov(&fock, &z, &rv, 1e-13);
        let v_otf = perelomov_otf(&otf, &z, &ref_occ, 1e-13);
        let d: f64 = v_stored
            .iter()
            .zip(&v_otf)
            .map(|(a, b)| (a - b).norm_sqr())
            .sum::<f64>()
            .sqrt();
        assert!(d < 1e-9, "state difference {d:e}");
    }
}

//! Sparse occupation-space operators for the Schwinger/Fock representation.
//!
//! All operators are built as sprs CsMat matrices by enumerating the
//! oscillator action once per basis state — the same mathematics as the
//! Python `coherent_states.py`, but with O(dim * K) Rust loops instead of
//! Python dict dispatch.

use crate::fock::FockSpace;
use num_complex::Complex64;
use rayon::prelude::*;
use sprs::CsMat;

type CMat = CsMat<Complex64>;

fn sqrtf(x: u8) -> f64 {
    (x as f64).sqrt()
}

/// Builder accumulating per-column triplets, assembled to CsMat.
struct TripletBuilder {
    dim: usize,
    rows: Vec<usize>,
    cols: Vec<usize>,
    vals: Vec<Complex64>,
}

impl TripletBuilder {
    fn new(dim: usize) -> Self {
        TripletBuilder { dim, rows: Vec::new(), cols: Vec::new(), vals: Vec::new() }
    }
    fn add(&mut self, row: usize, col: usize, val: Complex64) {
        self.rows.push(row);
        self.cols.push(col);
        self.vals.push(val);
    }
    fn build(self) -> CMat {
        // sort by (col, row) for csr via sprs TriMat
        let mut trips: Vec<(usize, usize, Complex64)> =
            self.rows.into_iter().zip(self.cols).zip(self.vals)
                .map(|((r, c), v)| (c, r, v))
                .collect();
        trips.sort_unstable_by_key(|&(c, r, _)| (c, r));
        let mut tm = sprs::TriMat::new((self.dim, self.dim));
        for (c, r, v) in trips {
            tm.add_triplet(r, c, v);
        }
        tm.to_csr()
    }
}

/// u(N) generator E_ij = a_i^dagger a_j + b_i^dagger b_j.
pub fn e_ij(space: &FockSpace, i: usize, j: usize) -> CMat {
    let _n = space.n;
    let mut b = TripletBuilder::new(space.dim);
    for col in 0..space.dim {
        let occ = space.occ(col);
        // a_i^dagger a_j : lower mode 2j, raise mode 2i (lower first: for
        // i == j the raising factor must see the decremented occupation,
        // so that E_ii is the number operator n_i)
        let (a_i, a_j) = (2 * i, 2 * j);
        if occ[a_j] > 0 {
            let mut o = occ.to_vec();
            o[a_j] -= 1;
            let f = sqrtf(occ[a_j]) * sqrtf(o[a_i] + 1);
            o[a_i] += 1;
            if let Some(r) = space.index_of(&o) {
                b.add(r as usize, col, Complex64::new(f, 0.0));
            }
        }
        // b_i^dagger b_j : modes 2i+1, 2j+1
        let (bi, bj) = (2 * i + 1, 2 * j + 1);
        if occ[bj] > 0 {
            let mut o = occ.to_vec();
            o[bj] -= 1;
            let f = sqrtf(occ[bj]) * sqrtf(o[bi] + 1);
            o[bi] += 1;
            if let Some(r) = space.index_of(&o) {
                b.add(r as usize, col, Complex64::new(f, 0.0));
            }
        }
    }
    b.build()
}

/// Number operator n_e = a_e^dagger a_e + b_e^dagger b_e (diagonal).
pub fn number_op(space: &FockSpace, e: usize) -> CMat {
    let mut b = TripletBuilder::new(space.dim);
    for col in 0..space.dim {
        let occ = space.occ(col);
        let f = (occ[2 * e] + occ[2 * e + 1]) as f64;
        b.add(col, col, Complex64::new(f, 0.0));
    }
    b.build()
}

/// su(2) single-edge generators: (jz diagonal, jp = a^dagger b, jm = b^dagger a).
pub fn su2_ops(space: &FockSpace, e: usize) -> (CMat, CMat, CMat) {
    let mut zj = TripletBuilder::new(space.dim);
    let mut pj = TripletBuilder::new(space.dim);
    let mut mj = TripletBuilder::new(space.dim);
    for col in 0..space.dim {
        let occ = space.occ(col);
        let (a, bmode) = (2 * e, 2 * e + 1);
        zj.add(col, col, Complex64::new(0.5 * (occ[a] as f64 - occ[bmode] as f64), 0.0));
        // jp = a^dagger b : lower b, raise a
        if occ[bmode] > 0 {
            let mut o = occ.to_vec();
            let f = sqrtf(occ[bmode]) * sqrtf(o[a] + 1);
            o[bmode] -= 1;
            o[a] += 1;
            if let Some(r) = space.index_of(&o) {
                pj.add(r as usize, col, Complex64::new(f, 0.0));
            }
        }
        // jm = b^dagger a : lower a, raise b
        if occ[a] > 0 {
            let mut o = occ.to_vec();
            let f = sqrtf(occ[a]) * sqrtf(o[bmode] + 1);
            o[a] -= 1;
            o[bmode] += 1;
            if let Some(r) = space.index_of(&o) {
                mj.add(r as usize, col, Complex64::new(f, 0.0));
            }
        }
    }
    (zj.build(), pj.build(), mj.build())
}

/// scalar * matrix (sprs has no f64 * CsMat)
fn scaled(a: &CMat, s: f64) -> CMat {
    let mut b = TripletBuilder::new(a.rows());
    for (&v, (r, c)) in a.iter() {
        b.add(r, c, v * s);
    }
    b.build()
}

/// J_i . J_j = Jz_i Jz_j + (J+_i J-_j + J-_i J+_j)/2.
pub fn j_dot(space: &FockSpace, i: usize, j: usize) -> CMat {
    let (zi, pi, mi) = su2_ops(space, i);
    let (zj, pj, mj) = su2_ops(space, j);
    let zprod = &zi * &zj;
    let pp = scaled(&(&pi * &mj), 0.5);
    let pm = scaled(&(&mi * &pj), 0.5);
    &(&zprod + &pp) + &pm
}

/// Assemble A = sum_ij Z_ij E_ij as a single sparse matrix (for the
/// Perelomov exponential).
pub fn generator_matrix(space: &FockSpace, z: &[Complex64], n: usize) -> CMat {
    let mut b = TripletBuilder::new(space.dim);
    for i in 0..n {
        for j in 0..n {
            let zij = z[i * n + j];
            if zij == Complex64::zero() {
                continue;
            }
            let e = e_ij(space, i, j);
            for (&v, (r, c)) in e.iter() {
                b.add(r, c, zij * v); // sprs iter yields (val, (row, col))
            }
        }
    }
    b.build()
}

use num_traits::Zero;

/// Ray row-parallel sparse matvec: out = A v.
pub fn matvec(a: &CMat, v: &[Complex64]) -> Vec<Complex64> {
    let dim = a.rows();
    let mut out = vec![Complex64::zero(); dim];
    let indptr_buf = a.indptr();
    let indptr: &[usize] = indptr_buf.raw_storage();
    let indices = a.indices();
    let data = a.data();
    out.par_iter_mut().enumerate().for_each(|(row, o)| {
        let mut acc = Complex64::zero();
        for p in indptr[row]..indptr[row + 1] {
            acc += data[p] * v[indices[p]];
        }
        *o = acc;
    });
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::fock::FockSpace;
    use num_traits::One;

    fn expect(space: &FockSpace, mat: &CMat, occ_in: &[u8], occ_out: &[u8]) -> Complex64 {
        let ci = space.index_of(occ_in).unwrap() as usize;
        let co = space.index_of(occ_out).unwrap() as usize;
        *mat.get(co, ci).unwrap_or(&Complex64::zero())
    }

    #[test]
    fn su2_matrix_elements() {
        let space = FockSpace::new(1, 3);
        let (zj, pj, mj) = su2_ops(&space, 0);
        // |1,2> : jz = (1-2)/2 = -1/2
        assert!((expect(&space, &zj, &[1, 2], &[1, 2]) - Complex64::new(-0.5, 0.0)).norm() < 1e-14);
        // jp |0,1> = |1,0>
        assert!((expect(&space, &pj, &[0, 1], &[1, 0]) - Complex64::new(1.0, 0.0)).norm() < 1e-14);
        // jm |2,0> = sqrt(2) |1,1>
        assert!((expect(&space, &mj, &[2, 0], &[1, 1]) - Complex64::new(2.0f64.sqrt(), 0.0)).norm() < 1e-14);
    }

    #[test]
    fn un_algebra_commutator() {
        // [E_ij, E_kl] = delta_jk E_il - delta_li E_kj on n=3, K=3
        let n = 3;
        let space = FockSpace::new(n, 3);
        let e: Vec<Vec<CMat>> = (0..n).map(|i| (0..n).map(|j| e_ij(&space, i, j)).collect()).collect();
        let mut rng_state = 0x2545_f491_4f6c_dd1d_u64;
        let mut rnd = move || {
            rng_state ^= rng_state << 13;
            rng_state ^= rng_state >> 7;
            rng_state ^= rng_state << 17;
            rng_state
        };
        let mut max_err = 0.0f64;
        for _ in 0..64 {
            let col = (rnd() as usize) % space.dim;
            let i = (rnd() as usize) % n;
            let j = (rnd() as usize) % n;
            let k = (rnd() as usize) % n;
            let l = (rnd() as usize) % n;
            let mut v = vec![Complex64::zero(); space.dim];
            v[col] = Complex64::one();
            let lhs = {
                let a = matvec(&e[i][j], &matvec(&e[k][l], &v));
                let b = matvec(&e[k][l], &matvec(&e[i][j], &v));
                a.iter().zip(b).map(|(x, y)| x - y).collect::<Vec<_>>()
            };
            let rhs = {
                let a = matvec(&e[i][l], &v);
                let b = matvec(&e[k][j], &v);
                let mut r = vec![Complex64::zero(); space.dim];
                if j == k {
                    for (x, y) in r.iter_mut().zip(a) {
                        *x += y;
                    }
                }
                if l == i {
                    for (x, y) in r.iter_mut().zip(b) {
                        *x -= y;
                    }
                }
                r
            };
            for (x, y) in lhs.iter().zip(rhs) {
                max_err = max_err.max((x - y).norm());
            }
        }
        assert!(max_err < 1e-12, "u(3) algebra max error {max_err:e}");
    }

    #[test]
    fn j_dot_matrix_elements() {
        // J_1 . J_2 on |a0 a1> (one a-boson on each of edges 0,1) = 1/4 (triplet m=1)
        let space = FockSpace::new(4, 3);
        let j = j_dot(&space, 0, 1);
        let v = expect(&space, &j, &[1, 0, 1, 0, 0, 0, 0, 0], &[1, 0, 1, 0, 0, 0, 0, 0]);
        assert!((v - Complex64::new(0.25, 0.0)).norm() < 1e-14);
        let v = expect(&space, &j, &[1, 0, 0, 1, 0, 0, 0, 0], &[1, 0, 0, 1, 0, 0, 0, 0]);
        assert!((v - Complex64::new(-0.25, 0.0)).norm() < 1e-14);
    }
}

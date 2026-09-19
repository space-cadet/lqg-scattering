//! LQG volume operator for U(N) coherent states.
//!
//! De Pietri / Rovelli-Smolin construction on a triple of edges
//! (i, j, k): with A_ij = J_i . J_j, q = i [A_ij, A_jk] and
//! V = (gamma * hbar)^{3/2} sqrt(|<q>|).
//!
//! Matches `positivity.volume_operator` in the Python pipeline. Two exact
//! zero mechanisms (verified in the Python reference and re-tested here):
//! all-a/b references freeze the spins (q = 0), and real planes give real
//! Fock amplitudes (q = 0 for any triple).

use crate::fock::FockSpace;
use crate::ops::{j_dot, matvec, su2_ops, CMat};
use num_complex::Complex64;

pub const GAMMA: f64 = 0.2375;

/// Volume expectation on a state, plus <q>.
pub fn volume_operator(
    space: &FockSpace,
    v: &[Complex64],
    triple: (usize, usize, usize),
) -> (f64, Complex64) {
    let (i, j, k) = triple;
    let a_ij = j_dot(space, i, j);
    let a_jk = j_dot(space, j, k);
    // q = i [A_ij, A_jk]
    let comm = &(&a_ij * &a_jk) - &(&a_jk * &a_ij);
    let mut qmat = TriMatLike::new(space.dim);
    for (&val, (r, c)) in comm.iter() {
        qmat.add(r, c, Complex64::new(0.0, 1.0) * val);
    }
    let qmat = qmat.build();
    let w = matvec(&qmat, v);
    let q_exp: Complex64 = v.iter().zip(w).map(|(a, b)| a.conj() * b).sum();
    let v_vol = GAMMA.powf(1.5) * q_exp.norm().sqrt();
    (v_vol, q_exp)
}

/// Minimal triplet accumulator (avoids exposing ops::TripletBuilder).
struct TriMatLike {
    dim: usize,
    rows: Vec<usize>,
    cols: Vec<usize>,
    vals: Vec<Complex64>,
}

impl TriMatLike {
    fn new(dim: usize) -> Self {
        TriMatLike { dim, rows: Vec::new(), cols: Vec::new(), vals: Vec::new() }
    }
    fn add(&mut self, row: usize, col: usize, val: Complex64) {
        self.rows.push(row);
        self.cols.push(col);
        self.vals.push(val);
    }
    fn build(self) -> CMat {
        let mut trips: Vec<(usize, usize, Complex64)> = self
            .rows
            .into_iter()
            .zip(self.cols)
            .zip(self.vals)
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

/// Spin expectation vectors <J_i^a>, a = x, y, z, for every edge.
/// <J_i^+> = <J_i^-> = 0 identically (N_a/N_b conservation), so all
/// vectors lie on the z axis.
pub fn spin_vectors(space: &FockSpace, v: &[Complex64]) -> Vec<[f64; 3]> {
    let mut out = Vec::with_capacity(space.n);
    for e in 0..space.n {
        let (zj, pj, mj) = su2_ops(space, e);
        let jx = {
            let mut t = TriMatLike::new(space.dim);
            for (&val, (r, c)) in pj.iter() {
                t.add(r, c, 0.5 * val);
            }
            for (&val, (r, c)) in mj.iter() {
                t.add(r, c, 0.5 * val);
            }
            t.build()
        };
        let jy = {
            let mut t = TriMatLike::new(space.dim);
            for (&val, (r, c)) in pj.iter() {
                t.add(r, c, -0.5 * Complex64::i() * val);
            }
            for (&val, (r, c)) in mj.iter() {
                t.add(r, c, 0.5 * Complex64::i() * val);
            }
            t.build()
        };
        let exp = |m: &CMat| -> f64 {
            let w = matvec(m, v);
            v.iter().zip(w).map(|(a, b)| (a.conj() * b).re).sum::<f64>()
        };
        out.push([exp(&jx), exp(&jy), exp(&zj)]);
    }
    out
}

/// Max over triples of |det[n_i, n_j, n_k]| for the spin vectors.
pub fn coplanarity(vectors: &[[f64; 3]]) -> f64 {
    let m = vectors.len();
    let mut worst = 0.0f64;
    for i in 0..m {
        for j in (i + 1)..m {
            for k in (j + 1)..m {
                let (a, b, c) = (vectors[i], vectors[j], vectors[k]);
                let det = a[0] * (b[1] * c[2] - b[2] * c[1])
                    - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0]);
                worst = worst.max(det.abs());
            }
        }
    }
    worst
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::coherent::{perelomov, reference_vector};
    use crate::grassmannian::positive_plane_curve;
    use crate::grassmannian::plane_to_z;

    fn ref_vertex4() -> Vec<(u8, u8)> {
        vec![(1, 1), (1, 1), (1, 0), (1, 0)]
    }

    #[test]
    fn analytic_triple_product() {
        // product state: edge0 |a> (J = z/2), edge1 |+x> = (|a>+|b>)/sqrt2,
        // edge2 |+y> = (|a>+i|b>)/sqrt2.
        // |<q>| = |eps J1 J2 J3| = 1/8.
        let space = FockSpace::new(4, 3);
        let mut v = space.zeros();
        for (e1, e2, amp) in [
            ((1u8, 0u8), (1u8, 0u8), Complex64::new(0.5, 0.0)),
            ((1, 0), (0, 1), Complex64::new(0.0, 0.5)),
            ((0, 1), (1, 0), Complex64::new(0.5, 0.0)),
            ((0, 1), (0, 1), Complex64::new(0.0, 0.5)),
        ] {
            let mut f = vec![0u8; 8];
            f[0] = 1; // edge0 |a>
            f[2] = e1.0;
            f[3] = e1.1;
            f[4] = e2.0;
            f[5] = e2.1;
            let idx = space.index_of(&f).unwrap() as usize;
            v[idx] = amp;
        }
        let (_, q) = volume_operator(&space, &v, (0, 1, 2));
        // sign convention: q = i[A12, A23] = -eps J1 J2 J3; Python measured
        // +0.125 for this configuration, magnitude must be 1/8
        assert!((q.norm() - 0.125).abs() < 1e-12, "q = {q}");
    }

    #[test]
    fn volume_zero_on_real_plane_any_triple() {
        let n = 6usize;
        let space = FockSpace::new(n, 6);
        let plane = positive_plane_curve(n, 5);
        let z = plane_to_z(&plane, n);
        let mut ref_occ = vec![(0u8, 0u8); n];
        for e in ref_occ.iter_mut().take(3) {
            *e = (1, 1);
        }
        let rv = reference_vector(&space, &ref_occ);
        let v = perelomov(&space, &z, &rv, 1e-13);
        for triple in [(0usize, 1usize, 2usize), (2, 3, 4), (1, 4, 5)] {
            let (vol, q) = volume_operator(&space, &v, triple);
            assert!(q.norm() < 1e-10, "triple {triple:?} q = {q}");
            assert!(vol < 1e-8, "triple {triple:?} V = {vol}");
        }
    }

    #[test]
    fn volume_nonzero_on_complex_plane() {
        let n = 4usize;
        let space = FockSpace::new(n, 6);
        let mut plane = positive_plane_curve(n, 9);
        // imaginary perturbation breaking the minor-phase cocycle
        for i in 0..n {
            plane[n + i] += Complex64::new(0.0, 0.3 * (i as f64 + 1.0) - 0.7);
        }
        let z = plane_to_z(&plane, n);
        let rv = reference_vector(&space, &ref_vertex4());
        let v = perelomov(&space, &z, &rv, 1e-13);
        let (vol, _q) = volume_operator(&space, &v, (0, 1, 2));
        assert!(vol > 1e-6, "V = {vol}");
        // normals stay z-aligned even off the positive cell
        let sv = spin_vectors(&space, &v);
        assert!(coplanarity(&sv) < 1e-12);
    }
}

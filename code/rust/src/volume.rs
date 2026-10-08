//! Triple-grasp diagnostics and RS/AL positive vertex volumes.
//!
//! `volume_operator` is the legacy signed-mean proxy
//! gamma^(3/2)*sqrt(|<q_ijk>|), q_ijk=i[J_i.J_j,J_j.J_k]. It is not a
//! positive volume expectation. `rovelli_smolin_volume` evaluates the sum
//! of positive triple contributions; `ashtekar_lewandowski_volume` evaluates
//! the positive root of the orientation-weighted vertex sum. Both use exact
//! dense spectral decomposition by populated invariant blocks, capped at 512.
//! Their default prefactor is the project's gamma^(3/2) normalization; the
//! standard regularization prefactors are intentionally caller-supplied.
//!
//! Matches `positivity.volume_operator` in the Python pipeline. Two exact
//! zero mechanisms (verified in the Python reference and re-tested here):
//! all-a/b references freeze the spins (<q> = 0), and real planes give real
//! Fock amplitudes (<q> = 0 for any triple). Neither implies q|state> = 0.

use crate::fock::FockSpace;
use crate::ops::{j_dot, matvec, su2_ops, CMat};
use nalgebra::{linalg::SymmetricEigen, DMatrix};
use num_complex::Complex64;
use std::collections::BTreeMap;

pub const GAMMA: f64 = 0.2375;

/// Legacy signed-mean proxy on one triple, plus <q>.
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

const MAX_DENSE_VERTEX_BLOCK: usize = 512;

fn q_matrix(space: &FockSpace, triple: (usize, usize, usize)) -> CMat {
    let (i, j, k) = triple;
    let a_ij = j_dot(space, i, j);
    let a_jk = j_dot(space, j, k);
    let comm = &(&a_ij * &a_jk) - &(&a_jk * &a_ij);
    let mut builder = TriMatLike::new(space.dim);
    for (&val, (r, c)) in comm.iter() {
        builder.add(r, c, Complex64::new(0.0, 1.0) * val);
    }
    builder.build()
}

fn active_blocks(
    space: &FockSpace,
    v: &[Complex64],
) -> Result<Vec<(Vec<usize>, Vec<Complex64>)>, String> {
    if v.len() != space.dim {
        return Err("state dimension does not match Fock space".into());
    }
    let mut all: BTreeMap<Vec<u8>, Vec<usize>> = BTreeMap::new();
    let mut active = BTreeMap::<Vec<u8>, bool>::new();
    for idx in 0..space.dim {
        let occ = space.occ(idx);
        let mut key = Vec::with_capacity(space.n + 1);
        let mut total_a = 0u16;
        for e in 0..space.n {
            key.push(occ[2 * e] + occ[2 * e + 1]);
            total_a += occ[2 * e] as u16;
        }
        key.push(total_a as u8);
        all.entry(key.clone()).or_default().push(idx);
        if v[idx].norm_sqr() > 1e-28 {
            active.insert(key, true);
        }
    }
    let mut out = Vec::new();
    for (key, indices) in all {
        if !active.contains_key(&key) {
            continue;
        }
        if indices.len() > MAX_DENSE_VERTEX_BLOCK {
            return Err(format!("active fixed-spin block has dimension {}; exact dense volume evaluation is capped at {}", indices.len(), MAX_DENSE_VERTEX_BLOCK));
        }
        let state = indices.iter().map(|&i| v[i]).collect();
        out.push((indices, state));
    }
    Ok(out)
}

fn dense_positive_sqrt_expectation(
    matrix: &CMat,
    indices: &[usize],
    state: &[Complex64],
) -> Result<f64, String> {
    let m = indices.len();
    if m > MAX_DENSE_VERTEX_BLOCK {
        return Err(format!(
            "active fixed-spin block dimension {m} exceeds dense limit {MAX_DENSE_VERTEX_BLOCK}"
        ));
    }
    // Realify the Hermitian complex matrix H as the symmetric matrix
    // [[Re H, -Im H], [Im H, Re H]]. Its spectrum is duplicated, while the
    // realified state preserves the complex inner product.
    let mut real = DMatrix::<f64>::zeros(2 * m, 2 * m);
    for (ri, &i) in indices.iter().enumerate() {
        for (cj, &j) in indices.iter().enumerate() {
            let h = matrix.get(i, j).copied().unwrap_or_default();
            real[(ri, cj)] = h.re;
            real[(ri, m + cj)] = -h.im;
            real[(m + ri, cj)] = h.im;
            real[(m + ri, m + cj)] = h.re;
        }
    }
    let eig = SymmetricEigen::new(real);
    let mut x = vec![0.0; 2 * m];
    for j in 0..m {
        x[j] = state[j].re;
        x[m + j] = state[j].im;
    }
    let norm2: f64 = x.iter().map(|z| z * z).sum();
    if norm2 <= 0.0 {
        return Ok(0.0);
    }
    let mut value = 0.0;
    let spectral_scale = eig
        .eigenvalues
        .iter()
        .fold(1.0_f64, |scale, &lambda| scale.max(lambda.abs()));
    // Exact kernel eigenvalues acquire O(eps * ||q||) residuals in the
    // dense eigensolver. Since sqrt(|lambda|) magnifies those residuals,
    // discard only values within a scale-aware backward-error tolerance.
    let zero_tol = 64.0 * f64::EPSILON * spectral_scale;
    for col in 0..(2 * m) {
        let amp: f64 = (0..(2 * m))
            .map(|row| eig.eigenvectors[(row, col)] * x[row])
            .sum();
        let lambda = eig.eigenvalues[col];
        if lambda.abs() > zero_tol {
            value += amp * amp * lambda.abs().sqrt();
        }
    }
    Ok(value)
}

/// Rovelli–Smolin vertex volume in the repository's dimensionless J and
/// gamma normalization: gamma^(3/2) sum_{i<j<k} sqrt(|q_ijk|).
/// Each positive triple operator is evaluated spectrally before summing.
pub fn rovelli_smolin_volume(space: &FockSpace, v: &[Complex64]) -> Result<f64, String> {
    rovelli_smolin_volume_with_prefactor(space, v, GAMMA.powf(1.5))
}

pub fn rovelli_smolin_volume_with_prefactor(
    space: &FockSpace,
    v: &[Complex64],
    prefactor: f64,
) -> Result<f64, String> {
    let triples: Vec<_> = (0..space.n)
        .flat_map(|i| {
            ((i + 1)..space.n).flat_map(move |j| ((j + 1)..space.n).map(move |k| (i, j, k)))
        })
        .collect();
    let blocks = active_blocks(space, v)?;
    let norm2: f64 = v.iter().map(|x| x.norm_sqr()).sum();
    if norm2 <= 0.0 {
        return Err("volume expectation requires a nonzero state".into());
    }
    let mut total = 0.0;
    for triple in triples {
        let q = q_matrix(space, triple);
        for (indices, state) in &blocks {
            total += dense_positive_sqrt_expectation(&q, indices, state)?;
        }
    }
    Ok(prefactor * total / norm2)
}

/// Ashtekar–Lewandowski vertex volume in repository normalization.
/// `orientation_signs` follows lexicographic triples and contains each
/// tangent determinant sign (-1, 0, +1). Signs are applied to q before the
/// absolute value and positive square root.
pub fn ashtekar_lewandowski_volume(
    space: &FockSpace,
    v: &[Complex64],
    orientation_signs: &[i8],
) -> Result<f64, String> {
    ashtekar_lewandowski_volume_with_prefactor(space, v, orientation_signs, GAMMA.powf(1.5))
}

pub fn ashtekar_lewandowski_volume_with_prefactor(
    space: &FockSpace,
    v: &[Complex64],
    orientation_signs: &[i8],
    prefactor: f64,
) -> Result<f64, String> {
    let triples: Vec<_> = (0..space.n)
        .flat_map(|i| {
            ((i + 1)..space.n).flat_map(move |j| ((j + 1)..space.n).map(move |k| (i, j, k)))
        })
        .collect();
    if orientation_signs.len() != triples.len()
        || orientation_signs.iter().any(|s| !(-1..=1).contains(s))
    {
        return Err(
            "orientation signs must contain one -1, 0, or +1 per lexicographic edge triple".into(),
        );
    }
    let blocks = active_blocks(space, v)?;
    let norm2: f64 = v.iter().map(|x| x.norm_sqr()).sum();
    if norm2 <= 0.0 {
        return Err("volume expectation requires a nonzero state".into());
    }
    let mut matrices = Vec::with_capacity(triples.len());
    for triple in &triples {
        matrices.push(q_matrix(space, *triple));
    }
    let mut total = 0.0;
    for (indices, state) in &blocks {
        let m = indices.len();
        let mut qsum = DMatrix::<Complex64>::zeros(m, m);
        for (q, &sign) in matrices.iter().zip(orientation_signs) {
            if sign == 0 {
                continue;
            }
            for (ri, &i) in indices.iter().enumerate() {
                for (cj, &j) in indices.iter().enumerate() {
                    qsum[(ri, cj)] += q.get(i, j).copied().unwrap_or_default() * (sign as f64);
                }
            }
        }
        let mut builder = TriMatLike::new(m);
        for i in 0..m {
            for j in 0..m {
                if qsum[(i, j)].norm() > 1e-14 {
                    builder.add(i, j, qsum[(i, j)]);
                }
            }
        }
        let qsum_sparse = builder.build();
        let local_indices: Vec<_> = (0..m).collect();
        total += dense_positive_sqrt_expectation(&qsum_sparse, &local_indices, state)?;
    }
    Ok(prefactor * total / norm2)
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
        TriMatLike {
            dim,
            rows: Vec::new(),
            cols: Vec::new(),
            vals: Vec::new(),
        }
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
                let det = a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
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
    use crate::grassmannian::plane_to_z;
    use crate::grassmannian::positive_plane_curve;

    fn ref_vertex4() -> Vec<(u8, u8)> {
        vec![(1, 1), (1, 1), (1, 0), (1, 0)]
    }

    fn paired_spin_half_singlet(space: &FockSpace) -> Vec<Complex64> {
        // (|up down> - |down up>)_01 x (|up down> - |down up>)_23.
        let mut v = space.zeros();
        for &(s12, s34) in &[(1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0)] {
            let pair = |s: f64| {
                if s > 0.0 {
                    [(1u8, 0u8), (0u8, 1u8)]
                } else {
                    [(0u8, 1u8), (1u8, 0u8)]
                }
            };
            let p12 = pair(s12);
            let p34 = pair(s34);
            let mut occ = vec![0u8; 8];
            for (edge, spin) in [p12[0], p12[1], p34[0], p34[1]].iter().enumerate() {
                occ[2 * edge] = spin.0;
                occ[2 * edge + 1] = spin.1;
            }
            let idx = space.index_of(&occ).unwrap() as usize;
            v[idx] = Complex64::new(0.5 * s12 * s34, 0.0);
        }
        v
    }

    #[test]
    fn rs_and_al_positive_volumes_on_closed_spin_half_vertex() {
        let space = FockSpace::new(4, 4);
        let state = paired_spin_half_singlet(&space);
        let (_, q_mean) = volume_operator(&space, &state, (0, 1, 2));
        let rs = rovelli_smolin_volume(&space, &state).unwrap();
        // Regular tetrahedron tangent signs in lexicographic triple order.
        let al = ashtekar_lewandowski_volume(&space, &state, &[1, -1, 1, -1]).unwrap();
        println!("spin_half_pair_singlet <q012>={q_mean} V_RS={rs:.12} V_AL={al:.12}");
        assert!(q_mean.norm() < 1e-12);
        assert!(rs > 0.0 && al > 0.0);
        assert!((rs - 2.0 * al).abs() < 1e-10, "RS={rs}, AL={al}");
    }

    #[test]
    fn rs_and_al_vanish_on_collinear_product_state() {
        let space = FockSpace::new(4, 4);
        let mut occ = vec![0u8; 8];
        for e in 0..4 {
            occ[2 * e] = 1;
        }
        let mut state = space.zeros();
        state[space.index_of(&occ).unwrap() as usize] = Complex64::new(1.0, 0.0);
        assert!(rovelli_smolin_volume(&space, &state).unwrap() < 1e-12);
        assert!(ashtekar_lewandowski_volume(&space, &state, &[1, -1, 1, -1]).unwrap() < 1e-12);
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
    fn signed_mean_zero_on_real_plane_any_triple() {
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
    fn signed_mean_zero_on_real_plane_outside_positive_cell() {
        let n = 4usize;
        let space = FockSpace::new(n, 6);
        let rows = [[1.0, 0.0, -2.0, -1.0], [0.0, 1.0, 1.0, 1.0]];
        let plane: Vec<Complex64> = rows
            .iter()
            .flatten()
            .map(|&x| Complex64::new(x, 0.0))
            .collect();
        let minors = crate::grassmannian::plucker(&plane, n);
        assert!(minors.iter().any(|m| m.re < 0.0));
        let z = plane_to_z(&plane, n);
        let rv = reference_vector(&space, &ref_vertex4());
        let v = perelomov(&space, &z, &rv, 1e-13);
        let (_proxy, q) = volume_operator(&space, &v, (0, 1, 2));
        assert!(q.norm() < 1e-12, "real off-cell signed mean = {q}");
    }

    #[test]
    fn proxy_nonzero_on_tested_complex_plane() {
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

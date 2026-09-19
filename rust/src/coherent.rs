//! Perelomov U(N) coherent states and area observables.

use crate::fock::FockSpace;
use crate::ops::{generator_matrix, matvec};
use num_complex::Complex64;
use num_traits::{One, Zero};

/// Build the normalized reference vector from per-edge occupations
/// [(n_a, n_b); N] (a single basis state).
pub fn reference_vector(space: &FockSpace, ref_occ: &[(u8, u8)]) -> Vec<Complex64> {
    let mut flat = vec![0u8; 2 * space.n];
    for (i, &(na, nb)) in ref_occ.iter().enumerate() {
        flat[2 * i] = na;
        flat[2 * i + 1] = nb;
    }
    let idx = space.index_of(&flat).expect("reference occupation within K");
    let mut v = space.zeros();
    v[idx as usize] = Complex64::one();
    v
}

/// Perelomov coherent state |Z> = exp(A) |ref> / norm, where
/// A = sum_ij Z_ij E_ij. The Taylor series terminates on the total-K Fock
/// space (A conserves K); we stop early when the increment is below tol.
/// Mirrors `coherent_states.perelomov_state` in the Python pipeline.
pub fn perelomov(
    space: &FockSpace,
    z: &[Complex64],
    ref_vec: &[Complex64],
    tol: f64,
) -> Vec<Complex64> {
    let n = space.n;
    let a = generator_matrix(space, z, n);
    // cap 4K+8: 2K+4 was shown to truncate at large K (T5e audit child).
    let k = 4 * space.k + 8;
    let mut result = ref_vec.to_vec();
    let mut term = ref_vec.to_vec();
    for it in 1..k {
        term = matvec(&a, &term);
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

/// Expectation <v|O|v> for a normalized dense v and sparse O, via matvec.
pub fn expectation(space: &FockSpace, o: &sprs::CsMat<Complex64>, v: &[Complex64]) -> Complex64 {
    let _ = space;
    let w = matvec(o, v);
    v.iter().zip(w).map(|(a, b)| a.conj() * b).sum()
}

/// Mean and uncertainty of edge area A_e = gamma * hbar * n_e.
/// (n_e is diagonal, so <n^2> is exact without a second operator.)
pub fn area_stats(
    space: &FockSpace,
    v: &[Complex64],
    edge: usize,
) -> (f64, f64) {
    // n_e is diagonal: read occupations directly
    let d: Vec<f64> = (0..space.dim)
        .map(|i| (space.occ(i)[2 * edge] + space.occ(i)[2 * edge + 1]) as f64)
        .collect();
    let mean: f64 = v.iter().zip(&d).map(|(x, &di)| di * x.norm_sqr()).sum();
    let mean2: f64 = v
        .iter()
        .zip(&d)
        .map(|(x, &di)| di * di * x.norm_sqr())
        .sum();
    (mean, (mean2 - mean * mean).max(0.0).sqrt())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::grassmannian::{plane_to_z, positive_plane_curve};

    fn ref_vertex4() -> Vec<(u8, u8)> {
        vec![(1, 1), (1, 1), (1, 0), (1, 0)]
    }

    #[test]
    fn closure_sums_to_k() {
        // sum_i <n_i> = total boson number K (u(N) conserves K)
        let n = 4;
        let k = 6;
        let space = FockSpace::new(n, k);
        let plane = positive_plane_curve(n, 11);
        let z = plane_to_z(&plane, n);
        let rv = reference_vector(&space, &ref_vertex4());
        let v = perelomov(&space, &z, &rv, 1e-13);
        let total: f64 = (0..n).map(|e| area_stats(&space, &v, e).0).sum();
        assert!((total - k as f64).abs() < 1e-9, "closure {total}");
    }

    #[test]
    fn exponential_from_empty_vacuum_is_trivial() {
        let space = FockSpace::new(3, 2);
        let mut z = vec![Complex64::zero(); 9];
        z[1] = Complex64::one(); // Z_01
        let rv = reference_vector(&space, &[(0, 0), (0, 0), (0, 0)]);
        let v = perelomov(&space, &z, &rv, 1e-14);
        let nnz = v.iter().filter(|x| x.norm() > 1e-12).count();
        assert_eq!(nnz, 1);
    }
}

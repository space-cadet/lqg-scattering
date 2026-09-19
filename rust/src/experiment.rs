//! Experiment T5a: triple-volume correlations from a single coherent
//! state (spec: memory-bank/implementation-details/experiments.md).
//!
//! From ONE Perelomov state on a complex (off-cell) plane, compute
//! q_ijk = i <[A_ij, A_jk]> with A_ij = J_i . J_j, on every C(n,3) edge
//! triple, then correlate across triples:
//! (1) Pearson correlation of |q| magnitudes, (2) sign-agreement fraction
//! among nonzero triples. Goal: single handedness (correlated) vs
//! per-triple chirality (independent).
//!
//! Identity used: with z = <A_ij psi | A_jk psi> = <psi|A_ij A_jk|psi>
//! (A_ij Hermitian), q = i(z - conj(z)) = -2 Im z.

use crate::coherent::{perelomov, reference_vector};
use crate::fock::FockSpace;
use crate::grassmannian::plane_to_z;
use crate::ops::{j_dot, matvec};
use num_complex::Complex64;

pub struct T5aResult {
    pub n: usize,
    pub triples: Vec<(usize, usize, usize)>,
    pub q: Vec<f64>,
    /// Pearson correlation of |q| across triples (single state: the
    /// correlation is taken over seeds if provided, else reported as the
    /// |q| distribution summary)
    pub abs_q: Vec<f64>,
}

/// All C(n,3) triples, lexicographic.
pub fn all_triples(n: usize) -> Vec<(usize, usize, usize)> {
    let mut out = Vec::new();
    for i in 0..n {
        for j in (i + 1)..n {
            for k in (j + 1)..n {
                out.push((i, j, k));
            }
        }
    }
    out
}

/// q_ijk for every triple, from one state. Pair matrices A_ij are built
/// once and reused across all triples sharing the pair.
pub fn triple_q_all_pairs(
    space: &FockSpace,
    plane: &[Complex64],
    ref_occ: &[(u8, u8)],
    tol: f64,
) -> (Vec<(usize, usize, usize)>, Vec<f64>) {
    let n = space.n;
    let z = plane_to_z(plane, n);
    let rv = reference_vector(space, ref_occ);
    let v = perelomov(space, &z, &rv, tol);

    // Pivot scheme for bounded memory: for each middle edge j, build the
    // n-1 matrices A_ij (i != j) once, compute every q with middle index
    // j, then drop them before the next pivot. Each unordered pair is
    // built exactly once (pairs are owned by their pivot's middle index).
    let triples = all_triples(n);
    let mut by_middle: Vec<Vec<usize>> = vec![Vec::new(); n];
    for (idx, &(_, j, _)) in triples.iter().enumerate() {
        by_middle[j].push(idx);
    }
    let mut qs = vec![0.0f64; triples.len()];
    for j in 0..n {
        // w_i = A_{min(i,j) max(i,j)} psi for all i != j
        let mut w: Vec<Option<Vec<Complex64>>> = vec![None; n];
        for i in 0..n {
            if i == j {
                continue;
            }
            let a = j_dot(space, i.min(j), i.max(j));
            w[i] = Some(matvec(&a, &v));
        }
        for &ti in &by_middle[j] {
            let (i, _, k) = triples[ti];
            let (wi, wk) = match (w[i].as_ref(), w[k].as_ref()) {
                (Some(a), Some(b)) => (a, b),
                _ => unreachable!(),
            };
            let znum: Complex64 = wi.iter().zip(wk).map(|(x, y)| x.conj() * y).sum();
            qs[ti] = -2.0 * znum.im;
        }
    }
    (triples, qs)
}

/// Pearson correlation coefficient between two samples (uses the common
/// prefix if lengths differ).
pub fn pearson(x: &[f64], y: &[f64]) -> f64 {
    let m = x.len().min(y.len());
    let (x, y) = (&x[..m], &y[..m]);
    let mx = x.iter().sum::<f64>() / m as f64;
    let my = y.iter().sum::<f64>() / m as f64;
    let mut cov = 0.0;
    let mut vx = 0.0;
    let mut vy = 0.0;
    for i in 0..m {
        cov += (x[i] - mx) * (y[i] - my);
        vx += (x[i] - mx).powi(2);
        vy += (y[i] - my).powi(2);
    }
    cov / (vx.sqrt() * vy.sqrt())
}

/// Sign-agreement fraction: max(#positive, #negative) / count among
/// triples with |q| above the absolute nonzero threshold.
pub fn sign_agreement(qs: &[f64], nonzero_tol: f64) -> (f64, usize, usize, usize) {
    let live: Vec<f64> = qs.iter().copied().filter(|&q| q.abs() > nonzero_tol).collect();
    if live.is_empty() {
        return (0.0, 0, 0, qs.len());
    }
    let pos = live.iter().filter(|&&q| q > 0.0).count();
    let neg = live.len() - pos;
    (pos.max(neg) as f64 / live.len() as f64, pos, neg, qs.len())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::grassmannian::positive_plane_curve;
    use crate::volume::GAMMA;

    #[test]
    fn n4_sign_matches_python() {
        // Python positivity.py reference: plane = positive_region_N4(1,2,
        // 0.5,1.5) + dC, ref [(1,1),(1,1),(1,0),(1,0)], triple (0,1,2):
        // <q> = -8.496572e-04. Exercise q = -2 Im <A01 psi|A12 psi>.
        let n = 4;
        let space = FockSpace::new(n, 6);
        let base: [[f64; 4]; 2] = [
            [1.0, 0.0, -0.5, -1.5],
            [0.0, 1.0, 1.0, 2.0],
        ];
        let im: [[f64; 4]; 2] = [
            [0.0, 0.0, 0.3, 0.2],
            [0.0, 0.0, 0.0, 0.3],
        ];
        let re: [[f64; 4]; 2] = [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, -0.5, 0.0],
        ];
        let plane: Vec<Complex64> = base.iter().flat_map(|r| r.iter())
            .zip(im.iter().flat_map(|r| r.iter()))
            .zip(re.iter().flat_map(|r| r.iter()))
            .map(|((&b, &i), &r)| Complex64::new(b + r, i))
            .collect();
        let (_, qs) = triple_q_all_pairs(&space, &plane, &[(1, 1), (1, 1), (1, 0), (1, 0)], 1e-13);
        assert_eq!(qs.len(), 4);
        assert!(
            (qs[0] - (-8.496572e-04)).abs() < 1e-9,
            "q_012 = {:.9}, expected -8.496572e-04",
            qs[0]
        );
        let _ = GAMMA;
    }

    #[test]
    fn pearson_perfect() {
        assert!((pearson(&[1.0, 2.0, 3.0], &[2.0, 4.0, 6.0]) - 1.0).abs() < 1e-12);
        assert!((pearson(&[1.0, 2.0, 3.0], &[6.0, 4.0, 2.0]) + 1.0).abs() < 1e-12);
    }
}

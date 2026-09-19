//! Grassmannian Gr(2, N) helpers: Plücker minors, the momentum map
//! plane -> u(N)*, and random positive planes via the moment curve.

use num_complex::Complex64;
use num_traits::Zero;

/// All Plücker minors M_ij = C_{1i} C_{2j} - C_{1j} C_{2i}, i < j.
pub fn plucker(plane: &[Complex64], n: usize) -> Vec<Complex64> {
    let at = |r: usize, c: usize| plane[r * n + c];
    let mut out = Vec::with_capacity(n * (n - 1) / 2);
    for i in 0..n {
        for j in (i + 1)..n {
            out.push(at(0, i) * at(1, j) - at(0, j) * at(1, i));
        }
    }
    out
}

/// Momentum map Gr(2, N) -> u(N)*: orthonormalize the two rows (a, b) and
/// return Z_ij = a_i conj(b_j) - b_i conj(a_j), row-major N x N.
/// Z is anti-Hermitian. Panics on degenerate planes.
pub fn plane_to_z(plane: &[Complex64], n: usize) -> Vec<Complex64> {
    let at = |r: usize, c: usize| plane[r * n + c];
    let mut a: Vec<Complex64> = (0..n).map(|i| at(0, i)).collect();
    let mut b: Vec<Complex64> = (0..n).map(|i| at(1, i)).collect();
    let norm = |v: &[Complex64]| v.iter().map(|x| x.norm_sqr()).sum::<f64>().sqrt();
    let na = norm(&a);
    assert!(na > 1e-14, "degenerate plane row");
    for x in a.iter_mut() {
        *x /= na;
    }
    // Gram-Schmidt: b -= a (a . b)
    let ip: Complex64 = (0..n).map(|i| a[i].conj() * b[i]).sum();
    for i in 0..n {
        b[i] -= ip * a[i];
    }
    let nb = norm(&b);
    assert!(nb > 1e-14, "parallel plane rows");
    for x in b.iter_mut() {
        *x /= nb;
    }
    let mut z = vec![Complex64::zero(); n * n];
    for i in 0..n {
        for j in 0..n {
            z[i * n + j] = a[i] * b[j].conj() - b[i] * a[j].conj();
        }
    }
    z
}

/// Random positive plane in Gr+(2, N): columns (t_i, t_i^2) on the moment
/// curve give M_ij = t_i t_j (t_j - t_i) > 0 for i < j. Deterministic
/// (splitmix64) via `seed`.
pub fn positive_plane_curve(n: usize, seed: u64) -> Vec<Complex64> {
    // tiny deterministic PRNG, output in (0, 1)
    let mut s = seed.wrapping_add(0x9e3779b97f4a7c15);
    let mut unit = move || {
        s = (s ^ (s >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        s = (s ^ (s >> 27)).wrapping_mul(0x94d049bb133111eb);
        s ^= s >> 31;
        (s >> 11) as f64 / (1u64 << 53) as f64
    };
    let mut t: Vec<f64> = (0..n).map(|_| unit()).collect();
    t.sort_by(|x, y| x.partial_cmp(y).unwrap());
    let mut plane = vec![Complex64::zero(); 2 * n];
    for i in 0..n {
        plane[i] = Complex64::new(t[i], 0.0);
        plane[n + i] = Complex64::new(t[i] * t[i], 0.0);
    }
    plane
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn minors_match_definition() {
        // C = [[1, 2], [3, 4]]: M_01 = 1*4 - 2*3 = -2
        let c = vec![
            Complex64::new(1.0, 0.0),
            Complex64::new(2.0, 0.0),
            Complex64::new(3.0, 0.0),
            Complex64::new(4.0, 0.0),
        ];
        let m = plucker(&c, 2);
        assert_eq!(m.len(), 1);
        assert!((m[0] - Complex64::new(-2.0, 0.0)).norm() < 1e-14);
    }

    #[test]
    fn momentum_map_antihermitian() {
        let n = 5;
        let plane = positive_plane_curve(n, 7);
        let z = plane_to_z(&plane, n);
        for i in 0..n {
            for j in 0..n {
                assert!((z[i * n + j] + z[j * n + i].conj()).norm() < 1e-12);
            }
        }
    }

    #[test]
    fn moment_curve_is_positive() {
        // all minors real and positive
        let plane = positive_plane_curve(6, 3);
        for m in plucker(&plane, 6) {
            assert!(m.im.abs() < 1e-15 && m.re > 0.0, "minor {m}");
        }
    }
}

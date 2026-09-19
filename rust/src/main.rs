//! Verification binary: reproduces the Python n = 4 reference numbers
//! (positive plane vs. complex-perturbed plane) and prints them for
//! comparison. Usage: lqg [n]

use lqg_grassmannian::coherent::{area_stats, perelomov, reference_vector};
use lqg_grassmannian::fock::FockSpace;
use lqg_grassmannian::grassmannian::plane_to_z;
use lqg_grassmannian::volume::{volume_operator, GAMMA};
use num_complex::Complex64;

/// The n = 4 canonical positive plane used throughout the Python pipeline:
/// positive_region_N4(a=1, b=2, c=0.5, d=1.5).
fn positive_plane_n4() -> Vec<Complex64> {
    let rows: [[f64; 4]; 2] = [
        [1.0, 0.0, -0.5, -1.5],
        [0.0, 1.0, 1.0, 2.0],
    ];
    rows.iter()
        .flat_map(|r| r.iter().map(|&x| Complex64::new(x, 0.0)))
        .collect()
}

fn main() {
    let n = std::env::args()
        .nth(1)
        .and_then(|s| s.parse::<usize>().ok())
        .unwrap_or(4);
    let k = 6;
    let space = FockSpace::new(n, k);
    let ref_occ: Vec<(u8, u8)> = if n == 4 {
        vec![(1, 1), (1, 1), (1, 0), (1, 0)]
    } else {
        // a-boson on every edge, b-bosons on the volume triple (0,1,2)
        let mut r = vec![(1u8, 0u8); n];
        for e in r.iter_mut().take(3) {
            e.1 = 1;
        }
        r
    };
    // k must equal total occupation
    let k_actual: usize = ref_occ.iter().map(|&(a, b)| (a + b) as usize).sum();
    assert_eq!(k_actual, k, "reference occupation must sum to K={k}");

    let plane = positive_plane_n4();
    // complex perturbation identical to positivity.py's
    // dC = [[0, 0, 0.3j, 0.2j], [0, 0, -0.5, 0.3j]]
    let d_c: [[f64; 4]; 2] = [
        [0.0, 0.0, 0.3, 0.2],
        [0.0, 0.0, 0.0, 0.3],
    ];
    let d_real: [[f64; 4]; 2] = [
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, -0.5, 0.0],
    ];
    let planes: Vec<(&str, Vec<Complex64>)> = vec![
        ("positive", plane.clone()),
        (
            "complex",
            plane
                .iter()
                .zip(d_c.iter().flat_map(|r| r.iter()))
                .zip(d_real.iter().flat_map(|r| r.iter()))
                .map(|((&p, &di), &dr)| p + Complex64::new(dr, di))
                .collect(),
        ),
    ];

    let rv = reference_vector(&space, &ref_occ);
    for (name, pl) in planes {
        let z = plane_to_z(&pl, n);
        let t0 = std::time::Instant::now();
        let v = perelomov(&space, &z, &rv, 1e-13);
        let dt = t0.elapsed();
        let areas: Vec<String> = (0..n)
            .map(|e| {
                let (m, u) = area_stats(&space, &v, e);
                format!("{m:.6} +- {u:.6}")
            })
            .collect();
        let closure: f64 = (0..n).map(|e| area_stats(&space, &v, e).0).sum();
        let (vol, q) = volume_operator(&space, &v, (0, 1, 2));
        println!(
            "n={n} [{name}] areas <n_e> = [{}]  closure={closure:.9}  \
             V/(gamma*hbar)^1.5={:.6e}  <q>={:+.6e}  ({:.2?})",
            areas.join(", "),
            vol / GAMMA.powf(1.5),
            q.re,
            dt
        );
    }
}

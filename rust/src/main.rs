//! Verification binary: reproduces the Python n = 4 reference numbers
//! (positive plane vs. complex-perturbed plane) and prints them for
//! comparison. Usage: lqg [n]

use lqg_grassmannian::coherent::{area_stats, perelomov, reference_vector};
use lqg_grassmannian::fock::FockSpace;
use lqg_grassmannian::grassmannian::{plane_to_z, positive_plane_curve};
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
    let args: Vec<String> = std::env::args().collect();
    let mode = args.get(1).map(|s| s.as_str()).unwrap_or("verify4");
    match mode {
        "verify4" => verify4(),
        "scan" => scan(),
        _ => {
            eprintln!("usage: lqg [verify4|scan]");
            std::process::exit(2);
        }
    }
}

/// n = 4 verification against the Python pipeline (positivity.py):
/// canonical positive plane and its complex perturbation dC, reference
/// occupations [(1,1),(1,1),(1,0),(1,0)] (K = 6).
fn verify4() {
    let n = 4;
    let k = 6;
    let space = FockSpace::new(n, k);
    let ref_occ: Vec<(u8, u8)> = vec![(1, 1), (1, 1), (1, 0), (1, 0)];

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

/// Higher-n benchmark: random positive plane (moment curve) vs. the same
/// plane with an imaginary perturbation, for n = 5..8. References: full
/// vertex (a on every edge, b on the triple) for n <= 6; triple-local
/// (K = 6) for n >= 7 to keep the Fock space moderate.
fn scan() {
    println!("{:>3} {:>10} {:>14} {:>14} {:>10}", "n", "K", "dim", "V/g^1.5", "time");
    for n in 5..=8usize {
        let ref_occ: Vec<(u8, u8)> = if n <= 6 {
            let mut r = vec![(1u8, 0u8); n];
            for e in r.iter_mut().take(3) {
                e.1 = 1;
            }
            r
        } else {
            let mut r = vec![(0u8, 0u8); n];
            for e in r.iter_mut().take(3) {
                *e = (1, 1);
            }
            r
        };
        let k: usize = ref_occ.iter().map(|&(a, b)| (a + b) as usize).sum();
        let space = FockSpace::new(n, k);
        let plane = positive_plane_curve(n, 100 + n as u64);
        // imaginary perturbation violating the minor-phase cocycle
        let mut cplane = plane.clone();
        for i in 0..n {
            cplane[n + i] += Complex64::new(0.0, 0.35 * (i as f64 + 0.5));
        }
        let rv = reference_vector(&space, &ref_occ);
        for (name, pl) in [("positive", &plane), ("complex", &cplane)] {
            let z = plane_to_z(pl, n);
            let t0 = std::time::Instant::now();
            let v = perelomov(&space, &z, &rv, 1e-13);
            let (vol, q) = volume_operator(&space, &v, (0, 1, 2));
            let dt = t0.elapsed();
            println!(
                "{n:>3} {k:>10} {:>14} {:>14.6e} {:>10.2?}",
                space.dim,
                vol / GAMMA.powf(1.5),
                dt
            );
            if name == "positive" {
                assert!(q.norm() < 1e-10, "V must vanish on Gr+(2,{n})");
            } else {
                assert!(vol > 1e-6, "V must be nonzero off Gr+(2,{n})");
            }
        }
    }
}

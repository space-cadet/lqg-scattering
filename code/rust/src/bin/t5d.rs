//! T5d: relate the signed triple grasp to a gauge-invariant Pluecker phase.
//!
//! Fixed n=4, K=7 vertex reference. The complex path adds an imaginary
//! perturbation to the second row of a positive moment-curve plane. Real
//! positive and mixed-sign controls must both have zero phase defect and
//! zero signed grasp.

use lqg_grassmannian::grassmannian::{plane_to_z, plucker, positive_plane_curve};
use lqg_grassmannian::onthefly::{apply_jdot, perelomov_otf_diag, OtfSpace};
use num_complex::Complex64;

const N: usize = 4;
const SEED: u64 = 11;
const EPSILONS: [f64; 8] = [0.0, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 0.1, 1.0];

fn phase_defect(plane: &[Complex64]) -> (f64, f64) {
    // Pluecker cross ratio M_01 M_23 / (M_02 M_13) is invariant under
    // GL(2) row changes and independent rescalings of the four columns.
    let m = plucker(plane, N);
    let cross_ratio = m[0] * m[5] / (m[1] * m[4]);
    let defect = cross_ratio.im.abs() / cross_ratio.norm();
    (cross_ratio.arg(), defect)
}

fn signed_grasp(space: &OtfSpace, plane: &[Complex64]) -> (f64, usize) {
    let z = plane_to_z(plane, N);
    let reference = [(1, 1), (1, 1), (1, 1), (1, 0)];
    let (state, iters, converged) =
        perelomov_otf_diag(space, &z, &reference, 1.0e-13, 8 * space.k + 50);
    assert!(converged, "T5d Perelomov exponential did not converge");
    let a01 = apply_jdot(space, 0, 1, &state);
    let a12 = apply_jdot(space, 1, 2, &state);
    let overlap: Complex64 = a01.iter().zip(&a12).map(|(x, y)| x.conj() * y).sum();
    (-2.0 * overlap.im, iters)
}

fn point_json(label: &str, epsilon: f64, plane: &[Complex64], space: &OtfSpace) -> String {
    let (phase, defect) = phase_defect(plane);
    let (q, iters) = signed_grasp(space, plane);
    format!(
        "    {{\"control\":\"{label}\",\"epsilon\":{epsilon:.8e},\"phaseRadians\":{phase:.12e},\"phaseDefect\":{defect:.12e},\"signedGrasp\":{q:.12e},\"taylorIters\":{iters}}}"
    )
}

fn main() {
    let space = OtfSpace::new(N, 7);
    let base = positive_plane_curve(N, SEED);
    let mut rows = Vec::new();

    let positive = base.clone();
    rows.push(point_json("positive_real", 0.0, &positive, &space));

    let mut mixed_sign = base.clone();
    mixed_sign[0] = -mixed_sign[0];
    rows.push(point_json("mixed_sign_real", 0.0, &mixed_sign, &space));

    for epsilon in EPSILONS {
        let mut plane = base.clone();
        for i in 0..N {
            plane[N + i] += Complex64::new(0.0, epsilon * 0.35 * (i as f64 + 0.5));
        }
        rows.push(point_json("complex_path", epsilon, &plane, &space));
    }
    println!(
        "{{\"study\":\"T5d cocycle phase pilot\",\"n\":4,\"K\":7,\"seed\":{SEED},\"points\":[\n{}\n]}}",
        rows.join(",\n")
    );
}

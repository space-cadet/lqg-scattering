//! Evaluate the equal-area FL fixed-area state on the T5c fixed-x shape path.
//!
//! Usage: cargo run --release --example fl_volume_scan -- <J> <phi-radians>

use lqg_grassmannian::fock::FockSpace;
use lqg_grassmannian::volume::{ashtekar_lewandowski_volume, rovelli_smolin_volume};
use num_complex::Complex64;
use std::env;

fn spinor(theta: f64, phi: f64) -> [Complex64; 2] {
    let scale = 1.0 / 2.0_f64.sqrt(); // equal area fractions a_i = 1/4
    [
        Complex64::new(scale * (theta / 2.0).cos(), 0.0),
        Complex64::from_polar(scale * (theta / 2.0).sin(), phi),
    ]
}

fn bracket(left: [Complex64; 2], right: [Complex64; 2]) -> Complex64 {
    left[0] * right[1] - left[1] * right[0]
}

fn create_pair(space: &FockSpace, state: &[Complex64], i: usize, j: usize) -> Vec<Complex64> {
    let mut out = space.zeros();
    for (column, amplitude) in state.iter().enumerate() {
        if amplitude.norm_sqr() == 0.0 {
            continue;
        }
        let occupation = space.occ(column);
        let mut first = occupation.to_vec();
        let factor_first = (((first[2 * i] + 1) as f64) * ((first[2 * j + 1] + 1) as f64)).sqrt();
        first[2 * i] += 1;
        first[2 * j + 1] += 1;
        let row_first = space
            .index_of(&first)
            .expect("pair creation remains within K");
        out[row_first as usize] += amplitude * factor_first;

        let mut second = occupation.to_vec();
        let factor_second =
            (((second[2 * j] + 1) as f64) * ((second[2 * i + 1] + 1) as f64)).sqrt();
        second[2 * j] += 1;
        second[2 * i + 1] += 1;
        let row_second = space
            .index_of(&second)
            .expect("pair creation remains within K");
        out[row_second as usize] -= amplitude * factor_second;
    }
    out
}

fn determinant(a: [f64; 3], b: [f64; 3], c: [f64; 3]) -> f64 {
    a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: fl_volume_scan <J> <phi-radians>");
        std::process::exit(2);
    }
    let j: usize = args[1].parse().expect("J must be a positive integer");
    let phi: f64 = args[2].parse().expect("phi must be a finite number");
    assert!(j > 0 && j <= 127, "J must be in 1..=127");
    assert!(phi.is_finite() && (0.0..=std::f64::consts::FRAC_PI_2).contains(&phi));

    let x = 1.0 / 3.0_f64.sqrt();
    let transverse = (1.0 - x * x).sqrt();
    let normals = [
        [transverse, 0.0, x],
        [-transverse, 0.0, x],
        [transverse * phi.cos(), transverse * phi.sin(), -x],
        [-transverse * phi.cos(), -transverse * phi.sin(), -x],
    ];
    let spinors: Vec<_> = normals
        .iter()
        .map(|n| spinor(n[2].acos(), n[1].atan2(n[0])))
        .collect();

    let space = FockSpace::new(4, 2 * j);
    let mut state = space.zeros();
    state[space.index_of(&[0; 8]).unwrap() as usize] = Complex64::new(1.0, 0.0);
    for _ in 0..j {
        let mut next = space.zeros();
        for i in 0..4 {
            for k in (i + 1)..4 {
                let coefficient = bracket(spinors[k], spinors[i]);
                let created = create_pair(&space, &state, i, k);
                for (dst, value) in next.iter_mut().zip(created) {
                    *dst += coefficient * value;
                }
            }
        }
        state = next;
    }
    let norm = state.iter().map(|z| z.norm_sqr()).sum::<f64>().sqrt();
    state.iter_mut().for_each(|z| *z /= norm);

    let rs = rovelli_smolin_volume(&space, &state).expect("RS volume evaluation");
    let al =
        ashtekar_lewandowski_volume(&space, &state, &[1, -1, 1, -1]).expect("AL volume evaluation");
    let face = |i: usize| normals[i].map(|v| v / 4.0);
    let classical =
        ((2.0 / 9.0) * determinant(face(1), face(2), face(3)).abs()).sqrt() * 0.2375_f64.powf(1.5);
    let j32 = (j as f64).powf(1.5);
    let geometry_rs = 2.0_f64.sqrt() / 12.0;
    let geometry_al = 2.0_f64.sqrt() / 6.0;

    println!(
        "{{\"J\":{j},\"phiRadians\":{phi:.17},\"ambientDimension\":{},\"norm\":{:.16},\"classicalProject\":{classical:.17e},\"rsMeanOverJ32\":{:.17e},\"alMeanOverJ32\":{:.17e},\"rsGeometryMatched\":{:.17e},\"alGeometryMatched\":{:.17e}}}",
        space.dim,
        state.iter().map(|z| z.norm_sqr()).sum::<f64>(),
        rs / j32,
        al / j32,
        geometry_rs * rs / j32,
        geometry_al * al / j32,
    );
}

//! Evaluate the FL Eq. (38) fixed-area state on a regular tetrahedron.

use lqg_grassmannian::fock::FockSpace;
use lqg_grassmannian::volume::{
    ashtekar_lewandowski_volume, rovelli_smolin_volume, volume_operator,
};
use num_complex::Complex64;

fn spinor(theta: f64, phi: f64) -> [Complex64; 2] {
    [
        Complex64::new((theta / 2.0).cos(), 0.0),
        Complex64::from_polar((theta / 2.0).sin(), phi),
    ]
}

fn bracket(left: [Complex64; 2], right: [Complex64; 2]) -> Complex64 {
    left[0] * right[1] - left[1] * right[0]
}

fn create_pair(
    space: &FockSpace,
    state: &[Complex64],
    i: usize,
    j: usize,
) -> Vec<Complex64> {
    let mut out = space.zeros();
    for (column, amplitude) in state.iter().enumerate() {
        if amplitude.norm_sqr() == 0.0 {
            continue;
        }
        let occupation = space.occ(column);
        let mut first = occupation.to_vec();
        let factor_first =
            (((first[2 * i] + 1) as f64) * ((first[2 * j + 1] + 1) as f64)).sqrt();
        first[2 * i] += 1;
        first[2 * j + 1] += 1;
        let row_first = space.index_of(&first).expect("pair creation remains within K");
        out[row_first as usize] += amplitude * factor_first;

        let mut second = occupation.to_vec();
        let factor_second =
            (((second[2 * j] + 1) as f64) * ((second[2 * i + 1] + 1) as f64)).sqrt();
        second[2 * j] += 1;
        second[2 * i + 1] += 1;
        let row_second = space.index_of(&second).expect("pair creation remains within K");
        out[row_second as usize] -= amplitude * factor_second;
    }
    out
}

fn main() {
    let normals = [
        [1.0, 1.0, 1.0],
        [1.0, -1.0, -1.0],
        [-1.0, 1.0, -1.0],
        [-1.0, -1.0, 1.0],
    ];
    let root = 3.0_f64.sqrt();
    let spinors: Vec<_> = normals
        .iter()
        .map(|n| {
            let x = n[0] / root;
            let y = n[1] / root;
            let z = n[2] / root;
            spinor(z.acos(), y.atan2(x))
        })
        .collect();

    let space = FockSpace::new(4, 4); // J=2 gives K=2J=4 bosons.
    let mut state = space.zeros();
    state[space.index_of(&[0; 8]).unwrap() as usize] = Complex64::new(1.0, 0.0);
    for _ in 0..2 {
        let mut next = space.zeros();
        for i in 0..4 {
            for j in (i + 1)..4 {
                // F_z^dagger = sum_{i<j} [z_j|z_i> F_ij^dagger.
                let coefficient = bracket(spinors[j], spinors[i]);
                let created = create_pair(&space, &state, i, j);
                for (dst, value) in next.iter_mut().zip(created) {
                    *dst += coefficient * value;
                }
            }
        }
        state = next;
    }
    let norm = state.iter().map(|z| z.norm_sqr()).sum::<f64>().sqrt();
    state.iter_mut().for_each(|z| *z /= norm);

    let (proxy, q) = volume_operator(&space, &state, (0, 1, 2));
    let rs = rovelli_smolin_volume(&space, &state).expect("RS volume");
    let al =
        ashtekar_lewandowski_volume(&space, &state, &[1, -1, 1, -1]).expect("AL volume");
    println!("norm={:.16}", state.iter().map(|z| z.norm_sqr()).sum::<f64>());
    println!("q_012={:+.15e}{:+.3e}i proxy={:.15e}", q.re, q.im, proxy);
    println!("V_RS={:.15e} V_AL={:.15e}", rs, al);
}

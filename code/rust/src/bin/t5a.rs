//! T5a driver: triple-volume correlations from coherent states.
//! Usage: t5a <n> [seed ...]
//!
//! With multiple seeds, computes the ensemble statistics of the spec:
//! Pearson correlation of |q| magnitudes across states, plus per-state
//! sign-agreement fractions.

use lqg_grassmannian::experiment::{all_triples, pearson, sign_agreement};
use lqg_grassmannian::fock::FockSpace;
use lqg_grassmannian::grassmannian::{plane_to_z, positive_plane_curve};
use lqg_grassmannian::onthefly::{apply_jdot, perelomov_otf, OtfSpace};
use lqg_grassmannian::volume::GAMMA;
use num_complex::Complex64;

fn run_one(n: usize, seed: u64, ref_occ: &[(u8, u8)]) -> Vec<f64> {
    // one complex (off-cell) plane: moment curve + imaginary perturbation
    let mut plane = positive_plane_curve(n, seed);
    for i in 0..n {
        plane[n + i] += Complex64::new(0.0, 0.35 * (i as f64 + 0.5));
    }
    if n <= 6 {
        let k: usize = ref_occ.iter().map(|&(a, b)| (a + b) as usize).sum();
        let space = FockSpace::new(n, k);
        lqg_grassmannian::experiment::triple_q_all_pairs(&space, &plane, ref_occ, 1e-13).1
    } else {
        // on-the-fly engine: Fock space too large to store sparse operators
        let k: usize = ref_occ.iter().map(|&(a, b)| (a + b) as usize).sum();
        let space = OtfSpace::new(n, k);
        eprintln!("otf space ready, dim={}", space.dim);
        let z = plane_to_z(&plane, n);
        let v = perelomov_otf(&space, &z, ref_occ, 1e-13);
        eprintln!("state ready");
        let triples = all_triples(n);
        let mut qs = vec![0.0f64; triples.len()];
        // pivot scheme: for each middle edge j, compute w_i = A_ij psi for
        // all i != j, then all pairwise dots in one pass
        let mut by_middle: Vec<Vec<usize>> = vec![Vec::new(); n];
        for (idx, &(_, j, _)) in triples.iter().enumerate() {
            by_middle[j].push(idx);
        }
        for j in 0..n {
            let mut w: Vec<Option<Vec<Complex64>>> = vec![None; n];
            for i in 0..n {
                if i == j {
                    continue;
                }
                w[i] = Some(apply_jdot(&space, i.min(j), i.max(j), &v));
            }
            for &ti in &by_middle[j] {
                let (i, _, k) = triples[ti];
                let (wi, wk) = (w[i].as_ref().unwrap(), w[k].as_ref().unwrap());
                let znum: Complex64 =
                    wi.iter().zip(wk).map(|(x, y)| x.conj() * y).sum();
                qs[ti] = -2.0 * znum.im;
            }
            estderr_pivot(j);
        }
        qs
    }
}

#[allow(clippy::needless_range_loop)]
fn estderr_pivot(j: usize) {
    eprintln!("pivot {j} done");
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let n: usize = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(6);
    let seeds: Vec<u64> = if args.len() > 2 {
        args[2..].iter().map(|s| s.parse().unwrap()).collect()
    } else {
        vec![1000]
    };

    // uniform reference (1,1) on every edge: no triple privileged
    let ref_occ: Vec<(u8, u8)> = vec![(1, 1); n];
    let k: usize = ref_occ.iter().map(|&(a, b)| (a + b) as usize).sum();

    let mut all_q: Vec<Vec<f64>> = Vec::new();
    for &seed in &seeds {
        let t0 = std::time::Instant::now();
        let qs = run_one(n, seed, &ref_occ);
        let dt = t0.elapsed();
        all_q.push(qs.clone());

        let abs_q: Vec<f64> = qs.iter().map(|q| q.abs()).collect();
        let max_abs = abs_q.iter().cloned().fold(0.0, f64::max);
        let (agree, pos, neg, total) = sign_agreement(&qs, 1e-9);
        let mean_abs = abs_q.iter().sum::<f64>() / abs_q.len() as f64;
        let var_abs =
            abs_q.iter().map(|x| (x - mean_abs).powi(2)).sum::<f64>() / abs_q.len() as f64;

        println!("T5a n={n} seed={seed} K={k} time={dt:.2?}");
        println!(
            "  |q|: max={max_abs:.6e} mean={mean_abs:.6e} std={:.6e}",
            var_abs.sqrt()
        );
        println!("  nonzero triples: {pos} pos + {neg} neg of {total}");
        println!("  sign-agreement fraction: {agree:.4}");
        for (t, q) in all_triples(n).iter().zip(&qs) {
            println!(
                "    q_{}{}{} = {:+.6e}   V/g^1.5 = {:.6e}",
                t.0 + 1,
                t.1 + 1,
                t.2 + 1,
                q,
                q.abs().sqrt() / GAMMA.powf(1.5)
            );
        }
    }

    // ensemble statistics across seeds: Pearson of |q| magnitudes and of
    // signed q between every pair of states
    if all_q.len() >= 2 {
        let abs_all: Vec<Vec<f64>> = all_q
            .iter()
            .map(|qs| qs.iter().map(|q| q.abs()).collect())
            .collect();
        for a in 0..all_q.len() {
            for b in (a + 1)..all_q.len() {
                let m = all_q[a].len().min(all_q[b].len());
                let r_abs = pearson(&abs_all[a][..m], &abs_all[b][..m]);
                let r_sg = pearson(&all_q[a][..m], &all_q[b][..m]);
                println!(
                    "  seeds {} vs {}: Pearson |q| = {r_abs:.4}, signed q = {r_sg:.4}",
                    seeds[a], seeds[b]
                );
            }
        }
    }
}

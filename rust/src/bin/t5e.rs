//! T5e driver: large-K semiclassical scaling V(K) ~ K^alpha.
//!
//! Fixed shape (moment-curve positive plane + fixed imaginary perturbation
//! breaking the minor-phase cocycle), fixed triple (0,1,2), fixed n=4.
//! Total boson number K is varied through M=0 uniform-area reference
//! occupations: per-edge total m = K/4, a/b split evenly (alternating
//! orientation for odd m so global M stays 0 and every edge keeps both
//! species -- no spin freezing).
//!
//! Single engine: on-the-fly (no stored operators; validated against the
//! stored engine in lib tests). q = -2 Im <A_ij psi | A_jk psi>.
//!
//! Usage: t5e [--seed 11] [--ks 8,12,16,20,24] [--out t5e_results.json]
//!         [--xcheck] [--controls]
//!   --xcheck: also run the stored engine where dim < 200k and compare.
//!   --controls: real-plane (eps=0) zero check at min and max K.
//!
//! The JSON out file is rewritten after every K, so a kill/OOM leaves the
//! completed points behind (checkpoint rule).

use lqg_grassmannian::grassmannian::{plane_to_z, positive_plane_curve};
use lqg_grassmannian::onthefly::{apply_jdot, perelomov_otf, OtfSpace};
use lqg_grassmannian::volume::GAMMA;
use num_complex::Complex64;
use std::time::Instant;

const N: usize = 4;
const TRIPLE: (usize, usize, usize) = (0, 1, 2);

/// Uniform-area reference for total K = 4*m (m >= 2): every edge carries
/// total m, split as evenly as possible, global M = 0 always.
/// Even m: (m/2,m/2) on all edges. Odd m: ((m+1)/2,(m-1)/2) on edges 0,1
/// and swapped on 2,3 (2/2 orientation split keeps M=0 with uniform area;
/// the even-m subset is additionally shape-uniform -- fittable alone).
fn ref_m0(k: usize) -> Vec<(u8, u8)> {
    assert!(k % 4 == 0 && k >= 8, "K must be a multiple of 4, >= 8");
    let m = k / 4;
    if m % 2 == 0 {
        vec![(m as u8 / 2, m as u8 / 2); N]
    } else {
        let hi = ((m + 1) / 2) as u8;
        let lo = ((m - 1) / 2) as u8;
        vec![(hi, lo), (hi, lo), (lo, hi), (lo, hi)]
    }
}

/// T5b-style vertex reference (K = N+3 = 7): one a-boson per edge + one
/// b-boson on each edge of the volume triple. Regression point only.
fn ref_vertex() -> Vec<(u8, u8)> {
    let mut r = vec![(1u8, 0u8); N];
    for &e in &[TRIPLE.0, TRIPLE.1, TRIPLE.2] {
        r[e].1 = 1;
    }
    r
}

/// Vertex-scaled family: (1,0) on every edge + (0,s) on each triple edge,
/// K = 4 + 3*s. Concentrates the b-bosons on the measured triple (maximal
/// consistent signal); edge 3 stays spin-1/2 (lopsided limit -- caveat).
fn ref_vertex_scaled(k: usize) -> Vec<(u8, u8)> {
    assert!(k >= 7 && (k - 4) % 3 == 0, "vertex K must be 4+3s, >= 7");
    let s = ((k - 4) / 3) as u8;
    let mut r = vec![(1u8, 0u8); N];
    for &e in &[TRIPLE.0, TRIPLE.1, TRIPLE.2] {
        r[e].1 = s;
    }
    r
}

/// Complex (off-cell) plane: moment curve + fixed imag perturbation
/// dC[1,i] = i*0.35*(i+0.5), eps = 1 (same shape as the scan/t5a driver).
fn complex_plane(seed: u64) -> Vec<Complex64> {
    let mut plane = positive_plane_curve(N, seed);
    for i in 0..N {
        plane[N + i] += Complex64::new(0.0, 0.35 * (i as f64 + 0.5));
    }
    plane
}

struct Point {
    k: usize,
    dim: usize,
    ref_occ: Vec<(u8, u8)>,
    q: f64,
    v: f64,
    closure: f64,
    secs: f64,
}

fn run_k(seed: u64, k: usize, ref_occ: &[(u8, u8)], eps_zero: bool) -> Point {
    let space = OtfSpace::new(N, k);
    let plane = if eps_zero {
        positive_plane_curve(N, seed)
    } else {
        complex_plane(seed)
    };
    let z = plane_to_z(&plane, N);
    let t0 = Instant::now();
    let v = perelomov_otf(&space, &z, ref_occ, 1e-13);
    // closure: sum_e <n_e> must equal K (u(N) conservation)
    let mut closure = 0.0f64;
    for (amp, idx) in v.iter().zip(0..space.dim) {
        let o = space.occ(idx);
        let tot: f64 = o.iter().map(|&x| x as f64).sum();
        closure += amp.norm_sqr() * tot;
    }
    let (i, j, kk) = TRIPLE;
    let wij = apply_jdot(&space, i.min(j), i.max(j), &v);
    let wjk = apply_jdot(&space, j.min(kk), j.max(kk), &v);
    let zdot: Complex64 = wij.iter().zip(&wjk).map(|(x, y)| x.conj() * y).sum();
    let q = -2.0 * zdot.im;
    let dt = t0.elapsed().as_secs_f64();
    let vol = GAMMA.powf(1.5) * q.abs().sqrt();
    Point { k, dim: space.dim, ref_occ: ref_occ.to_vec(), q, v: vol, closure, secs: dt }
}

fn write_json(path: &str, seed: u64, family: &str, pts: &[Point], controls: &[Point]) {
    let mut s = String::new();
    s.push_str(&format!(
        "{{\n  \"experiment\": \"T5e large-K semiclassics\",\n  \"n\": {N},\n  \
         \"seed\": {seed},\n  \"family\": \"{family}\",\n  \"triple\": [{}, {}, {}],\n  \"gamma\": 0.2375,\n  \
         \"hbar\": 1.0,\n  \"plane\": \"moment-curve + imag dC[1,i]=0.35*(i+0.5), eps=1\",\n  \
         \"engine\": \"rust on-the-fly (q=-2Im<Aij|A jk>)\",\n  \"points\": [\n",
        TRIPLE.0, TRIPLE.1, TRIPLE.2
    ));
    for (n, p) in pts.iter().enumerate() {
        s.push_str(&format!(
            "    {{\"K\": {}, \"dim\": {}, \"ref\": {:?}, \"q\": {:.6e}, \
             \"V\": {:.6e}, \"closure\": {:.9}, \"secs\": {:.1}}}",
            p.k, p.dim, p.ref_occ, p.q, p.v, p.closure, p.secs
        ));
        if n + 1 < pts.len() {
            s.push(',');
        }
        s.push('\n');
    }
    s.push_str("  ],\n  \"controls\": [\n");
    for (n, p) in controls.iter().enumerate() {
        s.push_str(&format!(
            "    {{\"K\": {}, \"kind\": \"real-plane eps=0\", \"q\": {:.6e}, \
             \"V\": {:.6e}, \"closure\": {:.9}, \"secs\": {:.1}}}",
            p.k, p.q, p.v, p.closure, p.secs
        ));
        if n + 1 < controls.len() {
            s.push(',');
        }
        s.push('\n');
    }
    s.push_str("  ]\n}\n");
    std::fs::write(path, s).expect("write json");
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let mut seed: u64 = 11;
    let mut ks = String::from("8,12,16,20,24");
    let mut out = String::from("t5e_results.json");
    let mut family = String::from("uniform");
    let mut xcheck = false;
    let mut controls = false;
    let mut ai = args.iter().skip(1);
    while let Some(a) = ai.next() {
        match a.as_str() {
            "--seed" => seed = ai.next().expect("--seed value").parse().unwrap(),
            "--ks" => ks = ai.next().expect("--ks value").clone(),
            "--out" => out = ai.next().expect("--out value").clone(),
            "--family" => family = ai.next().expect("--family value").clone(),
            "--xcheck" => xcheck = true,
            "--controls" => controls = true,
            _ => {
                eprintln!("unknown arg {a}");
                std::process::exit(2);
            }
        }
    }
    let kvals: Vec<usize> = ks.split(',').map(|x| x.trim().parse().unwrap()).collect();

    println!("T5e: n={N} seed={seed} triple={TRIPLE:?} family={family} engine=otf");
    // Sanity gate: K=7 vertex reference must reproduce the t5b scale
    // (V ~ 1e-3..1e-2); a mismatch stops the sweep before it starts.
    {
        let r = ref_vertex();
        let p = run_k(seed, 7, &r, false);
        println!(
            "REGRESS K=7 vertex ref: q={:+.6e} V={:.6e} closure={:.6} ({:.1}s)",
            p.q, p.v, p.closure, p.secs
        );
        assert!(
            p.v > 1e-3 && p.v < 1e-2,
            "sanity gate failed: V={} outside [1e-3, 1e-2]",
            p.v
        );
    }
    let mut pts: Vec<Point> = Vec::new();
    let mut ctrls: Vec<Point> = Vec::new();
    for &k in &kvals {
        let r = match family.as_str() {
            "uniform" => ref_m0(k),
            "vertex" => ref_vertex_scaled(k),
            _ => {
                eprintln!("unknown family {family}");
                std::process::exit(2);
            }
        };
        let p = run_k(seed, k, &r, false);
        println!(
            "K={:>3} dim={:>10} ref={:?} q={:+.6e} V={:.6e} closure={:.6} ({:.1}s)",
            p.k, p.dim, p.ref_occ, p.q, p.v, p.closure, p.secs
        );
        assert!(
            (p.closure - k as f64).abs() < 1e-6,
            "closure violated at K={k}: {}",
            p.closure
        );
        if xcheck && p.dim < 200_000 {
            let fock = lqg_grassmannian::fock::FockSpace::new(N, k);
            let plane = complex_plane(seed);
            let (_, qs) =
                lqg_grassmannian::experiment::triple_q_all_pairs(&fock, &plane, &r, 1e-13);
            // triple (0,1,2) is lexicographically first
            let qs0 = qs[0];
            let rel = ((qs0 - p.q) / p.q).abs();
            println!("  xcheck stored-engine q_012={qs0:+.6e} rel-diff={rel:.2e}");
            // tolerance is loose on purpose: the two engines sum the long
            // Taylor series in different orders, so roundoff-level drift
            // (~1e-9 at dim 1e5) is expected; physics needs only 1e-3.
            assert!(rel < 1e-6, "engine mismatch at K={k}");
        }
        pts.push(p);
            write_json(&out, seed, &family, &pts, &ctrls);
    }
    if controls {
        for &k in &[kvals[0], kvals[kvals.len() - 1]] {
            let r = match family.as_str() {
                "uniform" => ref_m0(k),
                "vertex" => ref_vertex_scaled(k),
                _ => unreachable!(),
            };
            let p = run_k(seed, k, &r, true);
            println!(
                "CONTROL real-plane K={k}: q={:+.6e} V={:.6e} (expect ~0)",
                p.q, p.v
            );
            ctrls.push(p);
        write_json(&out, seed, &family, &pts, &ctrls);
        }
    }
    println!("wrote {out}");
}

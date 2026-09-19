# Product Context

*Last Updated: 2026-09-19 16:30 IST*

## Physics Motivation

Loop Quantum Gravity (LQG) and perturbative scattering amplitudes have evolved largely independently. This project bridges them: LQG spin networks provide a non-perturbative, background-independent quantization of geometry, while the amplituhedron program reveals a hidden positive-geometry structure in planar N=4 SYM scattering amplitudes. The interface is the Grassmannian — specifically, the observation that U(N) coherent states for LQG intertwiners admit a natural embedding into the Grassmannian Gr(k,n), whose positive part is central to the amplituhedron.

## The Core Question

Does the amplituhedron region of the Grassmannian — the "positive" cell where scattering amplitudes live — correspond to a region of zero or nonzero quantum volume in LQG?

## Published Result (EPJC)

The volume operator vanishes identically on the positive Grassmannian cell. The amplituhedron region corresponds to classical, zero-volume geometry. Quantum volume lives in the complex extension of the positive cell.

**Citation**: D. Vaid, "LQG and the Amplituhedron", EPJC (2026). `paper/lqg-amplituhedron.pdf`

## Follow-up Numerical Program

The original paper established the zero-volume result analytically for n=4. The current program computes numerical volume spectra for n≥5 vertices, which was computationally infeasible at publication time. The goal is to confirm the zero-volume result extends to higher valence and to map the volume landscape across the full Grassmannian.

## Users and Stakeholders

- Deepak Vaid (project lead, NIT Karnataka / IUCAA)
- The LQG and amplitudes communities interested in the interface

## Success Criteria

1. Rust implementation matches Python at n=4 (f64 machine precision)
2. Volume computed for n=5,6,7,8 with reasonable runtime (< 1 min per n)
3. Follow-up manuscript drafted with numerical results

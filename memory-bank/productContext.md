# Product Context

*Last Updated: 2026-10-01 20:31 IST*

## Physics Motivation

Loop Quantum Gravity (LQG) and perturbative scattering amplitudes have evolved largely independently. This project bridges them: LQG spin networks provide a non-perturbative, background-independent quantization of geometry, while the amplituhedron program reveals a hidden positive-geometry structure in planar N=4 SYM scattering amplitudes. The interface is the Grassmannian — specifically, the observation that U(N) coherent states for LQG intertwiners admit a natural embedding into the Grassmannian Gr(k,n), whose positive part is central to the amplituhedron.

## The Core Question

How do Grassmannian plane labels affect the signed triple-grasp mean, the
expectation of a specified positive quantum volume operator, and a
reconstructed classical volume? These are distinct observables.

## Published Baseline (EPJC)

The 2022 paper establishes the kinematic Grassmannian/coherent-state
correspondence. It does not report the follow-up numerical volume results.
The red-team audit found that the later code's zero result is a cancellation
of the signed mean on real planes, including planes outside the positive
cell. It does not establish zero positive quantum volume.

**Citation**: D. Vaid and D. Suresh, EPJC (2022), DOI
10.1140/epjc/s10052-022-10701-6. `paper/lqg-amplituhedron.pdf`

## Follow-up Numerical Program

The follow-up program has corrected converged $n=4$–$8$ scans of a signed-mean proxy.
The $n=4$ comparison shared a truncated Taylor state, so complex-plane
magnitudes have been rerun with Rust convergence assertions; the $n=6$ point still needs an independent state check. The next goal is to define and
calculate positive volume separately, then test its geometric meaning.

## Users and Stakeholders

- Deepak Vaid (project lead, NIT Karnataka / IUCAA)
- The LQG and amplitudes communities interested in the interface

## Success Criteria

1. Rust and Python match an independent converged exponential at $n=4$.
2. $n=5$–$8$ observables are rerun with convergence checks and provenance.
3. A specified positive quantum volume is compared with reconstructed
   classical geometry; the follow-up manuscript states only validated claims.

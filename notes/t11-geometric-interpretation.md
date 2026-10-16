# T11: geometric interpretation of the four-site volume crossover

[Research map](quantum-geometry-research.md) · Related: [volume studies](volume-studies.md), [geometric area redistribution](geometric-area-redistribution.md).

Plan recorded 2026-10-10 21:58:38 IST, before implementation. This is a
focused T11 sub-study. It does not update the task registry, active context,
progress, cache, session history, or other Memory Bank records.

## Question and interpretation

Does the four-site low-temperature positive-volume drop reflect flattened
tetrahedral configurations, fewer active faces, broad quantum shape
fluctuations, or a combination? Interpret the existing result before adding
larger systems or new dynamics.

An intertwiner is a quantum-polyhedron state; a definite classical shape
requires additional evidence. The hopping graph specifies interactions and
is not assumed to be the reconstructed face-adjacency graph. The volume
operator is the chosen positive RS prescription, not an independently
reconstructed Euclidean volume.

## Frozen implementation scope

1. Reuse the normalized FL state $|K,z\rangle\propto(F_z^\dagger)^K|0\rangle$
   at $K=4$ with four equal input face-area fractions. Use the implemented
   normals $n_i(x,\varphi)$ at $x=1/\sqrt3$, with $\varphi=90,60,30,10$ degrees
   and $0$ degrees as a separately labelled flat-boundary control. Labels
   are held fixed; this one path is not a complete shape search.
2. The input face vectors are $F_i=(K/4)n_i$. Compare the quantum reference
   to those specified vectors, not to individual $\langle\mathbf J_i\rangle$,
   which vanish in a singlet. Total linear area $K=\sum_i j_i$ is fixed;
   individual face spins fluctuate. Do not replace it by Casimir area.
3. Keep four sites, $K=4$, $t=1,U=20,g=0$ and existing complete/ring hopping.
   Diagnose uniform mixtures in each of the first three distinct energy
   groups; reconstruct thermal observables using the entire spectrum.
4. Read out individual face-area means, covariances and assignment weights,
   active-face probabilities, all six pair dots, positive RS mean/variance
   and outcome distribution. For angles restrict to four nonzero faces and
   use $C_{ij}=D_{ij}/\sqrt{j_i(j_i+1)j_j(j_j+1)}$ separately in each spin
   assignment. Report means, variances and symmetrized joint covariances.
   Also report per-assignment conditional pair data and probabilities.
5. Report full-state and four-active-face-conditioned results together.
   Compute FL overlaps with full and conditioned states, without treating
   nonorthogonal reference overlaps as exclusive shape probabilities.
6. Use $\beta t=0$, 601 logarithmic values from $10^{-3}$ to $10^3$, and the
   exact zero-temperature ground-space mixture. Save the first-three-level
   populations and the remaining population alongside thermal diagnostics.
7. Retain project $\gamma=0.2375,\hbar=1$ positive roots and the existing
   $64\epsilon_{\mathrm{mach}}\max(1,\rho(|q|))$ kernel cutoff. For all four
   connected triples use the established T5c factor $\sqrt2/12$ to convert
   RS project values to its geometric convention. The classical input
   reference uses flux vectors $\gamma F_i$ for the same convention.
   Physical regularization/Planck-unit calibration remains unselected.
8. Accept operator/state/spectrum residuals below $2\times10^{-10}$.
   Independently check local-spin pair dots and epsilon-contracted triples,
   analytic paired-spin-half angular moments, explicit projection/trace
   conditioning, phase-basis invariance of degenerate mixtures, closure,
   thermal parity with saved data, and small conditional probabilities.

## Planned delivery and claim limits

Save source, protocol, results, validation and provenance under a separate
`results/t11-geometric-interpretation/` directory. Present one compact state
comparison table and a vector-PDF/300-dpi-PNG figure linking geometric
diagnostics to thermal volume. Retain the previous calculations unchanged.

At finite $K$, reference angular expectations need not equal classical
normal dot products. A Gram matrix built from means does not establish a
single classical geometry; noncommuting angular quantities and their
fluctuations matter. No large-$K$ convergence study, phase-transition
claim, complete shape classification, time evolution, five-site extension,
sewing calculation, or T9 work is included. A negative or ambiguous geometric
interpretation is an acceptable result; do not change the Hamiltonian to
manufacture a preferred outcome.

Related source records: [Hamiltonian pilot](hamiltonian-studies.md),
[T5c geometry and normalization](../memory-bank/implementation-details/T5c-flux-covariance-volume-comparison.md),
[T11 task](../memory-bank/tasks/T11.md).

## Implemented calculation and findings

The specified $K=4$ reference family and the first three complete/ring energy
groups are calculated. Full results, reproduction commands, and independent
checks are in [the result record](../results/t11-geometric-interpretation/README.md).
This section reports implementation without changing the broader Memory Bank.

The complete-graph volume drop is not principally loss of active faces:
ground and first-excited four-face weights are 0.999934 and 0.999878. Their
dominant assignment is $j_i=1$ on all four faces, with weights 0.931429 and
0.932435. Within that assignment the ground state is in the positive-volume
kernel, whereas the first excited doublet has volume 0.609306 in project
units and essentially zero kernel weight.

Both conditional states have all six angular means $-1/3$, but standard
deviations differ: 0.745356 for the ground state versus 0.552771 for the
first excited group. Therefore reconstructing a regular tetrahedron from
those means alone would conceal the volume difference and substantial
quantum fluctuations.

The same-area regular FL reference has zero overlap with the ground state
and overlap 0.5 with the uniform excited-doublet mixture. Ground-state
overlap increases toward the flat-input reference along the tested path,
reaching 0.444444 at the boundary. These nonorthogonal overlaps are not a
shape-probability distribution, nor is 0.444444 sufficient to identify one
definite flattened classical tetrahedron. The exact flat-input reference
itself retains nonzero positive volume at $K=4$, consistent with the prior
T5c finite-area observations.

The justified interpretation is a low-temperature shift from a high-volume
excited group toward a volume-kernel-dominated ground state with broad
angular fluctuations. A unique classical flattening interpretation remains
unestablished. The ring ground state instead has nearly antiparallel
opposite-face correlations in its dominant equal-spin assignment, with
other angular correlations broad; it should not be assigned a unique
classical shape from means either.

Independent magnetic-space pair-dot and epsilon-triple reconstructions,
positive-root reconstruction, sliced conditional traces, same-area overlaps,
degenerate-mixture invariance, and matrix-exponential Gibbs controls pass.
The largest independent residual is $5.2\times10^{-12}$, below the frozen
$2\times10^{-10}$ tolerance. All 42 Python tests pass, including four new
analytic angular/conditioning controls. No independent Rust calculation,
large-area limit, dynamical run, or physical volume calibration is claimed.

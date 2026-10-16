# Exact closed-channel redistribution: pre-run protocol

October 16, 2026, T11. Primary size L=8,K=4; controls L=4,6 at the same K.
Use the exact SU(2) singlet subspace at fixed Nb=2K=8. Work in the magnetic
M=0 occupation space for operator construction, never the full unprojected
Fock space and never a dense full Hamiltonian or propagator.

Hamiltonian H=alpha sum_i Ji² - sum_edges w(Eij+Eji), hbar=1.
Compare rings (w=1/2) and complete graphs (w=1/(L-1)), so the one-particle
hopping row sum is one in both. alpha=0,1,5. Ring L=4 has four unique bonds.
No added volume interaction. K is linear area sum_i ji, not sum sqrt(ji(ji+1)).

Preparations: regular and phi=30-degree deformed closed input normals at
x=1/sqrt(3), projected fixed-area FL states onto exact local counts
(2,2,2,2,0,...). These normalized closed states have exactly four occupied
channels, ji=1 on each. Report the preconditioning probability. The third
preparation is the unconditioned regular FL state with four nonzero input
labels; it has fluctuating occupation and is explicitly a separate control.
Cold receivers are channels 4..L-1 (zero based). Global SU(2) rotations are
not physical preparation controls. Face-dependent phases of fixed-count
states contribute only an overall phase and are not independent inputs.

Time: 0..20 inclusive, spacing .2 (101 points), in inverse unit hopping-row-sum
energy. Store local area/Casimir means, active-count distributions, receiver
linear area and Casimir energy ratios, concentration, return, norm/energy
residuals and single-channel entropy. Entropy includes spin multiplicity:
S_i=-sum_n p_i(n) log[p_i(n)/(n+1)] for an exact singlet at fixed Nb.
At times 0,2,5,10,20 additionally measure all conditional pair-angle means
and standard deviations, pair-presence probabilities, total positive RS
volume and zero-volume probability. Use all unordered triples for this
single-vertex RS operator, independent of interaction graph. This differs
from connected-induced-triple Hamiltonian-graph conventions in earlier T11
studies. Retain repository gamma=0.2375 normalization; no physical calibration
or higher-valence classical volume interpretation is claimed.

Validation: orthonormal coupled basis, magnetic raising annihilation, Hermitian
operators, hopping projection leakage, closure scalar-product identity, positive
volume blocks/kernel projectors, norm and energy conservation. Target absolute
operator residuals <2e-9 and trajectory residuals <2e-8. Compare free unconditioned
FL dynamics with independent analytic spinor evolution/readouts, and selected
interacting trajectories with magnetic-space propagation. No-hopping control
must keep occupations and return probability fixed (fixed-count seeds).

Late-window summaries: equal weights on saved t in [10,20], plus extrema over
whole window. They are descriptive, not equilibrium or thermalization tests.
No fitted transfer threshold. No reconstruction of a classical polyhedron from
mean fluxes, which vanish in a singlet. Pair correlations and RS volume provide
quantum geometric diagnostics; activated channels need not be distinct normals.

Retain protocol, initial coefficients, compact CSV/JSON summaries, selected
geometric samples, provenance, validation and PDF/300-dpi PNG figures. Do not
save full trajectories of state vectors or density matrices. A single run's
state vectors can be held transiently in memory and released. Intermediate
operators are rebuilt and are not retained as large files. Artifacts approaching
200 MB are temporary and need not be retained; keep final output far below that.

## Additional bookkeeping diagnostic after the initial run

Before the final rerun, add local total energies by assigning half of each
hopping-bond energy to each endpoint: Ei=alpha Ji² - (1/2) sum_j w(Eij+Eji).
Check sum_i <Ei>=<H> at every output time. Receiver local energy includes
this convention-dependent interaction share and is saved separately from
the positive local Casimir diagnostic. No physical parameters, preparations,
acceptance criteria or output windows were changed by this addition.

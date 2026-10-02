# Volume Operator: Implemented Prescriptions and Limits

*Last Updated: 2026-10-02 12:22:16 IST*

## Current code

`positivity.volume_operator` and `rust::volume::volume_operator` construct one
triple-grasp matrix $q_{ijk}=i[J_i\cdot J_j,J_j\cdot J_k]$, evaluate
$\langle q_{ijk}\rangle$, and return

$$V_{\rm proxy}=(\gamma\hbar)^{3/2}\sqrt{|\langle q_{ijk}\rangle|}.$$

This is a signed-mean diagnostic followed by a scalar transformation. It does
not apply the positive square root of the operator to the state, and it does
not assemble a vertex operator from the edge triples. The function name and
older completion notes overstated what this code calculates. The corrected
Rust and Python scans must be described as signed triple-grasp results only.

## RS and AL vertex-volume calculations

The code now implements both prescriptions in the repository's dimensionless
triple-grasp normalization. For unordered triples $I<J<K$:

$$\hat V_{v,\mathrm{RS}}=c_{\mathrm{RS}}\sum_{I<J<K}\sqrt{|\hat q_{IJK}|},\qquad
\hat V_{v,\mathrm{AL}}=c_{\mathrm{AL}}\sqrt{\left|\sum_{I<J<K}\epsilon(e_I,e_J,e_K)\hat q_{IJK}\right|}.$$

The reported observable is $\langle\psi|\hat V_v|\psi\rangle$. The caller
supplies all AL tangent signs in lexicographic triple order. Each implementation
decomposes the populated sectors and evaluates the positive square root by
dense Hermitian spectral decomposition. It returns an error for an active
fixed-spin block larger than 512, rather than silently approximating it.
The default project prefactor is $(\gamma\hbar)^{3/2}$; use the explicit
`scale`/`prefactor` argument for a different regularization normalization.
The standard LQG regularization constants and $8\pi\ell_P^2$ factors have not
been selected or included, so these outputs are in project-normalized units.

For a finite-dimensional Hermitian $Q_v=U\,\mathrm{diag}(\lambda_a)U^\dagger$,
the required expectation is

$$\langle V_v\rangle=c\frac{\sum_a |(U^\dagger\psi)_a|^2\sqrt{|\lambda_a|}}{\langle\psi|\psi\rangle}.$$

It is generally not $c\sqrt{|\langle Q_v\rangle|}$. In particular,
$\langle q_{ijk}\rangle=0$ does not imply $q_{ijk}|\psi\rangle=0$ or zero
positive volume.

## Remaining work before large-scan or physical-volume claims

- Select and document the physical prefactors for the intended regularization.
- Supply justified graph embeddings and tangent-orientation signs for each
  AL state; the Grassmannian plane alone does not provide them.
- Confirm the coherent state lies in the Hilbert space where that operator
  and any proposed single-triple reduction apply.
- The outstanding project-coherent-state check means the Freidel–Speziale
  coherent state used in the EPJC paper. No construction or positive-volume
  evaluation of that state is recorded yet; the paired-singlet check is a
  separate simple-state validation.
- The Freidel–Livine U(N) Perelomov family discussed in the 2026-10-02 session
  is distinct from that project target. Its F† singlet-pair construction and
  overlap results do not count as an FS-state volume evaluation.
- Replace or extend dense block diagonalization before applying it to large
  sectors; current exact code refuses blocks above 512.
- Rerun the reported states. Keep the existing signed-mean series under its
  correct name; it is not a volume series.

## Code locations

| File | Current role |
|---|---|
| `positivity.py` | Python signed-mean proxy and positive RS/AL expectations |
| `rust/src/volume.rs` | Rust signed-mean proxy and positive RS/AL expectations |
| `memory-bank/implementation-details/red-team-audit.md` | Numerical audit and current evidence |

The positive routines are `rovelli_smolin_volume` and
`ashtekar_lewandowski_volume` in both implementations. The exact small-state
cross-check is recorded in `volume_prescription_results.json` and can be
reproduced with `volume_prescription_demo.py`.

References: Rovelli and Smolin, [Discreteness of Area and Volume in Quantum Gravity](https://arxiv.org/abs/gr-qc/9411005), and Lewandowski, [Volume and Quantizations](https://arxiv.org/abs/gr-qc/9602035), distinguish the RS sum of positive triple contributions from the AL orientation-weighted sum. Ashtekar and Lewandowski, [Quantum Theory of Geometry II: Volume Operators](https://arxiv.org/abs/gr-qc/9711031), construct the AL operator. Regularization prefactors depend on the selected convention.

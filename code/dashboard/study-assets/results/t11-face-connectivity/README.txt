# Four-to-five-to-six face-channel connectivity

Static T11 Hamiltonian audit, October 16, 2026. Read the [pedagogical derivation](../../notes/face-activation-connectivity.md) and [pre-run protocol](protocol.md).

H = alpha sum Ji² - t sum_edges(Eij+Eji), alpha=t=hbar=1. Area means fixed linear area K=Nb/2; local activity means ni>0. No time evolution or geometric reconstruction was performed.

## Primary results: L=6, K=3

Complete Fock dimension 12,376; exact singlet dimension 490. Singlet dimensions at 4/5/6 active channels: 240/90/5. Full-space dimensions at 4/5/6 active channels: 5160/1440/64.

| Graph | Singlet rank P5 H P4 | Singlet rank P6 H² P4 | Direct P6 H P4 |
|---|---:|---:|---:|
| ring | 90 | 5 | 0 |
| complete | 90 | 5 | 0 |

For the closed normalized source (F03†)^2 F12†|0>/sqrt(24), counts (2,1,1,2,0,0), define target5=E50 source/sqrt(2) and target6=E43 target5/sqrt(2). Both have exact closure and counts (1,1,1,2,0,1) and (1,1,1,1,1,1). In both graphs, <target5|H|source> = <target6|H|target5> = -sqrt(2). These same directed matrix elements hold for the nonclosed J=3 highest-weight source and its M=0 descendant.

| Source sector | Ring norm P5 H source | Ring norm P6 H² source | Complete norm P5 H source | Complete norm P6 H² source |
|---|---:|---:|---:|---:|
| closed | 2 | 4 | 2.8284271 | 4 |
| open_highest_weight | 2 | 4 | 2.8284271 | 8 |
| open_M0 | 2 | 4 | 2.8284271 | 8 |

Direct four-to-six amplitudes vanish. The second-power numbers use the actual H² and retain interference. The disconnected-receiver and no-hopping controls give zero witness activation. Global blocks for the disconnected graph include other initial occupations and are not themselves zero. Ring/complete full Fock graphs have seven components (fixed Na=0..6); their singlet basis graphs each have one component. Graph counts and block ranks are stable at 1e-10 and 1e-12.

The direct singlet 4-to-5 block has source nullity 150. This is a first-order cancellation subspace, not proof of permanent confinement. A connected basis graph is not proof that every superposition activates every count sector. Explicit witnesses establish existence without that inference.

Five available channels at K=3 also have a nonzero direct closed 4-to-5 block (rank 15). Six channels at K=2 have no 5/6-active states because Nb=4. The Casimir is diagonal and has no activity-changing block. The exact onsite identity uses U=alpha/2 and additive constant 3 alpha Nb/4.

## Verification

Maximum production residual across all three sizes: 3.55e-15. Checks include orthonormal recoupling, exact singlet dimensions, all closure generators, Hermiticity, full-space commutators with Jx/Jy/Jz/J², singlet projection leakage, definite-spin witness residuals and the onsite/Casimir identity.

Independent dictionary oscillator/SU(2) ladder algebra reproduces saved witness norms, matrix elements, active counts and spin sectors: 99 comparisons, maximum residual 1.99e-15, tolerance 2e-10. Source SHA256 hashes were checked. All 67 regression tests passed, including five new analytic connectivity tests.

## Saved artifacts and reproduction

- L6-K3.json: full/singlet block statistics, graph components, ranks, validation and explicit normalized witness coefficients in full Fock occupations, including the directed chain. Code labels are zero based; the pedagogical note uses channels 1..6.
- L5-K3.json, L6-K2.json: size and minimum-number controls.
- L6-K3-*-singlet-H.npz: sparse singlet Hamiltonians for all three graphs.
- L6-K3-singlet-embedding.npz, L6-K3-full-occupations.npz, L6-K3-singlet-labels.json: full-to-singlet embedding, basis ordering, local counts and recoupling paths.
- summary.json: source provenance. independent-validation.json: independent saved-witness audit.

```sh
OPENBLAS_NUM_THREADS=1 python3 code/python/t11_face_connectivity.py
python3 code/python/verify_t11_face_connectivity.py
python3 -m unittest discover -s code/python -p 'test_*.py'
```

Dependencies are the existing project NumPy, SciPy and SymPy. This demonstrates allowed occupation redistribution with and without exact closure. It does not establish polyhedral shape, distinct normals, positive volume, transfer rates, equilibration, a semiclassical limit, or changes between different total-spin sectors. No dashboard changes or publication are included.

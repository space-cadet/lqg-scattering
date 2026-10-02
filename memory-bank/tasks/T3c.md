---
source_branch: work
source_commit: 9602c9811278635eb4b3e3e601badd28e7964862
---

# T3c: Positive-volume construction and validation in Rust
*Created: 2026-10-02 12:15:21 IST*
*Last Updated: 2026-10-02 12:22:16 IST*

**Description**: Implement and validate positive Rovelli–Smolin and Ashtekar–Lewandowski volume expectations in the Rust implementation, using n=4 as the reference case.
**Status**: 🔄 IN PROGRESS
**Priority**: HIGH
**Started**: 2026-09-19
**Last Active**: 2026-10-02 12:22:16 IST
**Dependencies**: T3

## Completion Criteria
- ✅ Construct triple-grasp matrices from sparse Schwinger generators.
- ✅ Implement positive RS and AL expectations by active-sector spectral decomposition.
- ✅ Match simple-state results against Python and an independent tensor-product calculation.
- 🔄 Validate on the Freidel–Speziale coherent states used in the EPJC paper and select physical regularization prefactors.
- 🔄 Replace dense diagonalization before evaluating active blocks above dimension 512.

## Related Files
- `rust/src/volume.rs`
- `rust/src/ops.rs`
- `rust/src/fock.rs`
- `memory-bank/implementation-details/fock-space-construction.md`
- `memory-bank/implementation-details/volume-operator.md`

## Progress
1. ✅ Positive RS and AL calculations and simple-state controls are recorded in the repository.
2. ✅ The project target was clarified as the Freidel–Speziale coherent state used in the EPJC paper.
3. 🔄 Continue with its construction, positive-volume evaluation, prefactor choice, and larger-block method.

## Context
The 2026-10-02 discussion covered the distinct Freidel–Livine U(N) Perelomov family and its singlet-pair construction. No Rust code was changed or validated in that discussion. $(F^\dagger_{12})^2|0\rangle$ has local spin one on each leg and total spin zero across the pair; this conceptual derivation does not complete the open FS-state volume validation.

Keep signed triple-grasp means separate from expectations of positive volume operators.

---
source_branch: work
source_commit: 9602c9811278635eb4b3e3e601badd28e7964862
---

# T3c: Positive-volume construction and validation in Rust
*Created: 2026-10-02 12:15:21 IST*
*Last Updated: 2026-10-02 13:49:49 IST*

**Description**: Implement and validate positive Rovelli–Smolin and Ashtekar–Lewandowski volume expectations in the Rust implementation, using n=4 as the reference case.
**Status**: 🔄 IN PROGRESS
**Priority**: HIGH
**Started**: 2026-09-19
**Last Active**: 2026-10-02 13:49:49 IST
**Dependencies**: T3

## Completion Criteria
- ✅ Construct triple-grasp matrices from sparse Schwinger generators.
- ✅ Implement positive RS and AL expectations by active-sector spectral decomposition.
- ✅ Match simple-state results against Python and an independent tensor-product calculation.
- 🔄 Validate the EPJC Eq. (38) FL fixed-area coherent-state case in the Rust implementation; select physical regularization prefactors and reconcile with the Python/direct-tensor values.
- 🔄 Replace dense diagonalization before evaluating active blocks above dimension 512.

## Related Files
- `rust/src/volume.rs`
- `rust/src/ops.rs`
- `rust/src/fock.rs`
- `memory-bank/implementation-details/fock-space-construction.md`
- `memory-bank/implementation-details/volume-operator.md`

## Progress
1. ✅ Positive RS and AL calculations and simple-state controls are recorded in the repository.
2. ✅ The EPJC Eq. (38) FL fixed-area state has been evaluated in Python on one regular-tetrahedron case.
3. 🔄 Validate that case in Rust, reconcile the direct-tensor discrepancy, choose physical prefactors, and address larger blocks.

## Context
No Rust code was changed or validated in the 2026-10-02 numerical follow-up. Python evaluated the EPJC Eq. (38) FL fixed-area state and found positive RS/AL volumes with a small unresolved direct-tensor discrepancy. Rust evaluation of this same state remains open; FL names the fixed-area state, while FS refers to the spinorial phase-space framework.

Keep signed triple-grasp means separate from expectations of positive volume operators.

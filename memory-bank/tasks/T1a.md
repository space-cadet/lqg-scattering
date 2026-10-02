---
source_branch: work
source_commit: 9602c9811278635eb4b3e3e601badd28e7964862
---

# T1a: Positive-volume construction and validation in Python
*Created: 2026-10-02 12:15:21 IST*
*Last Updated: 2026-10-02 12:22:16 IST*

**Description**: Implement and validate positive Rovelli–Smolin and Ashtekar–Lewandowski volume expectations in the Python reference implementation at n=4.
**Status**: 🔄 IN PROGRESS
**Priority**: HIGH
**Started**: 2026-09-19
**Last Active**: 2026-10-02 12:22:16 IST
**Dependencies**: T1

## Completion Criteria
- ✅ Implement positive RS and AL expectations using exact active-sector spectral decomposition.
- ✅ Check paired spin-1/2 singlet and collinear controls against an independent tensor-product calculation.
- 🔄 Construct and evaluate the Freidel–Speziale coherent state used in the EPJC paper; select physical regularization prefactors.
- 🔄 Replace dense diagonalization before evaluating active blocks above dimension 512.

## Related Files
- `positivity.py`
- `coherent_states.py`
- `memory-bank/implementation-details/fock-space-construction.md`
- `memory-bank/implementation-details/volume-operator.md`

## Progress
1. ✅ Positive RS and AL calculations and simple-state controls are recorded in the repository.
2. ✅ The project target was clarified as the Freidel–Speziale coherent state used in the EPJC paper.
3. 🔄 Continue with its construction, positive-volume evaluation, prefactor choice, and larger-block method.

## Context
The 2026-10-02 discussion covered the separate Freidel–Livine U(N) Perelomov family and the action of its singlet-pair creator. It did not construct or evaluate the project Freidel–Speziale state. In particular, $(F^\dagger_{12})^2$ gives spin one on each leg coupled to a two-leg singlet; this conceptual result does not satisfy the open FS-state validation criterion.

The task remains in progress. Keep the signed-mean proxy distinct from expectation values of positive volume operators.

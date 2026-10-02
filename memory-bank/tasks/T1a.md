---
source_branch: work
source_commit: 9602c9811278635eb4b3e3e601badd28e7964862
---

# T1a: Positive-volume construction and validation in Python
*Created: 2026-10-02 12:15:21 IST*
*Last Updated: 2026-10-02 13:49:49 IST*

**Description**: Implement and validate positive Rovelli–Smolin and Ashtekar–Lewandowski volume expectations in the Python reference implementation at n=4.
**Status**: 🔄 IN PROGRESS
**Priority**: HIGH
**Started**: 2026-09-19
**Last Active**: 2026-10-02 13:49:49 IST
**Dependencies**: T1

## Completion Criteria
- ✅ Implement positive RS and AL expectations using exact active-sector spectral decomposition.
- ✅ Check paired spin-1/2 singlet and collinear controls against an independent tensor-product calculation.
- ✅ Preliminary Python evaluation of the EPJC Eq. (38) FL fixed-area coherent state on a regular tetrahedron gives positive RS and AL volumes.
- 🔄 Reconcile the approximately $1.8\times10^{-10}$ direct-tensor discrepancy; extend validation and select physical regularization prefactors.
- 🔄 Replace dense diagonalization before evaluating active blocks above dimension 512.

## Related Files
- `positivity.py`
- `coherent_states.py`
- `memory-bank/implementation-details/fock-space-construction.md`
- `memory-bank/implementation-details/volume-operator.md`

## Progress
1. ✅ Positive RS and AL calculations and simple-state controls are recorded in the repository.
2. ✅ The EPJC Eq. (38) target is the FL fixed-area coherent state; one regular-tetrahedron case has positive RS and AL expectations.
3. 🔄 Reconcile the direct-tensor discrepancy, extend checks, choose physical prefactors, and address larger blocks.

## Context
The EPJC Eq. (38) fixed-area coherent state is the FL state. In the regular-tetrahedron case ($N=4$, $J=2$, $K=4$), project routines give $V_{RS}=0.05077553260216399$ and $V_{AL}=0.025387766749131433$; direct tensor-product evaluation gives $0.05077553242330542$ and $0.025387766570272866$. The roughly $1.8\times10^{-10}$ discrepancy remains unresolved. The spinorial phase-space framework is due to Freidel–Speziale (FS); do not treat it as a distinct target family for this EPJC equation.

The task remains in progress. Keep the signed-mean proxy distinct from expectation values of positive volume operators.

"""Classical limit of the U(N) coherent states.

Semiclassical check: as the total Schwinger boson number K (the quantum
scale of the geometry) grows at fixed Grassmannian shape, the Perelomov
state should become sharply peaked on the classical plane — the relative
area uncertainty  Delta A_i / <A_i>  of every edge must fall like
K^{-1/2}, the universal coherent-state suppression.

The occupation of the reference state is scaled proportionally to the
classical column norms of a fixed plane, with one b-boson per edge kept
so the vertex carries genuine spin degrees of freedom at every K.

Only numpy is used.
"""

import numpy as np

from coherent_states import (
    GAMMA,
    area_expectation,
    area_uncertainty,
    plane_to_Z,
    perelomov_state,
)
from positivity import positive_region_N4


def classical_limit(N=4, scales=(4, 6, 8, 10, 12), plane=None,
                    verbose=True):
    """Verify uncertainty suppression at large quantum numbers.

    Parameters
    ----------
    N : int
        Number of edges (vertex valence).
    scales : iterable of int
        Total boson numbers K at which to build the coherent state.
    plane : array-like, shape (2, N), optional
        Fixed classical shape; defaults to an explicit Gr+(2, 4) plane
        (for N != 4 a random complex plane of the same canonical form is
        used, with the cell condition generalized trivially).

    Returns
    -------
    dict with 'K', 'rel_uncertainty' (len-N list per K), 'exponent'
    (log-log slope of the mean relative uncertainty vs K; -0.5 is the
    coherent-state prediction).
    """
    if plane is None:
        if N != 4:
            raise ValueError("default plane is the Gr+(2,4) cell; pass a "
                             "plane explicitly for other N")
        plane, _ = positive_region_N4(1.0, 2.0, 0.5, 1.5)
    plane = np.asarray(plane, dtype=complex)
    Z = plane_to_Z(plane)

    # classical weights: column norms of the plane
    w = np.linalg.norm(plane, axis=0)
    w = w / w.sum()

    K_list, rel_list = [], []
    for K in scales:
        # distribute K - N a-bosons proportionally to w, plus one b-boson
        # per edge (N_b = N fixed, N_a ~ K)
        na = np.maximum(np.round((K - N) * w).astype(int), 0)
        na[np.argmax(w)] += (K - N) - na.sum()  # absorb rounding
        ref = np.stack([na, np.ones(N, dtype=int)], axis=1)
        state, space = perelomov_state(Z, k_max=K, ref_occupations=ref)
        rel = []
        for i in range(N):
            mean = area_expectation(state, i, space)
            unc = area_uncertainty(state, i, space)
            rel.append(unc / mean if mean > 0 else np.inf)
        K_list.append(int(K))
        rel_list.append(rel)
        if verbose:
            print(f"  K={K:3d}: <A_i>/(gamma*hbar) = "
                  f"{[f'{area_expectation(state, i, space) / GAMMA:.3f}' for i in range(N)]}"
                  f"   Delta A/<A> = {[f'{r:.4f}' for r in rel]}")

    K_arr = np.array(K_list, dtype=float)
    mean_rel = np.mean(np.array(rel_list), axis=1)
    exponent = float(np.polyfit(np.log(K_arr), np.log(mean_rel), 1)[0])
    if verbose:
        print(f"  log-log exponent of mean relative uncertainty vs K: "
              f"{exponent:.3f} (coherent-state prediction: -0.5)")
    return {
        "K": K_arr,
        "rel_uncertainty": np.array(rel_list),
        "mean_rel_uncertainty": mean_rel,
        "exponent": exponent,
    }


def _test():
    out = classical_limit()
    rel = out["rel_uncertainty"]
    mean_rel = out["mean_rel_uncertainty"]
    # overall suppression: mean relative uncertainty drops substantially
    # from the smallest to the largest quantum number
    assert mean_rel[-1] < 0.75 * mean_rel[0], \
        "relative uncertainty should drop with K"
    # fit should be close to the coherent-state K^{-1/2} law
    assert -0.9 < out["exponent"] < -0.15, out["exponent"]
    print("\nAll classical_limit.py tests passed.")


if __name__ == "__main__":
    _test()

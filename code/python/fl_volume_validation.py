#!/usr/bin/env python3
"""FL Eq. (38) regular-tetrahedron positive-volume checks and area sweep."""

import json

import numpy as np

from lqg_scattering.fl_volume import (
    GAMMA, N, NORMALS, ORIENTATIONS, TRIPLES,
    direct_tensor_q, direct_tensor_volumes, evaluate_area,
)
from lqg_scattering.intertwiners import fixed_area_state, regular_tetrahedron_spinors
from lqg_scattering.spinors import spinors_from_normals
from lqg_scattering.positivity import volume_operator


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="calculate area labels J=1 through J=5 and print JSON",
    )
    args = parser.parse_args()

    if args.sweep:
        results = [evaluate_area(j, direct_check=True) for j in range(1, 6)]
        print(json.dumps(results, indent=2))
        return

    result = evaluate_area(2, direct_check=True)
    q_mean = volume_operator(fixed_area_state(2)[1], fixed_area_state(2)[0],
                             triple=(0, 1, 2))[1]
    print(f"closure residual: {np.linalg.norm(NORMALS.sum(axis=0)):.3e}")
    print(f"<q_012>: {q_mean.real:.15g}{q_mean.imag:+.3g}i")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

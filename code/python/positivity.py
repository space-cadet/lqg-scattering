"""Compatibility re-exports; use :mod:`lqg_scattering.positivity`."""

from lqg_scattering.positivity import *
from lqg_scattering.positivity import (
    _active_vertex_blocks, _dot_ops, _positive_sqrt_expectation,
    _q_action, _sign_consistent, _triple_matrix_block,
)

if __name__ == "__main__":
    from lqg_scattering.positivity import _test, _test_higher_n
    _test()
    _test_higher_n()

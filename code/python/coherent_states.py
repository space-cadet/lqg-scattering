"""Compatibility re-exports; use :mod:`lqg_scattering.coherent_states`."""

from lqg_scattering.coherent_states import *
from lqg_scattering.coherent_states import (
    _combine, _edge_ops, _exponential_state, _test,
)

if __name__ == "__main__":
    _test()

"""Compatibility re-exports; use :mod:`lqg_scattering.schwinger`."""

from lqg_scattering.schwinger import (
    SparseSchwingerSpace,
    bounded_compositions,
    normalized_taylor_exp,
    q_operator,
    volume_on_vec,
)

__all__ = [
    "SparseSchwingerSpace", "bounded_compositions", "normalized_taylor_exp",
    "q_operator", "volume_on_vec",
]

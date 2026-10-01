from typing import Literal

import numpy as np

from tca import _core

ArgsortMethod = Literal["insertion", "merge", "radix_binary"]
ArgsortBackend = Literal["cpp"]

_ARGSORT_METHODS = ("insertion", "merge", "radix_binary")


def available_argsort_algorithms() -> tuple[str, ...]:
    """Return the argsort methods exposed by the public API."""
    return _ARGSORT_METHODS


def argsort(
    values: np.ndarray,
    *,
    method: ArgsortMethod = "merge",
    backend: ArgsortBackend = "cpp",
) -> np.ndarray:
    """Return a stable permutation of indices without modifying ``values``.

    The initial public API targets C-contiguous ``float64`` NumPy arrays. The
    C++ insertion and merge kernels are generic in ``T`` and ``Compare``;
    ``radix_binary`` is deliberately specialized for ``double``/``float64``.
    """
    if not isinstance(values, np.ndarray):
        raise TypeError("values must be a NumPy array")

    if values.ndim != 1:
        raise ValueError("values must be one-dimensional")

    if backend != "cpp":
        raise ValueError("argsort currently supports only backend='cpp'")

    if method not in _ARGSORT_METHODS:
        raise ValueError(
            f"unknown argsort method {method!r}; expected one of {_ARGSORT_METHODS!r}"
        )

    if values.dtype != np.float64:
        raise TypeError("the C++ backend requires dtype=np.float64")

    if not values.flags.c_contiguous:
        raise ValueError("the C++ backend requires a C-contiguous array")

    function = getattr(_core, f"{method}_argsort")
    return function(values)

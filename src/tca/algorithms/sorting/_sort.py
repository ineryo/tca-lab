from typing import Literal

import numpy as np

from tca import _core
from tca.core.instrumentation import Metrics
from tca.reference.sorting.registry import (
    available_sorting_algorithms as _available_sorting_algorithms,
)
from tca.reference.sorting.registry import get_sorting_algorithm

Backend = Literal["python", "cpp"]


def available_sorting_algorithms() -> tuple[str, ...]:
    return _available_sorting_algorithms()


def sort(
    values: np.ndarray,
    *,
    method: str,
    backend: Backend = "python",
    metrics: Metrics | None = None,
) -> None:
    if not isinstance(values, np.ndarray):
        raise TypeError("values must be a NumPy array")

    if values.ndim != 1:
        raise ValueError("values must be one-dimensional")

    algorithm = get_sorting_algorithm(method)

    if backend == "python":
        algorithm(
            values,
            metrics=metrics,
        )
        return

    if backend == "cpp":
        if values.dtype != np.float64:
            raise TypeError("the C++ backend requires " "dtype=np.float64")

        if not values.flags.c_contiguous:
            raise ValueError("the C++ backend requires " "a C-contiguous array")

        _core.sort(
            values,
            method,
            metrics,
        )
        return

    raise ValueError(f"unknown backend {backend!r}; " "expected 'python' or 'cpp'")

from typing import Literal

import numpy as np

from tca import _core
from tca.core.instrumentation import Metrics, Trace
from tca.reference.sorting.registry import (
    available_sorting_algorithms as _available_sorting_algorithms,
)
from tca.reference.sorting.registry import get_sorting_algorithm

Backend = Literal["python", "cpp"]

MERGE_PROFILES = {
    "merge_classic": {
        "buffer": "local",
    },
    "merge_smarter": {
        "buffer": "reused",
    },
}

QUICK_PROFILES = {
    "quick_classic": {
        "pivot": "first",
        "recursion": "classic",
    },
    "quick_smarter": {
        "pivot": "random",
        "recursion": "bounded",
    },
}


def available_sorting_algorithms() -> tuple[str, ...]:
    return (
        *_available_sorting_algorithms(),
        *MERGE_PROFILES,
        *QUICK_PROFILES,
    )


def sort(
    values: np.ndarray,
    *,
    method: str,
    backend: Backend = "python",
    metrics: Metrics | None = None,
    trace: Trace | None = None,
) -> None:
    if not isinstance(values, np.ndarray):
        raise TypeError("values must be a NumPy array")

    if values.ndim != 1:
        raise ValueError("values must be one-dimensional")

    merge_profile = MERGE_PROFILES.get(method)
    quick_profile = QUICK_PROFILES.get(method)

    if merge_profile is not None:
        algorithm = get_sorting_algorithm("merge")
    elif quick_profile is not None:
        algorithm = get_sorting_algorithm("quick")
    else:
        algorithm = get_sorting_algorithm(method)

    if backend == "python":
        if merge_profile is not None:
            algorithm(
                values,
                metrics=metrics,
                trace=trace,
                **merge_profile,
            )
            return

        if quick_profile is not None:
            algorithm(
                values,
                metrics=metrics,
                trace=trace,
                **quick_profile,
            )
            return

        algorithm(
            values,
            metrics=metrics,
            trace=trace,
        )
        return

    if backend == "cpp":
        if trace is not None:
            raise ValueError("trace is only supported by the Python backend")

        if values.dtype != np.float64:
            raise TypeError("the C++ backend requires dtype=np.float64")

        if not values.flags.c_contiguous:
            raise ValueError("the C++ backend requires a C-contiguous array")

        if merge_profile is not None:
            _core.merge_sort(
                values,
                metrics=metrics,
                **merge_profile,
            )
            return

        if quick_profile is not None:
            _core.quick_sort(
                values,
                metrics=metrics,
                **quick_profile,
            )
            return

        _core.sort(
            values,
            method,
            metrics,
        )
        return

    raise ValueError(f"unknown backend {backend!r}; expected 'python' or 'cpp'")

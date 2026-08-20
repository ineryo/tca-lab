from typing import Literal

import numpy as np

from tca import _core
from tca.reference.sorting.selection_sort import (
    selection_sort as _selection_sort_python,
)

Backend = Literal["python", "cpp"]


def selection_sort(
    values: np.ndarray,
    *,
    backend: Backend = "python",
) -> None:
    if not isinstance(values, np.ndarray):
        raise TypeError("values must be a NumPy array")

    if values.ndim != 1:
        raise ValueError("values must be one-dimensional")

    if backend == "python":
        _selection_sort_python(values)
        return

    if backend == "cpp":
        if values.dtype != np.float64:
            raise TypeError("the C++ backend currently requires dtype=np.float64")

        if not values.flags.c_contiguous:
            raise ValueError("the C++ backend requires a C-contiguous array")

        _core.selection_sort(values)
        return

    raise ValueError(f"unknown backend {backend!r}; expected 'python' or 'cpp'")

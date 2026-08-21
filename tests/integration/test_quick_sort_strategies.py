import numpy as np
import pytest
import tca._core as cpp

from tca.core.instrumentation import Metrics
from tca.reference.sorting.quick_sort import quick_sort


@pytest.mark.parametrize(
    "pivot",
    ["first", "quarter", "random"],
)
@pytest.mark.parametrize(
    "recursion",
    ["classic", "bounded"],
)
@pytest.mark.parametrize(
    "values",
    [
        [8, 3, 7, 4, 9, 2, 6, 5, 1],
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [9, 8, 7, 6, 5, 4, 3, 2, 1],
        [2, 2, 2, 2, 2, 2],
        [3, 1, 3, 2, 1, 2, 3],
    ],
)
def test_quick_sort_strategies_python_cpp_parity(values, pivot, recursion):
    python_values = values.copy()
    cpp_values = np.array(values, dtype=np.float64)

    python_metrics = Metrics()
    cpp_metrics = Metrics()

    quick_sort(
        python_values,
        metrics=python_metrics,
        pivot=pivot,
        recursion=recursion,
        seed=42,
    )

    cpp.quick_sort(
        cpp_values,
        pivot=pivot,
        recursion=recursion,
        seed=42,
        metrics=cpp_metrics,
    )

    assert python_values == cpp_values.tolist()
    assert python_metrics == cpp_metrics


def test_cpp_quick_sort_rejects_invalid_pivot():
    values = np.array([3, 2, 1], dtype=np.float64)

    with pytest.raises(ValueError, match="unknown pivot strategy"):
        cpp.quick_sort(values, pivot="invalid")


def test_cpp_quick_sort_rejects_invalid_recursion():
    values = np.array([3, 2, 1], dtype=np.float64)

    with pytest.raises(ValueError, match="unknown recursion strategy"):
        cpp.quick_sort(values, recursion="invalid")

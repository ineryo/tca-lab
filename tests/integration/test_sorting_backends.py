import numpy as np
import pytest

from tca import _core
from tca.algorithms.sorting import (
    available_sorting_algorithms,
    sort,
)
from tca.core.instrumentation import Metrics

METHODS = available_sorting_algorithms()


def test_python_cpp_registries_match():
    python_methods = set(METHODS)

    cpp_methods = set(_core.available_sorting_algorithms())

    assert python_methods == cpp_methods


@pytest.mark.parametrize("method", METHODS)
def test_cpp_sort(method):
    values = np.array(
        [5, 2, 4, 8, 4, 2, 1],
        dtype=np.float64,
    )

    result = _core.sort(
        values,
        method,
    )

    assert result is None

    np.testing.assert_array_equal(
        values,
        np.array(
            [1, 2, 2, 4, 4, 5, 8],
            dtype=np.float64,
        ),
    )


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "backend",
    ["python", "cpp"],
)
@pytest.mark.parametrize(
    "size",
    [0, 1, 2, 10, 100],
)
def test_sort_random_inputs(
    method,
    backend,
    size,
):
    rng = np.random.default_rng(42)

    values = rng.integers(
        -100,
        101,
        size=size,
    ).astype(np.float64)

    expected = np.sort(values.copy())

    sort(
        values,
        method=method,
        backend=backend,
    )

    np.testing.assert_array_equal(
        values,
        expected,
    )


@pytest.mark.parametrize("method", METHODS)
def test_sort_metrics_python_cpp_equivalence(
    method,
):
    original = np.array(
        [5, 2, 4, 8, 4, 2, 1],
        dtype=np.float64,
    )

    python_values = original.copy()
    cpp_values = original.copy()

    python_metrics = Metrics()
    cpp_metrics = Metrics()

    sort(
        python_values,
        method=method,
        backend="python",
        metrics=python_metrics,
    )

    sort(
        cpp_values,
        method=method,
        backend="cpp",
        metrics=cpp_metrics,
    )

    np.testing.assert_array_equal(
        python_values,
        cpp_values,
    )

    assert python_metrics == cpp_metrics

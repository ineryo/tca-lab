import numpy as np
import pytest

from tca.algorithms.sorting import (
    available_sorting_algorithms,
    sort,
)
from tca.core.instrumentation import Metrics, Trace

METHODS = available_sorting_algorithms()


def test_sorting_registry_is_not_empty():
    assert METHODS


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "backend",
    ["python", "cpp"],
)
def test_sort_public_api(method, backend):
    values = np.array(
        [5, 2, 4, 8, 4, 2, 1],
        dtype=np.float64,
    )

    result = sort(
        values,
        method=method,
        backend=backend,
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
def test_sort_public_api_trace(method):
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )
    metrics = Metrics()
    trace = Trace()

    result = sort(
        values,
        method=method,
        backend="python",
        metrics=metrics,
        trace=trace,
    )

    assert result is None

    np.testing.assert_array_equal(
        values,
        np.array(
            [1, 2, 3],
            dtype=np.float64,
        ),
    )

    assert len(trace) > 0


def test_sort_rejects_trace_with_cpp_backend():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )
    trace = Trace()

    with pytest.raises(
        ValueError,
        match="trace is only supported by the Python backend",
    ):
        sort(
            values,
            method=METHODS[0],
            backend="cpp",
            trace=trace,
        )


def test_sort_rejects_unknown_method():
    values = np.array(
        [3, 2, 1],
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        sort(
            values,
            method="does_not_exist",
        )


def test_sort_rejects_unknown_backend():
    values = np.array(
        [3, 2, 1],
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        sort(
            values,
            method=METHODS[0],
            backend="cuda",
        )


@pytest.mark.parametrize("method", ["insertion", "merge", "radix_binary"])
def test_argsort_public_api_is_stable_and_does_not_modify_input(method):
    from tca.algorithms.sorting import argsort

    values = np.array([3.0, 1.0, 3.0, 1.0, 3.0], dtype=np.float64)
    original = values.copy()

    order = argsort(values, method=method)

    np.testing.assert_array_equal(order, np.array([1, 3, 0, 2, 4]))
    np.testing.assert_array_equal(values, original)


@pytest.mark.parametrize("method", ["insertion", "merge", "radix_binary"])
@pytest.mark.parametrize("size", [0, 1, 2, 10, 100])
def test_argsort_public_api_matches_stable_numpy_sort(method, size):
    from tca.algorithms.sorting import argsort

    rng = np.random.default_rng(42)
    values = rng.integers(-10, 11, size=size).astype(np.float64)

    order = argsort(values, method=method)
    expected = np.argsort(values, kind="stable")

    np.testing.assert_array_equal(order, expected)


def test_argsort_rejects_unknown_method():
    from tca.algorithms.sorting import argsort

    values = np.array([3.0, 2.0, 1.0], dtype=np.float64)

    with pytest.raises(ValueError, match="unknown argsort method"):
        argsort(values, method="quick")


def test_argsort_rejects_python_backend():
    from tca.algorithms.sorting import argsort

    values = np.array([3.0, 2.0, 1.0], dtype=np.float64)

    with pytest.raises(ValueError, match="only backend='cpp'"):
        argsort(values, backend="python")


def test_argsort_requires_float64():
    from tca.algorithms.sorting import argsort

    values = np.array([3.0, 2.0, 1.0], dtype=np.float32)

    with pytest.raises(TypeError, match="dtype=np.float64"):
        argsort(values)

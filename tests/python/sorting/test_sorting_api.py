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

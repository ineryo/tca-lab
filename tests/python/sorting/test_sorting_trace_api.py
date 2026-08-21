import numpy as np
import pytest

from tca.algorithms.sorting import (
    SortTraceResult,
    available_sorting_algorithms,
    trace_sort,
)

METHODS = available_sorting_algorithms()


@pytest.mark.parametrize("method", METHODS)
def test_trace_sort(method):
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method=method,
    )

    assert isinstance(result, SortTraceResult)

    np.testing.assert_array_equal(
        result.initial_values,
        np.array([3, 1, 2], dtype=np.float64),
    )

    np.testing.assert_array_equal(
        result.final_values,
        np.array([1, 2, 3], dtype=np.float64),
    )

    np.testing.assert_array_equal(
        values,
        result.final_values,
    )

    assert len(result.trace) > 0

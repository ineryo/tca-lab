import numpy as np
import pytest

from tca.algorithms.sorting import (
    available_sorting_algorithms,
    sort,
)

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

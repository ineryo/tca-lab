import numpy as np
import pytest

from tca import _core
from tca.algorithms.sorting import selection_sort
from tca.reference.sorting.selection_sort import (
    selection_sort as reference_selection_sort,
)


def test_cpp_selection_sort():
    values = np.array(
        [5, 2, 4, 8, 4, 2, 1],
        dtype=np.float64,
    )

    result = _core.selection_sort(values)

    assert result is None

    np.testing.assert_array_equal(
        values,
        np.array(
            [1, 2, 2, 4, 4, 5, 8],
            dtype=np.float64,
        ),
    )


def test_selection_sort_python_cpp_equivalence():
    original = [5, 2, 4, 8, 4, 2, 1]

    python_values = original.copy()

    cpp_values = np.array(
        original,
        dtype=np.float64,
    )

    reference_selection_sort(python_values)
    _core.selection_sort(cpp_values)

    np.testing.assert_array_equal(
        cpp_values,
        np.asarray(python_values),
    )


@pytest.mark.parametrize("backend", ["python", "cpp"])
@pytest.mark.parametrize("size", [0, 1, 2, 10, 100])
def test_selection_sort_random_inputs(backend, size):
    rng = np.random.default_rng(42)

    values = rng.integers(
        -100,
        101,
        size=size,
    ).astype(np.float64)

    expected = np.sort(values.copy())

    selection_sort(values, backend=backend)

    np.testing.assert_array_equal(values, expected)

import numpy as np
import pytest

from tca.algorithms.sorting import selection_sort


@pytest.mark.parametrize("backend", ["python", "cpp"])
def test_selection_sort_public_api(backend):
    values = np.array(
        [5, 2, 4, 8, 4, 2, 1],
        dtype=np.float64,
    )

    result = selection_sort(values, backend=backend)

    assert result is None

    np.testing.assert_array_equal(
        values,
        np.array(
            [1, 2, 2, 4, 4, 5, 8],
            dtype=np.float64,
        ),
    )


def test_selection_sort_rejects_unknown_backend():
    values = np.array([3, 2, 1], dtype=np.float64)

    with pytest.raises(ValueError):
        selection_sort(values, backend="cuda")

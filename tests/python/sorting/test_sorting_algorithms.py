import numpy as np
import pytest

from tca.reference.sorting.registry import (
    available_sorting_algorithms,
    get_sorting_algorithm,
)

METHODS = available_sorting_algorithms()


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], []),
        ([1], [1]),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ([3, 1, 3, 1, 2], [1, 1, 2, 3, 3]),
        ([5, 2, 4, 8, 4, 2, 1], [1, 2, 2, 4, 4, 5, 8]),
    ],
)
def test_sorting_algorithm(method, values, expected):
    algorithm = get_sorting_algorithm(method)

    result = algorithm(values)

    assert result is None
    assert values == expected


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("size", [0, 1, 2, 10, 100, 1000])
def test_sorting_algorithm_random_inputs(method, size):
    rng = np.random.default_rng(42)

    values = rng.integers(
        -100,
        101,
        size=size,
    ).tolist()

    expected = sorted(values)

    algorithm = get_sorting_algorithm(method)

    algorithm(values)

    assert values == expected

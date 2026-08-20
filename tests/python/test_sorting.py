import pytest

from tca.core.instrumentation import Metrics
from tca.reference.sorting.selection_sort import selection_sort


def test_selection_sort():
    values = [5, 2, 4, 8, 4, 2, 1]

    result = selection_sort(values)

    assert result is None
    assert values == [1, 2, 2, 4, 4, 5, 8]


def test_selection_sort_empty():
    values = []

    selection_sort(values)

    assert values == []


def test_selection_sort_single_element():
    values = [42]

    selection_sort(values)

    assert values == [42]


def test_selection_sort_already_sorted():
    values = [1, 2, 3, 4, 5]

    selection_sort(values)

    assert values == [1, 2, 3, 4, 5]


def test_selection_sort_reverse():
    values = [5, 4, 3, 2, 1]

    selection_sort(values)

    assert values == [1, 2, 3, 4, 5]


def test_selection_sort_duplicates():
    values = [3, 1, 3, 1, 2]

    selection_sort(values)

    assert values == [1, 1, 2, 3, 3]


def test_selection_sort_metrics():
    values = [3, 1, 2]
    metrics = Metrics()

    result = selection_sort(
        values,
        metrics=metrics,
    )

    assert result is None
    assert values == [1, 2, 3]

    assert metrics.comparisons == 3
    assert metrics.swaps == 2


def test_selection_sort_sorted_input_requires_no_swaps():
    values = [1, 2, 3, 4, 5]
    metrics = Metrics()

    selection_sort(
        values,
        metrics=metrics,
    )

    assert values == [1, 2, 3, 4, 5]
    assert metrics.comparisons == 10
    assert metrics.swaps == 0


@pytest.mark.parametrize(
    "size",
    [0, 1, 2, 5, 10, 100],
)
def test_selection_sort_comparison_count(size):
    values = list(range(size, 0, -1))
    metrics = Metrics()

    selection_sort(
        values,
        metrics=metrics,
    )

    expected = size * (size - 1) // 2

    assert metrics.comparisons == expected

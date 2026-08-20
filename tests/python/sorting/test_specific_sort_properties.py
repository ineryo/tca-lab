import pytest

from tca.core.instrumentation import Metrics
from tca.reference.sorting.insertion_sort import insertion_sort
from tca.reference.sorting.selection_sort import selection_sort


def test_selection_sort_metrics():
    values = [3, 1, 2]
    metrics = Metrics()

    selection_sort(
        values,
        metrics=metrics,
    )

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


@pytest.mark.parametrize(
    "size",
    [1, 2, 5, 10, 100],
)
def test_insertion_sort_best_case(size):
    values = list(range(size))
    metrics = Metrics()

    insertion_sort(
        values,
        metrics=metrics,
    )

    assert metrics.comparisons == size - 1
    assert metrics.writes == size - 1
    assert metrics.swaps == 0


@pytest.mark.parametrize(
    "size",
    [1, 2, 5, 10, 100],
)
def test_insertion_sort_worst_case(size):
    values = list(range(size, 0, -1))
    metrics = Metrics()

    insertion_sort(
        values,
        metrics=metrics,
    )

    expected_comparisons = size * (size - 1) // 2

    expected_writes = expected_comparisons + max(size - 1, 0)

    assert metrics.comparisons == expected_comparisons
    assert metrics.writes == expected_writes
    assert metrics.swaps == 0

import pytest

from tca.core.instrumentation import Metrics, Trace
from tca.reference.sorting.insertion_sort import insertion_sort
from tca.reference.sorting.merge_sort import merge_sort
from tca.reference.sorting.quick_sort import quick_sort
from tca.reference.sorting.radix_sort import radix_sort
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


def test_selection_sort_trace():
    values = [3, 1, 2]
    metrics = Metrics()
    trace = Trace()

    selection_sort(
        values,
        metrics=metrics,
        trace=trace,
    )

    assert values == [1, 2, 3]
    assert metrics.comparisons == 3
    assert metrics.swaps == 2
    assert metrics.writes == 4

    operation_events = [event for event in trace if event.kind in {"compare", "swap"}]

    assert [event.kind for event in operation_events] == [
        "compare",
        "compare",
        "swap",
        "compare",
        "swap",
    ]

    compare_events = [event for event in trace if event.kind == "compare"]

    assert [event.indices for event in compare_events] == [
        (1, 0),
        (2, 1),
        (2, 1),
    ]

    minimum_events = [event for event in trace if event.kind == "select_minimum"]

    assert [event.indices for event in minimum_events] == [
        (0,),
        (1,),
        (1,),
        (2,),
    ]


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


def test_insertion_sort_trace():
    values = [3, 1, 2]
    metrics = Metrics()
    trace = Trace()

    insertion_sort(
        values,
        metrics=metrics,
        trace=trace,
    )

    assert values == [1, 2, 3]
    assert metrics.comparisons == 3
    assert metrics.swaps == 0
    assert metrics.writes == 4

    key_events = [event for event in trace if event.kind == "select_key"]

    assert [event.indices for event in key_events] == [
        (1,),
        (2,),
    ]

    assert [event.values for event in key_events] == [
        (1,),
        (2,),
    ]

    compare_events = [event for event in trace if event.kind == "compare"]

    assert [event.indices for event in compare_events] == [
        (1, 0),
        (2, 1),
        (2, 0),
    ]


@pytest.mark.parametrize(
    "size",
    [1, 2, 4, 8, 16, 32],
)
def test_merge_sort_write_count_for_power_of_two(size):
    values = list(range(size, 0, -1))
    metrics = Metrics()

    merge_sort(
        values,
        metrics=metrics,
    )

    levels = size.bit_length() - 1
    expected_writes = 2 * size * levels

    assert metrics.writes == expected_writes
    assert metrics.swaps == 0


def test_merge_sort_is_stable():
    class Item:
        def __init__(self, key, label):
            self.key = key
            self.label = label

        def __lt__(self, other):
            return self.key < other.key

    values = [
        Item(2, "a"),
        Item(1, "b"),
        Item(2, "c"),
        Item(1, "d"),
        Item(2, "e"),
    ]

    merge_sort(values)

    assert [(item.key, item.label) for item in values] == [
        (1, "b"),
        (1, "d"),
        (2, "a"),
        (2, "c"),
        (2, "e"),
    ]


def test_merge_sort_trace():
    values = [4, 3, 2, 1]
    metrics = Metrics()
    trace = Trace()

    merge_sort(
        values,
        metrics=metrics,
        trace=trace,
    )

    assert values == [1, 2, 3, 4]
    assert metrics.comparisons == 4
    assert metrics.swaps == 0
    assert metrics.writes == 16

    merge_events = [event for event in trace if event.kind == "merge_range"]

    assert [event.indices for event in merge_events] == [
        (0, 1, 2),
        (2, 3, 4),
        (0, 2, 4),
    ]

    write_events = [event for event in trace if event.kind == "write"]

    buffer_writes = [
        event for event in write_events if event.data.get("target") == "buffer"
    ]

    value_writes = [
        event for event in write_events if event.data.get("target") == "values"
    ]

    assert len(buffer_writes) == 8
    assert len(value_writes) == 8


@pytest.mark.parametrize(
    "size",
    [1, 2, 5, 10, 100],
)
def test_quick_sort_sorted_input(size):
    values = list(range(size))
    metrics = Metrics()

    quick_sort(values, metrics=metrics)

    expected_comparisons = 0 if size < 2 else size * (size + 1) // 2 + size - 2

    assert metrics.comparisons == expected_comparisons
    assert metrics.swaps == 0
    assert metrics.writes == 0


@pytest.mark.parametrize(
    "pivot",
    ["first", "quarter", "random"],
)
@pytest.mark.parametrize(
    "recursion",
    ["classic", "bounded"],
)
def test_quick_sort_strategies(pivot, recursion):
    values = [8, 3, 7, 4, 9, 2, 6, 5, 1]

    quick_sort(values, pivot=pivot, recursion=recursion, seed=42)

    assert values == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_quick_sort_rejects_invalid_pivot():
    with pytest.raises(ValueError, match="unknown pivot strategy"):
        quick_sort([], pivot="invalid")


def test_quick_sort_rejects_invalid_recursion():
    with pytest.raises(ValueError, match="unknown recursion strategy"):
        quick_sort([], recursion="invalid")


def test_quick_sort_bounded_avoids_linear_recursion_depth():
    values = list(range(2000))

    quick_sort(values, pivot="first", recursion="bounded")

    assert values == list(range(2000))


def test_quick_sort_trace():
    values = [3, 1, 2]
    metrics = Metrics()
    trace = Trace()

    quick_sort(
        values,
        metrics=metrics,
        trace=trace,
        pivot="first",
        recursion="bounded",
    )

    assert values == [1, 2, 3]

    pivot_events = [event for event in trace if event.kind == "choose_pivot"]

    partition_events = [event for event in trace if event.kind == "partition"]

    compare_events = [event for event in trace if event.kind == "compare"]

    swap_events = [event for event in trace if event.kind == "swap"]

    assert [event.indices for event in pivot_events] == [
        (0,),
        (0,),
    ]

    assert [event.indices for event in partition_events] == [
        (0, 2, 2),
        (0, 1, 1),
    ]

    assert metrics.comparisons == len(compare_events)
    assert metrics.swaps == len(swap_events)
    assert metrics.writes == 2 * len(swap_events)

    assert [event.values for event in pivot_events] == [
        (3,),
        (2,),
    ]

    assert [event.data["strategy"] for event in pivot_events] == [
        "first",
        "first",
    ]


def test_radix_sort_metrics():
    values = [5.1342, 5.1346, 5.1344, 3.2, 5.1]
    metrics = Metrics()

    radix_sort(values, metrics=metrics, digits=3)

    assert values == [3.2, 5.1, 5.1342, 5.1346, 5.1344]
    assert metrics.comparisons == 0
    assert metrics.swaps == 0
    assert metrics.writes == 30


def test_radix_sort_trace():
    values = [5.1342, 5.1346, 5.1344, 3.2, 5.1]
    metrics = Metrics()
    trace = Trace()

    radix_sort(
        values,
        metrics=metrics,
        trace=trace,
        digits=3,
    )

    assert values == [3.2, 5.1, 5.1342, 5.1346, 5.1344]
    assert metrics.comparisons == 0
    assert metrics.swaps == 0
    assert metrics.writes == 30

    pass_events = [event for event in trace if event.kind == "radix_pass"]

    assert [event.data["exponent"] for event in pass_events] == [
        1,
        10,
        100,
        1000,
    ]

    assert pass_events[0].data["order"] == (
        3,
        4,
        0,
        1,
        2,
    )

    assert pass_events[-1].values == (
        3.2,
        5.1,
        5.1342,
        5.1346,
        5.1344,
    )

    write_events = [event for event in trace if event.kind == "write"]

    assert sum(event.data.get("target") == "indices" for event in write_events) == 20

    assert (
        sum(event.data.get("target") == "ordered_values" for event in write_events) == 5
    )

    assert sum(event.data.get("target") == "values" for event in write_events) == 5

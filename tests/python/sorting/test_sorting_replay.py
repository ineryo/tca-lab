import numpy as np
import pytest

from tca.algorithms.sorting import (
    available_sorting_algorithms,
    trace_sort,
)
from tca.algorithms.sorting.replay import (
    SortingState,
    make_sorting_replay,
    sorting_reducer,
)
from tca.core.instrumentation import TraceEvent

METHODS = available_sorting_algorithms()


@pytest.mark.parametrize("method", METHODS)
def test_sorting_replay_reconstructs_final_state(method):
    values = np.array(
        [5, 2, 4, 1, 3],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method=method,
    )

    replay = make_sorting_replay(result)

    replay.seek(replay.total_steps)

    np.testing.assert_array_equal(
        replay.state.values,
        result.final_values,
    )

    assert replay.state.metrics.comparisons == result.metrics.comparisons
    assert replay.state.metrics.swaps == result.metrics.swaps
    assert replay.state.metrics.writes == result.metrics.writes


def test_sorting_replay_tracks_intermediate_metrics():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="selection",
    )

    replay = make_sorting_replay(result)

    replay.seek(4)

    assert replay.state.metrics.comparisons == 2
    assert replay.state.metrics.swaps == 0
    assert replay.state.metrics.writes == 0

    replay.next()

    assert replay.current.event.kind == "swap"
    assert replay.state.metrics.comparisons == 2
    assert replay.state.metrics.swaps == 1
    assert replay.state.metrics.writes == 2


def test_sorting_replay_metrics_follow_navigation():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="selection",
    )

    replay = make_sorting_replay(result)

    replay.seek(replay.total_steps)

    final_comparisons = replay.state.metrics.comparisons
    final_swaps = replay.state.metrics.swaps
    final_writes = replay.state.metrics.writes

    replay.reset()

    assert replay.state.metrics.comparisons == 0
    assert replay.state.metrics.swaps == 0
    assert replay.state.metrics.writes == 0

    replay.seek(replay.total_steps)

    assert replay.state.metrics.comparisons == final_comparisons
    assert replay.state.metrics.swaps == final_swaps
    assert replay.state.metrics.writes == final_writes


def test_sorting_replay_tracks_intermediate_selection_state():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="selection",
    )

    replay = make_sorting_replay(result)

    replay.seek(4)

    np.testing.assert_array_equal(
        replay.state.values,
        np.array([3, 1, 2], dtype=np.float64),
    )

    replay.next()

    assert replay.current.event.kind == "swap"

    np.testing.assert_array_equal(
        replay.state.values,
        np.array([1, 3, 2], dtype=np.float64),
    )


def test_sorting_reducer_ignores_auxiliary_write():
    state = SortingState(
        values=np.array(
            [3, 1, 2],
            dtype=np.float64,
        )
    )

    event = TraceEvent(
        kind="write",
        indices=(0,),
        values=(None, 99),
        data={"target": "buffer"},
    )

    sorting_reducer(state, event)

    np.testing.assert_array_equal(
        state.values,
        np.array([3, 1, 2], dtype=np.float64),
    )


def test_sorting_reducer_applies_values_write():
    state = SortingState(
        values=np.array(
            [3, 1, 2],
            dtype=np.float64,
        )
    )

    event = TraceEvent(
        kind="write",
        indices=(1,),
        values=(1, 7),
        data={"target": "values"},
    )

    sorting_reducer(state, event)

    np.testing.assert_array_equal(
        state.values,
        np.array([3, 7, 2], dtype=np.float64),
    )

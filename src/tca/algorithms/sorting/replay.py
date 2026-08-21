from dataclasses import dataclass, field

import numpy as np

from tca.core.instrumentation import Metrics, TraceEvent
from tca.core.replay import Replay

from ._trace import SortTraceResult


@dataclass(slots=True)
class SortingState:
    values: np.ndarray
    metrics: Metrics = field(default_factory=Metrics)
    radix_base_values: list[object] | None = None
    radix_values: list[object | None] | None = None
    radix_writes_in_pass: int = 0


def sorting_reducer(
    state: SortingState,
    event: TraceEvent,
) -> SortingState:
    if event.kind == "compare":
        state.metrics.comparisons += 1

    elif event.kind == "swap":
        index_i, index_j = event.indices

        state.values[index_i], state.values[index_j] = (
            state.values[index_j],
            state.values[index_i],
        )

        state.metrics.swaps += 1
        state.metrics.writes += 2

    elif event.kind == "write":
        target = event.data.get("target")

        if target == "indices":
            if state.radix_values is None or state.radix_writes_in_pass == len(
                state.values
            ):
                state.radix_values = [None] * len(state.values)
                state.radix_writes_in_pass = 0

            (position,) = event.indices
            source_index = int(event.values[-1])

            state.radix_values[position] = state.values[source_index]
            state.radix_writes_in_pass += 1

        elif target is None or target == "values":
            (index,) = event.indices
            value = event.values[-1]

            state.values[index] = value

        state.metrics.writes += 1

    elif event.kind == "radix_pass":
        state.radix_base_values = list(event.values)

    return state


def make_sorting_replay(
    result: SortTraceResult,
) -> Replay[SortingState, TraceEvent]:
    initial_state = SortingState(
        values=result.initial_values.copy(),
    )

    return Replay(
        initial_state=initial_state,
        events=result.trace.events,
        reducer=sorting_reducer,
    )

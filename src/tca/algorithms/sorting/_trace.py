from dataclasses import dataclass

import numpy as np

from tca.core.instrumentation import Metrics, Trace

from ._sort import sort


@dataclass
class SortTraceResult:
    initial_values: np.ndarray
    final_values: np.ndarray
    metrics: Metrics
    trace: Trace


def trace_sort(
    values: np.ndarray,
    *,
    method: str,
) -> SortTraceResult:
    initial_values = values.copy()
    metrics = Metrics()
    trace = Trace()

    sort(
        values,
        method=method,
        backend="python",
        metrics=metrics,
        trace=trace,
    )

    return SortTraceResult(
        initial_values=initial_values,
        final_values=values.copy(),
        metrics=metrics,
        trace=trace,
    )

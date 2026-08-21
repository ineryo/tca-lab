from time import perf_counter_ns
from typing import Literal

from tca.algorithms.sorting import sort
from tca.core.instrumentation import Metrics

from .datasets import SortingCase, generate_sorting_data
from .results import SortingResult

Backend = Literal["python", "cpp"]
MeasurementMode = Literal["time", "metrics"]

MEASUREMENT_MODES = (
    "time",
    "metrics",
)


def measure_sorting_case(
    case: SortingCase,
    *,
    algorithm: str,
    backend: Backend = "python",
    mode: MeasurementMode = "time",
) -> SortingResult:
    if mode not in MEASUREMENT_MODES:
        raise ValueError(
            f"unknown measurement mode {mode!r}; "
            f"available modes: {MEASUREMENT_MODES}"
        )

    values = generate_sorting_data(
        case.n,
        case.family,
        seed=case.seed,
    ).copy()

    if mode == "time":
        start_ns = perf_counter_ns()

        sort(
            values,
            method=algorithm,
            backend=backend,
        )

        elapsed_seconds = (perf_counter_ns() - start_ns) / 1_000_000_000

        return SortingResult(
            case=case,
            algorithm=algorithm,
            backend=backend,
            mode=mode,
            elapsed_seconds=elapsed_seconds,
        )

    metrics = Metrics()

    sort(
        values,
        method=algorithm,
        backend=backend,
        metrics=metrics,
    )

    return SortingResult(
        case=case,
        algorithm=algorithm,
        backend=backend,
        mode=mode,
        comparisons=metrics.comparisons,
        swaps=metrics.swaps,
        writes=metrics.writes,
    )

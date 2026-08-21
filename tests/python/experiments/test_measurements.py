import pytest

import tca.experiments.measurements as measurements
from tca.algorithms.sorting import sort
from tca.core.instrumentation import Metrics
from tca.experiments import (
    MEASUREMENT_MODES,
    SortingCase,
    generate_sorting_data,
    measure_sorting_case,
)


def make_case() -> SortingCase:
    return SortingCase(
        n=20,
        family="uniform_random",
        repetition=0,
        seed=42,
    )


@pytest.mark.parametrize(
    "backend",
    ["python", "cpp"],
)
def test_measure_time_populates_only_elapsed_seconds(
    backend,
):
    result = measure_sorting_case(
        make_case(),
        algorithm="merge",
        backend=backend,
        mode="time",
    )

    assert result.elapsed_seconds is not None
    assert result.elapsed_seconds >= 0.0

    assert result.comparisons is None
    assert result.swaps is None
    assert result.writes is None
    assert result.peak_memory_bytes is None


def test_measure_time_uses_perf_counter_ns(
    monkeypatch,
):
    times = iter(
        [
            1_000_000_000,
            1_250_000_000,
        ]
    )

    monkeypatch.setattr(
        measurements,
        "perf_counter_ns",
        lambda: next(times),
    )

    result = measure_sorting_case(
        make_case(),
        algorithm="merge",
        backend="python",
        mode="time",
    )

    assert result.elapsed_seconds == 0.25


@pytest.mark.parametrize(
    "backend",
    ["python", "cpp"],
)
def test_measure_metrics_matches_direct_instrumentation(
    backend,
):
    case = make_case()

    values = generate_sorting_data(
        case.n,
        case.family,
        seed=case.seed,
    )

    expected = Metrics()

    sort(
        values,
        method="merge",
        backend=backend,
        metrics=expected,
    )

    result = measure_sorting_case(
        case,
        algorithm="merge",
        backend=backend,
        mode="metrics",
    )

    assert result.elapsed_seconds is None

    assert result.comparisons == expected.comparisons
    assert result.swaps == expected.swaps
    assert result.writes == expected.writes


def test_measure_metrics_is_reproducible():
    first = measure_sorting_case(
        make_case(),
        algorithm="quick",
        backend="python",
        mode="metrics",
    )

    second = measure_sorting_case(
        make_case(),
        algorithm="quick",
        backend="python",
        mode="metrics",
    )

    assert first == second


def test_measurement_result_preserves_case_metadata():
    case = make_case()

    result = measure_sorting_case(
        case,
        algorithm="radix",
        backend="cpp",
        mode="metrics",
    )

    assert result.case == case
    assert result.algorithm == "radix"
    assert result.backend == "cpp"
    assert result.mode == "metrics"
    assert result.status == "ok"


def test_measure_sorting_case_rejects_unknown_mode():
    with pytest.raises(
        ValueError,
        match="unknown measurement mode",
    ):
        measure_sorting_case(
            make_case(),
            algorithm="merge",
            mode="unknown",
        )


def test_measurement_modes_include_memory():
    assert MEASUREMENT_MODES == (
        "time",
        "metrics",
        "memory",
    )


@pytest.mark.parametrize(
    "backend",
    ["python", "cpp"],
)
def test_measure_memory_populates_only_peak_memory_bytes(
    backend,
):
    result = measure_sorting_case(
        make_case(),
        algorithm="merge",
        backend=backend,
        mode="memory",
    )

    assert result.peak_memory_bytes is not None
    assert result.peak_memory_bytes >= 0

    assert result.elapsed_seconds is None
    assert result.comparisons is None
    assert result.swaps is None
    assert result.writes is None


@pytest.mark.parametrize(
    "backend",
    ["python", "cpp"],
)
def test_measure_memory_preserves_result_metadata(
    backend,
):
    case = make_case()

    result = measure_sorting_case(
        case,
        algorithm="merge",
        backend=backend,
        mode="memory",
    )

    assert result.case == case
    assert result.algorithm == "merge"
    assert result.backend == backend
    assert result.mode == "memory"
    assert result.status == "ok"

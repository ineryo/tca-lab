import pytest

from tca.experiments import (
    BACKENDS,
    MEASUREMENT_MODES,
    SortingCase,
    SortingTask,
    load_sorting_results,
    run_sorting_task,
    run_sorting_tasks,
    sorting_task_catalog,
)


def make_case(
    n: int = 20,
) -> SortingCase:
    return SortingCase(
        n=n,
        family="uniform_random",
        repetition=0,
        seed=42,
    )


def test_sorting_task_catalog_expands_dimensions():
    tasks = sorting_task_catalog(
        cases=(make_case(),),
        algorithms=("merge",),
    )

    assert len(tasks) == (len(BACKENDS) * len(MEASUREMENT_MODES))


def test_sorting_task_catalog_accepts_subset():
    tasks = sorting_task_catalog(
        cases=(make_case(),),
        algorithms=("merge",),
        backends=("python",),
        modes=("time", "metrics"),
    )

    assert tasks == (
        SortingTask(
            case=make_case(),
            algorithm="merge",
            backend="python",
            mode="time",
        ),
        SortingTask(
            case=make_case(),
            algorithm="merge",
            backend="python",
            mode="metrics",
        ),
    )


def test_sorting_task_catalog_rejects_unknown_algorithm():
    with pytest.raises(
        ValueError,
        match="unknown sorting algorithms",
    ):
        sorting_task_catalog(
            cases=(make_case(),),
            algorithms=("unknown",),
        )


def test_sorting_task_catalog_rejects_unknown_backend():
    with pytest.raises(
        ValueError,
        match="unknown backends",
    ):
        sorting_task_catalog(
            cases=(make_case(),),
            algorithms=("merge",),
            backends=("unknown",),
        )


def test_sorting_task_catalog_rejects_unknown_mode():
    with pytest.raises(
        ValueError,
        match="unknown measurement modes",
    ):
        sorting_task_catalog(
            cases=(make_case(),),
            algorithms=("merge",),
            modes=("unknown",),
        )


def test_run_sorting_task_returns_result():
    task = SortingTask(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="metrics",
    )

    result = run_sorting_task(task)

    assert result.status == "ok"
    assert result.case == task.case
    assert result.algorithm == task.algorithm
    assert result.backend == task.backend
    assert result.mode == task.mode


def test_run_sorting_task_converts_error_to_result():
    task = SortingTask(
        case=make_case(),
        algorithm="unknown",
        backend="python",
        mode="metrics",
    )

    result = run_sorting_task(task)

    assert result.status == "error"
    assert result.message is not None


def test_run_sorting_task_applies_cutoff():
    task = SortingTask(
        case=make_case(n=1_000_000),
        algorithm="selection",
        backend="python",
        mode="time",
    )

    result = run_sorting_task(
        task,
        timeout_seconds=0.01,
    )

    assert result.status == "cutoff"
    assert result.elapsed_seconds is None
    assert result.message is not None


def test_run_sorting_task_rejects_invalid_timeout():
    task = SortingTask(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="time",
    )

    with pytest.raises(
        ValueError,
        match="timeout_seconds must be greater than zero",
    ):
        run_sorting_task(
            task,
            timeout_seconds=0,
        )


def test_memory_measurement_runs_directly_with_timeout_parameter():
    task = SortingTask(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="memory",
    )

    result = run_sorting_task(
        task,
        timeout_seconds=0.01,
    )

    assert result.status == "ok"
    assert result.peak_memory_bytes is not None


def test_run_sorting_tasks_preserves_order():
    tasks = (
        SortingTask(
            case=make_case(),
            algorithm="merge",
            backend="python",
            mode="metrics",
        ),
        SortingTask(
            case=make_case(),
            algorithm="radix",
            backend="python",
            mode="metrics",
        ),
    )

    results = run_sorting_tasks(tasks)

    assert tuple(result.algorithm for result in results) == (
        "merge",
        "radix",
    )


def test_run_sorting_tasks_can_persist_incrementally(
    tmp_path,
):
    path = tmp_path / "results.jsonl"

    tasks = (
        SortingTask(
            case=make_case(),
            algorithm="merge",
            backend="python",
            mode="metrics",
        ),
        SortingTask(
            case=make_case(),
            algorithm="radix",
            backend="python",
            mode="metrics",
        ),
    )

    results = run_sorting_tasks(
        tasks,
        output_path=path,
    )

    assert load_sorting_results(path) == results

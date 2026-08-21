from collections.abc import Iterable
from dataclasses import dataclass
from multiprocessing import get_context
from multiprocessing.connection import Connection
from pathlib import Path

from tca.algorithms.sorting import available_sorting_algorithms

from .datasets import SortingCase, sorting_case_catalog
from .measurements import MEASUREMENT_MODES, measure_sorting_case
from .results import SortingResult, append_sorting_result

BACKENDS = (
    "python",
    "cpp",
)


@dataclass(frozen=True, slots=True)
class SortingTask:
    case: SortingCase
    algorithm: str
    backend: str
    mode: str


def sorting_task_catalog(
    *,
    cases: tuple[SortingCase, ...] | None = None,
    algorithms: tuple[str, ...] | None = None,
    backends: tuple[str, ...] = BACKENDS,
    modes: tuple[str, ...] = MEASUREMENT_MODES,
) -> tuple[SortingTask, ...]:
    if cases is None:
        cases = sorting_case_catalog()

    available_algorithms = available_sorting_algorithms()

    if algorithms is None:
        algorithms = available_algorithms

    unknown_algorithms = tuple(
        algorithm for algorithm in algorithms if algorithm not in available_algorithms
    )

    if unknown_algorithms:
        raise ValueError(f"unknown sorting algorithms: {unknown_algorithms}")

    unknown_backends = tuple(backend for backend in backends if backend not in BACKENDS)

    if unknown_backends:
        raise ValueError(f"unknown backends: {unknown_backends}")

    unknown_modes = tuple(mode for mode in modes if mode not in MEASUREMENT_MODES)

    if unknown_modes:
        raise ValueError(f"unknown measurement modes: {unknown_modes}")

    return tuple(
        SortingTask(
            case=case,
            algorithm=algorithm,
            backend=backend,
            mode=mode,
        )
        for case in cases
        for algorithm in algorithms
        for backend in backends
        for mode in modes
    )


def run_sorting_task(
    task: SortingTask,
    *,
    timeout_seconds: float | None = None,
) -> SortingResult:
    if timeout_seconds is None or task.mode == "memory":
        return _run_sorting_task_direct(task)

    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")

    return _run_sorting_task_with_timeout(
        task,
        timeout_seconds=timeout_seconds,
    )


def run_sorting_tasks(
    tasks: Iterable[SortingTask],
    *,
    timeout_seconds: float | None = None,
    output_path: str | Path | None = None,
) -> tuple[SortingResult, ...]:
    results: list[SortingResult] = []

    for task in tasks:
        result = run_sorting_task(
            task,
            timeout_seconds=timeout_seconds,
        )

        results.append(result)

        if output_path is not None:
            append_sorting_result(
                output_path,
                result,
            )

    return tuple(results)


def _run_sorting_task_direct(
    task: SortingTask,
) -> SortingResult:
    try:
        return measure_sorting_case(
            task.case,
            algorithm=task.algorithm,
            backend=task.backend,
            mode=task.mode,
        )

    except Exception as error:
        return _error_result(
            task,
            error,
        )


def _run_sorting_task_with_timeout(
    task: SortingTask,
    *,
    timeout_seconds: float,
) -> SortingResult:
    context = get_context("spawn")

    parent_connection, child_connection = context.Pipe(duplex=False)

    process = context.Process(
        target=_task_worker,
        args=(
            child_connection,
            task,
        ),
    )

    process.start()
    child_connection.close()

    try:
        process.join(timeout_seconds)

        if process.is_alive():
            process.terminate()
            process.join()

            return SortingResult(
                case=task.case,
                algorithm=task.algorithm,
                backend=task.backend,
                mode=task.mode,
                status="cutoff",
                message=(f"timeout after " f"{timeout_seconds:g} seconds"),
            )

        if not parent_connection.poll():
            return SortingResult(
                case=task.case,
                algorithm=task.algorithm,
                backend=task.backend,
                mode=task.mode,
                status="error",
                message=("measurement worker exited " f"with code {process.exitcode}"),
            )

        status, payload = parent_connection.recv()

        if status == "ok":
            return payload

        return SortingResult(
            case=task.case,
            algorithm=task.algorithm,
            backend=task.backend,
            mode=task.mode,
            status="error",
            message=str(payload),
        )

    finally:
        if process.is_alive():
            process.terminate()
            process.join()

        parent_connection.close()


def _task_worker(
    connection: Connection,
    task: SortingTask,
) -> None:
    try:
        result = measure_sorting_case(
            task.case,
            algorithm=task.algorithm,
            backend=task.backend,
            mode=task.mode,
        )

        connection.send(
            (
                "ok",
                result,
            )
        )

    except Exception as error:
        connection.send(
            (
                "error",
                f"{type(error).__name__}: {error}",
            )
        )

    finally:
        connection.close()


def _error_result(
    task: SortingTask,
    error: Exception,
) -> SortingResult:
    return SortingResult(
        case=task.case,
        algorithm=task.algorithm,
        backend=task.backend,
        mode=task.mode,
        status="error",
        message=f"{type(error).__name__}: {error}",
    )

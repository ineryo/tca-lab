import gc
from contextlib import suppress
from multiprocessing import get_context
from multiprocessing.connection import Connection
from time import perf_counter_ns
from typing import Literal

import psutil

from tca.algorithms.sorting import sort
from tca.core.instrumentation import Metrics

from .datasets import SortingCase, generate_sorting_data
from .results import SortingResult

Backend = Literal["python", "cpp"]
MeasurementMode = Literal["time", "metrics", "memory"]

MEASUREMENT_MODES = (
    "time",
    "metrics",
    "memory",
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

    if mode == "memory":
        peak_memory_bytes = _measure_peak_memory(
            case,
            algorithm=algorithm,
            backend=backend,
        )

        return SortingResult(
            case=case,
            algorithm=algorithm,
            backend=backend,
            mode=mode,
            peak_memory_bytes=peak_memory_bytes,
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


def _measure_peak_memory(
    case: SortingCase,
    *,
    algorithm: str,
    backend: Backend,
) -> int:
    context = get_context("spawn")

    parent_connection, child_connection = context.Pipe(duplex=True)

    process = context.Process(
        target=_memory_worker,
        args=(
            child_connection,
            case,
            algorithm,
            backend,
        ),
    )

    process.start()
    child_connection.close()

    try:
        status, payload = parent_connection.recv()

        if status == "error":
            raise RuntimeError(f"memory worker failed: {payload}")

        if status != "ready":
            raise RuntimeError(f"unexpected memory worker status: " f"{status!r}")

        baseline_rss = int(payload)
        peak_rss = baseline_rss

        monitored_process = psutil.Process(process.pid)

        parent_connection.send("start")

        completed = False
        error_message: str | None = None

        while True:
            try:
                current_rss = monitored_process.memory_info().rss

                peak_rss = max(
                    peak_rss,
                    current_rss,
                )
            except psutil.NoSuchProcess:
                pass

            if parent_connection.poll():
                status, payload = parent_connection.recv()

                if status == "done":
                    peak_rss = max(
                        peak_rss,
                        int(payload),
                    )

                    completed = True
                    break

                if status == "error":
                    error_message = str(payload)
                    break

                raise RuntimeError(f"unexpected memory worker " f"status: {status!r}")

            if not process.is_alive():
                break

        process.join()

        if error_message is not None:
            raise RuntimeError(f"memory worker failed: " f"{error_message}")

        if not completed:
            raise RuntimeError(
                "memory worker exited unexpectedly " f"with code {process.exitcode}"
            )

        return max(
            0,
            peak_rss - baseline_rss,
        )

    finally:
        if process.is_alive():
            process.terminate()
            process.join()

        parent_connection.close()


def _memory_worker(
    connection: Connection,
    case: SortingCase,
    algorithm: str,
    backend: Backend,
) -> None:
    try:
        values = generate_sorting_data(
            case.n,
            case.family,
            seed=case.seed,
        ).copy()

        gc.collect()

        process = psutil.Process()
        baseline_rss = process.memory_info().rss

        connection.send(
            (
                "ready",
                baseline_rss,
            )
        )

        command = connection.recv()

        if command != "start":
            raise RuntimeError(f"unexpected memory worker command: " f"{command!r}")

        sort(
            values,
            method=algorithm,
            backend=backend,
        )

        final_rss = process.memory_info().rss

        connection.send(
            (
                "done",
                final_rss,
            )
        )

    except Exception as error:
        with suppress(BrokenPipeError, EOFError):
            connection.send(
                (
                    "error",
                    f"{type(error).__name__}: {error}",
                )
            )

    finally:
        connection.close()

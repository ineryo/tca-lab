import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .datasets import SortingCase

RESULT_STATUSES = (
    "ok",
    "error",
    "skipped",
    "cutoff",
)


@dataclass(frozen=True, slots=True)
class SortingResult:
    case: SortingCase
    algorithm: str
    backend: str
    mode: str

    elapsed_seconds: float | None = None

    comparisons: int | None = None
    swaps: int | None = None
    writes: int | None = None

    peak_memory_bytes: int | None = None

    status: str = "ok"
    message: str | None = None

    def __post_init__(self) -> None:
        if self.status not in RESULT_STATUSES:
            raise ValueError(
                f"unknown result status {self.status!r}; "
                f"available statuses: {RESULT_STATUSES}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "n": self.case.n,
            "family": self.case.family,
            "repetition": self.case.repetition,
            "seed": self.case.seed,
            "algorithm": self.algorithm,
            "backend": self.backend,
            "mode": self.mode,
            "elapsed_seconds": self.elapsed_seconds,
            "comparisons": self.comparisons,
            "swaps": self.swaps,
            "writes": self.writes,
            "peak_memory_bytes": self.peak_memory_bytes,
            "status": self.status,
            "message": self.message,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "SortingResult":
        return cls(
            case=SortingCase(
                n=int(data["n"]),
                family=str(data["family"]),
                repetition=int(data["repetition"]),
                seed=int(data["seed"]),
            ),
            algorithm=str(data["algorithm"]),
            backend=str(data["backend"]),
            mode=str(data["mode"]),
            elapsed_seconds=_optional_float(data.get("elapsed_seconds")),
            comparisons=_optional_int(data.get("comparisons")),
            swaps=_optional_int(data.get("swaps")),
            writes=_optional_int(data.get("writes")),
            peak_memory_bytes=_optional_int(data.get("peak_memory_bytes")),
            status=str(data.get("status", "ok")),
            message=_optional_str(data.get("message")),
        )


def append_sorting_result(
    path: str | Path,
    result: SortingResult,
) -> None:
    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        json.dump(
            result.to_dict(),
            file,
            separators=(",", ":"),
        )
        file.write("\n")


def load_sorting_results(
    path: str | Path,
) -> tuple[SortingResult, ...]:
    input_path = Path(path)

    if not input_path.exists():
        return ()

    results: list[SortingResult] = []

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"invalid JSON on line {line_number} " f"of {input_path}"
                ) from error

            results.append(SortingResult.from_dict(data))

    return tuple(results)


def _optional_int(
    value: Any,
) -> int | None:
    if value is None:
        return None

    return int(value)


def _optional_float(
    value: Any,
) -> float | None:
    if value is None:
        return None

    return float(value)


def _optional_str(
    value: Any,
) -> str | None:
    if value is None:
        return None

    return str(value)

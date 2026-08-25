from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
GrowthFunction = Callable[[FloatArray], FloatArray]


@dataclass(frozen=True, slots=True)
class GrowthModelFit:
    model: str
    coefficient: float
    intercept: float
    r_squared: float
    normalized_rmse: float


@dataclass(frozen=True, slots=True)
class ComplexityEstimate:
    points: tuple[tuple[int, float], ...]
    fits: tuple[GrowthModelFit, ...]
    power_exponent: float | None

    @property
    def best_fit(self) -> GrowthModelFit:
        return self.fits[0]

    @property
    def best_model(self) -> str:
        return self.best_fit.model

    @property
    def model_separation(self) -> float:
        if len(self.fits) < 2:
            return float("inf")

        return self.fits[1].normalized_rmse - self.fits[0].normalized_rmse


def _constant(n: FloatArray) -> FloatArray:
    return np.ones_like(n)


def _logarithmic(n: FloatArray) -> FloatArray:
    return np.log2(n)


def _linear(n: FloatArray) -> FloatArray:
    return n


def _linearithmic(n: FloatArray) -> FloatArray:
    return n * np.log2(n)


def _quadratic(n: FloatArray) -> FloatArray:
    return n * n


def _cubic(n: FloatArray) -> FloatArray:
    return n * n * n


_GROWTH_MODELS: tuple[tuple[str, GrowthFunction], ...] = (
    ("1", _constant),
    ("log n", _logarithmic),
    ("n", _linear),
    ("n log n", _linearithmic),
    ("n^2", _quadratic),
    ("n^3", _cubic),
)


def estimate_growth(
    sizes: Sequence[int],
    costs: Sequence[float],
    *,
    tail_points: int | None = None,
) -> ComplexityEstimate:
    points = _aggregate_points(sizes, costs)

    if len(points) < 3:
        raise ValueError("at least three distinct input sizes are required")

    if tail_points is not None:
        if tail_points < 3:
            raise ValueError("tail_points must be at least 3")

        points = points[-tail_points:]

    n = np.asarray(
        [point[0] for point in points],
        dtype=np.float64,
    )
    cost = np.asarray(
        [point[1] for point in points],
        dtype=np.float64,
    )

    fits = tuple(
        sorted(
            (
                _fit_model(n, cost, model, function)
                for model, function in _GROWTH_MODELS
            ),
            key=lambda fit: fit.normalized_rmse,
        )
    )

    return ComplexityEstimate(
        points=points,
        fits=fits,
        power_exponent=_estimate_power_exponent(n, cost),
    )


def estimate_complexity_from_results(
    records: Iterable[object],
    *,
    algorithm: str,
    backend: str,
    family: str,
    metric: str,
    tail_points: int | None = None,
) -> ComplexityEstimate:
    materialized = tuple(_as_mapping(item) for item in records)

    if not materialized:
        raise ValueError("no result records were provided")

    successful = tuple(
        record for record in materialized if record.get("status", "ok") == "ok"
    )

    if not successful:
        raise ValueError("no successful result records were found")

    _validate_filter(
        successful,
        field="algorithm",
        requested=algorithm,
    )
    _validate_filter(
        successful,
        field="backend",
        requested=backend,
    )
    _validate_filter(
        successful,
        field="family",
        requested=family,
    )

    matching = tuple(
        record
        for record in successful
        if record.get("algorithm") == algorithm
        and record.get("backend") == backend
        and record.get("family") == family
    )

    available_metrics = sorted(
        {
            key
            for record in matching
            for key, value in record.items()
            if isinstance(value, (int, float))
            and key not in {"n", "seed", "repetition"}
        }
    )

    if metric not in available_metrics:
        raise ValueError(
            f"metric {metric!r} is not available for "
            f"algorithm={algorithm!r}, "
            f"backend={backend!r}, "
            f"family={family!r}; "
            f"available metrics: {available_metrics}"
        )

    sizes: list[int] = []
    costs: list[float] = []

    for record in matching:
        value = record.get(metric)

        if value is None:
            continue

        sizes.append(int(record["n"]))
        costs.append(float(value))

    if not sizes:
        raise ValueError(
            f"metric {metric!r} has no measurements for "
            f"algorithm={algorithm!r}, "
            f"backend={backend!r}, "
            f"family={family!r}"
        )

    return estimate_growth(
        sizes,
        costs,
        tail_points=tail_points,
    )


def _validate_filter(
    records: Sequence[Mapping[str, object]],
    *,
    field: str,
    requested: str,
) -> None:
    available = sorted(
        {str(record[field]) for record in records if record.get(field) is not None}
    )

    if requested not in available:
        raise ValueError(
            f"unknown {field} {requested!r}; " f"available values: {available}"
        )


def _aggregate_points(
    sizes: Sequence[int],
    costs: Sequence[float],
) -> tuple[tuple[int, float], ...]:
    if len(sizes) != len(costs):
        raise ValueError("sizes and costs must have the same length")

    buckets: dict[int, list[float]] = defaultdict(list)

    for n, cost in zip(sizes, costs, strict=True):
        n = int(n)
        cost = float(cost)

        if n <= 0:
            raise ValueError("input sizes must be positive")

        if not np.isfinite(cost):
            raise ValueError("costs must be finite")

        if cost < 0:
            raise ValueError("costs must be non-negative")

        buckets[n].append(cost)

    return tuple(
        (
            n,
            float(np.mean(buckets[n])),
        )
        for n in sorted(buckets)
    )


def _fit_model(
    n: FloatArray,
    cost: FloatArray,
    model: str,
    function: GrowthFunction,
) -> GrowthModelFit:
    x = function(n)

    if model == "1":
        coefficient = 0.0
        intercept = float(np.mean(cost))
        predicted = np.full_like(cost, intercept)
    else:
        design = np.column_stack((x, np.ones_like(x)))
        coefficient, intercept = np.linalg.lstsq(
            design,
            cost,
            rcond=None,
        )[0]
        predicted = coefficient * x + intercept

    residual = cost - predicted

    rmse = float(np.sqrt(np.mean(residual * residual)))

    span = float(np.ptp(cost))

    if np.isclose(span, 0.0):
        normalized_rmse = 0.0 if np.isclose(rmse, 0.0) else float("inf")
    else:
        normalized_rmse = rmse / span

    ss_residual = float(np.dot(residual, residual))

    centered = cost - np.mean(cost)
    ss_total = float(np.dot(centered, centered))

    if np.isclose(ss_total, 0.0):
        r_squared = 1.0 if np.isclose(ss_residual, 0.0) else 0.0
    else:
        r_squared = 1.0 - ss_residual / ss_total

    return GrowthModelFit(
        model=model,
        coefficient=float(coefficient),
        intercept=float(intercept),
        r_squared=float(r_squared),
        normalized_rmse=float(normalized_rmse),
    )


def _estimate_power_exponent(
    n: FloatArray,
    cost: FloatArray,
) -> float | None:
    positive = cost > 0.0

    if np.count_nonzero(positive) < 2:
        return None

    slope = np.polyfit(
        np.log(n[positive]),
        np.log(cost[positive]),
        1,
    )[0]

    return float(slope)


def _as_mapping(
    record: object,
) -> Mapping[str, object]:
    if isinstance(record, Mapping):
        return record

    to_dict = getattr(record, "to_dict", None)

    if callable(to_dict):
        value = to_dict()

        if isinstance(value, Mapping):
            return value

        raise TypeError("record.to_dict() must return a mapping")

    raise TypeError("records must be mappings or expose to_dict()")

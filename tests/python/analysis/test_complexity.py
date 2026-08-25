import numpy as np
import pytest

from tca.analysis import (
    estimate_complexity_from_results,
    estimate_growth,
)


def test_estimate_growth_identifies_linear_growth():
    sizes = [10, 100, 1_000, 10_000]
    costs = [3 * n + 7 for n in sizes]

    estimate = estimate_growth(sizes, costs)

    assert estimate.best_model == "n"
    assert estimate.best_fit.r_squared == pytest.approx(1.0)


def test_estimate_growth_identifies_n_log_n_growth():
    sizes = [10, 100, 1_000, 10_000, 100_000]
    costs = [n * np.log2(n) for n in sizes]

    estimate = estimate_growth(sizes, costs)

    assert estimate.best_model == "n log n"
    assert estimate.best_fit.r_squared == pytest.approx(1.0)


def test_estimate_growth_identifies_selection_quadratic_growth():
    sizes = [10, 20, 40, 80, 160]
    costs = [n * (n - 1) / 2 for n in sizes]

    estimate = estimate_growth(sizes, costs)

    assert estimate.best_model == "n^2"
    assert estimate.best_fit.r_squared > 0.999
    assert estimate.power_exponent == pytest.approx(
        2.0,
        abs=0.1,
    )


def test_estimate_growth_aggregates_repeated_sizes():
    sizes = [
        10,
        10,
        100,
        100,
        1_000,
        1_000,
    ]
    costs = [
        10,
        12,
        100,
        120,
        1_000,
        1_200,
    ]

    estimate = estimate_growth(sizes, costs)

    assert estimate.points == (
        (10, 11.0),
        (100, 110.0),
        (1_000, 1_100.0),
    )
    assert estimate.best_model == "n"


def test_estimate_growth_can_use_asymptotic_tail():
    sizes = [2, 4, 8, 16, 32, 64]
    costs = [
        100,
        120,
        64,
        256,
        1_024,
        4_096,
    ]

    estimate = estimate_growth(
        sizes,
        costs,
        tail_points=4,
    )

    assert estimate.points == (
        (8, 64.0),
        (16, 256.0),
        (32, 1_024.0),
        (64, 4_096.0),
    )
    assert estimate.best_model == "n^2"


def test_estimate_complexity_from_results_filters_and_aggregates():
    records = []

    for n in (10, 100, 1_000, 10_000):
        expected = n * np.log2(n)

        records.extend(
            [
                {
                    "algorithm": "merge",
                    "backend": "python",
                    "family": "uniform",
                    "n": n,
                    "status": "ok",
                    "comparisons": expected,
                },
                {
                    "algorithm": "merge",
                    "backend": "python",
                    "family": "uniform",
                    "n": n,
                    "status": "ok",
                    "comparisons": expected,
                },
                {
                    "algorithm": "selection",
                    "backend": "python",
                    "family": "uniform",
                    "n": n,
                    "status": "ok",
                    "comparisons": n * n,
                },
            ]
        )

    estimate = estimate_complexity_from_results(
        records,
        algorithm="merge",
        backend="python",
        family="uniform",
        metric="comparisons",
    )

    assert estimate.best_model == "n log n"


def test_estimate_complexity_ignores_failed_records():
    records = [
        {
            "algorithm": "selection",
            "backend": "python",
            "family": "uniform",
            "n": n,
            "status": "ok",
            "comparisons": n * n,
        }
        for n in (10, 100, 1_000)
    ]

    records.append(
        {
            "algorithm": "selection",
            "backend": "python",
            "family": "uniform",
            "n": 10_000,
            "status": "failed",
            "comparisons": 1.0,
        }
    )

    estimate = estimate_complexity_from_results(
        records,
        algorithm="selection",
        backend="python",
        family="uniform",
        metric="comparisons",
    )

    assert estimate.best_model == "n^2"
    assert len(estimate.points) == 3


def test_estimate_growth_requires_three_sizes():
    with pytest.raises(
        ValueError,
        match="at least three distinct input sizes",
    ):
        estimate_growth(
            [10, 100],
            [100, 10_000],
        )


def test_estimate_complexity_reports_available_filter_values():
    records = [
        {
            "algorithm": "merge",
            "backend": "python",
            "family": "uniform_random",
            "n": n,
            "status": "ok",
            "comparisons": n,
        }
        for n in (10, 100, 1_000)
    ]

    with pytest.raises(
        ValueError,
        match="unknown family 'uniform'",
    ):
        estimate_complexity_from_results(
            records,
            algorithm="merge",
            backend="python",
            family="uniform",
            metric="comparisons",
        )

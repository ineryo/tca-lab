from dataclasses import fields

import numpy as np
import pytest

from tca import _core
from tca.algorithms.sorting import (
    available_sorting_algorithms,
    sort,
)
from tca.core.instrumentation import Metrics

METHODS = available_sorting_algorithms()
NATIVE_METHODS = tuple(_core.available_sorting_algorithms())


def test_python_cpp_metrics_match():
    python_metrics = {field.name for field in fields(Metrics)}

    cpp_metrics = set(_core.available_metrics())

    assert python_metrics == cpp_metrics


def test_python_cpp_registries_match():
    python_methods = set(METHODS)
    cpp_methods = set(NATIVE_METHODS)

    assert cpp_methods - python_methods == {"radix_binary"}


def test_radix_binary_is_cpp_only():
    assert "radix_binary" in NATIVE_METHODS
    assert "radix_binary" not in METHODS


@pytest.mark.parametrize("method", NATIVE_METHODS)
def test_cpp_sort(method):
    values = np.array(
        [5, 2, 4, 8, 4, 2, 1],
        dtype=np.float64,
    )

    result = _core.sort(
        values,
        method,
    )

    assert result is None

    np.testing.assert_array_equal(
        values,
        np.array(
            [1, 2, 2, 4, 4, 5, 8],
            dtype=np.float64,
        ),
    )


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize(
    "backend",
    ["python", "cpp"],
)
@pytest.mark.parametrize(
    "size",
    [0, 1, 2, 10, 100],
)
def test_sort_random_inputs(
    method,
    backend,
    size,
):
    rng = np.random.default_rng(42)

    values = rng.integers(
        -100,
        101,
        size=size,
    ).astype(np.float64)

    expected = np.sort(values.copy())

    sort(
        values,
        method=method,
        backend=backend,
    )

    np.testing.assert_array_equal(
        values,
        expected,
    )


@pytest.mark.parametrize("method", METHODS)
def test_sort_metrics_python_cpp_equivalence(
    method,
):
    original = np.array(
        [5, 2, 4, 8, 4, 2, 1],
        dtype=np.float64,
    )

    python_values = original.copy()
    cpp_values = original.copy()

    python_metrics = Metrics()
    cpp_metrics = Metrics()

    sort(
        python_values,
        method=method,
        backend="python",
        metrics=python_metrics,
    )

    sort(
        cpp_values,
        method=method,
        backend="cpp",
        metrics=cpp_metrics,
    )

    np.testing.assert_array_equal(
        python_values,
        cpp_values,
    )

    assert python_metrics == cpp_metrics


@pytest.mark.parametrize("backend", ["python", "cpp"])
@pytest.mark.parametrize(
    ("profile", "pivot", "recursion"),
    [
        ("quick_classic", "first", "classic"),
        ("quick_smarter", "random", "bounded"),
    ],
)
def test_quick_profiles_use_the_expected_strategy(
    backend,
    profile,
    pivot,
    recursion,
):
    values = np.array(
        [9, 1, 8, 2, 7, 3, 6, 4, 5],
        dtype=np.float64,
    )

    profile_values = values.copy()
    expected_values = values.copy()
    profile_metrics = Metrics()
    expected_metrics = Metrics()

    sort(
        profile_values,
        method=profile,
        backend=backend,
        metrics=profile_metrics,
    )

    if backend == "python":
        from tca.reference.sorting.quick_sort import quick_sort

        quick_sort(
            expected_values,
            metrics=expected_metrics,
            pivot=pivot,
            recursion=recursion,
        )
    else:
        _core.quick_sort(
            expected_values,
            pivot=pivot,
            recursion=recursion,
            metrics=expected_metrics,
        )

    np.testing.assert_array_equal(profile_values, expected_values)
    assert profile_metrics == expected_metrics


@pytest.mark.parametrize(
    "values",
    [
        [12.0, 15.0, 18.0, 92.0],
        [12.0, 15.0, 18.3, 92.14],
        [-92.0, 12.0],
        [120.0, 150.0, 910.0],
    ],
)
def test_radix_effective_digits_python_cpp_metrics_parity(values):
    values_python = np.array(values, dtype=np.float64)
    values_cpp = values_python.copy()

    metrics_python = Metrics()
    metrics_cpp = Metrics()

    sort(
        values_python,
        method="radix",
        backend="python",
        metrics=metrics_python,
    )

    sort(
        values_cpp,
        method="radix",
        backend="cpp",
        metrics=metrics_cpp,
    )

    np.testing.assert_array_equal(
        values_python,
        values_cpp,
    )

    assert metrics_python.comparisons == metrics_cpp.comparisons
    assert metrics_python.swaps == metrics_cpp.swaps
    assert metrics_python.writes == metrics_cpp.writes

import numpy as np
import pytest
import tca._core as cpp

from tca.core.instrumentation import Metrics
from tca.core.quantization import decimal_key
from tca.reference.sorting.radix_sort import radix_sort


def test_radix_sort_decimal_truncation():
    values = [5.1342, 5.1346, 5.1344, 3.2, 5.1]

    radix_sort(values, digits=3)

    assert values == [3.2, 5.1, 5.1342, 5.1346, 5.1344]


def test_radix_sort_preserves_order_for_equal_keys():
    values = [5.1342, 5.1346, 5.1344]

    radix_sort(values, digits=3)

    assert values == [5.1342, 5.1346, 5.1344]


@pytest.mark.parametrize(
    "digits",
    [0, 1, 2, 3, 6],
)
def test_radix_sort_python_cpp_parity(digits):
    values = [
        5.1342,
        -3.2,
        5.1346,
        0.0,
        -5.1342,
        5.1,
        -5.1346,
        2.25,
        5.1344,
    ]

    python_values = values.copy()
    cpp_values = np.array(values, dtype=np.float64)

    radix_sort(python_values, digits=digits)
    cpp.radix_sort(cpp_values, digits=digits)

    assert python_values == cpp_values.tolist()


@pytest.mark.parametrize(
    "digits",
    [0, 1, 2, 3, 6],
)
def test_radix_sort_orders_decimal_keys(digits):
    values = [
        5.1342,
        -3.2,
        5.1346,
        0.0,
        -5.1342,
        5.1,
        -5.1346,
        2.25,
        5.1344,
    ]

    radix_sort(values, digits=digits)

    keys = [decimal_key(value, digits) for value in values]

    assert keys == sorted(keys)


@pytest.mark.parametrize(
    "digits",
    [0, 1, 2, 3, 6],
)
def test_radix_sort_metrics_python_cpp_parity(digits):
    values = [5.1342, -3.2, 5.1346, 0.0, -5.1342, 5.1, 2.25]

    python_values = values.copy()
    cpp_values = np.array(values, dtype=np.float64)

    python_metrics = Metrics()
    cpp_metrics = Metrics()

    radix_sort(python_values, metrics=python_metrics, digits=digits)
    cpp.radix_sort(cpp_values, digits=digits, metrics=cpp_metrics)

    assert python_metrics == cpp_metrics
    assert python_metrics.comparisons == 0
    assert python_metrics.swaps == 0


@pytest.mark.parametrize(
    "digits",
    [-1, 16],
)
def test_python_radix_sort_rejects_invalid_digits(digits):
    with pytest.raises(ValueError, match="digits must be between"):
        radix_sort([3.0, 2.0, 1.0], digits=digits)


@pytest.mark.parametrize(
    "digits",
    [-1, 16],
)
def test_cpp_radix_sort_rejects_invalid_digits(digits):
    values = np.array([3.0, 2.0, 1.0], dtype=np.float64)

    with pytest.raises(ValueError, match="digits must be between"):
        cpp.radix_sort(values, digits=digits)

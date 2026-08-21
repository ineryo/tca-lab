import math

import pytest
import tca._core as cpp

from tca.core.quantization import decimal_key


@pytest.mark.parametrize(
    ("value", "digits", "expected"),
    [
        (5.1342, 3, 5134),
        (5.1346, 3, 5134),
        (5.1344, 3, 5134),
        (3.2, 3, 3200),
        (5.1, 3, 5100),
        (-5.1346, 3, -5134),
        (-1.9999, 3, -1999),
        (1.9999, 3, 1999),
        (5.9999, 0, 5),
        (-5.9999, 0, -5),
    ],
)
def test_decimal_key_reference_values(value, digits, expected):
    assert decimal_key(value, digits) == expected
    assert cpp.decimal_key(value, digits) == expected


@pytest.mark.parametrize(
    "digits",
    [0, 1, 2, 3, 6, 10, 15],
)
def test_decimal_key_python_cpp_parity(digits):
    values = [
        -123.456789,
        -5.1346,
        -1.9999,
        -0.0019,
        0.0,
        0.0019,
        1.9999,
        5.1346,
        123.456789,
    ]

    python_keys = [decimal_key(value, digits) for value in values]
    cpp_keys = [cpp.decimal_key(value, digits) for value in values]

    assert python_keys == cpp_keys


@pytest.mark.parametrize(
    "value",
    [math.inf, -math.inf, math.nan],
)
def test_python_decimal_key_rejects_non_finite_values(value):
    with pytest.raises(ValueError, match="value must be finite"):
        decimal_key(value)


@pytest.mark.parametrize(
    "value",
    [math.inf, -math.inf, math.nan],
)
def test_cpp_decimal_key_rejects_non_finite_values(value):
    with pytest.raises(ValueError, match="value must be finite"):
        cpp.decimal_key(value)


@pytest.mark.parametrize(
    "digits",
    [-1, 16],
)
def test_python_decimal_key_rejects_invalid_digits(digits):
    with pytest.raises(ValueError, match="digits must be between"):
        decimal_key(1.0, digits)


@pytest.mark.parametrize(
    "digits",
    [-1, 16],
)
def test_cpp_decimal_key_rejects_invalid_digits(digits):
    with pytest.raises(ValueError, match="digits must be between"):
        cpp.decimal_key(1.0, digits)

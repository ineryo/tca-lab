import numpy as np
import pytest
import tca._core as cpp


def test_radix_binary_argsort_orders_values():
    values = np.array(
        [40.0, 10.0, 30.0, 20.0],
        dtype=np.float64,
    )

    order = cpp.radix_binary_argsort(values)

    np.testing.assert_array_equal(
        order,
        np.array([1, 3, 2, 0]),
    )


def test_radix_binary_argsort_does_not_modify_values():
    values = np.array(
        [3.0, 1.0, 2.0],
        dtype=np.float64,
    )
    original = values.copy()

    cpp.radix_binary_argsort(values)

    np.testing.assert_array_equal(values, original)


def test_radix_binary_argsort_handles_negative_values():
    values = np.array(
        [3.0, -5.0, 0.0, -1.0, 2.0],
        dtype=np.float64,
    )

    order = cpp.radix_binary_argsort(values)

    np.testing.assert_array_equal(
        values[order],
        np.array([-5.0, -1.0, 0.0, 2.0, 3.0]),
    )


def test_radix_binary_argsort_is_stable():
    values = np.array(
        [3.0, 1.0, 3.0, 1.0, 3.0],
        dtype=np.float64,
    )

    order = cpp.radix_binary_argsort(values)

    np.testing.assert_array_equal(
        order,
        np.array([1, 3, 0, 2, 4]),
    )


@pytest.mark.parametrize(
    "values",
    [
        [],
        [1.0],
        [1.0, 2.0],
        [2.0, 1.0],
        [1.0, 1.0],
    ],
)
def test_radix_binary_argsort_small_inputs(values):
    array = np.array(values, dtype=np.float64)

    order = cpp.radix_binary_argsort(array)

    np.testing.assert_array_equal(
        array[order],
        np.sort(array, kind="stable"),
    )


def test_radix_binary_argsort_rejects_nan():
    values = np.array(
        [1.0, np.nan, 2.0],
        dtype=np.float64,
    )

    with pytest.raises(ValueError, match="does not support NaN"):
        cpp.radix_binary_argsort(values)

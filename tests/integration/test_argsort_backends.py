import numpy as np
import pytest

from tca import _core


@pytest.mark.parametrize(
    "method",
    ["insertion_argsort", "merge_argsort", "radix_binary_argsort"],
)
def test_native_argsort_returns_stable_permutation(method):
    values = np.array([5.0, -2.0, 5.0, 0.0, -2.0, 3.0], dtype=np.float64)
    original = values.copy()

    order = getattr(_core, method)(values)

    np.testing.assert_array_equal(order, np.argsort(values, kind="stable"))
    np.testing.assert_array_equal(values, original)


@pytest.mark.parametrize(
    "method",
    ["insertion_argsort", "merge_argsort", "radix_binary_argsort"],
)
def test_native_argsort_handles_empty_and_singleton(method):
    function = getattr(_core, method)

    for values in (
        np.array([], dtype=np.float64),
        np.array([7.0], dtype=np.float64),
    ):
        np.testing.assert_array_equal(
            function(values),
            np.arange(values.size, dtype=np.uintp),
        )


def test_radix_binary_argsort_rejects_nan():
    values = np.array([1.0, np.nan, 2.0], dtype=np.float64)

    with pytest.raises(ValueError, match="does not support NaN"):
        _core.radix_binary_argsort(values)

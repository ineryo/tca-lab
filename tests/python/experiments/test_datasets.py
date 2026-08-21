import numpy as np
import pytest

from tca.core.prng import PRNG
from tca.experiments import (
    DATA_FAMILIES,
    available_data_families,
    generate_sorting_data,
)


@pytest.mark.parametrize(
    "family",
    DATA_FAMILIES,
)
def test_generate_sorting_data_shape_and_dtype(family):
    values = generate_sorting_data(
        100,
        family,
        seed=42,
    )

    assert values.shape == (100,)
    assert values.dtype == np.float64


@pytest.mark.parametrize(
    "family",
    DATA_FAMILIES,
)
def test_generate_sorting_data_is_reproducible(family):
    first = generate_sorting_data(
        100,
        family,
        seed=42,
    )

    second = generate_sorting_data(
        100,
        family,
        seed=42,
    )

    np.testing.assert_array_equal(
        first,
        second,
    )


def test_available_data_families_matches_catalog():
    assert available_data_families() == DATA_FAMILIES


def test_uniform_random_uses_project_prng():
    n = 10
    low_key = -1_000_000_000
    key_span = 2_000_000_000
    scale = 1000

    prng = PRNG(42)

    expected = np.array(
        [(low_key + prng.randbelow(key_span)) / scale for _ in range(n)],
        dtype=np.float64,
    )

    result = generate_sorting_data(
        n,
        "uniform_random",
        seed=42,
    )

    np.testing.assert_array_equal(
        result,
        expected,
    )


def test_uniform_random_changes_with_seed():
    first = generate_sorting_data(
        100,
        "uniform_random",
        seed=42,
    )

    second = generate_sorting_data(
        100,
        "uniform_random",
        seed=43,
    )

    assert not np.array_equal(
        first,
        second,
    )


def test_sorted_is_sorted():
    values = generate_sorting_data(
        100,
        "sorted",
        seed=42,
    )

    assert np.all(values[:-1] <= values[1:])


def test_sorted_uses_same_base_values_as_uniform_random():
    random_values = generate_sorting_data(
        100,
        "uniform_random",
        seed=42,
    )

    sorted_values = generate_sorting_data(
        100,
        "sorted",
        seed=42,
    )

    np.testing.assert_array_equal(
        sorted_values,
        np.sort(random_values),
    )


def test_reverse_sorted_is_reverse_sorted():
    values = generate_sorting_data(
        100,
        "reverse_sorted",
        seed=42,
    )

    assert np.all(values[:-1] >= values[1:])


def test_reverse_sorted_uses_same_base_values_as_uniform_random():
    random_values = generate_sorting_data(
        100,
        "uniform_random",
        seed=42,
    )

    reverse_values = generate_sorting_data(
        100,
        "reverse_sorted",
        seed=42,
    )

    np.testing.assert_array_equal(
        reverse_values,
        np.sort(random_values)[::-1],
    )


def test_nearly_sorted_preserves_values_but_changes_order():
    sorted_values = generate_sorting_data(
        100,
        "sorted",
        seed=42,
    )

    nearly_sorted_values = generate_sorting_data(
        100,
        "nearly_sorted",
        seed=42,
    )

    np.testing.assert_array_equal(
        np.sort(nearly_sorted_values),
        sorted_values,
    )

    assert not np.array_equal(
        nearly_sorted_values,
        sorted_values,
    )


def test_nearly_reverse_sorted_preserves_values_but_changes_order():
    reverse_values = generate_sorting_data(
        100,
        "reverse_sorted",
        seed=42,
    )

    nearly_reverse_values = generate_sorting_data(
        100,
        "nearly_reverse_sorted",
        seed=42,
    )

    np.testing.assert_array_equal(
        np.sort(nearly_reverse_values)[::-1],
        reverse_values,
    )

    assert not np.array_equal(
        nearly_reverse_values,
        reverse_values,
    )


def test_many_repeated_has_sqrt_n_distinct_values():
    n = 10_000

    values = generate_sorting_data(
        n,
        "many_repeated",
        seed=42,
    )

    assert np.unique(values).size == int(np.sqrt(n))


def test_all_equal_has_one_distinct_value():
    values = generate_sorting_data(
        100,
        "all_equal",
        seed=42,
    )

    assert np.unique(values).size == 1


@pytest.mark.parametrize(
    "family",
    DATA_FAMILIES,
)
def test_generate_sorting_data_accepts_empty_array(family):
    values = generate_sorting_data(
        0,
        family,
        seed=42,
    )

    assert values.shape == (0,)
    assert values.dtype == np.float64


def test_generate_sorting_data_rejects_negative_n():
    with pytest.raises(
        ValueError,
        match="n must be non-negative",
    ):
        generate_sorting_data(
            -1,
            "uniform_random",
            seed=42,
        )


def test_generate_sorting_data_rejects_unknown_family():
    with pytest.raises(
        ValueError,
        match="unknown data family",
    ):
        generate_sorting_data(
            10,
            "unknown",
            seed=42,
        )


@pytest.mark.parametrize(
    "seed",
    [-1, 1 << 64],
)
def test_generate_sorting_data_rejects_seed_outside_uint64(
    seed,
):
    with pytest.raises(
        ValueError,
        match="seed must fit in uint64",
    ):
        generate_sorting_data(
            10,
            "uniform_random",
            seed=seed,
        )


@pytest.mark.parametrize(
    "fraction",
    [-0.1, 1.1],
)
def test_generate_sorting_data_rejects_invalid_nearly_fraction(
    fraction,
):
    with pytest.raises(
        ValueError,
        match="nearly_swaps_fraction",
    ):
        generate_sorting_data(
            10,
            "nearly_sorted",
            seed=42,
            nearly_swaps_fraction=fraction,
        )


@pytest.mark.parametrize(
    "digits",
    [-1, 16],
)
def test_generate_sorting_data_rejects_invalid_digits(
    digits,
):
    with pytest.raises(
        ValueError,
        match="digits must be between",
    ):
        generate_sorting_data(
            10,
            "uniform_random",
            seed=42,
            digits=digits,
        )

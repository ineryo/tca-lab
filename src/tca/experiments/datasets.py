from dataclasses import dataclass

import numpy as np

from tca.core.prng import MASK_64, PRNG
from tca.core.quantization import MAX_DECIMAL_DIGITS, decimal_key

DATA_FAMILIES = (
    "uniform_random",
    "sorted",
    "reverse_sorted",
    "nearly_sorted",
    "nearly_reverse_sorted",
    "many_repeated",
    "all_equal",
)

DEFAULT_LOW = -1_000_000.0
DEFAULT_HIGH = 1_000_000.0
DEFAULT_DIGITS = 3
DEFAULT_NEARLY_SWAPS_FRACTION = 0.05
DEFAULT_SIZES = tuple(10**k for k in range(7))
DEFAULT_REPETITIONS = 5
DEFAULT_BASE_SEED = 42


@dataclass(frozen=True, slots=True)
class SortingCase:
    n: int
    family: str
    repetition: int
    seed: int


def available_data_families() -> tuple[str, ...]:
    return DATA_FAMILIES


def sorting_case_catalog(
    *,
    sizes: tuple[int, ...] = DEFAULT_SIZES,
    families: tuple[str, ...] = DATA_FAMILIES,
    repetitions: int = DEFAULT_REPETITIONS,
    base_seed: int = DEFAULT_BASE_SEED,
) -> tuple[SortingCase, ...]:
    if repetitions <= 0:
        raise ValueError("repetitions must be greater than zero")

    if not 0 <= base_seed <= MASK_64:
        raise ValueError("base_seed must fit in uint64")

    if any(n < 0 for n in sizes):
        raise ValueError("sizes must be non-negative")

    unknown_families = tuple(
        family for family in families if family not in DATA_FAMILIES
    )

    if unknown_families:
        raise ValueError(f"unknown data families: {unknown_families}")

    n_seed_groups = len(sizes) * repetitions

    if n_seed_groups and base_seed + n_seed_groups - 1 > MASK_64:
        raise ValueError("generated seeds must fit in uint64")

    cases: list[SortingCase] = []

    for size_index, n in enumerate(sizes):
        for repetition in range(repetitions):
            seed = base_seed + size_index * repetitions + repetition

            for family in families:
                cases.append(
                    SortingCase(
                        n=n,
                        family=family,
                        repetition=repetition,
                        seed=seed,
                    )
                )

    return tuple(cases)


def generate_sorting_data(
    n: int,
    family: str,
    *,
    seed: int,
    low: float = DEFAULT_LOW,
    high: float = DEFAULT_HIGH,
    digits: int = DEFAULT_DIGITS,
    nearly_swaps_fraction: float = DEFAULT_NEARLY_SWAPS_FRACTION,
) -> np.ndarray:
    _validate_arguments(
        n=n,
        family=family,
        seed=seed,
        low=low,
        high=high,
        digits=digits,
        nearly_swaps_fraction=nearly_swaps_fraction,
    )

    scale = 10**digits

    low_key = decimal_key(
        low,
        digits,
    )

    high_key = decimal_key(
        high,
        digits,
    )

    key_span = high_key - low_key

    if key_span <= 0:
        raise ValueError("quantized interval must contain at least one value")

    if key_span > (1 << 64):
        raise ValueError("quantized interval must fit in uint64")

    prng = PRNG(seed)

    if family == "many_repeated":
        return _many_repeated(
            n=n,
            prng=prng,
            low_key=low_key,
            key_span=key_span,
            scale=scale,
        )

    values = _uniform_values(
        n=n,
        prng=prng,
        low_key=low_key,
        key_span=key_span,
        scale=scale,
    )

    if family == "uniform_random":
        return values

    if family == "sorted":
        return np.sort(values)

    if family == "reverse_sorted":
        return np.sort(values)[::-1].copy()

    if family == "nearly_sorted":
        values = np.sort(values)

        return _perturb_adjacent(
            values,
            prng,
            nearly_swaps_fraction,
        )

    if family == "nearly_reverse_sorted":
        values = np.sort(values)[::-1].copy()

        return _perturb_adjacent(
            values,
            prng,
            nearly_swaps_fraction,
        )

    if family == "all_equal":
        if n == 0:
            return values

        return np.full(
            n,
            values[0],
            dtype=np.float64,
        )

    raise RuntimeError(f"unhandled data family: {family}")


def _uniform_values(
    *,
    n: int,
    prng: PRNG,
    low_key: int,
    key_span: int,
    scale: int,
) -> np.ndarray:
    values = np.empty(
        n,
        dtype=np.float64,
    )

    for index in range(n):
        key = low_key + prng.randbelow(key_span)

        values[index] = key / scale

    return values


def _perturb_adjacent(
    values: np.ndarray,
    prng: PRNG,
    fraction: float,
) -> np.ndarray:
    if len(values) < 2 or fraction == 0.0:
        return values

    n_swaps = max(
        1,
        int(round(len(values) * fraction)),
    )

    n_swaps = min(
        n_swaps,
        len(values) - 1,
    )

    selected_indices: list[int] = []
    selected_set: set[int] = set()

    while len(selected_indices) < n_swaps:
        index = prng.randbelow(len(values) - 1)

        if index in selected_set:
            continue

        selected_indices.append(index)
        selected_set.add(index)

    for index in selected_indices:
        values[index], values[index + 1] = (
            values[index + 1],
            values[index],
        )

    return values


def _many_repeated(
    *,
    n: int,
    prng: PRNG,
    low_key: int,
    key_span: int,
    scale: int,
) -> np.ndarray:
    if n == 0:
        return np.empty(
            0,
            dtype=np.float64,
        )

    n_distinct = max(
        2,
        int(np.sqrt(n)),
    )

    n_distinct = min(
        n_distinct,
        n,
        key_span,
    )

    pool_keys: list[int] = []
    pool_set: set[int] = set()

    while len(pool_keys) < n_distinct:
        key = low_key + prng.randbelow(key_span)

        if key in pool_set:
            continue

        pool_keys.append(key)
        pool_set.add(key)

    values = np.empty(
        n,
        dtype=np.float64,
    )

    for index, key in enumerate(pool_keys):
        values[index] = key / scale

    for index in range(n_distinct, n):
        pool_index = prng.randbelow(n_distinct)

        values[index] = pool_keys[pool_index] / scale

    _shuffle(
        values,
        prng,
    )

    return values


def _shuffle(
    values: np.ndarray,
    prng: PRNG,
) -> None:
    for index_i in range(
        len(values) - 1,
        0,
        -1,
    ):
        index_j = prng.randbelow(index_i + 1)

        values[index_i], values[index_j] = (
            values[index_j],
            values[index_i],
        )


def _validate_arguments(
    *,
    n: int,
    family: str,
    seed: int,
    low: float,
    high: float,
    digits: int,
    nearly_swaps_fraction: float,
) -> None:
    if n < 0:
        raise ValueError("n must be non-negative")

    if family not in DATA_FAMILIES:
        raise ValueError(
            f"unknown data family {family!r}; " f"available families: {DATA_FAMILIES}"
        )

    if not 0 <= seed <= MASK_64:
        raise ValueError("seed must fit in uint64")

    if low >= high:
        raise ValueError("low must be smaller than high")

    if not 0 <= digits <= MAX_DECIMAL_DIGITS:
        raise ValueError(f"digits must be between 0 and " f"{MAX_DECIMAL_DIGITS}")

    if not 0.0 <= nearly_swaps_fraction <= 1.0:
        raise ValueError("nearly_swaps_fraction must be " "between 0 and 1")

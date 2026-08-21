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


def available_data_families() -> tuple[str, ...]:
    return DATA_FAMILIES


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

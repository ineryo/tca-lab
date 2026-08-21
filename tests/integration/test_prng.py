import pytest
import tca._core as cpp

from tca.core.prng import PRNG

EXPECTED_SEED_ZERO = [
    0xE220A8397B1DCDAF,
    0x6E789E6AA1B965F4,
    0x06C45D188009454F,
    0xF88BB8A8724C81EC,
    0x1B39896A51A8749B,
]


def test_python_prng_reference_sequence():
    prng = PRNG(0)

    result = [prng.next_uint64() for _ in range(5)]

    assert result == EXPECTED_SEED_ZERO


def test_cpp_prng_reference_sequence():
    prng = cpp.PRNG(0)

    result = [prng.next_uint64() for _ in range(5)]

    assert result == EXPECTED_SEED_ZERO


@pytest.mark.parametrize(
    "seed",
    [0, 1, 42, 123456789],
)
def test_prng_python_cpp_uint64_parity(seed):
    python_prng = PRNG(seed)
    cpp_prng = cpp.PRNG(seed)

    python_values = [python_prng.next_uint64() for _ in range(100)]
    cpp_values = [cpp_prng.next_uint64() for _ in range(100)]

    assert python_values == cpp_values


@pytest.mark.parametrize(
    "upper_bound",
    [1, 2, 3, 10, 100, 1000],
)
def test_prng_python_cpp_randbelow_parity(upper_bound):
    python_prng = PRNG(42)
    cpp_prng = cpp.PRNG(42)

    python_values = [python_prng.randbelow(upper_bound) for _ in range(100)]
    cpp_values = [cpp_prng.randbelow(upper_bound) for _ in range(100)]

    assert python_values == cpp_values


def test_python_prng_rejects_invalid_upper_bound():
    prng = PRNG()

    with pytest.raises(ValueError):
        prng.randbelow(0)


def test_cpp_prng_rejects_invalid_upper_bound():
    prng = cpp.PRNG()

    with pytest.raises(ValueError):
        prng.randbelow(0)

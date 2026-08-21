import math

MAX_DECIMAL_DIGITS = 15
INT64_MIN = -(1 << 63)
INT64_MAX_EXCLUSIVE = 1 << 63


def decimal_key(value, digits: int = 3) -> int:
    if not isinstance(digits, int):
        raise TypeError("digits must be an integer")

    if not 0 <= digits <= MAX_DECIMAL_DIGITS:
        raise ValueError(f"digits must be between 0 and {MAX_DECIMAL_DIGITS}")

    value = float(value)

    if not math.isfinite(value):
        raise ValueError("value must be finite")

    scale = 1.0

    for _ in range(digits):
        scale *= 10.0

    scaled = value * scale

    if scaled < INT64_MIN or scaled >= INT64_MAX_EXCLUSIVE:
        raise OverflowError("quantized value does not fit in int64")

    return math.trunc(scaled)

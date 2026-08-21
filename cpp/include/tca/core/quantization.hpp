#pragma once

#include <cmath>
#include <cstdint>
#include <stdexcept>

namespace tca {

inline constexpr int MAX_DECIMAL_DIGITS = 15;

inline std::int64_t decimal_key(double value, int digits = 3) {
    if (digits < 0 || digits > MAX_DECIMAL_DIGITS) {
        throw std::invalid_argument("digits must be between 0 and 15");
    }

    if (!std::isfinite(value)) {
        throw std::invalid_argument("value must be finite");
    }

    double scale = 1.0;

    for (int index = 0; index < digits; ++index) {
        scale *= 10.0;
    }

    const double scaled = value * scale;

    constexpr double int64_min = -9223372036854775808.0;
    constexpr double int64_max_exclusive = 9223372036854775808.0;

    if (scaled < int64_min || scaled >= int64_max_exclusive) {
        throw std::overflow_error("quantized value does not fit in int64");
    }

    return static_cast<std::int64_t>(std::trunc(scaled));
}

} // namespace tca
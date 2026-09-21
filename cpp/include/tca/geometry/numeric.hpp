#pragma once

#include <cmath>

namespace tca::geometry {

// Practical comparison policy for double; this is not an exact-real model.
inline constexpr double DEFAULT_TOLERANCE = 1e-12;

inline bool is_zero(double value, double tolerance = DEFAULT_TOLERANCE) {
    return std::abs(value) <= tolerance;
}

inline bool almost_equal(double left, double right,
                         double tolerance = DEFAULT_TOLERANCE) {
    return is_zero(left - right, tolerance);
}

inline int sign(double value, double tolerance = DEFAULT_TOLERANCE) {
    if (is_zero(value, tolerance)) {
        return 0;
    }

    return value < 0.0 ? -1 : 1;
}

} // namespace tca::geometry

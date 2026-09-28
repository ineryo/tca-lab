#pragma once

#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

/**
 * Sorts values in place using an IEEE-754 monotonic binary key.
 * For spans of two or more values, rejects NaN input values.
 * @throws std::invalid_argument when a span of two or more values contains NaN.
 */
void radix_binary_sort(std::span<double> values);

void radix_binary_sort(std::span<double> values,
                       tca::instrumentation::Metrics& metrics);

} // namespace tca::algorithms
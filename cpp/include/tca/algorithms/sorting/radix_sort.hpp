#pragma once

#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

/** Sorts finite values in place using three decimal quantization digits. */
void radix_sort(std::span<double> values);

void radix_sort(std::span<double> values, tca::instrumentation::Metrics& metrics);

/**
 * Sorts values in place by their truncated decimal keys at @p digits.
 * For spans of two or more values, rejects non-finite values.
 * @throws std::invalid_argument for invalid precision or a non-finite value
 *         in a span of two or more values.
 */
void radix_sort(std::span<double> values, int digits);

void radix_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                int digits);

} // namespace tca::algorithms
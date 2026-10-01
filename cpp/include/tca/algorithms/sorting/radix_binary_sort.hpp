#pragma once

#include <cstddef>
#include <span>
#include <vector>

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

/**
 * Returns the stable permutation of indices that orders values according to
 * the same IEEE-754 monotonic key used by radix_binary_sort.
 * The input values are not modified.
 * @throws std::invalid_argument when a span of two or more values contains NaN.
 */
std::vector<std::size_t> radix_binary_argsort(std::span<const double> values);

} // namespace tca::algorithms
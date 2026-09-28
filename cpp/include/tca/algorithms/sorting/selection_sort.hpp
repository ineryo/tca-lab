#pragma once

#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

/** Sorts @p values in place by repeatedly selecting the smallest remainder. */
void selection_sort(std::span<double> values);

void selection_sort(std::span<double> values, tca::instrumentation::Metrics& metrics);

} // namespace tca::algorithms
#pragma once

#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

void insertion_sort(std::span<double> values);

void insertion_sort(std::span<double> values, tca::instrumentation::Metrics& metrics);

} // namespace tca::algorithms
#pragma once

#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

void radix_sort(std::span<double> values);

void radix_sort(std::span<double> values, tca::instrumentation::Metrics& metrics);

void radix_sort(std::span<double> values, int digits);

void radix_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                int digits);

} // namespace tca::algorithms
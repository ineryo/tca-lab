#pragma once

#include <span>
#include <string_view>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

/** Sorts @p values in place using the registered @p method. */
void sort(std::span<double> values, std::string_view method);

/** Sorts @p values in place and accumulates semantic operations in @p metrics. */
void sort(std::span<double> values, std::string_view method,
          tca::instrumentation::Metrics& metrics);

/** Returns whether @p method is a currently registered native sorting algorithm. */
[[nodiscard]]
bool has_sorting_algorithm(std::string_view method) noexcept;

/** Returns the registered native sorting method names. */
[[nodiscard]]
std::span<const std::string_view> available_sorting_algorithms() noexcept;

} // namespace tca::algorithms
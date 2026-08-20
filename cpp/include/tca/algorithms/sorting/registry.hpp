#pragma once

#include <span>
#include <string_view>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

void sort(std::span<double> values, std::string_view method);

void sort(std::span<double> values, std::string_view method,
          tca::instrumentation::Metrics& metrics);

[[nodiscard]]
bool has_sorting_algorithm(std::string_view method) noexcept;

[[nodiscard]]
std::span<const std::string_view> available_sorting_algorithms() noexcept;

} // namespace tca::algorithms
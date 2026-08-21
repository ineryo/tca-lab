#pragma once

#include <cstdint>
#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

enum class QuickPivot {
    First,
    Quarter,
    Random,
};

enum class QuickRecursion {
    Classic,
    Bounded,
};

struct QuickSortOptions {
    QuickPivot pivot = QuickPivot::First;
    QuickRecursion recursion = QuickRecursion::Bounded;
    std::uint64_t seed = 0;
};

void quick_sort(std::span<double> values);

void quick_sort(std::span<double> values, tca::instrumentation::Metrics& metrics);

void quick_sort(std::span<double> values, const QuickSortOptions& options);

void quick_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                const QuickSortOptions& options);

} // namespace tca::algorithms
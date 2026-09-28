#pragma once

#include <cstdint>
#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

/** Pivot-selection strategy for quick sort. */
enum class QuickPivot {
    First,
    Quarter,
    Random,
};

/** Recursion strategy for quick sort; Bounded limits recursive depth. */
enum class QuickRecursion {
    Classic,
    Bounded,
};

/** Pivot, recursion, and deterministic random-seed options for quick sort. */
struct QuickSortOptions {
    QuickPivot pivot = QuickPivot::First;
    QuickRecursion recursion = QuickRecursion::Bounded;
    std::uint64_t seed = 0;
};

/** Sorts @p values in place with the default quick-sort options. */
void quick_sort(std::span<double> values);

/** Sorts @p values in place and records operations in @p metrics. */
void quick_sort(std::span<double> values, tca::instrumentation::Metrics& metrics);

void quick_sort(std::span<double> values, const QuickSortOptions& options);

void quick_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                const QuickSortOptions& options);

} // namespace tca::algorithms
#pragma once

#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

/** Storage strategy for merge-sort temporary values. */
enum class MergeBuffer {
    Local,
    Reused,
};

/** Options that select the merge-sort temporary-buffer strategy. */
struct MergeSortOptions {
    MergeBuffer buffer = MergeBuffer::Reused;
};

/** Sorts @p values in place with the default reused-buffer strategy. */
void merge_sort(std::span<double> values);

/** Sorts @p values in place and records operations in @p metrics. */
void merge_sort(std::span<double> values, tca::instrumentation::Metrics& metrics);

/** Sorts @p values in place according to @p options. */
void merge_sort(std::span<double> values, const MergeSortOptions& options);

void merge_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                const MergeSortOptions& options);

} // namespace tca::algorithms
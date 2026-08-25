#pragma once

#include <span>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::algorithms {

enum class MergeBuffer {
    Local,
    Reused,
};

struct MergeSortOptions {
    MergeBuffer buffer = MergeBuffer::Reused;
};

void merge_sort(std::span<double> values);

void merge_sort(std::span<double> values, tca::instrumentation::Metrics& metrics);

void merge_sort(std::span<double> values, const MergeSortOptions& options);

void merge_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                const MergeSortOptions& options);

} // namespace tca::algorithms
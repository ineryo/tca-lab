#include "tca/algorithms/sorting/selection_sort.hpp"

#include <utility>

#include "tca/core/instrumentation/direct_probe.hpp"
#include "tca/core/instrumentation/probe.hpp"

namespace {

// snippet:start selection-sort
template <typename ProbeType>
void selection_sort_impl(std::span<double> values, ProbeType& probe) {
    for (std::size_t index_i = 0; index_i < values.size(); ++index_i) { // i=(0)..(n-1)
        std::size_t marker = index_i;                                   // m=i

        for (std::size_t index_j = index_i + 1; index_j < values.size();
             ++index_j) {                                    // j=(i+1)..(n)
            if (probe.lt(values[index_j], values[marker])) { // se xj < xm
                marker = index_j;                            // m=j
            }
        }

        probe.swap(values, index_i, marker); // swap(x_i, x_m)
    }
}
// snippet:end selection-sort

} // namespace

namespace tca::algorithms {

void selection_sort(std::span<double> values) {
    tca::instrumentation::DirectProbe probe;
    selection_sort_impl(values, probe);
}

void selection_sort(std::span<double> values, tca::instrumentation::Metrics& metrics) {
    tca::instrumentation::Probe probe(metrics);
    selection_sort_impl(values, probe);
}

} // namespace tca::algorithms

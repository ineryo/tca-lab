#include "tca/algorithms/sorting/insertion_sort.hpp"

#include <cstddef>

#include "tca/core/instrumentation/direct_probe.hpp"
#include "tca/core/instrumentation/probe.hpp"

namespace {

template <typename ProbeType>
void insertion_sort_impl(std::span<double> values, ProbeType& probe) {
    for (std::size_t index_i = 1; index_i < values.size(); ++index_i) { // i=(1)..(n-1)
        const double value_marker = values[index_i];                    // v = xi
        std::size_t index_j = index_i;                                  // j = i

        while (index_j > 0 &&
               probe.lt(value_marker, values[index_j - 1]) // enquanto x_{j-1} > v
        ) {
            probe.write(values, index_j, values[index_j - 1]); // x_j = x_{j-1}
            --index_j;                                         // j = j - 1
        }

        probe.write(values, index_j, value_marker); // x_j = v
    }
}

} // namespace

namespace tca::algorithms {

void insertion_sort(std::span<double> values) {
    tca::instrumentation::DirectProbe probe;

    insertion_sort_impl(values, probe);
}

void insertion_sort(std::span<double> values, tca::instrumentation::Metrics& metrics) {
    tca::instrumentation::Probe probe(metrics);

    insertion_sort_impl(values, probe);
}

} // namespace tca::algorithms
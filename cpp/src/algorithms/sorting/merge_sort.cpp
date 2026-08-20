#include "tca/algorithms/sorting/merge_sort.hpp"

#include <cstddef>
#include <span>
#include <vector>

#include "tca/core/instrumentation/direct_probe.hpp"
#include "tca/core/instrumentation/probe.hpp"

namespace {

template <typename ProbeType>
void merge(std::span<double> values, std::span<double> buffer, std::size_t start,
           std::size_t middle, std::size_t end, ProbeType& probe) {
    for (std::size_t index_k = start; index_k < end; ++index_k) {
        probe.write(buffer, index_k,
                    values[index_k]); // l = x[start..m], r = x[m..end] {separação}
    }

    std::size_t index_l = start;  // i = 1
    std::size_t index_r = middle; // j = 1

    for (std::size_t index_k = start; index_k < end; ++index_k) {
        // para k = 1..n {combinação}

        if (index_l >= middle) {
            probe.write(values, index_k, buffer[index_r]); // x_k = r_j
            ++index_r;                                     // j = j+1

        } else if (index_r >= end) {
            probe.write(values, index_k, buffer[index_l]); // x_k = l_i
            ++index_l;                                     // i = i+1

        } else if (probe.lt(buffer[index_r],
                            buffer[index_l])) {            // se r_j < l_i então
            probe.write(values, index_k, buffer[index_r]); // x_k = r_j
            ++index_r;                                     // j = j+1

        } else {
            probe.write(values, index_k, buffer[index_l]); // x_k = l_i
            ++index_l;                                     // i = i+1
        }
    }
}

template <typename ProbeType>
void merge_sort_recursive(std::span<double> values, std::span<double> buffer,
                          std::size_t start, std::size_t end, ProbeType& probe) {
    if (end - start < 2) { // se n < 2 então retorne {caso básico da recursão}
        return;
    }

    const std::size_t middle = (start + end) / 2; // m = n/2

    merge_sort_recursive(values, buffer, start, middle,
                         probe); // mergesort(l, m) {recursão esquerda}

    merge_sort_recursive(values, buffer, middle, end,
                         probe); // mergesort(r, n-m) {recursão direita}

    merge(values, buffer, start, middle, end, probe); // {combinação}
}

template <typename ProbeType>
void merge_sort_impl(std::span<double> values, ProbeType& probe) {
    std::vector<double> buffer(values.size());

    merge_sort_recursive(values, std::span<double>{buffer}, 0, values.size(), probe);
}

} // namespace

namespace tca::algorithms {

void merge_sort(std::span<double> values) {
    tca::instrumentation::DirectProbe probe;

    merge_sort_impl(values, probe);
}

void merge_sort(std::span<double> values, tca::instrumentation::Metrics& metrics) {
    tca::instrumentation::Probe probe(metrics);

    merge_sort_impl(values, probe);
}

} // namespace tca::algorithms
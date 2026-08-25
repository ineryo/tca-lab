#include "tca/algorithms/sorting/merge_sort.hpp"

#include <cstddef>
#include <span>
#include <vector>

#include "tca/core/instrumentation/direct_probe.hpp"
#include "tca/core/instrumentation/probe.hpp"

namespace {

template <typename ProbeType>
void merge(std::span<double> values, std::span<double> buffer,
           std::size_t buffer_offset, std::size_t start, std::size_t middle,
           std::size_t end, ProbeType& probe) {
    for (std::size_t index_k = start; index_k < end; ++index_k) {
        const std::size_t index_buffer = index_k - buffer_offset;

        probe.write(buffer, index_buffer,
                    values[index_k]); // l = x[start..m], r = x[m..end] {separação}
    }

    std::size_t index_l = start;  // i = 1
    std::size_t index_r = middle; // j = 1

    for (std::size_t index_k = start; index_k < end; ++index_k) {
        // para k = 1..n {combinação}

        const std::size_t index_buffer_l = index_l - buffer_offset;
        const std::size_t index_buffer_r = index_r - buffer_offset;

        if (index_l >= middle) {
            probe.write(values, index_k,
                        buffer[index_buffer_r]); // x_k = r_j
            ++index_r;                           // j = j+1

        } else if (index_r >= end) {
            probe.write(values, index_k,
                        buffer[index_buffer_l]); // x_k = l_i
            ++index_l;                           // i = i+1

        } else if (probe.lt(buffer[index_buffer_r],
                            buffer[index_buffer_l])) { // se r_j < l_i então
            probe.write(values, index_k,
                        buffer[index_buffer_r]); // x_k = r_j
            ++index_r;                           // j = j+1

        } else {
            probe.write(values, index_k,
                        buffer[index_buffer_l]); // x_k = l_i
            ++index_l;                           // i = i+1
        }
    }
}

template <typename ProbeType>
void merge_sort_recursive(std::span<double> values, std::span<double> buffer,
                          std::size_t start, std::size_t end, ProbeType& probe,
                          const tca::algorithms::MergeSortOptions& options) {

    if (end - start < 2) { // se n < 2 então retorne {caso básico da recursão}
        return;
    }

    const std::size_t middle = (start + end) / 2; // m = n/2

    merge_sort_recursive(values, buffer, start, middle, probe,
                         options); // mergesort(l, m) {recursão esquerda}

    merge_sort_recursive(values, buffer, middle, end, probe,
                         options); // mergesort(r, n-m) {recursão direita}

    if (options.buffer == tca::algorithms::MergeBuffer::Local) {
        std::vector<double> local_buffer(end - start);

        merge(values, std::span<double>{local_buffer}, // aloca buffer local
              start, start, middle, end,
              probe); // {combinação classic}

    } else {
        merge(values,
              buffer, // usa buffer único reutilizado
              0, start, middle, end,
              probe); // {combinação smarter}
    }
}

template <typename ProbeType>
void merge_sort_impl(std::span<double> values, ProbeType& probe,
                     const tca::algorithms::MergeSortOptions& options) {

    std::vector<double> buffer;

    if (options.buffer == tca::algorithms::MergeBuffer::Reused) {
        buffer.resize(values.size()); // buffer único {smarter}
    }

    merge_sort_recursive(values, std::span<double>{buffer}, 0, values.size(), probe,
                         options);
}

} // namespace

namespace tca::algorithms {

void merge_sort(std::span<double> values) { merge_sort(values, MergeSortOptions{}); }

void merge_sort(std::span<double> values, tca::instrumentation::Metrics& metrics) {
    merge_sort(values, metrics, MergeSortOptions{});
}

void merge_sort(std::span<double> values, const MergeSortOptions& options) {
    tca::instrumentation::DirectProbe probe;

    merge_sort_impl(values, probe, options);
}

void merge_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                const MergeSortOptions& options) {
    tca::instrumentation::Probe probe(metrics);

    merge_sort_impl(values, probe, options);
}

} // namespace tca::algorithms
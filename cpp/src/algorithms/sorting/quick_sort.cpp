#include "tca/algorithms/sorting/quick_sort.hpp"

#include <cstddef>

#include "tca/core/instrumentation/direct_probe.hpp"
#include "tca/core/instrumentation/probe.hpp"
#include "tca/core/prng.hpp"

namespace {

std::size_t choose_pivot(std::size_t index_r, std::size_t index_s,
                         tca::algorithms::QuickPivot pivot, tca::PRNG& prng) {
    if (pivot == tca::algorithms::QuickPivot::First) {
        return index_r;
    }

    const std::size_t size = index_s - index_r + 1;

    if (pivot == tca::algorithms::QuickPivot::Quarter) {
        return index_r + size / 4;
    }

    return index_r + static_cast<std::size_t>(prng.randbelow(size));
}

// snippet:start quick-sort-partition
template <typename ProbeType>
std::size_t partition(std::span<double> values, std::size_t index_r,
                      std::size_t index_s, ProbeType& probe,
                      tca::algorithms::QuickPivot pivot, tca::PRNG& prng) {
    const std::size_t index_pivot = choose_pivot(index_r, index_s, pivot, prng);
    probe.swap(values, index_r, index_pivot); // move o pivô para x_r

    const double value_pivot = values[index_r]; // v = x_r
    std::size_t index_i = index_r;              // i = r
    std::size_t index_j = index_s + 1;          // j = s+1

    while (true) { // repita {separação}
        ++index_i; // i = i+1

        while (index_i <= index_s &&
               probe.lt(values[index_i], value_pivot)) { // até x_i >= v
            ++index_i;                                   // i = i+1
        }

        --index_j; // j = j-1

        while (probe.lt(value_pivot, values[index_j])) { // até x_j <= v
            --index_j;                                   // j = j-1
        }

        if (index_j <= index_i) { // até j <= i
            break;
        }

        probe.swap(values, index_i, index_j); // troque x_i com x_j
    }

    probe.swap(values, index_r, index_j); // troque x_r com x_j

    return index_j;
}
// snippet:end quick-sort-partition

// snippet:start quick-sort
template <typename ProbeType>
void quick_sort_recursive(std::span<double> values, std::size_t index_r,
                          std::size_t index_s, ProbeType& probe,
                          const tca::algorithms::QuickSortOptions& options,
                          tca::PRNG& prng) {
    while (index_r < index_s) { // enquanto s > r
        const std::size_t index_j =
            partition(values, index_r, index_s, probe, options.pivot, prng);

        if (options.recursion == tca::algorithms::QuickRecursion::Classic) {
            if (index_j > index_r) {
                quick_sort_recursive(values, index_r, index_j - 1, probe, options,
                                     prng);
            }

            if (index_j < index_s) {
                quick_sort_recursive(values, index_j + 1, index_s, probe, options,
                                     prng);
            }

            return;
        }

        const std::size_t left_size = index_j - index_r;
        const std::size_t right_size = index_s - index_j;

        if (left_size < right_size) {
            if (index_j > index_r) {
                quick_sort_recursive(values, index_r, index_j - 1, probe, options,
                                     prng);
            }

            index_r = index_j + 1; // continua iterativamente pela direita

        } else {
            if (index_j < index_s) {
                quick_sort_recursive(values, index_j + 1, index_s, probe, options,
                                     prng);
            }

            index_s = index_j - 1; // continua iterativamente pela esquerda
        }
    }
}
// snippet:end quick-sort

template <typename ProbeType>
void quick_sort_impl(std::span<double> values, ProbeType& probe,
                     const tca::algorithms::QuickSortOptions& options) {
    if (values.empty()) {
        return;
    }

    tca::PRNG prng(options.seed);

    quick_sort_recursive(values, 0, values.size() - 1, probe, options, prng);
}

} // namespace

namespace tca::algorithms {

void quick_sort(std::span<double> values) { quick_sort(values, QuickSortOptions{}); }

void quick_sort(std::span<double> values, tca::instrumentation::Metrics& metrics) {
    quick_sort(values, metrics, QuickSortOptions{});
}

void quick_sort(std::span<double> values, const QuickSortOptions& options) {
    tca::instrumentation::DirectProbe probe;

    quick_sort_impl(values, probe, options);
}

void quick_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                const QuickSortOptions& options) {
    tca::instrumentation::Probe probe(metrics);

    quick_sort_impl(values, probe, options);
}

} // namespace tca::algorithms

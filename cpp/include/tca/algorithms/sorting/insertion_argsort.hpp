#pragma once

#include <concepts>
#include <cstddef>
#include <functional>
#include <numeric>
#include <span>
#include <vector>

namespace tca::algorithms {

/**
 * Returns a stable permutation of indices that orders values according to
 * compare. The input values are not modified.
 */
template <typename T, typename Compare = std::less<>>
    requires std::strict_weak_order<Compare, const T&, const T&>
std::vector<std::size_t> insertion_argsort(std::span<const T> values,
                                           Compare compare = {}) {
    std::vector<std::size_t> indices(values.size());
    std::iota(indices.begin(), indices.end(), std::size_t{0});

    for (std::size_t index_i = 1; index_i < indices.size(); ++index_i) {
        const std::size_t current = indices[index_i];
        std::size_t index_j = index_i;

        while (index_j > 0 && compare(values[current], values[indices[index_j - 1]])) {
            indices[index_j] = indices[index_j - 1];
            --index_j;
        }

        indices[index_j] = current;
    }

    return indices;
}

} // namespace tca::algorithms

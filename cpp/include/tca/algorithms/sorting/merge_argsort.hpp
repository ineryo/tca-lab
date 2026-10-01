#pragma once

#include <algorithm>
#include <concepts>
#include <cstddef>
#include <functional>
#include <numeric>
#include <span>
#include <vector>

namespace tca::algorithms {

namespace detail {

template <typename T, typename Compare>
    requires std::strict_weak_order<Compare, const T&, const T&>
void merge_argsort_range(std::span<const T> values, std::vector<std::size_t>& indices,
                         std::vector<std::size_t>& buffer, std::size_t begin,
                         std::size_t end, Compare& compare) {
    if (end - begin < 2) {
        return;
    }

    const std::size_t middle = begin + (end - begin) / 2;

    merge_argsort_range(values, indices, buffer, begin, middle, compare);
    merge_argsort_range(values, indices, buffer, middle, end, compare);

    std::size_t left = begin;
    std::size_t right = middle;
    std::size_t output = begin;

    while (left < middle && right < end) {
        const std::size_t left_index = indices[left];
        const std::size_t right_index = indices[right];

        if (compare(values[right_index], values[left_index])) {
            buffer[output++] = right_index;
            ++right;
        } else {
            // Choose the left element on equivalence to preserve stability.
            buffer[output++] = left_index;
            ++left;
        }
    }

    while (left < middle) {
        buffer[output++] = indices[left++];
    }

    while (right < end) {
        buffer[output++] = indices[right++];
    }

    std::copy(buffer.begin() + static_cast<std::ptrdiff_t>(begin),
              buffer.begin() + static_cast<std::ptrdiff_t>(end),
              indices.begin() + static_cast<std::ptrdiff_t>(begin));
}

} // namespace detail

/**
 * Returns a stable permutation of indices that orders values according to
 * compare. The input values are not modified.
 */
template <typename T, typename Compare = std::less<>>
    requires std::strict_weak_order<Compare, const T&, const T&>
std::vector<std::size_t> merge_argsort(std::span<const T> values,
                                       Compare compare = {}) {
    std::vector<std::size_t> indices(values.size());
    std::iota(indices.begin(), indices.end(), std::size_t{0});

    if (values.size() < 2) {
        return indices;
    }

    std::vector<std::size_t> buffer(values.size());

    detail::merge_argsort_range(values, indices, buffer, 0, values.size(), compare);

    return indices;
}

} // namespace tca::algorithms

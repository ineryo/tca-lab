#pragma once

#include <cstddef>

namespace tca::instrumentation {

struct Metrics {
    std::size_t comparisons = 0;
    std::size_t swaps = 0;

    void reset() noexcept {
        comparisons = 0;
        swaps = 0;
    }
};

} // namespace tca::instrumentation
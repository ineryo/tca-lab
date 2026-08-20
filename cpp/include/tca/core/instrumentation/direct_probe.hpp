#pragma once

#include <cstddef>
#include <span>
#include <utility>

namespace tca::instrumentation {

class DirectProbe {
  public:
    bool lt(double left, double right) const noexcept { return left < right; }

    void swap(std::span<double> values, std::size_t index_i,
              std::size_t index_j) const noexcept {
        if (index_i != index_j) {
            std::swap(values[index_i], values[index_j]);
        }
    }
};

} // namespace tca::instrumentation
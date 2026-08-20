#pragma once

#include <cstddef>
#include <span>
#include <utility>

#include "tca/core/instrumentation/metrics.hpp"

namespace tca::instrumentation {

class Probe {
  public:
    explicit Probe(Metrics& metrics) noexcept : metrics_(metrics) {}

    bool lt(double left, double right) noexcept {
        ++metrics_.comparisons;
        return left < right;
    }

    void swap(std::span<double> values, std::size_t index_i,
              std::size_t index_j) noexcept {
        if (index_i == index_j) {
            return;
        }

        std::swap(values[index_i], values[index_j]);
        ++metrics_.swaps;
    }

  private:
    Metrics& metrics_;
};

} // namespace tca::instrumentation
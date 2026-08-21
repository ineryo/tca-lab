#pragma once

#include <cstdint>
#include <stdexcept>

namespace tca {

class PRNG {
  public:
    explicit PRNG(std::uint64_t seed = 0) noexcept : state_(seed) {}

    std::uint64_t next_uint64() noexcept {
        state_ += 0x9E3779B97F4A7C15ULL;

        std::uint64_t value = state_;
        value = (value ^ (value >> 30)) * 0xBF58476D1CE4E5B9ULL;
        value = (value ^ (value >> 27)) * 0x94D049BB133111EBULL;
        value ^= value >> 31;

        return value;
    }

    std::uint64_t randbelow(std::uint64_t upper_bound) {
        if (upper_bound == 0) {
            throw std::invalid_argument("upper_bound must be greater than zero");
        }

        const std::uint64_t threshold = -upper_bound % upper_bound;

        while (true) {
            const std::uint64_t value = next_uint64();

            if (value >= threshold) {
                return value % upper_bound;
            }
        }
    }

  private:
    std::uint64_t state_;
};

} // namespace tca
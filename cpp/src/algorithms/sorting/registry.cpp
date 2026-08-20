#include "tca/algorithms/sorting/registry.hpp"

#include <stdexcept>
#include <string>

namespace tca::algorithms {

#define TCA_SORTING_ALGORITHM(method, function)                                        \
    void function(std::span<double> values);                                           \
    void function(std::span<double> values, tca::instrumentation::Metrics& metrics);

#include "tca/algorithms/sorting/algorithms.def"

#undef TCA_SORTING_ALGORITHM

namespace {

using SortFunction = void (*)(std::span<double>);

using InstrumentedSortFunction = void (*)(std::span<double>,
                                          tca::instrumentation::Metrics&);

struct SortingAlgorithm {
    std::string_view method;
    SortFunction function;
    InstrumentedSortFunction instrumented_function;
};

#define TCA_SORTING_ALGORITHM(method, function)                                        \
    {                                                                                  \
        #method,                                                                       \
        static_cast<SortFunction>(&function),                                          \
        static_cast<InstrumentedSortFunction>(&function),                              \
    },

constexpr SortingAlgorithm algorithms[] = {
#include "tca/algorithms/sorting/algorithms.def"
};

#undef TCA_SORTING_ALGORITHM

#define TCA_SORTING_ALGORITHM(method, function) std::string_view{#method},

constexpr std::string_view algorithm_names[] = {
#include "tca/algorithms/sorting/algorithms.def"
};

#undef TCA_SORTING_ALGORITHM

const SortingAlgorithm* find_algorithm(std::string_view method) noexcept {
    for (const auto& algorithm : algorithms) {
        if (algorithm.method == method) {
            return &algorithm;
        }
    }

    return nullptr;
}

} // namespace

void sort(std::span<double> values, std::string_view method) {
    const auto* algorithm = find_algorithm(method);

    if (algorithm == nullptr) {
        throw std::invalid_argument("unknown sorting algorithm: " +
                                    std::string(method));
    }

    algorithm->function(values);
}

void sort(std::span<double> values, std::string_view method,
          tca::instrumentation::Metrics& metrics) {
    const auto* algorithm = find_algorithm(method);

    if (algorithm == nullptr) {
        throw std::invalid_argument("unknown sorting algorithm: " +
                                    std::string(method));
    }

    algorithm->instrumented_function(values, metrics);
}

bool has_sorting_algorithm(std::string_view method) noexcept {
    return find_algorithm(method) != nullptr;
}

std::span<const std::string_view> available_sorting_algorithms() noexcept {
    return algorithm_names;
}

} // namespace tca::algorithms
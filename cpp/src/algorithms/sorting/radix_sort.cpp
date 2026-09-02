#include "tca/algorithms/sorting/radix_sort.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>

#include "tca/core/instrumentation/direct_probe.hpp"
#include "tca/core/instrumentation/probe.hpp"
#include "tca/core/quantization.hpp"

namespace {

std::uint64_t digit_at(std::uint64_t value, std::uint64_t exponent) {
    return (value / exponent) % 10; // digito(v, exp)
}

std::vector<std::int64_t> normalize_keys(std::vector<std::int64_t> keys, int digits) {
    int removable_digits = 0;

    while (removable_digits < digits) {
        bool all_divisible_by_ten = true;

        for (const auto key : keys) {
            if (key != 0 && key % 10 != 0) {
                all_divisible_by_ten = false;
                break;
            }
        }

        if (!all_divisible_by_ten) {
            break;
        }

        for (auto& key : keys) {
            key /= 10;
        }

        ++removable_digits;
    }

    return keys;
}

int digit_count(std::uint64_t value) {
    int count = 0;

    while (value > 0) {
        value /= 10;
        ++count;
    }

    return count;
}

template <typename ProbeType>
std::vector<std::size_t> counting_sort_by_digit(const std::vector<std::size_t>& indices,
                                                const std::vector<std::uint64_t>& keys,
                                                std::uint64_t exponent,
                                                ProbeType& probe) {
    std::size_t counts[10] = {}; // c[0..9] = 0

    for (std::size_t index_i = 0; index_i < indices.size();
         ++index_i) {                                      // para i = 0..n-1 {contagem}
        const std::size_t index_source = indices[index_i]; // idx_i = idx[i]
        const std::uint64_t digit =
            digit_at(keys[index_source], exponent); // d = digito(y_idx[i], exp)

        ++counts[digit]; // c[d] = c[d] + 1
    }

    for (std::size_t digit = 1; digit < 10; ++digit) { // para d = 1..9 {acumulação}
        counts[digit] += counts[digit - 1];            // c[d] = c[d] + c[d-1]
    }

    std::vector<std::size_t> output(indices.size()); // out[0..n-1]

    for (std::size_t index_i = indices.size(); index_i > 0;
         --index_i) { // para i = n-1..0 {estabilidade}
        const std::size_t index_source = indices[index_i - 1]; // idx_i = idx[i]
        const std::uint64_t digit =
            digit_at(keys[index_source], exponent); // d = digito(y_idx_i, exp)

        const std::size_t position = counts[digit] - 1; // p = c[d] - 1

        probe.write(std::span<std::size_t>{output}, position,
                    index_source); // out[p] = idx_i

        --counts[digit]; // c[d] = c[d] - 1
    }

    return output;
}

// snippet:start radix-sort
template <typename ProbeType>
void radix_sort_impl(std::span<double> values, ProbeType& probe, int digits) {
    if (digits < 0 || digits > tca::MAX_DECIMAL_DIGITS) {
        throw std::invalid_argument("digits must be between 0 and 15");
    }

    if (values.size() < 2) { // se n < 2 então retorne {caso básico}
        return;
    }

    std::vector<std::int64_t> raw_keys(values.size());

    for (std::size_t index_i = 0; index_i < values.size(); ++index_i) {
        raw_keys[index_i] = tca::decimal_key(values[index_i],
                                             digits); // k_i = trunc(x_i * 10^digits)
    }

    const auto keys =
        normalize_keys(raw_keys, digits); // remove zeros comuns da quantizacao

    const auto minimum_key =
        *std::min_element(keys.begin(), keys.end()); // k_min = min(k)

    std::vector<std::uint64_t> shifted_keys(values.size());

    for (std::size_t index_i = 0; index_i < keys.size(); ++index_i) {
        shifted_keys[index_i] =
            // keys[index_i] - minimum_key seria um problema pois
            // se keys[index_i] for INT64_MAX e minimum_key for INT64_MIN,
            // a diferença não cabe em int64_t
            // Logo, a aritmética é feita em uint64_t.
            // A diferença representa corretamente a distância, sem overflow signed
            static_cast<std::uint64_t>(keys[index_i]) -
            static_cast<std::uint64_t>(minimum_key); // y_i = k_i - k_min
    }

    const auto maximum_key = *std::max_element(shifted_keys.begin(),
                                               shifted_keys.end()); // max = max(y)

    const int effective_digits =
        digit_count(maximum_key); // numero efetivo de digitos LSD

    std::vector<std::size_t> indices(values.size());

    for (std::size_t index_i = 0; index_i < indices.size(); ++index_i) {
        indices[index_i] = index_i; // idx = [0, 1, ..., n-1]
    }

    std::uint64_t exponent = 1; // exp = 1

    for (int pass = 0; pass < effective_digits;
         ++pass) { // para cada digito efetivo {passadas LSD}
        indices = counting_sort_by_digit(indices, shifted_keys, exponent, probe);
        // counting(idx, exp)

        exponent *= 10; // exp = 10 * exp
    }

    std::vector<double> ordered_values(values.size()); // x' = vetor ordenado

    for (std::size_t index_k = 0; index_k < indices.size();
         ++index_k) { // para k = 0..n-1 {reordenação final}
        const std::size_t index_source = indices[index_k];

        probe.write(std::span<double>{ordered_values}, index_k,
                    values[index_source]); // x'_k = x_idx[k]
    }

    for (std::size_t index_k = 0; index_k < values.size();
         ++index_k) { // para k = 0..n-1
        probe.write(values, index_k,
                    ordered_values[index_k]); // x_k = x'_k
    }
}
// snippet:end radix-sort

} // namespace

namespace tca::algorithms {

void radix_sort(std::span<double> values) { radix_sort(values, 3); }

void radix_sort(std::span<double> values, tca::instrumentation::Metrics& metrics) {
    radix_sort(values, metrics, 3);
}

void radix_sort(std::span<double> values, int digits) {
    tca::instrumentation::DirectProbe probe;

    radix_sort_impl(values, probe, digits);
}

void radix_sort(std::span<double> values, tca::instrumentation::Metrics& metrics,
                int digits) {
    tca::instrumentation::Probe probe(metrics);

    radix_sort_impl(values, probe, digits);
}

} // namespace tca::algorithms

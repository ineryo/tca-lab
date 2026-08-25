#include "tca/algorithms/sorting/radix_binary_sort.hpp"

#include <array>
#include <bit>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <span>
#include <stdexcept>
#include <utility>
#include <vector>

#include "tca/core/instrumentation/direct_probe.hpp"
#include "tca/core/instrumentation/probe.hpp"

namespace {

constexpr std::size_t BYTE_BITS = 8;
constexpr std::size_t BYTE_VALUES = 256;
constexpr std::size_t RADIX_PASSES = sizeof(std::uint64_t);

std::uint64_t sortable_key(double value) noexcept {
    const std::uint64_t bits =
        std::bit_cast<std::uint64_t>(value); // bits(x) {representação IEEE-754}

    const std::uint64_t sign = bits >> 63; // s = bit de sinal

    const std::uint64_t mask =
        (std::uint64_t{0} - sign) |
        (std::uint64_t{1} << 63); // negativo: ~0; positivo: somente bit de sinal

    return bits ^ mask; // chave monotônica correspondente à ordem numérica
}

std::size_t byte_at(std::uint64_t key, std::size_t pass) noexcept {
    const std::size_t shift = pass * BYTE_BITS; // shift = 8 * pass

    return static_cast<std::size_t>((key >> shift) & 0xFFu); // byte(key, pass)
}

void validate_values(std::span<double> values) {
    for (const double value : values) {
        if (std::isnan(value)) {
            throw std::invalid_argument("radix_binary_sort does not support NaN");
        }
    }
}

template <typename ProbeType>
void counting_sort_by_byte(std::span<double> source, std::span<double> destination,
                           std::size_t pass, ProbeType& probe) {
    std::array<std::size_t, BYTE_VALUES> counts{}; // c[0..255] = 0

    for (std::size_t index_i = 0; index_i < source.size();
         ++index_i) { // para i = 0..n-1 {contagem}

        const std::uint64_t key = sortable_key(source[index_i]); // k_i = chave(x_i)

        const std::size_t bucket = byte_at(key, pass); // b = byte(k_i, pass)

        ++counts[bucket]; // c[b] = c[b] + 1
    }

    std::array<std::size_t, BYTE_VALUES> offsets{}; // p[0..255]

    std::size_t position = 0;

    for (std::size_t bucket = 0; bucket < BYTE_VALUES;
         ++bucket) { // para b = 0..255 {offsets}

        offsets[bucket] = position; // p[b] = posição inicial do bucket
        position += counts[bucket]; // posição do próximo bucket
    }

    for (std::size_t index_i = 0; index_i < source.size();
         ++index_i) { // para i = 0..n-1 {distribuição estável}

        const std::uint64_t key = sortable_key(source[index_i]); // k_i = chave(x_i)

        const std::size_t bucket = byte_at(key, pass); // b = byte(k_i, pass)

        const std::size_t index_output = offsets[bucket]++; // j = p[b]; p[b] = p[b] + 1

        probe.write(destination, index_output,
                    source[index_i]); // out[j] = x_i
    }
}

template <typename ProbeType>
void radix_binary_sort_impl(std::span<double> values, ProbeType& probe) {
    if (values.size() < 2) { // se n < 2 então retorne {caso básico}
        return;
    }

    validate_values(values); // domínio inicial: double sem NaN

    std::vector<double> buffer(values.size()); // buffer auxiliar O(n)

    std::span<double> source = values;
    std::span<double> destination{buffer};

    for (std::size_t pass = 0; pass < RADIX_PASSES;
         ++pass) { // para cada um dos 8 bytes {passadas LSD}

        counting_sort_by_byte(source, destination, pass,
                              probe); // counting(source, byte)

        std::swap(source, destination); // próxima passada usa a saída anterior
    }

    // Como um uint64_t possui exatamente 8 bytes, há um número par de passadas.
    // A primeira escreve no buffer e a última escreve novamente em values.
    // Portanto, ao final das 8 passadas, values já contém a sequência ordenada.
}

} // namespace

namespace tca::algorithms {

void radix_binary_sort(std::span<double> values) {
    tca::instrumentation::DirectProbe probe;

    radix_binary_sort_impl(values, probe);
}

void radix_binary_sort(std::span<double> values,
                       tca::instrumentation::Metrics& metrics) {
    tca::instrumentation::Probe probe(metrics);

    radix_binary_sort_impl(values, probe);
}

} // namespace tca::algorithms
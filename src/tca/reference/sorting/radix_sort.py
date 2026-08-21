from tca.core.instrumentation import DirectProbe, Metrics, Probe
from tca.core.quantization import MAX_DECIMAL_DIGITS, decimal_key


def radix_sort(
    values,
    metrics: Metrics | None = None,
    *,
    digits: int = 3,
) -> None:
    if not isinstance(digits, int):
        raise TypeError("digits must be an integer")

    if not 0 <= digits <= MAX_DECIMAL_DIGITS:
        raise ValueError(f"digits must be between 0 and {MAX_DECIMAL_DIGITS}")

    probe = DirectProbe() if metrics is None else Probe(metrics)

    if len(values) < 2:  # se n < 2 então retorne {caso básico}
        return

    keys = [
        decimal_key(value, digits) for value in values
    ]  # k_i = trunc(x_i * 10^digits)
    minimum_key = min(keys)  # k_min = min(k)
    shifted_keys = [key - minimum_key for key in keys]  # y_i = k_i - k_min
    indices = list(range(len(values)))  # idx = [0, 1, ..., n-1]
    maximum_key = max(shifted_keys)  # max = max(y)

    exponent = 1  # exp = 1

    while maximum_key // exponent > 0:  # enquanto max / exp > 0 {passadas LSD}
        indices = _counting_sort_by_digit(
            indices, shifted_keys, exponent, probe
        )  # counting(idx, exp)
        exponent *= 10  # exp = 10 * exp

    ordered_values = [None] * len(values)  # x' = vetor ordenado

    for index_k, index_source in enumerate(
        indices
    ):  # para k = 0..n-1 {reordenação final}
        probe.write(ordered_values, index_k, values[index_source])  # x'_k = x_idx[k]

    for index_k, value in enumerate(ordered_values):  # para k = 0..n-1
        probe.write(values, index_k, value)  # x_k = x'_k


def _counting_sort_by_digit(
    indices,
    keys,
    exponent: int,
    probe,
):
    counts = [0] * 10  # c[0..9] = 0

    for index_i in range(len(indices)):  # para i = 0..n-1 {contagem}
        digit = _digit_at(keys[indices[index_i]], exponent)  # d = digito(y_idx[i], exp)
        counts[digit] += 1  # c[d] = c[d] + 1

    for digit in range(1, 10):  # para d = 1..9 {acumulação}
        counts[digit] += counts[digit - 1]  # c[d] = c[d] + c[d-1]

    output = [None] * len(indices)  # out[0..n-1]

    for index_i in range(len(indices) - 1, -1, -1):  # para i = n-1..0 {estabilidade}
        index_source = indices[index_i]  # idx_i = idx[i]
        digit = _digit_at(keys[index_source], exponent)  # d = digito(y_idx_i, exp)
        position = counts[digit] - 1  # p = c[d] - 1

        probe.write(output, position, index_source)  # out[p] = idx_i
        counts[digit] -= 1  # c[d] = c[d] - 1

    return output


def _digit_at(value: int, exponent: int) -> int:
    return (value // exponent) % 10  # digito(v, exp)

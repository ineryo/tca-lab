from tca.core.instrumentation import DirectProbe, Metrics, Probe


def merge_sort(values, metrics: Metrics | None = None) -> None:
    probe = DirectProbe() if metrics is None else Probe(metrics)

    buffer = [None] * len(values)

    _merge_sort(values, buffer, 0, len(values), probe)


def _merge_sort(values, buffer, start: int, end: int, probe) -> None:
    if end - start < 2:  # se n < 2 então retorne {caso básico da recursão}
        return

    middle = (start + end) // 2  # m = n/2

    _merge_sort(
        values, buffer, start, middle, probe
    )  # mergesort(l, m) {recursão esquerda}

    _merge_sort(
        values, buffer, middle, end, probe
    )  # mergesort(r, n-m) {recursão direita}

    _merge(values, buffer, start, middle, end, probe)  # {combinação}


def _merge(values, buffer, start: int, middle: int, end: int, probe) -> None:
    for index_k in range(start, end):
        probe.write(
            buffer, index_k, values[index_k]
        )  # l = x[start..m], r = x[m..end] {separação}

    index_l = start  # i = 1
    index_r = middle  # j = 1

    for index_k in range(start, end):  # para k = 1..n {combinação}
        if index_l >= middle:
            probe.write(values, index_k, buffer[index_r])  # x_k = r_j
            index_r += 1  # j = j+1

        elif index_r >= end:
            probe.write(values, index_k, buffer[index_l])  # x_k = l_i
            index_l += 1  # i = i+1

        elif probe.lt(buffer[index_r], buffer[index_l]):  # se r_j < l_i então
            probe.write(values, index_k, buffer[index_r])  # x_k = r_j
            index_r += 1  # j = j+1

        else:
            probe.write(values, index_k, buffer[index_l])  # x_k = l_i
            index_l += 1  # i = i+1

from tca.core.instrumentation import DirectProbe, Metrics, Probe


def insertion_sort(
    values,
    metrics: Metrics | None = None,
) -> None:
    probe = DirectProbe() if metrics is None else Probe(metrics)

    for index_i in range(1, len(values)):  # i=(1)..(n-1)
        value_marker = values[index_i]  # v = xi
        index_j = index_i  # j = i

        while index_j > 0 and probe.lt(
            value_marker, values[index_j - 1]
        ):  # enquanto x_{j-1} > v
            probe.write(values, index_j, values[index_j - 1])  # x_j = x_{j-1}
            index_j -= 1  # j = j - 1

        probe.write(values, index_j, value_marker)  # x_j = v

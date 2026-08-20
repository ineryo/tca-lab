from tca.core.instrumentation import DirectProbe, Metrics, Probe


def selection_sort(
    values,
    metrics: Metrics | None = None,
) -> None:
    probe = DirectProbe() if metrics is None else Probe(metrics)

    for index_i in range(len(values) - 1):  # i=(1)..(n-1)
        marker = index_i  # m=i

        for index_j in range(index_i + 1, len(values)):  # j=(i+1)..(n)
            if probe.lt(values[index_j], values[marker]):  # se xj < xm
                marker = index_j  # m=j

        probe.swap(values, index_i, marker)  # swap(x_i, x_m)

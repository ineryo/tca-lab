from tca.core.instrumentation import Metrics, Probe


def selection_sort(
    values,
    metrics: Metrics | None = None,
) -> None:
    if metrics is None:
        _selection_sort(values)
        return

    _selection_sort_instrumented(
        values,
        Probe(metrics),
    )


def _selection_sort(values) -> None:
    for index_i in range(len(values) - 1):  # i=(1)..(n-1)
        marker = index_i  # m=i

        for index_j in range(index_i + 1, len(values)):  # j=(i+1)..(n)
            if values[index_j] < values[marker]:  # se xj < xm
                marker = index_j  # m=j, xm=xj

        if marker != index_i:  # swap(x_i, x_m)
            values[marker], values[index_i] = values[index_i], values[marker]


def _selection_sort_instrumented(
    values,
    probe: Probe,
) -> None:
    for index_i in range(len(values) - 1):
        marker = index_i

        for index_j in range(index_i + 1, len(values)):
            if probe.lt(values[index_j], values[marker]):
                marker = index_j

        probe.swap(values, index_i, marker)

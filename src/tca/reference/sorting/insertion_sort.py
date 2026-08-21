from tca.core.instrumentation import Metrics, Trace, make_probe


def insertion_sort(
    values,
    metrics: Metrics | None = None,
    trace: Trace | None = None,
) -> None:
    probe = make_probe(metrics, trace)

    for index_i in range(1, len(values)):  # i=(1)..(n-1)
        value_marker = values[index_i]  # v = x_i
        index_j = index_i  # j = i

        probe.event(
            "select_key",
            indices=(index_i,),
            values=(value_marker,),
        )  # seleciona v = x_i

        while index_j > 0 and probe.lt(
            value_marker,
            values[index_j - 1],
            indices=(index_i, index_j - 1),
            roles=("key", "current"),
        ):  # enquanto x_{j-1} > v
            probe.write(values, index_j, values[index_j - 1])  # x_j = x_{j-1}
            index_j -= 1  # j = j - 1

        probe.write(values, index_j, value_marker)  # x_j = v

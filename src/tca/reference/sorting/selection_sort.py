from tca.core.instrumentation import Metrics, Trace, make_probe


def selection_sort(
    values,
    metrics: Metrics | None = None,
    trace: Trace | None = None,
) -> None:
    probe = make_probe(metrics, trace)

    for index_i in range(len(values) - 1):  # i=(1)..(n-1)
        marker = index_i  # m=i

        probe.event(
            "select_minimum",
            indices=(marker,),
            values=(values[marker],),
        )  # mínimo atual m=i

        for index_j in range(index_i + 1, len(values)):  # j=(i+1)..(n)
            if probe.lt(
                values[index_j],
                values[marker],
                indices=(index_j, marker),
                roles=("current", "marker"),
            ):  # se x_j < x_m
                marker = index_j  # m=j

                probe.event(
                    "select_minimum",
                    indices=(marker,),
                    values=(values[marker],),
                )  # novo mínimo m=j

        probe.swap(values, index_i, marker)  # swap(x_i, x_m)

from tca.core.instrumentation import Metrics, Trace, make_probe


def merge_sort(
    values,
    metrics: Metrics | None = None,
    trace: Trace | None = None,
    *,
    buffer: str = "reused",
) -> None:
    if buffer not in {"local", "reused"}:
        raise ValueError(f"unknown buffer strategy {buffer!r}")

    probe = make_probe(metrics, trace)

    shared_buffer = [None] * len(values) if buffer == "reused" else None

    _merge_sort(
        values,
        shared_buffer,
        0,
        len(values),
        probe,
        buffer,
    )


# snippet:start merge-sort
def _merge_sort(
    values,
    buffer,
    start: int,
    end: int,
    probe,
    buffer_strategy: str,
) -> None:
    if end - start < 2:  # se n < 2 então retorne {caso básico da recursão}
        return

    middle = (start + end) // 2  # m = n/2

    _merge_sort(
        values,
        buffer,
        start,
        middle,
        probe,
        buffer_strategy,
    )  # mergesort(l, m) {recursão esquerda}

    _merge_sort(
        values,
        buffer,
        middle,
        end,
        probe,
        buffer_strategy,
    )  # mergesort(r, n-m) {recursão direita}

    probe.event(
        "merge_range",
        indices=(start, middle, end),
    )  # combina [start..middle) com [middle..end)

    _merge(
        values,
        buffer,
        start,
        middle,
        end,
        probe,
        buffer_strategy,
    )  # {combinação}


# snippet:end merge-sort


# snippet:start merge-sort-combine
def _merge(
    values,
    buffer,
    start: int,
    middle: int,
    end: int,
    probe,
    buffer_strategy: str,
) -> None:
    if buffer_strategy == "local":
        working_buffer = [None] * (end - start)  # buffer local {classic}
        buffer_offset = start

    else:
        working_buffer = buffer  # buffer único reutilizado {smarter}
        buffer_offset = 0

    for index_k in range(start, end):
        index_buffer = index_k - buffer_offset

        probe.write(
            working_buffer,
            index_buffer,
            values[index_k],
            target="buffer",
        )  # l = x[start..m], r = x[m..end] {separação}

    index_l = start  # i = 1
    index_r = middle  # j = 1

    for index_k in range(start, end):  # para k = 1..n {combinação}
        index_buffer_l = index_l - buffer_offset
        index_buffer_r = index_r - buffer_offset

        if index_l >= middle:
            probe.write(
                values,
                index_k,
                working_buffer[index_buffer_r],
                target="values",
            )  # x_k = r_j
            index_r += 1  # j = j+1

        elif index_r >= end:
            probe.write(
                values,
                index_k,
                working_buffer[index_buffer_l],
                target="values",
            )  # x_k = l_i
            index_l += 1  # i = i+1
        elif probe.lt(
            working_buffer[index_buffer_r],
            working_buffer[index_buffer_l],
            indices=(index_r, index_l),
            roles=("right", "left"),
        ):  # se r_j < l_i então
            probe.write(
                values,
                index_k,
                working_buffer[index_buffer_r],
                target="values",
            )  # x_k = r_j
            index_r += 1  # j = j+1

        else:
            probe.write(
                values,
                index_k,
                working_buffer[index_buffer_l],
                target="values",
            )  # x_k = l_i
            index_l += 1  # i = i+1


# snippet:end merge-sort-combine

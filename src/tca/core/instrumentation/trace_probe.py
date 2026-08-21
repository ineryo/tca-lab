from .metrics import Metrics
from .trace import Trace


class TraceProbe:
    def __init__(self, metrics: Metrics, trace: Trace) -> None:
        self.metrics = metrics
        self.trace = trace

    def lt(
        self,
        left,
        right,
        *,
        indices: tuple[int, ...] = (),
        roles: tuple[str, ...] = (),
    ) -> bool:
        result = left < right

        self.metrics.comparisons += 1

        data = {"result": result}

        if roles:
            data["roles"] = roles

        self.trace.add(
            "compare",
            indices=indices,
            values=(left, right),
            **data,
        )

        return result

    def swap(self, values, index_i: int, index_j: int) -> None:
        if index_i == index_j:
            return

        value_i = values[index_i]
        value_j = values[index_j]

        values[index_i], values[index_j] = values[index_j], values[index_i]

        self.metrics.swaps += 1
        self.metrics.writes += 2

        self.trace.add(
            "swap",
            indices=(index_i, index_j),
            values=(value_i, value_j),
        )

    def write(
        self,
        values,
        index: int,
        value,
        *,
        target: str | None = None,
    ) -> None:
        previous = values[index]

        values[index] = value
        self.metrics.writes += 1

        data = {} if target is None else {"target": target}

        self.trace.add(
            "write",
            indices=(index,),
            values=(previous, value),
            **data,
        )

    def event(
        self,
        kind: str,
        *,
        indices: tuple[int, ...] = (),
        values: tuple[object, ...] = (),
        **data,
    ) -> None:
        self.trace.add(
            kind,
            indices=indices,
            values=values,
            **data,
        )

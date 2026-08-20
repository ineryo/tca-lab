from .metrics import Metrics


class Probe:
    def __init__(self, metrics: Metrics) -> None:
        self.metrics = metrics

    def lt(self, left, right) -> bool:
        self.metrics.comparisons += 1
        return left < right

    def write(self, values, index: int, value) -> None:
        values[index] = value
        self.metrics.writes += 1

    def swap(self, values, index_i: int, index_j: int) -> None:
        if index_i == index_j:
            return

        values[index_i], values[index_j] = (
            values[index_j],
            values[index_i],
        )

        self.metrics.swaps += 1
        self.metrics.writes += 2

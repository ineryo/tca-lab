from dataclasses import dataclass


@dataclass(slots=True)
class Metrics:
    comparisons: int = 0
    swaps: int = 0

    def reset(self) -> None:
        self.comparisons = 0
        self.swaps = 0

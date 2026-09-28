from dataclasses import dataclass, fields


@dataclass(slots=True)
class Metrics:
    """Semantic counters shared by direct, traced, and native sorting runs."""
    comparisons: int = 0
    swaps: int = 0
    writes: int = 0

    def reset(self) -> None:
        for field in fields(self):
            setattr(
                self,
                field.name,
                0,
            )

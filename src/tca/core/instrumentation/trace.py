from dataclasses import dataclass, field


@dataclass(slots=True)
class TraceEvent:
    kind: str
    indices: tuple[int, ...] = ()
    values: tuple[object, ...] = ()
    data: dict[str, object] = field(default_factory=dict)


@dataclass
class Trace:
    events: list[TraceEvent] = field(default_factory=list)

    def add(
        self,
        kind: str,
        *,
        indices: tuple[int, ...] = (),
        values: tuple[object, ...] = (),
        **data,
    ) -> None:
        self.events.append(
            TraceEvent(
                kind=kind,
                indices=indices,
                values=values,
                data=data,
            )
        )

    def clear(self) -> None:
        self.events.clear()

    def __len__(self) -> int:
        return len(self.events)

    def __iter__(self):
        return iter(self.events)

from collections.abc import Callable, Sequence
from copy import deepcopy
from dataclasses import dataclass
from typing import TypeVar

StateT = TypeVar("StateT")
EventT = TypeVar("EventT")

Reducer = Callable[[StateT, EventT], StateT]
Snapshot = Callable[[StateT], StateT]


@dataclass(frozen=True, slots=True)
class ReplayFrame[StateT, EventT]:
    step: int
    state: StateT
    event: EventT | None


class Replay[StateT, EventT]:
    def __init__(
        self,
        initial_state: StateT,
        events: Sequence[EventT],
        reducer: Reducer,
        *,
        snapshot: Snapshot | None = None,
    ) -> None:
        snapshot_state = deepcopy if snapshot is None else snapshot

        self._events = tuple(events)
        self._frames: list[ReplayFrame[StateT, EventT]] = []
        self._position = 0

        state = snapshot_state(initial_state)

        self._frames.append(
            ReplayFrame(
                step=0,
                state=state,
                event=None,
            )
        )

        for step, event in enumerate(self._events, start=1):
            state = reducer(
                snapshot_state(state),
                event,
            )

            self._frames.append(
                ReplayFrame(
                    step=step,
                    state=state,
                    event=event,
                )
            )

    @property
    def current(self) -> ReplayFrame[StateT, EventT]:
        return self._frames[self._position]

    @property
    def frames(self) -> tuple[ReplayFrame[StateT, EventT], ...]:
        return tuple(self._frames)

    @property
    def state(self) -> StateT:
        return self.current.state

    @property
    def position(self) -> int:
        return self._position

    @property
    def total_steps(self) -> int:
        return len(self._events)

    @property
    def finished(self) -> bool:
        return self._position == self.total_steps

    def next(self) -> ReplayFrame[StateT, EventT]:
        if not self.finished:
            self._position += 1

        return self.current

    def previous(self) -> ReplayFrame[StateT, EventT]:
        if self._position > 0:
            self._position -= 1

        return self.current

    def seek(self, step: int) -> ReplayFrame[StateT, EventT]:
        if step < 0 or step > self.total_steps:
            raise IndexError(
                f"replay step {step} is out of range " f"[0, {self.total_steps}]"
            )

        self._position = step
        return self.current

    def reset(self) -> ReplayFrame[StateT, EventT]:
        self._position = 0
        return self.current

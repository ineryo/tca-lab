import pytest

from tca.core.replay import Replay


def test_replay_builds_frames():
    replay = Replay(
        initial_state=0,
        events=[1, 2, 3],
        reducer=lambda state, event: state + event,
    )

    assert replay.total_steps == 3

    assert replay.seek(0).state == 0
    assert replay.seek(1).state == 1
    assert replay.seek(2).state == 3
    assert replay.seek(3).state == 6


def test_replay_next():
    replay = Replay(
        initial_state=0,
        events=[10, 20],
        reducer=lambda state, event: state + event,
    )

    assert replay.position == 0
    assert replay.state == 0

    replay.next()

    assert replay.position == 1
    assert replay.state == 10

    replay.next()

    assert replay.position == 2
    assert replay.state == 30
    assert replay.finished


def test_replay_previous():
    replay = Replay(
        initial_state=0,
        events=[10, 20],
        reducer=lambda state, event: state + event,
    )

    replay.seek(2)
    replay.previous()

    assert replay.position == 1
    assert replay.state == 10


def test_replay_stops_at_boundaries():
    replay = Replay(
        initial_state=0,
        events=[10],
        reducer=lambda state, event: state + event,
    )

    replay.previous()

    assert replay.position == 0

    replay.next()
    replay.next()

    assert replay.position == 1
    assert replay.finished


def test_replay_rejects_invalid_seek():
    replay = Replay(
        initial_state=0,
        events=[10, 20],
        reducer=lambda state, event: state + event,
    )

    with pytest.raises(IndexError):
        replay.seek(-1)

    with pytest.raises(IndexError):
        replay.seek(3)


def test_replay_preserves_previous_mutable_states():
    initial_state = []

    def reducer(state, event):
        state.append(event)
        return state

    replay = Replay(
        initial_state=initial_state,
        events=["a", "b", "c"],
        reducer=reducer,
    )

    assert replay.seek(0).state == []
    assert replay.seek(1).state == ["a"]
    assert replay.seek(2).state == ["a", "b"]
    assert replay.seek(3).state == ["a", "b", "c"]

    assert initial_state == []

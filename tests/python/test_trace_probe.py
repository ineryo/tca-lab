from tca.core.instrumentation import Metrics, Trace
from tca.core.instrumentation.trace_probe import TraceProbe


def test_trace_probe_comparison():
    metrics = Metrics()
    trace = Trace()
    probe = TraceProbe(metrics, trace)

    result = probe.lt(2, 5, indices=(1, 3))

    assert result is True
    assert metrics.comparisons == 1

    event = trace.events[0]

    assert event.kind == "compare"
    assert event.indices == (1, 3)
    assert event.values == (2, 5)
    assert event.data == {"result": True}


def test_trace_probe_write():
    values = [3, 2, 1]
    metrics = Metrics()
    trace = Trace()
    probe = TraceProbe(metrics, trace)

    probe.write(values, 1, 7)

    assert values == [3, 7, 1]
    assert metrics.writes == 1

    event = trace.events[0]

    assert event.kind == "write"
    assert event.indices == (1,)
    assert event.values == (2, 7)


def test_trace_probe_swap():
    values = [3, 2, 1]
    metrics = Metrics()
    trace = Trace()
    probe = TraceProbe(metrics, trace)

    probe.swap(values, 0, 2)

    assert values == [1, 2, 3]
    assert metrics.swaps == 1
    assert metrics.writes == 2

    event = trace.events[0]

    assert event.kind == "swap"
    assert event.indices == (0, 2)
    assert event.values == (3, 1)


def test_trace_probe_ignores_self_swap():
    values = [3, 2, 1]
    metrics = Metrics()
    trace = Trace()
    probe = TraceProbe(metrics, trace)

    probe.swap(values, 1, 1)

    assert values == [3, 2, 1]
    assert metrics.swaps == 0
    assert metrics.writes == 0
    assert len(trace) == 0


def test_trace_probe_semantic_event():
    metrics = Metrics()
    trace = Trace()
    probe = TraceProbe(metrics, trace)

    probe.event(
        "choose_pivot",
        indices=(3,),
        values=(7,),
        start=0,
        end=5,
    )

    event = trace.events[0]

    assert event.kind == "choose_pivot"
    assert event.indices == (3,)
    assert event.values == (7,)
    assert event.data == {
        "start": 0,
        "end": 5,
    }

    assert metrics.comparisons == 0
    assert metrics.swaps == 0
    assert metrics.writes == 0


def test_trace_probe_comparison_roles():
    metrics = Metrics()
    trace = Trace()
    probe = TraceProbe(metrics, trace)

    probe.lt(
        2,
        5,
        indices=(3, 1),
        roles=("current", "marker"),
    )

    event = trace.events[0]

    assert event.data["roles"] == (
        "current",
        "marker",
    )

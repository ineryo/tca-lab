from tca.core.instrumentation.trace import Trace, TraceEvent


def test_trace_add_event():
    trace = Trace()

    trace.add(
        "compare",
        indices=(1, 3),
        values=(2.0, 5.0),
    )

    assert len(trace) == 1

    event = trace.events[0]

    assert event == TraceEvent(
        kind="compare",
        indices=(1, 3),
        values=(2.0, 5.0),
    )


def test_trace_add_semantic_data():
    trace = Trace()

    trace.add(
        "radix_pass",
        exponent=100,
    )

    event = trace.events[0]

    assert event.kind == "radix_pass"
    assert event.data == {"exponent": 100}


def test_trace_iteration():
    trace = Trace()

    trace.add("first")
    trace.add("second")

    assert [event.kind for event in trace] == ["first", "second"]


def test_trace_clear():
    trace = Trace()

    trace.add("compare")
    trace.add("swap")

    trace.clear()

    assert len(trace) == 0

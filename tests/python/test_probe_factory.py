from tca.core.instrumentation import (
    DirectProbe,
    Metrics,
    Probe,
    Trace,
    TraceProbe,
    make_probe,
)


def test_make_probe_direct():
    probe = make_probe()

    assert isinstance(probe, DirectProbe)


def test_make_probe_metrics():
    metrics = Metrics()

    probe = make_probe(metrics=metrics)

    assert isinstance(probe, Probe)
    assert probe.metrics is metrics


def test_make_probe_trace():
    trace = Trace()

    probe = make_probe(trace=trace)

    assert isinstance(probe, TraceProbe)
    assert probe.trace is trace


def test_make_probe_metrics_and_trace():
    metrics = Metrics()
    trace = Trace()

    probe = make_probe(metrics=metrics, trace=trace)

    assert isinstance(probe, TraceProbe)
    assert probe.metrics is metrics
    assert probe.trace is trace

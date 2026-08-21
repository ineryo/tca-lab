from .direct_probe import DirectProbe
from .metrics import Metrics
from .probe import Probe
from .trace import Trace
from .trace_probe import TraceProbe


def make_probe(
    metrics: Metrics | None = None,
    trace: Trace | None = None,
):
    if trace is not None:
        trace_metrics = Metrics() if metrics is None else metrics
        return TraceProbe(trace_metrics, trace)

    if metrics is not None:
        return Probe(metrics)

    return DirectProbe()

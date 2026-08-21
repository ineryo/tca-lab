import numpy as np
import plotly.graph_objects as go

from tca.algorithms.sorting._trace import SortTraceResult
from tca.algorithms.sorting.replay import SortingState, make_sorting_replay
from tca.core.instrumentation import TraceEvent


def visualize_sorting(
    result: SortTraceResult,
    *,
    title: str = "Sorting Replay",
    frame_duration_ms: int = 500,
    base_color: str = "#636EFA",
    active_color: str = "#EF553B",
    marker_color: str = "#00CC96",
    template: str = "plotly_white",
) -> go.Figure:
    replay = make_sorting_replay(result)

    frames = [
        _make_frame(
            frame,
            replay.total_steps,
            title=title,
            base_color=base_color,
            active_color=active_color,
            marker_color=marker_color,
        )
        for frame in replay.frames
    ]

    figure = go.Figure(
        data=frames[0].data,
        layout=frames[0].layout,
        frames=frames,
    )

    figure.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={
                "size": 12,
                "color": base_color,
                "symbol": "square",
            },
            name="Normal",
            hoverinfo="skip",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={
                "size": 12,
                "color": active_color,
                "symbol": "square",
            },
            name="Current / comparison",
            hoverinfo="skip",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker={
                "size": 12,
                "color": marker_color,
                "symbol": "square",
            },
            name="Marker / key / pivot",
            hoverinfo="skip",
        )
    )

    figure.update_layout(
        template=template,
        xaxis_title="Index",
        yaxis_title="Value",
        yaxis=_y_axis(result.initial_values),
        showlegend=True,
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": 1.15,
            "yanchor": "bottom",
        },
        margin=dict(l=60, r=30, t=190, b=100),
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "showactive": False,
                "x": 0,
                "y": -0.15,
                "buttons": [
                    {
                        "label": "▶ Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {
                                    "duration": frame_duration_ms,
                                    "redraw": True,
                                },
                                "transition": {"duration": 0},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    },
                    {
                        "label": "⏸ Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {
                                    "duration": 0,
                                    "redraw": False,
                                },
                                "transition": {"duration": 0},
                                "mode": "immediate",
                            },
                        ],
                    },
                ],
            }
        ],
        sliders=[
            {
                "active": 0,
                "x": 0.22,
                "len": 0.78,
                "y": -0.12,
                "currentvalue": {
                    "prefix": "Step ",
                    "visible": True,
                },
                "steps": [
                    {
                        "label": str(frame.step),
                        "method": "animate",
                        "args": [
                            [str(frame.step)],
                            {
                                "mode": "immediate",
                                "frame": {
                                    "duration": 0,
                                    "redraw": True,
                                },
                                "transition": {"duration": 0},
                            },
                        ],
                    }
                    for frame in replay.frames
                ],
            }
        ],
    )

    return figure


def _make_frame(
    frame,
    total_steps: int,
    *,
    title: str,
    base_color: str,
    active_color: str,
    marker_color: str,
) -> go.Frame:
    event = frame.event
    values = _display_values(frame.state)

    colors = _bar_colors(
        frame.state,
        event,
        len(values),
        base_color=base_color,
        active_color=active_color,
        marker_color=marker_color,
    )
    metrics = frame.state.metrics

    subtitle = (
        f"Step {frame.step}/{total_steps}"
        f" · {_event_description(event)}"
        f"<br>"
        f"comparisons={metrics.comparisons}"
        f" · swaps={metrics.swaps}"
        f" · writes={metrics.writes}"
    )

    bar = go.Bar(
        x=np.arange(len(values)),
        y=values,
        marker_color=colors,
        hovertemplate="index=%{x}<br>value=%{y}<extra></extra>",
        showlegend=False,
    )

    return go.Frame(
        name=str(frame.step),
        data=[bar],
        layout=go.Layout(
            title={
                "text": f"{title}<br><sup>{subtitle}</sup>",
                "x": 0.5,
                "xanchor": "center",
            },
            shapes=_frame_shapes(event),
            annotations=_frame_annotations(event),
        ),
    )


def _bar_colors(
    state: SortingState,
    event: TraceEvent | None,
    size: int,
    *,
    base_color: str,
    active_color: str,
    marker_color: str,
) -> list[str]:
    colors = [base_color] * size

    if state.radix_values is not None:
        for index, value in enumerate(state.radix_values):
            if value is not None:
                colors[index] = marker_color

    if event is None:
        return colors

    if event.kind == "write" and event.data.get("target") == "indices":
        for index in event.indices:
            if 0 <= index < size:
                colors[index] = active_color

        return colors

    if event.kind == "compare":
        roles = event.data.get("roles", ())

        for index, role in zip(event.indices, roles, strict=False):
            if not 0 <= index < size:
                continue

            if role in {"marker", "key", "pivot"}:
                colors[index] = marker_color
            else:
                colors[index] = active_color

        return colors

    if event.kind in {
        "select_minimum",
        "select_key",
        "choose_pivot",
    }:
        for index in event.indices:
            if 0 <= index < size:
                colors[index] = marker_color

        return colors

    for index in _active_indices(event, size):
        colors[index] = active_color

    return colors


def _display_values(
    state: SortingState,
) -> np.ndarray:
    if state.radix_values is None:
        return state.values

    base_values = (
        state.radix_base_values if state.radix_base_values is not None else state.values
    )

    displayed_values = [
        radix_value if radix_value is not None else base_values[index]
        for index, radix_value in enumerate(state.radix_values)
    ]

    return np.asarray(
        displayed_values,
        dtype=float,
    )


def _active_indices(
    event: TraceEvent | None,
    size: int,
) -> set[int]:
    if event is None:
        return set()

    if event.kind == "merge_range":
        start, _, end = event.indices
        return set(range(start, min(end, size)))

    if event.kind == "partition":
        start, _, end = event.indices
        return set(range(start, min(end + 1, size)))

    if event.kind == "radix_pass":
        return set(range(size))

    if event.kind == "write":
        target = event.data.get("target")

        if target not in {None, "values"}:
            return set()

    return {index for index in event.indices if 0 <= index < size}


def _event_description(
    event: TraceEvent | None,
) -> str:
    if event is None:
        return "initial state"

    if event.kind == "compare":
        roles = event.data.get("roles", ())

        if len(roles) == len(event.indices):
            operands = ", ".join(
                f"{role}={index}"
                for role, index in zip(roles, event.indices, strict=True)
            )
            return f"compare: {operands}"

        return f"compare {event.indices}"

    if event.kind == "swap":
        return f"swap {event.indices}"

    if event.kind == "write":
        target = event.data.get("target", "values")

        if target == "indices":
            position = event.indices[0]
            source = event.values[-1]

            return f"place source={source} → position={position}"

        return f"write {event.indices} → {target}"

    if event.kind == "select_minimum":
        return f"minimum → {event.indices[0]}"

    if event.kind == "select_key":
        return f"key → {event.indices[0]}"

    if event.kind == "choose_pivot":
        pivot = event.indices[0]
        start = event.data["start"]
        end = event.data["end"]
        return f"choose pivot={pivot} in [{start}:{end}]"

    if event.kind == "merge_range":
        start, middle, end = event.indices
        return f"merge [{start}:{middle}) + [{middle}:{end})"

    if event.kind == "partition":
        start, pivot, end = event.indices
        return f"partition [{start}:{end}], pivot={pivot}"

    if event.kind == "radix_pass":
        return f"radix pass exponent={event.data['exponent']}"

    return event.kind.replace("_", " ")


def _y_axis(values: np.ndarray) -> dict:
    if len(values) == 0:
        return {}

    minimum = float(np.min(values))
    maximum = float(np.max(values))

    span = max(maximum - minimum, 1.0)
    padding = 0.1 * span

    return {
        "range": [
            min(0.0, minimum) - padding,
            max(0.0, maximum) + padding,
        ]
    }


def _frame_shapes(
    event: TraceEvent | None,
) -> list[dict]:
    if event is None:
        return []

    if event.kind == "merge_range":
        start, middle, end = event.indices

        return [
            {
                "type": "rect",
                "xref": "x",
                "yref": "paper",
                "x0": start - 0.5,
                "x1": middle - 0.5,
                "y0": 0,
                "y1": 1,
                "fillcolor": "rgba(99, 110, 250, 0.12)",
                "line": {"width": 0},
                "layer": "below",
            },
            {
                "type": "rect",
                "xref": "x",
                "yref": "paper",
                "x0": middle - 0.5,
                "x1": end - 0.5,
                "y0": 0,
                "y1": 1,
                "fillcolor": "rgba(0, 204, 150, 0.12)",
                "line": {"width": 0},
                "layer": "below",
            },
        ]

    if event.kind == "choose_pivot":
        (pivot,) = event.indices
        start = event.data["start"]
        end = event.data["end"]

        return [
            {
                "type": "rect",
                "xref": "x",
                "yref": "paper",
                "x0": start - 0.5,
                "x1": end + 0.5,
                "y0": 0,
                "y1": 1,
                "fillcolor": "rgba(239, 85, 59, 0.10)",
                "line": {"width": 1, "color": "rgba(239, 85, 59, 0.35)"},
                "layer": "below",
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "paper",
                "x0": pivot,
                "x1": pivot,
                "y0": 0,
                "y1": 1,
                "line": {
                    "color": "rgba(0, 204, 150, 0.9)",
                    "width": 2,
                    "dash": "dash",
                },
                "layer": "above",
            },
        ]

    if event.kind == "partition":
        start, pivot, end = event.indices

        return [
            {
                "type": "rect",
                "xref": "x",
                "yref": "paper",
                "x0": start - 0.5,
                "x1": end + 0.5,
                "y0": 0,
                "y1": 1,
                "fillcolor": "rgba(239, 85, 59, 0.10)",
                "line": {"width": 1, "color": "rgba(239, 85, 59, 0.35)"},
                "layer": "below",
            },
            {
                "type": "line",
                "xref": "x",
                "yref": "paper",
                "x0": pivot,
                "x1": pivot,
                "y0": 0,
                "y1": 1,
                "line": {
                    "color": "rgba(0, 204, 150, 0.9)",
                    "width": 2,
                    "dash": "dash",
                },
                "layer": "above",
            },
        ]

    return []


def _frame_annotations(
    event: TraceEvent | None,
) -> list[dict]:
    if event is None:
        return []

    if event.kind == "merge_range":
        start, middle, end = event.indices

        left_x = (start + middle - 1) / 2 if middle > start else start
        right_x = (middle + end - 1) / 2 if end > middle else middle

        return [
            {
                "xref": "x",
                "yref": "paper",
                "x": left_x,
                "y": 1.08,
                "text": f"L [{start}:{middle})",
                "showarrow": False,
                "font": {"size": 11, "color": "#636EFA"},
            },
            {
                "xref": "x",
                "yref": "paper",
                "x": right_x,
                "y": 1.08,
                "text": f"R [{middle}:{end})",
                "showarrow": False,
                "font": {"size": 11, "color": "#00CC96"},
            },
        ]

    if event.kind == "choose_pivot":
        (pivot,) = event.indices
        start = event.data["start"]
        end = event.data["end"]

        return [
            {
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 1.08,
                "text": f"active partition [{start}:{end}] · pivot at index {pivot}",
                "showarrow": False,
                "font": {"size": 11, "color": "#444"},
            }
        ]

    if event.kind == "partition":
        start, pivot, end = event.indices

        return [
            {
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 1.08,
                "text": f"active partition [{start}:{end}] · pivot at index {pivot}",
                "showarrow": False,
                "font": {"size": 11, "color": "#444"},
            }
        ]

    return []

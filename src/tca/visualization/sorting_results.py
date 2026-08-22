from collections.abc import Mapping, Sequence

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def visualize_sorting_results(
    data: pd.DataFrame,
    *,
    algorithms: Sequence[str],
    families: Sequence[str],
    labels: Mapping[str, str],
    colors: Mapping[str, str],
) -> go.Figure:
    panels = (
        ("elapsed_seconds", "Tempo médio", "s", True, None),
        ("peak_memory_mb", "Pico médio de memória", "MiB", False, None),
        ("comparisons", "Comparações médias", "operações", True, None),
        ("swaps", "Trocas médias", "operações", True, None),
        ("writes", "Escritas médias", "operações", True, None),
        (
            "elapsed_seconds",
            "Quick Classic × Quick Smarter",
            "s",
            True,
            {"quick_classic", "quick_smarter"},
        ),
    )

    figure = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=[panel[1] for panel in panels],
        horizontal_spacing=0.10,
        vertical_spacing=0.13,
    )

    trace_families = []

    for panel_index, (value, _, _, log_y, algorithm_filter) in enumerate(panels):
        row = panel_index // 2 + 1
        col = panel_index % 2 + 1

        panel_algorithms = [
            algorithm
            for algorithm in algorithms
            if algorithm_filter is None or algorithm in algorithm_filter
        ]

        for family in families:
            for algorithm in panel_algorithms:
                for backend, dash in (("python", "solid"), ("cpp", "dash")):
                    series = data.loc[
                        (data["family"] == family)
                        & (data["algorithm"] == algorithm)
                        & (data["backend"] == backend)
                    ].sort_values("n")

                    if log_y:
                        series = series.loc[series[value] > 0]
                    else:
                        series = series.loc[series[value].notna()]

                    if series.empty:
                        continue

                    figure.add_trace(
                        go.Scatter(
                            x=series["n"],
                            y=series[value],
                            mode="lines+markers",
                            name=f"{labels[algorithm]} · {backend.upper()}",
                            legendgroup=f"{algorithm}-{backend}",
                            showlegend=panel_index == 0,
                            line={
                                "color": colors[algorithm],
                                "dash": dash,
                            },
                            visible=family == families[0],
                            hovertemplate=(
                                "n=%{x:,}<br>"
                                "%{y:.4g}<br>"
                                f"{family}"
                                "<extra>%{fullData.name}</extra>"
                            ),
                        ),
                        row=row,
                        col=col,
                    )

                    trace_families.append(family)

        figure.update_xaxes(
            title_text="n",
            type="log",
            row=row,
            col=col,
        )

        figure.update_yaxes(
            title_text=panels[panel_index][2],
            type="log" if log_y else "linear",
            row=row,
            col=col,
        )

    buttons = [
        {
            "label": family,
            "method": "update",
            "args": [
                {
                    "visible": [
                        trace_family == family for trace_family in trace_families
                    ]
                },
                {"title": f"Resultados — {family}"},
            ],
        }
        for family in families
    ]

    figure.update_layout(
        title=f"Resultados — {families[0]}",
        template="plotly_white",
        height=1100,
        margin={"l": 65, "r": 35, "t": 125, "b": 100},
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.06,
            "yanchor": "top",
        },
        legend_groupclick="togglegroup",
        updatemenus=[
            {
                "buttons": buttons,
                "direction": "down",
                "x": 1.0,
                "xanchor": "right",
                "y": 1.08,
                "yanchor": "bottom",
            }
        ],
    )

    return figure

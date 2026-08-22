import json
from collections.abc import Mapping, Sequence
from uuid import uuid4

import numpy as np
import plotly.io as pio

from tca.algorithms.sorting import trace_sort
from tca.visualization.sorting import visualize_sorting


def visualize_sorting_comparison(
    values: np.ndarray,
    *,
    methods: Sequence[str],
    labels: Mapping[str, str] | None = None,
    frame_duration_ms: int = 140,
) -> str:
    labels = labels or {}

    figures = [
        visualize_sorting(
            trace_sort(values.copy(), method=method),
            title=labels.get(method, method),
            frame_duration_ms=frame_duration_ms,
        )
        for method in methods
    ]

    for figure in figures:
        figure.update_layout(
            height=330,
            margin={"l": 40, "r": 20, "t": 55, "b": 35},
            showlegend=False,
            updatemenus=[],
            sliders=[],
        )

    suffix = uuid4().hex
    plot_ids = [f"sorting-{index}-{suffix}" for index in range(len(figures))]

    frame_names = [[frame.name for frame in figure.frames] for figure in figures]

    max_steps = max(map(len, frame_names))

    plots = [
        pio.to_html(
            figure,
            full_html=False,
            include_plotlyjs=index == 0,
            auto_play=False,
            div_id=plot_id,
        )
        for index, (figure, plot_id) in enumerate(zip(figures, plot_ids, strict=True))
    ]

    return f"""
<div style="margin: 4px 0 8px;">
  <button id="play-{suffix}">Play</button>
  <button id="pause-{suffix}">Pause</button>
  <button id="reset-{suffix}">Reset</button>
</div>

<div style="
    display:grid;
    grid-template-columns:repeat(2, minmax(0, 1fr));
    gap:6px 10px;
">
  {"".join(plots)}
</div>

<script>
(() => {{
  const plotIds = {json.dumps(plot_ids)};
  const frameNames = {json.dumps(frame_names)};
  const maxSteps = {max_steps};
  const duration = {frame_duration_ms};

  let step = 0;
  let timer = null;

  const showStep = () => {{
    plotIds.forEach((plotId, index) => {{
      const names = frameNames[index];
      const frame = names[Math.min(step, names.length - 1)];

      Plotly.animate(
        document.getElementById(plotId),
        [frame],
        {{
          mode: "immediate",
          frame: {{duration: 0, redraw: true}},
          transition: {{duration: 0}},
        }}
      );
    }});
  }};

  const pause = () => {{
    if (timer !== null) {{
      clearTimeout(timer);
      timer = null;
    }}
  }};

  const tick = () => {{
    if (step >= maxSteps - 1) {{
      pause();
      return;
    }}

    step += 1;
    showStep();
    timer = setTimeout(tick, duration);
  }};

  document.getElementById("play-{suffix}").onclick = () => {{
    if (timer === null) {{
      timer = setTimeout(tick, duration);
    }}
  }};

  document.getElementById("pause-{suffix}").onclick = pause;

  document.getElementById("reset-{suffix}").onclick = () => {{
    pause();
    step = 0;
    showStep();
  }};

  showStep();
}})();
</script>
"""

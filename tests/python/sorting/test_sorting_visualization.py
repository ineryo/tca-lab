import numpy as np
import pytest

from tca.algorithms.sorting import (
    available_sorting_algorithms,
    trace_sort,
)
from tca.visualization import visualize_sorting

METHODS = available_sorting_algorithms()


@pytest.mark.parametrize("method", METHODS)
def test_visualize_sorting_builds_all_frames(method):
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method=method,
    )

    figure = visualize_sorting(result)

    assert len(figure.frames) == len(result.trace.events) + 1

    np.testing.assert_array_equal(
        figure.frames[-1].data[0].y,
        result.final_values,
    )


def test_visualize_sorting_has_animation_controls():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="selection",
    )

    figure = visualize_sorting(result)

    assert len(figure.layout.sliders) == 1
    assert len(figure.layout.updatemenus) == 1

    labels = [button.label for button in figure.layout.updatemenus[0].buttons]

    assert labels == [
        "▶ Play",
        "⏸ Pause",
    ]


def test_visualize_selection_distinguishes_current_and_marker():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="selection",
    )

    figure = visualize_sorting(result)

    compare_frame = next(
        frame
        for frame in figure.frames
        if frame.data and "compare:" in frame.layout.title.text
    )

    colors = list(compare_frame.data[0].marker.color)

    event_step = int(compare_frame.name)
    event = result.trace.events[event_step - 1]

    current, marker = event.indices

    assert colors[current] != colors[marker]


def test_visualize_sorting_has_color_legend():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="selection",
    )

    figure = visualize_sorting(result)

    legend_names = [trace.name for trace in figure.data if trace.name is not None]

    assert legend_names == [
        "Normal",
        "Current / comparison",
        "Marker / key / pivot",
    ]


def test_visualize_sorting_hides_main_bar_from_legend():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="selection",
    )

    figure = visualize_sorting(result)

    assert figure.data[0].showlegend is False


def test_visualize_merge_has_range_shapes():
    values = np.array(
        [8, 7, 6, 5],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="merge",
    )

    figure = visualize_sorting(result)

    merge_frame = next(
        frame
        for frame in figure.frames
        if frame.layout.title is not None and "merge [" in frame.layout.title.text
    )

    assert len(merge_frame.layout.shapes) == 2
    assert len(merge_frame.layout.annotations) == 2


def test_visualize_quick_has_partition_shapes():
    values = np.array(
        [3, 1, 2],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="quick",
    )

    figure = visualize_sorting(result)

    partition_frame = next(
        frame
        for frame in figure.frames
        if frame.layout.title is not None and "partition [" in frame.layout.title.text
    )

    assert len(partition_frame.layout.shapes) >= 2
    assert len(partition_frame.layout.annotations) >= 1


def test_visualize_radix_shows_partial_counting_output():
    values = np.array(
        [92.0, 12.0, 18.0, 15.0],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="radix",
    )

    figure = visualize_sorting(result)

    radix_write_frames = [
        frame
        for frame in figure.frames
        if frame.layout.title is not None and "place source=" in frame.layout.title.text
    ]

    write_frame = radix_write_frames[1]

    displayed_values = list(write_frame.data[0].y)
    colors = list(write_frame.data[0].marker.color)

    assert all(value is not None for value in displayed_values)
    assert "#EF553B" in colors
    assert "#00CC96" in colors


def test_visualize_radix_next_pass_keeps_previous_pass_as_base():
    values = np.array(
        [92.0, 15.0, 18.0, 12.0],
        dtype=np.float64,
    )

    result = trace_sort(
        values,
        method="radix",
    )

    figure = visualize_sorting(result)

    radix_frames = [
        frame
        for frame in figure.frames
        if frame.layout.title is not None and "place source=" in frame.layout.title.text
    ]

    assert len(radix_frames) > len(values)

    first_pass_last = radix_frames[len(values) - 1]
    second_pass_first = radix_frames[len(values)]

    previous_values = list(first_pass_last.data[0].y)
    next_values = list(second_pass_first.data[0].y)

    # Ao iniciar a próxima passada, apenas uma posição deve ter sido
    # reconstruída; as demais continuam mostrando a passada anterior.
    matching_positions = sum(
        previous == current
        for previous, current in zip(
            previous_values,
            next_values,
            strict=True,
        )
    )

    assert matching_positions >= len(values) - 1

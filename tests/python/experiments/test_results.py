import json

import pytest

from tca.experiments import (
    SortingCase,
    SortingResult,
    append_sorting_result,
    load_sorting_results,
)


def make_case() -> SortingCase:
    return SortingCase(
        n=1000,
        family="uniform_random",
        repetition=2,
        seed=44,
    )


def test_sorting_result_to_dict_is_flat():
    result = SortingResult(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="metrics",
        comparisons=100,
        swaps=0,
        writes=200,
    )

    data = result.to_dict()

    assert data == {
        "n": 1000,
        "family": "uniform_random",
        "repetition": 2,
        "seed": 44,
        "algorithm": "merge",
        "backend": "python",
        "mode": "metrics",
        "elapsed_seconds": None,
        "comparisons": 100,
        "swaps": 0,
        "writes": 200,
        "peak_memory_bytes": None,
        "status": "ok",
        "message": None,
    }


def test_sorting_result_round_trip_dict():
    original = SortingResult(
        case=make_case(),
        algorithm="quick",
        backend="cpp",
        mode="time",
        elapsed_seconds=0.0123,
    )

    restored = SortingResult.from_dict(original.to_dict())

    assert restored == original


def test_sorting_result_accepts_incomplete_future_measurements():
    result = SortingResult(
        case=make_case(),
        algorithm="radix",
        backend="python",
        mode="normal",
    )

    assert result.elapsed_seconds is None
    assert result.comparisons is None
    assert result.swaps is None
    assert result.writes is None
    assert result.peak_memory_bytes is None


def test_sorting_result_rejects_unknown_status():
    with pytest.raises(
        ValueError,
        match="unknown result status",
    ):
        SortingResult(
            case=make_case(),
            algorithm="merge",
            backend="python",
            mode="metrics",
            status="unknown",
        )


def test_append_and_load_sorting_result(tmp_path):
    path = tmp_path / "results.jsonl"

    result = SortingResult(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="metrics",
        comparisons=100,
        swaps=0,
        writes=200,
    )

    append_sorting_result(
        path,
        result,
    )

    loaded = load_sorting_results(path)

    assert loaded == (result,)


def test_append_sorting_result_preserves_existing_results(
    tmp_path,
):
    path = tmp_path / "results.jsonl"

    first = SortingResult(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="time",
        elapsed_seconds=0.01,
    )

    second = SortingResult(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="metrics",
        comparisons=100,
        swaps=0,
        writes=200,
    )

    append_sorting_result(
        path,
        first,
    )

    append_sorting_result(
        path,
        second,
    )

    assert load_sorting_results(path) == (
        first,
        second,
    )


def test_append_sorting_result_creates_parent_directory(
    tmp_path,
):
    path = tmp_path / "nested" / "results.jsonl"

    result = SortingResult(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="normal",
    )

    append_sorting_result(
        path,
        result,
    )

    assert path.exists()


def test_load_sorting_results_returns_empty_for_missing_file(
    tmp_path,
):
    path = tmp_path / "missing.jsonl"

    assert load_sorting_results(path) == ()


def test_load_sorting_results_ignores_blank_lines(
    tmp_path,
):
    path = tmp_path / "results.jsonl"

    result = SortingResult(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="normal",
    )

    path.write_text(
        "\n" + json.dumps(result.to_dict()) + "\n\n",
        encoding="utf-8",
    )

    assert load_sorting_results(path) == (result,)


def test_load_sorting_results_reports_invalid_json_line(
    tmp_path,
):
    path = tmp_path / "results.jsonl"

    valid_result = SortingResult(
        case=make_case(),
        algorithm="merge",
        backend="python",
        mode="normal",
    )

    path.write_text(
        json.dumps(valid_result.to_dict()) + "\n" + "invalid-json\n",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="invalid JSON on line 2",
    ):
        load_sorting_results(path)

import pytest

from src.evaluation.metrics import (
    calculate_average_latency,
    calculate_local_resource_usage,
    calculate_render_success_rate,
    calculate_route_accuracy,
    build_benchmark_summary,
)


def test_route_accuracy():
    selected = [
        "ltx-video",
        "wan2.1",
        "ltx-video",
        "wan2.1",
    ]

    expected = [
        "ltx-video",
        "wan2.1",
        "wan2.1",
        "wan2.1",
    ]

    accuracy = calculate_route_accuracy(
        selected,
        expected,
    )

    assert accuracy == 0.75


def test_render_success_rate():
    rate = calculate_render_success_rate(
        successful_renders=9,
        total_renders=10,
    )

    assert rate == 0.9


def test_average_latency():
    latency = calculate_average_latency(
        [10.0, 20.0, 30.0]
    )

    assert latency == 20.0


def test_resource_usage():
    usage = calculate_local_resource_usage(
        peak_ram_gb=4.5,
        accelerator_time_seconds=19.0,
    )

    assert usage["peak_ram_gb"] == 4.5
    assert usage["accelerator_time_seconds"] == 19.0


def test_benchmark_summary():
    summary = build_benchmark_summary(
        total_briefs=4,
        successful_renders=4,
        selected_models=[
            "ltx-video",
            "wan2.1",
            "ltx-video",
            "wan2.1",
        ],
        expected_models=[
            "ltx-video",
            "wan2.1",
            "wan2.1",
            "wan2.1",
        ],
        runtimes=[
            10.0,
            20.0,
            15.0,
            25.0,
        ],
    )

    assert summary["total_briefs"] == 4
    assert summary["successful_renders"] == 4
    assert summary["render_success_rate"] == 1.0
    assert summary["route_accuracy"] == 0.75
    assert summary["average_latency_seconds"] == 17.5


def test_invalid_runtime():
    with pytest.raises(ValueError):
        calculate_average_latency([])


def test_invalid_render_count():
    with pytest.raises(ValueError):
        calculate_render_success_rate(
            successful_renders=11,
            total_renders=10,
        )
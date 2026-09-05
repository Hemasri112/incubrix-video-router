from src.router.fallback import (
    choose_fallback,
    handle_generation_failure,
)


def test_model_fallback():
    candidates = [
        {"model": "wan2.1", "score": 14},
        {"model": "ltx-video", "score": 13},
        {"model": "cogvideox", "score": 12},
    ]

    result = choose_fallback(
        primary_model="wan2.1",
        candidates=candidates,
    )

    assert result["fallback_type"] == "model"
    assert result["selected_model"] == "ltx-video"


def test_cpu_fallback_when_no_model_available():
    result = choose_fallback(
        primary_model="wan2.1",
        candidates=[
            {"model": "wan2.1", "score": 14},
        ],
    )

    assert result["fallback_type"] == "cpu_assembly"
    assert result["selected_model"] is None


def test_generation_failure_is_recorded():
    candidates = [
        {"model": "wan2.1", "score": 14},
        {"model": "ltx-video", "score": 13},
    ]

    result = handle_generation_failure(
        primary_model="wan2.1",
        candidates=candidates,
        error="Generation timed out.",
    )

    assert result["status"] == "fallback"
    assert result["primary_model"] == "wan2.1"
    assert result["error"] == "Generation timed out."
    assert result["selected_model"] == "ltx-video"


def test_missing_asset_uses_cpu_fallback():
    result = handle_generation_failure(
        primary_model="ltx-video",
        candidates=[
            {"model": "ltx-video", "score": 13},
        ],
        error="Generated asset is missing.",
    )

    assert result["status"] == "fallback"
    assert result["fallback_type"] == "cpu_assembly"
    assert result["selected_model"] is None
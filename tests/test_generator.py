import pytest

from src.generators.ltx_generator import LTXVideoGenerator


def test_ltx_generator_success():
    generator = LTXVideoGenerator(
        model_path="free-compute-model"
    )

    result = generator.generate(
        prompt="A clean educational video about Python programming.",
        output_path="outputs/captioned_test.mp4",
        seed=42,
        runtime_seconds=19.0,
    )

    assert result["status"] == "success"
    assert result["generator"] == "ltx-video"
    assert result["model"] == "LTX-Video 2B distilled"
    assert result["model_revision"] == (
        "ltxv-2b-0.9.6-distilled-04-25"
    )
    assert result["seed"] == 42
    assert result["runtime_seconds"] == 19.0
    assert result["runtime_type"] == "measured"


def test_ltx_generator_missing_output():
    generator = LTXVideoGenerator(
        model_path="free-compute-model"
    )

    with pytest.raises(FileNotFoundError):
        generator.generate(
            prompt="Test prompt",
            output_path="outputs/missing_ltx_video.mp4",
            seed=42,
        )


def test_ltx_generator_rejects_non_mp4():
    generator = LTXVideoGenerator(
        model_path="free-compute-model"
    )

    with pytest.raises(ValueError):
        generator.generate(
            prompt="Test prompt",
            output_path="outputs/timeline.json",
            seed=42,
        )
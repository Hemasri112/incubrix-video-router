from pathlib import Path

from src.validation.validator import validate_output


def test_valid_video():
    video_path = Path("outputs/test_video.mp4")

    result = validate_output(
        str(video_path),
        expected_duration=5,
    )

    assert result["valid"] is True
    assert result["checks"]["file_exists"] is True
    assert result["checks"]["non_empty"] is True
    assert result["checks"]["mp4_format"] is True
    assert result["checks"]["duration_readable"] is True
    assert result["checks"]["duration_matches"] is True


def test_missing_video():
    result = validate_output(
        "outputs/does_not_exist.mp4"
    )

    assert result["valid"] is False
    assert "Video file does not exist." in result["errors"]


def test_timeline_and_captions():
    video_path = Path("outputs/test_video.mp4")

    result = validate_output(
        str(video_path),
        expected_duration=5,
        captions_path="outputs/captions.srt",
        timeline_path="outputs/timeline.json",
    )

    assert result["valid"] is True
    assert result["checks"]["captions_present"] is True
    assert result["checks"]["timeline_present"] is True
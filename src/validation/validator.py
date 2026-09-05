from pathlib import Path
from typing import Dict, Optional


def validate_output(
    video_path: str,
    expected_duration: Optional[float] = None,
    captions_path: Optional[str] = None,
    timeline_path: Optional[str] = None,
) -> Dict:
    """
    Validate a generated video and its supporting files.

    Checks:
    - video exists
    - video is an MP4
    - video is not empty
    - expected duration is approximately correct
    - captions file exists when provided
    - timeline file exists when provided
    """

    video = Path(video_path)

    result = {
        "valid": True,
        "video": {
            "path": str(video),
            "exists": video.exists(),
            "format": video.suffix.lower(),
            "file_size_bytes": 0,
        },
        "checks": {},
        "errors": [],
    }

    # Check video existence
    if not video.exists():
        result["valid"] = False
        result["errors"].append("Video file does not exist.")
        return result

    result["video"]["file_size_bytes"] = video.stat().st_size

    # Check file size
    if video.stat().st_size == 0:
        result["valid"] = False
        result["errors"].append("Video file is empty.")

    # Check format
    if video.suffix.lower() != ".mp4":
        result["valid"] = False
        result["errors"].append("Video output must be an MP4 file.")

    result["checks"]["file_exists"] = video.exists()
    result["checks"]["non_empty"] = video.stat().st_size > 0
    result["checks"]["mp4_format"] = video.suffix.lower() == ".mp4"

    # Check duration using FFprobe
    duration = _get_duration(video)

    result["video"]["duration_seconds"] = duration

    if duration is None:
        result["valid"] = False
        result["errors"].append(
            "Unable to read video duration using FFprobe."
        )
        result["checks"]["duration_readable"] = False
    else:
        result["checks"]["duration_readable"] = True

        if expected_duration is not None:
            tolerance = 0.5

            duration_matches = abs(
                duration - expected_duration
            ) <= tolerance

            result["checks"]["duration_matches"] = duration_matches

            if not duration_matches:
                result["valid"] = False
                result["errors"].append(
                    f"Expected duration {expected_duration}s, "
                    f"but video duration is {duration}s."
                )

    # Check captions
    if captions_path is not None:
        captions = Path(captions_path)
        captions_valid = (
            captions.exists()
            and captions.stat().st_size > 0
        )

        result["checks"]["captions_present"] = captions_valid

        if not captions_valid:
            result["valid"] = False
            result["errors"].append(
                "Caption file is missing or empty."
            )

    # Check timeline
    if timeline_path is not None:
        timeline = Path(timeline_path)
        timeline_valid = (
            timeline.exists()
            and timeline.stat().st_size > 0
        )

        result["checks"]["timeline_present"] = timeline_valid

        if not timeline_valid:
            result["valid"] = False
            result["errors"].append(
                "Timeline file is missing or empty."
            )

    return result


def _get_duration(video_path: Path) -> Optional[float]:
    """
    Read video duration using FFprobe.
    """

    import subprocess

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        return round(float(completed.stdout.strip()), 3)

    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        ValueError,
    ):
        return None
import subprocess
from pathlib import Path
from typing import List


def run_ffmpeg(command: List[str]) -> None:
    """Run an FFmpeg command and raise an error if it fails."""

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg failed:\n" + result.stderr[-3000:]
        )


def create_test_video(
    output_path: str,
    duration: int = 5,
    aspect_ratio: str = "16:9",
) -> Path:
    """Create a simple video to verify FFmpeg integration."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if aspect_ratio == "16:9":
        resolution = "1280x720"
    elif aspect_ratio == "9:16":
        resolution = "720x1280"
    else:
        raise ValueError(
            f"Unsupported aspect ratio: {aspect_ratio}"
        )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=black:s={resolution}:r=24",
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output),
    ]

    run_ffmpeg(command)

    return output


def concatenate_clips(
    clip_paths: List[str],
    output_path: str,
) -> Path:
    """Concatenate multiple compatible MP4 clips."""

    if not clip_paths:
        raise ValueError("No video clips were provided.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    concat_file = output.parent / "concat_list.txt"

    with open(concat_file, "w", encoding="utf-8") as file:
        for clip in clip_paths:
            path = Path(clip)

            if not path.exists():
                raise FileNotFoundError(
                    f"Video clip not found: {path}"
                )

            file.write(
                f"file '{path.resolve().as_posix()}'\n"
            )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        str(output),
    ]

    run_ffmpeg(command)

    concat_file.unlink(missing_ok=True)

    return output


def convert_aspect_ratio(
    input_path: str,
    output_path: str,
    aspect_ratio: str,
) -> Path:
    """Convert a video to 16:9 or 9:16 using center cropping."""

    input_file = Path(input_path)
    output = Path(output_path)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input video not found: {input_file}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    if aspect_ratio == "16:9":
        width, height = 1280, 720
    elif aspect_ratio == "9:16":
        width, height = 720, 1280
    else:
        raise ValueError(
            f"Unsupported aspect ratio: {aspect_ratio}"
        )

    filter_expression = (
        f"scale={width}:{height}:"
        "force_original_aspect_ratio=increase,"
        f"crop={width}:{height}"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
        "-vf",
        filter_expression,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        str(output),
    ]

    run_ffmpeg(command)

    return output


def burn_captions(
    input_path: str,
    subtitle_path: str,
    output_path: str,
) -> Path:
    """Burn an SRT subtitle file permanently into an MP4."""

    input_file = Path(input_path)
    subtitles = Path(subtitle_path)
    output = Path(output_path)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input video not found: {input_file}"
        )

    if not subtitles.exists():
        raise FileNotFoundError(
            f"Subtitle file not found: {subtitles}"
        )

    output.parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg subtitle filters treat ':' specially.
    # Escape the Windows drive-letter colon.
    subtitle_path_ffmpeg = (
        subtitles.resolve()
        .as_posix()
        .replace(":", r"\:")
    )

    subtitle_filter = (
        f"subtitles='{subtitle_path_ffmpeg}'"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
        "-vf",
        subtitle_filter,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        str(output),
    ]

    run_ffmpeg(command)

    return output


def get_video_duration(video_path: str) -> float:
    """Return the duration of a video in seconds."""

    path = Path(video_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Video not found: {path}"
        )

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )

    return float(result.stdout.strip())


def validate_video_file(video_path: str) -> dict:
    """Perform basic validation of an MP4 video."""

    path = Path(video_path)

    if not path.exists():
        return {
            "valid": False,
            "reason": "file_not_found",
        }

    if path.stat().st_size == 0:
        return {
            "valid": False,
            "reason": "empty_file",
        }

    try:
        duration = get_video_duration(str(path))
    except Exception as error:
        return {
            "valid": False,
            "reason": "ffprobe_failed",
            "error": str(error),
        }

    return {
        "valid": duration > 0,
        "duration_seconds": round(duration, 3),
        "file_size_bytes": path.stat().st_size,
        "format": "mp4",
    }
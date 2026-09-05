import subprocess
from pathlib import Path
from typing import Dict, List


WORKFLOW_VISUALS = {
    "education": {
        "background": "0x17324D",
        "accent": "0x4FC3F7",
    },
    "news": {
        "background": "0x3A1111",
        "accent": "0xFF5252",
    },
    "product": {
        "background": "0x24113D",
        "accent": "0xCE93D8",
    },
}


def _get_resolution(aspect_ratio: str) -> str:
    """Return the video resolution for the requested aspect ratio."""

    if aspect_ratio == "16:9":
        return "1280x720"

    if aspect_ratio == "9:16":
        return "720x1280"

    raise ValueError(
        f"Unsupported aspect ratio: {aspect_ratio}"
    )


def _run_ffmpeg(command: List[str]) -> None:
    """Run FFmpeg and raise an error if it fails."""

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg failed:\n"
            + result.stderr[-3000:]
        )


def create_workflow_video(
    use_case: str,
    scene_plan: List[Dict],
    output_path: str,
    aspect_ratio: str,
) -> Path:
    """
    Create a visually differentiated workflow video.

    Education, news and product workflows use different
    visual treatments and scene pacing.

    This is a local CPU/FFmpeg assembly stage.
    It does not claim that an AI model generated the video.
    """

    use_case = use_case.lower()

    if use_case not in WORKFLOW_VISUALS:
        raise ValueError(
            f"Unsupported workflow: {use_case}"
        )

    if not scene_plan:
        raise ValueError(
            "Scene plan cannot be empty."
        )

    output = Path(output_path)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resolution = _get_resolution(aspect_ratio)
    settings = WORKFLOW_VISUALS[use_case]

    scene_files = []

    try:
        for scene in scene_plan:
            scene_id = scene["scene_id"]
            duration = float(scene["duration"])

            scene_path = (
                output.parent
                / f".{use_case}_scene_{scene_id}.mp4"
            )

            # Different workflows use different visual motion.
            if use_case == "education":
                video_filter = (
                    "scale=1280:720,"
                    "zoompan="
                    "z='min(zoom+0.0015,1.08)':"
                    "d=1:"
                    "s=1280x720:"
                    "fps=24"
                )

            elif use_case == "news":
                video_filter = (
                    "scale=1280:720,"
                    "crop=1280:720,"
                    "hflip"
                )

            else:
                video_filter = (
                    "scale=1280:720,"
                    "crop=1280:720,"
                    "transpose=clock"
                )

            # Use a simple generated background.
            # No drawtext is used, so Windows font configuration
            # is not required.
            command = [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                (
                    f"color=c={settings['background']}:"
                    f"s={resolution}:"
                    f"r=24"
                ),
                "-t",
                str(duration),
                "-vf",
                video_filter,
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(scene_path),
            ]

            _run_ffmpeg(command)

            scene_files.append(scene_path)

        concat_file = (
            output.parent
            / f".{use_case}_concat.txt"
        )

        with open(
            concat_file,
            "w",
            encoding="utf-8",
        ) as file:
            for scene_file in scene_files:
                file.write(
                    f"file '{scene_file.resolve().as_posix()}'\n"
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

        _run_ffmpeg(command)

        return output

    finally:
        for scene_file in scene_files:
            scene_file.unlink(
                missing_ok=True
            )

        concat_file = (
            output.parent
            / f".{use_case}_concat.txt"
        )

        concat_file.unlink(
            missing_ok=True
        )
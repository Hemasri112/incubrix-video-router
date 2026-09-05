import subprocess
from pathlib import Path
from typing import Dict, List


WORKFLOW_VISUALS = {
    "education": {
        "background": "0x17324D",
        "panel": "0x234B6F",
        "accent": "0x4FC3F7",
        "label": "LEARN",
        "subtitle": "LEARN • UNDERSTAND • APPLY",
    },
    "news": {
        "background": "0x321313",
        "panel": "0x5A2020",
        "accent": "0xFF5252",
        "label": "NEWS UPDATE",
        "subtitle": "LATEST • CONTEXT • IMPACT",
    },
    "product": {
        "background": "0x24113D",
        "panel": "0x432267",
        "accent": "0xCE93D8",
        "label": "PRODUCT SPOTLIGHT",
        "subtitle": "FEATURES • BENEFITS • ACTION",
    },
}


WINDOWS_FONT = "C\\:/Windows/Fonts/arial.ttf"


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
            + result.stderr[-4000:]
        )


def _escape_drawtext(text: str) -> str:
    """Escape text for FFmpeg drawtext."""

    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace(",", "\\,")
        .replace("%", "\\%")
    )


def _build_visual_filter(
    use_case: str,
    scene_type: str,
    scene_number: int,
    aspect_ratio: str,
) -> str:
    """
    Build a structured visual layout for one scene.

    This is local CPU/FFmpeg assembly.
    It is not an AI-generated video stage.
    """

    settings = WORKFLOW_VISUALS[use_case]

    resolution = _get_resolution(
        aspect_ratio
    )

    if aspect_ratio == "16:9":
        title_x = 80
        title_y = 70

        scene_x = 80
        scene_y = 155

        subtitle_x = 80
        subtitle_y = 610

        panel_x = 760
        panel_y = 150
        panel_w = 400
        panel_h = 390

        circle_x = "1000+80*sin(t*1.4)"
        circle_y = "340+70*cos(t*1.1)"

        bar_x = 80
        bar_y = 230
        bar_w = 570
        bar_h = 18

        title_size = 52
        scene_size = 34
        subtitle_size = 24

    else:
        title_x = 55
        title_y = 100

        scene_x = 55
        scene_y = 175

        subtitle_x = 55
        subtitle_y = 1160

        panel_x = 55
        panel_y = 300
        panel_w = 610
        panel_h = 560

        circle_x = "360+120*sin(t*1.2)"
        circle_y = "600+100*cos(t*0.9)"

        bar_x = 55
        bar_y = 250
        bar_w = 610
        bar_h = 16

        title_size = 42
        scene_size = 30
        subtitle_size = 22

    scene_label = _escape_drawtext(
        scene_type.replace(
            "_",
            " "
        ).upper()
    )

    workflow_label = _escape_drawtext(
        settings["label"]
    )

    subtitle = _escape_drawtext(
        settings["subtitle"]
    )

    filters = [
        f"scale={resolution}",

        (
            f"drawbox="
            f"x={panel_x}:"
            f"y={panel_y}:"
            f"w={panel_w}:"
            f"h={panel_h}:"
            f"color={settings['panel']}:"
            f"t=fill"
        ),

        (
            f"drawbox="
            f"x={bar_x}:"
            f"y={bar_y}:"
            f"w={bar_w}:"
            f"h={bar_h}:"
            f"color={settings['accent']}:"
            f"t=fill"
        ),

        (
            f"drawbox="
            f"x={panel_x + 35}:"
            f"y={panel_y + 35}:"
            f"w={panel_w - 70}:"
            f"h=8:"
            f"color={settings['accent']}:"
            f"t=fill"
        ),

        (
            f"drawtext="
            f"fontfile='{WINDOWS_FONT}':"
            f"text='{workflow_label}':"
            f"fontcolor=white:"
            f"fontsize={title_size}:"
            f"x={title_x}:"
            f"y={title_y}"
        ),

        (
            f"drawtext="
            f"fontfile='{WINDOWS_FONT}':"
            f"text='{scene_label}':"
            f"fontcolor={settings['accent']}:"
            f"fontsize={scene_size}:"
            f"x={scene_x}:"
            f"y={scene_y}"
        ),

        (
            f"drawtext="
            f"fontfile='{WINDOWS_FONT}':"
            f"text='{subtitle}':"
            f"fontcolor=white:"
            f"fontsize={subtitle_size}:"
            f"x={subtitle_x}:"
            f"y={subtitle_y}"
        ),

        (
            f"drawtext="
            f"fontfile='{WINDOWS_FONT}':"
            f"text='SCENE {scene_number}':"
            f"fontcolor=white:"
            f"fontsize={subtitle_size}:"
            f"x={panel_x + 35}:"
            f"y={panel_y + 65}"
        ),

        (
            f"drawbox="
            f"x={panel_x + 60}:"
            f"y={panel_y + 125}:"
            f"w={panel_w - 120}:"
            f"h=8:"
            f"color={settings['accent']}:"
            f"t=fill"
        ),

        (
            f"drawbox="
            f"x={panel_x + 60}:"
            f"y={panel_y + 165}:"
            f"w={panel_w - 180}:"
            f"h=12:"
            f"color=white@0.65:"
            f"t=fill"
        ),

        (
            f"drawbox="
            f"x={panel_x + 60}:"
            f"y={panel_y + 205}:"
            f"w={panel_w - 240}:"
            f"h=12:"
            f"color=white@0.45:"
            f"t=fill"
        ),

        (
            f"drawbox="
            f"x={panel_x + 60}:"
            f"y={panel_y + 245}:"
            f"w={panel_w - 140}:"
            f"h=12:"
            f"color=white@0.30:"
            f"t=fill"
        ),

        (
            f"drawbox="
            f"x={panel_x + 60}:"
            f"y={panel_y + 305}:"
            f"w={panel_w - 220}:"
            f"h=55:"
            f"color={settings['accent']}@0.25:"
            f"t=fill"
        ),

        (
            f"drawbox="
            f"x={circle_x}:"
            f"y={circle_y}:"
            f"w=70:"
            f"h=70:"
            f"color={settings['accent']}@0.75:"
            f"t=fill"
        ),
    ]

    return ",".join(filters)


def create_workflow_video(
    use_case: str,
    scene_plan: List[Dict],
    output_path: str,
    aspect_ratio: str,
) -> Path:
    """
    Create a visually differentiated CPU workflow video.

    Education, news and product workflows use different:
    - visual themes
    - labels
    - scene structures
    - motion
    - pacing

    This stage uses local FFmpeg assembly.
    It does not claim AI generation.
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

    resolution = _get_resolution(
        aspect_ratio
    )

    settings = WORKFLOW_VISUALS[
        use_case
    ]

    scene_files = []

    concat_file = (
        output.parent
        / f".{use_case}_concat.txt"
    )

    try:
        for scene in scene_plan:
            scene_id = int(
                scene["scene_id"]
            )

            duration = float(
                scene["duration"]
            )

            scene_type = str(
                scene["type"]
            )

            scene_path = (
                output.parent
                / (
                    f".{use_case}_"
                    f"scene_{scene_id}.mp4"
                )
            )

            visual_filter = _build_visual_filter(
                use_case=use_case,
                scene_type=scene_type,
                scene_number=scene_id,
                aspect_ratio=aspect_ratio,
            )

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
                visual_filter,
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-pix_fmt",
                "yuv420p",
                "-r",
                "24",
                str(scene_path),
            ]

            _run_ffmpeg(command)

            scene_files.append(
                scene_path
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

        concat_file.unlink(
            missing_ok=True
        )
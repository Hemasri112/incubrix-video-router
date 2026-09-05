import json
from pathlib import Path
from typing import List, Dict


def create_timeline(
    clips: List[Dict],
    output_path: str,
    aspect_ratio: str,
) -> Path:
    """
    Create an editable timeline description.

    Each clip should contain:
        - id
        - start
        - duration
        - source
        - prompt
    """

    if not clips:
        raise ValueError("Timeline must contain at least one clip.")

    timeline = {
        "version": "1.0",
        "aspect_ratio": aspect_ratio,
        "clips": clips,
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as file:
        json.dump(timeline, file, indent=4)

    return output


def scene_plan_to_clips(
    scene_plan: List[Dict],
) -> List[Dict]:
    """
    Convert a workflow scene plan into editable timeline clips.
    """

    if not scene_plan:
        raise ValueError("Scene plan cannot be empty.")

    clips = []

    for scene in scene_plan:
        clips.append(
            {
                "id": f"scene_{scene['scene_id']}",
                "start": scene["start"],
                "duration": scene["duration"],
                "source": None,
                "prompt": (
                    f"{scene['type']}: "
                    f"{scene['visual_strategy']}"
                ),
                "caption_style": scene["caption_style"],
            }
        )

    return clips


def create_timeline_from_scene_plan(
    scene_plan: List[Dict],
    output_path: str,
    aspect_ratio: str,
) -> Path:
    """
    Convert a scene plan directly into timeline.json.
    """

    clips = scene_plan_to_clips(scene_plan)

    return create_timeline(
        clips=clips,
        output_path=output_path,
        aspect_ratio=aspect_ratio,
    )
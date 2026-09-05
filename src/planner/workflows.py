from typing import Dict, List

from src.planner.planner import CreativeBrief


WORKFLOW_TEMPLATES = {
    "education": {
        "scene_structure": [
            "hook",
            "concept_explanation",
            "example",
            "summary",
        ],
        "pacing": "moderate",
        "visual_strategy": "clean diagrams, simple motion, educational visuals",
        "caption_style": "clear instructional captions",
    },
    "news": {
        "scene_structure": [
            "headline",
            "context",
            "key_development",
            "impact",
            "closing",
        ],
        "pacing": "fast",
        "visual_strategy": "news-style visuals, headlines, supporting imagery",
        "caption_style": "short headline-focused captions",
    },
    "product": {
        "scene_structure": [
            "hook",
            "problem",
            "product_showcase",
            "benefits",
            "call_to_action",
        ],
        "pacing": "fast",
        "visual_strategy": "product-focused shots, close-ups, dynamic transitions",
        "caption_style": "short promotional captions",
    },
}


def get_workflow(use_case: str) -> Dict:
    """Return the workflow configuration for a supported use case."""

    workflow = WORKFLOW_TEMPLATES.get(use_case.lower())

    if workflow is None:
        raise ValueError(f"Unsupported use case: {use_case}")

    return workflow


def create_scene_plan(brief: CreativeBrief) -> List[Dict]:
    """Convert a creative brief into a structured scene plan."""

    workflow = get_workflow(brief.use_case)

    scenes = workflow["scene_structure"]
    scene_duration = brief.duration / len(scenes)

    scene_plan = []
    current_time = 0.0

    for index, scene_type in enumerate(scenes, start=1):
        scene = {
            "scene_id": index,
            "type": scene_type,
            "start": round(current_time, 2),
            "duration": round(scene_duration, 2),
            "end": round(current_time + scene_duration, 2),
            "visual_strategy": workflow["visual_strategy"],
            "caption_style": workflow["caption_style"],
        }

        scene_plan.append(scene)
        current_time += scene_duration

    return scene_plan
from pathlib import Path

from src.assembly.ffmpeg import validate_video_file
from src.assembly.workflow_video import create_workflow_video
from src.planner.planner import CreativeBrief
from src.planner.workflows import create_scene_plan


def test_education_workflow_video(tmp_path):
    brief = CreativeBrief(
        title="Python Basics",
        use_case="education",
        script="Python is beginner friendly.",
        duration=15,
        aspect_ratio="16:9",
    )

    scene_plan = create_scene_plan(brief)

    output = tmp_path / "education.mp4"

    create_workflow_video(
        use_case="education",
        scene_plan=scene_plan,
        output_path=str(output),
        aspect_ratio="16:9",
    )

    result = validate_video_file(str(output))

    assert result["valid"] is True
    assert abs(result["duration_seconds"] - 15) <= 0.5


def test_news_workflow_video(tmp_path):
    brief = CreativeBrief(
        title="Technology News",
        use_case="news",
        script="A technology development was announced.",
        duration=15,
        aspect_ratio="16:9",
    )

    scene_plan = create_scene_plan(brief)

    output = tmp_path / "news.mp4"

    create_workflow_video(
        use_case="news",
        scene_plan=scene_plan,
        output_path=str(output),
        aspect_ratio="16:9",
    )

    result = validate_video_file(str(output))

    assert result["valid"] is True
    assert abs(result["duration_seconds"] - 15) <= 0.5


def test_product_workflow_video_vertical(tmp_path):
    brief = CreativeBrief(
        title="Product Launch",
        use_case="product",
        script="Introducing a new product.",
        duration=15,
        aspect_ratio="9:16",
    )

    scene_plan = create_scene_plan(brief)

    output = tmp_path / "product.mp4"

    create_workflow_video(
        use_case="product",
        scene_plan=scene_plan,
        output_path=str(output),
        aspect_ratio="9:16",
    )

    result = validate_video_file(str(output))

    assert result["valid"] is True
    assert abs(result["duration_seconds"] - 15) <= 0.5
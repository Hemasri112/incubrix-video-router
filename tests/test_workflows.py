from src.planner.planner import CreativeBrief
from src.planner.workflows import create_scene_plan, get_workflow


def make_brief(use_case, aspect_ratio="16:9"):
    return CreativeBrief(
        title=f"{use_case} test",
        use_case=use_case,
        script="Test script for the workflow.",
        duration=15,
        aspect_ratio=aspect_ratio,
    )


def test_education_workflow():
    workflow = get_workflow("education")

    assert workflow["pacing"] == "moderate"
    assert workflow["scene_structure"] == [
        "hook",
        "concept_explanation",
        "example",
        "summary",
    ]


def test_news_workflow():
    workflow = get_workflow("news")

    assert workflow["pacing"] == "fast"
    assert workflow["scene_structure"] == [
        "headline",
        "context",
        "key_development",
        "impact",
        "closing",
    ]


def test_product_workflow():
    workflow = get_workflow("product")

    assert workflow["pacing"] == "fast"
    assert workflow["scene_structure"] == [
        "hook",
        "problem",
        "product_showcase",
        "benefits",
        "call_to_action",
    ]


def test_workflows_have_different_scene_structures():
    education = get_workflow("education")
    news = get_workflow("news")
    product = get_workflow("product")

    assert education["scene_structure"] != news["scene_structure"]
    assert news["scene_structure"] != product["scene_structure"]
    assert education["scene_structure"] != product["scene_structure"]


def test_education_scene_plan():
    brief = make_brief("education")

    scenes = create_scene_plan(brief)

    assert len(scenes) == 4
    assert scenes[0]["type"] == "hook"
    assert scenes[-1]["type"] == "summary"


def test_news_scene_plan():
    brief = make_brief("news")

    scenes = create_scene_plan(brief)

    assert len(scenes) == 5
    assert scenes[0]["type"] == "headline"
    assert scenes[-1]["type"] == "closing"


def test_product_vertical_scene_plan():
    brief = make_brief(
        "product",
        aspect_ratio="9:16",
    )

    scenes = create_scene_plan(brief)

    assert len(scenes) == 5
    assert scenes[0]["type"] == "hook"
    assert scenes[2]["type"] == "product_showcase"


def test_scene_plan_covers_full_duration():
    brief = make_brief("education")

    scenes = create_scene_plan(brief)

    assert scenes[0]["start"] == 0
    assert scenes[-1]["end"] == brief.duration
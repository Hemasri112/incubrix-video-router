import pytest
from pydantic import ValidationError

from src.planner.planner import CreativeBrief
from src.planner.workflows import get_workflow


def test_valid_creative_brief():
    brief = CreativeBrief(
        title="Python Basics",
        use_case="education",
        script="Python is a programming language.",
        duration=15,
        aspect_ratio="16:9",
        style="educational",
        constraints=["captions"],
    )

    assert brief.title == "Python Basics"
    assert brief.use_case == "education"
    assert brief.duration == 15
    assert brief.aspect_ratio == "16:9"


def test_invalid_duration():
    with pytest.raises(ValidationError):
        CreativeBrief(
            title="Invalid Video",
            use_case="education",
            script="Test script",
            duration=0,
            aspect_ratio="16:9",
        )


def test_unsupported_workflow():
    with pytest.raises(ValueError):
        get_workflow("unknown_use_case")
from src.planner.planner import CreativeBrief
from src.router.router import route_request


def test_router_selects_supported_model():
    brief = CreativeBrief(
        title="Python Basics",
        use_case="education",
        script="Python is a programming language.",
        duration=15,
        aspect_ratio="16:9",
    )

    decision = route_request(brief)

    assert decision["selected_model"] is not None
    assert decision["score"] > 0
    assert len(decision["candidates"]) == 5


def test_router_prefers_16_9_capable_models():
    brief = CreativeBrief(
        title="Technology News",
        use_case="news",
        script="Latest technology development.",
        duration=15,
        aspect_ratio="16:9",
    )

    decision = route_request(brief)

    selected_model = decision["selected_model"]

    assert selected_model in {
        "wan2.1",
        "ltx-video",
        "cogvideox",
        "hunyuanvideo",
        "mochi-1",
    }


def test_router_supports_vertical_video():
    brief = CreativeBrief(
        title="Product Launch",
        use_case="product",
        script="Introducing a new product.",
        duration=15,
        aspect_ratio="9:16",
    )

    decision = route_request(brief)

    assert decision["selected_model"] in {
        "wan2.1",
        "ltx-video",
    }
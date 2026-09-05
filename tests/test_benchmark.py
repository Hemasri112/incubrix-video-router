from pathlib import Path

from src.evaluation.benchmark import run_routing_benchmark
from src.planner.planner import CreativeBrief


def test_routing_benchmark(tmp_path):
    briefs = [
        CreativeBrief(
            title="Python Basics",
            use_case="education",
            script="Python is a programming language.",
            duration=15,
            aspect_ratio="16:9",
        ),
        CreativeBrief(
            title="Product Launch",
            use_case="product",
            script="Introducing a new product.",
            duration=15,
            aspect_ratio="9:16",
        ),
        CreativeBrief(
            title="Technology News",
            use_case="news",
            script="Latest technology development.",
            duration=15,
            aspect_ratio="16:9",
        ),
    ]

    output_path = tmp_path / "benchmark.json"

    result = run_routing_benchmark(
        briefs=briefs,
        expected_models=[
            "wan2.1",
            "wan2.1",
            "wan2.1",
        ],
        runtimes=[
            10.0,
            20.0,
            15.0,
        ],
        successful_renders=3,
        output_path=str(output_path),
    )

    assert result["summary"]["total_briefs"] == 3
    assert result["summary"]["successful_renders"] == 3
    assert result["summary"]["render_success_rate"] == 1.0
    assert len(result["routes"]) == 3
    assert output_path.exists()


def test_benchmark_rejects_mismatched_models():
    briefs = [
        CreativeBrief(
            title="Python Basics",
            use_case="education",
            script="Python is a programming language.",
            duration=15,
            aspect_ratio="16:9",
        )
    ]

    try:
        run_routing_benchmark(
            briefs=briefs,
            expected_models=[],
            runtimes=[10.0],
            successful_renders=1,
        )
    except ValueError as error:
        assert "expected models" in str(error).lower()
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
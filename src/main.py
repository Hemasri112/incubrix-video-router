import json
from pathlib import Path
from typing import Optional

import typer
from rich import print

from src.planner.planner import CreativeBrief
from src.pipeline import run_pipeline
from src.evaluation.benchmark import run_benchmark_from_file


app = typer.Typer(
    help="IncuBrix open-source video generation and model routing CLI."
)


@app.command()
def generate(
    brief_file: str = typer.Option(
        ...,
        "--brief",
        "-b",
        help="Path to a JSON creative brief.",
    ),
    video: Optional[str] = typer.Option(
        None,
        "--video",
        "-v",
        help="Optional path to an existing generated MP4 artifact.",
    ),
    captions: Optional[str] = typer.Option(
        None,
        "--captions",
        "-c",
        help="Optional SRT captions file.",
    ),
):
    """
    Run the planning, routing, generation/fallback,
    timeline, captions, manifest and validation pipeline.
    """

    brief_path = Path(brief_file)

    if not brief_path.exists():
        raise typer.BadParameter(
            f"Brief file does not exist: {brief_file}"
        )

    try:
        with open(
            brief_path,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        raise typer.BadParameter(
            f"Invalid JSON brief: {error}"
        )

    try:
        brief = CreativeBrief(**data)

    except Exception as error:
        raise typer.BadParameter(
            f"Invalid creative brief: {error}"
        )

    result = run_pipeline(
        brief=brief,
        video_path=video,
        captions_path=captions,
    )

    print(
        json.dumps(
            result,
            indent=4,
        )
    )


@app.command()
def benchmark(
    briefs_file: str = typer.Option(
        ...,
        "--briefs",
        "-b",
        help="Path to a benchmark JSON file.",
    ),
):
    """
    Run the routing benchmark over multiple creative briefs.
    """

    try:
        result = run_benchmark_from_file(
            input_path=briefs_file,
            output_path="outputs/benchmark.json",
        )

    except (
        FileNotFoundError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        raise typer.BadParameter(
            str(error)
        )

    print(
        json.dumps(
            result,
            indent=4,
        )
    )


@app.command()
def version():
    """Display the project version."""

    print("IncuBrix Video Router v0.1.0")


if __name__ == "__main__":
    app()
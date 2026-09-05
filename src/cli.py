import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON

from src.pipeline import run_pipeline
from src.planner.planner import validate_brief
from src.evaluation.benchmark import run_benchmark_from_file


app = typer.Typer(
    help="IncuBrix video generation and model routing CLI."
)

console = Console()


def load_json_file(file_path: str) -> dict:
    """Load and parse a JSON file."""

    path = Path(file_path)

    if not path.exists():
        raise typer.BadParameter(
            f"File not found: {path}"
        )

    if path.suffix.lower() != ".json":
        raise typer.BadParameter(
            "Input file must be a JSON file."
        )

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except json.JSONDecodeError as error:
        raise typer.BadParameter(
            f"Invalid JSON: {error}"
        ) from error


@app.command()
def validate(
    brief: str = typer.Argument(
        ...,
        help="Path to a creative brief JSON file.",
    ),
):
    """Validate a creative brief."""

    data = load_json_file(brief)

    try:
        creative_brief = validate_brief(data)
    except Exception as error:
        raise typer.BadParameter(
            f"Invalid creative brief: {error}"
        ) from error

    console.print(
        "[bold green]Creative brief is valid.[/bold green]"
    )

    console.print(
        JSON.from_data(
            creative_brief.model_dump()
        )
    )


@app.command()
def generate(
    brief: str = typer.Argument(
        ...,
        help="Path to a creative brief JSON file.",
    ),
    video: Optional[str] = typer.Option(
        None,
        "--video",
        help="Optional previously generated model video.",
    ),
    captions: Optional[str] = typer.Option(
        None,
        "--captions",
        help="Optional existing SRT caption file.",
    ),
    seed: int = typer.Option(
        42,
        "--seed",
        help="Generation seed.",
    ),
):
    """Generate a draft video from a creative brief."""

    data = load_json_file(brief)

    try:
        creative_brief = validate_brief(data)
    except Exception as error:
        raise typer.BadParameter(
            f"Invalid creative brief: {error}"
        ) from error

    console.print(
        f"[bold]Generating:[/bold] {creative_brief.title}"
    )

    result = run_pipeline(
        brief=creative_brief,
        video_path=video,
        captions_path=captions,
        seed=seed,
    )

    console.print(
        JSON.from_data(result)
    )

    if result["status"] != "success":
        raise typer.Exit(code=1)

    console.print(
        "\n[bold green]Generation completed successfully.[/bold green]"
    )

    console.print(
        f"Video: {result['video']}"
    )
    console.print(
        f"Timeline: {result['timeline']}"
    )
    console.print(
        f"Captions: {result['captions']}"
    )
    console.print(
        f"Manifest: {result['manifest']}"
    )


@app.command()
def benchmark(
    briefs: str = typer.Option(
        "examples/benchmark_10.json",
        "--briefs",
        help="Path to benchmark JSON file.",
    ),
):
    """Run the 10-brief routing and assembly benchmark."""

    benchmark_path = Path(briefs)

    if not benchmark_path.exists():
        raise typer.BadParameter(
            f"Benchmark file not found: {benchmark_path}"
        )

    console.print(
        f"[bold]Running benchmark:[/bold] {benchmark_path}"
    )

    result = run_benchmark_from_file(
        str(benchmark_path)
    )

    console.print(
        JSON.from_data(result)
    )

    console.print(
        "\n[bold green]Benchmark completed.[/bold green]"
    )


if __name__ == "__main__":
    app()
import json
import re
import shutil
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from src.evaluation.metrics import build_benchmark_summary
from src.pipeline import run_pipeline
from src.planner.planner import CreativeBrief
from src.router.router import route_request


def load_benchmark_briefs(
    input_path: str,
) -> List[CreativeBrief]:
    """Load creative briefs from a JSON array."""

    path = Path(input_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Benchmark file not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Benchmark JSON must contain a list of briefs."
        )

    return [
        CreativeBrief(**item)
        for item in data
    ]


def load_routing_policy(
    policy_path: str,
) -> Dict:
    """Load the independent routing evaluation policy."""

    path = Path(policy_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Routing policy not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        policy = json.load(file)

    if "policy" not in policy:
        raise ValueError(
            "Routing policy must contain a 'policy' section."
        )

    if "rules" not in policy["policy"]:
        raise ValueError(
            "Routing policy must contain routing rules."
        )

    return policy


def expected_model_from_policy(
    brief: CreativeBrief,
    policy: Dict,
) -> str:
    """
    Determine the expected model independently from the router.

    Current benchmark policy:
    - duration > 20 seconds -> Wan2.1
    - duration <= 20 seconds -> LTX-Video
    """

    if brief.duration > 20:
        return "wan2.1"

    if (
        brief.duration <= 20
        and brief.aspect_ratio in {"16:9", "9:16"}
    ):
        return "ltx-video"

    return "cpu_fallback"


def _safe_name(text: str) -> str:
    """Convert text into a filesystem-safe name."""

    name = text.lower()

    name = re.sub(
        r"[^a-z0-9]+",
        "_",
        name,
    )

    return name.strip("_")


def _preserve_benchmark_artifacts(
    result: Dict,
    brief: CreativeBrief,
    index: int,
) -> Dict:
    """
    Copy pipeline artifacts into a unique benchmark directory.
    """

    benchmark_dir = (
        Path("outputs")
        / "benchmark"
        / f"{index:02d}_{_safe_name(brief.title)}"
    )

    benchmark_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_mapping = {
        "video": "final.mp4",
        "captions": "captions.srt",
        "timeline": "timeline.json",
        "manifest": "manifest.json",
    }

    preserved_paths = {}

    for result_key, destination_name in artifact_mapping.items():
        source_value = result.get(result_key)

        if not source_value:
            continue

        source = Path(source_value)

        if not source.exists():
            continue

        destination = (
            benchmark_dir
            / destination_name
        )

        shutil.copy2(
            source,
            destination,
        )

        preserved_paths[result_key] = str(
            destination
        )

    route_source = Path(
        "outputs/route_decision.json"
    )

    if route_source.exists():
        route_destination = (
            benchmark_dir
            / "route_decision.json"
        )

        shutil.copy2(
            route_source,
            route_destination,
        )

        preserved_paths["route_decision"] = str(
            route_destination
        )

    manifest_path = preserved_paths.get(
        "manifest"
    )

    if manifest_path:
        with open(
            manifest_path,
            "r",
            encoding="utf-8",
        ) as file:
            manifest = json.load(file)

        if "output" in manifest:
            manifest["output"]["file"] = (
                preserved_paths.get(
                    "video",
                    manifest["output"].get("file"),
                )
            )

        with open(
            manifest_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                manifest,
                file,
                indent=4,
            )

    return preserved_paths


def _build_group_statistics(
    routes: List[Dict],
) -> Dict:
    """
    Build benchmark statistics grouped by use case and
    aspect ratio.
    """

    groups = {
        "use_case": defaultdict(list),
        "aspect_ratio": defaultdict(list),
    }

    for route in routes:
        groups["use_case"][
            route["use_case"]
        ].append(route)

        groups["aspect_ratio"][
            route["aspect_ratio"]
        ].append(route)

    statistics = {}

    for group_name, grouped_routes in groups.items():
        statistics[group_name] = {}

        for key, items in grouped_routes.items():
            total = len(items)

            successful = sum(
                item["render_success"]
                for item in items
            )

            correct = sum(
                item["routing_correct"]
                for item in items
            )

            average_runtime = (
                sum(
                    item["runtime_seconds"]
                    for item in items
                )
                / total
            )

            statistics[group_name][key] = {
                "total_briefs": total,
                "successful_renders": successful,
                "render_success_rate": (
                    successful / total
                ),
                "correct_routes": correct,
                "route_accuracy": (
                    correct / total
                ),
                "average_latency_seconds": round(
                    average_runtime,
                    3,
                ),
            }

    return statistics


def run_routing_benchmark(
    briefs: List[CreativeBrief],
    expected_models: List[str],
    runtimes: List[float],
    successful_renders: int,
    output_path: str = "outputs/benchmark.json",
) -> Dict:
    """
    Run routing evaluation without executing video generation.

    Retained for compatibility with the existing unit tests.
    """

    if not briefs:
        raise ValueError(
            "At least one creative brief is required."
        )

    if len(briefs) != len(expected_models):
        raise ValueError(
            "Number of briefs must match expected models."
        )

    if len(briefs) != len(runtimes):
        raise ValueError(
            "Number of briefs must match runtime measurements."
        )

    if successful_renders < 0:
        raise ValueError(
            "Successful renders cannot be negative."
        )

    if successful_renders > len(briefs):
        raise ValueError(
            "Successful renders cannot exceed total briefs."
        )

    selected_models = []
    route_results = []

    for brief, expected_model in zip(
        briefs,
        expected_models,
    ):
        decision = route_request(brief)

        selected_model = decision["selected_model"]

        selected_models.append(
            selected_model
        )

        route_results.append(
            {
                "brief": brief.title,
                "use_case": brief.use_case,
                "duration": brief.duration,
                "aspect_ratio": brief.aspect_ratio,
                "expected_model": expected_model,
                "selected_model": selected_model,
                "routing_correct": (
                    selected_model == expected_model
                ),
                "score": decision["score"],
                "routing_status": decision[
                    "routing_status"
                ],
                "generation_method": (
                    "not_executed"
                ),
                "render_success": False,
                "runtime_seconds": runtimes[
                    len(route_results)
                ],
                "reason": decision["reason"],
            }
        )

    summary = build_benchmark_summary(
        total_briefs=len(briefs),
        successful_renders=successful_renders,
        selected_models=selected_models,
        expected_models=expected_models,
        runtimes=runtimes,
    )

    result = {
        "benchmark": {
            "total_briefs": len(briefs),
            "routing_policy": (
                "configs/routing_policy.json"
            ),
            "evaluation_type": "independent_policy",
        },
        "summary": summary,
        "routes": route_results,
        "group_statistics": _build_group_statistics(
            route_results
        ),
    }

    output = Path(output_path)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=4,
        )

    return result


def run_measured_benchmark(
    briefs: List[CreativeBrief],
    expected_models: List[str],
    output_path: str = "outputs/benchmark.json",
) -> Dict:
    """
    Execute the local pipeline for every benchmark brief.

    Runtime is measured using time.perf_counter().

    Every benchmark run is preserved independently.
    """

    if not briefs:
        raise ValueError(
            "At least one creative brief is required."
        )

    if len(briefs) != len(expected_models):
        raise ValueError(
            "Number of briefs must match expected models."
        )

    route_results = []
    runtimes = []
    successful_renders = 0

    for index, (brief, expected_model) in enumerate(
        zip(briefs, expected_models),
        start=1,
    ):
        print(
            f"[{index}/{len(briefs)}] "
            f"Running: {brief.title}"
        )

        start_time = time.perf_counter()

        try:
            result = run_pipeline(
                brief=brief,
            )

            runtime = time.perf_counter() - start_time

            validation = result.get(
                "validation",
                {},
            )

            render_success = (
                result.get("status") == "success"
                and validation.get("valid") is True
            )

            if render_success:
                successful_renders += 1

            decision = result.get(
                "route_decision",
                {},
            )

            selected_model = decision.get(
                "selected_model"
            )

            preserved = _preserve_benchmark_artifacts(
                result=result,
                brief=brief,
                index=index,
            )

            route_results.append(
                {
                    "brief": brief.title,
                    "use_case": brief.use_case,
                    "duration": brief.duration,
                    "aspect_ratio": brief.aspect_ratio,
                    "expected_model": expected_model,
                    "selected_model": selected_model,
                    "routing_correct": (
                        selected_model == expected_model
                    ),
                    "routing_status": decision.get(
                        "routing_status"
                    ),
                    "generation_method": result.get(
                        "generation_method"
                    ),
                    "render_success": render_success,
                    "runtime_seconds": round(
                        runtime,
                        3,
                    ),
                    "artifacts": preserved,
                    "validation": validation,
                }
            )

            runtimes.append(runtime)

            print(
                f"    Route: {selected_model}"
            )
            print(
                f"    Method: "
                f"{result.get('generation_method')}"
            )
            print(
                f"    Success: {render_success}"
            )
            print(
                f"    Runtime: "
                f"{runtime:.2f}s"
            )

        except Exception as error:
            runtime = time.perf_counter() - start_time

            runtimes.append(runtime)

            decision = route_request(brief)

            route_results.append(
                {
                    "brief": brief.title,
                    "use_case": brief.use_case,
                    "duration": brief.duration,
                    "aspect_ratio": brief.aspect_ratio,
                    "expected_model": expected_model,
                    "selected_model": decision.get(
                        "selected_model"
                    ),
                    "routing_correct": (
                        decision.get(
                            "selected_model"
                        )
                        == expected_model
                    ),
                    "routing_status": (
                        "execution_failed"
                    ),
                    "generation_method": "failed",
                    "render_success": False,
                    "runtime_seconds": round(
                        runtime,
                        3,
                    ),
                    "error": str(error),
                }
            )

            print(
                f"    FAILED: {error}"
            )
            print(
                f"    Runtime: "
                f"{runtime:.2f}s"
            )

    selected_models = [
        route["selected_model"]
        for route in route_results
    ]

    summary = build_benchmark_summary(
        total_briefs=len(briefs),
        successful_renders=successful_renders,
        selected_models=selected_models,
        expected_models=expected_models,
        runtimes=runtimes,
    )

    result = {
        "benchmark": {
            "total_briefs": len(briefs),
            "evaluation_type": (
                "measured_pipeline_execution"
            ),
            "routing_policy": (
                "configs/routing_policy.json"
            ),
            "runtime_measurement": (
                "time.perf_counter"
            ),
            "generation_note": (
                "The benchmark executes the local pipeline. "
                "When no generated model artifact is supplied, "
                "the pipeline uses CPU workflow assembly fallback."
            ),
            "artifact_storage": (
                "Each benchmark run is preserved in "
                "outputs/benchmark/<index>_<brief>/."
            ),
        },
        "summary": summary,
        "group_statistics": _build_group_statistics(
            route_results
        ),
        "routes": route_results,
    }

    output = Path(output_path)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=4,
        )

    return result


def run_benchmark_from_file(
    input_path: str,
    policy_path: str = "configs/routing_policy.json",
    output_path: str = "outputs/benchmark.json",
) -> Dict:
    """Load the benchmark and execute the measured pipeline."""

    briefs = load_benchmark_briefs(
        input_path
    )

    policy = load_routing_policy(
        policy_path
    )

    expected_models = [
        expected_model_from_policy(
            brief,
            policy,
        )
        for brief in briefs
    ]

    return run_measured_benchmark(
        briefs=briefs,
        expected_models=expected_models,
        output_path=output_path,
    )
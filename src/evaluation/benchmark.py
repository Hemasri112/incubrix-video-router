import ctypes
import json
import os
import platform
import re
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

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


def _get_machine_info() -> Dict:
    """Collect machine information for benchmark provenance."""

    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "processor": platform.processor(),
        "python_version": sys.version.split()[0],
        "logical_cpus": os.cpu_count(),
    }


def _get_current_memory_gb() -> Optional[float]:
    """Return current process working-set memory in GB."""

    try:
        import psutil

        process = psutil.Process()

        return round(
            process.memory_info().rss
            / (1024 ** 3),
            4,
        )

    except ImportError:
        return None


def _get_peak_working_set_gb() -> Optional[float]:
    """
    Return the process peak working-set size.

    Windows exposes this directly through GetProcessMemoryInfo.
    On unsupported platforms, return None.
    """

    if platform.system() != "Windows":
        return None

    try:
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                (
                    "cb",
                    ctypes.c_ulong,
                ),
                (
                    "PageFaultCount",
                    ctypes.c_ulong,
                ),
                (
                    "PeakWorkingSetSize",
                    ctypes.c_size_t,
                ),
                (
                    "WorkingSetSize",
                    ctypes.c_size_t,
                ),
                (
                    "QuotaPeakPagedPoolUsage",
                    ctypes.c_size_t,
                ),
                (
                    "QuotaPagedPoolUsage",
                    ctypes.c_size_t,
                ),
                (
                    "QuotaPeakNonPagedPoolUsage",
                    ctypes.c_size_t,
                ),
                (
                    "QuotaNonPagedPoolUsage",
                    ctypes.c_size_t,
                ),
                (
                    "PagefileUsage",
                    ctypes.c_size_t,
                ),
                (
                    "PeakPagefileUsage",
                    ctypes.c_size_t,
                ),
            ]

        counters = PROCESS_MEMORY_COUNTERS()

        counters.cb = ctypes.sizeof(
            PROCESS_MEMORY_COUNTERS
        )

        process_handle = ctypes.windll.kernel32.GetCurrentProcess()

        result = ctypes.windll.psapi.GetProcessMemoryInfo(
            process_handle,
            ctypes.byref(counters),
            counters.cb,
        )

        if not result:
            return None

        return round(
            counters.PeakWorkingSetSize
            / (1024 ** 3),
            4,
        )

    except Exception:
        return None


def _detect_cache_state(
    result: Dict,
    runtime_seconds: float,
) -> str:
    """
    Classify cache state conservatively.

    This does not claim that a run was cold unless the pipeline
    explicitly exposes that information.
    """

    generation_method = result.get(
        "generation_method"
    )

    if generation_method == "cpu_workflow_assembly":
        if runtime_seconds < 0.1:
            return "likely_cached_or_resumed"

        return "pipeline_execution"

    return "model_or_external_artifact"


def _calculate_quality_metrics(
    result: Dict,
    brief: CreativeBrief,
) -> Dict:
    """
    Calculate objective structural quality metrics.

    These metrics do not claim subjective visual quality or
    semantic prompt adherence.
    """

    validation = result.get(
        "validation",
        {},
    )

    timeline_path = result.get(
        "timeline"
    )

    captions_path = result.get(
        "captions"
    )

    scene_count = 0
    temporal_defects = 0

    if timeline_path:
        timeline_file = Path(timeline_path)

        if timeline_file.exists():
            try:
                with open(
                    timeline_file,
                    "r",
                    encoding="utf-8",
                ) as file:
                    timeline = json.load(file)

                clips = timeline.get(
                    "clips",
                    [],
                )

                scene_count = len(clips)

                previous_end = 0.0

                for clip in clips:
                    start = float(
                        clip.get(
                            "start",
                            0,
                        )
                    )

                    duration = float(
                        clip.get(
                            "duration",
                            0,
                        )
                    )

                    end = start + duration

                    if duration <= 0:
                        temporal_defects += 1

                    if start < previous_end - 0.01:
                        temporal_defects += 1

                    previous_end = end

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError,
            ):
                temporal_defects += 1

    caption_present = (
        captions_path is not None
        and Path(captions_path).exists()
        and Path(captions_path).stat().st_size > 0
    )

    return {
        "scene_count": scene_count,
        "scene_coverage": (
            1.0
            if scene_count > 0
            else 0.0
        ),
        "caption_coverage": (
            1.0
            if caption_present
            else 0.0
        ),
        "temporal_defects": temporal_defects,
        "render_success": (
            result.get("status") == "success"
            and validation.get("valid") is True
        ),
        "semantic_prompt_adherence": None,
        "semantic_prompt_adherence_status": (
            "not_automatically_measured"
        ),
        "use_case": brief.use_case,
    }


def _preserve_benchmark_artifacts(
    result: Dict,
    brief: CreativeBrief,
    index: int,
) -> Dict:
    """Copy pipeline artifacts into a unique benchmark directory."""

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
    """Build benchmark statistics by use case and aspect ratio."""

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

            average_scene_coverage = (
                sum(
                    item["quality_metrics"][
                        "scene_coverage"
                    ]
                    for item in items
                )
                / total
            )

            average_caption_coverage = (
                sum(
                    item["quality_metrics"][
                        "caption_coverage"
                    ]
                    for item in items
                )
                / total
            )

            total_temporal_defects = sum(
                item["quality_metrics"][
                    "temporal_defects"
                ]
                for item in items
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
                "average_observed_runtime_seconds": round(
                    average_runtime,
                    3,
                ),
                "average_scene_coverage": round(
                    average_scene_coverage,
                    3,
                ),
                "average_caption_coverage": round(
                    average_caption_coverage,
                    3,
                ),
                "temporal_defects": (
                    total_temporal_defects
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
    """Run routing evaluation without video generation."""

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

    for index, (
        brief,
        expected_model,
    ) in enumerate(
        zip(
            briefs,
            expected_models,
        )
    ):
        decision = route_request(brief)

        selected_model = decision[
            "selected_model"
        ]

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
                    index
                ],
                "quality_metrics": {
                    "scene_count": 0,
                    "scene_coverage": 0.0,
                    "caption_coverage": 0.0,
                    "temporal_defects": 0,
                    "render_success": False,
                    "semantic_prompt_adherence": None,
                    "semantic_prompt_adherence_status": (
                        "not_measured"
                    ),
                    "use_case": brief.use_case,
                },
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
            "evaluation_type": (
                "independent_policy"
            ),
            "repetitions": 1,
            "timing_boundary": (
                "Externally supplied runtime measurements."
            ),
            "machine": _get_machine_info(),
            "resource_measurements": {
                "peak_ram_gb": None,
                "peak_ram_status": (
                    "not_measured"
                ),
                "accelerator_time_seconds": None,
                "accelerator_memory_gb": None,
                "model_size_gb": None,
            },
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
    repetitions: int = 1,
) -> Dict:
    """
    Execute the local pipeline for every benchmark brief.

    Runtime is measured using time.perf_counter().

    Each run records:
    - wall-clock runtime
    - cache interpretation
    - peak working-set memory
    - structural quality metrics
    - preserved artifacts
    """

    if not briefs:
        raise ValueError(
            "At least one creative brief is required."
        )

    if len(briefs) != len(expected_models):
        raise ValueError(
            "Number of briefs must match expected models."
        )

    if repetitions <= 0:
        raise ValueError(
            "Repetitions must be greater than zero."
        )

    route_results = []
    runtimes = []
    successful_renders = 0

    overall_peak_ram_gb: Optional[float] = None

    for index, (
        brief,
        expected_model,
    ) in enumerate(
        zip(
            briefs,
            expected_models,
        ),
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

            runtime = (
                time.perf_counter()
                - start_time
            )

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

            peak_ram_gb = (
                _get_peak_working_set_gb()
            )

            if peak_ram_gb is None:
                peak_ram_gb = (
                    _get_current_memory_gb()
                )

            if peak_ram_gb is not None:
                if (
                    overall_peak_ram_gb is None
                    or peak_ram_gb
                    > overall_peak_ram_gb
                ):
                    overall_peak_ram_gb = (
                        peak_ram_gb
                    )

            cache_state = _detect_cache_state(
                result=result,
                runtime_seconds=runtime,
            )

            preserved = (
                _preserve_benchmark_artifacts(
                    result=result,
                    brief=brief,
                    index=index,
                )
            )

            quality_metrics = (
                _calculate_quality_metrics(
                    result=result,
                    brief=brief,
                )
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
                        selected_model
                        == expected_model
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
                    "runtime_type": (
                        "observed_wall_clock"
                    ),
                    "cache_state": cache_state,
                    "peak_ram_gb": peak_ram_gb,
                    "quality_metrics": quality_metrics,
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
                f"    Cache state: "
                f"{cache_state}"
            )
            print(
                f"    Success: "
                f"{render_success}"
            )
            print(
                f"    Runtime: "
                f"{runtime:.3f}s"
            )
            print(
                f"    Peak RAM: "
                f"{peak_ram_gb} GB"
            )

        except Exception as error:
            runtime = (
                time.perf_counter()
                - start_time
            )

            runtimes.append(runtime)

            decision = route_request(
                brief
            )

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
                    "runtime_type": (
                        "observed_wall_clock"
                    ),
                    "cache_state": (
                        "execution_failed"
                    ),
                    "peak_ram_gb": (
                        _get_peak_working_set_gb()
                    ),
                    "quality_metrics": {
                        "scene_count": 0,
                        "scene_coverage": 0.0,
                        "caption_coverage": 0.0,
                        "temporal_defects": 0,
                        "render_success": False,
                        "semantic_prompt_adherence": None,
                        "semantic_prompt_adherence_status": (
                            "not_measured"
                        ),
                        "use_case": brief.use_case,
                    },
                    "error": str(error),
                }
            )

            print(
                f"    FAILED: {error}"
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
            "timing_boundary": (
                "Wall-clock time measured from immediately "
                "before run_pipeline() until run_pipeline() "
                "returns. It includes planning, routing, "
                "pipeline cache/resume behavior, CPU assembly, "
                "captions, validation and manifest creation."
            ),
            "runtime_interpretation": (
                "Observed pipeline wall time. A cached or "
                "resumed run must not be interpreted as a "
                "cold video-render latency measurement."
            ),
            "repetitions": repetitions,
            "machine": _get_machine_info(),
            "resource_measurements": {
                "peak_ram_gb": overall_peak_ram_gb,
                "peak_ram_status": (
                    "measured"
                    if overall_peak_ram_gb
                    is not None
                    else "unavailable"
                ),
                "accelerator_time_seconds": None,
                "accelerator_memory_gb": None,
                "model_size_gb": None,
                "accelerator_status": (
                    "not_applicable_cpu_fallback"
                ),
                "model_size_status": (
                    "not_applicable_cpu_fallback"
                ),
            },
            "generation_note": (
                "The benchmark executes the local pipeline. "
                "When no generated model artifact is supplied, "
                "the pipeline uses CPU workflow assembly fallback."
            ),
            "cache_note": (
                "The project supports resumable artifact caching. "
                "Benchmark runtime is therefore reported as "
                "observed pipeline wall time and cache state is "
                "recorded per run."
            ),
            "artifact_storage": (
                "Each benchmark run is preserved in "
                "outputs/benchmark/<index>_<brief>/."
            ),
            "quality_measurement_boundary": (
                "Quality metrics are objective structural "
                "pipeline checks. Semantic visual quality and "
                "subjective prompt adherence are not automatically measured."
            ),
        },
        "summary": {
            **summary,
            "average_observed_pipeline_runtime_seconds": (
                summary[
                    "average_latency_seconds"
                ]
            ),
        },
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
    repetitions: int = 1,
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
        repetitions=repetitions,
    )
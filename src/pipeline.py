import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from src.assembly.captions import create_srt
from src.assembly.ffmpeg import burn_captions
from src.assembly.manifest import create_manifest
from src.assembly.timeline import create_timeline_from_scene_plan
from src.assembly.workflow_video import create_workflow_video
from src.logs.logger import get_logger, log_stage
from src.planner.planner import CreativeBrief
from src.planner.workflows import create_scene_plan
from src.router.fallback import handle_generation_failure
from src.router.router import route_request
from src.run_cache import RunCache, build_run_key, is_usable_file
from src.validation.validator import validate_output


def _split_script_into_chunks(script: str, count: int) -> List[str]:
    """Split a script into a practical number of caption chunks."""
    text = script.strip()
    if not text:
        return [""] * count
    sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", text) if item.strip()]
    if len(sentences) >= count:
        chunks = sentences[:count]
        if len(sentences) > count:
            chunks[-1] = f"{chunks[-1]} {' '.join(sentences[count:])}"
        return chunks
    words = text.split()
    words_per_chunk = max(1, (len(words) + count - 1) // count)
    chunks = [" ".join(words[i * words_per_chunk:(i + 1) * words_per_chunk]).strip() for i in range(count)]
    chunks = [chunk for chunk in chunks if chunk]
    while len(chunks) < count:
        chunks.append(chunks[-1])
    return chunks[:count]


def _create_script_captions(brief: CreativeBrief, scene_plan: List[Dict], output_path: str) -> Path:
    captions = [{"start": scene["start"], "end": scene["end"], "text": text} for scene, text in zip(scene_plan, _split_script_into_chunks(brief.script, len(scene_plan)))]
    return create_srt(captions=captions, output_path=output_path)


def _cache_hit(logger, stage: str, path: Optional[str] = None) -> None:
    log_stage(logger, "cache", f"Reused completed {stage} stage", {"path": path} if path else {})


def run_pipeline(
    brief: CreativeBrief,
    video_path: Optional[str] = None,
    captions_path: Optional[str] = None,
    seed: Optional[int] = 42,
    runtime_seconds: Optional[float] = None,
    output_dir: str = "outputs",
    resume: bool = True,
) -> Dict:
    """Run the pipeline and resume valid completed stages for identical inputs.

    State is saved atomically after each stage in a deterministic directory
    below ``outputs/runs``. Re-running after an interruption only executes the
    first missing or invalid artifact stage.
    """
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    run_key = build_run_key(brief.model_dump(), video_path, captions_path, seed)
    cache = RunCache(output_root, run_key, enabled=resume)
    run_dir = cache.run_dir if resume else output_root
    run_dir.mkdir(parents=True, exist_ok=True)
    logger = get_logger()

    plan_stage = cache.get("planning")
    if plan_stage and isinstance(plan_stage.get("scene_plan"), list):
        scene_plan = plan_stage["scene_plan"]
        _cache_hit(logger, "planning")
    else:
        scene_plan = create_scene_plan(brief)
        cache.set("planning", {"scene_plan": scene_plan})
        log_stage(logger, "planning", "Scene plan created", {"use_case": brief.use_case, "scene_count": len(scene_plan), "duration": brief.duration, "aspect_ratio": brief.aspect_ratio})

    route_stage = cache.get("routing")
    if route_stage and isinstance(route_stage.get("decision"), dict):
        decision = route_stage["decision"]
        _cache_hit(logger, "routing")
    else:
        decision = route_request(brief)
        route_path = run_dir / "route_decision.json"
        route_path.write_text(json.dumps(decision, indent=4), encoding="utf-8")
        cache.set("routing", {"decision": decision, "path": str(route_path)})
        log_stage(logger, "routing", "Model selected", {"model": decision["selected_model"], "score": decision["score"]})

    generation_stage = cache.get("generation")
    if generation_stage and is_usable_file(generation_stage.get("video")):
        video = Path(generation_stage["video"])
        generation_method, generation_model = generation_stage["method"], generation_stage["model"]
        generation_revision, generation_license = generation_stage["revision"], generation_stage["license"]
        _cache_hit(logger, "generation", str(video))
    else:
        video = Path(video_path) if video_path and Path(video_path).is_file() else None
        generation_method, generation_model = "model_output", decision["selected_model"]
        generation_revision, generation_license = "registry-reported", "registry-reported"
        if video is None:
            fallback = handle_generation_failure(primary_model=decision["selected_model"], candidates=decision["candidates"], error="Generated video artifact does not exist.")
            log_stage(logger, "generation", "Model artifact unavailable", fallback)
            video = run_dir / "workflow.mp4"
            create_workflow_video(use_case=brief.use_case, scene_plan=scene_plan, output_path=str(video), aspect_ratio=brief.aspect_ratio)
            generation_method, generation_model = "cpu_workflow_assembly", "none"
            generation_revision, generation_license = "not_applicable", "not_applicable"
            log_stage(logger, "generation", "CPU workflow assembly created", {"path": str(video), "duration": brief.duration, "aspect_ratio": brief.aspect_ratio, "workflow": brief.use_case})
        else:
            log_stage(logger, "generation", "Provided generation artifact found", {"path": str(video), "model": generation_model, "size_bytes": video.stat().st_size})
        cache.set("generation", {"video": str(video), "method": generation_method, "model": generation_model, "revision": generation_revision, "license": generation_license})

    timeline_stage = cache.get("timeline")
    if timeline_stage and is_usable_file(timeline_stage.get("path")):
        timeline_path = Path(timeline_stage["path"])
        _cache_hit(logger, "timeline", str(timeline_path))
    else:
        timeline_path = run_dir / "timeline.json"
        create_timeline_from_scene_plan(scene_plan=scene_plan, output_path=str(timeline_path), aspect_ratio=brief.aspect_ratio)
        cache.set("timeline", {"path": str(timeline_path)})
        log_stage(logger, "timeline", "Editable timeline created", {"path": str(timeline_path), "scene_count": len(scene_plan)})

    captions_stage = cache.get("captions")
    if captions_stage and is_usable_file(captions_stage.get("path")):
        active_captions_path = captions_stage["path"]
        _cache_hit(logger, "captions", active_captions_path)
    else:
        active_captions_path = captions_path or str(run_dir / "captions.srt")
        if captions_path is None:
            _create_script_captions(brief, scene_plan, active_captions_path)
            log_stage(logger, "captions", "Captions generated from script", {"path": active_captions_path, "scene_count": len(scene_plan)})
        if not is_usable_file(active_captions_path):
            raise FileNotFoundError(f"Captions file does not exist or is empty: {active_captions_path}")
        cache.set("captions", {"path": active_captions_path})

    final_stage = cache.get("final_video")
    if final_stage and is_usable_file(final_stage.get("path")):
        final_video_path = Path(final_stage["path"])
        _cache_hit(logger, "final_video", str(final_video_path))
    else:
        final_video_path = run_dir / "final.mp4"
        burn_captions(input_path=str(video), subtitle_path=active_captions_path, output_path=str(final_video_path))
        cache.set("final_video", {"path": str(final_video_path)})
        log_stage(logger, "captions", "Captions burned into final video", {"video": str(final_video_path), "captions": active_captions_path})

    validation_stage = cache.get("validation")
    if validation_stage and validation_stage.get("valid") is True:
        validation = validation_stage
        _cache_hit(logger, "validation")
    else:
        validation = validate_output(video_path=str(final_video_path), expected_duration=float(brief.duration), captions_path=active_captions_path, timeline_path=str(timeline_path))
        cache.set("validation", validation)
        log_stage(logger, "validation", "Video validation passed" if validation["valid"] else "Video validation failed", validation)

    manifest_stage = cache.get("manifest")
    if manifest_stage and is_usable_file(manifest_stage.get("path")):
        manifest_path = Path(manifest_stage["path"])
        _cache_hit(logger, "manifest", str(manifest_path))
    else:
        manifest_path = run_dir / "manifest.json"
        duration = validation["video"].get("duration_seconds", float(brief.duration))
        width, height = (1280, 720) if brief.aspect_ratio == "16:9" else (720, 1280)
        create_manifest(output_path=str(manifest_path), project_name=brief.title, model_name=generation_model, model_revision=generation_revision, model_license=generation_license, generation_method=generation_method, prompt=brief.script, seed=seed, output_file=str(final_video_path), duration_seconds=float(duration), width=width, height=height, fps=24, source_assets=[], runtime_seconds=runtime_seconds)
        cache.set("manifest", {"path": str(manifest_path)})
        log_stage(logger, "manifest", "Reproducibility manifest created", {"path": str(manifest_path), "generation_method": generation_method, "model": generation_model, "seed": seed})

    return {"status": "success" if validation["valid"] else "validation_failed", "generation_method": generation_method, "route_decision": decision, "timeline": str(timeline_path), "captions": active_captions_path, "manifest": str(manifest_path), "video": str(final_video_path), "validation": validation, "run_key": run_key, "resumed": resume}

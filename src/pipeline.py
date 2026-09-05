import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from src.planner.planner import CreativeBrief
from src.planner.workflows import create_scene_plan
from src.router.router import route_request
from src.router.fallback import handle_generation_failure
from src.assembly.timeline import create_timeline_from_scene_plan
from src.assembly.manifest import create_manifest
from src.assembly.workflow_video import create_workflow_video
from src.assembly.captions import create_srt
from src.assembly.ffmpeg import burn_captions
from src.validation.validator import validate_output
from src.logs.logger import get_logger, log_stage


def _split_script_into_chunks(
    script: str,
    count: int,
) -> List[str]:
    """
    Split the script into a practical number of caption chunks.

    Sentence boundaries are preferred. If there are fewer sentences
    than scenes, the remaining text is distributed by word count.
    """

    text = script.strip()

    if not text:
        return [""] * count

    sentences = [
        sentence.strip()
        for sentence in re.split(
            r"(?<=[.!?])\s+",
            text,
        )
        if sentence.strip()
    ]

    if len(sentences) >= count:
        chunks = sentences[:count]

        if len(sentences) > count:
            remaining = " ".join(sentences[count:])
            chunks[-1] = f"{chunks[-1]} {remaining}"

        return chunks

    words = text.split()

    if not words:
        return [""] * count

    chunks = []
    words_per_chunk = max(
        1,
        (len(words) + count - 1) // count,
    )

    for index in range(count):
        start = index * words_per_chunk
        end = start + words_per_chunk

        chunk = " ".join(words[start:end]).strip()

        if chunk:
            chunks.append(chunk)

    while len(chunks) < count:
        chunks.append(chunks[-1])

    return chunks[:count]


def _create_script_captions(
    brief: CreativeBrief,
    scene_plan: List[Dict],
    output_path: str,
) -> Path:
    """
    Create SRT captions aligned with the scene plan.
    """

    chunks = _split_script_into_chunks(
        brief.script,
        len(scene_plan),
    )

    captions = []

    for scene, text in zip(scene_plan, chunks):
        captions.append(
            {
                "start": scene["start"],
                "end": scene["end"],
                "text": text,
            }
        )

    return create_srt(
        captions=captions,
        output_path=output_path,
    )


def run_pipeline(
    brief: CreativeBrief,
    video_path: Optional[str] = None,
    captions_path: Optional[str] = None,
    seed: Optional[int] = 42,
    runtime_seconds: Optional[float] = None,
) -> Dict:
    """
    Run the complete video-generation orchestration pipeline.

    Stages:
        1. Planning
        2. Routing
        3. Generation artifact check
        4. CPU workflow assembly fallback
        5. Timeline creation
        6. Caption generation
        7. Caption burning
        8. Output validation
        9. Manifest creation
        10. Structured logging
    """

    output_dir = Path("outputs")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = get_logger()

    # ---------------------------------------------------------
    # 1. PLAN
    # ---------------------------------------------------------

    scene_plan = create_scene_plan(brief)

    log_stage(
        logger,
        stage="planning",
        message="Scene plan created",
        details={
            "use_case": brief.use_case,
            "scene_count": len(scene_plan),
            "duration": brief.duration,
            "aspect_ratio": brief.aspect_ratio,
        },
    )

    # ---------------------------------------------------------
    # 2. ROUTE
    # ---------------------------------------------------------

    decision = route_request(brief)

    route_path = output_dir / "route_decision.json"

    with open(
        route_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            decision,
            file,
            indent=4,
        )

    selected_model = decision["selected_model"]

    log_stage(
        logger,
        stage="routing",
        message="Model selected",
        details={
            "model": selected_model,
            "score": decision["score"],
        },
    )

    # ---------------------------------------------------------
    # 3. GENERATION ARTIFACT
    # ---------------------------------------------------------

    generation_method = "model_output"
    generation_model = selected_model
    generation_revision = "registry-reported"
    generation_license = "registry-reported"

    video = None

    if video_path is not None:
        candidate_video = Path(video_path)

        if candidate_video.exists():
            video = candidate_video

            log_stage(
                logger,
                stage="generation",
                message="Provided generation artifact found",
                details={
                    "path": str(video),
                    "model": selected_model,
                    "size_bytes": video.stat().st_size,
                },
            )

    # ---------------------------------------------------------
    # 4. CPU WORKFLOW ASSEMBLY FALLBACK
    # ---------------------------------------------------------

    if video is None:

        fallback = handle_generation_failure(
            primary_model=selected_model,
            candidates=decision["candidates"],
            error="Generated video artifact does not exist.",
        )

        log_stage(
            logger,
            stage="generation",
            message="Model artifact unavailable",
            details=fallback,
        )

        fallback_video_path = (
            output_dir
            / f"{brief.use_case}_workflow.mp4"
        )

        create_workflow_video(
            use_case=brief.use_case,
            scene_plan=scene_plan,
            output_path=str(fallback_video_path),
            aspect_ratio=brief.aspect_ratio,
        )

        video = fallback_video_path

        generation_method = "cpu_workflow_assembly"
        generation_model = "none"
        generation_revision = "not_applicable"
        generation_license = "not_applicable"

        log_stage(
            logger,
            stage="generation",
            message="CPU workflow assembly created",
            details={
                "path": str(video),
                "duration": brief.duration,
                "aspect_ratio": brief.aspect_ratio,
                "workflow": brief.use_case,
            },
        )

    # ---------------------------------------------------------
    # 5. CREATE EDITABLE TIMELINE
    # ---------------------------------------------------------

    timeline_path = (
        output_dir
        / f"{brief.use_case}_timeline.json"
    )

    create_timeline_from_scene_plan(
        scene_plan=scene_plan,
        output_path=str(timeline_path),
        aspect_ratio=brief.aspect_ratio,
    )

    log_stage(
        logger,
        stage="timeline",
        message="Editable timeline created",
        details={
            "path": str(timeline_path),
            "scene_count": len(scene_plan),
        },
    )

    # ---------------------------------------------------------
    # 6. CREATE CAPTIONS
    # ---------------------------------------------------------

    if captions_path is None:

        generated_captions_path = (
            output_dir
            / f"{brief.use_case}_captions.srt"
        )

        _create_script_captions(
            brief=brief,
            scene_plan=scene_plan,
            output_path=str(
                generated_captions_path
            ),
        )

        captions_path = str(
            generated_captions_path
        )

        log_stage(
            logger,
            stage="captions",
            message="Captions generated from script",
            details={
                "path": captions_path,
                "scene_count": len(scene_plan),
            },
        )

    # ---------------------------------------------------------
    # 7. BURN CAPTIONS
    # ---------------------------------------------------------

    captioned_video_path = (
        output_dir
        / f"{brief.use_case}_final.mp4"
    )

    burn_captions(
        input_path=str(video),
        subtitle_path=str(captions_path),
        output_path=str(captioned_video_path),
    )

    video = captioned_video_path

    log_stage(
        logger,
        stage="captions",
        message="Captions burned into final video",
        details={
            "video": str(video),
            "captions": captions_path,
        },
    )

    # ---------------------------------------------------------
    # 8. VALIDATE OUTPUT
    # ---------------------------------------------------------

    validation = validate_output(
        video_path=str(video),
        expected_duration=float(brief.duration),
        captions_path=captions_path,
        timeline_path=str(timeline_path),
    )

    log_stage(
        logger,
        stage="validation",
        message=(
            "Video validation passed"
            if validation["valid"]
            else "Video validation failed"
        ),
        details=validation,
    )

    # ---------------------------------------------------------
    # 9. CREATE MANIFEST
    # ---------------------------------------------------------

    manifest_path = (
        output_dir
        / f"{brief.use_case}_manifest.json"
    )

    video_duration = validation["video"].get(
        "duration_seconds",
        float(brief.duration),
    )

    if brief.aspect_ratio == "16:9":
        width = 1280
        height = 720
    else:
        width = 720
        height = 1280

    manifest = create_manifest(
        output_path=str(manifest_path),
        project_name=brief.title,
        model_name=generation_model,
        model_revision=generation_revision,
        model_license=generation_license,
        generation_method=generation_method,
        prompt=brief.script,
        seed=seed,
        output_file=str(video),
        duration_seconds=float(video_duration),
        width=width,
        height=height,
        fps=24,
        source_assets=[],
        runtime_seconds=runtime_seconds,
    )

    log_stage(
        logger,
        stage="manifest",
        message="Reproducibility manifest created",
        details={
            "path": str(manifest),
            "generation_method": generation_method,
            "model": generation_model,
            "seed": seed,
        },
    )

    # ---------------------------------------------------------
    # 10. RETURN RESULT
    # ---------------------------------------------------------

    return {
        "status": (
            "success"
            if validation["valid"]
            else "validation_failed"
        ),
        "generation_method": generation_method,
        "route_decision": decision,
        "timeline": str(timeline_path),
        "captions": str(captions_path),
        "manifest": str(manifest),
        "video": str(video),
        "validation": validation,
    }
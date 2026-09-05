from typing import Dict, List

from src.planner.planner import CreativeBrief
from src.router.capabilities import MODEL_REGISTRY, ModelCapability


def score_model(
    model: ModelCapability,
    brief: CreativeBrief,
) -> int:
    """
    Score a model against the creative brief.

    Scoring considers:
    - text-to-video support
    - duration compatibility
    - aspect-ratio compatibility
    - local execution availability
    - measured runtime
    - registry priority

    Capability facts and measurements are kept separate.
    """

    score = 0

    if model.supports_text_to_video:
        score += 3

    duration_supported = (
        model.min_duration
        <= brief.duration
        <= model.max_duration
    )

    if duration_supported:
        score += 3
    else:
        score -= 5

    aspect_supported = (
        brief.aspect_ratio
        in model.supported_aspect_ratios
    )

    if aspect_supported:
        score += 3
    else:
        score -= 5

    # A locally executable model is preferable when available.
    if model.locally_executable:
        score += 4

    # A measured runtime provides stronger evidence than
    # an unmeasured model estimate.
    if model.measured_runtime_seconds is not None:
        score += 2

    # Lower priority number means higher registry priority.
    score += max(0, 6 - model.priority)

    return score


def explain_model(
    model: ModelCapability,
    brief: CreativeBrief,
) -> Dict:
    """
    Return the capability checks used for routing.
    """

    duration_supported = (
        model.min_duration
        <= brief.duration
        <= model.max_duration
    )

    aspect_supported = (
        brief.aspect_ratio
        in model.supported_aspect_ratios
    )

    return {
        "model": model.name,
        "text_to_video": model.supports_text_to_video,
        "duration_supported": duration_supported,
        "aspect_ratio_supported": aspect_supported,
        "locally_executable": model.locally_executable,
        "measured_runtime_seconds": (
            model.measured_runtime_seconds
        ),
        "runtime_type": (
            "measured"
            if model.measured_runtime_seconds is not None
            else "not_measured"
        ),
        "license": model.license_name,
        "source_type": model.source_type,
    }


def route_request(
    brief: CreativeBrief,
) -> Dict:
    """
    Select the highest-scoring compatible video model.

    If no model supports the requested duration and aspect ratio,
    the router returns a CPU fallback decision.
    """

    scored_models: List[Dict] = []

    for model in MODEL_REGISTRY:
        score = score_model(
            model,
            brief,
        )

        compatibility = explain_model(
            model,
            brief,
        )

        scored_models.append(
            {
                **compatibility,
                "score": score,
            }
        )

    compatible_models = [
        item
        for item in scored_models
        if item["duration_supported"]
        and item["aspect_ratio_supported"]
        and item["text_to_video"]
    ]

    if not compatible_models:
        return {
            "selected_model": None,
            "score": None,
            "routing_status": "cpu_fallback",
            "reason": (
                "No registered model supports the requested "
                "text-to-video, duration and aspect ratio."
            ),
            "candidates": sorted(
                scored_models,
                key=lambda item: item["score"],
                reverse=True,
            ),
        }

    compatible_models.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    best = compatible_models[0]

    return {
        "selected_model": best["model"],
        "score": best["score"],
        "routing_status": "model_selected",
        "reason": (
            "Selected the highest-scoring compatible model "
            "using capability, local-execution, measured-runtime "
            "and priority evidence."
        ),
        "candidates": sorted(
            scored_models,
            key=lambda item: item["score"],
            reverse=True,
        ),
    }
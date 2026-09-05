from typing import Dict, Any


def choose_fallback(
    primary_model: str,
    candidates: list[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Choose the next available model when the primary model fails.

    The primary model is skipped and the remaining candidates
    are considered in score order.
    """

    for candidate in candidates:
        if candidate["model"] != primary_model:
            return {
                "fallback_type": "model",
                "selected_model": candidate["model"],
                "reason": "Primary model failed; selected next ranked candidate.",
            }

    return {
        "fallback_type": "cpu_assembly",
        "selected_model": None,
        "reason": "No alternative model available; use CPU assembly fallback.",
    }


def handle_generation_failure(
    primary_model: str,
    candidates: list[Dict[str, Any]],
    error: str,
) -> Dict[str, Any]:
    """
    Create a structured fallback decision after generation failure.
    """

    fallback = choose_fallback(
        primary_model=primary_model,
        candidates=candidates,
    )

    return {
        "status": "fallback",
        "primary_model": primary_model,
        "error": error,
        **fallback,
    }
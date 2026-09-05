from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ModelCapability:
    """
    Capability and provenance information for an open video model.

    Reported capabilities come from model documentation.
    Measured values come from our own experiments.
    """

    name: str
    supports_text_to_video: bool
    supports_image_to_video: bool
    min_duration: int
    max_duration: int
    supported_aspect_ratios: List[str]
    priority: int

    # Provenance
    license_name: str
    source_type: str = "reported"

    # Optional measured benchmark values
    measured_runtime_seconds: Optional[float] = None
    measured_vram_gb: Optional[float] = None

    # Whether the model can be executed directly in the
    # current local laptop environment.
    locally_executable: bool = False


MODEL_REGISTRY = [
    ModelCapability(
        name="wan2.1",
        supports_text_to_video=True,
        supports_image_to_video=True,
        min_duration=5,
        max_duration=30,
        supported_aspect_ratios=["16:9", "9:16"],
        priority=1,
        license_name="Apache-2.0",
        source_type="reported",
        locally_executable=False,
    ),
    ModelCapability(
        name="ltx-video",
        supports_text_to_video=True,
        supports_image_to_video=True,
        min_duration=2,
        max_duration=20,
        supported_aspect_ratios=["16:9", "9:16"],
        priority=2,
        license_name="LTXV Open Weights License",
        source_type="reported+measured",
        measured_runtime_seconds=19.0,
        locally_executable=False,
    ),
    ModelCapability(
        name="cogvideox",
        supports_text_to_video=True,
        supports_image_to_video=False,
        min_duration=5,
        max_duration=20,
        supported_aspect_ratios=["16:9"],
        priority=3,
        license_name="Apache-2.0",
        source_type="reported",
        locally_executable=False,
    ),
    ModelCapability(
        name="hunyuanvideo",
        supports_text_to_video=True,
        supports_image_to_video=True,
        min_duration=5,
        max_duration=30,
        supported_aspect_ratios=["16:9", "9:16"],
        priority=4,
        license_name="Tencent Hunyuan Community License",
        source_type="reported",
        locally_executable=False,
    ),
    ModelCapability(
        name="mochi-1",
        supports_text_to_video=True,
        supports_image_to_video=False,
        min_duration=5,
        max_duration=20,
        supported_aspect_ratios=["16:9"],
        priority=5,
        license_name="Apache-2.0",
        source_type="reported",
        locally_executable=False,
    ),
]


def get_model(name: str) -> Optional[ModelCapability]:
    """Return a registered model by name."""

    for model in MODEL_REGISTRY:
        if model.name == name:
            return model

    return None
from pathlib import Path
from typing import Optional

from src.generators.base import VideoGenerator


class LTXVideoGenerator(VideoGenerator):
    """
    Adapter for the LTX-Video generation workflow.

    The actual LTX model execution is performed in the approved
    free-compute environment. This adapter records the generated
    artifact and its provenance for the local pipeline.
    """

    def __init__(
        self,
        model_name: str = "LTX-Video 2B distilled",
        model_revision: str = "ltxv-2b-0.9.6-distilled-04-25",
        model_path: Optional[str] = None,
        license_name: str = "LTXV Open Weights License",
    ):
        self.model_name = model_name
        self.model_revision = model_revision
        self.model_path = model_path
        self.license_name = license_name

    def generate(
        self,
        prompt: str,
        output_path: str,
        source_video: Optional[str] = None,
        seed: int = 42,
        runtime_seconds: Optional[float] = None,
    ) -> dict:
        """
        Register a previously generated LTX artifact.

        The actual generation is executed on approved free compute.
        This local adapter integrates the resulting MP4 into the
        orchestration pipeline.
        """

        output = Path(output_path)

        if not output.exists():
            raise FileNotFoundError(
                f"LTX output does not exist: {output}"
            )

        if output.suffix.lower() != ".mp4":
            raise ValueError(
                "LTX generator output must be an MP4 file."
            )

        if output.stat().st_size == 0:
            raise ValueError(
                "LTX output file is empty."
            )

        return {
            "status": "success",
            "generator": "ltx-video",
            "model": self.model_name,
            "model_revision": self.model_revision,
            "model_license": self.license_name,
            "model_path": self.model_path,
            "prompt": prompt,
            "seed": seed,
            "output_path": str(output),
            "source_video": source_video,
            "runtime_seconds": runtime_seconds,
            "runtime_type": (
                "measured"
                if runtime_seconds is not None
                else "not_measured"
            ),
        }
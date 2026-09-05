import json
from pathlib import Path
from typing import Dict, List, Optional


def create_manifest(
    output_path: str,
    project_name: str,
    model_name: str,
    model_revision: str,
    model_license: str,
    generation_method: str,
    prompt: str,
    seed: Optional[int],
    output_file: str,
    duration_seconds: float,
    width: int,
    height: int,
    fps: int,
    source_assets: Optional[List[Dict]] = None,
    runtime_seconds: Optional[float] = None,
) -> Path:
    """
    Create a reproducibility and asset/model manifest.

    The manifest records:
    - model provenance
    - license
    - prompt
    - seed
    - output information
    - source assets
    - measured runtime
    """

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    manifest = {
        "project": project_name,
        "generation": {
            "method": generation_method,
            "model": model_name,
            "model_revision": model_revision,
            "model_license": model_license,
            "prompt": prompt,
            "seed": seed,
        },
        "output": {
            "file": output_file,
            "format": "mp4",
            "duration_seconds": duration_seconds,
            "width": width,
            "height": height,
            "fps": fps,
        },
        "source_assets": source_assets or [],
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "runtime_type": (
                "measured"
                if runtime_seconds is not None
                else "not_measured"
            ),
        },
    }

    with open(output, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

    return output
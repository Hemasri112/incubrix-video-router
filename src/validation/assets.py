from pathlib import Path
from typing import Dict, List


SUPPORTED_ASSET_TYPES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".mp4",
    ".wav",
    ".mp3",
}


def validate_asset(asset_path: str) -> Dict:
    """
    Validate a single source asset.

    Checks:
    - asset exists
    - asset is a file
    - asset is not empty
    - file extension is supported
    """

    path = Path(asset_path)

    result = {
        "path": str(path),
        "valid": True,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "non_empty": False,
        "extension_supported": False,
        "errors": [],
    }

    if not path.exists():
        result["valid"] = False
        result["errors"].append(
            "Asset does not exist."
        )
        return result

    if not path.is_file():
        result["valid"] = False
        result["errors"].append(
            "Asset path is not a file."
        )
        return result

    result["non_empty"] = path.stat().st_size > 0

    if not result["non_empty"]:
        result["valid"] = False
        result["errors"].append(
            "Asset file is empty."
        )

    extension = path.suffix.lower()

    result["extension_supported"] = (
        extension in SUPPORTED_ASSET_TYPES
    )

    if not result["extension_supported"]:
        result["valid"] = False
        result["errors"].append(
            f"Unsupported asset type: {extension}"
        )

    return result


def validate_assets(
    asset_paths: List[str],
) -> Dict:
    """
    Validate multiple source assets.
    """

    if not asset_paths:
        raise ValueError(
            "At least one asset path is required."
        )

    results = [
        validate_asset(path)
        for path in asset_paths
    ]

    valid = all(
        result["valid"]
        for result in results
    )

    return {
        "valid": valid,
        "total_assets": len(results),
        "valid_assets": sum(
            result["valid"]
            for result in results
        ),
        "invalid_assets": sum(
            not result["valid"]
            for result in results
        ),
        "assets": results,
    }
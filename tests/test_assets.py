from pathlib import Path

import pytest

from src.validation.assets import (
    validate_asset,
    validate_assets,
)


def test_valid_asset(tmp_path):
    asset = tmp_path / "image.png"
    asset.write_bytes(b"fake image data")

    result = validate_asset(str(asset))

    assert result["valid"] is True
    assert result["exists"] is True
    assert result["is_file"] is True
    assert result["non_empty"] is True
    assert result["extension_supported"] is True


def test_missing_asset():
    result = validate_asset(
        "outputs/missing_asset.png"
    )

    assert result["valid"] is False
    assert "Asset does not exist." in result["errors"]


def test_empty_asset(tmp_path):
    asset = tmp_path / "empty.png"
    asset.touch()

    result = validate_asset(str(asset))

    assert result["valid"] is False
    assert "Asset file is empty." in result["errors"]


def test_unsupported_asset_type(tmp_path):
    asset = tmp_path / "document.txt"
    asset.write_text("test", encoding="utf-8")

    result = validate_asset(str(asset))

    assert result["valid"] is False
    assert result["extension_supported"] is False


def test_multiple_assets(tmp_path):
    image = tmp_path / "image.png"
    audio = tmp_path / "audio.wav"

    image.write_bytes(b"image")
    audio.write_bytes(b"audio")

    result = validate_assets(
        [
            str(image),
            str(audio),
        ]
    )

    assert result["valid"] is True
    assert result["total_assets"] == 2
    assert result["valid_assets"] == 2
    assert result["invalid_assets"] == 0


def test_multiple_assets_with_failure(tmp_path):
    image = tmp_path / "image.png"
    image.write_bytes(b"image")

    result = validate_assets(
        [
            str(image),
            str(tmp_path / "missing.png"),
        ]
    )

    assert result["valid"] is False
    assert result["total_assets"] == 2
    assert result["valid_assets"] == 1
    assert result["invalid_assets"] == 1


def test_empty_asset_list():
    with pytest.raises(ValueError):
        validate_assets([])
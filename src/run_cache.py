"""Persistent, per-input state for resumable pipeline runs."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


def _file_identity(path: Optional[str]) -> Optional[Dict[str, Any]]:
    """Return provenance for an optional user-supplied file."""
    if path is None:
        return None
    candidate = Path(path).resolve()
    identity: Dict[str, Any] = {"path": str(candidate)}
    if candidate.exists():
        stat = candidate.stat()
        identity.update({"size": stat.st_size, "mtime_ns": stat.st_mtime_ns})
    return identity


def build_run_key(brief_data: Dict[str, Any], video_path: Optional[str], captions_path: Optional[str], seed: Optional[int]) -> str:
    """Create a deterministic key for inputs that affect generated artifacts."""
    payload = {"brief": brief_data, "video": _file_identity(video_path), "captions": _file_identity(captions_path), "seed": seed}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def is_usable_file(path: Optional[str]) -> bool:
    """True only for a non-empty artifact still present on disk."""
    if not path:
        return False
    candidate = Path(path)
    return candidate.is_file() and candidate.stat().st_size > 0


class RunCache:
    """Small JSON state store written atomically after every completed stage."""

    def __init__(self, output_root: Path, run_key: str, enabled: bool = True) -> None:
        self.enabled = enabled
        self.run_key = run_key
        self.run_dir = output_root / "runs" / run_key
        self.state_path = self.run_dir / "run_state.json"
        self.state: Dict[str, Any] = {"run_key": run_key, "stages": {}}
        if self.enabled:
            self.run_dir.mkdir(parents=True, exist_ok=True)
            self._load()

    def _load(self) -> None:
        if not self.state_path.exists():
            return
        try:
            with open(self.state_path, "r", encoding="utf-8") as file:
                candidate = json.load(file)
        except (json.JSONDecodeError, OSError):
            return
        if candidate.get("run_key") == self.run_key:
            self.state = candidate
            self.state.setdefault("stages", {})

    def get(self, stage: str) -> Optional[Dict[str, Any]]:
        value = self.state.get("stages", {}).get(stage)
        return value if isinstance(value, dict) else None

    def set(self, stage: str, value: Dict[str, Any]) -> None:
        self.state.setdefault("stages", {})[stage] = value
        if self.enabled:
            temporary = self.state_path.with_suffix(".tmp")
            with open(temporary, "w", encoding="utf-8") as file:
                json.dump(self.state, file, indent=2)
            os.replace(temporary, self.state_path)

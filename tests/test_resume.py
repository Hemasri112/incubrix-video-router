from pathlib import Path

import pytest

from src.pipeline import run_pipeline
from src.planner.planner import CreativeBrief


def _brief():
    return CreativeBrief(
        title="Resume Test",
        use_case="education",
        script="One sentence. Two sentence.",
        duration=15,
        aspect_ratio="16:9",
    )


def _install_fast_stages(monkeypatch, fail_first_burn=False):
    """Replace ffmpeg work with deterministic tiny artifacts for cache tests."""
    import src.pipeline as pipeline

    calls = {"workflow": 0, "burn": 0}

    monkeypatch.setattr(pipeline, "create_scene_plan", lambda brief: [{"start": 0, "end": 15}])
    monkeypatch.setattr(pipeline, "route_request", lambda brief: {"selected_model": "LTX-Video", "score": 1, "candidates": ["LTX-Video"]})
    monkeypatch.setattr(pipeline, "handle_generation_failure", lambda **kwargs: kwargs)

    def workflow(**kwargs):
        calls["workflow"] += 1
        Path(kwargs["output_path"]).write_bytes(b"workflow")

    def timeline(**kwargs):
        Path(kwargs["output_path"]).write_text("{}", encoding="utf-8")

    def captions(brief, scene_plan, output_path):
        Path(output_path).write_text("caption", encoding="utf-8")
        return Path(output_path)

    def burn(**kwargs):
        calls["burn"] += 1
        if fail_first_burn and calls["burn"] == 1:
            raise RuntimeError("simulated interruption")
        Path(kwargs["output_path"]).write_bytes(b"final")

    monkeypatch.setattr(pipeline, "create_workflow_video", workflow)
    monkeypatch.setattr(pipeline, "create_timeline_from_scene_plan", timeline)
    monkeypatch.setattr(pipeline, "_create_script_captions", captions)
    monkeypatch.setattr(pipeline, "burn_captions", burn)
    monkeypatch.setattr(pipeline, "validate_output", lambda **kwargs: {"valid": True, "video": {"duration_seconds": 15}, "checks": {}})
    return calls


def test_interrupted_run_resumes_from_saved_generation_artifact(tmp_path, monkeypatch):
    calls = _install_fast_stages(monkeypatch, fail_first_burn=True)

    with pytest.raises(RuntimeError, match="simulated interruption"):
        run_pipeline(_brief(), output_dir=str(tmp_path))

    resumed = run_pipeline(_brief(), output_dir=str(tmp_path))

    assert resumed["status"] == "success"
    assert calls == {"workflow": 1, "burn": 2}
    state_path = tmp_path / "runs" / resumed["run_key"] / "run_state.json"
    assert state_path.is_file()
    assert not state_path.with_suffix(".tmp").exists()


def test_completed_run_reuses_all_file_artifacts(tmp_path, monkeypatch):
    calls = _install_fast_stages(monkeypatch)

    first = run_pipeline(_brief(), output_dir=str(tmp_path))
    second = run_pipeline(_brief(), output_dir=str(tmp_path))

    assert first["video"] == second["video"]
    assert calls == {"workflow": 1, "burn": 1}


def test_changed_seed_creates_an_independent_run(tmp_path, monkeypatch):
    calls = _install_fast_stages(monkeypatch)

    first = run_pipeline(_brief(), output_dir=str(tmp_path), seed=1)
    second = run_pipeline(_brief(), output_dir=str(tmp_path), seed=2)

    assert first["run_key"] != second["run_key"]
    assert calls == {"workflow": 2, "burn": 2}

import json
from pathlib import Path

from src.pipeline import run_pipeline
from src.planner.planner import CreativeBrief


def test_cpu_fallback_pipeline_end_to_end(tmp_path):
    """Run the complete local pipeline without a model-generation artifact."""
    brief = CreativeBrief(title="End-to-End Education Draft", use_case="education", script="Learn the basics. Practice with a small example.", duration=15, aspect_ratio="16:9")
    result = run_pipeline(brief=brief, output_dir=str(tmp_path))

    assert result["status"] == "success"
    assert result["generation_method"] == "cpu_workflow_assembly"
    for artifact in ("video", "captions", "timeline", "manifest"):
        path = Path(result[artifact])
        assert path.is_file()
        assert path.stat().st_size > 0

    manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
    assert manifest["generation"]["method"] == "cpu_workflow_assembly"
    assert manifest["output"]["file"] == result["video"]
    assert result["validation"]["valid"] is True

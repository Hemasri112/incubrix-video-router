# IncuBrix Video Router - Test Plan

## 1. Purpose

This test pack documents functional, failure, validation, cache/resume and end-to-end tests for the video-generation routing system.

## 2. Required Test Matrix

| Test | Description | Expected Result |
|---|---|---|
| Baseline | Generate a valid 15-second brief | Successful MP4 |
| Education | Education workflow | Education scene structure |
| News | News workflow | News scene structure |
| Product | Product workflow | Product scene structure |
| 16:9 | Generate landscape output | Valid 16:9 MP4 |
| 9:16 | Generate portrait output | Valid 9:16 MP4 |
| Invalid brief | Missing/invalid required field | Validation failure |
| Model failure | Generation artifact unavailable | CPU fallback |
| Missing asset | Missing source asset | Asset validation failure |
| Corrupt asset | Empty/invalid asset | Asset validation failure |
| Timeline | Create editable timeline | Valid timeline JSON |
| Captions | Generate captions | Valid SRT |
| Output validation | Validate generated MP4 | Valid output |
| Cache/resume | Retry an interrupted matching run | Completed artifacts are reused |
| End-to-end | Execute the complete CPU fallback path | Valid MP4, SRT, timeline and manifest |
| Benchmark | Evaluate 10 varied briefs | Benchmark summary |

## 3. Automated Tests

Run the suite with:

```text
python -m pytest -q
```

The suite covers planner validation, workflow planning, router behavior, fallback handling, generator behavior, asset validation, video validation, captions, timeline, manifest, workflow video generation, evaluation metrics, benchmark behavior, cache/resume, and an explicit end-to-end pipeline path.

Expected result after the cache/resume and E2E additions:

```text
47 passed
```

The E2E test uses CPU workflow assembly. It does not invoke LTX-Video or any other model inference.

## 4. Benchmark Test

The 10-brief benchmark contains four education briefs, three news briefs, three product briefs, six landscape briefs and four portrait briefs.

Measured result:

- Total briefs: 10
- Successful renders: 10
- Render success rate: 100%
- Route accuracy: 100%
- Average local pipeline latency: approximately 2.10 seconds

The benchmark latency measures routing and CPU workflow assembly. It is not generative-model inference latency.

## 5. Generative Model Evidence

LTX-Video was successfully executed on an approved free Google Colab Tesla T4 environment.

Measured configuration:

- Model: LTX-Video 2B distilled
- Revision: ltxv-2b-0.9.6-distilled-04-25
- GPU: Tesla T4
- Frames: 25
- Resolution: 512 x 768
- FPS: 8
- Steps: 8
- Seed: 42
- Runtime: approximately 19 seconds

## 6. Failure Handling

The system handles invalid creative briefs, unsupported workflows or aspect ratios, missing video artifacts, missing/empty/unsupported assets, invalid captions or timelines, FFmpeg failures, output validation failures, and interrupted local runs.

## 7. Evidence Index

| Assessment claim | Evidence | How to verify |
|---|---|---|
| Three materially different workflows | `src/planner/workflows.py`, `tests/test_workflows.py` | `python -m pytest tests/test_workflows.py -q` |
| Capability-based routing and fallback | `src/router/`, `tests/test_router.py`, `tests/test_fallback.py` | `python -m pytest tests/test_router.py tests/test_fallback.py -q` |
| Local CPU assembly, captions and validation | `src/assembly/`, `src/validation/`, `tests/test_workflow_video.py`, `tests/test_validation.py` | `python -m pytest tests/test_workflow_video.py tests/test_validation.py -q` |
| Complete local orchestration path | `src/pipeline.py`, `tests/test_pipeline_e2e.py` | `python -m pytest tests/test_pipeline_e2e.py -q` |
| Cache/resume after interruption | `src/run_cache.py`, `src/pipeline.py`, `tests/test_resume.py` | `python -m pytest tests/test_resume.py -q` |
| Deterministic provenance and manifest | `src/assembly/manifest.py`, `src/pipeline.py` | Inspect generated `outputs/runs/<run-key>/manifest.json` |
| Ten-brief routing benchmark | `examples/benchmark_10.json`, `src/evaluation/benchmark.py`, `tests/test_benchmark.py` | `python -m src.cli benchmark --briefs examples/benchmark_10.json` |
| Measured LTX execution | `notebooks/ltx_t4_baseline.ipynb`, `SOURCES.md`, `docs/TECHNICAL_REPORT.md` | Review the notebook and report; do not claim reported values as measured |

## 8. Evidence Boundary

Project measurements are explicitly separated from model-author-reported specifications. The five researched models are documented in `SOURCES.md`. Only successful project executions are described as measured executions.


# IncuBrix Open-Source Draft Video Generation and Model Routing

## 1. Project Overview

This project implements a local video-generation orchestration and model-routing system for creating short draft videos from structured creative briefs.

The system separates:

- creative brief validation
- workflow planning
- model capability evaluation
- model routing
- video generation artifact handling
- CPU/FFmpeg fallback assembly
- captions
- editable timeline generation
- output validation
- reproducibility metadata
- benchmarking
- structured logging

The system is designed to run its planning, routing, validation, assembly, logging and evaluation locally on a non-GPU laptop.

At least one open/open-weight video model was executed using approved free accelerator compute.

---

## 2. Architecture

```text
Creative Brief
      |
      v
Brief Validator
      |
      v
Workflow Planner
      |
      v
Capability Registry
      |
      v
Model Router
      |
      +----------------------+
      |                      |
      v                      v
Video Model             CPU/FFmpeg Fallback
      |                      |
      +----------+-----------+
                 |
                 v
        Video Assembly
                 |
                 v
            Captions
                 |
                 v
          Output Validation
                 |
        +--------+--------+
        |        |        |
        v        v        v
       MP4    Timeline   Manifest
              JSON       JSON
                 |
                 v
          Structured Logs
```

---

## 3. Supported Workflows

The system currently supports three materially different workflows.

### Education

Scene structure:

```text
Hook
Concept Explanation
Example
Summary
```

Characteristics:

- moderate pacing
- clean educational visuals
- instructional captions
- concept-oriented scene structure

### News

Scene structure:

```text
Headline
Context
Key Development
Impact
Closing
```

Characteristics:

- fast pacing
- news-style visual treatment
- headline-focused captions
- context and impact sections

### Product

Scene structure:

```text
Hook
Problem
Product Showcase
Benefits
Call To Action
```

Characteristics:

- fast pacing
- product-focused visuals
- dynamic visual treatment
- short promotional captions

---

## 4. Input Contract

The system accepts a structured creative brief.

Example:

```json
{
    "title": "Python Variables",
    "use_case": "education",
    "script": "Python variables store values that can be reused in a program.",
    "duration": 15,
    "aspect_ratio": "16:9",
    "style": "clean educational",
    "constraints": [
        "simple visuals",
        "clear captions"
    ]
}
```

### Required fields

- `title`
- `use_case`
- `script`
- `duration`
- `aspect_ratio`

### Optional fields

- `style`
- `constraints`

### Supported use cases

```text
education
news
product
```

### Supported aspect ratios

```text
16:9
9:16
```

### Duration

The current planner accepts durations greater than 0 and up to 60 seconds.

---

## 5. Output Contract

The pipeline produces:

### MP4 video

Final assembled video with captions.

Example:

```text
outputs/education_final.mp4
```

### Editable timeline

```text
outputs/education_timeline.json
```

The timeline contains:

- scene IDs
- start times
- durations
- source references
- prompts
- caption style
- aspect ratio

### Route decision

```text
outputs/route_decision.json
```

The routing result records:

- selected model
- routing score
- compatibility checks
- license information
- local execution status
- measured runtime when available
- candidate models

### Captions

```text
outputs/education_captions.srt
```

### Manifest

```text
outputs/education_manifest.json
```

The manifest records:

- model
- model revision
- license
- generation method
- prompt
- seed
- output information
- source assets
- measured runtime

### Logs

Structured logs are written to the `logs/` directory.

---

## 6. Repository Structure

```text
incubrix-video-router/
|
├── src/
│   ├── planner/
│   │   ├── planner.py
│   │   └── workflows.py
│   │
│   ├── router/
│   │   ├── capabilities.py
│   │   ├── router.py
│   │   └── fallback.py
│   │
│   ├── generators/
│   │   ├── base.py
│   │   ├── mock_generator.py
│   │   └── ltx_generator.py
│   │
│   ├── assembly/
│   │   ├── ffmpeg.py
│   │   ├── captions.py
│   │   ├── timeline.py
│   │   ├── manifest.py
│   │   └── workflow_video.py
│   │
│   ├── validation/
│   │   ├── validator.py
│   │   └── assets.py
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── benchmark.py
│   │
│   ├── logs/
│   │   └── logger.py
│   │
│   └── pipeline.py
│
├── tests/
│
├── configs/
├── examples/
├── outputs/
├── logs/
├── notebooks/
│
├── README.md
├── SOURCES.md
├── AI_USE.md
└── requirements.txt
```

---

## 7. Local Environment

The local pipeline is designed for CPU execution.

### Requirements

- Python 3.11
- FFmpeg
- pip
- Windows/Linux/macOS

The project was developed and tested using Python 3.11.

---

## 8. Installation

Create and activate the virtual environment:

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Verify Python:

```powershell
python --version
```

Verify FFmpeg:

```powershell
ffmpeg -version
```

---

## 9. Running Tests

Run the complete test suite:

```powershell
pytest -v
```

The project contains tests covering:

- brief validation
- workflow planning
- model routing
- fallback handling
- asset validation
- generator behavior
- timeline generation
- captions
- workflow video assembly
- output validation
- evaluation metrics
- benchmark behavior

---

## 10. Example Briefs

Example briefs are provided in:

```text
examples/
```

Current examples include:

```text
examples/education_brief.json
examples/news_brief.json
examples/product_brief.json
examples/benchmark_10.json
```

The benchmark file contains 10 varied briefs covering:

- education
- news
- product
- 16:9
- 9:16

---

## 11. Benchmark

The benchmark evaluates the local routing and assembly pipeline using 10 varied briefs.

Run the benchmark using the project's benchmark entry point.

The benchmark records:

- total briefs
- successful renders
- render success rate
- selected models
- expected routes
- route accuracy
- latency
- use-case statistics
- aspect-ratio statistics

Benchmark artifacts are preserved under:

```text
outputs/benchmark/
```

Each benchmark case has its own directory so that previous results are not overwritten.

### Important measurement boundary

The 10-brief benchmark measures the local routing and CPU workflow assembly pipeline.

It does NOT represent ten generative-model inference runs.

The current benchmark successfully rendered all 10 briefs through the local workflow assembly path.

Measured benchmark result:

```text
Total briefs: 10
Successful renders: 10
Render success rate: 100%
Route accuracy: 100%
Average latency: approximately 2.10 seconds
```

The latency measurement represents local pipeline execution and should not be interpreted as video-model inference latency.

---

## 12. Model Research

Five open/open-weight video models were researched:

1. LTX-Video
2. Wan2.1
3. CogVideoX-2B
4. HunyuanVideo
5. Mochi-1

Detailed sources, licenses, reported hardware requirements and execution status are documented in:

```text
SOURCES.md
```

The system distinguishes reported model information from measurements performed by this project.

---

## 13. LTX-Video Execution

LTX-Video was successfully executed using a free Google Colab Tesla T4 accelerator.

Model revision:

```text
ltxv-2b-0.9.6-distilled-04-25
```

Measured configuration:

```text
GPU: Tesla T4
Frames: 25
Resolution: 512 x 768
FPS: 8
Inference steps: 8
Seed: 42
Runtime: approximately 19 seconds
```

The successful generation artifact was:

```text
ltx_baseline_test.mp4
```

The generated model artifact is preserved separately from the local CPU assembly pipeline.

---

## 14. Free Compute Execution

The actual generative model execution is performed in an approved free accelerator environment.

The local laptop pipeline does not require a GPU for:

- planning
- routing
- validation
- captions
- timeline generation
- FFmpeg assembly
- logging
- benchmarking
- evaluation

The successful LTX-Video execution notebook is stored/exported under:

```text
notebooks/
```

The notebook records the model revision, execution configuration, seed and generated artifact.

---

## 15. CPU Fallback

If a usable model-generated video artifact is unavailable, the local system can create a deterministic workflow video using FFmpeg.

The fallback:

- does not claim AI-generated content
- creates workflow-specific visuals
- creates the requested duration
- supports 16:9 and 9:16
- generates captions
- creates timeline metadata
- validates the final MP4

The fallback allows the rest of the pipeline to remain operational even when model generation is unavailable.

---

## 16. Validation

The output validator checks:

- file existence
- non-empty output
- MP4 output
- FFprobe readability
- video duration
- expected duration tolerance
- captions
- timeline

Asset validation additionally checks:

- existence
- file type
- non-empty content
- supported extension

---

## 17. Reproducibility

The project records reproducibility information including:

- model name
- model revision
- prompt
- seed
- generation method
- output path
- license information
- runtime when measured
- source assets

Model facts reported by external sources are explicitly separated from project measurements.

---

## 18. Error Handling and Fallback

The routing system evaluates model capabilities before selection.

Compatibility checks include:

- text-to-video support
- duration
- aspect ratio
- local execution availability
- measured runtime evidence
- registry priority

If generation fails or an expected model artifact is unavailable, the system records the failure and uses the local CPU assembly fallback.

The fallback decision is recorded in structured output/log information.

---

## 19. Determinism

The project uses deterministic seeds where supported.

The current LTX baseline execution used:

```text
Seed: 42
```

The seed is stored in the generation manifest.

---

## 20. Licensing

The project uses open-source/local components where possible.

Model licensing information is documented in:

```text
SOURCES.md
```

Users must verify the current license of a model/checkpoint before redistribution or commercial use.

---

## 21. AI-Assisted Development

AI coding assistance was used during development.

All material AI-assisted development is disclosed in:

```text
AI_USE.md
```

The candidate remains responsible for the final implementation, testing, debugging and live modification of the system.

---

## 22. Assessment Evidence

The repository is structured to provide evidence for:

- baseline video generation
- three workflow types
- 16:9 and 9:16 outputs
- model capability registry
- routing decisions
- CPU fallback
- captions
- editable timeline
- asset/model manifest
- validation
- structured logging
- automated tests
- 10-brief benchmark
- five-model research
- reproducible LTX-Video execution

---

## 23. Current Limitations

The following limitations are intentionally documented.

### Model execution

Only LTX-Video has been successfully executed in the available free accelerator environment.

The other four models are documented as researched candidates and are not represented as successfully executed by this project.

### Generated text

The LTX baseline can produce distorted text-like visual artifacts.

Final captions are therefore generated locally rather than relying on generated text inside the video model output.

### Benchmark interpretation

The 10-brief benchmark measures the local routing and assembly pipeline.

It does not represent ten generative-model inference executions.

### Model fallback

The current fallback path records the next candidate model when applicable, but the implemented execution path ultimately uses CPU workflow assembly when a usable model artifact is unavailable.

---

## 24. Reproduction Summary

A CPU-only reproduction of the local orchestration pipeline requires:

```text
Python 3.11
FFmpeg
Project dependencies
```

The high-level reproduction flow is:

```text
Creative Brief
    ->
Validation
    ->
Workflow Planning
    ->
Model Routing
    ->
Generation Artifact / CPU Fallback
    ->
Timeline
    ->
Captions
    ->
FFmpeg Assembly
    ->
Validation
    ->
Manifest + Logs
```

The generative-model portion requires the approved free accelerator notebook.

---

## 25. Key Files

| File | Purpose |
|---|---|
| `src/planner/planner.py` | Creative brief validation |
| `src/planner/workflows.py` | Workflow-specific scene planning |
| `src/router/capabilities.py` | Model capability registry |
| `src/router/router.py` | Model routing |
| `src/router/fallback.py` | Failure/fallback decisions |
| `src/generators/ltx_generator.py` | LTX artifact integration |
| `src/assembly/ffmpeg.py` | FFmpeg operations |
| `src/assembly/workflow_video.py` | CPU workflow video assembly |
| `src/assembly/captions.py` | SRT caption generation |
| `src/assembly/timeline.py` | Editable timeline generation |
| `src/assembly/manifest.py` | Reproducibility manifest |
| `src/validation/validator.py` | Video validation |
| `src/validation/assets.py` | Asset validation |
| `src/evaluation/metrics.py` | Evaluation metrics |
| `src/evaluation/benchmark.py` | Benchmark execution |
| `src/pipeline.py` | End-to-end orchestration |
| `SOURCES.md` | Five-model research and sources |
| `AI_USE.md` | AI assistance disclosure |

---





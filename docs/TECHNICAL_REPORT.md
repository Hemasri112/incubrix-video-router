# IncuBrix Video Generation and Model Routing
## Technical Report

## 1. Executive Summary

This project implements a local orchestration and model-routing system for generating short draft videos from structured creative briefs.

The system separates creative planning, model capability evaluation, routing, generation-artifact handling, CPU/FFmpeg fallback, captions, editable timeline generation, validation, structured logging and evaluation.

The local pipeline is designed to execute on a non-GPU laptop.

The project also includes a reproducible open-model execution path. LTX-Video was successfully executed using an approved free Google Colab Tesla T4 accelerator.

The project researched five open/open-weight video models:

1. LTX-Video
2. Wan2.1
3. CogVideoX-2B
4. HunyuanVideo
5. Mochi-1

The implementation intentionally distinguishes reported model capabilities from measurements performed by this project.



## 2. Problem Statement

The system must transform a structured creative brief into a reproducible short-form draft video.

The input contains:

- title
- use case
- script
- duration
- aspect ratio
- optional style
- optional constraints

The system then:

1. validates the brief
2. selects a workflow
3. creates a scene plan
4. evaluates available model capabilities
5. selects a routing candidate
6. handles a model-generated artifact when available
7. falls back to local CPU/FFmpeg assembly when required
8. creates captions
9. creates an editable timeline
10. validates the final output
11. records reproducibility metadata
12. records structured logs and evaluation results



## 3. System Architecture

text
Creative Brief
      |
      v
Brief Validation
      |
      v
Workflow Planning
      |
      v
Capability Registry
      |
      v
Model Routing
      |
      +----------------------+
      |                      |
      v                      v
Video Model          CPU/FFmpeg Fallback
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
       MP4    Timeline  Manifest
                JSON      JSON
                 |
                 v
          Structured Logs


The architecture separates model execution from the local orchestration layer.

The laptop is responsible for:

- brief validation
- workflow planning
- routing
- fallback handling
- captions
- timeline generation
- FFmpeg assembly
- validation
- logging
- benchmarking
- evaluation

The generative model execution is performed separately in the approved free accelerator environment.



## 4. Workflow Design

The system implements three materially different workflow templates.

### 4.1 Education

Scene structure:

text
Hook
Concept Explanation
Example
Summary


The education workflow uses moderate pacing, concept-oriented scenes, clean educational visual treatment and instructional captions.

### 4.2 News

Scene structure:

text
Headline
Context
Key Development
Impact
Closing


The news workflow uses faster pacing, headline-focused captions and separate context, development and impact sections.

### 4.3 Product

Scene structure:

text
Hook
Problem
Product Showcase
Benefits
Call To Action


The product workflow uses faster pacing, product-focused visual treatment and short promotional captions.

The workflow templates therefore differ in:

- scene structure
- pacing
- visual strategy
- caption style
- content progression



## 5. Input and Output Contract

### Input

Creative briefs are represented as JSON.

Example:

json
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


Required fields are:

- `title`
- `use_case`
- `script`
- `duration`
- `aspect_ratio`

Supported use cases:


education
news
product


Supported aspect ratios:


16:9
9:16


The current planner accepts durations greater than zero and up to 60 seconds.

### Outputs

The pipeline produces:

- MP4 video
- editable `timeline.json`
- `route_decision.json`
- SRT captions
- model/asset manifest
- structured logs

The timeline records scene IDs, timing, sources, prompts, caption style and aspect ratio.

The manifest records model provenance, revision, license, prompt, seed, output information, source assets and measured runtime when available.



## 6. Model Capability Registry

The routing registry contains five researched candidates:

- LTX-Video
- Wan2.1
- CogVideoX-2B
- HunyuanVideo
- Mochi-1

The registry records capability and provenance information such as:

- text-to-video support
- image-to-video support
- duration range
- supported aspect ratios
- priority
- license
- source classification
- measured runtime when available
- execution availability/evidence

The detailed model research is documented in `SOURCES.md`.



## 7. Routing Strategy

The router evaluates each registered model against the creative brief.

The scoring considers:

1. text-to-video capability
2. duration compatibility
3. aspect-ratio compatibility
4. execution evidence/availability
5. measured runtime evidence
6. registry priority

Compatible candidates are ranked and the highest-scoring candidate is selected.

The router also records the individual candidate checks in `route_decision.json`.

This makes the routing decision inspectable rather than treating model selection as a hardcoded single-model choice.

Reported model runtime or VRAM information is not treated as a project measurement.

Measured project evidence receives stronger routing significance than unmeasured external estimates.



## 8. Five-Model Research

The project researched five open/open-weight video models using primary sources.

### LTX-Video

LTX-Video provides text-to-video and image-to-video capabilities.

The project successfully executed:


ltxv-2b-0.9.6-distilled-04-25


on a Tesla T4.

The exact checkpoint is governed by the LTXV Open Weights License dated April 17, 2025.

### Wan2.1

Wan2.1 provides text-to-video and image-to-video capabilities and includes a smaller T2V-1.3B model.

The official project reports approximately 8.19 GB VRAM for the T2V-1.3B configuration.

The project investigated execution on free Colab hardware but did not obtain a successful generation.

### CogVideoX-2B

CogVideoX-2B provides text-to-video generation and documented optimized/quantized inference configurations.

The project investigated execution on free Colab hardware.

Attempts using quantized/offloaded configurations caused system-memory failures in the available environment.

No successful CogVideoX-2B generation is claimed.

### HunyuanVideo

HunyuanVideo is a substantially larger video-generation model.

The official documentation reports substantially higher GPU memory requirements than the available T4 environment.

The project therefore did not attempt a full execution.

The model also uses the Tencent Hunyuan Community License, which contains important territorial and usage restrictions.

### Mochi-1

Mochi-1 provides text-to-video generation and is released under Apache-2.0 according to its official repository.

The standard implementation has substantially higher reported resource requirements than the available T4 environment.

The project therefore did not claim a successful execution.

Detailed evidence and source references are maintained in `SOURCES.md`.



## 9. LTX-Video Execution Evidence

LTX-Video was successfully executed using an approved free Google Colab Tesla T4 accelerator.

Model revision:


ltxv-2b-0.9.6-distilled-04-25


Measured configuration:


GPU: Tesla T4
PyTorch: 2.11.0+cu128
CUDA available: True
Frames: 25
Resolution: 512 x 768
FPS: 8
Inference steps: 8
Seed: 42
Runtime: approximately 19 seconds


The successful generated artifact was:


ltx_baseline_test.mp4


The execution notebook is preserved as:


notebooks/ltx_t4_baseline.ipynb


### Execution strategy

The standard execution path initially attempted to place the T5 text encoder on the T4 GPU and exceeded the available CUDA memory.

A custom execution path was used:

1. load T5 on CPU using bfloat16
2. encode positive and negative prompts
3. release T5 from memory
4. move the VAE and transformer to CUDA
5. construct the pipeline using precomputed prompt embeddings
6. generate the video
7. save the MP4 artifact

This successfully completed model inference on the T4.

### Output limitation

The generated video contained visual artifacts and distorted text-like content.

The final pipeline therefore does not rely on the generative model to render readable captions.

Captions are generated locally and burned into the final video using FFmpeg.


## 10. CPU/FFmpeg Fallback

The system provides a local CPU workflow fallback when a usable model-generated artifact is unavailable.

The fallback is explicitly distinguished from AI-generated video.

It uses:

- scene planning
- workflow-specific visual treatments
- FFmpeg
- captions
- timeline metadata
- validation
- manifest generation

The fallback supports:

- education
- news
- product
- 16:9
- 9:16

The fallback keeps the rest of the pipeline operational even when model inference cannot be completed.


## 11. Error Handling

The system handles several failure conditions.

### Invalid creative brief

Brief validation rejects invalid or unsupported input values before generation.

### Missing model artifact

If the expected model-generated artifact does not exist, the pipeline records the failure and uses CPU workflow assembly.

### Model failure

The fallback module records:

- primary model
- failure reason
- fallback decision

The current implementation may identify the next ranked candidate, but it does not falsely claim that the alternative model was executed if the actual pipeline falls through to CPU assembly.

### Missing or invalid assets

Asset validation checks:

- existence
- file type
- non-empty content
- supported extension

### Invalid final video

The output validator checks:

- file existence
- non-empty output
- MP4 format
- FFprobe readability
- duration
- captions
- timeline



## 12. Video Assembly

FFmpeg is used for local video operations.

The assembly layer provides functionality for:

- test-video creation
- clip concatenation
- aspect-ratio conversion
- caption burning
- duration inspection
- basic MP4 validation

The final output is encoded as MP4 using H.264-compatible local FFmpeg processing.



## 13. Captions

Captions are generated from the supplied script.

The script is divided into scene-aligned caption segments.

The caption generator produces standard SRT files.

The SRT file is then burned into the final video using FFmpeg.

This separates readable caption rendering from the video-generation model itself.

---

## 14. Editable Timeline

The system produces an editable timeline JSON file.

Each scene contains:

- scene ID
- start time
- duration
- source
- prompt
- caption style

The timeline also records the requested aspect ratio.

The timeline is generated from the workflow scene plan, making the output inspectable and editable rather than producing only a final MP4.



## 15. Reproducibility and Provenance

For model-generated outputs, the system records:

- model name
- model revision
- prompt
- seed
- generation method
- output path
- license
- runtime when measured

For assembled outputs, the system records:

- workflow
- scene plan
- timeline
- captions
- validation result
- manifest
- logs

The project distinguishes:


reported

from:


measured

evidence.

External model documentation is never presented as if it were measured locally.


## 16. Evaluation

The project includes a 10-brief benchmark.

The benchmark contains varied briefs across:

- education
- news
- product
- 16:9
- 9:16

Measured result:

Total briefs: 10
Successful renders: 10
Render success rate: 100%
Route accuracy: 100%
Average latency: approximately 2.10 seconds

### Measurement boundary

These measurements represent the local routing and CPU workflow assembly pipeline.

They do **not** represent ten generative-model inference executions.

All ten benchmark cases successfully rendered through the local CPU workflow assembly path.

The approximately 2.10-second latency therefore measures local pipeline execution and must not be interpreted as LTX-Video, Wan2.1, CogVideoX, HunyuanVideo or Mochi-1 inference latency.


## 17. Testing

The automated test suite contains:


43 passing tests


Coverage includes:

- creative brief validation
- workflow planning
- routing
- fallback behavior
- generator adapters
- workflow-specific video assembly
- captions
- timeline generation
- asset validation
- output validation
- evaluation metrics
- benchmark behavior

The project also includes explicit test scenarios for:

- baseline workflow
- education workflow
- news workflow
- product workflow
- 16:9 output
- 9:16 output
- invalid brief
- model failure
- missing/corrupt asset
- output validation

The detailed test plan is maintained in:

test_pack/TEST_PLAN.md


## 18. CLI and Local Reproduction

The project provides a local CLI.

Show available commands:


python -m src.cli --help

Validate a brief:


python -m src.cli validate examples\education_brief.json


Generate an education draft:


python -m src.cli generate examples\education_brief.json


Generate a news draft:


python -m src.cli generate examples\news_brief.json


Generate a product draft:


python -m src.cli generate examples\product_brief.json


Run the benchmark:


python -m src.cli benchmark


The CPU reproduction requires:


Python 3.11
FFmpeg
Project dependencies


No paid API or pay-as-you-go inference service is required for the local orchestration pipeline.

The actual generative-model execution requires the approved free accelerator notebook.



## 19. Resource Strategy

The project separates resource requirements between local orchestration and model inference.

### Non-GPU laptop

Used for:

- planning
- routing
- validation
- captions
- timeline generation
- FFmpeg assembly
- logging
- evaluation
- benchmarking

### Approved free accelerator

Used for:

- LTX-Video model inference

This architecture allows the core software pipeline to remain reproducible on CPU hardware while still providing actual open-model execution evidence.



## 20. Licensing

Model licenses are documented in `SOURCES.md`.

The project records the repository license separately from the exact model/checkpoint license where they differ.

For the executed LTX checkpoint:


ltxv-2b-0.9.6-distilled-04-25


the applicable checkpoint license is:


LTXV Open Weights License


dated April 17, 2025.

The LTX-Video source repository itself is Apache-2.0 licensed.

This distinction is intentional.

Users must verify the applicable license terms before redistribution or commercial use.



## 21. AI-Assisted Development

AI coding assistance was used during development.

Material AI-assisted development is disclosed in:


AI_USE.md


The candidate remains responsible for:

- understanding the implementation
- modifying the generated code
- testing
- debugging
- validating outputs
- explaining engineering decisions
- performing live changes during demonstration

The project does not treat AI-generated code as independently validated without project testing.

---

## 22. Engineering Ownership

The implementation contains original project-level engineering across:

- workflow orchestration
- capability registry
- routing logic
- fallback handling
- video assembly
- caption generation
- timeline generation
- validation
- asset validation
- reproducibility manifests
- structured logging
- evaluation metrics
- benchmark execution
- automated tests
- CLI integration

The final system was tested through the project's automated test suite and local workflow executions.


## 23. Limitations

### Model execution

Only LTX-Video was successfully executed by this project in the available free accelerator environment.

Wan2.1, CogVideoX-2B, HunyuanVideo and Mochi-1 are documented as researched candidates and are not represented as successful project executions.

### Model output quality

The LTX baseline contained visual artifacts and distorted text-like content.

Readable captions are therefore generated locally.

### Benchmark interpretation

The 10-brief benchmark measures local routing and CPU workflow assembly.

It does not represent ten generative-model inference runs.

### Fallback execution

The fallback module can identify the next ranked model candidate after failure, but the implemented pipeline ultimately uses CPU workflow assembly when a usable model artifact is unavailable.

### Model-resource evidence

Hardware and runtime figures for models that were not successfully executed are treated as author-reported values from primary sources.

They are not represented as project measurements.



## 24. Evidence Boundary

The project intentionally separates three categories of evidence.

### Reported model evidence

Obtained from:

- official repositories
- official model documentation
- official model cards
- official technical reports

### Measured project evidence

Obtained from executions performed by this project, including:

- LTX T4 execution
- local pipeline benchmark
- automated tests
- local workflow generation
- video validation

### Engineering decisions

Produced by the project's implementation, including:

- routing scores
- workflow templates
- fallback logic
- validation rules
- benchmark structure

This separation prevents external model claims from being presented as project measurements.



## 25. Deliverables

The repository contains or documents the following project evidence:

- source code
- automated tests
- example briefs
- 10-brief benchmark
- model capability registry
- five-model research
- CPU fallback
- workflow outputs
- captions
- editable timelines
- manifests
- structured logs
- LTX T4 execution notebook
- `SOURCES.md`
- `AI_USE.md`
- `test_pack/TEST_PLAN.md`
- `docs/TECHNICAL_REPORT.md`

The generated MP4 outputs are produced locally from the example briefs and are intentionally excluded from Git tracking through `.gitignore`.


## 26. Conclusion

The resulting system provides a reproducible local orchestration pipeline for short-form video generation.

It combines:

- structured creative briefs
- workflow-aware planning
- capability-based routing
- open-model execution evidence
- CPU/FFmpeg fallback
- captions
- editable timelines
- validation
- manifests
- structured logging
- automated testing
- benchmark evaluation

The project successfully demonstrates an actual open-model execution on a free T4 accelerator while maintaining a CPU-capable local orchestration pipeline.

The implementation also explicitly documents its evidence limitations rather than claiming successful execution or measured performance for models that were not successfully run.
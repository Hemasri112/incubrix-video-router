# IncuBrix Video Router - Test Plan

## 1. Purpose

This test pack documents functional, failure and validation tests for the video-generation routing system.

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
| Benchmark | Evaluate 10 varied briefs | Benchmark summary |

## 3. Automated Tests

The automated pytest suite covers:

- planner validation
- workflow planning
- router behavior
- fallback handling
- generator behavior
- asset validation
- video validation
- captions
- timeline
- manifest
- workflow video generation
- evaluation metrics
- benchmark behavior

Current test suite result:

43 tests passed.

## 4. Benchmark Test

The 10-brief benchmark contains:

- 4 education briefs
- 3 news briefs
- 3 product briefs
- 6 landscape briefs
- 4 portrait briefs

Measured result:

- Total briefs: 10
- Successful renders: 10
- Render success rate: 100%
- Route accuracy: 100%
- Average local pipeline latency: approximately 2.10 seconds

The benchmark latency measures routing and CPU workflow assembly.

It is not generative-model inference latency.

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

The system handles:

- invalid creative briefs
- unsupported workflows
- unsupported aspect ratios
- missing video artifacts
- missing assets
- empty assets
- unsupported asset extensions
- invalid captions
- invalid timeline input
- FFmpeg failures
- output validation failures

## 7. Evidence Boundary

Project measurements are explicitly separated from model-author-reported specifications.

The five researched models are documented in SOURCES.md.

Only successful project executions are described as measured executions.
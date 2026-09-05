# IncuBrix Video Generation and Model Routing
## Technical Report

## 1. Executive Summary

This project implements a local orchestration system for generating short draft videos from structured creative briefs.

The system combines workflow planning, capability-based model routing, open-model execution evidence, CPU/FFmpeg fallback, captions, editable timelines, validation, logging and benchmarking.

## 2. Problem Statement

The system must transform a structured creative brief into a reproducible short-form draft video while selecting an appropriate generation strategy based on model capabilities and available resources.

## 3. Architecture

```text
Creative Brief
    ->
Brief Validation
    ->
Workflow Planning
    ->
Capability Registry
    ->
Model Routing
    ->
Video Generation / CPU Fallback
    ->
FFmpeg Assembly
    ->
Captions
    ->
Validation
    ->
MP4 + Timeline + Manifest + Logs
```

## 4. Workflow Design

### Education

Hook -> Concept Explanation -> Example -> Summary

### News

Headline -> Context -> Key Development -> Impact -> Closing

### Product

Hook -> Problem -> Product Showcase -> Benefits -> Call To Action

## 5. Model Routing

The system maintains a capability registry containing five researched video models:

- LTX-Video
- Wan2.1
- CogVideoX-2B
- HunyuanVideo
- Mochi-1

Routing considers:

- text-to-video capability
- duration compatibility
- aspect ratio
- local execution availability
- measured runtime evidence
- model priority

## 6. Model Research

Detailed model research is provided in SOURCES.md.

Reported model specifications are kept separate from project measurements.

## 7. LTX-Video Execution

LTX-Video was successfully executed using an approved free Tesla T4 accelerator.

Measured runtime:

approximately 19 seconds.

Configuration:

- 25 frames
- 512 x 768
- 8 FPS
- 8 inference steps
- seed 42

## 8. CPU Fallback

When a usable model artifact is unavailable, the local system creates a deterministic workflow video using FFmpeg.

The fallback supports:

- education
- news
- product
- 16:9
- 9:16
- captions
- timeline generation
- validation

## 9. Validation

The system validates:

- video existence
- MP4 format
- file size
- FFprobe readability
- duration
- captions
- timeline

## 10. Evaluation

The 10-brief benchmark produced:

- 10/10 successful renders
- 100% render success rate
- 100% route accuracy
- approximately 2.10 seconds average local pipeline latency

The benchmark measures local routing and CPU assembly, not generative-model inference.

## 11. Testing

The automated test suite contains 43 passing tests.

Coverage includes:

- planning
- routing
- fallback
- generation adapters
- workflows
- captions
- timeline
- assets
- validation
- metrics
- benchmark behavior

## 12. Reproducibility

The project records:

- model revision
- prompt
- seed
- generation method
- runtime when measured
- output metadata
- timeline
- manifest
- logs

## 13. Limitations

Only LTX-Video was successfully executed in the available free accelerator environment.

The other four researched models are documented candidates and are not represented as successful project executions.

## 14. Engineering Ownership

AI assistance was used during development and is disclosed in AI_USE.md.

The candidate is responsible for the final implementation, testing, debugging and demonstration.
